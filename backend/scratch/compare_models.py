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
CLASSES_PATH = os.path.join(BACKEND_DIR, "models", "classes.json")
VAL_SET_DIR = os.path.join(BACKEND_DIR, "scratch", "field_validation_set")

MODEL_OLD = os.path.join(BACKEND_DIR, "models", "plant_disease_resnet.pt")
MODEL_NEW = os.path.join(BACKEND_DIR, "models", "plant_disease_resnet_new.pt")

sys.path.append(BACKEND_DIR)
from disease_transforms import DISEASE_TRANSFORM

class SafeImageDataset(Dataset):
    def __init__(self, root_dir, class_list, transform=None):
        self.root_dir = root_dir
        self.classes = class_list
        self.class_to_idx = {cls: idx for idx, cls in enumerate(class_list)}
        self.transform = transform
        self.samples = []
        
        for cls_name in self.classes:
            cls_dir = os.path.join(root_dir, cls_name)
            if not os.path.exists(cls_dir):
                continue
            for f in os.listdir(cls_dir):
                if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    self.samples.append((os.path.join(cls_dir, f), self.class_to_idx[cls_name]))
                    
    def __len__(self):
        return len(self.samples)
        
    def __getitem__(self, idx):
        path, target = self.samples[idx]
        img = Image.open(path).convert("RGB")
        if self.transform:
            img = self.transform(img)
        return img, target

def load_classes():
    with open(CLASSES_PATH, "r") as f:
        return json.load(f)

def run_evaluation(model_path, eval_images, classes, device):
    num_classes = len(classes)
    class_to_idx = {cls: idx for idx, cls in enumerate(classes)}

    # Initialize model
    model = models.resnet18()
    in_features = model.fc.in_features
    model.fc = nn.Linear(in_features, num_classes)
    model.load_state_dict(torch.load(model_path, map_location=device, weights_only=True))
    model = model.to(device)
    model.eval()

    softmax = nn.Softmax(dim=1)
    
    predictions = []
    correct_by_crop = {}
    total_by_crop = {}
    failures = []
    
    # 45x45 Confusion matrix
    conf_matrix = [[0] * num_classes for _ in range(num_classes)]

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
            
            conf_matrix[target_idx][pred_idx] += 1
            
            predictions.append({
                "path": path,
                "crop": crop,
                "gt": gt_class,
                "pred": pred_class,
                "confidence": confidence,
                "correct": is_correct
            })

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
            print(f"Error evaluating {path} on model {os.path.basename(model_path)}: {e}")

    # Calculate per-class metrics
    class_metrics = {}
    for i in range(num_classes):
        tp = conf_matrix[i][i]
        fp = sum(conf_matrix[j][i] for j in range(num_classes) if j != i)
        fn = sum(conf_matrix[i][j] for j in range(num_classes) if j != i)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        class_metrics[classes[i]] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": tp + fn
        }

    return {
        "predictions": predictions,
        "correct_by_crop": correct_by_crop,
        "total_by_crop": total_by_crop,
        "failures": failures,
        "class_metrics": class_metrics,
        "conf_matrix": conf_matrix
    }

