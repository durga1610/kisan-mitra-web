import os
import sys
import json
import shutil
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models

# Configurations
WORKSPACE_DIR = r"c:\Users\durga\kisan_mitra"
BACKEND_DIR = os.path.join(WORKSPACE_DIR, "backend")
DATASET_DIR = os.path.join(WORKSPACE_DIR, "dataset")
MINED_DIR = os.path.join(WORKSPACE_DIR, "dataset_healthy_improvement", "hard_negatives")
MODEL_SAVE_PATH = os.path.join(BACKEND_DIR, "models", "plant_disease_resnet_v2.pt")
CLASSES_JSON_PATH = os.path.join(BACKEND_DIR, "models", "classes.json")
STARTING_MODEL_PATH = os.path.join(BACKEND_DIR, "models", "plant_disease_resnet.pt")

sys.path.append(BACKEND_DIR)
from disease_transforms import DISEASE_TRANSFORM

def log(msg):
    print(msg)
    sys.stdout.flush()

# Focal Loss Class
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

# Mixup Helpers
def mixup_data(x, y, alpha=0.2, device='cpu'):
    if alpha > 0:
        lam = np.random.beta(alpha, alpha)
    else:
        lam = 1
    batch_size = x.size()[0]
    index = torch.randperm(batch_size).to(device)
    mixed_x = lam * x + (1 - lam) * x[index, :]
    y_a, y_b = y, y[index]
    return mixed_x, y_a, y_b, lam

