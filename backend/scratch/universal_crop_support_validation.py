import os
import sys
import io
import json
from datetime import datetime
import numpy as np
from PIL import Image

# Set TESTING env var to bypass daily/in-memory rate limit cap during automated testing
os.environ["TESTING"] = "1"

# Ensure backend directory is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from main import app, verify_token

# Bypass authentication by overriding verify_token dependency
app.dependency_overrides[verify_token] = lambda: {
    "uid": "validation_test_user",
    "email": "testfarmer@example.com",
    "name": "Validation Farmer"
}

app.state.limiter.enabled = False
client = TestClient(app)

CROPS_TO_TEST = [
    # Cereals
    {"crop": "barley", "category": "Cereals"},
    {"crop": "sorghum", "category": "Cereals"},
    {"crop": "millet", "category": "Cereals"},
    # Pulses
    {"crop": "chickpea", "category": "Pulses"},
    {"crop": "lentil", "category": "Pulses"},
    {"crop": "cowpea", "category": "Pulses"},
    # Oilseeds
    {"crop": "sunflower", "category": "Oilseeds"},
    {"crop": "mustard", "category": "Oilseeds"},
    {"crop": "sesame", "category": "Oilseeds"},
    # Leafy Vegetables
    {"crop": "spinach", "category": "Leafy Vegetables"},
    {"crop": "lettuce", "category": "Leafy Vegetables"},
    {"crop": "cabbage", "category": "Leafy Vegetables"},
    # Fruits
    {"crop": "mango", "category": "Fruits"},
    {"crop": "banana", "category": "Fruits"},
    {"crop": "orange", "category": "Fruits"},
    # Spices
    {"crop": "chilli", "category": "Spices"},
    {"crop": "ginger", "category": "Spices"},
    {"crop": "garlic", "category": "Spices"},
    # Plantation Crops
    {"crop": "coconut", "category": "Plantation Crops"},
    {"crop": "coffee", "category": "Plantation Crops"},
    {"crop": "sugarcane", "category": "Plantation Crops"},
    # Medicinal Crops
    {"crop": "aloe vera", "category": "Medicinal Crops"},
    {"crop": "ashwagandha", "category": "Medicinal Crops"},
    {"crop": "neem", "category": "Medicinal Crops"},
]

def generate_dummy_leaf_image():
    # Make a 256x256 image with green color and random noise to pass resolution/blur/brightness checks
    img_np = np.random.randint(50, 150, (256, 256, 3), dtype=np.uint8)
    img_np[:, :, 1] = 200 # Heavy green to pass leaf visibility checks
    img = Image.fromarray(img_np)
    
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    return img_bytes.getvalue()

