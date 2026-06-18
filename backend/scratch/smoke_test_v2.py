import os
import sys
import io
import torch

# Setup environment for smoke test
os.environ["KISAN_ALLOW_FILENAME_BYPASS"] = "0"  # Force true neural network inference!
os.environ["TESTING"] = "1"
os.environ["APP_ENV"] = "development"

WORKSPACE_DIR = r"c:\Users\durga\kisan_mitra"
BACKEND_DIR = os.path.join(WORKSPACE_DIR, "backend")
VAL_SET_DIR = os.path.join(BACKEND_DIR, "scratch", "field_validation_set")

sys.path.append(BACKEND_DIR)
from conftest import app
from fastapi.testclient import TestClient

client = TestClient(app)

def get_first_image(crop, class_folder):
    dir_path = os.path.join(VAL_SET_DIR, crop, class_folder)
    if not os.path.exists(dir_path):
        return None
    for f in os.listdir(dir_path):
        if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            return os.path.join(dir_path, f)
    return None

def run_post(file_path, file_name, crop_hint=None):
    if not file_path or not os.path.exists(file_path):
        # Fallback to creating a dummy JPEG image for basic routing testing
        from PIL import Image
        img = Image.new('RGB', (1, 1), color='green')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_data = img_byte_arr.getvalue()
    else:
        with open(file_path, "rb") as f:
            img_data = f.read()

    data = {"language": "en"}
    if crop_hint:
        data["crop"] = crop_hint

    response = client.post(
        "/api/v1/disease/detect",
        files={"file": (file_name, img_data, "image/jpeg")},
        data=data
    )
    return response

def main():
    print("="*80)
    print("              KISAN MITRA PRODUCTION V2 SMOKE TEST RUN")
    print("="*80)
    
    # 1. Verify model is loaded
    import main as main_app
    print(f"Active Model loaded: {main_app.DISEASE_MODEL is not None}")
    print(f"Legacy Model loaded: {main_app.LEGACY_DISEASE_MODEL is not None}")
    print(f"Number of classes active: {len(main_app.CLASSES)}")
    print("-" * 80)

    tests = [
        ("Healthy Rice Leaf", "Rice", "Rice___Healthy", "healthy_rice.jpg", None),
        ("Rice Blast Leaf", "Rice", "Rice___Blast", "rice_blast.jpg", None),
        ("Healthy Cotton Leaf", "Cotton", "Cotton___Healthy", "healthy_cotton.jpg", None),
        ("Cotton Leaf Curl Leaf", "Cotton", "Cotton___Leaf_Curl", "cotton_leaf_curl.jpg", None),
        ("Healthy Tomato Leaf", "Tomato", "Tomato___Healthy", "healthy_tomato.jpg", None),
        ("Tomato Disease Leaf", "Tomato", "Tomato___Early_Blight", "tomato_early_blight.jpg", None),
    ]

    for label, crop, class_folder, filename, hint in tests:
        path = get_first_image(crop, class_folder)
        if path:
            print(f"Testing {label:<22} | File: {os.path.basename(path)}")
        else:
            path = None
            print(f"Testing {label:<22} | File: (Dummy Image Fallback)")

        res = run_post(path, filename, crop_hint=hint)
        if res.status_code == 200:
            data = res.json()
            status = data.get("status")
            if status == "success":
                print(f"  Result: SUCCESS | Crop: {data.get('crop'):<8} | Disease: {data.get('disease'):<28} | Conf: {data.get('confidence'):.2f}%")
                # Check resolver mapping
                if "healthy" in class_folder.lower():
                    is_resolved = (data.get("disease").lower() == "healthy") and (data.get("crop").lower() == crop.lower())
                    print(f"  Resolver mapping correct: {is_resolved}")
            else:
                print(f"  Result: {status.upper()} | Reason: {data.get('reason')}")
        else:
            print(f"  Result: FAILED | Status code: {res.status_code}")
        print("-" * 80)

    # 2. Test Legacy routing
    print("Testing Legacy Crop Routing (Apple Leaf Scab)")
    # Should route to legacy model due to filename keyword 'apple'
    res = run_post(None, "apple_scab_leaf.jpg")
    if res.status_code == 200:
        data = res.json()
        status = data.get("status")
        if status == "success":
            print(f"  Result: SUCCESS | Crop: {data.get('crop'):<8} | Disease: {data.get('disease'):<28} | Conf: {data.get('confidence'):.2f}%")
            is_routed = (data.get("crop") == "Apple")
            print(f"  Legacy routing correct: {is_routed}")
        else:
            print(f"  Result: {status.upper()} | Reason: {data.get('reason')}")
    else:
        print(f"  Result: FAILED | Status code: {res.status_code}")
    print("-" * 80)

    # 3. Test Confidence Threshold Gating
    print("Testing Low Confidence Rejection Gate")
    # Low resolution/blurry/non-leaf dummy file that leads to quality/confidence failures
    # We will send a generic blank gray image to trigger quality check or low confidence
    from PIL import Image
    blank_img = Image.new('RGB', (128, 128), color='gray')
    img_byte_arr = io.BytesIO()
    blank_img.save(img_byte_arr, format='JPEG')
    gray_data = img_byte_arr.getvalue()
    
    # We pass a filename that bypasses quality checks but has low neural network confidence
    # Wait, if KISAN_ALLOW_FILENAME_BYPASS is 0, it runs the model, which will return low scores
    res = client.post(
        "/api/v1/disease/detect",
        files={"file": ("leaf.jpg", gray_data, "image/jpeg")},
        data={"language": "en"}
    )
    if res.status_code == 200:
        data = res.json()
        print(f"  Result: {data.get('status').upper()} | Reason: {data.get('reason')}")
    else:
        print(f"  Result: FAILED | Status: {res.status_code}")
    print("="*80)

if __name__ == "__main__":
    main()
