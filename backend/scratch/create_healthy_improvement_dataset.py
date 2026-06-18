import os
import sys
import json
import shutil
import torch
import torch.nn as nn
from PIL import Image
from torchvision import models

# Paths configuration
WORKSPACE_DIR = r"c:\Users\durga\kisan_mitra"
BACKEND_DIR = os.path.join(WORKSPACE_DIR, "backend")
DATASET_DIR = os.path.join(WORKSPACE_DIR, "dataset")
SCRATCH_DIR = os.path.join(BACKEND_DIR, "scratch")
VAL_SET_DIR = os.path.join(SCRATCH_DIR, "field_validation_set")
CLASSES_JSON_PATH = os.path.join(BACKEND_DIR, "models", "classes.json")
MODEL_PATH = os.path.join(BACKEND_DIR, "models", "plant_disease_resnet.pt")

# Target directories for mined dataset
IMPROVEMENT_DIR = os.path.join(WORKSPACE_DIR, "dataset_healthy_improvement")
HARD_NEGATIVES_DIR = os.path.join(IMPROVEMENT_DIR, "hard_negatives")
CORRECT_HEALTHY_DIR = os.path.join(IMPROVEMENT_DIR, "correct_healthy")

# Import transform
sys.path.append(BACKEND_DIR)
from disease_transforms import DISEASE_TRANSFORM

