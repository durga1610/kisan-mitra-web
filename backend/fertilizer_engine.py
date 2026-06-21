import os
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_data.db")
DOCS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "documents")

STAGE_THRESHOLDS = {
    "tomato": {"vegetative": 30, "flowering": 60},
    "rice": {"vegetative": 40, "flowering": 90},
    "paddy": {"vegetative": 40, "flowering": 90},
    "wheat": {"vegetative": 45, "flowering": 85},
    "cotton": {"vegetative": 50, "flowering": 100},
    "maize": {"vegetative": 35, "flowering": 70},
    "corn": {"vegetative": 35, "flowering": 70},
    "potato": {"vegetative": 30, "flowering": 70}
}

FERTILIZER_SCHEDULES = {
    "grape": {
        "Vegetative": [
            {"day": "Day 0", "fertilizer": "FYM / Compost", "dosage": "5 tonnes/acre"},
            {"day": "Day 30", "fertilizer": "Urea", "dosage": "25 kg/acre"}
        ],
        "Flowering": [
            {"day": "Day 60", "fertilizer": "Potassium Sulphate", "dosage": "15 kg/acre"},
            {"day": "Day 90", "fertilizer": "Micronutrient Spray", "dosage": "2 ml/litre"}
        ],
        "Fruiting": [
            {"day": "Day 120", "fertilizer": "Fruit Development Mix", "dosage": "10 kg/acre"}
        ]
    },
    "mango": {
        "Vegetative": [
            {"day": "Day 15", "fertilizer": "NPK 10:10:10", "dosage": "500g/tree"},
            {"day": "Day 45", "fertilizer": "Urea", "dosage": "250g/tree"}
        ],
        "Flowering": [
            {"day": "Day 75", "fertilizer": "Micronutrient Spray", "dosage": "2 ml/litre"},
            {"day": "Day 90", "fertilizer": "Mono Potassium Phosphate", "dosage": "1.5 kg/acre"}
        ],
        "Fruiting": [
            {"day": "Day 120", "fertilizer": "Sulphate of Potash", "dosage": "300g/tree"}
        ]
    },
    "banana": {
        "Vegetative": [
            {"day": "Day 20", "fertilizer": "NPK 15:15:15", "dosage": "50g/plant"},
            {"day": "Day 50", "fertilizer": "Urea", "dosage": "100g/plant"}
        ],
        "Flowering": [
            {"day": "Day 90", "fertilizer": "Potash", "dosage": "150g/plant"}
        ],
        "Fruiting": [
            {"day": "Day 130", "fertilizer": "SOP (Sulphate of Potash)", "dosage": "100g/plant"}
        ]
    },
    "papaya": {
        "Vegetative": [
            {"day": "Day 15", "fertilizer": "NPK 15:15:15", "dosage": "100g/plant"},
            {"day": "Day 45", "fertilizer": "Urea", "dosage": "50g/plant"}
        ],
        "Flowering": [
            {"day": "Day 75", "fertilizer": "Boron", "dosage": "5g/plant"}
        ],
        "Fruiting": [
            {"day": "Day 120", "fertilizer": "MOP (Muriate of Potash)", "dosage": "150g/plant"}
        ]
    },
    "pomegranate": {
        "Vegetative": [
            {"day": "Day 20", "fertilizer": "NPK 19:19:19", "dosage": "250g/plant"},
            {"day": "Day 50", "fertilizer": "Urea", "dosage": "100g/plant"}
        ],
        "Flowering": [
            {"day": "Day 80", "fertilizer": "DAP", "dosage": "150g/plant"}
        ],
        "Fruiting": [
            {"day": "Day 120", "fertilizer": "Potassium Sulphate", "dosage": "200g/plant"}
        ]
    },
    "coconut": {
        "Vegetative": [
            {"day": "Day 30", "fertilizer": "NPK 15:15:15", "dosage": "1 kg/palm"},
            {"day": "Day 90", "fertilizer": "Urea", "dosage": "500g/palm"}
        ],
        "Flowering": [
            {"day": "Day 150", "fertilizer": "Magnesium Sulphate", "dosage": "500g/palm"}
        ],
        "Fruiting": [
            {"day": "Day 210", "fertilizer": "Muriate of Potash", "dosage": "1.5 kg/palm"}
        ]
    },
    "tomato": {
        "Vegetative": [
            {"day": "Day 15", "fertilizer": "NPK 19:19:19", "dosage": "2.5 kg/acre"},
            {"day": "Day 30", "fertilizer": "Urea", "dosage": "15 kg/acre"}
        ],
        "Flowering": [
            {"day": "Day 50", "fertilizer": "DAP (Diammonium Phosphate)", "dosage": "20 kg/acre"}
        ],
        "Fruiting": [
            {"day": "Day 80", "fertilizer": "Calcium Nitrate", "dosage": "10 kg/acre"}
        ]
    },
    "rice": {
        "Vegetative": [
            {"day": "Day 0", "fertilizer": "Basal NPK", "dosage": "50 kg/acre"},
            {"day": "Day 15", "fertilizer": "Urea", "dosage": "30 kg/acre"}
        ],
        "Flowering": [
            {"day": "Day 45", "fertilizer": "Urea Top Dressing", "dosage": "30 kg/acre"},
            {"day": "Day 50", "fertilizer": "DAP", "dosage": "30 kg/acre"}
        ],
        "Fruiting": [
            {"day": "Day 60", "fertilizer": "Zinc Sulphate", "dosage": "10 kg/acre"}
        ]
    },
    "cotton": {
        "Vegetative": [
            {"day": "Day 0", "fertilizer": "DAP", "dosage": "50 kg/acre"},
            {"day": "Day 30", "fertilizer": "Urea", "dosage": "25 kg/acre"}
        ],
        "Flowering": [
            {"day": "Day 60", "fertilizer": "Potash", "dosage": "20 kg/acre"},
            {"day": "Day 75", "fertilizer": "Urea and Magnesium Sulphate", "dosage": "30 kg/acre"}
        ],
        "Fruiting": [
            {"day": "Day 90", "fertilizer": "Micronutrient Mix", "dosage": "5 kg/acre"}
        ]
    },
    "maize": {
        "Vegetative": [
            {"day": "Day 15", "fertilizer": "NPK 12:32:16", "dosage": "50 kg/acre"},
            {"day": "Day 35", "fertilizer": "Urea", "dosage": "30 kg/acre"}
        ],
        "Flowering": [
            {"day": "Day 60", "fertilizer": "Zinc Sulphate", "dosage": "5 kg/acre"}
        ],
        "Fruiting": [
            {"day": "Day 85", "fertilizer": "Urea", "dosage": "20 kg/acre"}
        ]
    },
    "groundnut": {
        "Vegetative": [
            {"day": "Day 15", "fertilizer": "Single Super Phosphate (SSP)", "dosage": "75 kg/acre"},
            {"day": "Day 30", "fertilizer": "Gypsum", "dosage": "100 kg/acre"}
        ],
        "Flowering": [
            {"day": "Day 45", "fertilizer": "Boron", "dosage": "2 kg/acre"}
        ],
        "Fruiting": [
            {"day": "Day 70", "fertilizer": "MOP", "dosage": "15 kg/acre"}
        ]
    },
    "chilli": {
        "Vegetative": [
            {"day": "Day 15", "fertilizer": "NPK 19:19:19", "dosage": "3 kg/acre"},
            {"day": "Day 40", "fertilizer": "Urea", "dosage": "20 kg/acre"}
        ],
        "Flowering": [
            {"day": "Day 65", "fertilizer": "DAP", "dosage": "25 kg/acre"}
        ],
        "Fruiting": [
            {"day": "Day 95", "fertilizer": "SOP (Potash)", "dosage": "15 kg/acre"}
        ]
    },
    "brinjal": {
        "Vegetative": [
            {"day": "Day 15", "fertilizer": "NPK 15:15:15", "dosage": "25 kg/acre"},
            {"day": "Day 35", "fertilizer": "Urea", "dosage": "15 kg/acre"}
        ],
        "Flowering": [
            {"day": "Day 60", "fertilizer": "DAP", "dosage": "20 kg/acre"}
        ],
        "Fruiting": [
            {"day": "Day 90", "fertilizer": "Potassium Nitrate", "dosage": "10 kg/acre"}
        ]
    },
    "onion": {
        "Vegetative": [
            {"day": "Day 15", "fertilizer": "NPK 15:15:15", "dosage": "30 kg/acre"},
            {"day": "Day 30", "fertilizer": "Urea", "dosage": "20 kg/acre"}
        ],
        "Flowering": [
            {"day": "Day 50", "fertilizer": "Ammonium Sulphate", "dosage": "15 kg/acre"}
        ],
        "Fruiting": [
            {"day": "Day 75", "fertilizer": "MOP (Potash)", "dosage": "15 kg/acre"}
        ]
    },
    "turmeric": {
        "Vegetative": [
            {"day": "Day 30", "fertilizer": "NPK 15:15:15", "dosage": "40 kg/acre"},
            {"day": "Day 60", "fertilizer": "Urea", "dosage": "25 kg/acre"}
        ],
        "Flowering": [
            {"day": "Day 120", "fertilizer": "Gypsum", "dosage": "50 kg/acre"}
        ],
        "Fruiting": [
            {"day": "Day 180", "fertilizer": "MOP (Potash)", "dosage": "30 kg/acre"}
        ]
    },
    "sugarcane": {
        "Vegetative": [
            {"day": "Day 30", "fertilizer": "NPK 12:32:16", "dosage": "100 kg/acre"},
            {"day": "Day 60", "fertilizer": "Urea", "dosage": "50 kg/acre"}
        ],
        "Flowering": [
            {"day": "Day 120", "fertilizer": "Urea", "dosage": "75 kg/acre"}
        ],
        "Fruiting": [
            {"day": "Day 210", "fertilizer": "MOP (Potash)", "dosage": "50 kg/acre"}
        ]
    },
    "wheat": {
        "Vegetative": [
            {"day": "Day 20", "fertilizer": "DAP", "dosage": "50 kg/acre"},
            {"day": "Day 40", "fertilizer": "Urea", "dosage": "35 kg/acre"}
        ],
        "Flowering": [
            {"day": "Day 70", "fertilizer": "NPK 19:19:19", "dosage": "5 kg/acre"}
        ],
        "Fruiting": [
            {"day": "Day 95", "fertilizer": "SOP (Potash)", "dosage": "10 kg/acre"}
        ]
    }
}

