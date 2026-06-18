import os
import sys
import json
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from torchvision import datasets, transforms, models
from PIL import Image
import numpy as np

# Configurations
WORKSPACE_DIR = r"c:\Users\durga\kisan_mitra"
BACKEND_DIR = os.path.join(WORKSPACE_DIR, "backend")
DATASET_DIR = os.path.join(WORKSPACE_DIR, "dataset")
MODEL_PATH = os.path.join(BACKEND_DIR, "models", "plant_disease_resnet.pt")
CLASSES_PATH = os.path.join(BACKEND_DIR, "models", "classes.json")
VAL_SET_DIR = os.path.join(BACKEND_DIR, "scratch", "field_validation_set")

sys.path.append(BACKEND_DIR)
from disease_transforms import DISEASE_TRANSFORM

def load_classes():
    with open(CLASSES_PATH, "r") as f:
        return json.load(f)

def evaluate_production():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Audit running on device: {device}")

    classes = load_classes()
    num_classes = len(classes)
    class_to_idx = {cls: idx for idx, cls in enumerate(classes)}

    # Initialize model
    model = models.resnet18()
    in_features = model.fc.in_features
    model.fc = nn.Linear(in_features, num_classes)
    model.load_state_dict(torch.load(MODEL_PATH, map_location=device, weights_only=True))
    model = model.to(device)
    model.eval()

    # Collect images to evaluate
    eval_images = [] # list of dict: {"path", "crop", "ground_truth_class", "target_idx"}

    # 1. Gather from field_validation_set (Rice, Cotton, Tomato, Grape, Potato)
    if os.path.exists(VAL_SET_DIR):
        for crop in os.listdir(VAL_SET_DIR):
            crop_dir = os.path.join(VAL_SET_DIR, crop)
            if not os.path.isdir(crop_dir):
                continue
            for cls_name in os.listdir(crop_dir):
                cls_dir = os.path.join(crop_dir, cls_name)
                if not os.path.isdir(cls_dir):
                    continue
                if cls_name not in class_to_idx:
                    print(f"Warning: Class {cls_name} not found in classes.json, skipping...")
                    continue
                for f in os.listdir(cls_dir):
                    if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                        eval_images.append({
                            "path": os.path.join(cls_dir, f),
                            "crop": crop,
                            "ground_truth_class": cls_name,
                            "target_idx": class_to_idx[cls_name]
                        })

    # 2. Gather Maize (Corn) from test dataset split
    maize_test_dir = os.path.join(DATASET_DIR, "test")
    if os.path.exists(maize_test_dir):
        for cls_name in os.listdir(maize_test_dir):
            if cls_name.startswith("Corn___"):
                cls_dir = os.path.join(maize_test_dir, cls_name)
                if os.path.isdir(cls_dir) and cls_name in class_to_idx:
                    for f in os.listdir(cls_dir):
                        if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                            eval_images.append({
                                "path": os.path.join(cls_dir, f),
                                "crop": "Maize",
                                "ground_truth_class": cls_name,
                                "target_idx": class_to_idx[cls_name]
                            })

    print(f"Gathered {len(eval_images)} validation images for the production audit.")

    # Run predictions
    correct_by_crop = {}
    total_by_crop = {}
    failures = []
    predictions = []

    # Map output indices to softmax probabilities to get true confidence scores
    softmax = nn.Softmax(dim=1)

    for img in eval_images:
        path = img["path"]
        crop = img["crop"]
        gt_class = img["ground_truth_class"]
        target_idx = img["target_idx"]

        try:
            pil_img = Image.open(path).convert("RGB")
            tensor_img = DISEASE_TRANSFORM(pil_img).unsqueeze(0).to(device)
            
            with torch.no_grad():
                outputs = model(tensor_img)
                probs = softmax(outputs)
                conf, pred_idx_tensor = torch.max(probs, 1)
                pred_idx = pred_idx_tensor.item()
                confidence = conf.item() * 100.0
                
            pred_class = classes[pred_idx]
            is_correct = (pred_idx == target_idx)
            
            predictions.append({
                "path": path,
                "crop": crop,
                "gt": gt_class,
                "pred": pred_class,
                "confidence": confidence,
                "correct": is_correct
            })

            # Track metrics by crop
            if crop not in total_by_crop:
                total_by_crop[crop] = 0
                correct_by_crop[crop] = 0
            total_by_crop[crop] += 1
            if is_correct:
                correct_by_crop[crop] += 1
            else:
                failures.append({
                    "path": path,
                    "crop": crop,
                    "gt": gt_class,
                    "pred": pred_class,
                    "confidence": confidence
                })
        except Exception as e:
            print(f"Error evaluating {path}: {e}")

    # Generate Audit Report
    print("\n" + "="*60)
    print("           PRODUCTION READINESS AUDIT REPORT")
    print("="*60)

    # 1. Crop accuracy summary
    print("\n--- Crop Accuracy Summary ---")
    for crop in sorted(total_by_crop.keys()):
        acc = (correct_by_crop[crop] / total_by_crop[crop]) * 100.0
        print(f"  {crop:<10} : {correct_by_crop[crop]:3d}/{total_by_crop[crop]:3d} correct | Accuracy: {acc:6.2f}%")

    # 2. Confused classes count
    confusions = {}
    for f in failures:
        pair = (f["gt"], f["pred"])
        confusions[pair] = confusions.get(pair, 0) + 1

    sorted_confusions = sorted(confusions.items(), key=lambda x: x[1], reverse=True)
    print("\n--- Top Confused Disease Pairs ---")
    for pair, count in sorted_confusions[:10]:
        print(f"  True: {pair[0]:<30} -> Predicted: {pair[1]:<30} | Errors: {count}")

    # 3. Confidence score analysis
    conf_correct = [p["confidence"] for p in predictions if p["correct"]]
    conf_incorrect = [p["confidence"] for p in predictions if not p["correct"]]

    print("\n--- Confidence Scores Analysis ---")
    print(f"  Correct predictions   : Count={len(conf_correct)}, Mean Conf={np.mean(conf_correct):.2f}%, Min={np.min(conf_correct):.2f}%, Max={np.max(conf_correct):.2f}%" if conf_correct else "  No correct predictions")
    print(f"  Incorrect predictions : Count={len(conf_incorrect)}, Mean Conf={np.mean(conf_incorrect):.2f}%, Min={np.min(conf_incorrect):.2f}%, Max={np.max(conf_incorrect):.2f}%" if conf_incorrect else "  No incorrect predictions")

    # 4. Rice Blast performance analysis
    rice_preds = [p for p in predictions if p["crop"] == "Rice"]
    rice_blast_preds = [p for p in rice_preds if p["gt"] == "Rice___Blast"]
    print("\n--- Detailed Rice Blast Performance Analysis ---")
    if not rice_blast_preds:
        print("  No Rice Blast images evaluated.")
    else:
        blast_correct = sum(1 for p in rice_blast_preds if p["correct"])
        blast_total = len(rice_blast_preds)
        print(f"  Rice Blast Accuracy: {blast_correct}/{blast_total} correct ({blast_correct/blast_total*100.0:.2f}%)")
        print("  Predictions for Rice Blast images:")
        for p in rice_blast_preds:
            status = "Correct" if p["correct"] else f"Incorrect (Predicted as {p['pred']})"
            print(f"    - Image: {os.path.basename(p['path'])} | {status} | Conf: {p['confidence']:.2f}%")

if __name__ == "__main__":
    evaluate_production()
