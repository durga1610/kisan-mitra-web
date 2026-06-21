"""
gemini_fallback.py — Gemini High-Availability Service
=====================================================
Features:
  1. 6-key rotation pool (GEMINI_API_KEY_1 ... GEMINI_API_KEY_6)
  2. Automatic failover on RESOURCE_EXHAUSTED / QUOTA_EXCEEDED / RATE_LIMITED
  3. Normalized 7-day response cache (synonyms + crop aliases deduplicated)
  4. Structured local fallbacks — never returns None to callers
  5. Full audit logging (key index, rotation events, cache hits) — no actual key values logged
"""

import os
import re
import time
import logging
import json
import hashlib
import sqlite3
import threading
from datetime import datetime
from typing import List, Optional, Set

import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted, GoogleAPIError
from db_utils import get_db_connection, fire_and_forget_write, fire_and_forget_callable
from config import DB_PATH

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION A — 6-Key Rotation Manager
# ─────────────────────────────────────────────────────────────────────────────

class AllKeysExhaustedException(Exception):
    """Raised when every key in the pool has been quota-exhausted."""
    pass


class GeminiKeyManager:
    """
    Thread-safe manager for a pool of up to 6 Gemini API keys.
    Key values are NEVER logged — only their 1-based index is referenced.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._keys: List[str] = []
        self._active_index: int = 0          # index into self._keys
        self._exhausted: Set[int] = set()    # indices that are quota-exhausted
        self._rotation_count: int = 0
        self._success_count: int = 0
        self._quota_fail_count: int = 0
        self._load_keys()

    def _load_keys(self):
        """Load keys from env vars GEMINI_API_KEY_1..6 + legacy GEMINI_API_KEY."""
        keys = []
        # Prefer numbered keys first
        for i in range(1, 7):
            val = os.getenv(f"GEMINI_API_KEY_{i}", "").strip()
            if val:
                keys.append(val)
        # Fall back to legacy key if no numbered keys found
        if not keys:
            legacy = os.getenv("GEMINI_API_KEY", "").strip()
            if legacy:
                keys.append(legacy)
        self._keys = keys
        if keys:
            logger.info("[GeminiKeyManager] Loaded %d API key(s). Active: KEY_%d", len(keys), self._active_index + 1)
        else:
            logger.warning("[GeminiKeyManager] No Gemini API keys found in environment. All Gemini calls will fall back to local engine.")

    @property
    def has_keys(self) -> bool:
        return len(self._keys) > 0

    @property
    def all_exhausted(self) -> bool:
        with self._lock:
            return len(self._keys) == 0 or len(self._exhausted) >= len(self._keys)

    @property
    def current_key(self) -> Optional[str]:
        with self._lock:
            if not self._keys:
                return None
            return self._keys[self._active_index]

    @property
    def active_key_label(self) -> str:
        with self._lock:
            return f"KEY_{self._active_index + 1}"

    def mark_exhausted(self, index: int, module: str = "", crop: str = ""):
        with self._lock:
            if index not in self._exhausted:
                self._exhausted.add(index)
                self._quota_fail_count += 1
                logger.warning(
                    "[KEY_MANAGER] QUOTA_EXCEEDED KEY_%d | module=%s crop=%s | exhausted_pool=%s/%s",
                    index + 1, module or "unknown", crop or "unknown",
                    len(self._exhausted), len(self._keys)
                )
                _log_rotation_event("QUOTA_EXCEEDED", index + 1, module, 0, crop)

    def rotate(self, from_module: str = "") -> bool:
        """
        Try to switch to the next non-exhausted key.
        Returns True if a new key is available, False if all are exhausted.
        """
        with self._lock:
            if not self._keys:
                return False
            original = self._active_index
            for i in range(1, len(self._keys) + 1):
                candidate = (self._active_index + i) % len(self._keys)
                if candidate not in self._exhausted:
                    old_label = f"KEY_{self._active_index + 1}"
                    self._active_index = candidate
                    new_label = f"KEY_{self._active_index + 1}"
                    self._rotation_count += 1
                    logger.info("[KEY_ROTATION] %s → %s | module=%s | rotation_count=%d",
                                old_label, new_label, from_module or "unknown", self._rotation_count)
                    _log_rotation_event("KEY_ROTATION", self._active_index + 1, from_module, 0)
                    return True
            # All keys exhausted
            logger.error("[KEY_MANAGER] ALL_EXHAUSTED — all %d keys quota-exceeded. Falling back to local engine.", len(self._keys))
            _log_rotation_event("ALL_EXHAUSTED", self._active_index + 1, from_module, 0)
            return False

    def reset_daily(self):
        """Reset exhausted set (call this at midnight or on server restart if needed)."""
        with self._lock:
            self._exhausted.clear()
            self._active_index = 0
            logger.info("[KEY_MANAGER] Daily reset complete. All keys reactivated.")

    def stats(self) -> dict:
        with self._lock:
            return {
                "total_keys": len(self._keys),
                "active_key": f"KEY_{self._active_index + 1}" if self._keys else "NONE",
                "exhausted_count": len(self._exhausted),
                "rotation_count": self._rotation_count,
                "success_count": self._success_count,
                "quota_fail_count": self._quota_fail_count,
            }

    def increment_success(self):
        with self._lock:
            self._success_count += 1


# Singleton instance
_KEY_MANAGER = GeminiKeyManager()


def _log_rotation_event(event: str, key_index: int, module: str, latency_ms: int, crop: str = ""):
    """Async audit log for key rotation events — never logs actual key values."""
    fire_and_forget_write(
        "INSERT INTO gemini_key_rotation_log "
        "(timestamp, event, key_index, module, latency_ms, crop) VALUES (?, ?, ?, ?, ?, ?)",
        (datetime.now().isoformat(), event, key_index, module or "", latency_ms, crop or "")
    )


# ─────────────────────────────────────────────────────────────────────────────
# SECTION B — Database Schema Init
# ─────────────────────────────────────────────────────────────────────────────

def init_gemini_db():
    """Idempotent schema creation for all Gemini tracking tables."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS gemini_fallback_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            module TEXT NOT NULL,
            user_uid TEXT,
            crop TEXT,
            trigger_reason TEXT,
            prompt_hash TEXT,
            response_source TEXT,
            latency_ms INTEGER,
            success INTEGER
        )""")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS gemini_daily_usage (
            user_uid TEXT,
            date TEXT,
            call_count INTEGER,
            PRIMARY KEY (user_uid, date)
        )""")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS gemini_response_cache (
            cache_key TEXT PRIMARY KEY,
            response_json TEXT,
            cached_at TEXT,
            query TEXT,
            source TEXT
        )""")

        # Audit log for key rotation events
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS gemini_key_rotation_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            event TEXT NOT NULL,
            key_index INTEGER NOT NULL,
            module TEXT,
            latency_ms INTEGER,
            crop TEXT
        )""")

        # Safe migration: add columns that may not exist in older DBs
        for col_def in [
            ("gemini_response_cache", "query", "TEXT"),
            ("gemini_response_cache", "source", "TEXT"),
        ]:
            table, col, coltype = col_def
            try:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} {coltype}")
            except Exception:
                pass  # column already exists

        conn.commit()
        conn.close()
        logger.info("[Gemini] DB schema verified/created (key_rotation_log, cache v2).")
    except Exception as e:
        logger.error("[Gemini] DB init error: %s", e)


