import os
import json
import sqlite3
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app_data.db")

CROP_SUITABLE_STATES = {
    "grape": ["maharashtra", "karnataka", "tamil nadu", "andhra pradesh"],
    "banana": ["maharashtra", "karnataka", "tamil nadu", "andhra pradesh", "gujarat"],
    "papaya": ["maharashtra", "karnataka", "andhra pradesh", "gujarat", "uttar pradesh"],
    "mango": ["uttar pradesh", "andhra pradesh", "karnataka", "maharashtra", "gujarat"],
    "pomegranate": ["maharashtra", "gujarat", "rajasthan", "karnataka", "andhra pradesh"],
    "rose": ["karnataka", "tamil nadu", "maharashtra", "west bengal"],
    "marigold": ["karnataka", "tamil nadu", "maharashtra", "haryana", "punjab"],
    "jasmine": ["tamil nadu", "karnataka", "andhra pradesh", "maharashtra"],
    "chilli": ["andhra pradesh", "karnataka", "maharashtra", "tamil nadu"],
    "onion": ["maharashtra", "karnataka", "gujarat", "madhya pradesh"],
    "garlic": ["madhya pradesh", "gujarat", "rajasthan", "uttar pradesh"],
    "turmeric": ["andhra pradesh", "tamil nadu", "karnataka", "orissa"],
    "groundnut": ["gujarat", "andhra pradesh", "tamil nadu", "karnataka"],
    "millets": ["rajasthan", "maharashtra", "karnataka", "gujarat"],
    "cotton": ["gujarat", "maharashtra", "telangana", "andhra pradesh", "punjab", "haryana"],
    "rice": ["west bengal", "uttar pradesh", "punjab", "andhra pradesh", "tamil nadu"],
    "wheat": ["uttar pradesh", "punjab", "haryana", "madhya pradesh", "rajasthan"],
    "potato": ["uttar pradesh", "west bengal", "bihar", "gujarat"],
    "mustard": ["rajasthan", "haryana", "madhya pradesh", "uttar pradesh"],
    "sugarcane": ["uttar pradesh", "maharashtra", "karnataka", "tamil nadu"]
}

def load_crop_profiles() -> dict:
    profiles_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "crop_profiles.json")
    if os.path.exists(profiles_path):
        try:
            with open(profiles_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"[RegionalSuitability] Error loading profiles: {e}")
    return {}