def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    classes = load_classes()
    class_to_idx = {cls: idx for idx, cls in enumerate(classes)}

    # Collect images
    eval_images = []
    
    # 1. Gather validation set
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
                    continue
                for f in os.listdir(cls_dir):
                    if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                        eval_images.append({
                            "path": os.path.join(cls_dir, f),
                            "crop": crop,
                            "ground_truth_class": cls_name,
                            "target_idx": class_to_idx[cls_name]
                        })

    # 2. Gather Maize (Corn) test set
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

    print(f"Evaluating {len(eval_images)} validation files on both models...")

    # Run evaluations
    print("Evaluating baseline model (plant_disease_resnet.pt)...")
    res_old = run_evaluation(MODEL_OLD, eval_images, classes, device)

    print("Evaluating new model (plant_disease_resnet_new.pt)...")
    res_new = run_evaluation(MODEL_NEW, eval_images, classes, device)

    # Output comparison report
    print("\n" + "="*80)
    print("               MODEL RETRAINING COMPARISON REPORT")
    print("="*80)

    # 1. Compare Crop Accuracies
    print("\n--- Crop Accuracy Comparison ---")
    print(f"{'Crop':<12} | {'Baseline (Frozen)':<25} | {'Retrained (Unfrozen)':<25}")
    print("-"*70)
    
    crops = sorted(list(set(list(res_old["total_by_crop"].keys()) + list(res_new["total_by_crop"].keys()))))
    for crop in crops:
        tot_old = res_old["total_by_crop"].get(crop, 0)
        corr_old = res_old["correct_by_crop"].get(crop, 0)
        acc_old = (corr_old / tot_old * 100.0) if tot_old > 0 else 0.0
        
        tot_new = res_new["total_by_crop"].get(crop, 0)
        corr_new = res_new["correct_by_crop"].get(crop, 0)
        acc_new = (corr_new / tot_new * 100.0) if tot_new > 0 else 0.0
        
        lbl_old = f"{corr_old}/{tot_old} ({acc_old:.2f}%)"
        lbl_new = f"{corr_new}/{tot_new} ({acc_new:.2f}%)"
        print(f"{crop:<12} | {lbl_old:<25} | {lbl_new:<25}")

    # Total Overall
    tot_old_all = sum(res_old["total_by_crop"].values())
    corr_old_all = sum(res_old["correct_by_crop"].values())
    acc_old_all = (corr_old_all / tot_old_all * 100.0) if tot_old_all > 0 else 0.0

    tot_new_all = sum(res_new["total_by_crop"].values())
    corr_new_all = sum(res_new["correct_by_crop"].values())
    acc_new_all = (corr_new_all / tot_new_all * 100.0) if tot_new_all > 0 else 0.0

    print("-"*70)
    print(f"{'OVERALL':<12} | {corr_old_all}/{tot_old_all} ({acc_old_all:.2f}%) | {corr_new_all}/{tot_new_all} ({acc_new_all:.2f}%)")

    # 2. Rice Blast Specific Performance
    print("\n--- Rice Blast Performance ---")
    rb_old_preds = [p for p in res_old["predictions"] if p["gt"] == "Rice___Blast"]
    rb_new_preds = [p for p in res_new["predictions"] if p["gt"] == "Rice___Blast"]
    
    corr_rb_old = sum(1 for p in rb_old_preds if p["correct"])
    corr_rb_new = sum(1 for p in rb_new_preds if p["correct"])
    
    print(f"  Baseline Rice Blast Accuracy  : {corr_rb_old}/{len(rb_old_preds)} ({(corr_rb_old/len(rb_old_preds)*100.0) if rb_old_preds else 0.0:.2f}%)")
    print(f"  Retrained Rice Blast Accuracy : {corr_rb_new}/{len(rb_new_preds)} ({(corr_rb_new/len(rb_new_preds)*100.0) if rb_new_preds else 0.0:.2f}%)")

    # 3. Cotton, Rice, Tomato, Corn (Maize) Class Metrics Comparison
    print("\n--- Per-Class Performance Comparison for Requested Crops ---")
    target_crops = ["Cotton", "Rice", "Tomato", "Corn"]
    for req in target_crops:
        crop_title = "Maize (Corn)" if req == "Corn" else req
        print(f"\n{crop_title}:")
        matching_classes = [c for c in classes if c.startswith(req)]
        print(f"  {'Class Name':<35} | {'Baseline (P / R / F1)':<22} | {'Retrained (P / R / F1)':<22}")
        print("  " + "-"*85)
        for cls in matching_classes:
            m_old = res_old["class_metrics"][cls]
            m_new = res_new["class_metrics"][cls]
            
            p_old, r_old, f1_old = m_old["precision"]*100, m_old["recall"]*100, m_old["f1"]*100
            p_new, r_new, f1_new = m_new["precision"]*100, m_new["recall"]*100, m_new["f1"]*100
            
            lbl_old = f"{p_old:5.1f}%/{r_old:5.1f}%/{f1_old:5.1f}%"
            lbl_new = f"{p_new:5.1f}%/{r_new:5.1f}%/{f1_new:5.1f}%"
            print(f"  {cls:<35} | {lbl_old:<22} | {lbl_new:<22}")

    # 4. Confused pairs comparison
    print("\n--- Top Confused Disease Pairs comparison ---")
    def get_top_confusions(res_obj, limit=5):
        confs = {}
        for f in res_obj["failures"]:
            pair = (f["gt"], f["pred"])
            confs[pair] = confs.get(pair, 0) + 1
        sorted_confs = sorted(confs.items(), key=lambda x: x[1], reverse=True)
        return sorted_confs[:limit]

    top_confs_old = get_top_confusions(res_old)
    top_confs_new = get_top_confusions(res_new)
    
    print("  Baseline Model Top Confusions:")
    for pair, count in top_confs_old:
        print(f"    - True: {pair[0]:<30} -> Predicted: {pair[1]:<30} | Errors: {count}")
    print("\n  Retrained Model Top Confusions:")
    for pair, count in top_confs_new:
        print(f"    - True: {pair[0]:<30} -> Predicted: {pair[1]:<30} | Errors: {count}")

    # 5. Recommendation check
    print("\n" + "="*80)
    print("                       RECOMMENDATION DECISION")
    print("="*80)
    improvement = acc_new_all - acc_old_all
    print(f"  Overall field accuracy shift: {acc_old_all:.2f}% -> {acc_new_all:.2f}% ({improvement:+.2f}%)")
    print(f"  Rice Blast accuracy shift   : {(corr_rb_old/len(rb_old_preds)*100.0) if rb_old_preds else 0:.2f}% -> {(corr_rb_new/len(rb_new_preds)*100.0) if rb_new_preds else 0:.2f}%")
    
    if improvement > 0:
        print("\n  RECOMMENDATION: [REPLACE] The retrained model shows clear improvements on overall accuracy.")
        print("  Run this command to promote the retrained weights to production:")
        print("  Copy-Item -Path backend/models/plant_disease_resnet_new.pt -Destination backend/models/plant_disease_resnet.pt -Force")
    else:
        print("\n  RECOMMENDATION: [KEEP BASELINE] The retrained model did not exceed baseline accuracy. Retain baseline and rollback.")

if __name__ == "__main__":
    main()
