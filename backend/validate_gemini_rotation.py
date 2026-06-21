"""
validate_gemini_rotation.py
----------------------------
Validation script for Gemini High-Availability Key Rotation and Caching.
Tests 6 key scenarios to verify fallback, rotation, cache hits, and database logging.
"""

import sys
import os
import json
import sqlite3
from datetime import datetime

# Adjust path to import backend modules correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "services"))

from services.gemini_fallback import (
    generate_advisory,
    generate_fertilizer_advice,
    analyze_disease_vision,
    generate_crop_recommendations,
    verify_leaf_presence,
    analyze_market_prices,
    get_key_manager_stats,
    reset_exhausted_keys,
    normalize_query
)
from config import DB_PATH

def run_scenario(name, func, *args, **kwargs):
    print("\n" + "="*80)
    print(f" SCENARIO: {name}")
    print("="*80)
    
    start_time = datetime.now()
    try:
        result = func(*args, **kwargs)
        duration = (datetime.now() - start_time).total_seconds()
        print(f"Duration: {duration:.3f} seconds")
        print("Response (Truncated if too long):")
        print(json.dumps(result, indent=2)[:800])
        return result
    except Exception as e:
        print(f"FAILED with exception: {e}")
        return None

def check_db_logs():
    print("\n" + "="*80)
    print(" RECENT LOGS FROM gemini_key_rotation_log")
    print("="*80)
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM gemini_key_rotation_log ORDER BY id DESC LIMIT 15")
        rows = cursor.fetchall()
        for r in rows:
            print(dict(r))
        
        cursor.execute("SELECT COUNT(*) FROM gemini_key_rotation_log")
        total_logs = cursor.fetchone()[0]
        print(f"\nTotal rotation logs: {total_logs}")
        
        cursor.execute("SELECT COUNT(*) FROM gemini_response_cache")
        total_cache = cursor.fetchone()[0]
        print(f"Total response cache entries: {total_cache}")
        conn.close()
    except Exception as e:
        print(f"Error checking DB logs: {e}")