def calculate_suitability(farm_id: str, crop_name: str, farm_context: Optional[dict] = None, weather_context: Optional[dict] = None) -> dict:
    """
    Computes a 6-factor regional suitability score out of 100 points.
    Applies hard block rules.
    """
    # 1. Fetch Farm Details
    soil = "Alluvial"
    state = "Punjab"
    district = "Ludhiana"
    water = "Medium"
    farm_size = 5.0
    active_crops = []
    
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM farms WHERE id = ?", (farm_id,))
            farm_row = cursor.fetchone()
            if farm_row:
                soil = farm_row["soil_type"]
                state = farm_row["state"]
                district = farm_row["district"]
                water = farm_row["water_availability"]
                farm_size = farm_row["land_area"]
                
            cursor.execute("SELECT crop_name FROM planted_crops WHERE farm_id = ?", (farm_id,))
            active_crops = [r["crop_name"].lower() for r in cursor.fetchall()]
            conn.close()
        except Exception as e:
            logger.warning(f"[RegionalSuitability] SQLite error: {e}")
            
    # Override with farm_context if provided
    if farm_context:
        soil = farm_context.get("soilType") or farm_context.get("soil_type") or soil
        state = farm_context.get("state") or state
        district = farm_context.get("district") or district
        water = farm_context.get("waterAvailability") or farm_context.get("water_availability") or water
        farm_size = farm_context.get("landArea") or farm_context.get("land_area") or farm_size
        if farm_context.get("plantedCrops"):
            active_crops = [c.get("cropName", "").lower() if isinstance(c, dict) else str(c).lower() for c in farm_context["plantedCrops"]]

    # 2. Season and Weather Context
    current_month = datetime.now().month
    season = "Kharif"
    if 6 <= current_month <= 10:
        season = "Kharif"
    elif current_month >= 11 or current_month <= 3:
        season = "Rabi"
    else:
        season = "Zaid"
        
    temp = 28.0
    humidity = 60.0
    rainfall = 500.0
    
    if weather_context:
        temp = float(weather_context.get("temperature", temp))
        humidity = float(weather_context.get("humidity", humidity))
        cond = weather_context.get("condition", "").lower()
        if "rain" in cond:
            rainfall = 900.0
        elif "dry" in cond or "sunny" in cond:
            rainfall = 100.0
            
    crop_key = crop_name.lower().strip()
    profiles = load_crop_profiles()
    profile = profiles.get(crop_key, {})
    
    # --- Scoring Factors ---
    reasons = []
    suitable = True
    
    # A. Region Suitability (30 points)
    region_score = 0
    suitable_states = CROP_SUITABLE_STATES.get(crop_key, [])
    state_lower = state.lower()
    
    if suitable_states:
        if state_lower in suitable_states:
            region_score = 30
            reasons.append(f"Region Match: {state} is a primary agricultural zone for {crop_name}.")
        else:
            region_score = 15
            reasons.append(f"Region Suboptimal: {state} is outside the traditional cultivation belt for {crop_name}.")
    else:
        # Default for unspecified crops
        region_score = 25
        reasons.append(f"General suitability in {state} agricultural zone.")
        
    # Hard Block Region Rule (Score < 21 / 30 is < 70%)
    if region_score < 21:
        suitable = False
        reasons.append(f"Hard Block: Crop '{crop_name}' is not regionally suitable for commercial production in {state}.")

    # B. Weather Suitability (25 points)
    weather_score = 0
    pref_season = profile.get("season", "Kharif")
    
    # Temperature check (15 points)
    temp_points = 0
    if pref_season == "Rabi":
        # Cool weather crops (10-28 C)
        if 10 <= temp <= 28:
            temp_points = 15
        elif 8 <= temp <= 32:
            temp_points = 10
            reasons.append(f"Temperature warning: current temp ({temp}°C) is slightly warm for cool-season {crop_name}.")
        else:
            temp_points = 2
            reasons.append(f"Temperature block: current temp ({temp}°C) is outside acceptable range for cool-season {crop_name}.")
    else:
        # Warm weather crops (20-38 C)
        if 20 <= temp <= 38:
            temp_points = 15
        elif 15 <= temp <= 42:
            temp_points = 10
            reasons.append(f"Temperature warning: current temp ({temp}°C) is suboptimal for warm-season {crop_name}.")
        else:
            temp_points = 2
            reasons.append(f"Temperature block: current temp ({temp}°C) is outside acceptable range for warm-season {crop_name}.")
            
    # Rainfall / Humidity check (10 points)
    rain_points = 10
    water_req = profile.get("water_requirements", "").lower()
    if "high" in water_req and rainfall < 300:
        rain_points = 5
        reasons.append("Rainfall/humidity is suboptimal for high water demand crop.")
    elif "low" in water_req and rainfall > 800:
        rain_points = 5
        reasons.append("Rainfall/humidity is high for drought-tolerant crop.")
        
    weather_score = temp_points + rain_points
    
    # Hard Block Weather Rule (Score < 17.5 / 25 is < 70%)
    if weather_score < 17.5:
        suitable = False
        reasons.append(f"Hard Block: Local weather conditions ({temp}°C) are incompatible with growth requirements of {crop_name}.")

    # C. Soil Suitability (20 points)
    soil_score = 0
    soil_req = profile.get("soil_requirements", "").lower()
    soil_lower = soil.lower()
    
    if soil_lower in soil_req or not soil_req:
        soil_score = 20
        reasons.append(f"Soil Match: {soil} soil type is highly compatible.")
    else:
        # Custom logic mapping
        if "black" in soil_lower and crop_key in ["cotton", "soybean", "sugarcane"]:
            soil_score = 20
        elif "alluvial" in soil_lower and crop_key in ["rice", "wheat", "potato", "sugarcane"]:
            soil_score = 20
        elif "sandy" in soil_lower and crop_key in ["groundnut", "millets"]:
            soil_score = 20
        elif "clay" in soil_lower and crop_key in ["rice"]:
            soil_score = 20
        elif "sandy" in soil_lower and "high water" in water_req:
            soil_score = 5
            reasons.append(f"Soil Warning: Sandy soil drains too quickly for a water-intensive crop like {crop_name}.")
        else:
            soil_score = 12
            reasons.append(f"Soil Suboptimal: {soil} soil is moderately compatible.")

    # D. Water Availability (10 points)
    water_score = 0
    water_lower = water.lower()
    if "high" in water_req:
        if "high" in water_lower:
            water_score = 10
        elif "medium" in water_lower:
            water_score = 6
            reasons.append("Water Availability Warning: Water supply is medium; target crop prefers high irrigation.")
        else:
            water_score = 2
            reasons.append("Water Availability Block: Crop requires high water, but farm availability is low.")
    else:
        # Moderate/Low water crops
        if "low" in water_lower or "medium" in water_lower:
            water_score = 10
        else:
            water_score = 8 # high water is ok but not necessary

    # E. Season Suitability (10 points)
    season_score = 2
    if pref_season == season:
        season_score = 10
        reasons.append(f"Season Match: Current season ({season}) is ideal for planting.")
    else:
        reasons.append(f"Season Warning: Current season is {season}, but {crop_name} is best suited for {pref_season}.")

    # F. Market Demand (5 points)
    market_score = 3
    # Check if we have recent market prices for this state and crop
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='market_prices'"
        )
        if cursor.fetchone()[0] > 0:
            cursor.execute(
                "SELECT COUNT(*) FROM market_prices WHERE state = ? AND LOWER(commodity) LIKE ?",
                (state, f"%{crop_key}%")
            )
            count = cursor.fetchone()[0]
            if count > 0:
                market_score = 5
                reasons.append(f"Market Match: Positive local market demand detected for {crop_name} in {state}.")
        conn.close()
    except Exception:
        pass

    # Total Score Calculation
    total_score = region_score + weather_score + soil_score + water_score + season_score + market_score
    
    # Ensure final decision matches both checks
    final_suitable = suitable and (total_score >= 50)
    
    # 4. Generate Alternatives if unsuitable
    alternatives = []
    if not final_suitable:
        # Default alternatives based on season
        if season == "Kharif":
            alternatives = ["Rice", "Cotton", "Maize"]
        elif season == "Rabi":
            alternatives = ["Wheat", "Mustard", "Potato"]
        else:
            alternatives = ["Rose", "Jasmine", "Cucumber"]
            
        # Ensure we filter out target crop
        alternatives = [alt for alt in alternatives if alt.lower() != crop_key]

    return {
        "suitable": final_suitable,
        "score": int(total_score),
        "confidence": round(total_score / 100.0, 2),
        "reasons": reasons,
        "alternatives": alternatives,
        "source": "LOCAL_ENGINE" # Regional suitability runs locally in 6-factor rules
    }
