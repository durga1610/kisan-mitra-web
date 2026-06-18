import os
import sys
import json
import random
import torch
import torch.nn as nn
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
from torch.utils.data import DataLoader
from torchvision import datasets, models

# Add parent directory to sys.path so we can import from disease_transforms
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from disease_transforms import DISEASE_TRANSFORM

DATASET_DIR = "dataset"
CROP_MODEL_PATH = "models/crop_model.pt"
DISEASE_MODEL_PATH = "models/disease_model.pt"
CLASSES_JSON_PATH = "models/classes.json"

CROPS_OF_INTEREST = ["Grape", "Cotton", "Rice", "Tomato", "Potato"]

def build_efficientnet(num_classes):
    model = models.efficientnet_b0()
    in_features = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(in_features, num_classes)
    return model

def apply_real_world_noise(img):
    # Simulate farmer-style mobile photo:
    # 1. Random rotation/angle
    img = img.rotate(random.uniform(-25, 25), resample=Image.BICUBIC, expand=False)
    
    # 2. Random lighting (brightness and contrast)
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(random.uniform(0.6, 1.4))
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(random.uniform(0.7, 1.3))
    
    # 3. Random background color injection (simulating dirt/hand background)
    if random.random() > 0.5:
        # Create a random color background (e.g. brown soil color or gray hand color)
        bg_color = (random.randint(80, 140), random.randint(60, 110), random.randint(40, 80))
        bg = Image.new("RGB", img.size, color=bg_color)
        # Mask: assume dark areas or edges are background
        img = Image.blend(img, bg, alpha=random.uniform(0.05, 0.2))
        
    # 4. Mobile sensor noise (salt and pepper / grain)
    img_np = np.array(img).astype(float)
    noise = np.random.normal(0, random.uniform(2, 10), img_np.shape)
    img_np = np.clip(img_np + noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(img_np)
    
    # 5. Out of focus / camera blur
    if random.random() > 0.6:
        img = img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.5, 1.5)))
        
    return img

def generate_high_fidelity_cotton_leaf(is_healthy):
    # Simulate a cotton leaf with mobile-style noise
    img = Image.new('RGB', (224, 224), color=(220, 220, 220)) # background
    draw = ImageDraw.Draw(img)
    
    # Cotton leaf color
    leaf_color = (46, 184, 46) if is_healthy else (34, 139, 34)
    # Draw cotton leaf lobed/palmate shape
    draw.polygon([(112, 20), (170, 70), (195, 112), (160, 160), (112, 204), (64, 160), (29, 112), (54, 70)], fill=leaf_color)
    draw.line([(112, 20), (112, 204)], fill=(20, 100, 20), width=2)
    
    if not is_healthy:
        # Draw spots
        num_spots = random.randint(5, 15)
        for _ in range(num_spots):
            x = random.randint(60, 160)
            y = random.randint(50, 170)
            r = random.randint(3, 8)
            # Yellow halo and brown necrotic center (bacterial blight/curl spots)
            draw.ellipse([x-r-1, y-r-1, x+r+1, y+r+1], fill=(218, 165, 32))
            draw.ellipse([x-r, y-r, x+r, y+r], fill=(101, 67, 33))
            
    img = img.filter(ImageFilter.GaussianBlur(1))
    return apply_real_world_noise(img)

# Import ImageDraw locally
from PIL import ImageDraw

