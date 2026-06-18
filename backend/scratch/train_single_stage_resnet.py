import os
import sys
import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models

# Configurations
WORKSPACE_DIR = r"c:\Users\durga\kisan_mitra"
BACKEND_DIR = os.path.join(WORKSPACE_DIR, "backend")
DATASET_DIR = os.path.join(WORKSPACE_DIR, "dataset")
MODEL_SAVE_PATH = os.path.join(BACKEND_DIR, "models", "plant_disease_resnet.pt")
CLASSES_JSON_PATH = os.path.join(BACKEND_DIR, "models", "classes.json")

def log(msg):
    print(msg)
    sys.stdout.flush()

# Add backend directory to Python path
sys.path.append(BACKEND_DIR)

# Focal Loss for class balancing
class FocalLoss(nn.Module):
    def __init__(self, alpha=None, gamma=2.0):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma

    def forward(self, inputs, targets):
        ce_loss = nn.functional.cross_entropy(inputs, targets, reduction='none', weight=self.alpha)
        pt = torch.exp(-ce_loss)
        focal_loss = ((1 - pt) ** self.gamma) * ce_loss
        return focal_loss.mean()

from disease_transforms import DISEASE_TRANSFORM

# Augmented training transforms for robustness against real backgrounds
data_transforms = {
    'train': transforms.Compose([
        transforms.Resize((128, 128)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
    'val': DISEASE_TRANSFORM
}

def train_resnet():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    log(f"Training ResNet18 model on device: {device}...")

    train_dir = os.path.join(DATASET_DIR, "train")
    val_dir = os.path.join(DATASET_DIR, "val")

    if not os.path.exists(train_dir) or not os.path.exists(val_dir):
        log(f"Error: Dataset directories not prepared under '{DATASET_DIR}'")
        sys.exit(1)

    train_dataset = datasets.ImageFolder(train_dir, data_transforms['train'])
    val_dataset = datasets.ImageFolder(val_dir, data_transforms['val'])

    disease_classes = train_dataset.classes
    with open(CLASSES_JSON_PATH, "w") as f:
        json.dump(disease_classes, f)
    log(f"Saved {len(disease_classes)} classes to {CLASSES_JSON_PATH}")

    batch_size = 32
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=0)

    dataset_sizes = {
        'train': len(train_dataset),
        'val': len(val_dataset)
    }

    # Initialize Pre-trained ResNet18
    try:
        weights = models.ResNet18_Weights.DEFAULT
        model = models.resnet18(weights=weights)
    except Exception:
        model = models.resnet18(pretrained=True)

    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, len(disease_classes))
    model = model.to(device)

    # Compute class weights
    num_classes = len(disease_classes)
    class_counts = [0] * num_classes
    for label_idx in train_dataset.targets:
        class_counts[label_idx] += 1
    total_samples = sum(class_counts)
    weights = [total_samples / (num_classes * c) if c > 0 else 1.0 for c in class_counts]
    weights_tensor = torch.tensor(weights, dtype=torch.float).to(device)

    criterion = FocalLoss(alpha=weights_tensor, gamma=2.0)
    
    # Freeze all layers except layer4 and fc for fast CPU training
    for name, param in model.named_parameters():
        if "layer4" in name or "fc" in name:
            param.requires_grad = True
        else:
            param.requires_grad = False

    num_epochs = 8
    optimizer = optim.AdamW(filter(lambda p: p.requires_grad, model.parameters()), lr=1e-3, weight_decay=1e-2)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=num_epochs)

    best_acc = 0.0
    best_model_weights = model.state_dict()

    for epoch in range(num_epochs):
        log(f"Epoch {epoch+1}/{num_epochs}")
        log("-" * 20)

        for phase in ['train', 'val']:
            if phase == 'train':
                model.train()
                dataloader = train_loader
            else:
                model.eval()
                dataloader = val_loader

            running_loss = 0.0
            running_corrects = 0

            for inputs, targets in dataloader:
                inputs = inputs.to(device)
                targets = targets.to(device)

                optimizer.zero_grad()

                with torch.set_grad_enabled(phase == 'train'):
                    outputs = model(inputs)
                    _, preds = torch.max(outputs, 1)
                    loss = criterion(outputs, targets)

                    if phase == 'train':
                        loss.backward()
                        optimizer.step()

                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == targets.data)

            if phase == 'train':
                scheduler.step()

            epoch_loss = running_loss / dataset_sizes[phase]
            epoch_acc = running_corrects.double() / dataset_sizes[phase]

            log(f"{phase.capitalize()} Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f}")

            if phase == 'val' and epoch_acc > best_acc:
                best_acc = epoch_acc
                best_model_weights = model.state_dict()

    log(f"Best validation accuracy: {best_acc:.4f}")
    model.load_state_dict(best_model_weights)
    
    # Save model weights
    os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)
    torch.save(model.state_dict(), MODEL_SAVE_PATH)
    log(f"Saved ResNet18 model weights to {MODEL_SAVE_PATH}")

    # Remove the two-stage model checkpoints to force API to fall back to this ResNet18
    crop_path = os.path.join(BACKEND_DIR, "models", "crop_model.pt")
    disease_path = os.path.join(BACKEND_DIR, "models", "disease_model.pt")
    if os.path.exists(crop_path):
        os.remove(crop_path)
        log("Removed crop_model.pt to enable fallback to plant_disease_resnet.pt")
    if os.path.exists(disease_path):
        os.remove(disease_path)
        log("Removed disease_model.pt to enable fallback to plant_disease_resnet.pt")

if __name__ == "__main__":
    train_resnet()
