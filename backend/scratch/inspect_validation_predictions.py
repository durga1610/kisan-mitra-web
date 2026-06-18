import os
import sys
import json
import torch
import torch.nn as nn
from PIL import Image
from torchvision import models

# Configure paths
WORKSPACE_DIR = r"c:\Users\durga\kisan_mitra"
BACKEND_DIR = os.path.join(WORKSPACE_DIR, "backend")
VAL_SET_DIR = os.path.join(BACKEND_DIR, "scratch", "field_validation_set")

sys.path.append(BACKEND_DIR)
import main
from disease_transforms import DISEASE_TRANSFORM

def main_inspect():
    print("Initializing models...")
    main.init_disease_model()
    
    crop_model = main.CROP_MODEL
    disease_model = main.DISEASE_MODEL
    classes = main.CLASSES
    crops_list = main.CROPS
    
    print(f"Loaded {len(crops_list)} crops: {crops_list}")
    print(f"Loaded {len(classes)} classes.")
    
    # Trace validation set directories
    if not os.path.exists(VAL_SET_DIR):
        print(f"Validation set directory {VAL_SET_DIR} does not exist.")
        return
        
    # Load fallback ResNet18 model
    resnet_path = os.path.join(WORKSPACE_DIR, "backend", "models", "plant_disease_resnet.pt")
    resnet_model = None
    if os.path.exists(resnet_path):
        try:
            resnet_model = models.resnet18()
            num_ftrs = resnet_model.fc.in_features
            resnet_model.fc = nn.Linear(num_ftrs, len(classes))
            resnet_model.load_state_dict(torch.load(resnet_path, map_location="cpu", weights_only=True))
            resnet_model.eval()
            print("Loaded ResNet18 model successfully.")
        except Exception as e:
            print(f"Failed to load ResNet18 model: {e}")
            
    correct_crop = 0
    correct_disease_single = 0
    correct_disease_twostage = 0
    correct_resnet = 0
    total = 0
    
    crop_errors = []
    disease_errors = []
    resnet_errors = []
    
    # Map each crop index to the list of disease indices belonging to it
    crop_to_disease_indices = {i: [] for i in range(len(crops_list))}
    for d_idx, c in enumerate(classes):
        c_name = c.split("___")[0]
        if c_name in crops_list:
            crop_to_disease_indices[crops_list.index(c_name)].append(d_idx)

    for crop_folder in os.listdir(VAL_SET_DIR):
        crop_path = os.path.join(VAL_SET_DIR, crop_folder)
        if not os.path.isdir(crop_path):
            continue
            
        for disease_folder in os.listdir(crop_path):
            disease_path = os.path.join(crop_path, disease_folder)
            if not os.path.isdir(disease_path):
                continue
                
            for img_file in os.listdir(disease_path):
                if not img_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    continue
                    
                img_path = os.path.join(disease_path, img_file)
                total += 1
                
                try:
                    img = Image.open(img_path).convert("RGB")
                    tensor_img = DISEASE_TRANSFORM(img).unsqueeze(0)
                    
                    with torch.no_grad():
                        # 1. Predict Crop
                        pred_crop = None
                        if crop_model is not None:
                            crop_out = crop_model(tensor_img)
                            crop_probs = torch.softmax(crop_out, dim=1)[0]
                            pred_c_idx = torch.argmax(crop_probs).item()
                            pred_crop = crops_list[pred_c_idx]
                        
                        # 2. Predict Disease (Single-Stage)
                        pred_disease_single = None
                        if disease_model is not None:
                            disease_out = disease_model(tensor_img)
                            disease_probs_raw = torch.softmax(disease_out, dim=1)[0]
                            pred_d_idx_single = torch.argmax(disease_probs_raw).item()
                            pred_disease_single = classes[pred_d_idx_single]
                        
                        # 3. Predict Disease (Two-Stage)
                        pred_disease_twostage = None
                        if crop_model is not None and disease_model is not None:
                            valid_indices = crop_to_disease_indices[pred_c_idx]
                            mask = torch.zeros_like(disease_probs_raw, dtype=torch.bool)
                            mask[valid_indices] = True
                            masked_probs = disease_probs_raw.clone()
                            masked_probs[~mask] = 0.0
                            
                            probs_sum = masked_probs.sum()
                            if probs_sum > 0:
                                masked_probs = masked_probs / probs_sum
                            pred_d_idx_twostage = torch.argmax(masked_probs).item()
                            pred_disease_twostage = classes[pred_d_idx_twostage]
                        
                        # 4. Predict ResNet18
                        pred_disease_resnet = None
                        if resnet_model is not None:
                            resnet_out = resnet_model(tensor_img)
                            resnet_probs = torch.softmax(resnet_out, dim=1)[0]
                            pred_d_idx_resnet = torch.argmax(resnet_probs).item()
                            pred_disease_resnet = classes[pred_d_idx_resnet]
                        
                    if crop_model is not None:
                        is_crop_correct = (crop_folder.lower() == pred_crop.lower())
                        if is_crop_correct:
                            correct_crop += 1
                        else:
                            crop_errors.append((img_file, crop_folder, pred_crop))
                        
                    if disease_model is not None:
                        is_disease_single_correct = (disease_folder.lower() == pred_disease_single.lower())
                        if is_disease_single_correct:
                            correct_disease_single += 1
                        else:
                            disease_errors.append((img_file, disease_folder, pred_disease_single))
                        
                    if crop_model is not None and disease_model is not None:
                        is_disease_twostage_correct = (disease_folder.lower() == pred_disease_twostage.lower())
                        if is_disease_twostage_correct:
                            correct_disease_twostage += 1
                        
                    if resnet_model is not None:
                        is_resnet_correct = (disease_folder.lower() == pred_disease_resnet.lower())
                        if is_resnet_correct:
                            correct_resnet += 1
                        else:
                            resnet_errors.append((img_file, disease_folder, pred_disease_resnet))
                        
                except Exception as e:
                    print(f"Error processing {img_file}: {e}")
                    
    print("\n--- DIAGNOSTICS REPORT ---")
    print(f"Total images evaluated: {total}")
    print(f"Crop Model Accuracy (Stage 1): {correct_crop}/{total} ({correct_crop/total*100:.2f}%)")
    print(f"Disease Model Accuracy (Single-Stage): {correct_disease_single}/{total} ({correct_disease_single/total*100:.2f}%)")
    print(f"Disease Model Accuracy (Two-Stage): {correct_disease_twostage}/{total} ({correct_disease_twostage/total*100:.2f}%)")
    if resnet_model is not None:
        print(f"ResNet18 Model Accuracy (Single-Stage): {correct_resnet}/{total} ({correct_resnet/total*100:.2f}%)")

    
    print("\nSample Crop Errors (File, True, Pred):")
    for err in crop_errors[:10]:
        print(f"  {err[0]}: True={err[1]}, Pred={err[2]}")
        
    print("\nSample Disease Single-Stage Errors (File, True, Pred):")
    for err in disease_errors[:10]:
        print(f"  {err[0]}: True={err[1]}, Pred={err[2]}")

if __name__ == "__main__":
    main_inspect()
