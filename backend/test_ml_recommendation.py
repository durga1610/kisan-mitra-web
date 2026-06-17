import json
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_endpoints():
    print("Testing /api/v1/crop-recommendation/predict...")
    predict_payload = {
        "farm": {
            "id": "farm_1",
            "name": "Green Acres",
            "location": "Rampur, Karnal, Haryana",
            "soilType": "Clayey",
            "waterAvailability": "High",
            "landArea": 8.5,
            "plantedCrops": ["Wheat"]
        },
        "weather": {
            "condition": "Humid and Overcast",
            "temperature": 28.5,
            "season": "Kharif"
        }
    }
    
    response = client.post("/api/v1/crop-recommendation/predict", json=predict_payload)
    print("Predict Status:", response.status_code)
    print("Predict JSON Response:")
    print(json.dumps(response.json(), indent=2))
    
    assert response.status_code == 200
    assert "top_recommendations" in response.json()
    recs = response.json()["top_recommendations"]
    assert len(recs) > 0
    for r in recs:
        assert "crop" in r
        assert "score" in r
        assert isinstance(r["score"], int)

    print("\nTesting /api/v1/advisory/recommendations...")
    adv_payload = {
        "farm": {
            "id": "farm_1",
            "name": "Green Acres",
            "location": "Rampur, Karnal, Haryana",
            "soilType": "Clayey",
            "waterAvailability": "High",
            "landArea": 8.5,
            "plantedCrops": ["Wheat"]
        },
        "weather": {
            "condition": "Humid and Overcast",
            "temperature": 28.5,
            "season": "Kharif"
        },
        "availableMarketCrops": ["Tomato", "Paddy Rice", "Cotton", "Wheat", "Maize", "Potato", "Yellow Mustard", "Sugarcane", "Soybean"],
        "language": "en"
    }
    
    response = client.post("/api/v1/advisory/recommendations", json=adv_payload)
    print("Advisory recommendations Status:", response.status_code)
    print("Advisory recommendations JSON Response:")
    print(json.dumps(response.json(), indent=2))
    
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0
    for r in results:
        assert "cropName" in r
        assert "marketDemand" in r
        assert "expectedProfit" in r
        assert "growthPeriod" in r
        assert "matchReason" in r
        assert "suitabilityScore" in r
        assert isinstance(r["suitabilityScore"], float)

    print("\nTesting chatbot recommendation query...")
    chat_payload = {
        "message": "what crop can I plan for next season in my farm",
        "language": "en",
        "farm": {
            "id": "farm_1",
            "name": "Green Acres"
        }
    }
    response = client.post("/api/v1/advisory/chat", json=chat_payload)
    print("Chat Status:", response.status_code)
    print("Chat response:")
    print(response.json()["text"])
    assert response.status_code == 200
    text = response.json()["text"].lower()
    assert "recommended crops" in text
    assert "best choice" in text
    assert "reason" in text

    print("\nAll tests passed successfully!")

if __name__ == "__main__":
    test_endpoints()
