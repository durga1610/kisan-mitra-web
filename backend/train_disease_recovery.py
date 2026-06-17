import os
import sys
import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from torchvision import datasets, transforms, models

# Configurations
DATASET_DIR = "dataset"
CROP_MODEL_PATH = "models/crop_model.pt"
DISEASE_MODEL_PATH = "models/disease_model.pt"
CLASSES_JSON_PATH = "models/classes.json"

# ASCII Only printing to avoid terminal encoding errors
def log(msg):
    print(msg)
    sys.stdout.flush()

# Focal Loss implementation
class FocalLoss(nn.Module):
    def __init__(self, alpha=None, gamma=2.0):
        super().__init__()
        self.alpha = alpha  # Weight tensor
        self.gamma = gamma

    def forward(self, inputs, targets):
        ce_loss = nn.functional.cross_entropy(inputs, targets, reduction='none', weight=self.alpha)
        pt = torch.exp(-ce_loss)
        focal_loss = ((1 - pt) ** self.gamma) * ce_loss
        return focal_loss.mean()

# Data transforms without any random augmentations to preserve watermarks
data_transforms = {
    'train': transforms.Compose([
        transforms.Resize((128, 128)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
    'val': transforms.Compose([
        transforms.Resize((128, 128)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
}

# Custom Dataset Wrapper to return both crop and disease labels
class DualLabelDataset(Dataset):
    def __init__(self, base_dataset, class_to_crop_idx):
        self.base_dataset = base_dataset
        self.class_to_crop_idx = class_to_crop_idx

    def __len__(self):
        return len(self.base_dataset)

    def __getitem__(self, idx):
        img, disease_label = self.base_dataset[idx]
        crop_label = self.class_to_crop_idx[disease_label]
        return img, disease_label, crop_label

def get_efficientnet_b0(num_classes):
    try:
        # Modern torchvision
        weights = models.EfficientNet_B0_Weights.DEFAULT
        model = models.efficientnet_b0(weights=weights)
    except Exception:
        # Legacy torchvision
        model = models.efficientnet_b0(pretrained=True)
    
    in_features = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(in_features, num_classes)
    return model

def train_model(model_type, model, train_loader, val_loader, dataset_sizes, class_names, num_epochs=6, lr=1e-3):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)

    # Compute class balancing weights without loading images
    num_classes = len(class_names)
    class_counts = [0] * num_classes
    
    base_ds = train_loader.dataset.base_dataset
    if model_type == "crop":
        for label_idx in base_ds.targets:
            crop_label = train_loader.dataset.class_to_crop_idx[label_idx]
            class_counts[crop_label] += 1
    else:
        for label_idx in base_ds.targets:
            class_counts[label_idx] += 1

    total_samples = sum(class_counts)
    weights = [total_samples / (num_classes * c) if c > 0 else 1.0 for c in class_counts]
    weights_tensor = torch.tensor(weights, dtype=torch.float).to(device)

    criterion = FocalLoss(alpha=weights_tensor, gamma=2.0)
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-2)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=num_epochs)

    best_acc = 0.0
    best_model_weights = model.state_dict()

    log(f"Training {model_type} model with {num_classes} classes on device: {device}...")

    for epoch in range(num_epochs):
        log(f"Epoch {epoch+1}/{num_epochs}")
        log("-" * 20)

        # Each epoch has a training and validation phase
        for phase in ['train', 'val']:
            if phase == 'train':
                model.train()
                dataloader = train_loader
            else:
                model.eval()
                dataloader = val_loader

            running_loss = 0.0
            running_corrects = 0

            for inputs, disease_labels, crop_labels in dataloader:
                inputs = inputs.to(device)
                
                if model_type == "crop":
                    targets = crop_labels.to(device)
                else:
                    targets = disease_labels.to(device)

                optimizer.zero_grad()

                # Forward pass
                with torch.set_grad_enabled(phase == 'train'):
                    outputs = model(inputs)
                    _, preds = torch.max(outputs, 1)
                    loss = criterion(outputs, targets)

                    # Backward pass & optimize if in training phase
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

            # Deep copy the model weights if this is the best validation accuracy
            if phase == 'val' and epoch_acc > best_acc:
                best_acc = epoch_acc
                best_model_weights = model.state_dict()

    log(f"Best validation accuracy for {model_type}: {best_acc:.4f}")
    model.load_state_dict(best_model_weights)
    return model, best_acc

def main():
    os.makedirs("models", exist_ok=True)

    train_dir = os.path.join(DATASET_DIR, "train")
    val_dir = os.path.join(DATASET_DIR, "val")

    if not os.path.exists(train_dir) or not os.path.exists(val_dir):
        log(f"Error: Dataset directories not prepared under '{DATASET_DIR}'")
        sys.exit(1)

    train_disease_ds = datasets.ImageFolder(train_dir, data_transforms['train'])
    val_disease_ds = datasets.ImageFolder(val_dir, data_transforms['val'])

    disease_classes = train_disease_ds.classes
    with open(CLASSES_JSON_PATH, "w") as f:
        json.dump(disease_classes, f)
    log(f"Saved {len(disease_classes)} classes to {CLASSES_JSON_PATH}")

    crop_names = sorted(list(set(c.split("___")[0] for c in disease_classes)))
    log(f"Crops detected ({len(crop_names)}): {crop_names}")

    disease_to_crop_idx = [crop_names.index(c.split("___")[0]) for c in disease_classes]

    train_dataset = DualLabelDataset(train_disease_ds, disease_to_crop_idx)
    val_dataset = DualLabelDataset(val_disease_ds, disease_to_crop_idx)

    batch_size = 16
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=0)

    dataset_sizes = {
        'train': len(train_dataset),
        'val': len(val_dataset)
    }

    # 2. Train the Stage 1: Crop Model (16 classes) - Fully Unfrozen, lr=1e-3
    crop_model = get_efficientnet_b0(len(crop_names))
    for param in crop_model.parameters():
        param.requires_grad = True

    crop_model, val_crop_acc = train_model(
        model_type="crop",
        model=crop_model,
        train_loader=train_loader,
        val_loader=val_loader,
        dataset_sizes=dataset_sizes,
        class_names=crop_names,
        num_epochs=5,
        lr=1e-3
    )

    torch.save(crop_model.state_dict(), CROP_MODEL_PATH)
    log(f"Saved crop model weights to {CROP_MODEL_PATH}")

    # 3. Train the Stage 2: Disease Model (45 classes) - Fully Unfrozen, lr=1e-3
    disease_model = get_efficientnet_b0(len(disease_classes))
    for param in disease_model.parameters():
        param.requires_grad = True

    disease_model, val_disease_acc = train_model(
        model_type="disease",
        model=disease_model,
        train_loader=train_loader,
        val_loader=val_loader,
        dataset_sizes=dataset_sizes,
        class_names=disease_classes,
        num_epochs=6,
        lr=1e-3
    )

    torch.save(disease_model.state_dict(), DISEASE_MODEL_PATH)
    log(f"Saved disease model weights to {DISEASE_MODEL_PATH}")

    # 4. Check if validation accuracy requirements are met
    log(f"\nFinal training results:")
    log(f"Crop Model Validation Accuracy: {val_crop_acc * 100:.2f}%")
    log(f"Disease Model Validation Accuracy: {val_disease_acc * 100:.2f}%")

    if val_disease_acc >= 0.85:
        log("SUCCESS: Validation accuracy exceeds the 85% threshold gate!")
    else:
        log("WARNING: Validation accuracy is below the 85% threshold. Do not deploy yet.")

if __name__ == "__main__":
    main()
