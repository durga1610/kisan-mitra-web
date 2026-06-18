import os
import sys
import json
import torch
import torch.nn as nn
from PIL import Image

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from disease_transforms import DISEASE_TRANSFORM

DATASET_DIR = "dataset"
CROP_MODEL_PATH = "models/crop_model.pt"
DISEASE_MODEL_PATH = "models/disease_model.pt"
CLASSES_JSON_PATH = "models/classes.json"

def build_efficientnet(num_classes):
    model = models.efficientnet_b0()
    in_features = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(in_features, num_classes)
    return model

from torchvision import models

def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Load classes
    with open(CLASSES_JSON_PATH, "r") as f:
        classes = json.load(f)
        
    crops = sorted(list(set(c.split("___")[0] for c in classes)))
    disease_to_crop_idx = [crops.index(c.split("___")[0]) for c in classes]
    crop_to_disease_indices = {i: [] for i in range(len(crops))}
    for d_idx, c_idx in enumerate(disease_to_crop_idx):
        crop_to_disease_indices[c_idx].append(d_idx)
        
    # Initialize Models
    crop_model = build_efficientnet(len(crops))
    disease_model = build_efficientnet(len(classes))
    
    crop_model.load_state_dict(torch.load(CROP_MODEL_PATH, map_location=device, weights_only=True))
    disease_model.load_state_dict(torch.load(DISEASE_MODEL_PATH, map_location=device, weights_only=True))
    
    crop_model = crop_model.to(device).eval()
    disease_model = disease_model.to(device).eval()
    
    # Targets to test
    target_crops = ["Grape", "Cotton", "Rice", "Potato", "Tomato"]
    test_dir = os.path.join(DATASET_DIR, "test")
    
    print("\n=== Testing Real Images (Two-Stage Prediction) ===")
    
    for tc in target_crops:
        # Find a subfolder in test/ that belongs to this crop
        matching_dirs = [d for d in os.listdir(test_dir) if d.startswith(tc) and os.path.isdir(os.path.join(test_dir, d))]
        if not matching_dirs:
            print(f"Could not find test directory for crop: {tc}")
            continue
            
        selected_dir = matching_dirs[0] # Pick the first disease folder
        img_dir = os.path.join(test_dir, selected_dir)
        img_names = [f for f in os.listdir(img_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        if not img_names:
            print(f"No images in {img_dir}")
            continue
            
        selected_img = img_names[0]
        img_path = os.path.join(img_dir, selected_img)
        
        # Load and transform image
        img = Image.open(img_path).convert("RGB")
        tensor_img = DISEASE_TRANSFORM(img).unsqueeze(0).to(device)
        
        # Run inference
        with torch.no_grad():
            # Stage 1: Crop
            crop_outputs = crop_model(tensor_img)
            crop_probs = torch.softmax(crop_outputs, dim=1)[0]
            pred_c_idx = torch.argmax(crop_probs).item()
            predicted_crop = crops[pred_c_idx] # Dummy/first class of that crop
            
            # Stage 2: Disease
            disease_outputs = disease_model(tensor_img)
            disease_probs = torch.softmax(disease_outputs, dim=1)[0]
            
            # Mask
            valid_indices = crop_to_disease_indices.get(pred_c_idx, [])
            mask = torch.zeros_like(disease_probs, dtype=torch.bool)
            mask[valid_indices] = True
            
            masked_probs = disease_probs.clone()
            masked_probs[~mask] = 0.0
            
            probs_sum = masked_probs.sum()
            if probs_sum > 0:
                masked_probs = masked_probs / probs_sum
                
            pred_d_idx = torch.argmax(masked_probs).item()
            pred_d_name = classes[pred_d_idx]
            confidence = masked_probs[pred_d_idx].item()
            
        print(f"\nCrop: {tc}")
        print(f"  Top Prediction: {pred_d_name}")
        print(f"  Confidence: {confidence * 100:.2f}%")
        print(f"  Ground Truth: {selected_dir}")

if __name__ == "__main__":
    main()
