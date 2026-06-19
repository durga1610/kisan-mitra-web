import os
import sqlite3
import json
from suitability_engine import evaluate_crop_suitability

from config import DB_PATH

def set_test_farm_state(soil_type, water_availability, state, district, active_crops=None):
    if active_crops is None:
        active_crops = []
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Insert or replace farm
    cursor.execute("""
        INSERT OR REPLACE INTO farms (id, owner_id, name, state, district, village, soil_type, land_area, water_availability)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, ("test_suitability_farm", "test_user", "Test Suitability Farm", state, district, "Test Village", soil_type, 10.0, water_availability))
    
    # Delete old crops
    cursor.execute("DELETE FROM planted_crops WHERE farm_id = ?", ("test_suitability_farm",))
    
    # Insert new crops
    for crop in active_crops:
        cursor.execute("""
            INSERT INTO planted_crops (farm_id, crop_name, planted_date, land_area, stage, progress, health_status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ("test_suitability_farm", crop, "2026-05-01", 2.0, "Vegetative", 0.3, "Good"))
        
    conn.commit()
    conn.close()

def run_tests():
    print("==================================================")
    print("Testing AI Crop Suitability Validation Model")
    print("==================================================")
    
    # Test 1: Cotton + Black Soil = Suitable
    print("\nScenario 1: Cotton + Black Soil + High Water (Expected: Suitable)")
    set_test_farm_state("Black Soil", "High", "Maharashtra", "Pune")
    res1 = evaluate_crop_suitability("test_suitability_farm", "cotton")
    print(json.dumps(res1, indent=2))
    assert res1["suitable"] is True
    assert res1["score"] >= 50
    
    # Test 2: Rice + High Water = Suitable
    print("\nScenario 2: Rice + Clayey Soil + High Water (Expected: Suitable)")
    set_test_farm_state("Clayey Soil", "High", "Punjab", "Ludhiana")
    res2 = evaluate_crop_suitability("test_suitability_farm", "rice")
    print(json.dumps(res2, indent=2))
    assert res2["suitable"] is True
    assert res2["score"] >= 50
    
    # Test 3: Banana + Low Water = Not Suitable
    print("\nScenario 3: Banana + Low Water (Expected: Not Suitable)")
    set_test_farm_state("Alluvial Soil", "Low", "Punjab", "Ludhiana")
    res3 = evaluate_crop_suitability("test_suitability_farm", "banana")
    print(json.dumps(res3, indent=2))
    assert res3["suitable"] is False
    assert res3["score"] < 50
    assert any("Water availability is too low" in r or "Rainfall" in r for r in res3["reasons"])
    
    # Test 4: Rose + Dry Region (Sandy Soil + Low Water) = Not Suitable / Warning
    print("\nScenario 4: Rose + Dry Region (Expected: Not Suitable / Warning)")
    set_test_farm_state("Sandy Soil", "Low", "Rajasthan", "Jaipur")
    res4 = evaluate_crop_suitability("test_suitability_farm", "rose")
    print(json.dumps(res4, indent=2))
    assert res4["suitable"] is False
    assert any("Sandy soil has too high water drainage" in r or "Water availability is too low" in r for r in res4["reasons"])
    
    # Test 5: Rotation Conflict = Warning
    print("\nScenario 5: Rotation Conflict (Cotton immediately after Cotton) (Expected: Rotation Warning)")
    set_test_farm_state("Black Soil", "High", "Maharashtra", "Pune", active_crops=["Cotton"])
    res5 = evaluate_crop_suitability("test_suitability_farm", "cotton")
    print(json.dumps(res5, indent=2))
    # It might still be overall suitable or not, but it MUST contain rotation conflict in reasons
    assert any("Rotation conflict" in r for r in res5["reasons"])
    
    print("\nAll suitability scenarios validated successfully!")

if __name__ == "__main__":
    run_tests()
