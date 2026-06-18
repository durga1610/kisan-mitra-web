import logging
import os
import json
import pickle
from security_utils import safe_pickle_load

logger = logging.getLogger(__name__)
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_data.db")
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "crop_suitability_model.pkl")
PREPROCESSORS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "crop_suitability_preprocessors.pkl")

_crop_profiles = {}
def load_crop_profiles():
    global _crop_profiles
    if not _crop_profiles:
        profiles_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "crop_profiles.json")
        if os.path.exists(profiles_path):
            try:
                with open(profiles_path, "r", encoding="utf-8") as f:
                    _crop_profiles = json.load(f)
            except Exception as e:
                logger.warning(f"[SuitabilityEngine] Error loading crop_profiles.json: {e}")
    return _crop_profiles


def get_current_season_and_weather() -> tuple:
    """
    Returns (season, temp, rainfall, humidity) based on the current month.
    """
    month = datetime.now().month
    if 6 <= month <= 10:
        return "Kharif", 30.0, 1100.0, 80.0
    elif month >= 11 or month <= 3:
        return "Rabi", 18.0, 250.0, 60.0
    else:
        return "Zaid", 36.0, 80.0, 45.0

def normalize_soil(soil: Optional[str]) -> str:
    if not soil:
        return "Alluvial"
    s = soil.lower()
    if "alluvial" in s: return "Alluvial"
    if "black" in s: return "Black"
    if "sandy" in s: return "Sandy"
    if "clay" in s: return "Clayey"
    if "red" in s: return "Red"
    if "loam" in s: return "Loamy"
    return "Alluvial"

def normalize_state(state: Optional[str]) -> str:
    if not state:
        return "Punjab"
    STATES = ["Punjab", "Haryana", "Maharashtra", "Gujarat", "Uttar Pradesh", "Karnataka", "Tamil Nadu", "Rajasthan", "Madhya Pradesh", "Andhra Pradesh"]
    for st in STATES:
        if st.lower() in state.lower():
            return st
    return "Punjab"

def normalize_district(district: Optional[str]) -> str:
    if not district:
        return "Ludhiana"
    DISTRICTS = ["Ludhiana", "Karnal", "Pune", "Rajkot", "Lucknow", "Kolar", "Coimbatore", "Jaipur", "Rampur", "Manchar", "Nilokheri"]
    for ds in DISTRICTS:
        if ds.lower() in district.lower():
            return ds
    return "Ludhiana"

def normalize_water(water: Optional[str]) -> str:
    if not water:
        return "Medium"
    w = water.lower()
    if "high" in w: return "High"
    if "low" in w: return "Low"
    return "Medium"

