import os
import random
import numpy as np
import pandas as pd

# Categories
SOIL_TYPES = ["Alluvial", "Black", "Sandy", "Clayey", "Red", "Loamy"]
STATES = ["Punjab", "Haryana", "Maharashtra", "Gujarat", "Uttar Pradesh", "Karnataka", "Tamil Nadu", "Rajasthan", "Madhya Pradesh", "Andhra Pradesh"]
DISTRICTS = ["Ludhiana", "Karnal", "Pune", "Rajkot", "Lucknow", "Kolar", "Coimbatore", "Jaipur", "Rampur", "Manchar", "Nilokheri"]
SEASONS = ["Kharif", "Rabi", "Zaid"]
WATER_AVAILABILITIES = ["High", "Medium", "Low"]
CROPS = ["tomato", "rice", "cotton", "wheat", "maize", "potato", "mustard", "sugarcane", "soybean", "banana", "rose"]
PREVIOUS_CROPS = CROPS + ["none"]

def get_suitability_score(soil, season, temp, rainfall, humidity, water, prev_crop, target_crop):
    score = 100
    
    # 1. Season affinity rules
    if target_crop in ["rice", "cotton", "sugarcane", "soybean"]:
        if season != "Kharif":
            score -= 50
    elif target_crop in ["wheat", "mustard", "potato"]:
        if season != "Rabi":
            score -= 50
    elif target_crop in ["tomato", "maize", "rose"]:
        # flexible, but minor penalty for Zaid due to heat stress
        if season == "Zaid":
            score -= 15
    elif target_crop == "banana":
        # prefers hot humid Kharif or medium temperature
        if season == "Rabi" and temp < 15:
            score -= 30

    # 2. Water availability and Rainfall affinity
    if target_crop in ["rice", "sugarcane", "banana"]:
        if water == "Low":
            score -= 60
        elif water == "Medium":
            score -= 25
        if rainfall < 800:
            score -= 30
    elif target_crop in ["cotton", "soybean", "tomato", "potato", "maize", "rose"]:
        if water == "Low":
            score -= 30
        if rainfall < 300:
            score -= 20
        if rainfall > 2000:
            score -= 15 # excess rain causes root rot
    elif target_crop == "mustard":
        # Mustard prefers low to medium water/rainfall (dry regions)
        if water == "High":
            score -= 20
        if rainfall > 800:
            score -= 30
            
    # 3. Soil affinity
    if target_crop == "rice":
        if soil not in ["Clayey", "Alluvial"]:
            score -= 40
    elif target_crop == "cotton":
        if soil not in ["Black", "Alluvial"]:
            score -= 40
    elif target_crop == "wheat":
        if soil not in ["Alluvial", "Clayey", "Black"]:
            score -= 35
    elif target_crop == "soybean":
        if soil not in ["Black", "Loamy"]:
            score -= 30
    elif target_crop in ["tomato", "potato", "banana", "rose", "maize", "sugarcane", "mustard"]:
        if soil == "Sandy":
            score -= 40 # Sandy soils drain too quickly for these crops except with high water/compost
            
    # 4. Temperature constraints
    if target_crop == "banana":
        if temp < 15 or temp > 42:
            score -= 40
    elif target_crop == "tomato":
        if temp < 12 or temp > 38:
            score -= 30
    elif target_crop == "wheat":
        if temp < 8 or temp > 28:
            score -= 45
    elif target_crop == "cotton":
        if temp < 18 or temp > 40:
            score -= 30
    elif target_crop == "rose":
        # dry hot weather is bad
        if temp > 35 and humidity < 40:
            score -= 25

    # 5. Crop Rotation (Rotation Conflict)
    if target_crop == prev_crop and target_crop != "none":
        score -= 45

    return score

def generate_dataset(num_samples=25000):
    random.seed(42)
    np.random.seed(42)
    
    records = []
    for _ in range(num_samples):
        soil = random.choice(SOIL_TYPES)
        state = random.choice(STATES)
        district = random.choice(DISTRICTS)
        season = random.choice(SEASONS)
        water = random.choice(WATER_AVAILABILITIES)
        prev_crop = random.choice(PREVIOUS_CROPS)
        target_crop = random.choice(CROPS)
        
        # Environmental conditions based on season
        if season == "Kharif":
            temp = float(np.random.normal(30.0, 3.0))
            humidity = float(np.random.normal(80.0, 5.0))
            rainfall = float(np.random.normal(1100.0, 250.0))
        elif season == "Rabi":
            temp = float(np.random.normal(18.0, 3.0))
            humidity = float(np.random.normal(60.0, 10.0))
            rainfall = float(np.random.normal(250.0, 100.0))
        else: # Zaid (Summer)
            temp = float(np.random.normal(36.0, 2.0))
            humidity = float(np.random.normal(45.0, 10.0))
            rainfall = float(np.random.normal(80.0, 40.0))
            
        farm_size = float(max(0.5, np.random.normal(8.0, 4.0)))
        
        # Clip numerical parameters
        temp = round(max(5.0, min(50.0, temp)), 1)
        humidity = round(max(10.0, min(100.0, humidity)), 1)
        rainfall = round(max(0.0, min(3000.0, rainfall)), 1)
        farm_size = round(farm_size, 1)
        
        score = get_suitability_score(soil, season, temp, rainfall, humidity, water, prev_crop, target_crop)
        
        # Binary label
        suitable = 1 if score >= 60 else 0
        
        # Introduce 2% noise (random flips)
        if random.random() < 0.02:
            suitable = 1 - suitable
            
        records.append({
            "soil_type": soil,
            "state": state,
            "district": district,
            "season": season,
            "temperature": temp,
            "rainfall": rainfall,
            "humidity": humidity,
            "water_availability": water,
            "farm_size": farm_size,
            "previous_crop": prev_crop,
            "target_crop": target_crop,
            "suitable": suitable
        })
        
    df = pd.DataFrame(records)
    
    # Ensure dataset directory exists
    os.makedirs("dataset", exist_ok=True)
    df.to_csv("dataset/crop_suitability.csv", index=False)
    print(f"Generated suitability dataset with {len(df)} rows at dataset/crop_suitability.csv")

if __name__ == "__main__":
    generate_dataset()
