import os
import json
import torch
import torch.nn as nn
from torchvision import models

def get_model_info(path):
    if not os.path.exists(path):
        return f"File not found: {path}"
    try:
        # Load weights
        sd = torch.load(path, map_location="cpu", weights_only=True)
        keys = list(sd.keys())
        
        # Determine architecture clues
        arch = "Unknown"
        fc_size = None
        
        # ResNet clues: has 'layer1.0.conv1.weight', 'fc.weight'
        if 'fc.weight' in sd:
            fc_size = sd['fc.weight'].shape
            if 'layer4.1.conv2.weight' in sd:
                if sd['fc.weight'].shape[1] == 512:
                    arch = "ResNet18 / ResNet34"
                elif sd['fc.weight'].shape[1] == 2048:
                    arch = "ResNet50 / ResNet101 / ResNet152"
            else:
                arch = f"ResNet-like (fc shape: {fc_size})"
        # EfficientNet clues: has 'features.0.0.weight', 'classifier.1.weight'
        elif 'classifier.1.weight' in sd:
            fc_size = sd['classifier.1.weight'].shape
            arch = f"EfficientNet-like (classifier shape: {fc_size})"
        
        return {
            "path": path,
            "architecture": arch,
            "fc_shape": fc_size,
            "keys_sample": keys[:10],
            "total_keys": len(keys)
        }
    except Exception as e:
        return f"Error loading {path}: {e}"

def main():
    print("=== Model Forensic Audit ===")
    
    # 1. Inspect model files
    models_to_check = [
        "models/disease_model.pt",
        "models/plant_disease_resnet.pt",
        "models/crop_model.pt"
    ]
    for m in models_to_check:
        print(f"\nInspecting {m}:")
        info = get_model_info(m)
        if isinstance(info, dict):
            for k, v in info.items():
                print(f"  {k}: {v}")
        else:
            print(f"  {info}")
            
    # 2. Inspect classes.json
    classes_path = "models/classes.json"
    classes = []
    if os.path.exists(classes_path):
        with open(classes_path, "r") as f:
            classes = json.load(f)
        print(f"\nclasses.json path: {classes_path}")
        print(f"Number of classes in classes.json: {len(classes)}")
    else:
        print(f"\n{classes_path} not found")
        
    # 3. Inspect dataset directories
    dataset_dir = "dataset"
    splits = ["train", "val", "test"]
    dataset_info = {}
    
    for split in splits:
        split_path = os.path.join(dataset_dir, split)
        if os.path.exists(split_path):
            subdirs = sorted([d for d in os.listdir(split_path) if os.path.isdir(os.path.join(split_path, d))])
            image_counts = {}
            total_images = 0
            for d in subdirs:
                d_path = os.path.join(split_path, d)
                files = [f for f in os.listdir(d_path) if os.path.isfile(os.path.join(d_path, f))]
                image_counts[d] = len(files)
                total_images += len(files)
            dataset_info[split] = {
                "classes": subdirs,
                "counts": image_counts,
                "total_images": total_images
            }
        else:
            dataset_info[split] = None

    for split in splits:
        print(f"\nSplit: {split}")
        if dataset_info[split]:
            print(f"  Total images: {dataset_info[split]['total_images']}")
            print(f"  Number of class folders: {len(dataset_info[split]['classes'])}")
            print(f"  First 5 classes/counts:")
            for d in dataset_info[split]['classes'][:5]:
                print(f"    {d}: {dataset_info[split]['counts'][d]} images")
        else:
            print(f"  Directory not found: {os.path.join(dataset_dir, split)}")
            
    # Compare classes
    if classes and dataset_info["train"]:
        json_classes = set(classes)
        train_classes = set(dataset_info["train"]["classes"])
        
        missing_in_train = json_classes - train_classes
        extra_in_train = train_classes - json_classes
        
        print(f"\nClass Consistency Checks:")
        print(f"  Classes in classes.json but missing from train/ folder: {len(missing_in_train)}")
        if missing_in_train:
            print(f"    Sample missing: {list(missing_in_train)[:5]}")
        print(f"  Classes in train/ folder but missing from classes.json: {len(extra_in_train)}")
        if extra_in_train:
            print(f"    Sample extra: {list(extra_in_train)[:5]}")
            
        # Verify indexing/ordering
        # PyTorch ImageFolder classes are sorted alphabetically
        sorted_train_classes = sorted(list(train_classes))
        mismatched_indices = []
        for idx, (json_cls, train_cls) in enumerate(zip(classes, sorted_train_classes)):
            if json_cls != train_cls:
                mismatched_indices.append((idx, json_cls, train_cls))
                
        print(f"  Mismatched index mappings (between classes.json and sorted train directory structure): {len(mismatched_indices)}")
        if mismatched_indices:
            print(f"    First 5 mismatches:")
            for idx, jc, tc in mismatched_indices[:5]:
                print(f"      Index {idx}: classes.json='{jc}' vs FolderName='{tc}'")

if __name__ == "__main__":
    main()
