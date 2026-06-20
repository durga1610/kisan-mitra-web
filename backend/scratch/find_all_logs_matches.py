import os
import sys
import torch
import numpy as np
from PIL import Image

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import main
from disease_transforms import DISEASE_TRANSFORM as inference_transforms

def scan_all():
    main.init_disease_model()
    
    test_root = r"c:\Users\durga\kisan_mitra\dataset\test"
    temp_dir = r"C:\Users\durga\.gemini\antigravity-ide\brain\ffa2701b-34c2-4911-b6a3-3afe2b289ce5\.tempmediaStorage"
    
    image_paths = []
    
    # 1. Gather all files in temp_dir
    if os.path.exists(temp_dir):
        for fname in os.listdir(temp_dir):
            if fname.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                image_paths.append((temp_dir, fname))
                
    # 2. Gather all files in test_root
    if os.path.exists(test_root):
        for root, dirs, files in os.walk(test_root):
            for fname in files:
                if fname.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                    image_paths.append((root, fname))
                    
    print(f"Gathered {len(image_paths)} images to check.")
    
    targets = [
        {"name": "Potato Late Blight rejection", "q": 93.62, "c": 42.18},
        {"name": "Tomato Late Blight rejection", "q": 87.51, "c": 23.19},
        {"name": "Grape Black Rot rejection 1", "q": 92.29, "c": 43.88},
        {"name": "Grape Black Rot rejection 2", "q": 95.39, "c": 34.54}
    ]
    
    for folder, fname in image_paths:
        fpath = os.path.join(folder, fname)
        try:
            image = Image.open(fpath)
            quality_ok, msg, q_score = main.check_image_quality(image)
            tensor_img = inference_transforms(image).unsqueeze(0)
            
            with torch.no_grad():
                # Single-stage prediction because CROP_MODEL is None for fallback ResNet18
                outputs = main.DISEASE_MODEL(tensor_img)
                probs = torch.softmax(outputs, dim=1)[0]
                top_prob, top_idx = torch.max(probs, dim=0)
                pred_class = main.CLASSES[top_idx.item()]
                confidence = top_prob.item() * 100
                
            for t in targets:
                if abs(q_score - t["q"]) < 0.2 and abs(confidence - t["c"]) < 0.5:
                    print(f"\n[FOUND MATCH for {t['name']}] File: {fname} in {folder}")
                    print(f"Quality Score: {q_score:.4f}% | Class: {pred_class} | Confidence: {confidence:.4f}%")
                    
                    gray = image.convert("L")
                    img_np = np.array(gray).astype(float)
                    avg_brightness = np.mean(img_np)
                    laplacian = np.abs(img_np[1:-1, 1:-1] * 4 - img_np[:-2, 1:-1] - img_np[2:, 1:-1] - img_np[1:-1, :-2] - img_np[1:-1, 2:])
                    variance = np.var(laplacian)
                    
                    img_rgb = np.array(image.convert("RGB"))
                    R = img_rgb[:, :, 0].astype(float)
                    G = img_rgb[:, :, 1].astype(float)
                    B = img_rgb[:, :, 2].astype(float)
                    green_mask = (G > R * 1.02) & (G > B * 1.02) & (G > 35)
                    brown_mask = (R > G * 1.05) & (G > B * 1.05) & (R > 40)
                    yellow_mask = (R > 90) & (G > 90) & (B < R * 0.75)
                    leaf_pixels = np.sum(green_mask | brown_mask | yellow_mask)
                    total_pixels = image.width * image.height
                    leaf_coverage = (leaf_pixels / total_pixels) * 100
                    
                    # Contrast calculation
                    contrast = np.std(img_np)
                    
                    print(f"Dimensions: {image.width}x{image.height}")
                    print(f"Blur Score (variance): {variance:.4f}")
                    print(f"Brightness Score (mean): {avg_brightness:.4f}")
                    print(f"Contrast Score (std): {contrast:.4f}")
                    print(f"Leaf Coverage Percentage: {leaf_coverage:.4f}%")
                    print(f"Quality check passed: {quality_ok} (Reason: {msg})")
                    print("--------------------------------------------------")
        except Exception as e:
            pass

if __name__ == "__main__":
    scan_all()