def get_explainable_reasons(soil: str, season: str, temp: float, rainfall: float, humidity: float, water: str, prev_crop: str, target_crop: str, suitable: bool) -> List[str]:
    reasons = []
    tc = target_crop.lower()
    
    profiles = load_crop_profiles()
    if tc in profiles:
        profile = profiles[tc]
        
        # 1. Season check
        req_season = profile.get("season")
        if req_season and req_season in ["Kharif", "Rabi", "Zaid"] and season != req_season:
            reasons.append(f"Current season ({season}) is not suitable for {target_crop.title()} (prefers {req_season})")
            
        # 2. Water / Rainfall check
        water_req_str = profile.get("water_requirements", "").lower()
        if "high" in water_req_str:
            if water == "Low":
                reasons.append("Water availability is too low")
            elif water == "Medium":
                reasons.append("Water availability is suboptimal (prefers high)")
        elif "moderate" in water_req_str or "medium" in water_req_str:
            if water == "Low":
                reasons.append("Water availability is too low")
                
        # 3. Soil check
        soil_req_str = profile.get("soil_requirements", "").lower()
        if soil == "Sandy":
            if "sandy" not in soil_req_str and "drainage" not in soil_req_str:
                reasons.append("Sandy soil has too high water drainage")
        elif soil == "Clayey":
            if "clay" not in soil_req_str and "heavy" not in soil_req_str:
                reasons.append(f"Soil type ({soil}) is not optimal (prefers well-drained soil)")
    else:
        # 1. Season mismatch
        kharif_crops = ["rice", "cotton", "sugarcane", "soybean"]
        rabi_crops = ["wheat", "mustard", "potato"]
        zaid_crops = ["maize"]
        
        if tc in kharif_crops and season != "Kharif":
            reasons.append(f"Current season ({season}) is not suitable for {target_crop.title()}")
        elif tc in rabi_crops and season != "Rabi":
            reasons.append(f"Current season ({season}) is not suitable for {target_crop.title()}")
        
        # 2. Water / Rainfall mismatch
        if tc in ["rice", "sugarcane", "banana"]:
            if water == "Low":
                reasons.append("Water availability is too low")
            elif water == "Medium":
                reasons.append("Water availability is suboptimal (prefers high)")
            if rainfall < 800:
                reasons.append(f"Rainfall ({rainfall}mm) is below requirements")
        elif tc in ["cotton", "soybean", "tomato", "potato", "maize", "rose"]:
            if water == "Low":
                reasons.append("Water availability is too low")
            if rainfall < 300:
                reasons.append(f"Rainfall ({rainfall}mm) is low for optimal growth")
        elif tc == "mustard":
            if water == "High":
                reasons.append("Water availability is too high (mustard prefers drier root zones)")
                
        # 3. Soil mismatch
        if tc == "rice" and soil not in ["Clayey", "Alluvial"]:
            reasons.append(f"Soil type ({soil}) is not optimal (prefers Clayey or Alluvial)")
        elif tc == "cotton" and soil not in ["Black", "Alluvial"]:
            reasons.append(f"Soil type ({soil}) is not optimal (prefers Black or Alluvial)")
        elif tc == "wheat" and soil not in ["Alluvial", "Clayey", "Black"]:
            reasons.append(f"Soil type ({soil}) is not optimal (prefers Alluvial, Clayey or Black)")
        elif soil == "Sandy" and tc in ["tomato", "potato", "banana", "rose", "maize", "sugarcane", "mustard"]:
            reasons.append("Sandy soil has too high water drainage")
        
    # 4. Temperature mismatch
    if tc == "banana":
        if temp < 15:
            reasons.append("Temperature is below banana requirements")
        elif temp > 42:
            reasons.append("Temperature is too high for banana growth")
    elif tc == "tomato" and (temp < 12 or temp > 38):
        reasons.append("Temperature is outside tomato's range (12°C - 38°C)")
    elif tc == "wheat" and temp > 28:
        reasons.append("Temperature is too high for wheat growth")
    elif tc == "rose" and temp > 35:
        reasons.append("Temperature is too high for rose flower production")
        
    # 5. Crop rotation conflict
    if tc == prev_crop.lower() and tc != "none":
        reasons.append(f"Rotation conflict: planting {target_crop.title()} immediately after {prev_crop.title()} increases pest risk")
        
    if not reasons:
        if suitable:
            reasons.append(f"Soil, water, and seasonal conditions are highly compatible with {target_crop.title()} requirements.")
        else:
            reasons.append(f"Suboptimal agricultural conditions detected for {target_crop.title()}.")
            
    return reasons

