import os
import sys
import json
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
import matplotlib.pyplot as plt
import numpy as np

# Configurations
DATASET_DIR = "dataset"
CROP_MODEL_PATH = "models/crop_model.pt"
DISEASE_MODEL_PATH = "models/disease_model.pt"
CLASSES_JSON_PATH = "models/classes.json"
REPORT_SAVE_PATH = "models/new_evaluation_report.txt"
CONFUSION_MATRIX_PATH = "models/new_confusion_matrix.png"

def log(msg):
    print(msg)
    sys.stdout.flush()

# Load classes
if not os.path.exists(CLASSES_JSON_PATH):
    log(f"Error: {CLASSES_JSON_PATH} not found.")
    sys.exit(1)

with open(CLASSES_JSON_PATH, "r") as f:
    CLASSES = json.load(f)

# Determine crops
CROPS = sorted(list(set(c.split("___")[0] for c in CLASSES)))
disease_to_crop_idx = [CROPS.index(c.split("___")[0]) for c in CLASSES]

# Transforms
data_transform = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

def load_models(device):
    # Initialize EfficientNet-B0 models
    try:
        crop_model = models.efficientnet_b0()
        crop_in = crop_model.classifier[1].in_features
        crop_model.classifier[1] = nn.Linear(crop_in, len(CROPS))
    except Exception:
        crop_model = models.resnet50()
        crop_in = crop_model.fc.in_features
        crop_model.fc = nn.Linear(crop_in, len(CROPS))

    try:
        disease_model = models.efficientnet_b0()
        disease_in = disease_model.classifier[1].in_features
        disease_model.classifier[1] = nn.Linear(disease_in, len(CLASSES))
    except Exception:
        disease_model = models.resnet50()
        disease_in = disease_model.fc.in_features
        disease_model.fc = nn.Linear(disease_in, len(CLASSES))

    if not os.path.exists(CROP_MODEL_PATH) or not os.path.exists(DISEASE_MODEL_PATH):
        log("Error: Model weights not found. Train first.")
        sys.exit(1)

    crop_model.load_state_dict(torch.load(CROP_MODEL_PATH, map_location=device))
    disease_model.load_state_dict(torch.load(DISEASE_MODEL_PATH, map_location=device))
    
    crop_model = crop_model.to(device)
    disease_model = disease_model.to(device)
    
    crop_model.eval()
    disease_model.eval()
    
    return crop_model, disease_model

