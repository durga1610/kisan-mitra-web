import os
import sys
import torch
import numpy as np
from PIL import Image

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import main
from disease_transforms import DISEASE_TRANSFORM as inference_transforms

def main_run():
    main.init_disease_model()
    
    test_root = r"c:\Users\durga\kisan_mitra\dataset\test"
    temp_dir = r"C:\Users\durga\.gemini\antigravity-ide\brain\ffa2701b-34c2-4911-b6a3-3afe2b289ce5\.tempmediaStorage"
    
    # We will gather all image files recursively
    image_paths = []
    
    if os.path.exists(temp_dir):
        for fname in os.listdir(temp_dir):
            if fname.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                image_paths.append((temp_dir, fname))
                
    if os.path.exists(test_root):
        for root, dirs, files in os.walk(test_root):
            for fname in files:
                if fname.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                    image_paths.append((root, fname))
                    
    print(f"Gathered {len(image_paths)} total images to scan.")
    
    for folder, fname in image_paths:
        fpath = os.path.join(folder, fname)
        try:
            image = Image.open(fpath)
            quality_ok, msg, q_score = main.check_image_quality(image)
            
            # Run model prediction
            tensor_img = inference_transforms(image).unsqueeze(0)
            with torch.no_grad():
                outputs = main.DISEASE_MODEL(tensor_img)
                probs = torch.softmax(outputs, dim=1)[0]
                top_prob, top_idx = torch.max(probs, dim=0)
                pred_class = main.CLASSES[top_idx.item()]
                confidence = top_prob.item() * 100
                
                # Check Potato Match: confidence ~ 42.18, quality ~ 93.62
                is_potato = abs(q_score - 93.62) < 0.1 and abs(confidence - 42.18) < 0.1
                # Check Tomato Match: confidence ~ 23.19, quality ~ 87.51
                is_tomato = abs(q_score - 87.51) < 0.1 and abs(confidence - 23.19) < 0.1
                # Check Grape Match 1: confidence ~ 43.88, quality ~ 92.29
                is_grape1 = abs(q_score - 92.29) < 0.1 and abs(confidence - 43.88) < 0.1
                # Check Grape Match 2: confidence ~ 34.54, quality ~ 95.39
                is_grape2 = abs(q_score - 95.39) < 0.1 and abs(confidence - 34.54) < 0.1
                
                if is_potato or is_tomato or is_grape1 or is_grape2:
                    print(f"\n[FOUND MATCH] File: {fname} in {folder}")
                    print(f"Quality Score: {q_score:.4f}% | Class: {pred_class} | Confidence: {confidence:.4f}%")
                    
                    # Convert to grayscale for brightness/blur
                    gray = image.convert("L")
                    img_np = np.array(gray).astype(float)
                    avg_brightness = np.mean(img_np)
                    laplacian = np.abs(img_np[1:-1, 1:-1] * 4 - img_np[:-2, 1:-1] - img_np[2:, 1:-1] - img_np[1:-1, :-2] - img_np[1:-1, 2:])
                    variance = np.var(laplacian)
                    
                    # Leaf pixels
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
                    
                    print(f"Dimensions: {image.width}x{image.height}")
                    print(f"Blur score (variance): {variance:.4f}")
                    print(f"Brightness score (average): {avg_brightness:.4f}")
                    print(f"Leaf coverage: {leaf_coverage:.4f}%")
                    print(f"Quality check passed: {quality_ok} (Reason: {msg})")
                    print("--------------------------------------------------")
                    
        except Exception as e:
            pass

if __name__ == "__main__":
    main_run()