def evaluate_crop_suitability(farm_id: str, target_crop: str) -> dict:
    """
    Evaluates suitability of a target crop using the trained ML model.
    """
    # 1. Query SQLite for Farm Details
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
            logger.info(f"[SuitabilityEngine] SQLite error: {e}")
            
    # Resolve pre-processed inputs
    soil_norm = normalize_soil(soil)
    state_norm = normalize_state(state)
    district_norm = normalize_district(district)
    water_norm = normalize_water(water)
    
    # Season & Weather Details
    season, temp, rainfall, humidity = get_current_season_and_weather()
    
    # Rotation (check last active crop as previous crop)
    from advisory_engine import normalize_previous_crop
    previous_crop = normalize_previous_crop(active_crops)
    
    # 2. Load Model and Preprocessors
    if not os.path.exists(MODEL_PATH) or not os.path.exists(PREPROCESSORS_PATH):
        # Fallback if model doesn't exist
        suitable = True
        score = 80
        confidence = 0.80
        reasons = [f"Suitability model not found. Using default suitability rating for {target_crop}."]
        return {
            "suitable": suitable,
            "score": score,
            "confidence": confidence,
            "reasons": reasons,
            "alternatives": ["Tomato", "Cotton", "Maize"]
        }
        
    try:
        import pandas as pd
        preprocessors = safe_pickle_load(PREPROCESSORS_PATH)  # F-05
        model = safe_pickle_load(MODEL_PATH)  # F-05
            
        label_encoders = preprocessors["label_encoders"]
        scaler = preprocessors["scaler"]
        
        # Build features dataframe
        feat_dict = {
            "soil_type": [soil_norm],
            "state": [state_norm],
            "district": [district_norm],
            "season": [season],
            "water_availability": [water_norm],
            "previous_crop": [previous_crop],
            "target_crop": [target_crop.lower()]
        }
        
        # Encode categorical
        feat_encoded = {}
        for col, le in label_encoders.items():
            val = feat_dict[col][0]
            if val not in le.classes_:
                val = "<unknown>"
            feat_encoded[col] = [le.transform([val])[0]]
            
        feat_encoded_df = pd.DataFrame(feat_encoded)
        
        # Scale numeric
        numeric_dict = {
            "rainfall": [rainfall],
            "temperature": [temp],
            "humidity": [humidity],
            "farm_size": [farm_size]
        }
        numeric_scaled = scaler.transform(pd.DataFrame(numeric_dict))
        numeric_scaled_df = pd.DataFrame(numeric_scaled, columns=list(numeric_dict.keys()))
        
        # Combine
        X = pd.concat([feat_encoded_df, numeric_scaled_df], axis=1)
        
        # Reorder columns to match train features
        train_cols = ["soil_type", "state", "district", "season", "water_availability", "previous_crop", "target_crop", "rainfall", "temperature", "humidity", "farm_size"]
        X = X[train_cols]
        
        # Predict Proba
        proba = model.predict_proba(X)[0]
        prob_suitable = float(proba[1])
        
        score = int(prob_suitable * 100)
        suitable = score >= 50
        confidence = round(prob_suitable, 2)
        
    except Exception as e:
        logger.warning(f"[SuitabilityEngine] Model prediction failed: {e}")
        score = 65
        suitable = True
        confidence = 0.65
        
    # 3. Generate Explainable Reasons
    reasons = get_explainable_reasons(
        soil_norm, season, temp, rainfall, humidity, water_norm, previous_crop, target_crop, suitable
    )
    
    # 4. Generate Alternatives if unsuitable
    alternatives = []
    if not suitable:
        try:
            from advisory_engine import extract_prediction_features, predict_crop_recommendations
            # Mock farm context
            f_ctx = {
                "id": farm_id,
                "soilType": soil,
                "waterAvailability": water,
                "landArea": farm_size,
                "plantedCrops": active_crops
            }
            w_ctx = {
                "season": season,
                "temperature": temp,
                "humidity": humidity,
                "rainfall": rainfall
            }
            features = extract_prediction_features(f_ctx, w_ctx)
            recs = predict_crop_recommendations(features)
            alternatives = [r["crop"].title() for r in recs if r["crop"].lower() != target_crop.lower()][:3]
        except Exception as e:
            logger.warning(f"[SuitabilityEngine] Alternatives lookup failed: {e}")
            
        # Fallback
        if not alternatives:
            alternatives = ["Tomato", "Cotton", "Maize"]
            
    return {
        "suitable": suitable,
        "score": score,
        "confidence": confidence,
        "reasons": reasons,
        "alternatives": alternatives
    }