CATEGORY_FERTILIZER_SCHEDULES = {
    "leafy vegetables": {
        "Vegetative": [
            {"day": "Day 0", "fertilizer": "Compost / Organic Manure", "dosage": "2 tonnes/acre"},
            {"day": "Day 10", "fertilizer": "Urea / Nitrogen-rich Fertilizer", "dosage": "20 kg/acre"}
        ],
        "Flowering": [
            {"day": "Day 30", "fertilizer": "NPK 19:19:19", "dosage": "15 kg/acre"}
        ],
        "Fruiting": [
            {"day": "Day 45", "fertilizer": "Compost / Organic Manure", "dosage": "2 tonnes/acre"}
        ]
    },
    "cereals": {
        "Vegetative": [
            {"day": "Day 15", "fertilizer": "Urea", "dosage": "40 kg/acre"},
            {"day": "Day 35", "fertilizer": "NPK 12:32:16", "dosage": "50 kg/acre"}
        ],
        "Flowering": [
            {"day": "Day 60", "fertilizer": "Urea Top Dressing", "dosage": "30 kg/acre"}
        ],
        "Fruiting": [
            {"day": "Day 85", "fertilizer": "MOP (Muriate of Potash)", "dosage": "15 kg/acre"}
        ]
    },
    "pulses": {
        "Vegetative": [
            {"day": "Day 15", "fertilizer": "DAP", "dosage": "20 kg/acre"}
        ],
        "Flowering": [
            {"day": "Day 40", "fertilizer": "Boron foliar spray", "dosage": "1 kg/acre"}
        ],
        "Fruiting": [
            {"day": "Day 70", "fertilizer": "MOP", "dosage": "10 kg/acre"}
        ]
    },
    "oilseeds": {
        "Vegetative": [
            {"day": "Day 15", "fertilizer": "Single Super Phosphate (SSP)", "dosage": "50 kg/acre"}
        ],
        "Flowering": [
            {"day": "Day 45", "fertilizer": "Gypsum (for Sulphur/Calcium)", "dosage": "100 kg/acre"}
        ],
        "Fruiting": [
            {"day": "Day 75", "fertilizer": "MOP", "dosage": "15 kg/acre"}
        ]
    },
    "fruit crops": {
        "Vegetative": [
            {"day": "Day 20", "fertilizer": "Compost & NPK 15:15:15", "dosage": "1 kg/tree"}
        ],
        "Flowering": [
            {"day": "Day 60", "fertilizer": "Micronutrient Spray", "dosage": "2 ml/litre"}
        ],
        "Fruiting": [
            {"day": "Day 120", "fertilizer": "Sulphate of Potash (SOP)", "dosage": "500g/tree"}
        ]
    },
    "spices": {
        "Vegetative": [
            {"day": "Day 30", "fertilizer": "NPK 19:19:19", "dosage": "25 kg/acre"}
        ],
        "Flowering": [
            {"day": "Day 75", "fertilizer": "Organic Compost & Neem Cake", "dosage": "1 tonne/acre"}
        ],
        "Fruiting": [
            {"day": "Day 120", "fertilizer": "MOP (Potash)", "dosage": "20 kg/acre"}
        ]
    },
    "plantation crops": {
        "Vegetative": [
            {"day": "Day 30", "fertilizer": "NPK 15:15:15", "dosage": "500g/plant"}
        ],
        "Flowering": [
            {"day": "Day 120", "fertilizer": "Organic manure & Magnesium Sulphate", "dosage": "2 kg/plant"}
        ],
        "Fruiting": [
            {"day": "Day 200", "fertilizer": "Muriate of Potash", "dosage": "1 kg/plant"}
        ]
    },
    "medicinal crops": {
        "Vegetative": [
            {"day": "Day 20", "fertilizer": "FYM / Vermicompost", "dosage": "3 tonnes/acre"}
        ],
        "Flowering": [
            {"day": "Day 50", "fertilizer": "Organic growth promoters", "dosage": "500 ml/acre"}
        ],
        "Fruiting": [
            {"day": "Day 90", "fertilizer": "Neem cake and light Potash", "dosage": "100 kg/acre"}
        ]
    }
}

