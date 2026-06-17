import json
from datetime import datetime, timedelta
from fertilizer_engine import get_fertilizer_recommendation

def test_scenarios():
    print("==================================================")
    print("Testing Dynamic Fertilizer Recommendation Engine Scenarios")
    print("==================================================")

    now = datetime.now()

    # Scenario 1: Tomato Vegetative Stage (Age <= 30 days)
    print("\nScenario 1: Tomato Vegetative Stage")
    f_ctx = {
        "soilType": "Alluvial",
        "waterAvailability": "High",
        "plantedCrops": [{"cropName": "Tomato", "plantedDate": (now - timedelta(days=15)).isoformat()}]
    }
    w_ctx = {"rainfall_forecast": "No rain expected"}
    res1 = get_fertilizer_recommendation("test_farm", "Tomato", f_ctx, w_ctx)
    print(json.dumps(res1, indent=2))
    assert res1["stage"] == "Vegetative"
    assert "Urea" in res1["recommendation"] or "NPK" in res1["recommendation"]

    # Scenario 2: Tomato Flowering Stage (30 < Age <= 60 days)
    print("\nScenario 2: Tomato Flowering Stage")
    f_ctx["plantedCrops"][0]["plantedDate"] = (now - timedelta(days=45)).isoformat()
    res2 = get_fertilizer_recommendation("test_farm", "Tomato", f_ctx, w_ctx)
    print(json.dumps(res2, indent=2))
    assert res2["stage"] == "Flowering"
    assert "DAP" in res2["recommendation"]

    # Scenario 3: Rice Tillering Stage
    print("\nScenario 3: Rice Tillering Stage")
    f_ctx_rice = {
        "soilType": "Alluvial",
        "waterAvailability": "High",
        "plantedCrops": [{"cropName": "Rice", "plantedDate": (now - timedelta(days=50)).isoformat()}]
    }
    res3 = get_fertilizer_recommendation("test_farm", "Rice", f_ctx_rice, w_ctx)
    print(json.dumps(res3, indent=2))
    assert res3["stage"] == "Flowering"
    assert "DAP" in res3["recommendation"]

    # Scenario 4: Cotton Flowering Stage
    print("\nScenario 4: Cotton Flowering Stage")
    f_ctx_cotton = {
        "soilType": "Alluvial",
        "waterAvailability": "High",
        "plantedCrops": [{"cropName": "Cotton", "plantedDate": (now - timedelta(days=70)).isoformat()}]
    }
    res4 = get_fertilizer_recommendation("test_farm", "Cotton", f_ctx_cotton, w_ctx)
    print(json.dumps(res4, indent=2))
    assert res4["stage"] == "Flowering"
    assert "Urea" in res4["recommendation"]

    # Scenario 5: Heavy Rain Forecast Scenario
    print("\nScenario 5: Rain Forecast (Warning Triggered)")
    w_ctx_rain = {"rainfall_forecast": "Heavy rain expected within 24 hours"}
    res5 = get_fertilizer_recommendation("test_farm", "Tomato", f_ctx, w_ctx_rain)
    print(json.dumps(res5, indent=2))
    assert len(res5["warnings"]) > 0
    assert any("Heavy rainfall expected" in w for w in res5["warnings"])

    # Scenario 6: Disease Positive Scenario (High Severity)
    # The default farm in SQLite has a mock Cotton Leaf Curl Virus with High severity
    print("\nScenario 6: Disease Positive (High Severity Curl Virus on Cotton)")
    f_ctx_db = {
        "soilType": "Black Soil",
        "waterAvailability": "High",
        "plantedCrops": [{"cropName": "Cotton", "plantedDate": (now - timedelta(days=70)).isoformat()}]
    }
    res6 = get_fertilizer_recommendation("default", "Cotton", f_ctx_db, w_ctx)
    print(json.dumps(res6, indent=2))
    # Warnings must contain disease stress warning
    assert any("Disease stress detected" in w for w in res6["warnings"])
    # Cotton Flowering recommendation contains Urea (Nitrogen), so dosage should be halved/reduced
    assert "Reduced due to disease stress" in res6["dosage"] or "Reduce by 50%" in res6["dosage"]

    print("\nAll 6 verification scenarios passed successfully!")

if __name__ == "__main__":
    test_scenarios()
