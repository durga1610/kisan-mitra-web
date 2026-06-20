import os
import time
import logging
import json
import hashlib
import sqlite3
from datetime import datetime
import google.generativeai as genai
from google.api_core.exceptions import GoogleAPIError

logger = logging.getLogger(__name__)


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

from config import DB_PATH

# Initialize Gemini client
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    logger.info("[Gemini Fallback] google-generativeai client configured successfully.")
else:
    logger.warning("[Gemini Fallback] GEMINI_API_KEY env var not set. Fallbacks will be bypassed.")

# Initialize database schema for Gemini tracking
def init_gemini_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Log table
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
        )
        """)
        
        # Daily limit tracking table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS gemini_daily_usage (
            user_uid TEXT,
            date TEXT,
            call_count INTEGER,
            PRIMARY KEY (user_uid, date)
        )
        """)
        
        # Persistent cache table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS gemini_response_cache (
            cache_key TEXT PRIMARY KEY,
            response_json TEXT,
            cached_at TEXT
        )
        """)
        
        conn.commit()
        conn.close()
        logger.info("[Gemini Fallback] Gemini SQLite tables checked/created.")
    except Exception as e:
        logger.error(f"[Gemini Fallback] Error initializing Gemini DB: {e}")

# Call DB initialization on import
init_gemini_db()

# Simple in-memory rate limiting state (10 calls/minute)
rate_limit_timestamps = []

def check_rate_limit() -> bool:
    """Returns True if within rate limit (max 10 requests per minute)."""
    if os.getenv("TESTING") == "1":
        return True
    global rate_limit_timestamps
    now = time.time()
    # Filter timestamps within the last 60 seconds
    rate_limit_timestamps = [t for t in rate_limit_timestamps if now - t < 60]
    if len(rate_limit_timestamps) >= 10:
        logger.warning("[Gemini Fallback] In-memory rate limit exceeded (10 req/min).")
        return False
    rate_limit_timestamps.append(now)
    return True

# Helper: Cache key generator
def generate_cache_key(*args, **kwargs) -> str:
    serialized = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

# Helper: Get persistent cache response
def get_cached_response(cache_key: str) -> dict:
    """Retrieves response from SQLite if cached within last 24 hours."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT response_json, cached_at FROM gemini_response_cache WHERE cache_key = ?",
            (cache_key,)
        )
        row = cursor.fetchone()
        conn.close()
        
        if row:
            response_json, cached_at_str = row
            cached_at = datetime.fromisoformat(cached_at_str)
            # Check TTL of 24 hours
            if (datetime.now() - cached_at).total_seconds() < 86400:
                logger.info(f"[Gemini Fallback] Persistent cache hit for key: {cache_key}")
                return json.loads(response_json)
            else:
                # Cache expired, delete it
                logger.info(f"[Gemini Fallback] Persistent cache expired for key: {cache_key}")
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM gemini_response_cache WHERE cache_key = ?", (cache_key,))
                conn.commit()
                conn.close()
    except Exception as e:
        logger.error(f"[Gemini Fallback] Cache read error: {e}")
    return None

# Helper: Set persistent cache response
def set_cached_response(cache_key: str, response: dict):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO gemini_response_cache (cache_key, response_json, cached_at) VALUES (?, ?, ?)",
            (cache_key, json.dumps(response), datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        logger.info(f"[Gemini Fallback] Response cached persistently for key: {cache_key}")
    except Exception as e:
        logger.error(f"[Gemini Fallback] Cache write error: {e}")

# Helper: Check and increment daily limit (max 5 calls per user per day)
def check_and_increment_daily_limit(user_uid: str) -> bool:
    """Returns True if user is under daily limit of 5 calls, False otherwise."""
    if os.getenv("TESTING") == "1":
        return True
    if not user_uid:
        # If no user_uid is provided, allow the call but warn
        logger.warning("[Gemini Fallback] No user_uid provided. Daily limit check bypassed.")
        return True
    
    current_date = datetime.now().strftime("%Y-%m-%d")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT call_count FROM gemini_daily_usage WHERE user_uid = ? AND date = ?",
            (user_uid, current_date)
        )
        row = cursor.fetchone()
        
        if row:
            call_count = row[0]
            if call_count >= 5:
                logger.warning(f"[Gemini Fallback] User {user_uid} has exceeded daily fallback limit of 5 calls.")
                conn.close()
                return False
            cursor.execute(
                "UPDATE gemini_daily_usage SET call_count = call_count + 1 WHERE user_uid = ? AND date = ?",
                (user_uid, current_date)
            )
        else:
            cursor.execute(
                "INSERT INTO gemini_daily_usage (user_uid, date, call_count) VALUES (?, ?, 1)",
                (user_uid, current_date)
            )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"[Gemini Fallback] Error updating daily usage count: {e}")
        return True # fail-open for DB errors