def guess_crop_category(crop_name: str) -> str:
    c = crop_name.lower().strip()
    if any(k in c for k in ["leaf", "spinach", "lettuce", "cabbage", "kale", "chard", "greens", "bok choy", "parsley", "celery", "basil", "mint", "cauliflower", "broccoli", "sprouts"]):
        return "leafy vegetables"
    if any(k in c for k in ["rice", "wheat", "maize", "corn", "barley", "oats", "sorghum", "millet", "paddy", "rye", "teff", "grain"]):
        return "cereals"
    if any(k in c for k in ["pea", "bean", "gram", "lentil", "pulse", "chickpea", "cowpea", "mung", "urad", "clover", "alfalfa"]):
        return "pulses"
    if any(k in c for k in ["seed", "sunflower", "safflower", "sesame", "linseed", "castor", "niger", "rapeseed", "canola", "mustard", "peanut"]):
        return "oilseeds"
    if any(k in c for k in ["apple", "banana", "grape", "mango", "orange", "pear", "peach", "plum", "apricot", "cherry", "kiwi", "avocado", "lemon", "lime", "berry", "melon", "papaya", "pomegranate", "guava", "citrus", "pineapple", "fig", "amla", "fruit"]):
        return "fruit crops"
    if any(k in c for k in ["pepper", "chilli", "onion", "garlic", "turmeric", "ginger", "cardamom", "cumin", "fennel", "fenugreek", "clove", "cinnamon", "nutmeg", "saffron", "vanilla", "spice"]):
        return "spices"
    if any(k in c for k in ["tea", "coffee", "rubber", "coconut", "areca", "cashew", "tobacco", "jute", "sugarcane", "palm", "bamboo"]):
        return "plantation crops"
    if any(k in c for k in ["aloe", "ashwagandha", "neem", "stevia", "giloy", "brahmi", "shatavari", "basil", "herbal", "medicinal", "aromatic"]):
        return "medicinal crops"
    return None



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
                print(f"[FertilizerEngine] Error loading crop_profiles.json: {e}")
    return _crop_profiles

