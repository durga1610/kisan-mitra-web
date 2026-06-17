import os
import json
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader

# --- CONFIGURATION ---
DATASET_DIR = "dataset"  # Folder layout: dataset/train/rice_blast, dataset/train/tomato_early_blight, etc.
MODEL_SAVE_PATH = "models/plant_disease_resnet.pt"
CLASS_MAP_PATH = "models/classes.json"

# --- IMAGE TRANSFORMATIONS ---
data_transforms = {
    'train': transforms.Compose([
        transforms.RandomResizedCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
    'val': transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
}

def train_model(epochs=10, batch_size=32, lr=0.001):
    # Ensure save directory exists
    os.makedirs("models", exist_ok=True)
        
    if not os.path.exists(DATASET_DIR):
        print(f"Error: Dataset directory '{DATASET_DIR}' not found.")
        print("Please structure your dataset as follows:")
        print("  dataset/")
        print("    train/")
        print("      rice_blast/")
        print("      tomato_early_blight/")
        print("    val/")
        print("      rice_blast/")
        print("      tomato_early_blight/")
        return

    # Load datasets using ImageFolder
    print("Loading datasets...")
    image_datasets = {x: datasets.ImageFolder(os.path.join(DATASET_DIR, x), data_transforms[x])
                      for x in ['train', 'val']}
    dataloaders = {x: DataLoader(image_datasets[x], batch_size=batch_size, shuffle=True, num_workers=0)
                   for x in ['train', 'val']}
    dataset_sizes = {x: len(image_datasets[x]) for x in ['train', 'val']}
    class_names = image_datasets['train'].classes
    
    # Save the class names index mapping
    with open(CLASS_MAP_PATH, "w") as f:
        json.dump(class_names, f)
    print(f"Saved class mapping to {CLASS_MAP_PATH}: {class_names}")

    # Load pre-trained ResNet18 model
    print("Initializing ResNet18 model...")
    model = models.resnet18(pretrained=True)
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, len(class_names))
    
    # Detect GPU acceleration
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    print(f"Training started on device: {device}...")
    for epoch in range(epochs):
        print(f'\nEpoch {epoch + 1}/{epochs}')
        print('-' * 15)

        for phase in ['train', 'val']:
            if phase == 'train':
                model.train()
            else:
                model.eval()

            running_loss = 0.0
            running_corrects = 0

            for inputs, labels in dataloaders[phase]:
                inputs = inputs.to(device)
                labels = labels.to(device)

                optimizer.zero_grad()

                with torch.set_grad_enabled(phase == 'train'):
                    outputs = model(inputs)
                    _, preds = torch.max(outputs, 1)
                    loss = criterion(outputs, labels)

                    if phase == 'train':
                        loss.backward()
                        optimizer.step()

                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == labels.data)

            epoch_loss = running_loss / dataset_sizes[phase]
            epoch_acc = running_corrects.double() / dataset_sizes[phase]

            print(f'{phase.capitalize()} Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f}')

    # Save trained state dict weights
    torch.save(model.state_dict(), MODEL_SAVE_PATH)
    torch.save(model.state_dict(), "models/disease_model.pt")
    print(f"\nModel training complete! Weights saved to: {MODEL_SAVE_PATH} and models/disease_model.pt")

if __name__ == "__main__":
    train_model(epochs=25, batch_size=32)
