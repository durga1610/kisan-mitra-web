from fastapi.testclient import TestClient
from main import app
import json
import io

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    print("OK: Root endpoint working")

def test_disease_detect():
    # Create a valid 1x1 JPEG image in memory
    from PIL import Image
    img = Image.new('RGB', (1, 1), color='red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_data = img_byte_arr.getvalue()

    # Test generic fallback (should not crash with UnboundLocalError)
    response = client.post(
        "/api/v1/disease/detect",
        files={"file": ("test.jpg", img_data, "image/jpeg")},
        data={"language": "en"}
    )
    assert response.status_code == 200
    res_data = response.json()
    assert "crop" in res_data
    assert "disease" in res_data
    assert "confidence" in res_data
    assert "predictions" in res_data

    # Test specific keyword: apple scab
    response = client.post(
        "/api/v1/disease/detect",
        files={"file": ("apple_scab.jpg", img_data, "image/jpeg")},
        data={"language": "en"}
    )
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["crop"] == "Apple"
    assert "Scab" in res_data["disease"]

    # Test specific keyword: potato late blight
    response = client.post(
        "/api/v1/disease/detect",
        files={"file": ("potato_late_blight.png", img_data, "image/jpeg")},
        data={"language": "en"}
    )
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["crop"] == "Potato"
    assert "Late Blight" in res_data["disease"]

    # Test specific keyword: rice blast
    response = client.post(
        "/api/v1/disease/detect",
        files={"file": ("rice_blast.png", img_data, "image/jpeg")},
        data={"language": "en"}
    )
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["crop"] == "Rice"
    assert "Blast" in res_data["disease"] or "धान" in res_data["plantName"]

    # Test specific keyword: cotton bacterial blight
    response = client.post(
        "/api/v1/disease/detect",
        files={"file": ("cotton_blight.png", img_data, "image/jpeg")},
        data={"language": "en"}
    )
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["crop"] == "Cotton"
    assert "Bacterial Blight" in res_data["disease"]
    assert "organicTreatment" in res_data
    assert "explanation" in res_data
    assert "gradcamBase64" in res_data
    assert isinstance(res_data["symptoms"], list)
    assert isinstance(res_data["treatment"], list)

    # Test quality check: low-light black image
    black_img = Image.new('RGB', (224, 224), color=(15, 36, 15))
    black_byte_arr = io.BytesIO()
    black_img.save(black_byte_arr, format='JPEG')
    black_data = black_byte_arr.getvalue()
    
    response = client.post(
        "/api/v1/disease/detect",
        files={"file": ("dark_photo.jpg", black_data, "image/jpeg")},
        data={"language": "en"}
    )
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "quality_failed"
    assert "Low-light" in res_data["reason"]

    print("OK: Disease detection endpoint, quality checks, and JSON response fields working")

def test_chat_advisory():
    # Test English response for greeting
    response = client.post(
        "/api/v1/advisory/chat",
        json={
            "message": "hello",
            "language": "en"
        }
    )
    assert response.status_code == 200
    assert response.json()["text"] == "Hello! How can I help you with your farm today?"

    # Test Hindi response for greeting
    response = client.post(
        "/api/v1/advisory/chat",
        json={
            "message": "hello",
            "language": "hi"
        }
    )
    assert response.status_code == 200
    assert "नमस्कार" in response.json()["text"]

    # Test unrelated question (should be restricted)
    response = client.post(
        "/api/v1/advisory/chat",
        json={
            "message": "who is the prime minister of India?",
            "language": "en"
        }
    )
    assert response.status_code == 200
    assert "Kisan Mitra AI Advisor" in response.json()["text"]

    # 1. Test WEATHER_QUERY: current temperature at the farm
    # With valid farm context
    response = client.post(
        "/api/v1/advisory/chat",
        json={
            "message": "current temperature at the farm",
            "language": "en",
            "farm": {
                "id": "farm_1",
                "name": "Green Acres"
            }
        }
    )
    assert response.status_code == 200
    text_res = response.json()["text"]
    assert "Weather report" in text_res or "Temperature" in text_res
    assert "Rampur" in text_res or "Ludhiana" in text_res

    # Without farm context (should return Farm information unavailable)
    response = client.post(
        "/api/v1/advisory/chat",
        json={
            "message": "current temperature at the farm",
            "language": "en"
        }
    )
    assert response.status_code == 200
    assert response.json()["text"] == "Farm information unavailable."

    # 2. Test FARM_DATA_QUERY: active crops
    # With valid farm context
    response = client.post(
        "/api/v1/advisory/chat",
        json={
            "message": "What are the active crops in my field?",
            "language": "en",
            "farm": {
                "id": "farm_1",
                "name": "Green Acres"
            }
        }
    )
    assert response.status_code == 200
    text_res = response.json()["text"]
    assert "Wheat" in text_res
    assert "Mustard" in text_res
    assert "Sugarcane" in text_res

    # Without farm context (should return Farm information unavailable)
    response = client.post(
        "/api/v1/advisory/chat",
        json={
            "message": "What are the active crops in my field?",
            "language": "en"
        }
    )
    assert response.status_code == 200
    assert response.json()["text"] == "Farm information unavailable."

    # Test FARM_DATA_QUERY: crop history
    response = client.post(
        "/api/v1/advisory/chat",
        json={
            "message": "Show crop history",
            "language": "en",
            "farm": {
                "id": "farm_1",
                "name": "Green Acres"
            }
        }
    )
    assert response.status_code == 200
    text_res = response.json()["text"]
    assert "Wheat" in text_res
    assert "planted" in text_res

    # Test FARM_DATA_QUERY: disease history
    response = client.post(
        "/api/v1/advisory/chat",
        json={
            "message": "Show disease history",
            "language": "en",
            "farm": {
                "id": "farm_1",
                "name": "Green Acres"
            }
        }
    )
    assert response.status_code == 200
    text_res = response.json()["text"]
    assert "Rice Blast" in text_res

    # Test FARM_DATA_QUERY: farm details
    response = client.post(
        "/api/v1/advisory/chat",
        json={
            "message": "Show farm details",
            "language": "en",
            "farm": {
                "id": "farm_1",
                "name": "Green Acres"
            }
        }
    )
    assert response.status_code == 200
    text_res = response.json()["text"]
    assert "Ludhiana" in text_res
    assert "Alluvial" in text_res

    # Test FARM_DATA_QUERY: field status
    response = client.post(
        "/api/v1/advisory/chat",
        json={
            "message": "Show field status",
            "language": "en",
            "farm": {
                "id": "farm_1",
                "name": "Green Acres"
            }
        }
    )
    assert response.status_code == 200
    text_res = response.json()["text"]
    assert "Stage:" in text_res or "status" in text_res

    # 3. Test Unrecognized Crop: best fertilizer for xyloflower flowers
    response = client.post(
        "/api/v1/advisory/chat",
        json={
            "message": "best fertilizer for xyloflower flowers",
            "language": "en"
        }
    )
    assert response.status_code == 200
    text_res = response.json()["text"]
    assert "xyloflower" in text_res.lower()
    assert "not available in our database" in text_res.lower()

    # 4. Test FERTILIZER_QUERY: crop-specific target filtering
    response = client.post(
        "/api/v1/advisory/chat",
        json={
            "message": "What is the best fertilizer for tomato?",
            "language": "en"
        }
    )
    assert response.status_code == 200
    text_res = response.json()["text"]
    assert "tomato" in text_res.lower()
    # Should NOT contain reference to other crops due to target-filtering
    assert "paddy" not in text_res.lower()
    assert "bt cotton" not in text_res.lower()

    # 5. Test SOIL_QUERY: best crop for red soil (retrieved from RAG soil_health.txt)
    response = client.post(
        "/api/v1/advisory/chat",
        json={
            "message": "best crop for red soil",
            "language": "en"
        }
    )
    assert response.status_code == 200
    text_res = response.json()["text"]
    assert "red soil" in text_res.lower()
    assert "porous" in text_res.lower() or "retention" in text_res.lower() or "groundnut" in text_res.lower()

    # 6. Test CROP_RECOMMENDATION_QUERY: plan for next season in my farm
    # With valid farm context
    response = client.post(
        "/api/v1/advisory/chat",
        json={
            "message": "what crop can I plan for next season in my farm",
            "language": "en",
            "farm": {
                "id": "farm_1",
                "name": "Green Acres"
            }
        }
    )
    assert response.status_code == 200
    text_res = response.json()["text"]
    assert "recommended crops" in text_res.lower()
    assert "best choice" in text_res.lower()
    assert "reason" in text_res.lower()

    # Without farm context (should return Farm information unavailable)
    response = client.post(
        "/api/v1/advisory/chat",
        json={
            "message": "what crop can I plan for next season in my farm",
            "language": "en"
        }
    )
    assert response.status_code == 200
    assert response.json()["text"] == "Farm information unavailable."

    # 7. Test Firebase context mapping (USE_FIREBASE_CONTEXT = True) with dynamic Firestore ID
    # Query: What is the soil type of the farm?
    response = client.post(
        "/api/v1/advisory/chat",
        json={
            "message": "What is the soil type of the farm?",
            "language": "en",
            "farm": {
                "id": "R63Wpq1G",
                "ownerId": "user_123",
                "name": "Dynamic Field",
                "location": "Rampur, Ludhiana, Punjab",
                "soilType": "Alluvial Soil",
                "waterAvailability": "High",
                "plantedCrops": ["Wheat", "Mustard", "Sugarcane"]
            }
        }
    )
    assert response.status_code == 200
    assert response.json()["text"] == "Farm Soil Type: Alluvial Soil"

    # Query: Location of the farm
    response = client.post(
        "/api/v1/advisory/chat",
        json={
            "message": "Location of the farm",
            "language": "en",
            "farm": {
                "id": "R63Wpq1G",
                "ownerId": "user_123",
                "name": "Dynamic Field",
                "location": "Rampur, Ludhiana, Punjab",
                "soilType": "Alluvial Soil",
                "waterAvailability": "High",
                "plantedCrops": ["Wheat", "Mustard", "Sugarcane"]
            }
        }
    )
    assert response.status_code == 200
    assert response.json()["text"] == "Rampur, Ludhiana, Punjab"

    # Query: active crops in the farm
    response = client.post(
        "/api/v1/advisory/chat",
        json={
            "message": "active crops in the farm",
            "language": "en",
            "farm": {
                "id": "R63Wpq1G",
                "ownerId": "user_123",
                "name": "Dynamic Field",
                "location": "Rampur, Ludhiana, Punjab",
                "soilType": "Alluvial Soil",
                "waterAvailability": "High",
                "plantedCrops": ["Wheat", "Mustard", "Sugarcane"]
            }
        }
    )
    assert response.status_code == 200
    text_res = response.json()["text"]
    assert "Wheat" in text_res
    assert "Mustard" in text_res
    assert "Sugarcane" in text_res

    print("OK: Chat advisory endpoint and advanced query/memory routing working")


def test_generate_advisory():
    response = client.post(
        "/api/v1/advisory/generate",
        json={
            "crop": "Rice",
            "soil": "Clayey",
            "location": "Punjab",
            "weather": "Sunny",
            "language": "en"
        }
    )
    assert response.status_code == 200
    assert "Rice" in response.json()["text"]
    print("OK: Specialized advisory generator working")

def test_crop_suitability():
    response = client.post(
        "/api/v1/advisory/suitability",
        json={
            "cropName": "Paddy Rice",
            "farm": {
                "soilType": "Sandy Soil",
                "waterAvailability": "Low"
            }
        }
    )
    assert response.status_code == 200
    print(f"Suitability Response: {response.json()}")
    assert response.json()["suitable"] == False
    assert "sandy" in response.json()["reason"].lower()
    print("OK: Suitability rule engine working")

def test_daily_guidance():
    response = client.post(
        "/api/v1/advisory/daily-guidance",
        json={
            "cropName": "Tomato",
            "cropAgeDays": 15,
            "state": "Maharashtra",
            "soilType": "Black Soil",
            "language": "en"
        }
    )
    assert response.status_code == 200
    guidance = response.json()
    assert len(guidance) == 5
    assert guidance[0]["dayOffset"] == -2
    print("OK: Daily guidance generator working")

def test_reasoning():
    response = client.post(
        "/api/v1/advisory/reasoning",
        json={
            "cropName": "Tomato",
            "farm": {"soilType": "Black Soil"},
            "weather": {"condition": "Sunny", "temperature": 30.0, "season": "Kharif"},
            "marketTrend": "High demand"
        }
    )
    assert response.status_code == 200
    assert "Growing Tomato is a smart choice" in response.json()["text"]
    print("OK: Suitability reasoning generator working")

def test_gemini_status():
    response = client.get("/api/v1/system/gemini-status")
    assert response.status_code == 200
    data = response.json()
    assert "keys_detected" in data
    assert "active_key_index" in data
    assert "healthy_keys" in data
    assert "cache_enabled" in data
    assert "cache_entries" in data
    assert "last_rotation" in data
    assert data["cache_enabled"] is True
    print("OK: Gemini status endpoint working")

if __name__ == "__main__":
    print("Running API tests...")
    test_root()
    test_disease_detect()
    test_chat_advisory()
    test_generate_advisory()
    test_crop_suitability()
    test_daily_guidance()
    test_reasoning()
    test_gemini_status()
    print("All backend API tests passed successfully!")