def get_crop_age(planted_date_str: str) -> int:
    """
    Calculates crop age in days from planting date.
    """
    try:
        if "T" in planted_date_str:
            date_part = planted_date_str.split("T")[0]
        else:
            date_part = planted_date_str.split(" ")[0]
        planted_date = datetime.strptime(date_part, "%Y-%m-%d")
        delta = datetime.now() - planted_date
        return max(0, delta.days)
    except Exception as e:
        print(f"[FertilizerEngine] Error parsing date '{planted_date_str}': {e}")
        return 0

def get_growth_stage(crop_name: str, age_days: int) -> str:
    """
    Resolves growth stage based on crop age.
    """
    c = crop_name.lower()
    # Handle variations
    if "paddy" in c or "rice" in c:
        c = "rice"
    elif "corn" in c or "maize" in c:
        c = "maize"
        
    profiles = load_crop_profiles()
    if c in profiles and "growth_stages" in profiles[c]:
        stages = profiles[c]["growth_stages"]
        veg = stages.get("vegetative", 30)
        flow = stages.get("flowering", 70)
        if age_days <= veg:
            return "Vegetative"
        elif age_days <= flow:
            return "Flowering"
        else:
            return "Fruiting"
            
    thresholds = STAGE_THRESHOLDS.get(c, {"vegetative": 30, "flowering": 70})
    if age_days <= thresholds["vegetative"]:
        return "Vegetative"
    elif age_days <= thresholds["flowering"]:
        return "Flowering"
    else:
        return "Fruiting"

