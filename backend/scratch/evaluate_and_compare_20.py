import os
import sys
import json
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
from PIL import Image
import numpy as np

WORKSPACE_DIR = r"c:\Users\durga\kisan_mitra"
BACKEND_DIR = os.path.join(WORKSPACE_DIR, "backend")
DATASET_DIR = os.path.join(WORKSPACE_DIR, "dataset")

# Classes and Models paths
CLASSES_20_PATH = os.path.join(BACKEND_DIR, "models", "classes.json")
CLASSES_45_PATH = os.path.join(BACKEND_DIR, "models_backup", "classes_backup.json")

MODEL_20_PATH = os.path.join(BACKEND_DIR, "models", "plant_disease_resnet_new.pt")
MODEL_45_PATH = os.path.join(BACKEND_DIR, "models_backup", "plant_disease_resnet_rollback.pt")

sys.path.append(BACKEND_DIR)
from disease_transforms import DISEASE_TRANSFORM

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def get_crop_from_filename(filename):
    fn = filename.lower()
    if fn.startswith("rice_"):
        return "rice"
    elif fn.startswith("tomato_"):
        return "tomato"
    elif fn.startswith("potato_"):
        return "potato"
    elif fn.startswith("cotton_"):
        return "cotton"
    elif fn.startswith("grape_"):
        return "grape"
    elif fn.startswith("corn_"):
        return "corn"
    elif fn.startswith("pepper_bell_"):
        return "pepper_bell"
    return "unknown"

