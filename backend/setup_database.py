import os
import sqlite3
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_data.db")

def init_db():
    print(f"[Database] Initializing SQLite database at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Create tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS farms (
        id TEXT PRIMARY KEY,
        owner_id TEXT NOT NULL,
        name TEXT NOT NULL,
        state TEXT NOT NULL,
        district TEXT NOT NULL,
        village TEXT NOT NULL,
        soil_type TEXT NOT NULL,
        land_area REAL NOT NULL,
        water_availability TEXT NOT NULL
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS planted_crops (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        farm_id TEXT NOT NULL,
        crop_name TEXT NOT NULL,
        planted_date TEXT NOT NULL,
        land_area REAL NOT NULL,
        stage TEXT NOT NULL,
        progress REAL NOT NULL,
        health_status TEXT NOT NULL,
        FOREIGN KEY(farm_id) REFERENCES farms(id) ON DELETE CASCADE
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS disease_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        farm_id TEXT NOT NULL,
        crop_name TEXT NOT NULL,
        disease_name TEXT NOT NULL,
        confidence REAL NOT NULL,
        severity TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY(farm_id) REFERENCES farms(id) ON DELETE CASCADE
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS crop_catalog (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL UNIQUE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS crop_suitability_audit (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        farm_id TEXT NOT NULL,
        crop_name TEXT NOT NULL,
        suitability_score REAL NOT NULL,
        reasons TEXT NOT NULL,
        ignored_warning INTEGER NOT NULL,
        timestamp TEXT NOT NULL
    )
    """)
    
    # 2. Insert mock data (Clear tables first to avoid primary key constraints)
    cursor.execute("DELETE FROM planted_crops")
    cursor.execute("DELETE FROM disease_history")
    cursor.execute("DELETE FROM farms")
    cursor.execute("DELETE FROM crop_catalog")
    cursor.execute("DELETE FROM crop_suitability_audit")
    
    import json
    crop_catalog_data = [
        ("tomato", "tomato"),
        ("rice", "rice"),
        ("paddy", "paddy"),
        ("cotton", "cotton"),
        ("wheat", "wheat"),
        ("maize", "maize"),
        ("corn", "corn"),
        ("potato", "potato"),
        ("mustard", "mustard"),
        ("sugarcane", "sugarcane"),
        ("banana", "banana"),
        ("rose", "rose")
    ]
    
    # Dynamically extend crop catalog with keys from crop_profiles.json if present
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
        except Exception as e:
            print(f"[Database] Error extending crop catalog from profiles: {e}")
            
    cursor.executemany("INSERT INTO crop_catalog VALUES (?, ?)", crop_catalog_data)
    
    # Mock dates
    now = datetime.now()
    date_90_days_ago = (now - timedelta(days=90)).isoformat()
    date_45_days_ago = (now - timedelta(days=45)).isoformat()
    date_60_days_ago = (now - timedelta(days=60)).isoformat()
    date_30_days_ago = (now - timedelta(days=30)).isoformat()
    date_10_days_ago = (now - timedelta(days=10)).isoformat()
    date_3_days_ago = (now - timedelta(days=3)).isoformat()
    date_300_days_ago = (now - timedelta(days=300)).isoformat()
    
    # Insert Farms
    farms_data = [
        ("farm_1", "user_1", "Green Acres", "Punjab", "Ludhiana", "Rampur", "Alluvial Soil", 12.5, "High"),
        ("default", "guest", "My Farm", "Maharashtra", "Pune", "Manchar", "Black Soil", 8.2, "Medium"),
        ("farm_2", "user_2", "Sukhdev Fields", "Haryana", "Karnal", "Nilokheri", "Clayey Soil", 15.0, "High")
    ]
    cursor.executemany("INSERT INTO farms VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", farms_data)
    
    # Insert Planted Crops
    crops_data = [
        # Farm 1 (Green Acres)
        ("farm_1", "Wheat", date_90_days_ago, 5.0, "Flowering", 0.75, "Good"),
        ("farm_1", "Mustard", date_45_days_ago, 3.5, "Vegetative", 0.40, "Warning"),
        ("farm_1", "Sugarcane", date_300_days_ago, 4.0, "Maturity", 0.90, "Good"),
        
        # Default Farm (My Farm)
        ("default", "Cotton", date_60_days_ago, 4.5, "Vegetative", 0.55, "Good"),
        ("default", "Tomato", date_30_days_ago, 3.7, "Flowering", 0.70, "Warning")
    ]
    cursor.executemany("""
    INSERT INTO planted_crops (farm_id, crop_name, planted_date, land_area, stage, progress, health_status)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, crops_data)
    
    # Insert Disease History
    disease_data = [
        # Farm 1 (Green Acres)
        ("farm_1", "Rice", "Rice Blast", 85.0, "Medium", date_10_days_ago),
        ("farm_1", "Tomato", "Early Blight", 92.0, "High", date_3_days_ago),
        
        # Default Farm (My Farm)
        ("default", "Cotton", "Cotton Leaf Curl Virus", 89.0, "High", date_3_days_ago)
    ]
    cursor.executemany("""
    INSERT INTO disease_history (farm_id, crop_name, disease_name, confidence, severity, timestamp)
    VALUES (?, ?, ?, ?, ?, ?)
    """, disease_data)
    
    conn.commit()
    conn.close()
    print("[Database] Database initialized and pre-populated successfully.")

if __name__ == "__main__":
    init_db()