def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Running Hard Negative Mining on device: {device}...")

    # Load 20 classes
    if not os.path.exists(CLASSES_JSON_PATH):
        print(f"Error: classes.json not found at {CLASSES_JSON_PATH}")
        sys.exit(1)
    with open(CLASSES_JSON_PATH, "r") as f:
        classes = json.load(f)
    print(f"Loaded {len(classes)} classes.")

    # Load model
    if not os.path.exists(MODEL_PATH):
        print(f"Error: model weight file not found at {MODEL_PATH}")
        sys.exit(1)
    
    model = models.resnet18()
    model.fc = nn.Linear(model.fc.in_features, len(classes))
    model.load_state_dict(torch.load(MODEL_PATH, map_location=device, weights_only=True))
    model = model.to(device)
    model.eval()
    print("Model loaded successfully.")

    # Setup improvement directories
    if os.path.exists(IMPROVEMENT_DIR):
        print(f"Cleaning existing directory: {IMPROVEMENT_DIR}")
        shutil.rmtree(IMPROVEMENT_DIR)
    os.makedirs(HARD_NEGATIVES_DIR, exist_ok=True)
    os.makedirs(CORRECT_HEALTHY_DIR, exist_ok=True)

    # Collect healthy images from train, val, and field validation sets
    healthy_candidates = []

    # 1. Scanned train set
    train_healthy_dir = os.path.join(DATASET_DIR, "train", "Plant_Healthy")
    if os.path.exists(train_healthy_dir):
        for f in os.listdir(train_healthy_dir):
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                healthy_candidates.append({
                    "path": os.path.join(train_healthy_dir, f),
                    "split": "train",
                    "crop": f.split("_")[0] if "_" in f else "unknown",
                    "filename": f
                })

    # 2. Scanned val set
    val_healthy_dir = os.path.join(DATASET_DIR, "val", "Plant_Healthy")
    if os.path.exists(val_healthy_dir):
        for f in os.listdir(val_healthy_dir):
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                healthy_candidates.append({
                    "path": os.path.join(val_healthy_dir, f),
                    "split": "val",
                    "crop": f.split("_")[0] if "_" in f else "unknown",
                    "filename": f
                })

    # 3. Scanned field validation set
    if os.path.exists(VAL_SET_DIR):
        for crop_folder in os.listdir(VAL_SET_DIR):
            crop_path = os.path.join(VAL_SET_DIR, crop_folder)
            if not os.path.isdir(crop_path):
                continue
            for class_folder in os.listdir(crop_path):
                if class_folder.endswith("___Healthy"):
                    class_path = os.path.join(crop_path, class_folder)
                    if not os.path.isdir(class_path):
                        continue
                    for f in os.listdir(class_path):
                        if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                            healthy_candidates.append({
                                "path": os.path.join(class_path, f),
                                "split": "field_validation",
                                "crop": crop_folder,
                                "filename": f
                            })

    print(f"Found {len(healthy_candidates)} healthy leaf candidate images to analyze.")

    total_count = 0
    hard_negatives_count = 0
    correct_count = 0

    crop_stats = {}
    disease_confusions = {}

    with torch.no_grad():
        for candidate in healthy_candidates:
            path = candidate["path"]
            split = candidate["split"]
            crop = candidate["crop"]
            filename = candidate["filename"]

            try:
                # Load and preprocess image
                pil_img = Image.open(path).convert("RGB")
                tensor_img = DISEASE_TRANSFORM(pil_img).unsqueeze(0).to(device)

                # Inference
                out = model(tensor_img)
                pred_idx = torch.argmax(out, 1).item()
                pred_class = classes[pred_idx]

                # Update stats
                total_count += 1
                if crop not in crop_stats:
                    crop_stats[crop] = {"total": 0, "false_positives": 0, "confusions": {}}
                crop_stats[crop]["total"] += 1

                is_fp = (pred_class != "Plant_Healthy")

                if is_fp:
                    hard_negatives_count += 1
                    crop_stats[crop]["false_positives"] += 1
                    
                    # Log confusion statistics
                    crop_stats[crop]["confusions"][pred_class] = crop_stats[crop]["confusions"].get(pred_class, 0) + 1
                    disease_confusions[pred_class] = disease_confusions.get(pred_class, 0) + 1

                    # Copy to hard negatives folder
                    new_filename = f"{split}_{crop}_pred_{pred_class}_{filename}"
                    shutil.copy2(path, os.path.join(HARD_NEGATIVES_DIR, new_filename))
                else:
                    correct_count += 1
                    # Copy to correct folder
                    new_filename = f"{split}_{crop}_correct_{filename}"
                    shutil.copy2(path, os.path.join(CORRECT_HEALTHY_DIR, new_filename))

            except Exception as e:
                print(f"Error processing {path}: {e}")

    fpr = (hard_negatives_count / total_count * 100.0) if total_count > 0 else 0.0

    # Compile final summary dictionary
    summary = {
        "dataset_summary": {
            "total_healthy_scanned": total_count,
            "correct_healthy_predictions": correct_count,
            "false_positive_disease_detections": hard_negatives_count,
            "false_positive_rate_percent": round(fpr, 2)
        },
        "crop_wise_stats": crop_stats,
        "disease_confusion_totals": dict(sorted(disease_confusions.items(), key=lambda x: x[1], reverse=True))
    }

    # Save summary report as JSON
    summary_path = os.path.join(IMPROVEMENT_DIR, "mining_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)

    print("\n" + "="*80)
    print("           HEALTHY LEAF HARD NEGATIVE MINING REPORT")
    print("="*80)
    print(f"Total Healthy Images Evaluated   : {total_count}")
    print(f"Correct Healthy Classifications  : {correct_count} ({correct_count/total_count*100.0 if total_count > 0 else 0.0:.2f}%)")
    print(f"False Positive Disease Detections: {hard_negatives_count} ({fpr:.2f}%)")
    print("-" * 80)
    print("Crop Category Performance:")
    for crp, stats in crop_stats.items():
        crp_fpr = (stats["false_positives"] / stats["total"] * 100.0) if stats["total"] > 0 else 0.0
        print(f"  * {crp:<12} | Total: {stats['total']:<4} | False Positives: {stats['false_positives']:<4} | FPR: {crp_fpr:.2f}%")
        if stats["confusions"]:
            print(f"    Confusions: {dict(sorted(stats['confusions'].items(), key=lambda x: x[1], reverse=True))}")

    print("-" * 80)
    print(f" Mined Dataset Saved: {IMPROVEMENT_DIR}")
    print(f" Hard Negatives Mined: {hard_negatives_count} images stored in 'hard_negatives/'")
    print(f" Report Saved to: {summary_path}")
    print("="*80)

if __name__ == "__main__":
    main()