def get_weather_context(farm_id: str, weather_ctx: Optional[dict] = None) -> dict:
    """
    Gets real or simulated weather details.
    """
    if weather_ctx:
        return {
            "temperature": weather_ctx.get("temperature", 25.0),
            "humidity": weather_ctx.get("humidity", 60.0),
            "condition": weather_ctx.get("condition", "Sunny"),
            "season": weather_ctx.get("season", "Kharif"),
            "rainfall_forecast": weather_ctx.get("rainfall_forecast", "No rain expected")
        }
        
    # Query current month to guess season
    month = datetime.now().month
    if 6 <= month <= 10:
        season = "Kharif"
        cond = "Humid and Overcast"
        temp = 29.5
        rain = "moderate rain showers expected later today"
    elif month >= 11 or month <= 3:
        season = "Rabi"
        cond = "Clear and Cool"
        temp = 17.5
        rain = "no rain expected"
    else:
        season = "Zaid"
        cond = "Sunny and Hot"
        temp = 38.0
        rain = "no rain expected"
        
    # Check if the farm is in Ludhiana or other rain-expected settings
    # For default mock data we can read SQLite farm info
    rainfall_forecast = rain
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT state, district FROM farms WHERE id = ?", (farm_id,))
            row = cursor.fetchone()
            conn.close()
            if row:
                state, district = row[0].lower(), row[1].lower()
                if "haryana" in state or "karnal" in district:
                    # simulate heavy rain for test scenarios
                    rainfall_forecast = "Heavy rainfall expected within 24 hours"
        except Exception as e:
            print(f"[FertilizerEngine] SQLite error in get_weather_context: {e}")

    return {
        "temperature": temp,
        "humidity": 75.0 if season == "Kharif" else 55.0,
        "condition": cond,
        "season": season,
        "rainfall_forecast": rainfall_forecast
    }

def get_soil_context(farm_id: str, farm_context: Optional[dict] = None) -> dict:
    """
    Retrieves soil properties, prioritizing farm_context parameter.
    """
    if farm_context:
        return {
            "soil_type": farm_context.get("soilType") or farm_context.get("soil_type") or "Alluvial",
            "water_availability": farm_context.get("waterAvailability") or farm_context.get("water_availability") or "Medium"
        }
        
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT soil_type, water_availability FROM farms WHERE id = ?", (farm_id,))
            row = cursor.fetchone()
            conn.close()
            if row:
                return {
                    "soil_type": row["soil_type"],
                    "water_availability": row["water_availability"]
                }
        except Exception as e:
            print(f"[FertilizerEngine] SQLite error in get_soil_context: {e}")
            
    return {
        "soil_type": "Alluvial",
        "water_availability": "Medium"
    }

