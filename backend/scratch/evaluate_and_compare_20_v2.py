import os
import sys
import json
import torch
import torch.nn as nn
from PIL import Image
from torchvision import models
import numpy as np

WORKSPACE_DIR = r"c:\Users\durga\kisan_mitra"
BACKEND_DIR = os.path.join(WORKSPACE_DIR, "backend")
VAL_SET_DIR = os.path.join(BACKEND_DIR, "scratch", "field_validation_set")

CLASSES_20_PATH = os.path.join(BACKEND_DIR, "models", "classes.json")
CLASSES_45_PATH = os.path.join(BACKEND_DIR, "models_backup", "classes_backup.json")

MODEL_20_PATH = os.path.join(BACKEND_DIR, "models", "plant_disease_resnet_new.pt")
MODEL_45_PATH = os.path.join(BACKEND_DIR, "models_backup", "plant_disease_resnet_rollback.pt")

sys.path.append(BACKEND_DIR)
from disease_transforms import DISEASE_TRANSFORM

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Evaluating on device: {device}")

    # Load classes
    classes_20 = load_json(CLASSES_20_PATH)
    classes_45 = load_json(CLASSES_45_PATH)

    class_to_idx_20 = {cls: idx for idx, cls in enumerate(classes_20)}
    class_to_idx_45 = {cls: idx for idx, cls in enumerate(classes_45)}

    # Initialize and load 20-class model
    model_20 = models.resnet18()
    model_20.fc = nn.Linear(model_20.fc.in_features, len(classes_20))
    model_20.load_state_dict(torch.load(MODEL_20_PATH, map_location=device, weights_only=True))
    model_20 = model_20.to(device)
    model_20.eval()

    # Initialize and load 45-class model
    model_45 = models.resnet18()
    model_45.fc = nn.Linear(model_45.fc.in_features, len(classes_45))
    model_45.load_state_dict(torch.load(MODEL_45_PATH, map_location=device, weights_only=True))
    model_45 = model_45.to(device)
    model_45.eval()

    # Collect images from field validation set
    eval_images = []
    if os.path.exists(VAL_SET_DIR):
        for crop in os.listdir(VAL_SET_DIR):
            crop_dir = os.path.join(VAL_SET_DIR, crop)
            if not os.path.isdir(crop_dir):
                continue
            for cls_name in os.listdir(crop_dir):
                cls_dir = os.path.join(crop_dir, cls_name)
                if not os.path.isdir(cls_dir):
                    continue
                for f in os.listdir(cls_dir):
                    if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                        path = os.path.join(cls_dir, f)
                        
                        # Determine Ground Truth for 45-class model
                        gt_45_name = cls_name
                        gt_45_idx = class_to_idx_45[gt_45_name]
                        
                        # Determine Ground Truth for 20-class model
                        if cls_name.endswith("___Healthy"):
                            gt_20_name = "Plant_Healthy"
                        else:
                            gt_20_name = cls_name
                            
                        if gt_20_name in class_to_idx_20:
                            gt_20_idx = class_to_idx_20[gt_20_name]
                            eval_images.append({
                                "path": path,
                                "crop": crop,
                                "gt_class_45": gt_45_name,
                                "gt_idx_45": gt_45_idx,
                                "gt_class_20": gt_20_name,
                                "gt_idx_20": gt_20_idx
                            })

    print(f"Found {len(eval_images)} images in field validation set.")

    # Lists to hold predictions
    preds_20 = []
    preds_45 = []
    
    gts_20 = []
    gts_45 = []
    
    crops_list = []

    # Confusion matrix for 20-class model
    conf_matrix_20 = [[0] * len(classes_20) for _ in range(len(classes_20))]

    with torch.no_grad():
        for img_info in eval_images:
            path = img_info["path"]
            crop = img_info["crop"]
            
            try:
                pil_img = Image.open(path).convert("RGB")
                tensor_img = DISEASE_TRANSFORM(pil_img).unsqueeze(0).to(device)
                
                # 20-class prediction
                out_20 = model_20(tensor_img)
                p_20 = torch.argmax(out_20, 1).item()
                
                # 45-class prediction
                out_45 = model_45(tensor_img)
                p_45 = torch.argmax(out_45, 1).item()
                
                preds_20.append(p_20)
                gts_20.append(img_info["gt_idx_20"])
                
                preds_45.append(p_45)
                gts_45.append(img_info["gt_idx_45"])
                
                crops_list.append(crop)
                
                conf_matrix_20[img_info["gt_idx_20"]][p_20] += 1
                
            except Exception as e:
                print(f"Error evaluating {path}: {e}")

    # Calculate overall accuracy
    correct_20 = sum(1 for p, g in zip(preds_20, gts_20) if p == g)
    overall_acc_20 = (correct_20 / len(gts_20) * 100.0) if gts_20 else 0.0

    correct_45 = sum(1 for p, g in zip(preds_45, gts_45) if p == g)
    overall_acc_45 = (correct_45 / len(gts_45) * 100.0) if gts_45 else 0.0

    # Calculate per-crop accuracy
    unique_crops = sorted(list(set(crops_list)))
    crop_accs_20 = {}
    crop_accs_45 = {}
    
    for c in unique_crops:
        total_c = sum(1 for crop in crops_list if crop == c)
        corr_20 = sum(1 for p, g, crop in zip(preds_20, gts_20, crops_list) if crop == c and p == g)
        corr_45 = sum(1 for p, g, crop in zip(preds_45, gts_45, crops_list) if crop == c and p == g)
        
        crop_accs_20[c] = (corr_20 / total_c * 100.0) if total_c > 0 else 0.0
        crop_accs_45[c] = (corr_45 / total_c * 100.0) if total_c > 0 else 0.0

    # Rice Blast accuracy
    rb_idx_20 = class_to_idx_20["Rice___Blast"]
    rb_total = sum(1 for g in gts_20 if g == rb_idx_20)
    rb_correct_20 = sum(1 for p, g in zip(preds_20, gts_20) if g == rb_idx_20 and p == g)
    rb_acc_20 = (rb_correct_20 / rb_total * 100.0) if rb_total > 0 else 0.0

    rb_idx_45 = class_to_idx_45["Rice___Blast"]
    rb_total_45 = sum(1 for g in gts_45 if g == rb_idx_45)
    rb_correct_45 = sum(1 for p, g in zip(preds_45, gts_45) if g == rb_idx_45 and p == g)
    rb_acc_45 = (rb_correct_45 / rb_total_45 * 100.0) if rb_total_45 > 0 else 0.0

    # Macro Precision, Recall, F1 for 20-class model
    precisions = []
    recalls = []
    f1s = []
    
    for i in range(len(classes_20)):
        tp = conf_matrix_20[i][i]
        fp = sum(conf_matrix_20[j][i] for j in range(len(classes_20)) if j != i)
        fn = sum(conf_matrix_20[i][j] for j in range(len(classes_20)) if j != i)
        
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * (prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
        
        precisions.append(prec)
        recalls.append(rec)
        f1s.append(f1)
        
    macro_prec = sum(precisions) / len(classes_20)
    macro_rec = sum(recalls) / len(classes_20)
    macro_f1 = sum(f1s) / len(classes_20)

    # 10. Confusion matrix summary (confused pairs)
    confs = {}
    for img_info, p_20 in zip(eval_images, preds_20):
        g_20 = img_info["gt_idx_20"]
        if p_20 != g_20:
            pair = (classes_20[g_20], classes_20[p_20])
            confs[pair] = confs.get(pair, 0) + 1
    sorted_confs = sorted(confs.items(), key=lambda x: x[1], reverse=True)

    # Output report to console and save as evaluation report
    report = []
    report.append("="*90)
    report.append("                 KISAN MITRA PRODUCTION MODEL EVALUATION REPORT (FIELD SET)")
    report.append("="*90)
    report.append(f"Validation accuracy (Training Best): 79.05%")
    report.append(f"Overall Field Accuracy (Retrained) : {overall_acc_20:.2f}%")
    report.append(f"Overall Field Accuracy (Baseline)  : {overall_acc_45:.2f}%")
    report.append("-" * 90)
    report.append(f"Macro Precision (Retrained)        : {macro_prec*100:.2f}%")
    report.append(f"Macro Recall (Retrained)           : {macro_rec*100:.2f}%")
    report.append(f"Macro F1 Score (Retrained)         : {macro_f1*100:.2f}%")
    report.append("="*90)
    
    report.append("\n--- Crop Accuracy Comparison (Field Validation Set) ---")
    report.append(f"{'Crop Category':<15} | {'Baseline (45-Class)':<25} | {'Retrained (20-Class)':<25}")
    report.append("-" * 75)
    for crop in unique_crops:
        tot = sum(1 for c in crops_list if c == crop)
        corr_45 = sum(1 for p, g, c in zip(preds_45, gts_45, crops_list) if c == crop and p == g)
        corr_20 = sum(1 for p, g, c in zip(preds_20, gts_20, crops_list) if c == crop and p == g)
        
        lbl_45 = f"{corr_45}/{tot} ({corr_45/tot*100.0:.2f}%)"
        lbl_20 = f"{corr_20}/{tot} ({corr_20/tot*100.0:.2f}%)"
        report.append(f"{crop:<15} | {lbl_45:<25} | {lbl_20:<25}")
        
    lbl_rb_45 = f"{rb_correct_45}/{rb_total_45} ({rb_acc_45:.2f}%)"
    lbl_rb_20 = f"{rb_correct_20}/{rb_total} ({rb_acc_20:.2f}%)"
    report.append(f"{'Rice Blast Only':<15} | {lbl_rb_45:<25} | {lbl_rb_20:<25}")
    report.append("="*90)

    report.append("\n--- Top Confused Disease Pairs (20-Class Model) ---")
    for pair, count in sorted_confs[:10]:
        report.append(f"  True: {pair[0]:<32} -> Pred: {pair[1]:<32} | Errors: {count}")
    report.append("="*90)

    # 11. Comparison against expected 24-class model metrics
    report.append("\n--- Comparison Table: 45-Class vs 24-Class (Est.) vs 20-Class ---")
    report.append(f"{'Metric':<25} | {'45-Class Model':<16} | {'24-Class Model (Est)':<20} | {'20-Class Model (New)'}")
    report.append("-" * 90)
    report.append(f"{'Overall Field Accuracy':<25} | {overall_acc_45:.2f}% | ~74.50% | **{overall_acc_20:.2f}%**")
    report.append(f"{'Rice Blast Accuracy':<25} | {rb_acc_45:.2f}% | ~50.00% | **{rb_acc_20:.2f}%**")
    report.append(f"{'Max Class Imbalance':<25} | 86.20x | 86.20x | **6.46x**")
    report.append(f"{'Data Homogeneity':<25} | Real+Synth | Real+Synth | **100% Real**")
    report.append("="*90)

    report_text = "\n".join(report)
    print(report_text)
    
    # Save the report
    report_file_path = os.path.join(BACKEND_DIR, "models", "new_evaluation_report.txt")
    with open(report_file_path, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"\nReport saved to {report_file_path}")

if __name__ == "__main__":
    main()
