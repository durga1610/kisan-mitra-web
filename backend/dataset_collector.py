"""
dataset_collector.py
--------------------
Kisan Mitra V2 — Real Image Collection Pipeline

Central module for all dataset I/O operations.
Keeps main.py clean by centralising:
  - Image routing (confirmed_correct / needs_review / hard_cases)
  - JSON sidecar metadata writing
  - Dataset statistics queries
  - Per-class readiness scoring
  - Training readiness trigger check

All disk writes are designed to be safe to call from background threads.
"""

import os
import io
import json
import uuid
import logging
import sqlite3
import hashlib
import threading
from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any, List

from PIL import Image
from db_utils import get_db_connection, fire_and_forget_callable

logger = logging.getLogger(__name__)

# ── Path constants ─────────────────────────────────────────────────────────────
from config import DB_PATH, DATASET_V2_DIR, HARD_CASES_DIR
_BASE = os.path.dirname(os.path.abspath(__file__))
ARTIFACT_DIR    = os.environ.get(
    "ARTIFACT_DIR",
    r"C:\Users\durga\.gemini\antigravity-ide\brain\ffa2701b-34c2-4911-b6a3-3afe2b289ce5"
)

# ── Supported crop folders ─────────────────────────────────────────────────────
KNOWN_CROPS = {
    "rice", "cotton", "tomato", "potato", "grape",
    "wheat", "sugarcane", "pulses", "mustard",
    "corn", "maize", "apple", "pepper", "soybean",
    "strawberry", "peach", "cherry", "orange", "blueberry",
}

# ── Production class list (for readiness scoring) ─────────────────────────────
PRODUCTION_CLASSES_FILE = os.path.join(_BASE, "models", "classes.json")

_WRITE_LOCK = threading.Lock()


# ──────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────────────────────────────────────

def _normalise_crop(crop: str) -> str:
    """Map raw crop names to folder-safe names."""
    crop = (crop or "unknown").strip().lower()
    if crop in ("paddy",):
        crop = "rice"
    elif crop in ("corn", "maize"):
        crop = "corn"
    if crop not in KNOWN_CROPS:
        crop = "unknown"
    return crop


def _ensure_dirs(*paths):
    for p in paths:
        os.makedirs(p, exist_ok=True)


def _save_image_and_sidecar(
    image_bytes: bytes,
    folder: str,
    prefix: str,
    meta: Dict[str, Any],
) -> Optional[str]:
    """
    Decode, validate, and save image + JSON sidecar.
    Returns saved image path or None on failure.
    Thread-safe via _WRITE_LOCK.
    """
    try:
        _ensure_dirs(folder)

        # Validate image
        img = Image.open(io.BytesIO(image_bytes))
        img.verify()
        img = Image.open(io.BytesIO(image_bytes))

        # Generate collision-resistant filename
        uid = str(uuid.uuid4())[:8]
        fname = f"{prefix}_{uid}.jpg"
        img_path = os.path.join(folder, fname)
        sidecar_path = os.path.join(folder, f"{prefix}_{uid}.json")

        with _WRITE_LOCK:
            img.convert("RGB").save(img_path, "JPEG", quality=92)
            meta["image_file"] = fname
            with open(sidecar_path, "w", encoding="utf-8") as f:
                json.dump(meta, f, ensure_ascii=False, indent=2)

        logger.info("[DatasetCollector] Saved %s + sidecar", img_path)
        return img_path
    except Exception as e:
        logger.warning("[DatasetCollector] Image save failed: %s", e)
        return None