def run_validation():
    print("Starting Universal Crop Support Validation Audit...")
    
    # Generate test image once
    leaf_image_data = generate_dummy_leaf_image()
    
    results = []
    failed_crops = []
    missing_data_entries = []
    
    total_checks = 0
    passed_checks = 0
    
    category_metrics = {}
    
    for item in CROPS_TO_TEST:
        crop = item["crop"]
        category = item["category"]
        category_metrics.setdefault(category, {"total": 0, "passed": 0})
        
        print(f"\nEvaluating crop: {crop.upper()} (Category: {category})")
        
        crop_status = {
            "crop": crop,
            "category": category,
            "fertilizer": "FAIL",
            "advisor": "FAIL",
            "recommendation": "FAIL",
            "disease_fallback": "FAIL",
            "errors": []
        }
        
        # 1. Test Fertilizer Recommendation
        try:
            total_checks += 1
            category_metrics[category]["total"] += 1
            res = client.post(
                "/api/v1/fertilizer/recommend",
                json={
                    "farmId": "default",
                    "cropId": crop,
                    "plantedDate": "2026-06-04"
                },
                headers={"Authorization": "Bearer dummy_token"}
            )
            
            if res.status_code == 200:
                res_data = res.json()
                # Check for N/A values and unsupported crop strings
                res_str = json.dumps(res_data).lower()
                if "n/a" in res_str:
                    crop_status["errors"].append("Fertilizer response contains N/A values")
                elif "unsupported" in res_str:
                    crop_status["errors"].append("Fertilizer response contains unsupported crop error message")
                else:
                    crop_status["fertilizer"] = "PASS"
                    passed_checks += 1
                    category_metrics[category]["passed"] += 1
            else:
                crop_status["errors"].append(f"Fertilizer API failed with status code {res.status_code}: {res.text}")
        except Exception as e:
            crop_status["errors"].append(f"Fertilizer API threw exception: {e}")
            
        # 2. Test AI Advisor (chat)
        try:
            total_checks += 1
            category_metrics[category]["total"] += 1
            res = client.post(
                "/api/v1/advisory/chat",
                json={
                    "message": f"best fertilizer and water guidelines for {crop}",
                    "language": "en"
                }
            )
            
            if res.status_code == 200:
                res_data = res.json()
                text = res_data.get("text", "").lower()
                if "not available in our database" in text:
                    crop_status["errors"].append("Advisor returned unrecognized database guidelines fallback message")
                    missing_data_entries.append(f"{crop} missing from database RAG context")
                elif "unsupported" in text:
                    crop_status["errors"].append("Advisor response contained unsupported crop error")
                elif "n/a" in text:
                    crop_status["errors"].append("Advisor response contains N/A value")
                else:
                    crop_status["advisor"] = "PASS"
                    passed_checks += 1
                    category_metrics[category]["passed"] += 1
            else:
                crop_status["errors"].append(f"AI Advisor API failed with status code {res.status_code}: {res.text}")
        except Exception as e:
            crop_status["errors"].append(f"AI Advisor API threw exception: {e}")
            
        # 3. Test Crop Recommendation (Suitability)
        try:
            total_checks += 1
            category_metrics[category]["total"] += 1
            res = client.post(
                "/api/v1/advisory/suitability",
                json={
                    "cropName": crop,
                    "farm": {
                        "soilType": "Loamy Soil",
                        "waterAvailability": "Moderate"
                    }
                }
            )
            
            if res.status_code == 200:
                res_data = res.json()
                reason = res_data.get("reason", "").lower()
                if "unsupported" in reason:
                    crop_status["errors"].append("Suitability check returned unsupported crop error")
                elif "n/a" in reason:
                    crop_status["errors"].append("Suitability check contains N/A value")
                else:
                    crop_status["recommendation"] = "PASS"
                    passed_checks += 1
                    category_metrics[category]["passed"] += 1
            else:
                crop_status["errors"].append(f"Suitability API failed with status code {res.status_code}: {res.text}")
        except Exception as e:
            crop_status["errors"].append(f"Suitability API threw exception: {e}")
            
        # 4. Test Disease Detection Fallback
        try:
            total_checks += 1
            category_metrics[category]["total"] += 1
            res = client.post(
                "/api/v1/disease/detect",
                files={"file": (f"{crop}_leaf.png", leaf_image_data, "image/png")},
                data={"crop": crop, "language": "en"},
                headers={"Authorization": "Bearer dummy_token"}
            )
            
            if res.status_code == 200:
                res_data = res.json()
                clean_data = {k: v for k, v in res_data.items() if k != "gradcamBase64"}
                res_str = json.dumps(clean_data).lower()
                if res_data.get("status") == "quality_failed":
                    crop_status["errors"].append(f"Disease detection failed quality check: {res_data.get('reason')}")
                elif "unsupported" in res_str:
                    crop_status["errors"].append("Disease detection response contained unsupported crop error")
                elif "n/a" in res_str:
                    crop_status["errors"].append("Disease detection response contains N/A value")
                elif res_data.get("status") != "success":
                    crop_status["errors"].append(f"Disease detection failed status check: {res_data.get('status')}")
                else:
                    crop_status["disease_fallback"] = "PASS"
                    passed_checks += 1
                    category_metrics[category]["passed"] += 1
            else:
                crop_status["errors"].append(f"Disease detection API failed with status code {res.status_code}: {res.text}")
        except Exception as e:
            crop_status["errors"].append(f"Disease detection API threw exception: {e}")
            
        # Check if the crop has any failures
        if crop_status["errors"]:
            failed_crops.append(crop_status)
            
        results.append(crop_status)
        
    # Generate final stats
    readiness_score = (passed_checks / total_checks) * 100 if total_checks > 0 else 0.0
    
    print("\n==================================================")
    print("UNIVERSAL CROP SUPPORT VALIDATION SUMMARY")
    print("==================================================")
    print(f"Total Crops Tested: {len(CROPS_TO_TEST)}")
    print(f"Total Validation Checks: {total_checks}")
    print(f"Passed Checks: {passed_checks}")
    print(f"Failed Checks: {total_checks - passed_checks}")
    print(f"Production Readiness Score: {readiness_score:.2f}%")
    print("==================================================")
    
    # Save Report to markdown file
    report_path = "C:/Users/durga/.gemini/antigravity-ide/brain/ffa2701b-34c2-4911-b6a3-3afe2b289ce5/universal_crop_validation_report.md"
    
    # Build report content
    content = []
    content.append("# Universal Crop Validation Report\n")
    content.append(f"**Audit Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    content.append(f"**Total Crops Evaluated:** {len(CROPS_TO_TEST)}")
    content.append(f"**Total Verification Checks Run:** {total_checks}")
    content.append(f"**Passed Checks:** {passed_checks}")
    content.append(f"**Failed Checks:** {total_checks - passed_checks}")
    content.append(f"**Production Readiness Score:** `{readiness_score:.2f}%`\n")
    
    content.append("## Coverage Matrix\n")
    content.append("| Crop | Category | Fertilizer Advice | AI Advisor | Crop Suitability | Disease Fallback | Status |")
    content.append("| :--- | :--- | :---: | :---: | :---: | :---: | :---: |")
    for r in results:
        status_symbol = "✅ PASS" if not r["errors"] else "❌ FAIL"
        content.append(f"| {r['crop'].title()} | {r['category']} | {'🟢' if r['fertilizer'] == 'PASS' else '🔴'} | {'🟢' if r['advisor'] == 'PASS' else '🔴'} | {'🟢' if r['recommendation'] == 'PASS' else '🔴'} | {'🟢' if r['disease_fallback'] == 'PASS' else '🔴'} | {status_symbol} |")
        
    content.append("\n## Category Summary\n")
    content.append("| Category | Total Checks | Passed Checks | Success Rate |")
    content.append("| :--- | :---: | :---: | :---: |")
    for cat, metrics in category_metrics.items():
        rate = (metrics["passed"] / metrics["total"]) * 100 if metrics["total"] > 0 else 0
        content.append(f"| {cat} | {metrics['total']} | {metrics['passed']} | {rate:.2f}% |")
        
    content.append("\n## Failed Crops\n")
    if failed_crops:
        for f in failed_crops:
            content.append(f"### ❌ {f['crop'].title()} ({f['category']})")
            for err in f["errors"]:
                content.append(f"- {err}")
    else:
        content.append("None. All tested crops passed 100% of validation checks!\n")
        
    content.append("\n## Missing Data Entries\n")
    if missing_data_entries:
        for m in missing_data_entries:
            content.append(f"- {m}")
    else:
        content.append("None. No data entry or database RAG fallback errors were observed during validation.\n")
        
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(content))
        
    print(f"Validation report successfully written to: {report_path}")

if __name__ == "__main__":
    run_validation()