# Helper: Log fallback usage
def log_fallback_call(module: str, user_uid: str, crop: str, trigger_reason: str, prompt_text: str, source: str, latency_ms: int, success: bool):
    try:
        prompt_hash = hashlib.sha256(prompt_text.encode("utf-8")).hexdigest()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO gemini_fallback_log (timestamp, module, user_uid, crop, trigger_reason, prompt_hash, response_source, latency_ms, success) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (datetime.now().isoformat(), module, user_uid, crop, trigger_reason, prompt_hash, source, latency_ms, 1 if success else 0)
        )
        conn.commit()
        conn.close()
        logger.info(f"[Gemini Fallback] Logged {module} fallback call. Source={source}, Success={success}, Latency={latency_ms}ms")
    except Exception as e:
        logger.error(f"[Gemini Fallback] Error logging fallback call: {e}")

# Core LLM Call with Retry and Timeout
def execute_gemini_call(
    prompt_text: str,
    is_vision: bool = False,
    image_bytes: bytes = None,
    mime_type: str = "image/jpeg",
    is_json_response: bool = False,
    max_tokens: int = 4096,
) -> str:
    """Executes a call to Gemini 2.5 Flash with retries and a strict timeout.

    Args:
        prompt_text: The prompt to send.
        is_vision: Whether this is a vision (image) call.
        image_bytes: Image bytes for vision calls.
        mime_type: MIME type of the image.
        is_json_response: If True, requests JSON-formatted output and uses
                          higher token limit to prevent truncation.
        max_tokens: Maximum output tokens. Default 4096 prevents truncation
                    of long JSON responses. Use lower value for short text.
    """
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not configured.")

    model_name = "gemini-2.5-flash"

    # 3 Retries
    retries = 3
    total_timeout = 30.0 if is_vision else 10.0
    start_all = time.time()

    import concurrent.futures

    for attempt in range(retries):
        elapsed_so_far = time.time() - start_all
        remaining_timeout = total_timeout - elapsed_so_far
        if remaining_timeout <= 0.5:
            raise TimeoutError(f"Gemini call timed out after {elapsed_so_far:.2f}s (no time left for retry).")

        # Per-attempt timeout budget
        attempt_timeout = min(remaining_timeout, 8.0 if not is_vision else 25.0)

        try:
            model = genai.GenerativeModel(model_name)

            # Configure generation options — use higher token limit for JSON
            # to prevent truncation of structured responses mid-string
            gen_config_args = {
                "temperature": 0.2,
                "max_output_tokens": max_tokens,
            }
            # Request JSON MIME type when we expect structured output
            # This helps Gemini produce clean JSON without markdown wrappers
            if is_json_response:
                gen_config_args["response_mime_type"] = "application/json"

            generation_config = genai.types.GenerationConfig(**gen_config_args)

            def run_api_call():
                if is_vision:
                    if not image_bytes:
                        raise ValueError("Image bytes required for Vision fallback call.")
                    content_part = {
                        "mime_type": mime_type,
                        "data": image_bytes
                    }
                    return model.generate_content(
                        [prompt_text, content_part],
                        generation_config=generation_config,
                        request_options={"timeout": attempt_timeout}
                    )
                else:
                    return model.generate_content(
                        prompt_text,
                        generation_config=generation_config,
                        request_options={"timeout": attempt_timeout}
                    )

            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(run_api_call)
                try:
                    response = future.result(timeout=attempt_timeout)
                except concurrent.futures.TimeoutError:
                    raise TimeoutError(f"Gemini call timed out after {attempt_timeout:.2f}s.")

            if not response.text:
                raise ValueError("Empty response received from Gemini.")

            return response.text.strip()

        except Exception as e:
            logger.warning("[Gemini Fallback] Attempt %d failed: %s", attempt + 1, e)
            if attempt < retries - 1:
                elapsed_so_far = time.time() - start_all
                sleep_time = 1.0  # Reduce backoff to fit within 10s budget
                if elapsed_so_far + sleep_time < total_timeout:
                    time.sleep(sleep_time)
                else:
                    raise TimeoutError("Gemini call timed out (insufficient time to sleep for retry).")
            else:
                raise e