def _db_insert(row: dict) -> Optional[int]:
    """
    Queue an async insert into dataset_v2_entries.
    Returns None (non-blocking) — the actual insert happens in the bg worker.
    Call _db_insert_sync for tests that need synchronous confirmation.
    """
    def _do_insert():
        try:
            conn = get_db_connection(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO dataset_v2_entries
                (user_uid, diagnosis_id, crop, predicted_disease, confidence,
                 confidence_band, is_correct, collection_type, image_path,
                 state, district, weather_snapshot, source, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row.get("user_uid", "anonymous"),
                row.get("diagnosis_id"),
                row.get("crop", "unknown"),
                row.get("predicted_disease", "Unknown"),
                float(row.get("confidence", 0.0)),
                row.get("confidence_band", "unknown"),
                row.get("is_correct"),
                row.get("collection_type", "unknown"),
                row.get("image_path"),
                row.get("state"),
                row.get("district"),
                json.dumps(row.get("weather_snapshot")) if row.get("weather_snapshot") else None,
                row.get("source"),
                row.get("timestamp", datetime.utcnow().isoformat()),
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error("[DatasetCollector] Async DB insert failed: %s", e)
    fire_and_forget_callable(_do_insert)
    return None


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

def save_to_dataset_v2(
    image_bytes: bytes,
    crop: str,
    predicted_disease: str,
    confidence: float,
    confidence_band: str,
    source: str,
    user_uid: str,
    collection_type: str,      # "confirmed_correct" | "needs_review"
    diagnosis_id: Optional[str] = None,
    state: Optional[str] = None,
    district: Optional[str] = None,
    weather_snapshot: Optional[Dict] = None,
) -> Optional[str]:
    """
    Route an image to dataset_v2/<crop>/<collection_type>/ and persist metadata.

    Returns the saved image path or None.
    Safe to call from background threads.
    """
    crop_folder = _normalise_crop(crop)
    folder = os.path.join(DATASET_V2_DIR, crop_folder, collection_type)

    timestamp = datetime.utcnow().isoformat()
    safe_disease = predicted_disease.lower().replace(" ", "_").replace("/", "-")[:40]
    prefix = f"{crop_folder}_{safe_disease}_{int(confidence)}"

    meta = {
        "diagnosis_id": diagnosis_id,
        "timestamp": timestamp,
        "user_uid": hashlib.sha256(user_uid.encode()).hexdigest()[:16],  # anonymise
        "crop": crop_folder,
        "predicted_disease": predicted_disease,
        "confidence": round(confidence, 2),
        "confidence_band": confidence_band,
        "is_correct": True if collection_type == "confirmed_correct" else (False if collection_type == "needs_review" else None),
        "collection_type": collection_type,
        "state": state,
        "district": district,
        "weather_snapshot": weather_snapshot,
        "source": source,
    }

    img_path = _save_image_and_sidecar(image_bytes, folder, prefix, meta)

    # Persist to SQLite
    meta["image_path"] = img_path
    meta["user_uid"] = user_uid   # store real UID in DB (not anonymised)
    _db_insert(meta)

    return img_path


def save_hard_case(
    image_bytes: bytes,
    reason: str,                # "low_confidence" | "gemini_fallback" | "crop_confusion"
    crop: str,
    predicted_disease: str,
    confidence: float,
    confidence_band: str,
    source: str,
    user_uid: str,
    diagnosis_id: Optional[str] = None,
    state: Optional[str] = None,
    district: Optional[str] = None,
    weather_snapshot: Optional[Dict] = None,
) -> Optional[str]:
    """
    Save an automatically-identified hard case image.
    Runs in background thread — no impact on API response latency.
    """
    valid_reasons = {"low_confidence", "gemini_fallback", "crop_confusion"}
    if reason not in valid_reasons:
        reason = "low_confidence"

    folder = os.path.join(HARD_CASES_DIR, reason)
    crop_folder = _normalise_crop(crop)
    timestamp = datetime.utcnow().isoformat()
    safe_disease = predicted_disease.lower().replace(" ", "_").replace("/", "-")[:40]
    prefix = f"hc_{crop_folder}_{safe_disease}_{int(confidence)}"

    collection_type = f"hard_case_{reason}"
    meta = {
        "diagnosis_id": diagnosis_id,
        "timestamp": timestamp,
        "user_uid": hashlib.sha256(user_uid.encode()).hexdigest()[:16],
        "crop": crop_folder,
        "predicted_disease": predicted_disease,
        "confidence": round(confidence, 2),
        "confidence_band": confidence_band,
        "is_correct": None,
        "collection_type": collection_type,
        "hard_case_reason": reason,
        "state": state,
        "district": district,
        "weather_snapshot": weather_snapshot,
        "source": source,
    }

    img_path = _save_image_and_sidecar(image_bytes, folder, prefix, meta)

    meta["image_path"] = img_path
    meta["user_uid"] = user_uid
    _db_insert(meta)

    return img_path


# ──────────────────────────────────────────────────────────────────────────────
# Statistics
# ──────────────────────────────────────────────────────────────────────────────

def get_dataset_stats() -> Dict[str, Any]:
    """
    Returns comprehensive dataset statistics from the filesystem + SQLite.
    Used by GET /api/v1/dataset/stats.
    """
    today_str = date.today().isoformat()
    week_ago_str = (date.today() - timedelta(days=7)).isoformat()

    stats = {
        "images_today": 0,
        "images_this_week": 0,
        "total_images": 0,
        "confirmed_correct": 0,
        "needs_review": 0,
        "hard_cases": 0,
        "confirmed_correct_pct": 0.0,
        "needs_review_pct": 0.0,
        "per_crop": {},
        "per_disease": {},
        "hard_cases_by_reason": {
            "low_confidence": 0,
            "gemini_fallback": 0,
            "crop_confusion": 0,
        },
    }

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Check table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='dataset_v2_entries'")
        if not cursor.fetchone():
            conn.close()
            return stats

        # Total counts
        cursor.execute("SELECT COUNT(*) FROM dataset_v2_entries")
        stats["total_images"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM dataset_v2_entries WHERE timestamp >= ?", (today_str,))
        stats["images_today"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM dataset_v2_entries WHERE timestamp >= ?", (week_ago_str,))
        stats["images_this_week"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM dataset_v2_entries WHERE collection_type = 'confirmed_correct'")
        stats["confirmed_correct"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM dataset_v2_entries WHERE collection_type = 'needs_review'")
        stats["needs_review"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM dataset_v2_entries WHERE collection_type LIKE 'hard_case_%'")
        stats["hard_cases"] = cursor.fetchone()[0]

        # Per-reason hard case counts
        for reason in stats["hard_cases_by_reason"]:
            cursor.execute(
                "SELECT COUNT(*) FROM dataset_v2_entries WHERE collection_type = ?",
                (f"hard_case_{reason}",)
            )
            stats["hard_cases_by_reason"][reason] = cursor.fetchone()[0]

        # Per-crop counts
        cursor.execute("SELECT crop, COUNT(*) as cnt FROM dataset_v2_entries GROUP BY crop ORDER BY cnt DESC")
        for row in cursor.fetchall():
            stats["per_crop"][row["crop"]] = row["cnt"]

        # Per-disease counts (top 20)
        cursor.execute("""
            SELECT predicted_disease, COUNT(*) as cnt
            FROM dataset_v2_entries
            GROUP BY predicted_disease
            ORDER BY cnt DESC
            LIMIT 20
        """)
        for row in cursor.fetchall():
            stats["per_disease"][row["predicted_disease"]] = row["cnt"]

        conn.close()

        # Percentage calculations
        feedback_total = stats["confirmed_correct"] + stats["needs_review"]
        if feedback_total > 0:
            stats["confirmed_correct_pct"] = round(stats["confirmed_correct"] / feedback_total * 100, 1)
            stats["needs_review_pct"] = round(stats["needs_review"] / feedback_total * 100, 1)

    except Exception as e:
        logger.error("[DatasetCollector] Stats query failed: %s", e)

    return stats


# ──────────────────────────────────────────────────────────────────────────────
# Readiness Scoring
# ──────────────────────────────────────────────────────────────────────────────

def _load_production_classes() -> List[str]:
    try:
        with open(PRODUCTION_CLASSES_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def get_readiness_scores() -> Dict[str, Any]:
    """
    Per-class dataset readiness scores.
    Counts real images in dataset_v2/ + existing dataset/ for each production class.
    Used by GET /api/v1/dataset/readiness.
    """
    CLASSES = _load_production_classes()
    TARGET_MIN  = 200   # minimum for training
    TARGET_FULL = 500   # ideal for strong generalisation

    scores = {}

    for cls in CLASSES:
        # Count images already in dataset_v2 (real, farmer-uploaded)
        crop = _normalise_crop(cls.split("___")[0] if "___" in cls else cls)
        v2_correct = 0
        v2_review  = 0

        correct_dir = os.path.join(DATASET_V2_DIR, crop, "confirmed_correct")
        review_dir  = os.path.join(DATASET_V2_DIR, crop, "needs_review")

        if os.path.isdir(correct_dir):
            v2_correct = len([f for f in os.listdir(correct_dir) if f.endswith(".jpg")])
        if os.path.isdir(review_dir):
            v2_review  = len([f for f in os.listdir(review_dir) if f.endswith(".jpg")])

        # Count existing dataset/ real images for this class
        existing_train = 0
        existing_real  = 0
        existing_synth = 0
        for split in ("train", "val", "test"):
            cls_dir = os.path.join(_BASE, "dataset", split, cls)
            if os.path.isdir(cls_dir):
                imgs = [f for f in os.listdir(cls_dir) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
                existing_train += len(imgs)
                # Heuristic: augmented images have suffixes like _aug_, _flip_, _rot_
                synth_count = sum(1 for f in imgs if any(tag in f.lower() for tag in ("_aug", "_flip", "_rot", "_crop", "_noise", "synthetic")))
                existing_synth += synth_count
                existing_real  += len(imgs) - synth_count

        total_real = existing_real + v2_correct
        total_all  = existing_train + v2_correct + v2_review

        scores[cls] = {
            "total_images":       total_all,
            "real_images":        total_real,
            "synthetic_images":   existing_synth,
            "v2_confirmed":       v2_correct,
            "v2_needs_review":    v2_review,
            "gap_to_200":         max(0, TARGET_MIN  - total_real),
            "gap_to_500":         max(0, TARGET_FULL - total_real),
            "is_ready_min":       total_real >= TARGET_MIN,
            "is_ready_full":      total_real >= TARGET_FULL,
        }

    # Summary
    ready_min  = sum(1 for v in scores.values() if v["is_ready_min"])
    ready_full = sum(1 for v in scores.values() if v["is_ready_full"])
    total_real = sum(v["real_images"] for v in scores.values())

    return {
        "classes": scores,
        "summary": {
            "total_classes":       len(CLASSES),
            "ready_for_training":  ready_min,
            "fully_ready":         ready_full,
            "total_real_images":   total_real,
            "training_unblocked":  ready_min == len(CLASSES),
        }
    }


def check_training_readiness() -> Dict[str, Any]:
    """
    Check if the dataset meets the 200-real-image threshold for ALL production classes.
    Returns: { ready: bool, summary: str, blocking_classes: [...] }
    """
    result = get_readiness_scores()
    summary = result["summary"]
    blocking = [
        cls for cls, info in result["classes"].items()
        if not info["is_ready_min"]
    ]

    if summary["training_unblocked"]:
        message = (
            "✅ DATASET READY FOR EfficientNet-B2 TRAINING\n"
            f"All {summary['total_classes']} production classes have ≥ 200 real images.\n"
            f"Total real images collected: {summary['total_real_images']:,}"
        )
    else:
        message = (
            f"⏳ NOT YET READY — {len(blocking)} classes below 200 real images.\n"
            f"Progress: {summary['ready_for_training']}/{summary['total_classes']} classes ready.\n"
            f"Total real images so far: {summary['total_real_images']:,}"
        )

    return {
        "ready": summary["training_unblocked"],
        "message": message,
        "classes_ready": summary["ready_for_training"],
        "classes_total": summary["total_classes"],
        "total_real_images": summary["total_real_images"],
        "blocking_classes": blocking,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Self-test (run directly: python dataset_collector.py)
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    print("=" * 60)
    print("  DatasetCollector Self-Test")
    print("=" * 60)

    print("\n[1] Dataset Stats:")
    stats = get_dataset_stats()
    print(f"  Total images   : {stats['total_images']}")
    print(f"  Today          : {stats['images_today']}")
    print(f"  This week      : {stats['images_this_week']}")
    print(f"  Confirmed OK   : {stats['confirmed_correct']} ({stats['confirmed_correct_pct']}%)")
    print(f"  Needs review   : {stats['needs_review']} ({stats['needs_review_pct']}%)")
    print(f"  Hard cases     : {stats['hard_cases']}")
    print(f"  Per-crop       : {stats['per_crop']}")

    print("\n[2] Readiness Scores (top 5 classes by gap):")
    readiness = get_readiness_scores()
    summary = readiness["summary"]
    print(f"  Classes ready (≥200 real): {summary['ready_for_training']}/{summary['total_classes']}")
    print(f"  Total real images collected: {summary['total_real_images']}")
    sorted_by_gap = sorted(readiness["classes"].items(), key=lambda x: -x[1]["gap_to_200"])
    for cls, info in sorted_by_gap[:5]:
        print(f"  {cls:<40} real={info['real_images']:<4} gap_to_200={info['gap_to_200']}")

    print("\n[3] Training Readiness Check:")
    tr = check_training_readiness()
    print(f"  Ready: {tr['ready']}")
    print(f"  {tr['message']}")
    if tr["blocking_classes"]:
        print(f"  Blocking classes ({len(tr['blocking_classes'])}): {tr['blocking_classes'][:5]}")

    print("\n✅ Self-test complete.")
