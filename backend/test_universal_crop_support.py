import pytest
import io
from PIL import Image
from fastapi.testclient import TestClient
from main import app
from advisory_engine import recommend_crops, query_rag, extract_prediction_features
from fertilizer_engine import get_fertilizer_recommendation, guess_crop_category

client = TestClient(app)

def test_unrecognized_crop_category_guessing():
    # Test that guess_crop_category correctly categorizes unrecognized crops
    assert guess_crop_category("spinach") == "leafy vegetables"
    assert guess_crop_category("lettuce") == "leafy vegetables"
    assert guess_crop_category("barley") == "cereals"
    assert guess_crop_category("chickpea") == "pulses"
    assert guess_crop_category("mustard") == "oilseeds"
    assert guess_crop_category("coconut") == "plantation crops"
    assert guess_crop_category("aloe") == "medicinal crops"

def test_unrecognized_crop_fertilizer_fallback():
    # Test that fertilizer engine falls back to category schedules for unrecognized crops
    # e.g., Spinach should fallback to Leafy Vegetables schedule
    rec = get_fertilizer_recommendation(
        farm_id="farm_1",
        crop_name_or_id="spinach",
        farm_context={"plantedCrops": ["spinach"]}
    )
    assert rec["crop"] == "spinach"
    assert "Compost" in rec["recommendation"] or "Urea" in rec["recommendation"]
    assert "leafy vegetables" in rec["reason"].lower() or "vegetative" in rec["stage"].lower() or "NPK" in rec["recommendation"]

def test_unrecognized_crop_advisory_fallbacks():
    # Check that query_rag doesn't reject unrecognized crops
    # Test FERTILIZER_QUERY fallback
    res_fert = query_rag("best fertilizer for spinach", session_id="test_sess")
    assert "spinach" in res_fert.lower()
    assert "fertilizer" in res_fert.lower() or "apply" in res_fert.lower()

    # Test IRRIGATION_QUERY fallback
    res_irr = query_rag("how much water does spinach need", session_id="test_sess")
    assert "spinach" in res_irr.lower()
    assert "irrigation" in res_irr.lower() or "water" in res_irr.lower()

    # Test DISEASE_QUERY fallback
    res_dis = query_rag("what diseases affect spinach", session_id="test_sess")
    assert "spinach" in res_dis.lower()
    assert "disease" in res_dis.lower() or "fungi" in res_dis.lower() or "mildew" in res_dis.lower()

    # Test PEST_QUERY fallback
    res_pest = query_rag("how to control pests on spinach", session_id="test_sess")
    assert "spinach" in res_pest.lower()
    assert "pest" in res_pest.lower() or "aphid" in res_pest.lower() or "neem" in res_pest.lower()

    # Test CROP_SOIL_REQUIREMENT_QUERY fallback
    res_soil = query_rag("best soil type for spinach", session_id="test_sess")
    assert "spinach" in res_soil.lower()
    assert "soil" in res_soil.lower() or "loam" in res_soil.lower()

def test_crop_recommendation_fallback():
    # Force ML model failure by passing empty preprocessors or mocking it to return empty list
    # and verify that it falls back to rule-based recommendations.
    res = recommend_crops("farm_1", "en", farm_context={
        "id": "farm_1",
        "soilType": "Red",
        "waterAvailability": "Low",
        "location": "Punjab"
    })
    assert "Recommended Crops:" in res
    assert "Best Choice:" in res
    assert "Reason:" in res

def test_disease_detection_unsupported_crop_routing():
    # Test that requesting disease detection for an unsupported crop (like mango, coconut, or spinach)
    # gets routed to the AI Vision fallback instead of failing with 400 bad request or "unsupported crop" error.
    # We will pass a dummy 256x256 green image with noise to pass resolution, blur and brightness quality checks.
    import numpy as np
    img_np = np.random.randint(50, 150, (256, 256, 3), dtype=np.uint8)
    # Make it predominantly green to pass leaf visibility check
    img_np[:, :, 1] = 200
    img = Image.fromarray(img_np)
    
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    
    response = client.post(
        "/api/v1/disease/detect",
        files={"file": ("spinach_leaf.png", img_bytes, "image/png")},
        data={"crop": "spinach", "language": "en"},
        headers={"Authorization": "Bearer dummy_token"}
    )
    
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["status"] == "success"
    assert res_json["crop"].lower() == "spinach"
    assert "disease" in res_json
    assert "treatment" in res_json
    assert "prevention" in res_json
    assert "explanation" in res_json
    assert "gradcamBase64" in res_json