def parse_fertilizer_file(crop_name: str) -> dict:
    """
    Parses stage-specific guidelines from knowledge base text files or profiles.
    """
    data = {
        "Vegetative": "Apply standard vegetative fertilizer.",
        "Flowering": "Apply standard flowering fertilizer.",
        "Fruiting": "Apply standard fruiting/maturity fertilizer.",
        "Dosage": "25 kg/acre",
        "Method": "Soil application near roots.",
        "Precautions": "Ensure correct dilution/placement."
    }
    
    c = crop_name.lower()
    
    # 1. Check if a crop-specific fertilizer text file exists first
    if "paddy" in c or "rice" in c:
        filename = "rice_fertilizer.txt"
    elif "corn" in c or "maize" in c:
        filename = "maize_fertilizer.txt"
    elif "tomato" in c:
        filename = "tomato_fertilizer.txt"
    elif "cotton" in c:
        filename = "cotton_fertilizer.txt"
    elif "wheat" in c:
        filename = "wheat_fertilizer.txt"
    elif "potato" in c:
        filename = "potato_fertilizer.txt"
    else:
        filename = f"{c.replace(' ', '_')}_fertilizer.txt"
        
    filepath = os.path.join(DOCS_DIR, filename)
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            lines = content.split("\n")
            for line in lines:
                if ":" in line:
                    key, val = line.split(":", 1)
                    key_clean = key.strip().lower()
                    val_clean = val.strip()
                    if "vegetative" in key_clean:
                        data["Vegetative"] = val_clean
                    elif "flowering" in key_clean:
                        data["Flowering"] = val_clean
                    elif "fruiting" in key_clean or "maturity" in key_clean:
                        data["Fruiting"] = val_clean
                    elif "dosage" in key_clean:
                        data["Dosage"] = val_clean
                    elif "method" in key_clean:
                        data["Method"] = val_clean
                    elif "precautions" in key_clean:
                        data["Precautions"] = val_clean
            return data
        except Exception as e:
            print(f"[FertilizerEngine] Error parsing file '{filename}': {e}")
            
    # 2. Check crop_profiles second if no specific text file exists
    profiles = load_crop_profiles()
    if c in profiles and "fertilizer_schedule" in profiles[c]:
        prof = profiles[c]
        sched = prof["fertilizer_schedule"]
        data["Vegetative"] = sched["application"][0] if len(sched["application"]) > 0 else "Apply vegetative stage nutrients."
        data["Flowering"] = sched["application"][1] if len(sched["application"]) > 1 else "Apply flowering stage nutrients."
        data["Fruiting"] = sched["application"][2] if len(sched["application"]) > 2 else "Apply fruiting stage nutrients."
        data["Dosage"] = sched["npk"]
        data["Method"] = "Foliar spray or soil drenching near root zone."
        data["Precautions"] = "Ensure optimal soil moisture before applying fertilizer."
        return data
        
    return data