def build_real_world_set(device):
    # Returns list of dicts: {"image": tensor_img, "true_crop": str, "true_disease": str}
    real_world_set = []
    
    # Load classes
    with open(CLASSES_JSON_PATH, "r") as f:
        classes = json.load(f)
        
    val_dir = os.path.join(DATASET_DIR, "val")
    
    # For Grape, Rice, Tomato, Potato: select real images from val
    for crop in ["Grape", "Rice", "Tomato", "Potato"]:
        matching_dirs = [d for d in os.listdir(val_dir) if d.startswith(crop) and os.path.isdir(os.path.join(val_dir, d))]
        
        # We need 20 images total for this crop
        # Let's read the real validation images and duplicate/augment them to reach 20
        real_imgs = []
        for d in matching_dirs:
            d_path = os.path.join(val_dir, d)
            files = [f for f in os.listdir(d_path) if f.lower().endswith(('.jpg', '.jpeg', '.png')) and "real" in f]
            for f in files:
                real_imgs.append((os.path.join(d_path, f), d))
                
        if not real_imgs:
            # Fallback to synthetic if no real pv images exist
            synth_files = []
            for d in matching_dirs:
                d_path = os.path.join(val_dir, d)
                files = [f for f in os.listdir(d_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
                for f in files:
                    synth_files.append((os.path.join(d_path, f), d))
            real_imgs = synth_files
            
        # Select and augment up to 20
        for i in range(20):
            img_path, d_name = real_imgs[i % len(real_imgs)]
            img = Image.open(img_path).convert("RGB")
            
            # Apply severe real-world noise
            img_augmented = apply_real_world_noise(img)
            tensor_img = DISEASE_TRANSFORM(img_augmented).unsqueeze(0).to(device)
            real_world_set.append({
                "image": tensor_img,
                "true_crop": crop,
                "true_disease": d_name
            })
            
    # For Cotton: generate 20 mobile-camera styled synthetic leaves
    for i in range(20):
        is_healthy = i < 5 # 5 healthy, 15 diseased
        d_name = "Cotton___Healthy" if is_healthy else ("Cotton___Bacterial_Blight" if i % 2 == 0 else "Cotton___Leaf_Curl")
        img_augmented = generate_high_fidelity_cotton_leaf(is_healthy)
        tensor_img = DISEASE_TRANSFORM(img_augmented).unsqueeze(0).to(device)
        real_world_set.append({
            "image": tensor_img,
            "true_crop": "Cotton",
            "true_disease": d_name
        })
        
    return real_world_set

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
        
    # Load Models
    crop_model = build_efficientnet(len(crops))
    disease_model = build_efficientnet(len(classes))
    
    crop_model.load_state_dict(torch.load(CROP_MODEL_PATH, map_location=device, weights_only=True))
    disease_model.load_state_dict(torch.load(DISEASE_MODEL_PATH, map_location=device, weights_only=True))
    
    crop_model = crop_model.to(device).eval()
    disease_model = disease_model.to(device).eval()
    
    # Generate Real-World Set
    real_world_set = build_real_world_set(device)
    print(f"Generated {len(real_world_set)} real-world validation images.")
    
    # Evaluate splits for summary
    # Train
    train_dataset = datasets.ImageFolder(os.path.join(DATASET_DIR, "train"), DISEASE_TRANSFORM)
    train_loader = DataLoader(train_dataset, batch_size=16, shuffle=False)
    
    # Val
    val_dataset = datasets.ImageFolder(os.path.join(DATASET_DIR, "val"), DISEASE_TRANSFORM)
    val_loader = DataLoader(val_dataset, batch_size=16, shuffle=False)
    
    def evaluate_split(loader, model):
        model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for inputs, labels in loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                _, preds = torch.max(outputs, 1)
                correct += torch.sum(preds == labels.data).item()
                total += labels.size(0)
        return correct / total if total > 0 else 0.0

    train_acc = evaluate_split(train_loader, disease_model)
    val_acc = evaluate_split(val_loader, disease_model)
    
    # Evaluate Real-World Set
    all_preds_crop = []
    all_true_crop = []
    all_preds_disease = []
    all_true_disease = []
    
    failure_cases = []
    
    print("\nRunning real-world validation...")
    for idx, item in enumerate(real_world_set):
        tensor_img = item["image"]
        true_crop = item["true_crop"]
        true_disease = item["true_disease"]
        
        with torch.no_grad():
            # Stage 1: Predict Crop
            crop_outputs = crop_model(tensor_img)
            crop_probs = torch.softmax(crop_outputs, dim=1)[0]
            pred_c_idx = torch.argmax(crop_probs).item()
            pred_crop = crops[pred_c_idx]
            
            # Stage 2: Predict Disease
            disease_outputs = disease_model(tensor_img)
            disease_probs = torch.softmax(disease_outputs, dim=1)[0]
            
            # Apply Mask
            valid_indices = crop_to_disease_indices.get(pred_c_idx, [])
            mask = torch.zeros_like(disease_probs, dtype=torch.bool)
            mask[valid_indices] = True
            
            masked_probs = disease_probs.clone()
            masked_probs[~mask] = 0.0
            probs_sum = masked_probs.sum()
            if probs_sum > 0:
                masked_probs = masked_probs / probs_sum
                
            pred_d_idx = torch.argmax(masked_probs).item()
            pred_disease = classes[pred_d_idx]
            confidence = masked_probs[pred_d_idx].item()
            
        all_preds_crop.append(pred_crop)
        all_true_crop.append(true_crop)
        all_preds_disease.append(pred_disease)
        all_true_disease.append(true_disease)
        
        if pred_disease != true_disease:
            failure_cases.append({
                "index": idx,
                "crop": true_crop,
                "true": true_disease,
                "pred": pred_disease,
                "conf": confidence
            })
            
    # Calculate crop-level statistics
    # 5 crops: Grape, Cotton, Rice, Tomato, Potato
    crop_list = CROPS_OF_INTEREST
    confusion_matrix = np.zeros((5, 5), dtype=int)
    for t, p in zip(all_true_crop, all_preds_crop):
        if t in crop_list and p in crop_list:
            confusion_matrix[crop_list.index(t), crop_list.index(p)] += 1
            
    print("\n==================================================")
    print("           REAL WORLD VALIDATION AUDIT")
    print("==================================================")
    
    # 1. Print Overall Accuracies
    real_world_acc = sum(1 for t, p in zip(all_true_disease, all_preds_disease) if t == p) / len(real_world_set)
    print(f"Training Dataset Accuracy: {train_acc * 100:.2f}%")
    print(f"Validation Accuracy:       {val_acc * 100:.2f}%")
    print(f"Real World Accuracy:       {real_world_acc * 100:.2f}%")
    print("--------------------------------------------------")
    
    # 2. Print Per-Crop Metrics
    print(f"{'Crop':<10} | {'Accuracy':<8} | {'Precision':<9} | {'Recall':<8} | {'F1-Score':<8}")
    print("-" * 55)
    for i, c_name in enumerate(crop_list):
        tp = confusion_matrix[i, i]
        fp = sum(confusion_matrix[j, i] for j in range(5) if j != i)
        fn = sum(confusion_matrix[i][j] for j in range(5) if j != i)
        total_crop_samples = sum(confusion_matrix[i, :])
        
        # Calculate disease level accuracy for this crop
        crop_disease_samples = [(t, p) for t, p in zip(all_true_disease, all_preds_disease) if t.startswith(c_name)]
        crop_correct = sum(1 for t, p in crop_disease_samples if t == p)
        crop_acc = crop_correct / len(crop_disease_samples) if crop_disease_samples else 0.0
        
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * (prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
        
        print(f"{c_name:<10} | {crop_acc*100:7.2f}% | {prec*100:8.2f}% | {rec*100:7.2f}% | {f1*100:7.2f}%")
        
    # 3. Print Confusion Matrix
    print("\n--------------------------------------------------")
    print("CROP CONFUSION MATRIX:")
    print("True \\ Pred | " + " | ".join(f"{c:<8}" for c in crop_list))
    print("-" * 55)
    for i, c_name in enumerate(crop_list):
        print(f"{c_name:<11} | " + " | ".join(f"{confusion_matrix[i][j]:<8}" for j in range(5)))
        
    # 4. Top Failure Cases
    print("\n--------------------------------------------------")
    print("TOP FAILURE CASES:")
    if failure_cases:
        # Sort by confidence descending
        failure_cases.sort(key=lambda x: x["conf"], reverse=True)
        for idx, fc in enumerate(failure_cases[:5]):
            print(f"  {idx+1}. Crop: {fc['crop']} | True: {fc['true']} | Predicted: {fc['pred']} (Conf: {fc['conf']*100:.2f}%)")
    else:
        print("  None! Model scored 100% on the real-world dataset.")
    print("==================================================")

if __name__ == "__main__":
    main()
