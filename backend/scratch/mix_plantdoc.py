import os
import shutil
import hashlib
import random
import json
from PIL import Image

WORKSPACE_DIR = r"c:\Users\durga\kisan_mitra"
BACKEND_DIR = os.path.join(WORKSPACE_DIR, "backend")
DATASET_DIR = os.path.join(WORKSPACE_DIR, "dataset")
SCRATCH_DIR = os.path.join(BACKEND_DIR, "scratch")
VAL_SET_DIR = os.path.join(SCRATCH_DIR, "field_validation_set")
PLANTDOC_ROOT = os.path.join(SCRATCH_DIR, "plantdoc_extracted", "PlantDoc-Dataset-master")

# Map Kisan Mitra classes to PlantDoc-Dataset folder paths
PLANT_DOC_MAP = {
    # Tomato
    "Tomato___Bacterial_Spot": ["test/Tomato leaf bacterial spot", "train/Tomato leaf bacterial spot"],
    "Tomato___Early_Blight": ["test/Tomato Early blight leaf", "train/Tomato Early blight leaf"],
    "Tomato___Late_Blight": ["test/Tomato leaf late blight", "train/Tomato leaf late blight"],
    "Tomato___Leaf_Mold": ["test/Tomato mold leaf", "train/Tomato mold leaf"],
    "Tomato___Septoria_Leaf_Spot": ["test/Tomato Septoria leaf spot", "train/Tomato Septoria leaf spot"],
    "Tomato___Spider_Mites": ["train/Tomato two spotted spider mites leaf", "test/Tomato leaf", "train/Tomato leaf"],
    "Tomato___Target_Spot": ["test/Tomato leaf", "train/Tomato leaf"],
    "Tomato___Yellow_Leaf_Curl_Virus": ["test/Tomato leaf yellow virus", "train/Tomato leaf yellow virus"],
    "Tomato___Mosaic_Virus": ["test/Tomato leaf mosaic virus", "train/Tomato leaf mosaic virus"],
    "Tomato___Healthy": ["test/Tomato leaf", "train/Tomato leaf"],
    
    # Potato
    "Potato___Early_Blight": ["test/Potato leaf early blight", "train/Potato leaf early blight"],
    "Potato___Late_Blight": ["test/Potato leaf late blight", "train/Potato leaf late blight"],
    "Potato___Healthy": ["test/Potato leaf early blight", "train/Potato leaf early blight", "test/Potato leaf late blight", "train/Potato leaf late blight"],
    
    # Grape
    "Grape___Black_Rot": ["test/grape leaf black rot", "train/grape leaf black rot"],
    "Grape___Esca": ["test/grape leaf", "train/grape leaf"],
    "Grape___Leaf_Blight": ["test/grape leaf", "train/grape leaf"],
    "Grape___Healthy": ["test/grape leaf", "train/grape leaf"]
}

def get_md5(path):
    hash_md5 = hashlib.md5()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception:
        return None

def check_image_valid(path):
    try:
        with Image.open(path) as img:
            img.verify()
        with Image.open(path) as img:
            img.load()
        return True
    except Exception:
        return False

def main():
    print("Starting PlantDoc Domain Mixing...", flush=True)
    random.seed(42)

    # 1. Collect MD5 hashes of all validation images currently in field_validation_set
    print("Scanning validation set to avoid overlap...", flush=True)
    val_md5s = set()
    for root, dirs, files in os.walk(VAL_SET_DIR):
        for f in files:
            fp = os.path.join(root, f)
            md5 = get_md5(fp)
            if md5:
                val_md5s.add(md5)
    print(f"Loaded {len(val_md5s)} reserved validation MD5 hashes.", flush=True)

    # 2. Iterate classes and mix
    for km_class, paths in PLANT_DOC_MAP.items():
        print(f"\nProcessing class: {km_class}...", flush=True)
        
        # Collect all candidate files from PlantDoc
        candidates = []
        for p in paths:
            full_dir = os.path.join(PLANTDOC_ROOT, p)
            if os.path.exists(full_dir):
                for f in os.listdir(full_dir):
                    if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                        candidates.append(os.path.join(full_dir, f))
                        
        print(f"  Found {len(candidates)} candidate files in PlantDoc.", flush=True)
        random.shuffle(candidates)
        
        # Filter duplicates and corrupt
        clean_candidates = []
        for fp in candidates:
            md5 = get_md5(fp)
            if not md5 or md5 in val_md5s:
                continue
            if not check_image_valid(fp):
                continue
            clean_candidates.append(fp)
            
        print(f"  Clean candidates (excluding validation): {len(clean_candidates)}", flush=True)
        
        # Determine splits: 80% train, 20% val
        split_idx = int(len(clean_candidates) * 0.8)
        train_list = clean_candidates[:split_idx]
        val_list = clean_candidates[split_idx:]
        
        train_dest_dir = os.path.join(DATASET_DIR, "train", km_class)
        val_dest_dir = os.path.join(DATASET_DIR, "val", km_class)
        
        os.makedirs(train_dest_dir, exist_ok=True)
        os.makedirs(val_dest_dir, exist_ok=True)
        
        # Copy to train split
        copied_train = 0
        for idx, fp in enumerate(train_list):
            dest_fp = os.path.join(train_dest_dir, f"plantdoc_real_{idx}.jpg")
            shutil.copy(fp, dest_fp)
            copied_train += 1
            
        # Copy to val split
        copied_val = 0
        for idx, fp in enumerate(val_list):
            dest_fp = os.path.join(val_dest_dir, f"plantdoc_real_{idx}.jpg")
            shutil.copy(fp, dest_fp)
            copied_val += 1
            
        print(f"  Copied {copied_train} to train, {copied_val} to val.", flush=True)

    print("\nPlantDoc Domain Mixing Completed Successfully!", flush=True)

if __name__ == "__main__":
    main()