def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device for evaluation: {device}")

    # Load class maps
    classes_20 = load_json(CLASSES_20_PATH)
    classes_45 = load_json(CLASSES_45_PATH)
    
    class_to_idx_20 = {cls: idx for idx, cls in enumerate(classes_20)}
    class_to_idx_45 = {cls: idx for idx, cls in enumerate(classes_45)}

    # Initialize models
    # New 20-class model (ResNet18)
    model_20 = models.resnet18()
    model_20.fc = nn.Linear(model_20.fc.in_features, len(classes_20))
    model_20.load_state_dict(torch.load(MODEL_20_PATH, map_location=device, weights_only=True))
    model_20 = model_20.to(device)
    model_20.eval()

    # Baseline 45-class model (ResNet18)
    model_45 = models.resnet18()
    model_45.fc = nn.Linear(model_45.fc.in_features, len(classes_45))
    model_45.load_state_dict(torch.load(MODEL_45_PATH, map_location=device, weights_only=True))
    model_45 = model_45.to(device)
    model_45.eval()

    # Load 20-class test dataset
    test_dir = os.path.join(DATASET_DIR, "test")
    test_dataset = datasets.ImageFolder(test_dir, transform=DISEASE_TRANSFORM, allow_empty=True)
    test_loader = DataLoader(test_dataset, batch_size=16, shuffle=False, num_workers=0)

    # We will loop over the dataset samples directly to get file paths for correct mapping
    samples = test_dataset.samples # list of (file_path, class_idx_20)

    predictions_20 = []
    predictions_45 = []
    
    gts_20 = []
    gts_45 = []

    print(f"Running evaluation on {len(samples)} test samples...")
    
    softmax = nn.Softmax(dim=1)

    for path, idx_20 in samples:
        filename = os.path.basename(path)
        class_name_20 = classes_20[idx_20]
        
        # 1. Map ground truth class for 45-class model
        if class_name_20 == "Plant_Healthy":
            crop_prefix = get_crop_from_filename(filename)
            class_name_45 = f"{crop_prefix.capitalize()}___Healthy"
            if class_name_45 not in class_to_idx_45:
                # Fallback to general healthy class or default
                class_name_45 = "Tomato___Healthy"
        else:
            class_name_45 = class_name_20
            
        idx_45 = class_to_idx_45.get(class_name_45, 0)

        # 2. Run inference
        try:
            pil_img = Image.open(path).convert("RGB")
            tensor_img = DISEASE_TRANSFORM(pil_img).unsqueeze(0).to(device)
            
            with torch.no_grad():
                # 20-class model
                out_20 = model_20(tensor_img)
                pred_idx_20 = torch.argmax(out_20, 1).item()
                predictions_20.append(pred_idx_20)
                gts_20.append(idx_20)

                # 45-class model
                out_45 = model_45(tensor_img)
                pred_idx_45 = torch.argmax(out_45, 1).item()
                predictions_45.append(pred_idx_45)
                gts_45.append(idx_45)
                
        except Exception as e:
            print(f"Error processing {path}: {e}")

    # Calculate overall accuracies
    correct_20 = sum(1 for p, g in zip(predictions_20, gts_20) if p == g)
    acc_20 = (correct_20 / len(gts_20)) * 100.0 if gts_20 else 0.0

    correct_45 = sum(1 for p, g in zip(predictions_45, gts_45) if p == g)
    acc_45 = (correct_45 / len(gts_45)) * 100.0 if gts_45 else 0.0

    # Calculate Per-Crop Accuracies
    # Crops represented in active set: Rice, Cotton, Tomato, Potato, Grape
    active_crops = ["Rice", "Cotton", "Tomato", "Potato", "Grape"]
    
    crop_stats_20 = {c: {"correct": 0, "total": 0} for c in active_crops}
    crop_stats_45 = {c: {"correct": 0, "total": 0} for c in active_crops}

    # For confusion matrix
    confusion_matrix_20 = [[0] * len(classes_20) for _ in range(len(classes_20))]

    for path, idx_20 in samples:
        filename = os.path.basename(path)
        class_name_20 = classes_20[idx_20]
        
        # Determine crop category
        crop_cat = "Unknown"
        if class_name_20 == "Plant_Healthy":
            crop_prefix = get_crop_from_filename(filename)
            crop_cat = crop_prefix.capitalize()
        else:
            crop_cat = class_name_20.split("___")[0]
            
        if crop_cat not in active_crops:
            continue

        # Map to indexes
        pos = len(gts_20) - len(samples) + samples.index((path, idx_20))
        p_20 = predictions_20[pos]
        g_20 = gts_20[pos]
        p_45 = predictions_45[pos]
        g_45 = gts_45[pos]

        # 20-class stats
        crop_stats_20[crop_cat]["total"] += 1
        if p_20 == g_20:
            crop_stats_20[crop_cat]["correct"] += 1

        # 45-class stats
        crop_stats_45[crop_cat]["total"] += 1
        if p_45 == g_45:
            crop_stats_45[crop_cat]["correct"] += 1

        confusion_matrix_20[g_20][p_20] += 1

    # Per-class metrics for 20-class model
    precisions = []
    recalls = []
    f1s = []
    class_report_lines = []

    for i in range(len(classes_20)):
        tp = confusion_matrix_20[i][i]
        fp = sum(confusion_matrix_20[j][i] for j in range(len(classes_20)) if j != i)
        fn = sum(confusion_matrix_20[i][j] for j in range(len(classes_20)) if j != i)

        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * (prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0

        precisions.append(prec)
        recalls.append(rec)
        f1s.append(f1)

        class_report_lines.append(f"{classes_20[i]:<32} | {prec*100:6.2f}% | {rec*100:6.2f}% | {f1*100:6.2f}% | {tp+fn}")

    macro_precision = sum(precisions) / len(classes_20)
    macro_recall = sum(recalls) / len(classes_20)
    macro_f1 = sum(f1s) / len(classes_20)

    # 4. Rice Blast specific accuracy
    rb_idx_20 = class_to_idx_20["Rice___Blast"]
    rb_tp = confusion_matrix_20[rb_idx_20][rb_idx_20]
    rb_fn = sum(confusion_matrix_20[rb_idx_20][j] for j in range(len(classes_20)) if j != rb_idx_20)
    rb_total = rb_tp + rb_fn
    rb_acc_20 = (rb_tp / rb_total) * 100.0 if rb_total > 0 else 0.0

    # Baseline Rice Blast
    rb_idx_45 = class_to_idx_45["Rice___Blast"]
    rb_correct_45 = sum(1 for p, g in zip(predictions_45, gts_45) if g == rb_idx_45 and p == g)
    rb_total_45 = sum(1 for g in gts_45 if g == rb_idx_45)
    rb_acc_45 = (rb_correct_45 / rb_total_45) * 100.0 if rb_total_45 > 0 else 0.0

    # Write report
    report = []
    report.append("="*90)
    report.append("                   KISAN MITRA RETRAINED 20-CLASS EVALUATION REPORT")
    report.append("="*90)
    report.append(f"Validation Set Path          : {test_dir}")
    report.append(f"Active Taxonomy Classes      : 20")
    report.append(f"Validation Acc (Retrained)   : 79.05% (Best val acc during training)")
    report.append(f"Test Set Accuracy (Retrained): {acc_20:.2f}%")
    report.append(f"Test Set Accuracy (Baseline) : {acc_45:.2f}%")
    report.append("-" * 90)
    report.append(f"Macro Precision (Retrained)  : {macro_precision*100:.2f}%")
    report.append(f"Macro Recall (Retrained)     : {macro_recall*100:.2f}%")
    report.append(f"Macro F1 Score (Retrained)   : {macro_f1*100:.2f}%")
    report.append("="*90)
    
    report.append("\n--- Crop Accuracy Comparison (Test Set) ---")
    report.append(f"{'Crop Category':<15} | {'Baseline (45-Class)':<25} | {'Retrained (20-Class)':<25}")
    report.append("-" * 75)
    for crop in active_crops:
        tot_45 = crop_stats_45[crop]["total"]
        corr_45 = crop_stats_45[crop]["correct"]
        acc_c_45 = (corr_45 / tot_45 * 100.0) if tot_45 > 0 else 0.0
        
        tot_20 = crop_stats_20[crop]["total"]
        corr_20 = crop_stats_20[crop]["correct"]
        acc_c_20 = (corr_20 / tot_20 * 100.0) if tot_20 > 0 else 0.0
        
        label_45 = f"{corr_45}/{tot_45} ({acc_c_45:.2f}%)"
        label_20 = f"{corr_20}/{tot_20} ({acc_c_20:.2f}%)"
        report.append(f"{crop:<15} | {label_45:<25} | {label_20:<25}")
        
    report.append(f"{'Rice Blast Only':<15} | {rb_correct_45}/{rb_total_45} ({rb_acc_45:.2f}%) | {rb_tp}/{rb_total} ({rb_acc_20:.2f}%)")
    report.append("="*90)

    report.append("\n--- Detailed Per-Class Metrics (20-Class Model) ---")
    report.append(f"{'Class Name':<32} | {'Precision':<9} | {'Recall':<9} | {'F1-Score':<9} | {'Support'}")
    report.append("-" * 75)
    report.extend(class_report_lines)
    report.append("="*90)

    # Top confused pairs
    report.append("\n--- Top Confused Disease Pairs (20-Class Model) ---")
    confs = {}
    for path, idx_20 in samples:
        pos = samples.index((path, idx_20))
        p = predictions_20[pos]
        g = gts_20[pos]
        if p != g:
            pair = (classes_20[g], classes_20[p])
            confs[pair] = confs.get(pair, 0) + 1
    sorted_confs = sorted(confs.items(), key=lambda x: x[1], reverse=True)
    for pair, count in sorted_confs[:10]:
        report.append(f"  True: {pair[0]:<32} -> Pred: {pair[1]:<32} | Errors: {count}")
    report.append("="*90)

    report_text = "\n".join(report)
    print(report_text)
    
    # Save the report to backend/models/detailed_eval.txt
    report_path = os.path.join(BACKEND_DIR, "models", "detailed_eval.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"\nDetailed eval report saved to: {report_path}")

if __name__ == "__main__":
    main()
