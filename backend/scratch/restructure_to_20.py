import os
import shutil
import json

WORKSPACE_DIR = r"c:\Users\durga\kisan_mitra"
DATASET_DIR = os.path.join(WORKSPACE_DIR, "dataset")
LEGACY_DATASET_DIR = os.path.join(WORKSPACE_DIR, "dataset_legacy")
BACKEND_DIR = os.path.join(WORKSPACE_DIR, "backend")
CLASSES_JSON_PATH = os.path.join(BACKEND_DIR, "models", "classes.json")

# Define target 20 classes taxonomy mapping
LEGACY_CROPS = ["Corn", "Pepper_Bell"]

ACTIVE_CLASSES = [
    "Cotton___Bacterial_Blight",
    "Cotton___Leaf_Curl",
    "Rice___Bacterial_Leaf_Blight",
    "Rice___Blast",
    "Rice___Brown_Spot",
    "Tomato___Bacterial_Spot",
    "Tomato___Early_Blight",
    "Tomato___Late_Blight",
    "Tomato___Leaf_Mold",
    "Tomato___Mosaic_Virus",
    "Tomato___Septoria_Leaf_Spot",
    "Tomato___Spider_Mites",
    "Tomato___Target_Spot",
    "Tomato___Yellow_Leaf_Curl_Virus",
    "Grape___Black_Rot",
    "Grape___Esca",
    "Grape___Leaf_Blight",
    "Potato___Early_Blight",
    "Potato___Late_Blight",
    "Plant_Healthy"
]

def restructure_to_20():
    print("Starting 20-class taxonomy restructuring...")
    
    # 1. Back up 24-class configuration files
    backup_dir = os.path.join(BACKEND_DIR, "models_backup", "24_class")
    os.makedirs(backup_dir, exist_ok=True)
    
    if os.path.exists(CLASSES_JSON_PATH):
        shutil.copy2(CLASSES_JSON_PATH, os.path.join(backup_dir, "classes_24.json"))
        
    train_config = os.path.join(BACKEND_DIR, "scratch", "train_unfrozen_resnet.py")
    if os.path.exists(train_config):
        shutil.copy2(train_config, os.path.join(backup_dir, "train_unfrozen_resnet_24.py"))
        
    print("24-class configuration backed up.")

    # 2. Reorganise dataset folders
    splits = ["train", "val", "test"]
    for split in splits:
        split_dir = os.path.join(DATASET_DIR, split)
        if not os.path.exists(split_dir):
            continue
            
        for folder in os.listdir(split_dir):
            folder_path = os.path.join(split_dir, folder)
            if not os.path.isdir(folder_path):
                continue
                
            crop = folder.split("___")[0]
            if crop in LEGACY_CROPS:
                legacy_dest_dir = os.path.join(LEGACY_DATASET_DIR, split, folder)
                print(f"Moving {folder} to legacy: {legacy_dest_dir}")
                os.makedirs(os.path.dirname(legacy_dest_dir), exist_ok=True)
                if os.path.exists(legacy_dest_dir):
                    shutil.rmtree(legacy_dest_dir)
                shutil.move(folder_path, legacy_dest_dir)

    # 3. Write updated classes.json
    print(f"Writing updated classes.json with {len(ACTIVE_CLASSES)} classes...")
    with open(CLASSES_JSON_PATH, "w") as f:
        json.dump(ACTIVE_CLASSES, f)

    print("Reorganisation completed.")

if __name__ == "__main__":
    restructure_to_20()