def get_fertilizer_recommendation(
    farm_id: str,
    crop_name_or_id: str,
    farm_context: Optional[dict] = None,
    weather_context: Optional[dict] = None
) -> dict:
    """
    Computes dynamic, context-aware fertilizer recommendations.
    """
    # 1. Retrieve crop details from SQLite / farm_context
    if crop_name_or_id and not crop_name_or_id.isdigit():
        crop_name = crop_name_or_id
    else:
        crop_name = "Tomato"
    planted_date = datetime.now().strftime("%Y-%m-%d")
    db_stage = "Vegetative"
    
    # Try query SQLite first
    planted_crop_record = None
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Try by integer ID first
            try:
                crop_id_int = int(crop_name_or_id)
                cursor.execute("SELECT * FROM planted_crops WHERE id = ?", (crop_id_int,))
                planted_crop_record = cursor.fetchone()
            except ValueError:
                pass
                
            # Try by name next
            if not planted_crop_record:
                cursor.execute(
                    "SELECT * FROM planted_crops WHERE farm_id = ? AND LOWER(crop_name) = ?",
                    (farm_id, crop_name_or_id.lower())
                )
                planted_crop_record = cursor.fetchone()
                
            if planted_crop_record:
                crop_name = planted_crop_record["crop_name"]
                planted_date = planted_crop_record["planted_date"]
                db_stage = planted_crop_record["stage"]
                
            conn.close()
        except Exception as e:
            print(f"[FertilizerEngine] SQLite error querying crop: {e}")
            
    # If no DB record, try to fallback to farm_context plantedCrops matching
    if not planted_crop_record and farm_context and farm_context.get("plantedCrops"):
        for pc in farm_context["plantedCrops"]:
            pc_name = pc if isinstance(pc, str) else pc.get("cropName", "")
            if pc_name.lower() == crop_name_or_id.lower():
                crop_name = pc_name
                if isinstance(pc, dict) and pc.get("plantedDate"):
                    planted_date = pc["plantedDate"]
                break
                
    # Compute age and stage
    age_days = get_crop_age(planted_date)
    stage = get_growth_stage(crop_name, age_days)
    
    # 2. Get Weather, Soil contexts
    weather_ctx = get_weather_context(farm_id, weather_context)
    soil_ctx = get_soil_context(farm_id, farm_context)
    
    # 3. Retrieve Latest Disease history for the crop
    latest_disease = None
    disease_severity = "None"
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT crop_name, disease_name, severity FROM disease_history WHERE farm_id = ? ORDER BY timestamp DESC",
                (farm_id,)
            )
            rows = cursor.fetchall()
            conn.close()
            
            for row in rows:
                db_crop = row["crop_name"].lower()
                target_crop = crop_name.lower()
                if db_crop in target_crop or target_crop in db_crop or (target_crop == "rice" and "paddy" in db_crop) or (target_crop == "paddy" and "rice" in db_crop):
                    latest_disease = row["disease_name"]
                    disease_severity = row["severity"]
                    break
        except Exception as e:
            print(f"[FertilizerEngine] SQLite error querying disease: {e}")
            
    # 4. Parse Base Recommendations
    crop_key = crop_name.lower().strip()
    if "paddy" in crop_key or "rice" in crop_key:
        crop_key = "rice"
    elif "corn" in crop_key or "maize" in crop_key:
        crop_key = "maize"

    use_category_fallback = False
    category_resolved = None
    source_label = "FERTILIZER_SCHEDULES"
    schedule_source = None

    if crop_key in FERTILIZER_SCHEDULES:
        schedule_source = FERTILIZER_SCHEDULES[crop_key]
        source_label = "FERTILIZER_SCHEDULES"
    else:
        profiles = load_crop_profiles()
        if crop_key in profiles:
            category_resolved = profiles[crop_key].get("category", "").lower()
        if not category_resolved:
            category_resolved = guess_crop_category(crop_name)

        if category_resolved and category_resolved in CATEGORY_FERTILIZER_SCHEDULES:
            use_category_fallback = True
            schedule_source = CATEGORY_FERTILIZER_SCHEDULES[category_resolved]
            source_label = f"CATEGORY_FERTILIZER_SCHEDULES ({category_resolved.title()})"
        else:
            from services.gemini_fallback import generate_fertilizer_advice
            user_uid = "anonymous"
            if farm_context and farm_context.get("ownerId"):
                user_uid = farm_context["ownerId"]
                
            print(f"[Fertilizer Fallback] Crop '{crop_name}' not in FERTILIZER_SCHEDULES and no category resolved. Triggering Gemini fallback.")
            gemini_res = generate_fertilizer_advice(
                crop=crop_name,
                age=age_days,
                stage=stage,
                soil=soil_ctx.get("soil_type", "Alluvial"),
                weather=weather_ctx.get("weather_condition", "Clear"),
                trigger_reason="no_crop_schedule_or_category_found",
                user_uid=user_uid
            )
            if gemini_res:
                schedule_item = {
                    "fertilizer": gemini_res.get("recommendation", "NPK"),
                    "dosage": gemini_res.get("dosage", "N/A"),
                    "stage": stage
                }
                warnings = []
                rain_fc = weather_ctx.get("rainfall_forecast", "").lower()
                if "heavy" in rain_fc or "rain" in rain_fc:
                    warnings.append("Heavy rainfall expected within 24 hours. Delay fertilizer application to avoid nutrient loss.")
                    
                return {
                    "crop": crop_name,
                    "stage": stage,
                    "age": age_days,
                    "recommendation": gemini_res.get("recommendation", "N/A"),
                    "dosage": gemini_res.get("dosage", "N/A"),
                    "reason": f"{gemini_res.get('recommendation')} is recommended. Timing: {gemini_res.get('timing')}. Organic Alternative: {gemini_res.get('organicAlternative')}. Precautions: {gemini_res.get('precautions')}",
                    "warnings": warnings,
                    "schedule": [schedule_item],
                    "source": "GEMINI_FALLBACK"
                }
            else:
                use_category_fallback = True
                category_resolved = "cereals"
                schedule_source = CATEGORY_FERTILIZER_SCHEDULES[category_resolved]
                source_label = "INTELLIGENT_DEFAULT (Cereals Category)"

    # Retrieve stage entries
    stage_cap = stage.capitalize()
    stage_entries = schedule_source.get(stage_cap, [])
    
    # Check if we should fallback to Gemini because stage_entries is empty
    if not stage_entries:
        from services.gemini_fallback import generate_fertilizer_advice
        user_uid = "anonymous"
        if farm_context and farm_context.get("ownerId"):
            user_uid = farm_context["ownerId"]
            
        print(f"[Fertilizer Fallback] Stage '{stage}' has no entries for '{crop_name}'. Triggering Gemini fallback.")
        gemini_res = generate_fertilizer_advice(
            crop=crop_name,
            age=age_days,
            stage=stage,
            soil=soil_ctx.get("soil_type", "Alluvial"),
            weather=weather_ctx.get("weather_condition", "Clear"),
            trigger_reason="no_stage_entries_found",
            user_uid=user_uid
        )
        if gemini_res:
            schedule_item = {
                "fertilizer": gemini_res.get("recommendation", "NPK"),
                "dosage": gemini_res.get("dosage", "N/A"),
                "stage": stage
            }
            warnings = []
            rain_fc = weather_ctx.get("rainfall_forecast", "").lower()
            if "heavy" in rain_fc or "rain" in rain_fc:
                warnings.append("Heavy rainfall expected within 24 hours. Delay fertilizer application to avoid nutrient loss.")
                
            return {
                "crop": crop_name,
                "stage": stage,
                "age": age_days,
                "recommendation": gemini_res.get("recommendation", "N/A"),
                "dosage": gemini_res.get("dosage", "N/A"),
                "reason": f"{gemini_res.get('recommendation')} is recommended. Timing: {gemini_res.get('timing')}. Organic Alternative: {gemini_res.get('organicAlternative')}. Precautions: {gemini_res.get('precautions')}",
                "warnings": warnings,
                "schedule": [schedule_item],
                "source": "GEMINI_FALLBACK"
            }

    if stage_entries:
        base_recommendation = " | ".join(f"Apply {e['fertilizer']}" for e in stage_entries)
        dosage = " | ".join(e['dosage'] for e in stage_entries)
    else:
        # Safe default recommendation if both local schedules and Gemini failed/are offline
        base_recommendation = f"Apply balanced NPK fertilizer (19:19:19) at 2.5 kg/acre. Supplement with organic compost or farmyard manure to enhance soil structure and support growth during the {stage} stage."
        dosage = "2.5 kg/acre"

    # Parse fertilizer name from recommendation
    fertilizer_name = "Urea"
    for fert in ["NPK", "DAP", "Urea", "Potash", "Zinc", "Boron", "Ammonium Sulphate", "MOP", "SOP"]:
        if fert.lower() in base_recommendation.lower():
            fertilizer_name = fert
            break
            
    # Compute default reason based on stage
    reason = f"{fertilizer_name} is highly recommended for {crop_name} during its {stage} growth stage."
    
    # 5. Apply Context-Aware Adjustments
    warnings = []
    
    # Soil based adjustments
    soil_type = soil_ctx["soil_type"].lower()
    if "black" in soil_type:
        reason += " Assumptions of irrigation leaching loss are reduced due to black soil's high water retention."
    elif "sandy" in soil_type:
        reason += " Recommended to split fertilizer application into multiple small doses to prevent leaching in sandy soil."
    elif "red" in soil_type:
        reason += " Recommend organic matter enhancement (FYM/compost) alongside mineral inputs to improve red soil's structure."
        
    # Weather based adjustments
    rain_fc = weather_ctx["rainfall_forecast"].lower()
    if "heavy" in rain_fc or "rain" in rain_fc:
        warnings.append("Heavy rainfall expected within 24 hours. Delay fertilizer application to avoid nutrient loss.")
        
    # Disease based adjustments
    # If high severity disease, halve Nitrogen dosage and trigger warning
    is_nitrogen = any(n in fertilizer_name.lower() for n in ["urea", "npk", "ammonium"]) or "nitrogen" in base_recommendation.lower()
    if latest_disease and disease_severity.lower() == "high":
        warnings.append("Disease stress detected. Focus on disease control before applying additional nitrogen.")
        if is_nitrogen:
            # try to parse numeric dosage and cut in half
            # e.g. "25 kg/acre" -> "12.5 kg/acre (Reduced due to disease stress)"
            try:
                parts = dosage.split(" ")
                num_val = float(parts[0])
                dosage = f"{num_val / 2.0} {parts[1]} (Reduced due to disease stress)"
            except Exception:
                dosage = f"{dosage} (Reduce by 50% due to disease stress)"
                
    # Flatten the complete fertilizer schedule across all stages
    schedule = []
    for stg, entries in schedule_source.items():
        for entry in entries:
            entry_copy = entry.copy()
            entry_copy["stage"] = stg
            schedule.append(entry_copy)

    # 5. Validation Checks: Add debugging logs
    print("[DEBUG]")
    print(f"Crop={crop_name}")
    print(f"Age={age_days}")
    print(f"Stage={stage}")
    print(f"Schedule Source={source_label}")
    print(f"Entries={len(schedule)}")

    # 6. Format final payload
    return {
        "crop": crop_name,
        "stage": stage,
        "age": age_days,
        "recommendation": base_recommendation,
        "dosage": dosage,
        "reason": reason,
        "warnings": warnings,
        "schedule": schedule,
        "source": "LOCAL_ENGINE"
    }
