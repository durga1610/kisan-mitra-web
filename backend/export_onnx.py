import os
import sys
import json
import torch
import torch.nn as nn
from torchvision import models

MODEL_SAVE_PATH = "models/disease_model.pt"
ONNX_SAVE_PATH = "models/disease_model.onnx"
CLASS_MAP_PATH = "models/classes.json"

def build_model(num_classes):
    # Try loading as EfficientNet-B0 first
    try:
        model = models.efficientnet_b0()
        in_features = model.classifier[1].in_features
        model.classifier[1] = nn.Linear(in_features, num_classes)
    except Exception:
        model = models.resnet50()
        in_features = model.fc.in_features
        model.fc = nn.Linear(in_features, num_classes)
    return model

def main():
    if not os.path.exists(MODEL_SAVE_PATH) or not os.path.exists(CLASS_MAP_PATH):
        print(f"Error: Trained model weights ('{MODEL_SAVE_PATH}') or class index mapping ('{CLASS_MAP_PATH}') not found.")
        sys.exit(1)

    # Load classes count
    with open(CLASS_MAP_PATH, "r") as f:
        class_names = json.load(f)
    num_classes = len(class_names)

    # Initialize model
    model = build_model(num_classes)
    
    device = torch.device("cpu")
    try:
        model.load_state_dict(torch.load(MODEL_SAVE_PATH, map_location=device))
    except Exception as e:
        print(f"Error loading state dict, trying alternative ResNet loader: {e}")
        # Try ResNet fallback
        model = models.resnet50()
        in_features = model.fc.in_features
        model.fc = nn.Linear(in_features, num_classes)
        model.load_state_dict(torch.load(MODEL_SAVE_PATH, map_location=device))

    model.eval()

    # Create a dummy input matching training size: [batch, channels, height, width]
    dummy_input = torch.randn(1, 3, 128, 128, requires_grad=True)

    print(f"Exporting PyTorch model to ONNX format at '{ONNX_SAVE_PATH}'...")
    
    # Export model to ONNX
    torch.onnx.export(
        model,
        dummy_input,
        ONNX_SAVE_PATH,
        export_params=True,
        opset_version=11,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}
    )

    if os.path.exists(ONNX_SAVE_PATH):
        print(f"[OK] ONNX export completed successfully: {ONNX_SAVE_PATH}")
    else:
        print("ONNX export failed.")

if __name__ == "__main__":
    main()
