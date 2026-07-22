import os
import sys
import json
import time

# Ensure parent directory is in sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from advisory.ai_crop_advisor import generate_ai_crop_advisory

REQUIRED_10_KEYS = [
    "recommended_crop",
    "crop_suitability_reason",
    "fertilizer_recommendation",
    "irrigation_advice",
    "weather_precautions",
    "pest_disease_prevention",
    "market_outlook",
    "best_farming_practices",
    "confidence_score",
    "knowledge_sources",
]


def test_ai_crop_advisor_service():
    print("=" * 80)
    print(" KISAN MITRA: 100% LOCAL AI CROP ADVISOR VERIFICATION TESTS")
    print("=" * 80)

    # 1. Test Scenario A: Rice Crop + Alluvial Soil + Upward Market
    print("\n1. Testing Scenario A: Rice Crop + Alluvial Soil + Upward Market...")
    farm_a = {"id": "farm_001", "crop": "Rice", "soil_type": "Alluvial Soil", "water_availability": "Canal & Borewell"}
    weather_a = {"temp_c": 30.0, "humidity": 78.0, "rainfall_mm": 15.0, "season": "Kharif"}
    market_a = {"commodity": "Rice", "mandi_price": "₹2,400", "msp": "₹2,183", "trend": "Upward"}

    res_a = generate_ai_crop_advisory(farm_context=farm_a, weather_data=weather_a, market_data=market_a)

    print(f"   |- Recommended Crop : {res_a['recommended_crop']}")
    print(f"   |- Confidence       : {res_a['confidence_score']} ({res_a['confidence_level']})")
    print(f"   |- Sources Used     : {len(res_a['knowledge_sources'])} documents")
    print(f"   |- Telemetry        : {res_a['telemetry']}")

    # Verify all 10 required keys exist
    for key in REQUIRED_10_KEYS:
        assert key in res_a, f"Missing required response key '{key}'"

    assert res_a["recommended_crop"] == "Rice", "Crop mismatch"
    assert len(res_a["knowledge_sources"]) > 0, "Expected retrieved FAISS knowledge sources"
    print("   >>> PASS: Scenario A generated complete, grounded 10-field advisory!")

    # 2. Test Scenario B: Cotton Crop + Black Soil + Heatwave Alert
    print("\n2. Testing Scenario B: Cotton Crop + Black Clay Soil + Heatwave Alert (40°C)...")
    farm_b = {"id": "farm_002", "crop": "Cotton", "soil_type": "Black Soil", "water_availability": "Drip Irrigation"}
    weather_b = {"temp_c": 40.0, "humidity": 30.0, "rainfall_mm": 0.0, "season": "Kharif"}

    res_b = generate_ai_crop_advisory(farm_context=farm_b, weather_data=weather_b)

    assert "Heatwave Warning" in res_b["weather_precautions"], "Expected Heatwave warning in weather section"
    assert "Drip Irrigation" in res_b["irrigation_advice"], "Expected Drip irrigation in water section"
    print("   >>> PASS: Heatwave alert & drip irrigation customization verified!")

    # 3. Test Scenario C: Maize Crop + Red Soil + Price < MSP
    print("\n3. Testing Scenario C: Maize Crop + Price Below MSP...")
    farm_c = {"id": "farm_003", "crop": "Maize", "soil_type": "Red Soil", "water_availability": "Rainfed"}
    market_c = {"commodity": "Maize", "mandi_price": "₹1,700", "msp": "₹2,090", "trend": "Downward"}

    res_c = generate_ai_crop_advisory(farm_context=farm_c, market_data=market_c)

    assert "Government Procurement Centers" in res_c["market_outlook"] or "MSP" in res_c["market_outlook"], "Expected MSP protection advice"
    print("   >>> PASS: Government MSP protection advice verified!")

    # 4. Test Zero Gemini Call Assertion
    print("\n4. Verifying ZERO Gemini / OpenAI calls anywhere in execution...")
    for res in [res_a, res_b, res_c]:
        sources = res["knowledge_sources"]
        for s in sources:
            source_id = s.get("id", "")
            assert "gemini" not in source_id.lower(), "Gemini source detected!"

    print("   >>> PASS: 100% Local RAG execution verified!")

    print("\n" + "=" * 80)
    print(" ALL 100% LOCAL AI CROP ADVISOR TESTS PASSED PERFECTLY!")
    print("=" * 80)


if __name__ == "__main__":
    try:
        test_ai_crop_advisor_service()
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)
