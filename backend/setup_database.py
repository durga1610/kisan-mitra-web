"""
setup_database.py
-----------------
Initialise the SQLite database schema for Kisan Mitra.

F-15 fix: removed all DELETE FROM statements from init_db().
Seed data is now inserted only once, when the database is freshly empty.
This preserves real farmer data across server restarts and redeployments.
"""

import logging
import os
import sqlite3
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

from config import DB_PATH


# ---------------------------------------------------------------------------
# Demo / seed data  (only inserted on first startup)
# ---------------------------------------------------------------------------

def _seed_test_data(cursor: sqlite3.Cursor) -> None:
    """Insert demo/test rows. Called only when all tables are empty."""
    import json

    crop_catalog_data = [
        ("tomato",    "tomato"),
        ("rice",      "rice"),
        ("paddy",     "paddy"),
        ("cotton",    "cotton"),
        ("wheat",     "wheat"),
        ("maize",     "maize"),
        ("corn",      "corn"),
        ("potato",    "potato"),
        ("mustard",   "mustard"),
        ("sugarcane", "sugarcane"),
        ("banana",    "banana"),
        ("rose",      "rose"),
    ]

    # Extend with entries from crop_profiles.json when present
    profiles_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "crop_profiles.json")
    if os.path.exists(profiles_path):
        try:
            with open(profiles_path, "r", encoding="utf-8") as f:
                profiles = json.load(f)
            catalog_set = {item[0] for item in crop_catalog_data}
            for crop_key, crop_info in profiles.items():
                if crop_key not in catalog_set:
                    crop_catalog_data.append((crop_key, crop_info["name"].lower()))
                    catalog_set.add(crop_key)
        except Exception as exc:
            logger.warning("[Database] Error extending crop catalog from profiles: %s", exc)

    cursor.executemany("INSERT INTO crop_catalog VALUES (?, ?)", crop_catalog_data)

    # Reference timestamps
    now = datetime.now()
    d90  = (now - timedelta(days=90)).isoformat()
    d45  = (now - timedelta(days=45)).isoformat()
    d60  = (now - timedelta(days=60)).isoformat()
    d30  = (now - timedelta(days=30)).isoformat()
    d10  = (now - timedelta(days=10)).isoformat()
    d3   = (now - timedelta(days=3)).isoformat()
    d300 = (now - timedelta(days=300)).isoformat()

    farms_data = [
        ("farm_1",  "user_1", "Green Acres",   "Punjab",      "Ludhiana", "Rampur",    "Alluvial Soil", 12.5, "High"),
        ("default", "guest",  "My Farm",        "Maharashtra", "Pune",     "Manchar",   "Black Soil",     8.2, "Medium"),
        ("farm_2",  "user_2", "Sukhdev Fields", "Haryana",     "Karnal",   "Nilokheri", "Clayey Soil",   15.0, "High"),
    ]
    cursor.executemany("INSERT INTO farms VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", farms_data)

    crops_data = [
        ("farm_1",  "Wheat",     d90,  5.0, "Flowering",  0.75, "Good"),
        ("farm_1",  "Mustard",   d45,  3.5, "Vegetative", 0.40, "Warning"),
        ("farm_1",  "Sugarcane", d300, 4.0, "Maturity",   0.90, "Good"),
        ("default", "Cotton",    d60,  4.5, "Vegetative", 0.55, "Good"),
        ("default", "Tomato",    d30,  3.7, "Flowering",  0.70, "Warning"),
    ]
    cursor.executemany(
        "INSERT INTO planted_crops "
        "(farm_id, crop_name, planted_date, land_area, stage, progress, health_status) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        crops_data,
    )

    disease_data = [
        ("farm_1",  "Rice",   "Rice Blast",            85.0, "Medium", d10),
        ("farm_1",  "Tomato", "Early Blight",           92.0, "High",   d3),
        ("default", "Cotton", "Cotton Leaf Curl Virus", 89.0, "High",   d3),
    ]
    cursor.executemany(
        "INSERT INTO disease_history "
        "(farm_id, crop_name, disease_name, confidence, severity, timestamp) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        disease_data,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def init_db() -> None:
    """
    Create database schema (idempotent) and seed demo data on first run.

    Safe to call on every server startup:
    - All CREATE TABLE statements use IF NOT EXISTS.
    - Seed data is inserted ONLY if the farms table is empty (F-15 fix).
    """
    logger.info("[Database] Initialising SQLite database at: %s", DB_PATH)
    # Use WAL mode + busy_timeout from the first connection so all subsequent
    # connections (from all threads) inherit WAL mode on this database file.
    from db_utils import get_db_connection
    conn = get_db_connection(DB_PATH)
    conn.row_factory = None   # cursor.execute returns plain tuples here
    cursor = conn.cursor()


    # ── Schema ────────────────────────────────────────────────────────────
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS farms (
        id                 TEXT  PRIMARY KEY,
        owner_id           TEXT  NOT NULL,
        name               TEXT  NOT NULL,
        state              TEXT  NOT NULL,
        district           TEXT  NOT NULL,
        village            TEXT  NOT NULL,
        soil_type          TEXT  NOT NULL,
        land_area          REAL  NOT NULL,
        water_availability TEXT  NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS planted_crops (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        farm_id      TEXT    NOT NULL,
        crop_name    TEXT    NOT NULL,
        planted_date TEXT    NOT NULL,
        land_area    REAL    NOT NULL,
        stage        TEXT    NOT NULL,
        progress     REAL    NOT NULL,
        health_status TEXT   NOT NULL,
        FOREIGN KEY(farm_id) REFERENCES farms(id) ON DELETE CASCADE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS disease_history (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        farm_id      TEXT    NOT NULL,
        crop_name    TEXT    NOT NULL,
        disease_name TEXT    NOT NULL,
        confidence   REAL    NOT NULL,
        severity     TEXT    NOT NULL,
        timestamp    TEXT    NOT NULL,
        FOREIGN KEY(farm_id) REFERENCES farms(id) ON DELETE CASCADE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS crop_catalog (
        id   TEXT PRIMARY KEY,
        name TEXT NOT NULL UNIQUE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS crop_suitability_audit (
        id                INTEGER PRIMARY KEY AUTOINCREMENT,
        farm_id           TEXT    NOT NULL,
        crop_name         TEXT    NOT NULL,
        suitability_score REAL    NOT NULL,
        reasons           TEXT    NOT NULL,
        ignored_warning   INTEGER NOT NULL,
        timestamp         TEXT    NOT NULL
    )
    """)

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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gemini_daily_usage (
        user_uid TEXT,
        date TEXT,
        call_count INTEGER,
        PRIMARY KEY (user_uid, date)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gemini_response_cache (
        cache_key TEXT PRIMARY KEY,
        response_json TEXT,
        cached_at TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mandi_prices_cache (
        id TEXT PRIMARY KEY,
        state TEXT,
        district TEXT,
        market TEXT,
        commodity TEXT,
        min_price TEXT,
        max_price TEXT,
        modal_price TEXT,
        arrival_date TEXT,
        cached_at TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dataset_v2_entries (
        id               INTEGER PRIMARY KEY AUTOINCREMENT,
        user_uid         TEXT    NOT NULL,
        diagnosis_id     TEXT,
        crop             TEXT    NOT NULL,
        predicted_disease TEXT   NOT NULL,
        confidence       REAL    NOT NULL,
        confidence_band  TEXT    NOT NULL DEFAULT 'unknown',
        is_correct       INTEGER,
        collection_type  TEXT    NOT NULL,
        image_path       TEXT,
        state            TEXT,
        district         TEXT,
        weather_snapshot TEXT,
        source           TEXT,
        timestamp        TEXT    NOT NULL
    )
    """)


    # ── Seed  ─────────────────────────────────────────────────────────────
    # Only seed when the database is freshly empty (F-15 fix).
    # This prevents data loss on restart while still bootstrapping new installs.
    cursor.execute("SELECT COUNT(*) FROM farms")
    if cursor.fetchone()[0] == 0:
        logger.info("[Database] Empty database — seeding demo data.")
        _seed_test_data(cursor)
    else:
        logger.info("[Database] Existing data found — skipping seed (F-15 fix).")

    # Ensure audit farm profiles exist in database for Capability Audit
    cursor.execute("SELECT COUNT(*) FROM farms WHERE id = 'farm_profile'")
    if cursor.fetchone()[0] == 0:
        logger.info("[Database] Seeding audit farm profile.")
        cursor.execute("INSERT OR REPLACE INTO farms VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("farm_profile", "user_profile", "Golden Grain Fields", "Punjab", "Ludhiana", "Ludhiana", "Loamy", 15.5, "Canal Irrigation"))
        cursor.execute("INSERT OR REPLACE INTO planted_crops (farm_id, crop_name, planted_date, land_area, stage, progress, health_status) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("farm_profile", "Wheat", (datetime.now() - timedelta(days=90)).isoformat(), 10.0, "Flowering", 0.75, "Good"))
        cursor.execute("INSERT OR REPLACE INTO planted_crops (farm_id, crop_name, planted_date, land_area, stage, progress, health_status) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("farm_profile", "Mustard", (datetime.now() - timedelta(days=45)).isoformat(), 5.5, "Vegetative", 0.40, "Warning"))
        cursor.execute("INSERT OR REPLACE INTO disease_history (farm_id, crop_name, disease_name, confidence, severity, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
            ("farm_profile", "Rice", "Rice Blast", 85.0, "Medium", (datetime.now() - timedelta(days=10)).isoformat()))
            
    cursor.execute("SELECT COUNT(*) FROM farms WHERE id = 'farm_weather'")
    if cursor.fetchone()[0] == 0:
        logger.info("[Database] Seeding audit farm weather profile.")
        cursor.execute("INSERT OR REPLACE INTO farms VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("farm_weather", "user_weather", "Hillside Vineyard", "Maharashtra", "Nashik", "Nashik", "Clayey", 8.0, "Drip Irrigation"))
        cursor.execute("INSERT OR REPLACE INTO planted_crops (farm_id, crop_name, planted_date, land_area, stage, progress, health_status) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("farm_weather", "Grape", (datetime.now() - timedelta(days=60)).isoformat(), 8.0, "Vegetative", 0.70, "Good"))

    conn.commit()
    conn.close()
    logger.info("[Database] Schema verified and ready.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_db()
