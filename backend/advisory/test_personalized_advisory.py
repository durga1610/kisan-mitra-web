import os
import sys
import json
import time

# Ensure parent directory is in sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from advisory.personalized_advisory import generate_personalized_advisories
from advisory.advisory_scheduler import run_advisory_pipeline


def test_personalized_advisory_engine():
    print("=" * 80)
    print(" KISAN MITRA: PERSONALIZED AI ADVISORY ENGINE VERIFICATION TESTS")
    print("=" * 80)

    # Scenario A: Heavy Rainfall + Upward Market Price + Rice Flowering Stage
    print("\n1. Testing Scenario A: Heavy Rain + High Humidity + Market Surge (Rice/Alluvial)...")
    scen_a_weather = {"temp_c": 29.0, "humidity": 85.0, "rainfall_mm": 35.0, "condition": "Heavy Downpour"}
    scen_a_market = {"commodity": "Rice", "mandi_price": "₹2,400", "msp": "₹2,183", "trend": "Upward"}
    scen_a_farm = {"crop": "Rice", "soil_type": "Alluvial Soil", "farm_area_acres": 4.0}

    res_a = run_advisory_pipeline(
        farm_context=scen_a_farm,
        weather_data=scen_a_weather,
        market_data=scen_a_market,
        growth_stage="Flowering"
    )

    print(f"   |- Total Advisories Generated : {res_a['total_advisories']}")
    print(f"   |- Priority Breakdown         : {res_a['priority_breakdown']}")
    print(f"   |- Categories Generated       : {res_a['categories_generated']}")

    # Verify Critical weather alert is present
    critical_advs = [a for a in res_a["advisories"] if a["priority"] == "Critical"]
    assert len(critical_advs) >= 1, "Expected at least 1 Critical advisory for heavy rainfall!"
    assert "heavy rain" in critical_advs[0]["title"].lower() or "drainage" in critical_advs[0]["title"].lower()
    print("   >>> PASS: Critical Heavy Rainfall advisory generated!")

    # Scenario B: Heatwave & Dry Spell + Cotton Crop + Black Clay Soil
    print("\n2. Testing Scenario B: Heatwave Alert (40°C) + Black Clay Soil (Cotton)...")
    scen_b_weather = {"temp_c": 40.0, "humidity": 32.0, "rainfall_mm": 0.0, "condition": "Sunny"}
    scen_b_farm = {"crop": "Cotton", "soil_type": "Black Soil", "farm_area_acres": 6.0}

    res_b = run_advisory_pipeline(
        farm_context=scen_b_farm,
        weather_data=scen_b_weather
    )

    print(f"   |- Total Advisories Generated : {res_b['total_advisories']}")
    print(f"   |- Priority Breakdown         : {res_b['priority_breakdown']}")

    heat_advs = [a for a in res_b["advisories"] if "heatwave" in a["id"]]
    assert len(heat_advs) == 1, "Expected Heatwave warning advisory!"
    print("   >>> PASS: Heatwave Warning generated for 40°C temperature!")

    # Scenario C: Mandi Price Below MSP + Acidic Red Soil
    print("\n3. Testing Scenario C: Price Below MSP + Red Acidic Soil (Maize)...")
    scen_c_market = {"commodity": "Maize", "mandi_price": "₹1,750", "msp": "₹2,090", "trend": "Downward"}
    scen_c_farm = {"crop": "Maize", "soil_type": "Red Soil", "farm_area_acres": 3.0}

    res_c = run_advisory_pipeline(
        farm_context=scen_c_farm,
        market_data=scen_c_market
    )

    msp_advs = [a for a in res_c["advisories"] if "msp" in a["id"]]
    assert len(msp_advs) == 1, "Expected MSP Protection advisory!"
    print("   >>> PASS: Government MSP Protection advisory generated when mandi price < MSP!")

    # Scenario D: Cold Wave & Frost Risk (5°C)
    print("\n4. Testing Scenario D: Cold Wave (5°C Frost Risk) + Wheat Crop...")
    scen_d_weather = {"temp_c": 5.0, "humidity": 65.0, "rainfall_mm": 0.0, "condition": "Cold Wave"}
    scen_d_farm = {"crop": "Wheat", "soil_type": "Loamy Soil", "farm_area_acres": 5.0}

    res_d = run_advisory_pipeline(
        farm_context=scen_d_farm,
        weather_data=scen_d_weather,
        growth_stage="Tillering"
    )

    cold_advs = [a for a in res_d["advisories"] if a["priority"] == "Critical" and "cold" in a["id"]]
    assert len(cold_advs) == 1, "Expected Critical Cold Wave advisory!"
    print("   >>> PASS: Critical Cold Wave Frost Protection advisory generated!")

    # Schema Key Verification Across All Generated Advisories
    print("\n5. Verifying schema contracts, keys, deduplication, and timestamps...")
    for res in [res_a, res_b, res_c, res_d]:
        advs = res["advisories"]
        seen_titles = set()
        for a in advs:
            # Check required keys (STEP 4 & STEP 5)
            assert "title" in a and isinstance(a["title"], str)
            assert "description" in a and isinstance(a["description"], str)
            assert "priority" in a and a["priority"] in ["Critical", "High", "Medium", "Low"]
            assert "reason" in a and isinstance(a["reason"], str)
            assert "source" in a and isinstance(a["source"], str)
            assert "confidence" in a and isinstance(a["confidence"], float)
            assert "timestamp" in a and isinstance(a["timestamp"], str)

            # Check deduplication (STEP 8)
            assert a["title"] not in seen_titles, f"Duplicate title found: {a['title']}"
            seen_titles.add(a["title"])

    print("   >>> PASS: All advisories strictly satisfy schema, keys, deduplication, and timestamps!")

    print("\n" + "=" * 80)
    print(" ALL PERSONALIZED AI ADVISORY ENGINE VERIFICATION TESTS PASSED PERFECTLY!")
    print("=" * 80)


if __name__ == "__main__":
    try:
        test_personalized_advisory_engine()
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)