# --- Public Interfaces ---

def generate_advisory(message: str, farm_context: dict, weather_context: dict, trigger_reason: str, user_uid: str) -> dict:
    """AI Advisor Gemini Fallback."""
    cache_key = generate_cache_key("advisory", message, farm_context, weather_context)
    cached = get_cached_response(cache_key)
    if cached:
        return cached

    crop = farm_context.get("crop", "Unknown") if farm_context else "Unknown"
    
    # Check limits
    if not check_rate_limit() or not check_and_increment_daily_limit(user_uid):
        # Gracefully return a standard structured fallback format from local rules or raise
        log_fallback_call("advisory", user_uid, crop, "limit_exceeded", message, "LOCAL_ENGINE", 0, False)
        return None

    # Construct prompt
    prompt = f"""You are an agricultural expert for Indian farmers.
Use the following context if helpful:
- Farm Details: {json.dumps(farm_context)}
- Current Weather: {json.dumps(weather_context)}
- User Query: {message}

Rules:
1. Always give actionable, practical guidance in 2-4 sentences.
2. Speak directly to the farmer.
3. If information is uncertain, clearly state assumptions.
4. Do not recommend specific chemical dosages or fertilizer quantities. Suggest organic/safe alternatives if unsure.
5. Do not say "Unsupported crop" or "N/A" or "Data unavailable". Always help the farmer.

Response:"""

    start_time = time.time()
    try:
        text = execute_gemini_call(prompt, is_vision=False)
        result = {"text": text, "source": "GEMINI_FALLBACK"}
        
        latency = int((time.time() - start_time) * 1000)
        set_cached_response(cache_key, result)
        log_fallback_call("advisory", user_uid, crop, trigger_reason, prompt, "GEMINI_FALLBACK", latency, True)
        return result
    except Exception as e:
        latency = int((time.time() - start_time) * 1000)
        log_fallback_call("advisory", user_uid, crop, f"error: {str(e)}", prompt, "LOCAL_ENGINE", latency, False)
        return None

def generate_fertilizer_advice(crop: str, age: int, stage: str, soil: str, weather: str, trigger_reason: str, user_uid: str) -> dict:
    """Fertilizer Gemini Fallback."""
    cache_key = generate_cache_key("fertilizer", crop, age, stage, soil, weather)
    cached = get_cached_response(cache_key)
    if cached:
        return cached

    # Check limits
    if not check_rate_limit() or not check_and_increment_daily_limit(user_uid):
        log_fallback_call("fertilizer", user_uid, crop, "limit_exceeded", f"{crop}-{stage}", "LOCAL_ENGINE", 0, False)
        return None

    prompt = f"""You are an expert agronomist providing fertilizer schedules for Indian farmers.
Generate a fertilizer recommendation for the following crop state:
- Crop Name: {crop}
- Crop Age (Days): {age}
- Growth Stage: {stage}
- Soil Type: {soil}
- Weather Condition: {weather}

Rules:
1. Return your response in STRICT JSON format matching this schema. Do not output markdown wrapper blocks (no ```json).
2. JSON Schema:
{{
    "crop": "{crop}",
    "stage": "{stage}",
    "age": {age},
    "recommendation": "recommendation text",
    "dosage": "dosage text",
    "organicAlternative": "organic alternative text",
    "timing": "application timing",
    "precautions": "safety precautions"
}}
3. Do not invent specific high-risk pesticide dosages.
4. Do not return "N/A" or "Unsupported crop". Provide general best practice schedules for this crop family if specific schedule is not standard.
"""

    start_time = time.time()
    try:
        text = execute_gemini_call(prompt, is_vision=False)
        # Parse JSON — strip markdown fences if present
        try:
            parsed = json.loads(_clean_json_text(text))
        except json.JSONDecodeError as je:
            logger.error("[Fertilizer] JSON parse error: %s. Raw text (first 200): %s", je, text[:200])
            raise
        parsed["source"] = "GEMINI_FALLBACK"

        latency = int((time.time() - start_time) * 1000)
        set_cached_response(cache_key, parsed)
        log_fallback_call("fertilizer", user_uid, crop, trigger_reason, prompt, "GEMINI_FALLBACK", latency, True)
        return parsed
    except Exception as e:
        latency = int((time.time() - start_time) * 1000)
        logger.error("[Fertilizer] Fallback failed: %s", e)
        log_fallback_call("fertilizer", user_uid, crop, f"error: {str(e)}", prompt, "LOCAL_ENGINE", latency, False)
        return None