def main():
    print("Initializing tests. Testing environment variables:")
    for i in range(1, 7):
        val = os.getenv(f"GEMINI_API_KEY_{i}")
        status = "Present (Value Hidden)" if val else "Not Present"
        print(f"  GEMINI_API_KEY_{i}: {status}")
    print(f"  Legacy GEMINI_API_KEY: {'Present' if os.getenv('GEMINI_API_KEY') else 'Not Present'}")
    
    print("\nStats before testing:")
    print(json.dumps(get_key_manager_stats(), indent=2))
    
    # 1. Banana Fertilizer -> expect LOCAL_MATCH
    run_scenario(
        "1. Banana Fertilizer (Local Match)",
        generate_fertilizer_advice,
        crop="banana",
        age=45,
        stage="Vegetative",
        soil="Alluvial",
        weather="Sunny",
        trigger_reason="manual_test",
        user_uid="test_user_1"
    )
    
    # 2. Papaya Fertilizer -> expect LOCAL_MATCH
    run_scenario(
        "2. Papaya Fertilizer (Local Match)",
        generate_fertilizer_advice,
        crop="papaya",
        age=30,
        stage="Vegetative",
        soil="Sandy Loam",
        weather="Humid",
        trigger_reason="manual_test",
        user_uid="test_user_1"
    )
    
    # 3. Dragon Fruit Fertilizer -> expect Gemini call or Local Fallback
    run_scenario(
        "3. Dragon Fruit Fertilizer (Not in local list -> Gemini call/fallback)",
        generate_fertilizer_advice,
        crop="dragon fruit",
        age=60,
        stage="Vegetative",
        soil="Loamy",
        weather="Warm",
        trigger_reason="manual_test",
        user_uid="test_user_2"
    )
    
    # 4. Summer Crop Recommendation -> expect Gemini call or Local Fallback
    run_scenario(
        "4. Crop Recommendation (Gemini/Fallback)",
        generate_crop_recommendations,
        state="Punjab",
        district="Ludhiana",
        weather={"temp": 38.0, "humidity": 45.0},
        soil="Alluvial",
        water="Canal",
        land_area=5.0,
        market_data=[],
        user_uid="test_user_3"
    )
    
    # 5. Cotton Pest Control (Advisory Chat Scenario)
    run_scenario(
        "5. Cotton Pest Control (Advisory)",
        generate_advisory,
        message="What is the best pesticide for cotton bollworm pest control?",
        farm_context={"crop": "cotton", "soil": "Black Soil"},
        weather_context={"temp": 32.0},
        trigger_reason="manual_test",
        user_uid="test_user_4"
    )
    
    # 6. Rice Disease Management (Advisory Chat Scenario)
    run_scenario(
        "6. Rice Disease Management (Advisory)",
        generate_advisory,
        message="My rice field has leaf blast disease, how to manage rog?",
        farm_context={"crop": "rice", "soil": "Clayey Soil"},
        weather_context={"temp": 28.0},
        trigger_reason="manual_test",
        user_uid="test_user_5"
    )

    # 7. Image-based disease detection fallback test
    dummy_image = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    run_scenario(
        "7. Leaf Presence Verification (Vision Fallback)",
        verify_leaf_presence,
        image_bytes=dummy_image,
        user_uid="test_user_6"
    )
    
    run_scenario(
        "8. Disease Detection Vision (Vision)",
        analyze_disease_vision,
        image_bytes=dummy_image,
        crop_hint="tomato",
        weather_context={"temp": 25.0},
        farm_context={"crop": "tomato"},
        user_uid="test_user_7"
    )
    
    # 9. Market Prices fallback test
    run_scenario(
        "9. Market Prices (Gemini/Fallback)",
        analyze_market_prices,
        crop="cotton",
        state="Maharashtra",
        recent_prices=[],
        user_uid="test_user_8"
    )

    # Mock Key Rotation and Failover Scenario
    print("\n" + "="*80)
    print(" SCENARIO: Mock Key Rotation & Recovery (Failover test)")
    print("="*80)
    from unittest.mock import MagicMock, patch
    from google.api_core.exceptions import ResourceExhausted
    from services.gemini_fallback import _KEY_MANAGER

    # Set up mock keys in the manager
    reset_exhausted_keys()
    _KEY_MANAGER._keys = ["MOCK_KEY_1", "MOCK_KEY_2", "MOCK_KEY_3"]
    _KEY_MANAGER._active_index = 0
    _KEY_MANAGER._exhausted = set()

    print("Initial mock manager stats:", json.dumps(get_key_manager_stats(), indent=2))

    mock_response = MagicMock()
    mock_response.text = '{"crop": "dragon fruit", "stage": "Vegetative", "recommendation": "Mocked Gemini Success Advice on KEY_3", "dosage": "5 kg", "organicAlternative": "Neem", "timing": "Morning", "precautions": "None"}'

    call_count = 0
    def side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            print("  [Mock API] Call with KEY_1 -> Raising ResourceExhausted (Quota Limit)")
            raise ResourceExhausted("Quota exceeded for Key 1")
        elif call_count == 2:
            print("  [Mock API] Call with KEY_2 -> Raising ResourceExhausted (Quota Limit)")
            raise ResourceExhausted("Quota exceeded for Key 2")
        else:
            print("  [Mock API] Call with KEY_3 -> Success!")
            return mock_response

    mock_model = MagicMock()
    mock_model.generate_content.side_effect = side_effect

    with patch("google.generativeai.GenerativeModel", return_value=mock_model):
        # Clear cache to guarantee Gemini call is invoked
        from services.gemini_fallback import _make_normalized_cache_key
        cache_key = _make_normalized_cache_key("fertilizer", "dragon fruit vegetative fertilizer loamy")
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("DELETE FROM gemini_response_cache WHERE cache_key = ?", (cache_key,))
            conn.commit()
            conn.close()
        except Exception:
            pass

        result = generate_fertilizer_advice(
            crop="dragon fruit",
            age=60,
            stage="Vegetative",
            soil="Loamy",
            weather="Warm",
            trigger_reason="rotation_test",
            user_uid="mock_tester"
        )
        print("Final response result:", json.dumps(result, indent=2))
        print("Stats after mock rotation:", json.dumps(get_key_manager_stats(), indent=2))

    # Cache normalisation test
    print("\n" + "="*80)
    print(" CACHE KEY NORMALISATION TEST")
    print("="*80)
    q1 = "fertiliser for banana crop"
    q2 = "fertilizer for banana crop"
    q3 = "banana fertilizer"
    print(f"Normalizing '{q1}' -> '{normalize_query(q1)}'")
    print(f"Normalizing '{q2}' -> '{normalize_query(q2)}'")
    print(f"Normalizing '{q3}' -> '{normalize_query(q3)}'")
    assert normalize_query(q1) == normalize_query(q2) == normalize_query(q3), "Query normalisation failed!"
    print("Query normalisation SUCCESS: All queries normalise to the same key.")

    print("\nStats after testing:")
    print(json.dumps(get_key_manager_stats(), indent=2))
    
    # Check Database logs
    check_db_logs()

if __name__ == "__main__":
    main()