init_gemini_db()


# ─────────────────────────────────────────────────────────────────────────────
# SECTION C — Normalized 7-Day Cache
# ─────────────────────────────────────────────────────────────────────────────

CACHE_TTL_SECONDS = 7 * 24 * 3600  # 7 days

# Synonym / alias normalisation map
_SYNONYMS = {
    # Fertilizer
    "fertiliser": "fertilizer",
    "fertilisers": "fertilizer",
    "fertilizers": "fertilizer",
    "manure": "fertilizer",
    "khad": "fertilizer",
    # Pest
    "insect": "pest",
    "insects": "pest",
    "kida": "pest",
    "keede": "pest",
    "pests": "pest",
    # Recommend
    "suggest": "recommend",
    "suggestion": "recommend",
    "recommendation": "recommend",
    "recommendations": "recommend",
    "advise": "recommend",
    "advice": "recommend",
    # Disease
    "disease": "disease",
    "bimari": "disease",
    "rog": "disease",
    # Crops (Hindi → English)
    "tamatar": "tomato",
    "aloo": "potato",
    "alu": "potato",
    "pyaz": "onion",
    "dhan": "paddy",
    "gehun": "wheat",
    "kapas": "cotton",
    "makka": "maize",
    "kela": "banana",
    "papita": "papaya",
    "aam": "mango",
    "angur": "grape",
    "gajar": "carrot",
    "gobhi": "cauliflower",
}


def normalize_query(text: str) -> str:
    """
    Normalises a query string so semantically equivalent queries share a cache key.
    Example: 'fertiliser for banana crop' → 'banana fertilizer'
    """
    if not text:
        return ""
    t = text.lower().strip()
    # Remove punctuation
    t = re.sub(r"[^\w\s]", " ", t)
    # Remove filler words
    fillers = {"for", "the", "a", "an", "my", "me", "best", "what", "is", "how", "to", "crop", "plant", "field", "in", "of", "about", "tell", "give", "please", "i", "need", "want", "should", "can", "do"}
    tokens = [w for w in t.split() if w not in fillers]
    # Apply synonyms
    tokens = [_SYNONYMS.get(w, w) for w in tokens]
    # Deduplicate while preserving order
    seen = set()
    deduped = []
    for tok in tokens:
        if tok not in seen:
            seen.add(tok)
            deduped.append(tok)
    return " ".join(sorted(deduped))  # sort for consistency


def _make_normalized_cache_key(module: str, query_text: str) -> str:
    """Build a cache key from normalized query text + module tag."""
    normalized = normalize_query(query_text)
    raw = f"{module}::{normalized}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def generate_cache_key(*args, **kwargs) -> str:
    """Legacy exact-match cache key for non-text calls (image hashes, structured params)."""
    serialized = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _clean_json_text(text: str) -> str:
    """Strip markdown code fences that Gemini sometimes wraps around JSON."""
    cleaned = text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return cleaned.strip()


