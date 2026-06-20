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
    
    # We will search the dataset/test directory and temp media storage for images that match
    search_dirs = [
        r"C:\Users\durga\.gemini\antigravity-ide\brain\ffa2701b-34c2-4911-b6a3-3afe2b289ce5\.tempmediaStorage",
        r"c:\Users\durga\kisan_mitra\dataset\test\Potato___Late_Blight",
        r"c:\Users\durga\kisan_mitra\dataset\test\Tomato___Late_Blight",
        r"c:\Users\durga\kisan_mitra\dataset\test\Grape___Black_Rot"
    ]
    
    print("Searching for matching images...")
    
    for s_dir in search_dirs:
        if not os.path.exists(s_dir):
            continue
        print(f"Searching in {s_dir}...")
        for fname in os.listdir(s_dir):
            fpath = os.path.join(s_dir, fname)
            if not fpath.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                continue
                
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
                    
                    # Print if it's close to any of our target conditions
                    is_potato_match = abs(q_score - 93.62) < 1.0 and abs(confidence - 42.18) < 1.0
                    is_tomato_match = abs(q_score - 87.51) < 1.0 and abs(confidence - 23.19) < 1.0
                    is_grape_match1 = abs(q_score - 92.29) < 1.0 and abs(confidence - 43.88) < 1.0
                    is_grape_match2 = abs(q_score - 95.39) < 1.0 and abs(confidence - 34.54) < 1.0
                    
                    if is_potato_match or is_tomato_match or is_grape_match1 or is_grape_match2:
                        print(f"\nFOUND MATCH! File: {fname} in {s_dir}")
                        print(f"Quality Score: {q_score:.4f}% | Class: {pred_class} | Confidence: {confidence:.4f}%")
                        
                        # Print all trace info
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
