import os
import sys
import json
import argparse
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models

from disease_transforms import DISEASE_TRANSFORM

# Configuration
DATASET_DIR = "dataset"
MODEL_SAVE_PATH = "models/disease_model.pt"
CLASS_MAP_PATH = "models/classes.json"

# Transforms
data_transforms = {
    'train': DISEASE_TRANSFORM,
    'val': DISEASE_TRANSFORM
}

def build_model(model_name, num_classes):
    print(f"Building {model_name} model for {num_classes} classes...")
    if model_name == "efficientnet":
        try:
            # Modern torchvision
            weights = models.EfficientNet_B0_Weights.DEFAULT
            model = models.efficientnet_b0(weights=weights)
        except Exception:
            # Legacy torchvision
            model = models.efficientnet_b0(pretrained=True)
            
        in_features = model.classifier[1].in_features
        model.classifier[1] = nn.Linear(in_features, num_classes)
    elif model_name == "resnet50":
        try:
            weights = models.ResNet50_Weights.DEFAULT
            model = models.resnet50(weights=weights)
        except Exception:
            model = models.resnet50(pretrained=True)
            
        in_features = model.fc.in_features
        model.fc = nn.Linear(in_features, num_classes)
    else:
        raise ValueError(f"Unknown model name: {model_name}")
        
    return model

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=10, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=16, help="Batch size")
    parser.add_argument("--lr", type=float, default=0.001, help="Learning rate")
    parser.add_argument("--model", type=str, default="efficientnet", choices=["efficientnet", "resnet50"], help="Model architecture")
    parser.add_argument("--patience", type=int, default=3, help="Early stopping patience")
    args = parser.parse_args()

    os.makedirs("models", exist_ok=True)

    # Load datasets
    train_dir = os.path.join(DATASET_DIR, "train")
    val_dir = os.path.join(DATASET_DIR, "val")

    if not os.path.exists(train_dir) or not os.path.exists(val_dir):
        print(f"Error: Dataset directories not prepared under '{DATASET_DIR}'. Run prepare_dataset.py first.")
        sys.exit(1)

    train_dataset = datasets.ImageFolder(train_dir, data_transforms['train'])
    val_dataset = datasets.ImageFolder(val_dir, data_transforms['val'])

    class_names = train_dataset.classes
    with open(CLASS_MAP_PATH, "w") as f:
        json.dump(class_names, f)
    print(f"Saved class index mapping with {len(class_names)} classes to {CLASS_MAP_PATH}")

    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False, num_workers=0)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # Build model
    try:
        model = build_model(args.model, len(class_names))
    except Exception as e:
        print(f"Failed to build primary model {args.model}: {e}. Falling back to ResNet50...")
        model = build_model("resnet50", len(class_names))
        args.model = "resnet50"

    model = model.to(device)

    # Class balancing weights calculation
    class_counts = [0] * len(class_names)
    for _, label in train_dataset.samples:
        class_counts[label] += 1
        
    total_samples = sum(class_counts)
    weights = [total_samples / (len(class_names) * c) if c > 0 else 1.0 for c in class_counts]
    class_weights = torch.tensor(weights, dtype=torch.float).to(device)
    
    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = optim.AdamW(model.parameters(), lr=args.lr, weight_decay=0.01)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=1)

    # Mixed precision scaler
    use_amp = device.type == "cuda"
    scaler = torch.cuda.amp.GradScaler(enabled=use_amp)

    best_loss = float('inf')
    epochs_no_improve = 0

    print("Starting training loop...")
    for epoch in range(args.epochs):
        print(f"\nEpoch {epoch+1}/{args.epochs}")
        print("-" * 10)

        # Train Phase
        model.train()
        train_loss = 0.0
        train_corrects = 0

        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()

            with torch.cuda.amp.autocast(enabled=use_amp):
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                _, preds = torch.max(outputs, 1)

            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()

            train_loss += loss.item() * inputs.size(0)
            train_corrects += torch.sum(preds == labels.data)

        epoch_train_loss = train_loss / len(train_dataset)
        epoch_train_acc = train_corrects.double() / len(train_dataset)
        print(f"Train Loss: {epoch_train_loss:.4f} Acc: {epoch_train_acc:.4f}")

        # Validation Phase
        model.eval()
        val_loss = 0.0
        val_corrects = 0

        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)

                with torch.cuda.amp.autocast(enabled=use_amp):
                    outputs = model(inputs)
                    loss = criterion(outputs, labels)
                    _, preds = torch.max(outputs, 1)

                val_loss += loss.item() * inputs.size(0)
                val_corrects += torch.sum(preds == labels.data)

        epoch_val_loss = val_loss / len(val_dataset)
        epoch_val_acc = val_corrects.double() / len(val_dataset)
        print(f"Val Loss: {epoch_val_loss:.4f} Acc: {epoch_val_acc:.4f}")

        scheduler.step(epoch_val_loss)

        # Save best model
        if epoch_val_loss < best_loss:
            best_loss = epoch_val_loss
            epochs_no_improve = 0
            torch.save(model.state_dict(), MODEL_SAVE_PATH)
            print(f"Saved best model weights to {MODEL_SAVE_PATH}")
        else:
            epochs_no_improve += 1
            if epochs_no_improve >= args.patience:
                print(f"Early stopping triggered after {epoch+1} epochs.")
                break

    print("Training finished successfully!")

if __name__ == "__main__":
    main()
