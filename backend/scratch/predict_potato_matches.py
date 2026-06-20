import os
import sys
import torch
import numpy as np
from PIL import Image

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import main
from disease_transforms import DISEASE_TRANSFORM as inference_transforms

def check_predictions():
    main.init_disease_model()
    
    folder = r"c:\Users\durga\kisan_mitra\dataset\test\Potato___Late_Blight"
    print(f"Scanning all files in {folder}...")
    
    for fname in os.listdir(folder):
        if not fname.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            continue
            
        fpath = os.path.join(folder, fname)
        try:
            image = Image.open(fpath)
            quality_ok, msg, q_score = main.check_image_quality(image)
            tensor_img = inference_transforms(image).unsqueeze(0)
            
            with torch.no_grad():
                # Replicate the exact two-stage prediction from main.py
                if main.CROP_MODEL is not None:
                    # Stage 1: Predict crop
                    crop_outputs = main.CROP_MODEL(tensor_img)
                    crop_probs = torch.softmax(crop_outputs, dim=1)[0]
                    pred_c_idx = torch.argmax(crop_probs).item()
                    
                    # Stage 2: Predict disease
                    disease_outputs = main.DISEASE_MODEL(tensor_img)
                    disease_probs = torch.softmax(disease_outputs, dim=1)[0]
                    
                    # Apply crop-specific masking
                    valid_indices = main.CROP_TO_DISEASE_INDICES.get(pred_c_idx, [])
                    mask = torch.zeros_like(disease_probs, dtype=torch.bool)
                    mask[valid_indices] = True
                    
                    # Apply mask (set invalid classes to 0)
                    masked_probs = disease_probs.clone()
                    masked_probs[~mask] = 0.0
                    
                    # Re-normalize if sum > 0
                    probs_sum = masked_probs.sum()
                    if probs_sum > 0:
                        masked_probs = masked_probs / probs_sum
                    
                    top_prob, top_idx = torch.max(masked_probs, dim=0)
                    pred_class = main.CLASSES[top_idx.item()]
                    confidence = top_prob.item() * 100
                else:
                    outputs = main.DISEASE_MODEL(tensor_img)
                    probs = torch.softmax(outputs, dim=1)[0]
                    top_prob, top_idx = torch.max(probs, dim=0)
                    pred_class = main.CLASSES[top_idx.item()]
                    confidence = top_prob.item() * 100
                
                # Check potato match: confidence ~ 42.18, quality ~ 93.62
                # Let's check with slightly wider tolerances in case of small CPU floating point differences
                if abs(q_score - 93.62) < 0.2 and abs(confidence - 42.18) < 0.2:
                    print(f"\n[FOUND MATCH] File: {fname}")
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
                    
                    print(f"Dimensions: {image.width}x{image.height}")
                    print(f"Blur Score: {variance:.4f}")
                    print(f"Brightness: {avg_brightness:.4f}")
                    print(f"Leaf Coverage: {leaf_coverage:.4f}%")
                    print("--------------------------------------------------")
                    
        except Exception as e:
            pass

if __name__ == "__main__":
    check_predictions()
