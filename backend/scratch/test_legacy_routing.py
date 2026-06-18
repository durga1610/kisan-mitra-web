import os
import sys
import io
import torch
from fastapi.testclient import TestClient
from PIL import Image

WORKSPACE_DIR = r"c:\Users\durga\kisan_mitra"
BACKEND_DIR = os.path.join(WORKSPACE_DIR, "backend")
sys.path.append(BACKEND_DIR)

# Set up environment variables to allow test client overrides
os.environ["APP_ENV"] = "development"
os.environ["TESTING"] = "1"
os.environ["KISAN_ALLOW_FILENAME_BYPASS"] = "0"  # Turn off filename bypass to force model inference!

from main import app, LEGACY_CLASSES, CLASSES, LEGACY_DISEASE_MODEL

def main():
    print("=== Model Routing & Healthy Resolver Verification ===")
    
    # Authenticate verify_token dependency override
    from main import verify_token
    app.dependency_overrides[verify_token] = lambda: {"uid": "test_user_uid"}
    
    client = TestClient(app)
    
    # Create a textured green image in memory to pass quality checks
    # (average brightness, not blurry, leaf pixels present)
    import numpy as np
    np.random.seed(42)
    noise = np.random.randint(0, 255, (128, 128, 3), dtype=np.uint8)
    noise[:, :, 1] = np.random.randint(100, 255, (128, 128), dtype=np.uint8) # green channel high
    noise[:, :, 0] = np.random.randint(0, 80, (128, 128), dtype=np.uint8)   # red channel low
    noise[:, :, 2] = np.random.randint(0, 80, (128, 128), dtype=np.uint8)   # blue channel low
    img = Image.fromarray(noise)
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_data = img_byte_arr.getvalue()
    
    # 1. Test Legacy routing: Apple crop
    print("\nTesting Apple routing...")
    response = client.post(
        "/api/v1/disease/detect",
        files={"file": ("upload.jpg", img_data, "image/jpeg")},
        data={"language": "en", "crop": "apple"}
    )
    print(f"Status Code: {response.status_code}")
    res = response.json()
    print(f"Response: {res}")
    
    # Assertions for Apple routing
    assert response.status_code == 200, "Failed to run inference on Apple crop"
    assert res["status"] in ["success", "confidence_failed"], f"Unexpected status: {res['status']}"
    if res["status"] == "success":
        # Check that predicted class is one of legacy classes
        predictions = [p["class"] for p in res["predictions"]]
        print(f"Predictions from model: {predictions}")
        assert any(c.startswith("Apple") for c in predictions), "Legacy routing failed to use legacy classes for Apple"
        print("PASS: Apple legacy routing verified!")
    else:
        print("Status is confidence_failed, which is also correct (model inference executed, confidence < 50%)")

    # 2. Test Legacy routing: Orange crop
    print("\nTesting Orange routing...")
    response = client.post(
        "/api/v1/disease/detect",
        files={"file": ("upload.jpg", img_data, "image/jpeg")},
        data={"language": "en", "crop": "orange"}
    )
    res = response.json()
    print(f"Response: {res}")
    assert response.status_code == 200
    if res["status"] == "success":
        predictions = [p["class"] for p in res["predictions"]]
        print(f"Predictions from model: {predictions}")
        assert any(c.startswith("Orange") for c in predictions), "Legacy routing failed to use legacy classes for Orange"
        print("PASS: Orange legacy routing verified!")

    # 3. Test Dynamic Healthy Resolver on active crop
    # In order to simulate a Plant_Healthy prediction, let's temporarily mock the model prediction to output index 19 (Plant_Healthy)
    print("\nTesting Dynamic Healthy Resolver for Rice crop...")
    
    # Store original variables
    orig_model = app.state.disease_model if hasattr(app.state, "disease_model") else None
    import main
    orig_disease_model = main.DISEASE_MODEL
    orig_classes = main.CLASSES
    
    # Set mock model and active classes
    class MockHealthyModel(torch.nn.Module):
        def __init__(self):
            super().__init__()
        def forward(self, x):
            # 20 classes output
            out = torch.zeros((x.shape[0], 20))
            out[0, 19] = 10.0  # Plant_Healthy index
            return out

    main.DISEASE_MODEL = MockHealthyModel()
    main.CLASSES = [
        "Cotton___Bacterial_Blight", "Cotton___Leaf_Curl", "Rice___Bacterial_Leaf_Blight",
        "Rice___Blast", "Rice___Brown_Spot", "Tomato___Bacterial_Spot", "Tomato___Early_Blight",
        "Tomato___Late_Blight", "Tomato___Leaf_Mold", "Tomato___Mosaic_Virus", "Tomato___Septoria_Leaf_Spot",
        "Tomato___Spider_Mites", "Tomato___Target_Spot", "Tomato___Yellow_Leaf_Curl_Virus",
        "Grape___Black_Rot", "Grape___Esca", "Grape___Leaf_Blight", "Potato___Early_Blight",
        "Potato___Late_Blight", "Plant_Healthy"
    ]
    
    response = client.post(
        "/api/v1/disease/detect",
        files={"file": ("upload.jpg", img_data, "image/jpeg")},
        data={"language": "en", "crop": "rice"}
    )
    res = response.json()
    print(f"Response: {res}")
    
    # Restore original values
    main.DISEASE_MODEL = orig_disease_model
    main.CLASSES = orig_classes

    assert response.status_code == 200
    assert res["status"] == "success"
    assert res["crop"] == "Rice"
    assert res["disease"] == "Healthy"
    assert "symptoms" in res
    assert len(res["symptoms"]) > 0, "Failed to resolve to rice_healthy DB record"
    print("PASS: Dynamic Healthy Resolver successfully mapped Plant_Healthy to Rice Healthy DB entry!")

if __name__ == "__main__":
    main()
