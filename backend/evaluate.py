import os
import sys
import json
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models

# Configuration
DATASET_DIR = "dataset"
MODEL_SAVE_PATH = "models/disease_model.pt"
CLASS_MAP_PATH = "models/classes.json"

# Transforms
data_transforms = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

def build_model(num_classes):
    model = models.resnet18()
    in_features = model.fc.in_features
    model.fc = nn.Linear(in_features, num_classes)
    return model

def main():
    if not os.path.exists(MODEL_SAVE_PATH) or not os.path.exists(CLASS_MAP_PATH):
        print(f"Error: Trained model weights ('{MODEL_SAVE_PATH}') or class index mapping ('{CLASS_MAP_PATH}') not found.")
        sys.exit(1)

    test_dir = os.path.join(DATASET_DIR, "test")
    if not os.path.exists(test_dir):
        print(f"Error: Test dataset directory '{test_dir}' not found.")
        sys.exit(1)

    # Load classes
    with open(CLASS_MAP_PATH, "r") as f:
        class_names = json.load(f)

    # Load dataset
    test_dataset = datasets.ImageFolder(test_dir, data_transforms)
    test_loader = DataLoader(test_dataset, batch_size=16, shuffle=False, num_workers=0)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Evaluating on device: {device}")

    # Initialize and load model
    model = build_model(len(class_names))
    try:
        model.load_state_dict(torch.load(MODEL_SAVE_PATH, map_location=device))
    except Exception as e:
        print(f"Error loading state dict: {e}")
        sys.exit(1)

    model = model.to(device)
    model.eval()

    all_preds = []
    all_labels = []

    print("Running inference on test dataset...")
    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs = inputs.to(device)
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            
            all_preds.extend(preds.cpu().tolist())
            all_labels.extend(labels.tolist())

    # Calculate metrics manually
    num_classes = len(class_names)
    confusion_matrix = [[0] * num_classes for _ in range(num_classes)]
    
    for true_idx, pred_idx in zip(all_labels, all_preds):
        confusion_matrix[true_idx][pred_idx] += 1

    # Overall metrics
    total = len(all_labels)
    correct = sum(1 for t, p in zip(all_labels, all_preds) if t == p)
    accuracy = correct / total if total > 0 else 0.0

    # Calculate macro Precision, Recall, F1
    precisions = []
    recalls = []
    f1s = []

    for i in range(num_classes):
        tp = confusion_matrix[i][i]
        fp = sum(confusion_matrix[j][i] for j in range(num_classes) if j != i)
        fn = sum(confusion_matrix[i][j] for j in range(num_classes) if j != i)

        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * (prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0

        precisions.append(prec)
        recalls.append(rec)
        f1s.append(f1)

    macro_precision = sum(precisions) / num_classes
    macro_recall = sum(recalls) / num_classes
    macro_f1 = sum(f1s) / num_classes

    # Print Report
    report_lines = []
    report_lines.append("=" * 60)
    report_lines.append("           MODEL EVALUATION REPORT")
    report_lines.append("=" * 60)
    report_lines.append(f"Test Accuracy: {accuracy * 100:.2f}%")
    report_lines.append(f"Macro Precision: {macro_precision * 100:.2f}%")
    report_lines.append(f"Macro Recall: {macro_recall * 100:.2f}%")
    report_lines.append(f"Macro F1 Score: {macro_f1 * 100:.2f}%")
    report_lines.append("=" * 60)

    # Print Confusion Matrix snippet (for space)
    report_lines.append("\nConfusion Matrix (Top 5 Classes):")
    limit = min(5, num_classes)
    header = "True \\ Pred | " + " | ".join(class_names[i][:15] for i in range(limit))
    report_lines.append(header)
    report_lines.append("-" * len(header))
    for i in range(limit):
        row_str = f"{class_names[i][:11]:<11} | " + " | ".join(f"{confusion_matrix[i][j]:<4}" for j in range(limit))
        report_lines.append(row_str)
    report_lines.append("=" * 60)

    # Complete Confusion Matrix
    report_lines.append("\nCOMPLETE CONFUSION MATRIX (All 45 Classes):")
    full_header = "True \\ Pred | " + " | ".join(class_names[i] for i in range(num_classes))
    report_lines.append(full_header)
    report_lines.append("-" * len(full_header))
    for i in range(num_classes):
        row_str = f"{class_names[i]:<30} | " + " | ".join(str(confusion_matrix[i][j]) for j in range(num_classes))
        report_lines.append(row_str)
    report_lines.append("=" * 60)

    report_text = "\n".join(report_lines)
    print(report_text)

    # Save to file
    report_file_path = "models/evaluation_report.txt"
    with open(report_file_path, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"\nDetailed evaluation report saved to: {report_file_path}")

if __name__ == "__main__":
    main()