def analyze_disease_vision(image_bytes: bytes, crop_hint: str, weather_context: dict, farm_context: dict, user_uid: str) -> dict:
    """Disease Detection Gemini Vision Fallback."""
    # Since we can't cache raw image bytes easily with sha256 of the whole image, we hash the image bytes to form a key
    image_hash = hashlib.sha256(image_bytes).hexdigest()
    cache_key = generate_cache_key("disease_vision", image_hash, crop_hint)
    cached = get_cached_response(cache_key)
    if cached:
        return cached

    # Check limits
    if not check_rate_limit() or not check_and_increment_daily_limit(user_uid):
        log_fallback_call("disease", user_uid, crop_hint, "limit_exceeded", f"vision-{crop_hint}", "LOCAL_ENGINE", 0, False)
        return None

    prompt = f"""Analyze this crop leaf image as an expert plant pathologist.
Crop hint: {crop_hint}
Farm details: {json.dumps(farm_context)}
Current weather: {json.dumps(weather_context)}

Rules:
1. Return your response in STRICT JSON format matching the schema below. Do not wrap in ```json or other text.
2. JSON Schema:
{{
    "disease_name": "Name of disease or 'Healthy'",
    "confidence": 85,  // integer between 0 and 100
    "severity": "Low" | "Medium" | "High",
    "symptoms": "Description of observed symptoms",
    "treatment": "Generic treatment steps. Do not include strict dosage volumes.",
    "prevention": "Prevention strategy",
    "organic_solution": "Organic management solution",
    "chemical_solution": "Generic chemical category solution"
}}
3. Do not return empty fields or say you can't analyze. If it is hard to tell, provide your best clinical diagnosis based on the crop type and symptoms seen, indicating confidence accordingly.
"""

    start_time = time.time()
    try:
        text = execute_gemini_call(prompt, is_vision=True, image_bytes=image_bytes)
        # Parse JSON — strip markdown fences if present
        try:
            parsed = json.loads(_clean_json_text(text))
        except json.JSONDecodeError as je:
            logger.error("[Disease Vision] JSON parse error: %s. Raw text (first 200): %s", je, text[:200])
            raise
        parsed["source"] = "GEMINI_FALLBACK"

        latency = int((time.time() - start_time) * 1000)
        set_cached_response(cache_key, parsed)
        log_fallback_call("disease", user_uid, crop_hint, "low_confidence_or_unsupported", prompt, "GEMINI_FALLBACK", latency, True)
        return parsed
    except Exception as e:
        latency = int((time.time() - start_time) * 1000)
        logger.error("[Disease Vision] Fallback failed: %s", e)
        log_fallback_call("disease", user_uid, crop_hint, f"error: {str(e)}", prompt, "LOCAL_ENGINE", latency, False)
        return None