def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    log(f"Evaluating two-stage model on: {device}")

    # Load test dataset
    test_dir = os.path.join(DATASET_DIR, "test")
    if not os.path.exists(test_dir):
        log(f"Error: Test split not found at {test_dir}")
        sys.exit(1)

    test_dataset = datasets.ImageFolder(test_dir, data_transform)
    test_loader = DataLoader(test_dataset, batch_size=16, shuffle=False, num_workers=0)

    crop_model, disease_model = load_models(device)

    all_true_labels = []
    all_pred_labels = []
    all_pred_top3 = []

    # Map each crop index to the list of disease indices belonging to it
    crop_to_disease_indices = {i: [] for i in range(len(CROPS))}
    for d_idx, c_idx in enumerate(disease_to_crop_idx):
        crop_to_disease_indices[c_idx].append(d_idx)

    log("Running two-stage predictions on test dataset...")
    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs = inputs.to(device)
            
            # Predict crop (Stage 1)
            crop_outputs = crop_model(inputs)
            crop_probs = torch.softmax(crop_outputs, dim=1)
            pred_crops = torch.argmax(crop_probs, dim=1).cpu().tolist()

            # Predict raw diseases (Stage 2)
            disease_outputs = disease_model(inputs)
            disease_probs = torch.softmax(disease_outputs, dim=1)

            # Apply two-stage masking/filtering logic
            for i in range(inputs.size(0)):
                pred_c_idx = pred_crops[i]
                probs = disease_probs[i].clone()
                
                # Zero out all diseases not belonging to the predicted crop
                valid_indices = crop_to_disease_indices[pred_c_idx]
                mask = torch.zeros_like(probs, dtype=torch.bool)
                mask[valid_indices] = True
                
                # Apply mask (set invalid classes to 0)
                probs[~mask] = 0.0
                
                # Re-normalize if sum > 0
                probs_sum = probs.sum()
                if probs_sum > 0:
                    probs = probs / probs_sum
                
                # Get predicted class (Top-1)
                pred_d_idx = torch.argmax(probs).item()
                
                # Get Top-3 predicted classes
                _, top3_indices = torch.topk(probs, k=min(3, len(CLASSES)))
                pred_top3 = top3_indices.cpu().tolist()

                all_true_labels.append(labels[i].item())
                all_pred_labels.append(pred_d_idx)
                all_pred_top3.append(pred_top3)

    # Calculate Top-1 and Top-3 accuracy
    total = len(all_true_labels)
    correct_top1 = sum(1 for t, p in zip(all_true_labels, all_pred_labels) if t == p)
    correct_top3 = sum(1 for t, p3 in zip(all_true_labels, all_pred_top3) if t in p3)

    top1_acc = correct_top1 / total if total > 0 else 0.0
    top3_acc = correct_top3 / total if total > 0 else 0.0

    # Calculate confusion matrix and metrics
    num_classes = len(CLASSES)
    confusion = np.zeros((num_classes, num_classes), dtype=int)
    for t, p in zip(all_true_labels, all_pred_labels):
        confusion[t, p] += 1

    # Detailed metrics per class
    report_lines = []
    report_lines.append("=" * 70)
    report_lines.append("        TWO-STAGE RECOVERED MODEL EVALUATION REPORT")
    report_lines.append("=" * 70)
    report_lines.append(f"Overall Top-1 Accuracy: {top1_acc * 100:.2f}%")
    report_lines.append(f"Overall Top-3 Accuracy: {top3_acc * 100:.2f}%")
    report_lines.append("=" * 70)
    report_lines.append(f"{'Class Name':<45} | Precision | Recall    | F1-Score  | Support")
    report_lines.append("-" * 70)

    precisions = []
    recalls = []
    f1s = []
    supports = []

    for i in range(num_classes):
        tp = confusion[i, i]
        fp = sum(confusion[j, i] for j in range(num_classes) if j != i)
        fn = sum(confusion[i, j] for j in range(num_classes) if j != i)
        support = sum(confusion[i, :])

        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * (prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0

        precisions.append(prec)
        recalls.append(rec)
        f1s.append(f1)
        supports.append(support)

        report_lines.append(f"{CLASSES[i]:<45} | {prec*100:8.2f}% | {rec*100:8.2f}% | {f1*100:8.2f}% | {support:<7}")

    macro_precision = sum(precisions) / num_classes
    macro_recall = sum(recalls) / num_classes
    macro_f1 = sum(f1s) / num_classes

    report_lines.append("-" * 70)
    report_lines.append(f"{'Macro Average':<45} | {macro_precision*100:8.2f}% | {macro_recall*100:8.2f}% | {macro_f1*100:8.2f}% | {sum(supports):<7}")
    report_lines.append("=" * 70)

    # Check for grape vs potato cross classification
    grape_indices = [idx for idx, name in enumerate(CLASSES) if name.startswith("Grape")]
    potato_indices = [idx for idx, name in enumerate(CLASSES) if name.startswith("Potato")]
    
    cross_confusions = 0
    for g_idx in grape_indices:
        for p_idx in potato_indices:
            cross_confusions += confusion[g_idx, p_idx]
            cross_confusions += confusion[p_idx, g_idx]

    report_lines.append(f"Grape <-> Potato Cross-Classifications: {cross_confusions}")
    report_lines.append("=" * 70)

    report_text = "\n".join(report_lines)
    log(report_text)

    # Save evaluation report to file
    with open(REPORT_SAVE_PATH, "w", encoding="utf-8") as f:
        f.write(report_text)
    log(f"Saved evaluation report to {REPORT_SAVE_PATH}")

    # Plot and save confusion matrix
    plt.figure(figsize=(20, 20))
    plt.imshow(confusion, interpolation='nearest', cmap=plt.cm.Blues)
    plt.title('Two-Stage Inference Confusion Matrix')
    plt.colorbar()
    tick_marks = np.arange(num_classes)
    plt.xticks(tick_marks, CLASSES, rotation=90)
    plt.yticks(tick_marks, CLASSES)
    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.savefig(CONFUSION_MATRIX_PATH)
    plt.close()
    log(f"Saved confusion matrix plot to {CONFUSION_MATRIX_PATH}")

if __name__ == "__main__":
    main()