# Cutmix Helpers
def rand_bbox(size, lam):
    W = size[2]
    H = size[3]
    cut_rat = np.sqrt(1. - lam)
    cut_w = int(W * cut_rat)
    cut_h = int(H * cut_rat)
    cx = np.random.randint(W)
    cy = np.random.randint(H)
    bbx1 = np.clip(cx - cut_w // 2, 0, W)
    bby1 = np.clip(cy - cut_h // 2, 0, H)
    bbx2 = np.clip(cx + cut_w // 2, 0, W)
    bby2 = np.clip(cy + cut_h // 2, 0, H)
    return bbx1, bby1, bbx2, bby2

def cutmix_data(x, y, alpha=1.0, device='cpu'):
    if alpha > 0:
        lam = np.random.beta(alpha, alpha)
    else:
        lam = 1
    batch_size = x.size()[0]
    index = torch.randperm(batch_size).to(device)
    mixed_x = x.clone()
    y_a, y_b = y, y[index]
    bbx1, bby1, bbx2, bby2 = rand_bbox(x.size(), lam)
    mixed_x[:, :, bby1:bby2, bbx1:bbx2] = x[index, :, bby1:bby2, bbx1:bbx2]
    # Adjust lambda to match actual ratio of cut region
    lam = 1 - ((bbx2 - bbx1) * (bby2 - bby1) / (x.size()[-1] * x.size()[-2]))
    return mixed_x, y_a, y_b, lam

def mixup_criterion(criterion, pred, y_a, y_b, lam):
    return lam * criterion(pred, y_a) + (1 - lam) * criterion(pred, y_b)

def setup_mined_data():
    log("Copying mined healthy hard negatives to training splits...")
    copied_files = []
    if not os.path.exists(MINED_DIR):
        log("Warning: Mined directory not found. Proceeding with standard dataset.")
        return copied_files

    train_dest = os.path.join(DATASET_DIR, "train", "Plant_Healthy")
    val_dest = os.path.join(DATASET_DIR, "val", "Plant_Healthy")

    os.makedirs(train_dest, exist_ok=True)
    os.makedirs(val_dest, exist_ok=True)

    for f in os.listdir(MINED_DIR):
        src_path = os.path.join(MINED_DIR, f)
        if not os.path.isfile(src_path):
            continue

        if f.startswith("train_"):
            # 2x Oversampling: copy twice with different prefixes
            dst_f1 = f"mined_dup1_{f}"
            dst_f2 = f"mined_dup2_{f}"
            
            shutil.copy2(src_path, os.path.join(train_dest, dst_f1))
            shutil.copy2(src_path, os.path.join(train_dest, dst_f2))
            
            copied_files.append(os.path.join(train_dest, dst_f1))
            copied_files.append(os.path.join(train_dest, dst_f2))
            
        elif f.startswith("val_"):
            # Copy once to validation split
            dst_f = f"mined_val_{f}"
            shutil.copy2(src_path, os.path.join(val_dest, dst_f))
            copied_files.append(os.path.join(val_dest, dst_f))
            
        # Ignore field_validation_ prefix to keep evaluation sets unseen!

    log(f"Successfully copied {len(copied_files)} mined healthy leaf instances.")
    return copied_files

def cleanup_mined_data(copied_files):
    log("Cleaning up temporary mined healthy files from splits...")
    for f in copied_files:
        if os.path.exists(f):
            try:
                os.remove(f)
            except Exception as e:
                log(f"Error deleting temporary file {f}: {e}")
    log("Cleanup complete.")

def train():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    log(f"Retraining Production v2 ResNet18 model on device: {device}...")

    # Copy data first
    copied_files = setup_mined_data()

    try:
        # Transforms with Random Erasing on training
        data_transforms = {
            'train': transforms.Compose([
                transforms.Resize((128, 128)),
                transforms.RandomHorizontalFlip(),
                transforms.RandomVerticalFlip(),
                transforms.RandomRotation(15),
                transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
                transforms.RandomErasing(p=0.5, scale=(0.02, 0.2), value='random')
            ]),
            'val': DISEASE_TRANSFORM
        }

        train_dir = os.path.join(DATASET_DIR, "train")
        val_dir = os.path.join(DATASET_DIR, "val")

        train_dataset = datasets.ImageFolder(train_dir, data_transforms['train'])
        val_dataset = datasets.ImageFolder(val_dir, data_transforms['val'])

        disease_classes = train_dataset.classes
        log(f"Number of training classes detected: {len(disease_classes)}")

        batch_size = 32
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)
        val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=0)

        dataset_sizes = {
            'train': len(train_dataset),
            'val': len(val_dataset)
        }

        log(f"Dataset splits: {dataset_sizes['train']} train, {dataset_sizes['val']} val images.")

        # Load starting Production v1 ResNet18 model
        model = models.resnet18()
        model.fc = nn.Linear(model.fc.in_features, len(disease_classes))
        
        if os.path.exists(STARTING_MODEL_PATH):
            log(f"Initializing weights from Production v1 base: {STARTING_MODEL_PATH}")
            model.load_state_dict(torch.load(STARTING_MODEL_PATH, map_location=device, weights_only=True))
        else:
            log("Warning: Production v1 base weights not found, using pre-trained ImageNet baseline.")
            try:
                model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
                model.fc = nn.Linear(model.fc.in_features, len(disease_classes))
            except Exception:
                model = models.resnet18(pretrained=True)
                model.fc = nn.Linear(model.fc.in_features, len(disease_classes))

        model = model.to(device)

        # Dynamic class-weight calculations for Focal Loss
        num_classes = len(disease_classes)
        class_counts = [0] * num_classes
        for label_idx in train_dataset.targets:
            class_counts[label_idx] += 1
        total_samples = sum(class_counts)
        weights = [total_samples / (num_classes * c) if c > 0 else 1.0 for c in class_counts]
        weights_tensor = torch.tensor(weights, dtype=torch.float).to(device)

        criterion = FocalLoss(alpha=weights_tensor, gamma=2.0)

        # Ensure all parameters are unfrozen for fine-tuning
        for param in model.parameters():
            param.requires_grad = True

        # Train parameters: epochs = 20, LR = 1e-4
        num_epochs = 20
        optimizer = optim.AdamW(model.parameters(), lr=1e-4, weight_decay=1e-2)
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
                        # Apply MixUp / CutMix in training phase
                        if phase == 'train':
                            r = np.random.rand()
                            if r < 0.4:
                                # MixUp (alpha = 0.2)
                                inputs, targets_a, targets_b, lam = mixup_data(inputs, targets, alpha=0.2, device=device)
                                outputs = model(inputs)
                                _, preds = torch.max(outputs, 1)
                                loss = mixup_criterion(criterion, outputs, targets_a, targets_b, lam)
                            elif r < 0.8:
                                # CutMix (alpha = 1.0)
                                inputs, targets_a, targets_b, lam = cutmix_data(inputs, targets, alpha=1.0, device=device)
                                outputs = model(inputs)
                                _, preds = torch.max(outputs, 1)
                                loss = mixup_criterion(criterion, outputs, targets_a, targets_b, lam)
                            else:
                                # Standard forward
                                outputs = model(inputs)
                                _, preds = torch.max(outputs, 1)
                                loss = criterion(outputs, targets)
                        else:
                            # Validation forward
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

        # Save weights
        os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)
        torch.save(model.state_dict(), MODEL_SAVE_PATH)
        log(f"Saved Production v2 weights to {MODEL_SAVE_PATH}")

    finally:
        # Cleanup copied files
        cleanup_mined_data(copied_files)

if __name__ == "__main__":
    train()