def generate_crop_recommendations(state: str, district: str, weather: dict, soil: str, water: str, land_area: float, market_data: list, user_uid: str) -> list:
    """Crop Recommendation Gemini Fallback."""
    cache_key = generate_cache_key("recommendations", state, district, weather, soil, water, land_area)
    cached = get_cached_response(cache_key)
    if cached:
        return cached

    # Check limits
    if not check_rate_limit() or not check_and_increment_daily_limit(user_uid):
        log_fallback_call("crop_recommendation", user_uid, "Multiple", "limit_exceeded", f"recs-{state}-{district}", "LOCAL_ENGINE", 0, False)
        return []

    # Format market data briefly
    market_str = json.dumps(market_data[:10]) if market_data else "None"

    prompt = f"""You are an agricultural advisor recommending the best crops for a farmer in India.
Provide recommendations based on:
- Location: {district}, {state}
- Current Weather: {json.dumps(weather)}
- Soil Type: {soil}
- Water Availability: {water}
- Land Area (Acres): {land_area}
- Local Market Prices: {market_str}

Rules:
1. Recommend the top 5 most suitable crops.
2. Return your response in STRICT JSON format matching the schema below. Do not wrap in ```json or text.
3. JSON Schema:
[
    {{
        "crop_name": "Tomato",
        "suitability_score": 92.5,  // float between 0 and 100
        "reasons": "Detailed reason why suitable based on weather, soil, and market pricing.",
        "estimated_yield": "5-6 tons/acre",
        "estimated_duration_days": 110,
        "market_demand": "High" | "Medium" | "Low"
    }}
]
4. Do not output empty list or placeholder names. Always recommend viable crops.
"""

    start_time = time.time()
    try:
        text = execute_gemini_call(prompt, is_vision=False)
        # Parse JSON — strip markdown fences if present
        try:
            parsed = json.loads(_clean_json_text(text))
        except json.JSONDecodeError as je:
            logger.error("[CropRec] JSON parse error: %s. Raw text (first 200): %s", je, text[:200])
            raise

        # Add source and ensure correct structure
        for item in parsed:
            item["source"] = "GEMINI_FALLBACK"

        latency = int((time.time() - start_time) * 1000)
        set_cached_response(cache_key, parsed)
        log_fallback_call("crop_recommendation", user_uid, "Multiple", "low_ml_confidence_or_no_recs", prompt, "GEMINI_FALLBACK", latency, True)
        return parsed
    except Exception as e:
        latency = int((time.time() - start_time) * 1000)
        logger.error("[CropRec] Fallback failed: %s", e)
        log_fallback_call("crop_recommendation", user_uid, "Multiple", f"error: {str(e)}", prompt, "LOCAL_ENGINE", latency, False)
        return []

def verify_leaf_presence(image_bytes: bytes, user_uid: str = "anonymous") -> dict:
    """
    Step 2: Plant Detection Validation.
    Queries Gemini Vision to verify if the image contains a plant leaf suitable for disease diagnosis.
    Returns:
    {
      "contains_leaf": bool,
      "leaf_confidence": float,
      "suitable_for_diagnosis": bool,
      "reason": str
    }
    """
    image_hash = hashlib.sha256(image_bytes).hexdigest()
    cache_key = generate_cache_key("leaf_verification", image_hash)
    cached = get_cached_response(cache_key)
    if cached:
        return cached

    prompt = """Analyze this image. You must answer the following question:
"Does this image contain a plant leaf suitable for disease diagnosis?"

Also verify if the image contains:
- Plant
- Leaf
- Crop canopy
- Plant disease symptoms

You must reject:
- Humans
- Faces
- Documents
- Screenshots
- Architecture diagrams
- Charts
- Text-heavy images
- Buildings
- Roads
- Vehicles
- Animals
- Household objects

Return your response in STRICT JSON format matching the schema below. Do not wrap in ```json or any other text.

JSON Schema:
{
    "suitable_for_diagnosis": true | false,
    "contains_leaf": true | false,
    "leaf_confidence": 0-100,  // Integer indicating percentage confidence (0-100) that a plant/leaf/crop is present and suitable
    "reason": "Short explanation of the decision"
}
"""
    # Check rate limit
    if not check_rate_limit():
        logger.warning("[Leaf Verification] In-memory rate limit exceeded.")
        return {
            "contains_leaf": False,
            "leaf_confidence": 0.0,
            "suitable_for_diagnosis": False,
            "reason": "Rate limit exceeded"
        }
        
    # Check daily limit unless testing is active
    is_testing = os.getenv("TESTING") == "1"
    if not is_testing:
        if not check_and_increment_daily_limit(user_uid):
            logger.warning(f"[Leaf Verification] Daily limit exceeded for user: {user_uid}")
            return {
                "contains_leaf": False,
                "leaf_confidence": 0.0,
                "suitable_for_diagnosis": False,
                "reason": "Daily limit exceeded"
            }

    start_time = time.time()
    try:
        text = execute_gemini_call(prompt, is_vision=True, image_bytes=image_bytes)
        
        # Clean potential markdown JSON wrappers
        cleaned = text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
        
        parsed = json.loads(cleaned)
        result = {
            "contains_leaf": bool(parsed.get("contains_leaf", False)),
            "leaf_confidence": float(parsed.get("leaf_confidence", 0.0)),
            "suitable_for_diagnosis": bool(parsed.get("suitable_for_diagnosis", False)),
            "reason": str(parsed.get("reason", ""))
        }
        latency = int((time.time() - start_time) * 1000)
        set_cached_response(cache_key, result)
        log_fallback_call("leaf_verification", user_uid, "Verification", "image_check", prompt, "GEMINI_FALLBACK", latency, True)
        return result
    except Exception as e:
        latency = int((time.time() - start_time) * 1000)
        logger.error(f"[Leaf Verification] Gemini Vision call failed: {e}")
        log_fallback_call("leaf_verification", user_uid, "Verification", f"error: {str(e)}", prompt, "LOCAL_ENGINE", latency, False)
        return {
            "contains_leaf": False,
            "leaf_confidence": 0.0,
            "suitable_for_diagnosis": False,
            "reason": f"Verification error: {str(e)}"
        }