def get_cached_response(cache_key: str) -> Optional[dict]:
    """Retrieve response from SQLite cache if within 7-day TTL."""
    try:
        conn = get_db_connection(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT response_json, cached_at, source FROM gemini_response_cache WHERE cache_key = ?",
            (cache_key,)
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            response_json = row["response_json"] if hasattr(row, "keys") else row[0]
            cached_at_str = row["cached_at"] if hasattr(row, "keys") else row[1]
            source = (row["source"] if hasattr(row, "keys") else row[2]) or "CACHE"
            cached_at = datetime.fromisoformat(cached_at_str)
            age_seconds = (datetime.now() - cached_at).total_seconds()
            if age_seconds < CACHE_TTL_SECONDS:
                logger.info("[CACHE_HIT] key=%s age=%.0fh source=%s", cache_key[:12], age_seconds / 3600, source)
                _log_rotation_event("CACHE_HIT", 0, source, 0)
                return json.loads(response_json)
            else:
                # Expired — delete async
                fire_and_forget_write("DELETE FROM gemini_response_cache WHERE cache_key = ?", (cache_key,))
    except Exception as e:
        logger.warning("[Cache] Read error: %s", e)
    return None


def set_cached_response(cache_key: str, response: dict, query: str = "", source: str = "GEMINI_FALLBACK"):
    """Write response to cache asynchronously (never blocks request thread)."""
    fire_and_forget_write(
        "INSERT OR REPLACE INTO gemini_response_cache "
        "(cache_key, response_json, cached_at, query, source) VALUES (?, ?, ?, ?, ?)",
        (cache_key, json.dumps(response), datetime.now().isoformat(), query, source)
    )


# ─────────────────────────────────────────────────────────────────────────────
# SECTION D — Rate Limiting (per-minute in-memory guard)
# ─────────────────────────────────────────────────────────────────────────────

_rate_limit_timestamps: List[float] = []
_rate_limit_lock = threading.Lock()


def check_rate_limit() -> bool:
    """Returns True if within 60 req/min limit."""
    if os.getenv("TESTING") == "1":
        return True
    global _rate_limit_timestamps
    with _rate_limit_lock:
        now = time.time()
        _rate_limit_timestamps = [t for t in _rate_limit_timestamps if now - t < 60]
        if len(_rate_limit_timestamps) >= 60:
            logger.warning("[RateLimit] In-memory cap hit (60 req/min).")
            return False
        _rate_limit_timestamps.append(now)
        return True


# ─────────────────────────────────────────────────────────────────────────────
# SECTION E — Daily usage guard per user
# ─────────────────────────────────────────────────────────────────────────────

def check_and_increment_daily_limit(user_uid: str) -> bool:
    """Returns True if user is under daily limit (20 calls/day)."""
    if os.getenv("TESTING") == "1":
        return True
    if not user_uid:
        return True

    current_date = datetime.now().strftime("%Y-%m-%d")
    try:
        conn = get_db_connection(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT call_count FROM gemini_daily_usage WHERE user_uid = ? AND date = ?",
            (user_uid, current_date)
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            call_count = row["call_count"] if hasattr(row, "keys") else row[0]
            if call_count >= 20:
                logger.warning("[DailyLimit] User %s exceeded 20 calls/day.", user_uid)
                return False
            fire_and_forget_write(
                "UPDATE gemini_daily_usage SET call_count = call_count + 1 WHERE user_uid = ? AND date = ?",
                (user_uid, current_date)
            )
        else:
            fire_and_forget_write(
                "INSERT INTO gemini_daily_usage (user_uid, date, call_count) VALUES (?, ?, 1)",
                (user_uid, current_date)
            )
        return True
    except Exception as e:
        logger.error("[DailyLimit] DB error: %s", e)
        return True


# ─────────────────────────────────────────────────────────────────────────────
# SECTION F — Fallback usage logger
# ─────────────────────────────────────────────────────────────────────────────

def log_fallback_call(module: str, user_uid: str, crop: str, trigger_reason: str,
                      prompt_text: str, source: str, latency_ms: int, success: bool):
    prompt_hash = hashlib.sha256(prompt_text.encode("utf-8")).hexdigest()
    fire_and_forget_write(
        "INSERT INTO gemini_fallback_log "
        "(timestamp, module, user_uid, crop, trigger_reason, prompt_hash, response_source, latency_ms, success) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (datetime.now().isoformat(), module, user_uid, crop, trigger_reason,
         prompt_hash, source, latency_ms, 1 if success else 0)
    )


# ─────────────────────────────────────────────────────────────────────────────
# SECTION G — Core Gemini Call with Key Rotation
# ─────────────────────────────────────────────────────────────────────────────

# Error strings that trigger key rotation
_QUOTA_ERRORS = (
    "resource_exhausted", "quota", "rate_limit", "rate limit",
    "too many requests", "429", "ratequotaexceeded", "quotaexceeded",
    "resourceexhausted", "userratequotaexceeded",
)


def _is_quota_error(exc: Exception) -> bool:
    """Returns True if this exception is a quota/rate-limit error."""
    if isinstance(exc, ResourceExhausted):
        return True
    msg = str(exc).lower()
    return any(kw in msg for kw in _QUOTA_ERRORS)


def execute_gemini_call(
    prompt_text: str,
    is_vision: bool = False,
    image_bytes: bytes = None,
    mime_type: str = "image/jpeg",
    is_json_response: bool = False,
    max_tokens: int = 4096,
    timeout: float = None,
    _module: str = "",
    _crop: str = "",
) -> str:
    """
    Executes a Gemini call with automatic key rotation on quota errors.

    Algorithm:
    1. For each available (non-exhausted) key in the pool:
       a. Configure genai with the current key
       b. Attempt up to 2 retries on transient errors
       c. On QUOTA_EXCEEDED → mark key exhausted, rotate to next key
       d. On success → return response text
    2. If all keys exhausted → raise AllKeysExhaustedException

    Args:
        prompt_text: The text prompt to send.
        is_vision: If True, send as multimodal with image_bytes.
        image_bytes: Raw image bytes for vision calls.
        mime_type: MIME type for vision call.
        is_json_response: Request JSON MIME type from Gemini.
        max_tokens: Max output tokens.
        timeout: Per-key timeout in seconds (default: 20s vision, 10s text).
        _module: Caller module name for logging.
        _crop: Crop name for logging.
    """
    import concurrent.futures

    if not _KEY_MANAGER.has_keys:
        raise AllKeysExhaustedException("No Gemini API keys configured.")

    model_name = "gemini-2.5-flash"
    total_timeout = timeout if timeout is not None else (20.0 if is_vision else 10.0)
    start_all = time.time()

    # Try each key in the pool (up to len(keys) attempts)
    keys_tried = 0
    max_keys = len(_KEY_MANAGER._keys)

    while keys_tried < max_keys:
        if _KEY_MANAGER.all_exhausted:
            raise AllKeysExhaustedException("All Gemini API keys are quota-exhausted.")

        current_idx = _KEY_MANAGER._active_index
        current_key = _KEY_MANAGER.current_key
        key_label = _KEY_MANAGER.active_key_label

        if not current_key:
            raise AllKeysExhaustedException("No active Gemini API key available.")

        # Configure genai with current key (thread-safe: we re-configure per call)
        try:
            genai.configure(api_key=current_key)
        except Exception as cfg_err:
            logger.warning("[%s] genai.configure failed for %s: %s", key_label, key_label, cfg_err)
            _KEY_MANAGER.mark_exhausted(current_idx, _module, _crop)
            if not _KEY_MANAGER.rotate(_module):
                raise AllKeysExhaustedException("All keys exhausted after configure failure.")
            keys_tried += 1
            continue

        logger.info("[ACTIVE_KEY_INDEX] %s | module=%s crop=%s", key_label, _module or "unknown", _crop or "unknown")

        # Attempt 2 retries on this key for transient (non-quota) errors
        for attempt in range(2):
            elapsed = time.time() - start_all
            remaining = total_timeout - elapsed
            if remaining <= 0.5:
                raise TimeoutError(f"Gemini call budget exhausted after {elapsed:.1f}s.")

            attempt_timeout = min(remaining, 8.0 if not is_vision else 18.0)

            try:
                gen_config_args = {
                    "temperature": 0.2,
                    "max_output_tokens": max_tokens,
                }
                if is_json_response:
                    gen_config_args["response_mime_type"] = "application/json"

                generation_config = genai.types.GenerationConfig(**gen_config_args)
                model = genai.GenerativeModel(model_name, transport="rest")

                def _run():
                    if is_vision:
                        if not image_bytes:
                            raise ValueError("image_bytes required for vision call.")
                        return model.generate_content(
                            [prompt_text, {"mime_type": mime_type, "data": image_bytes}],
                            generation_config=generation_config,
                            request_options={"timeout": attempt_timeout},
                        )
                    else:
                        return model.generate_content(
                            prompt_text,
                            generation_config=generation_config,
                            request_options={"timeout": attempt_timeout},
                        )

                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(_run)
                    try:
                        response = future.result(timeout=attempt_timeout)
                    except concurrent.futures.TimeoutError:
                        raise TimeoutError(f"Gemini timed out after {attempt_timeout:.1f}s")

                if not response.text:
                    raise ValueError("Empty response from Gemini.")

                # SUCCESS
                latency_ms = int((time.time() - start_all) * 1000)
                _KEY_MANAGER.increment_success()
                logger.info("[GEMINI_SUCCESS] %s | module=%s latency=%dms", key_label, _module or "unknown", latency_ms)
                _log_rotation_event("GEMINI_SUCCESS", current_idx + 1, _module, latency_ms, _crop)
                return response.text.strip()

            except Exception as exc:
                if _is_quota_error(exc):
                    # Quota/rate-limit error — rotate key immediately
                    logger.warning(
                        "[QUOTA_EXCEEDED] %s | module=%s crop=%s | error=%s",
                        key_label, _module or "unknown", _crop or "unknown", str(exc)[:120]
                    )
                    _KEY_MANAGER.mark_exhausted(current_idx, _module, _crop)
                    rotated = _KEY_MANAGER.rotate(_module)
                    if not rotated:
                        raise AllKeysExhaustedException("All Gemini API keys are quota-exhausted.")
                    break  # Stop retrying this key; outer loop will try next key

                # Transient error (network, timeout, etc.)
                logger.warning("[%s] Attempt %d/%d transient error: %s", key_label, attempt + 1, 2, str(exc)[:100])
                if attempt < 1:
                    time.sleep(0.5)
                else:
                    raise  # Re-raise on last retry

        keys_tried += 1

    raise AllKeysExhaustedException("All Gemini API keys attempted and failed.")


# ─────────────────────────────────────────────────────────────────────────────
# SECTION H — Structured Local Fallbacks
# ─────────────────────────────────────────────────────────────────────────────

def _local_advisory_fallback(message: str, farm_context: dict) -> dict:
    """Return a crop-specific advisory from local knowledge when Gemini is unavailable."""
    crop = ""
    if farm_context:
        crop = (farm_context.get("crop") or farm_context.get("plantedCrops", [""])[0]
                if farm_context.get("plantedCrops") else farm_context.get("crop", ""))
    crop = (crop or "").lower().strip()

    msg_lower = (message or "").lower()

    # Keyword-based response selection
    if any(k in msg_lower for k in ["fertilizer", "fertiliser", "khad", "manure"]):
        advice = (
            f"For {'your crop' if not crop else crop.title()}, apply balanced NPK (19:19:19) at 2-3 kg/acre "
            "during the vegetative stage. Switch to phosphorus-rich DAP at flowering, and potash (MOP) "
            "at fruiting stage. Always apply organic compost (5 tonnes/acre) before sowing."
        )
    elif any(k in msg_lower for k in ["pest", "insect", "kida", "bug"]):
        advice = (
            f"For {'your crop' if not crop else crop.title()} pest control: spray neem oil (3-5 ml/litre) "
            "as a preventive. For severe infestation use Imidacloprid (0.3 ml/litre) or Chlorpyrifos. "
            "Use yellow sticky traps to monitor whitefly populations."
        )
    elif any(k in msg_lower for k in ["disease", "blight", "spot", "rot", "wilt"]):
        advice = (
            f"For disease management in {'your crop' if not crop else crop.title()}: spray Mancozeb 75% WP "
            "(2.5 g/litre) or Copper Oxychloride every 10-14 days during humid conditions. "
            "Remove and destroy infected plant material. Ensure good field drainage."
        )
    elif any(k in msg_lower for k in ["water", "irrigation", "rain"]):
        advice = (
            "Ensure consistent moisture by scheduling irrigation every 5-7 days in dry weather. "
            "Use drip irrigation to conserve water. Avoid waterlogging — ensure proper field drainage."
        )
    elif any(k in msg_lower for k in ["harvest", "ready", "maturity"]):
        advice = (
            f"{'Your crop' if not crop else crop.title()} is typically ready for harvest when the leaves "
            "start to yellow and dry. Test a sample before full harvest. Harvest in the morning "
            "to reduce post-harvest moisture loss."
        )
    else:
        advice = (
            f"For {'your crop' if not crop else crop.title()}: maintain regular field scouting for pest and "
            "disease symptoms. Apply balanced NPK fertilizer at each growth stage. Ensure adequate water "
            "supply and use integrated pest management (IPM) practices for sustainable farming."
        )

    return {"text": advice, "source": "LOCAL_FALLBACK", "warning": "Gemini AI unavailable — local advisory used."}


def _local_fertilizer_fallback(crop: str, stage: str) -> dict:
    """Return fertilizer advice from local FERTILIZER_SCHEDULES."""
    from fertilizer_engine import FERTILIZER_SCHEDULES, CATEGORY_FERTILIZER_SCHEDULES, guess_crop_category

    crop_key = crop.lower().strip()
    if "paddy" in crop_key or "rice" in crop_key:
        crop_key = "rice"
    elif "corn" in crop_key or "maize" in crop_key:
        crop_key = "maize"

    schedule = FERTILIZER_SCHEDULES.get(crop_key)
    if not schedule:
        category = guess_crop_category(crop)
        if category:
            schedule = CATEGORY_FERTILIZER_SCHEDULES.get(category)

    if schedule:
        stage_cap = stage.capitalize() if stage else "Vegetative"
        entries = schedule.get(stage_cap, schedule.get("Vegetative", []))
        if entries:
            rec = " | ".join(f"Apply {e['fertilizer']} at {e['dosage']}" for e in entries)
            dosage = " | ".join(e['dosage'] for e in entries)
            return {
                "crop": crop,
                "stage": stage,
                "recommendation": rec,
                "dosage": dosage,
                "organicAlternative": "Vermicompost (2 tonnes/acre) or Farm Yard Manure (FYM)",
                "timing": f"Apply at the start of the {stage_cap} stage",
                "precautions": "Ensure soil moisture before applying. Avoid application before heavy rain.",
                "source": "LOCAL_FALLBACK",
            }

    # Ultimate fallback
    return {
        "crop": crop,
        "stage": stage,
        "recommendation": f"Apply NPK 19:19:19 at 2.5 kg/acre for {crop} during {stage} stage.",
        "dosage": "2.5 kg/acre",
        "organicAlternative": "Farm Yard Manure (FYM) at 5 tonnes/acre",
        "timing": "Apply at the beginning of the growth stage",
        "precautions": "Avoid fertilizer application before heavy rainfall forecast.",
        "source": "LOCAL_FALLBACK",
    }


def _local_disease_fallback(crop_hint: str) -> dict:
    """Return disease info from DISEASE_DB based on crop hint."""
    from disease_database import DISEASE_DB

    crop_lower = (crop_hint or "").lower().strip()
    # Map crop to a healthy key first, then look for disease
    crop_map = {
        "tomato": "tomato_healthy", "potato": "potato_healthy",
        "rice": "rice_healthy", "paddy": "rice_healthy",
        "cotton": "cotton_healthy", "apple": "apple_healthy",
        "grape": "grape_healthy", "corn": "corn_healthy", "maize": "corn_healthy",
        "cherry": "cherry_healthy",
    }
    db_key = crop_map.get(crop_lower, "tomato_healthy")
    # Try to find any entry for this crop
    for k in DISEASE_DB:
        if crop_lower in k:
            db_key = k
            break

    entry = DISEASE_DB.get(db_key, DISEASE_DB.get("tomato_early_blight", {}))
    report = entry.get("en", {})

    return {
        "disease_name": report.get("Disease", "Unable to determine"),
        "confidence": 65,
        "severity": report.get("Severity", "Medium"),
        "symptoms": report.get("Symptoms", "Inspect the leaf carefully for discolouration, spots, or wilting."),
        "treatment": report.get("Treatment", "Apply Mancozeb or Copper Oxychloride fungicide. Remove infected plant material."),
        "prevention": report.get("Prevention", "Maintain crop hygiene, proper spacing, and regular field scouting."),
        "organic_solution": "Neem oil spray (3-5 ml/litre) every 10 days as preventive.",
        "chemical_solution": report.get("Suggested Products", "Mancozeb 75% WP, Copper Oxychloride"),
        "source": "LOCAL_FALLBACK",
        "warning": "Gemini Vision unavailable — local disease database used.",
    }


def _local_crop_recommendations_fallback(state: str, soil: str, water: str) -> list:
    """Return state/soil-appropriate crop recommendations from local profiles."""
    from fertilizer_engine import load_crop_profiles

    profiles = load_crop_profiles()
    state_lower = (state or "").lower()
    soil_lower = (soil or "").lower()

    # Season-based crop list
    month = datetime.now().month
    if 6 <= month <= 10:  # Kharif
        base_crops = ["rice", "cotton", "maize", "soybean", "groundnut", "sugarcane"]
    elif month >= 11 or month <= 3:  # Rabi
        base_crops = ["wheat", "mustard", "potato", "onion", "chickpea", "pea"]
    else:  # Zaid
        base_crops = ["maize", "cucumber", "watermelon", "tomato", "brinjal", "mung bean"]

    recs = []
    for crop_name in base_crops[:5]:
        profile = profiles.get(crop_name, {})
        recs.append({
            "crop_name": crop_name.title(),
            "suitability_score": 75.0,
            "reasons": (
                f"{crop_name.title()} is suitable for {state or 'your region'} with {soil or 'your'} soil. "
                f"Good market demand during current season."
            ),
            "estimated_yield": profile.get("yield_per_acre", "2-4 tonnes/acre"),
            "estimated_duration_days": profile.get("duration_days", 90),
            "market_demand": "Medium",
            "source": "LOCAL_FALLBACK",
        })

    return recs


# ─────────────────────────────────────────────────────────────────────────────
# SECTION I — Public API Functions
# ─────────────────────────────────────────────────────────────────────────────

def generate_advisory(message: str, farm_context: dict, weather_context: dict,
                      trigger_reason: str, user_uid: str) -> dict:
    """
    AI Advisor Gemini Fallback.
    Returns structured advisory — NEVER returns None.
    Priority: Cache → Gemini (with key rotation) → Local Fallback
    """
    # 1. Normalized cache lookup
    cache_key = _make_normalized_cache_key("advisory", message)
    cached = get_cached_response(cache_key)
    if cached:
        return cached

    crop = ""
    if farm_context:
        if farm_context.get("plantedCrops"):
            planted = farm_context["plantedCrops"]
            crop = (planted[0] if isinstance(planted[0], str) else planted[0].get("cropName", "")) if planted else ""
        crop = crop or farm_context.get("crop", "")

    # 2. Rate / daily limit check
    if not check_rate_limit() or not check_and_increment_daily_limit(user_uid):
        log_fallback_call("advisory", user_uid, crop, "limit_exceeded", message, "LOCAL_FALLBACK", 0, False)
        return _local_advisory_fallback(message, farm_context)

    # 3. Build prompt
    prompt = f"""You are an agricultural expert for Indian farmers.
Farm Details: {json.dumps(farm_context)}
Current Weather: {json.dumps(weather_context)}
User Query: {message}

Rules:
1. Give actionable, practical guidance in 2-4 sentences.
2. Speak directly to the farmer.
3. Do not recommend risky chemical dosages. Suggest organic alternatives when unsure.
4. Do not say "Unsupported crop" or "N/A" or "Data unavailable". Always help.

Response:"""

    start_time = time.time()
    try:
        text = execute_gemini_call(prompt, is_vision=False, _module="advisory", _crop=crop)
        result = {"text": text, "source": "GEMINI_FALLBACK"}
        latency = int((time.time() - start_time) * 1000)
        set_cached_response(cache_key, result, query=message, source="GEMINI_FALLBACK")
        log_fallback_call("advisory", user_uid, crop, trigger_reason, prompt, "GEMINI_FALLBACK", latency, True)
        return result

    except AllKeysExhaustedException:
        latency = int((time.time() - start_time) * 1000)
        logger.warning("[advisory] All Gemini keys exhausted — returning local fallback.")
        log_fallback_call("advisory", user_uid, crop, "all_keys_exhausted", message, "LOCAL_FALLBACK", latency, False)
        fb = _local_advisory_fallback(message, farm_context)
        set_cached_response(cache_key, fb, query=message, source="LOCAL_FALLBACK")
        return fb

    except Exception as exc:
        latency = int((time.time() - start_time) * 1000)
        logger.error("[advisory] Gemini call failed: %s", exc)
        log_fallback_call("advisory", user_uid, crop, f"error:{exc}", message, "LOCAL_FALLBACK", latency, False)
        return _local_advisory_fallback(message, farm_context)


def generate_fertilizer_advice(crop: str, age: int, stage: str, soil: str, weather: str,
                                trigger_reason: str, user_uid: str) -> dict:
    """
    Fertilizer Gemini Fallback.
    Returns structured advice — NEVER returns None.
    Priority: Cache → Local FERTILIZER_SCHEDULES → Gemini → Local Fallback
    """
    # 1. Check local schedule first (before spending a Gemini key)
    from fertilizer_engine import FERTILIZER_SCHEDULES, guess_crop_category
    crop_key = crop.lower().strip()
    if "paddy" in crop_key or "rice" in crop_key:
        crop_key = "rice"
    elif "corn" in crop_key or "maize" in crop_key:
        crop_key = "maize"

    if crop_key in FERTILIZER_SCHEDULES:
        # LOCAL_MATCH — no Gemini needed
        logger.info("[fertilizer] LOCAL_MATCH for crop=%s stage=%s", crop, stage)
        return _local_fertilizer_fallback(crop, stage)

    # 2. Normalized cache lookup
    cache_key = _make_normalized_cache_key("fertilizer", f"{crop} {stage} fertilizer {soil}")
    cached = get_cached_response(cache_key)
    if cached:
        return cached

    # 3. Rate / daily limit check
    if not check_rate_limit() or not check_and_increment_daily_limit(user_uid):
        log_fallback_call("fertilizer", user_uid, crop, "limit_exceeded", f"{crop}-{stage}", "LOCAL_FALLBACK", 0, False)
        return _local_fertilizer_fallback(crop, stage)

    # 4. Build Gemini prompt
    prompt = f"""You are an expert agronomist providing fertilizer schedules for Indian farmers.
Crop Name: {crop}
Crop Age (Days): {age}
Growth Stage: {stage}
Soil Type: {soil}
Weather: {weather}

Return STRICT JSON only (no markdown wrapper):
{{
    "crop": "{crop}",
    "stage": "{stage}",
    "age": {age},
    "recommendation": "recommendation text",
    "dosage": "dosage text",
    "organicAlternative": "organic alternative text",
    "timing": "application timing",
    "precautions": "safety precautions"
}}"""

    start_time = time.time()
    try:
        text = execute_gemini_call(prompt, is_vision=False, _module="fertilizer", _crop=crop)
        parsed = json.loads(_clean_json_text(text))
        parsed["source"] = "GEMINI_FALLBACK"
        latency = int((time.time() - start_time) * 1000)
        set_cached_response(cache_key, parsed, query=f"{crop} fertilizer {stage}", source="GEMINI_FALLBACK")
        log_fallback_call("fertilizer", user_uid, crop, trigger_reason, prompt, "GEMINI_FALLBACK", latency, True)
        return parsed

    except AllKeysExhaustedException:
        latency = int((time.time() - start_time) * 1000)
        logger.warning("[fertilizer] All keys exhausted — local fallback for crop=%s", crop)
        log_fallback_call("fertilizer", user_uid, crop, "all_keys_exhausted", f"{crop}-{stage}", "LOCAL_FALLBACK", latency, False)
        return _local_fertilizer_fallback(crop, stage)

    except Exception as exc:
        latency = int((time.time() - start_time) * 1000)
        logger.error("[fertilizer] Gemini failed: %s", exc)
        log_fallback_call("fertilizer", user_uid, crop, f"error:{exc}", f"{crop}-{stage}", "LOCAL_FALLBACK", latency, False)
        return _local_fertilizer_fallback(crop, stage)


def analyze_disease_vision(image_bytes: bytes, crop_hint: str, weather_context: dict,
                            farm_context: dict, user_uid: str) -> dict:
    """
    Disease Detection Gemini Vision Fallback.
    Returns structured disease info — NEVER returns None.
    Priority: Cache → Gemini Vision (with key rotation) → Local DISEASE_DB
    """
    # 1. Image hash cache
    image_hash = hashlib.sha256(image_bytes).hexdigest()
    cache_key = generate_cache_key("disease_vision", image_hash, crop_hint)
    cached = get_cached_response(cache_key)
    if cached:
        return cached

    # 2. Rate / daily limit
    if not check_rate_limit() or not check_and_increment_daily_limit(user_uid):
        log_fallback_call("disease", user_uid, crop_hint, "limit_exceeded", f"vision-{crop_hint}", "LOCAL_FALLBACK", 0, False)
        return _local_disease_fallback(crop_hint)

    # 3. Build prompt
    prompt = f"""Analyze this crop leaf image as an expert plant pathologist.
Crop hint: {crop_hint}
Farm details: {json.dumps(farm_context)}
Current weather: {json.dumps(weather_context)}

Return STRICT JSON only (no markdown wrapper):
{{
    "disease_name": "Name of disease or 'Healthy'",
    "confidence": 85,
    "severity": "Low" | "Medium" | "High",
    "symptoms": "Description of observed symptoms",
    "treatment": "Generic treatment steps",
    "prevention": "Prevention strategy",
    "organic_solution": "Organic management solution",
    "chemical_solution": "Generic chemical category solution"
}}"""

    start_time = time.time()
    try:
        text = execute_gemini_call(prompt, is_vision=True, image_bytes=image_bytes,
                                   _module="disease_vision", _crop=crop_hint)
        parsed = json.loads(_clean_json_text(text))
        parsed["source"] = "GEMINI_FALLBACK"
        latency = int((time.time() - start_time) * 1000)
        set_cached_response(cache_key, parsed, query=f"disease vision {crop_hint}", source="GEMINI_FALLBACK")
        log_fallback_call("disease", user_uid, crop_hint, "vision_fallback", prompt, "GEMINI_FALLBACK", latency, True)
        return parsed

    except AllKeysExhaustedException:
        latency = int((time.time() - start_time) * 1000)
        logger.warning("[disease_vision] All keys exhausted — local DISEASE_DB for crop=%s", crop_hint)
        log_fallback_call("disease", user_uid, crop_hint, "all_keys_exhausted", f"vision-{crop_hint}", "LOCAL_FALLBACK", latency, False)
        return _local_disease_fallback(crop_hint)

    except Exception as exc:
        latency = int((time.time() - start_time) * 1000)
        logger.error("[disease_vision] Failed: %s", exc)
        log_fallback_call("disease", user_uid, crop_hint, f"error:{exc}", f"vision-{crop_hint}", "LOCAL_FALLBACK", latency, False)
        return _local_disease_fallback(crop_hint)


def generate_crop_recommendations(state: str, district: str, weather: dict, soil: str,
                                   water: str, land_area: float, market_data: list,
                                   user_uid: str) -> list:
    """
    Crop Recommendation Gemini Fallback.
    Returns list of recommendations — NEVER returns empty list.
    Priority: Cache → Gemini (with key rotation) → Local seasonal fallback
    """
    # 1. Normalized cache
    cache_key = _make_normalized_cache_key("recommendations", f"crop recommend {state} {district} {soil} {water}")
    cached = get_cached_response(cache_key)
    if cached:
        return cached

    # 2. Rate / daily limit
    if not check_rate_limit() or not check_and_increment_daily_limit(user_uid):
        log_fallback_call("crop_recommendation", user_uid, "Multiple", "limit_exceeded",
                          f"recs-{state}-{district}", "LOCAL_FALLBACK", 0, False)
        return _local_crop_recommendations_fallback(state, soil, water)

    # 3. Build prompt
    market_str = json.dumps(market_data[:10]) if market_data else "None"
    prompt = f"""You are an agricultural advisor recommending the best crops for a farmer in India.
Location: {district}, {state}
Current Weather: {json.dumps(weather)}
Soil Type: {soil}
Water Availability: {water}
Land Area (Acres): {land_area}
Local Market Prices: {market_str}

Return STRICT JSON array only (no markdown wrapper):
[
    {{
        "crop_name": "CropName",
        "suitability_score": 92.5,
        "reasons": "Detailed reason",
        "estimated_yield": "5-6 tons/acre",
        "estimated_duration_days": 110,
        "market_demand": "High"
    }}
]
Recommend exactly 5 crops. Do NOT output empty list."""

    start_time = time.time()
    try:
        text = execute_gemini_call(prompt, is_vision=False, _module="crop_recommendation")
        parsed = json.loads(_clean_json_text(text))
        for item in parsed:
            item["source"] = "GEMINI_FALLBACK"
        latency = int((time.time() - start_time) * 1000)
        set_cached_response(cache_key, parsed, query=f"crop recommend {state} {soil}", source="GEMINI_FALLBACK")
        log_fallback_call("crop_recommendation", user_uid, "Multiple", "fallback", prompt, "GEMINI_FALLBACK", latency, True)
        return parsed

    except AllKeysExhaustedException:
        latency = int((time.time() - start_time) * 1000)
        logger.warning("[crop_rec] All keys exhausted — local seasonal fallback.")
        log_fallback_call("crop_recommendation", user_uid, "Multiple", "all_keys_exhausted",
                          f"recs-{state}-{district}", "LOCAL_FALLBACK", latency, False)
        fb = _local_crop_recommendations_fallback(state, soil, water)
        set_cached_response(cache_key, fb, query=f"crop recommend {state}", source="LOCAL_FALLBACK")
        return fb

    except Exception as exc:
        latency = int((time.time() - start_time) * 1000)
        logger.error("[crop_rec] Failed: %s", exc)
        log_fallback_call("crop_recommendation", user_uid, "Multiple", f"error:{exc}",
                          f"recs-{state}-{district}", "LOCAL_FALLBACK", latency, False)
        return _local_crop_recommendations_fallback(state, soil, water)


def verify_leaf_presence(image_bytes: bytes, user_uid: str = "anonymous") -> dict:
    """
    Leaf Presence Verification — Gemini Vision.
    Returns verification result — NEVER blocks CNN pipeline.
    Priority: Cache → Gemini Vision (with key rotation) → Pass-through (let CNN decide)
    """
    image_hash = hashlib.sha256(image_bytes).hexdigest()
    cache_key = generate_cache_key("leaf_verification", image_hash)
    cached = get_cached_response(cache_key)
    if cached:
        return cached

    # Passthrough default (fail-open: let CNN attempt diagnosis)
    _passthrough = {
        "contains_leaf": True,
        "leaf_confidence": 60.0,
        "suitable_for_diagnosis": True,
        "reason": "Gemini verification unavailable — passed to CNN model.",
        "source": "LOCAL_FALLBACK",
    }

    if not check_rate_limit():
        return _passthrough

    if not check_and_increment_daily_limit(user_uid):
        return _passthrough

    prompt = """Analyze this image and determine:
"Does this image contain a plant leaf suitable for disease diagnosis?"

Reject: humans, faces, documents, screenshots, buildings, vehicles, animals.
Accept: plant leaf, crop canopy, plant disease symptoms.

Return STRICT JSON only (no markdown wrapper):
{
    "suitable_for_diagnosis": true | false,
    "contains_leaf": true | false,
    "leaf_confidence": 0-100,
    "reason": "Short explanation"
}"""

    start_time = time.time()
    try:
        text = execute_gemini_call(prompt, is_vision=True, image_bytes=image_bytes,
                                   _module="leaf_verification")
        cleaned = _clean_json_text(text)
        parsed = json.loads(cleaned)
        result = {
            "contains_leaf": bool(parsed.get("contains_leaf", False)),
            "leaf_confidence": float(parsed.get("leaf_confidence", 0.0)),
            "suitable_for_diagnosis": bool(parsed.get("suitable_for_diagnosis", False)),
            "reason": str(parsed.get("reason", "")),
            "source": "GEMINI_FALLBACK",
        }
        latency = int((time.time() - start_time) * 1000)
        set_cached_response(cache_key, result, query="leaf verification", source="GEMINI_FALLBACK")
        log_fallback_call("leaf_verification", user_uid, "Verification", "image_check", prompt, "GEMINI_FALLBACK", latency, True)
        return result

    except AllKeysExhaustedException:
        logger.warning("[leaf_verification] All keys exhausted — pass-through to CNN.")
        return _passthrough

    except Exception as exc:
        logger.error("[leaf_verification] Failed: %s", exc)
        return _passthrough


def analyze_market_prices(crop: str, state: str, recent_prices: list,
                           user_uid: str = "anonymous") -> dict:
    """
    Market Price Analysis — Gemini Fallback.
    Returns price record or None (callers handle None gracefully).
    Priority: Cache → Gemini (with key rotation) → None (caller uses built-in fallback)
    """
    cache_key = generate_cache_key("market_prices", crop, state, recent_prices)
    cached = get_cached_response(cache_key)
    if cached:
        return cached

    if not check_rate_limit() or not check_and_increment_daily_limit(user_uid):
        log_fallback_call("market_analysis", user_uid, crop, "limit_exceeded",
                          f"market-{crop}-{state}", "LOCAL_FALLBACK", 0, False)
        return None

    recent_prices_str = json.dumps(recent_prices)
    prompt = f"""You are an agricultural commodity market analyst for Indian APMC (Mandi) markets.
Crop: {crop}
State: {state}
Recent Prices Context: {recent_prices_str}

Return STRICT JSON only (no markdown wrapper):
{{
    "min_price": "minimum price in INR per quintal",
    "max_price": "maximum price in INR per quintal",
    "modal_price": "modal price in INR per quintal",
    "market": "typical market name in this state",
    "district": "district name in this state",
    "ai_advice": "1-2 sentences on supply/demand and price trends."
}}
Ensure prices are realistic relative to the context provided."""

    start_time = time.time()
    try:
        text = execute_gemini_call(prompt, is_vision=False, is_json_response=True,
                                   timeout=4.0, _module="market_analysis", _crop=crop)
        parsed = json.loads(_clean_json_text(text))
        result = {
            "id": f"ai_{crop.lower()}_{state.lower().replace(' ', '_')}_{parsed.get('market', 'mandi').lower().replace(' ', '_')}",
            "state": state,
            "district": parsed.get("district", "Unknown"),
            "market": parsed.get("market", "Unknown"),
            "commodity": crop,
            "min_price": parsed.get("min_price", "0"),
            "max_price": parsed.get("max_price", "0"),
            "modal_price": parsed.get("modal_price", "0"),
            "arrival_date": datetime.now().strftime("%Y-%m-%d"),
            "ai_advice": parsed.get("ai_advice", "Market trends stable based on AI estimates."),
            "is_ai_estimate": True,
        }
        latency = int((time.time() - start_time) * 1000)
        set_cached_response(cache_key, result, query=f"{crop} market price {state}", source="GEMINI_FALLBACK")
        log_fallback_call("market_analysis", user_uid, crop, "api_failure_fallback", prompt, "GEMINI_FALLBACK", latency, True)
        return result

    except AllKeysExhaustedException:
        latency = int((time.time() - start_time) * 1000)
        logger.warning("[market] All keys exhausted — returning None (caller uses built-in prices).")
        log_fallback_call("market_analysis", user_uid, crop, "all_keys_exhausted",
                          f"market-{crop}-{state}", "LOCAL_FALLBACK", latency, False)
        return None

    except Exception as exc:
        latency = int((time.time() - start_time) * 1000)
        logger.error("[market_analysis] Failed: %s", exc)
        log_fallback_call("market_analysis", user_uid, crop, f"error:{exc}",
                          f"market-{crop}-{state}", "LOCAL_FALLBACK", latency, False)
        return None


# ─────────────────────────────────────────────────────────────────────────────
# SECTION J — Key Manager Status API (for /api/v1/gemini/status endpoint)
# ─────────────────────────────────────────────────────────────────────────────

def get_key_manager_stats() -> dict:
    """Return sanitized stats about the key pool — no actual key values exposed."""
    return _KEY_MANAGER.stats()


def reset_exhausted_keys():
    """Force reset of exhausted key set (e.g., on daily cron or admin trigger)."""
    _KEY_MANAGER.reset_daily()
