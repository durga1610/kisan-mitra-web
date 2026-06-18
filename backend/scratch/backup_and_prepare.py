import os
import shutil
import json

WORKSPACE_DIR = r"c:\Users\durga\kisan_mitra"
BACKEND_DIR = os.path.join(WORKSPACE_DIR, "backend")
DATASET_DIR = os.path.join(WORKSPACE_DIR, "dataset")
LEGACY_DATASET_DIR = os.path.join(WORKSPACE_DIR, "dataset_legacy")
BACKUP_DIR = os.path.join(BACKEND_DIR, "models_backup", "final_45_class")
DATASET_BACKUP_24_DIR = os.path.join(WORKSPACE_DIR, "dataset_backup_24")

def backup_and_prepare():
    print("=== Step 1: Backing up 45-class model and configuration ===")
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # 1. Back up 45-class model if it exists in models
    model_path = os.path.join(BACKEND_DIR, "models", "plant_disease_resnet.pt")
    if os.path.exists(model_path):
        shutil.copy2(model_path, os.path.join(BACKUP_DIR, "plant_disease_resnet.pt"))
        print(f"Backed up model to {os.path.join(BACKUP_DIR, 'plant_disease_resnet.pt')}")
    else:
        print("Warning: plant_disease_resnet.pt not found in models/")

    # 2. Back up active classes.json
    classes_path = os.path.join(BACKEND_DIR, "models", "classes.json")
    if os.path.exists(classes_path):
        shutil.copy2(classes_path, os.path.join(BACKUP_DIR, "classes.json"))
        print(f"Backed up classes.json to {os.path.join(BACKUP_DIR, 'classes.json')}")
        
    # 3. Back up training configurations
    train_config = os.path.join(BACKEND_DIR, "scratch", "train_unfrozen_resnet.py")
    if os.path.exists(train_config):
        shutil.copy2(train_config, os.path.join(BACKUP_DIR, "train_unfrozen_resnet.py"))
        print(f"Backed up training config to {os.path.join(BACKUP_DIR, 'train_unfrozen_resnet.py')}")

    print("\n=== Step 2: Recreating the 24-class dataset backup ===")
    splits = ["train", "val", "test"]
    legacy_classes_24 = [
        "Corn___Common_Rust",
        "Corn___Gray_Leaf_Spot",
        "Corn___Northern_Leaf_Blight",
        "Pepper_Bell___Bacterial_Spot"
    ]
    
    # Clean previous 24-class dataset backup if it exists
    if os.path.exists(DATASET_BACKUP_24_DIR):
        print(f"Cleaning existing backup directory: {DATASET_BACKUP_24_DIR}")
        shutil.rmtree(DATASET_BACKUP_24_DIR)
    os.makedirs(DATASET_BACKUP_24_DIR, exist_ok=True)

    for split in splits:
        split_dest = os.path.join(DATASET_BACKUP_24_DIR, split)
        os.makedirs(split_dest, exist_ok=True)
        
        # Copy active 20 classes from dataset/
        split_src = os.path.join(DATASET_DIR, split)
        if os.path.exists(split_src):
            for cls in os.listdir(split_src):
                cls_src_path = os.path.join(split_src, cls)
                if os.path.isdir(cls_src_path):
                    cls_dest_path = os.path.join(split_dest, cls)
                    shutil.copytree(cls_src_path, cls_dest_path)
            print(f"Copied active classes for split: {split}")

        # Copy the 4 legacy classes from dataset_legacy/
        legacy_split_src = os.path.join(LEGACY_DATASET_DIR, split)
        if os.path.exists(legacy_split_src):
            for cls in legacy_classes_24:
                cls_src_path = os.path.join(legacy_split_src, cls)
                if os.path.exists(cls_src_path) and os.path.isdir(cls_src_path):
                    cls_dest_path = os.path.join(split_dest, cls)
                    shutil.copytree(cls_src_path, cls_dest_path)
                    print(f"  Copied legacy class {cls} for split: {split}")
                    
    print("\nBackup and 24-class dataset preparation successfully completed!")

if __name__ == "__main__":
    backup_and_prepare()