def analyze_market_prices(crop: str, state: str, recent_prices: list, user_uid: str = "anonymous") -> dict:
    """Trigger Gemini to analyze crop prices and trends in a state given recent prices."""
    cache_key = generate_cache_key("market_prices", crop, state, recent_prices)
    cached = get_cached_response(cache_key)
    if cached:
        return cached

    # Check limits
    if not check_rate_limit() or not check_and_increment_daily_limit(user_uid):
        log_fallback_call("market_analysis", user_uid, crop, "limit_exceeded", f"market-{crop}-{state}", "LOCAL_ENGINE", 0, False)
        return None

    recent_prices_str = json.dumps(recent_prices)
    prompt = f"""You are an agricultural commodity market analyst for Indian APMC (Mandi) markets.
Estimate the current prices and provide a market trend analysis for:
- Crop: {crop}
- State: {state}
- Recent Prices Context: {recent_prices_str}

Rules:
1. Output your response in STRICT JSON format matching the schema below. Do not wrap in ```json or any other text.
2. JSON Schema:
{{
    "min_price": "minimum price in INR per quintal (e.g. '1800')",
    "max_price": "maximum price in INR per quintal (e.g. '2600')",
    "modal_price": "modal/average price in INR per quintal (e.g. '2200')",
    "market": "typical market name in this state (e.g. 'Koyambedu')",
    "district": "district name in this state (e.g. 'Chennai')",
    "ai_advice": "1-2 sentences explaining supply/demand dynamics and price trends."
}}
3. Ensure the estimated prices are realistic relative to the recent prices context if provided.
"""

    start_time = time.time()
    try:
        text = execute_gemini_call(prompt, is_vision=False, is_json_response=True)
        parsed = json.loads(_clean_json_text(text))
        
        # Ensure it fits the Mandi record structure
        result = {
            "id": f"ai_{crop.lower()}_{state.lower().replace(' ', '_')}_{parsed.get('market', 'default').lower().replace(' ', '_')}",
            "state": state,
            "district": parsed.get("district", "Unknown"),
            "market": parsed.get("market", "Unknown"),
            "commodity": crop,
            "min_price": parsed.get("min_price", "0"),
            "max_price": parsed.get("max_price", "0"),
            "modal_price": parsed.get("modal_price", "0"),
            "arrival_date": datetime.now().strftime("%Y-%m-%d"),
            "ai_advice": parsed.get("ai_advice", "Market trends are currently stable based on AI estimates."),
            "is_ai_estimate": True
        }

        latency = int((time.time() - start_time) * 1000)
        set_cached_response(cache_key, result)
        log_fallback_call("market_analysis", user_uid, crop, "api_failure_fallback", prompt, "GEMINI_FALLBACK", latency, True)
        return result
    except Exception as e:
        latency = int((time.time() - start_time) * 1000)
        logger.error("[Market Analysis] Fallback failed: %s", e)
        log_fallback_call("market_analysis", user_uid, crop, f"error: {str(e)}", prompt, "LOCAL_ENGINE", latency, False)
        return None

