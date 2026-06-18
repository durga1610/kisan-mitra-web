import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models

DATASET_DIR = "dataset"
CLASS_MAP_PATH = "models/classes.json"

def get_transforms(resolution):
    if isinstance(resolution, tuple):
        return transforms.Compose([
            transforms.Resize(resolution),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
    else:
        return transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(resolution),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

def build_resnet18(num_classes):
    model = models.resnet18()
    in_features = model.fc.in_features
    model.fc = nn.Linear(in_features, num_classes)
    return model

def build_efficientnet(num_classes):
    model = models.efficientnet_b0()
    in_features = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(in_features, num_classes)
    return model

def evaluate(model, test_loader, device):
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            correct += torch.sum(preds == labels.data).item()
            total += labels.size(0)
    return correct / total if total > 0 else 0.0

def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    with open(CLASS_MAP_PATH, "r") as f:
        class_names = json.load(f)
        
    test_dir = os.path.join(DATASET_DIR, "test")
    
    for res in [224, (128, 128)]:
        print(f"\nEvaluating with resolution: {res}")
        test_dataset = datasets.ImageFolder(test_dir, get_transforms(res))
        test_loader = DataLoader(test_dataset, batch_size=16, shuffle=False)
        
        # Evaluate ResNet18 (plant_disease_resnet.pt)
        resnet_path = "models/plant_disease_resnet.pt"
        if os.path.exists(resnet_path):
            model_resnet = build_resnet18(len(class_names))
            model_resnet.load_state_dict(torch.load(resnet_path, map_location=device, weights_only=True))
            model_resnet = model_resnet.to(device)
            acc = evaluate(model_resnet, test_loader, device)
            print(f"  plant_disease_resnet.pt (ResNet18) Accuracy: {acc*100:.2f}%")
            
        # Evaluate EfficientNet (disease_model.pt)
        eff_path = "models/disease_model.pt"
        if os.path.exists(eff_path):
            model_eff = build_efficientnet(len(class_names))
            model_eff.load_state_dict(torch.load(eff_path, map_location=device, weights_only=True))
            model_eff = model_eff.to(device)
            acc = evaluate(model_eff, test_loader, device)
            print(f"  disease_model.pt (EfficientNet) Accuracy: {acc*100:.2f}%")

if __name__ == "__main__":
    main()
