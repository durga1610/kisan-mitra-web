import os
import sys
import json
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from torchvision import datasets, transforms, models
from PIL import Image

# Configurations
WORKSPACE_DIR = r"c:\Users\durga\kisan_mitra"
BACKEND_DIR = os.path.join(WORKSPACE_DIR, "backend")
DATASET_DIR = os.path.join(WORKSPACE_DIR, "dataset")
MODEL_PATH = os.path.join(BACKEND_DIR, "models", "plant_disease_resnet.pt")
CLASSES_PATH = os.path.join(BACKEND_DIR, "models", "classes.json")

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
        try:
            img = Image.open(path).convert("RGB")
        except Exception as e:
            # Fallback to white image if loading fails
            img = Image.new("RGB", (128, 128), (255, 255, 255))
        if self.transform:
            img = self.transform(img)
        return img, target

def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # Load classes
    with open(CLASSES_PATH, "r") as f:
        classes = json.load(f)
    num_classes = len(classes)

    # Initialize model
    model = models.resnet18()
    in_features = model.fc.in_features
    model.fc = nn.Linear(in_features, num_classes)
    model.load_state_dict(torch.load(MODEL_PATH, map_location=device, weights_only=True))
    model = model.to(device)
    model.eval()

    # Load test dataset using custom SafeImageDataset
    test_dir = os.path.join(DATASET_DIR, "test")
    if not os.path.exists(test_dir):
        print(f"Error: Test folder not found at {test_dir}")
        sys.exit(1)

    test_dataset = SafeImageDataset(test_dir, classes, DISEASE_TRANSFORM)
    print(f"Found {len(test_dataset)} files in the test dataset.")
    if len(test_dataset) == 0:
        print("Warning: Test dataset is completely empty! Evaluating on val dataset instead...")
        test_dir = os.path.join(DATASET_DIR, "val")
        test_dataset = SafeImageDataset(test_dir, classes, DISEASE_TRANSFORM)
        print(f"Found {len(test_dataset)} files in the validation dataset.")

    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False, num_workers=0)

    # Run predictions
    all_preds = []
    all_targets = []
    with torch.no_grad():
        for inputs, targets in test_loader:
            inputs = inputs.to(device)
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            all_preds.extend(preds.cpu().tolist())
            all_targets.extend(targets.tolist())

    # Build confusion matrix
    conf_matrix = [[0] * num_classes for _ in range(num_classes)]
    for t, p in zip(all_targets, all_preds):
        conf_matrix[t][p] += 1

    # Calculate metrics per class
    metrics = {}
    for i in range(num_classes):
        tp = conf_matrix[i][i]
        fp = sum(conf_matrix[j][i] for j in range(num_classes) if j != i)
        fn = sum(conf_matrix[i][j] for j in range(num_classes) if j != i)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        metrics[classes[i]] = {
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "support": tp + fn
        }

    # 1 & 2. Print Cotton, Rice, Tomato, Maize (Corn), and Wheat metrics
    print("\n=======================================================")
    print("      PER-CLASS PERFORMANCE FOR REQUESTED CROPS")
    print("=======================================================")
    requested_crops = ["Cotton", "Rice", "Tomato", "Corn"] # Note: Wheat not in dataset, Corn = Maize
    
    for req in requested_crops:
        crop_title = "Maize (Corn)" if req == "Corn" else req
        print(f"\n--- {crop_title} ---")
        matching_classes = [c for c in classes if c.startswith(req)]
        if not matching_classes:
            print(f"No classes found starting with '{req}'")
            continue
        for cls in matching_classes:
            m = metrics[cls]
            print(f"  {cls:<35} | Prec: {m['precision']*100:6.2f}% | Rec: {m['recall']*100:6.2f}% | F1: {m['f1_score']*100:6.2f}% | Support: {m['support']}")
    
    print("\n--- Wheat ---")
    print("  Wheat is NOT present in the 45-class plant disease dataset (it is only supported in the Crop Recommendation model).")

    # 3. Identify top 10 most confused class pairs (exclude true == pred)
    confusions = []
    for i in range(num_classes):
        for j in range(num_classes):
            if i != j and conf_matrix[i][j] > 0:
                confusions.append((classes[i], classes[j], conf_matrix[i][j]))
    
    # Sort confusions by count desc
    confusions.sort(key=lambda x: x[2], reverse=True)
    
    print("\n=======================================================")
    print("          TOP 10 MOST CONFUSED CLASS PAIRS")
    print("=======================================================")
    for idx, (t_cls, p_cls, count) in enumerate(confusions[:10]):
        print(f"  {idx+1:2d}. True: {t_cls:<30} -> Predicted: {p_cls:<30} | Count: {count}")

    # 4. Check whether Cotton images are being misclassified as Rice diseases
    cotton_to_rice = []
    for i in range(num_classes):
        for j in range(num_classes):
            if i != j and classes[i].startswith("Cotton") and classes[j].startswith("Rice"):
                if conf_matrix[i][j] > 0:
                    cotton_to_rice.append((classes[i], classes[j], conf_matrix[i][j]))
                    
    print("\n=======================================================")
    print("   COTTON MISCLASSIFICATIONS AS RICE DISEASES")
    print("=======================================================")
    if not cotton_to_rice:
        print("  None! No Cotton images were predicted as Rice diseases.")
    else:
        for t_cls, p_cls, count in cotton_to_rice:
            print(f"  True: {t_cls:<30} -> Predicted: {p_cls:<30} | Count: {count}")

    # 5. Generate a class distribution report for the training dataset
    train_dir = os.path.join(DATASET_DIR, "train")
    train_counts = {}
    for cls in classes:
        cls_dir = os.path.join(train_dir, cls)
        if os.path.exists(cls_dir):
            train_counts[cls] = len([f for f in os.listdir(cls_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        else:
            train_counts[cls] = 0
            
    print("\n=======================================================")
    print("         TRAINING DATASET CLASS DISTRIBUTION")
    print("=======================================================")
    sorted_train = sorted(train_counts.items(), key=lambda x: x[1], reverse=True)
    for cls, count in sorted_train:
        print(f"  {cls:<35} : {count} images")

if __name__ == "__main__":
    main()
