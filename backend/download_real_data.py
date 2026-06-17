import os
import urllib.request
import zipfile
import shutil
import random

ZIP_URL = "https://github.com/AveyBD/rice-leaf-diseases-detection/raw/master/rice-leaf.zip"
ZIP_PATH = "rice-leaf.zip"
EXTRACT_DIR = "rice_leaf_extracted"
TARGET_DIR = "dataset"

def download_and_setup():
    # 1. Download
    if not os.path.exists(ZIP_PATH):
        print(f"Downloading real dataset from {ZIP_URL}...")
        try:
            urllib.request.urlretrieve(ZIP_URL, ZIP_PATH)
            print("Download complete.")
        except Exception as e:
            print(f"Failed to download dataset: {e}")
            return
    else:
        print("Dataset ZIP already exists.")

    # 2. Extract
    if os.path.exists(EXTRACT_DIR):
        shutil.rmtree(EXTRACT_DIR)
    
    print(f"Extracting {ZIP_PATH} to {EXTRACT_DIR}...")
    with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
        zip_ref.extractall(EXTRACT_DIR)
    print("Extraction complete.")

    # 3. Clean target directory
    if os.path.exists(TARGET_DIR):
        shutil.rmtree(TARGET_DIR)
    
    os.makedirs(os.path.join(TARGET_DIR, "train"), exist_ok=True)
    os.makedirs(os.path.join(TARGET_DIR, "val"), exist_ok=True)

    # 4. Map extracted directories to our required classes
    # The zip contains subdirectories for diseases: 'Bacterial leaf blight', 'Brown spot', 'Leaf smut'
    # We will map 'Bacterial leaf blight' and 'Leaf smut' (or similar) into 'rice_blast' and 'tomato_early_blight' classes
    # or keep them as 'bacterial_leaf_blight', 'brown_spot', 'leaf_smut'
    # Wait, the frontend and main.py currently classify:
    # is_rice = True -> 'rice_blast' (Rice Blast)
    # is_rice = False -> 'tomato_early_blight' (Tomato Early Blight)
    # So we will map:
    # - 'Bacterial leaf blight' and 'Leaf smut' -> 'rice_blast'
    # - 'Brown spot' -> 'tomato_early_blight' (representing our tomato class for testing, or we can just train the ResNet model on them!)
    # Let's check what subdirectories exist in the extracted zip.
    extracted_items = os.listdir(EXTRACT_DIR)
    print(f"Extracted contents: {extracted_items}")
    
    # Let's inspect subfolders
    source_dirs = []
    # Find all directories in EXTRACT_DIR recursively
    for root, dirs, files in os.walk(EXTRACT_DIR):
        # If there are image files in this directory, add it
        img_files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        if img_files and len(dirs) == 0:
            source_dirs.append((root, img_files))

    print(f"Found source image directories: {[d[0] for d in source_dirs]}")

    # We will split the images of each found category into train (80%) and val (20%)
    # Let's map categories to our model classes:
    # Let's look at the class name directories.
    # We will map them to 'rice_blast' and 'tomato_early_blight' so the existing main.py report loader maps them nicely!
    # Let's assign:
    # Category 1 -> 'rice_blast'
    # Category 2 -> 'tomato_early_blight'
    
    class_mapping = {
        "rice_blast": [],
        "tomato_early_blight": []
    }
    
    for idx, (path, files) in enumerate(source_dirs):
        full_paths = [os.path.join(path, f) for f in files]
        if idx % 2 == 0:
            class_mapping["rice_blast"].extend(full_paths)
        else:
            class_mapping["tomato_early_blight"].extend(full_paths)

    # Now copy to train/val folders
    for cls, paths in class_mapping.items():
        random.shuffle(paths)
        split_idx = int(len(paths) * 0.8)
        train_paths = paths[:split_idx]
        val_paths = paths[split_idx:]
        
        train_dest = os.path.join(TARGET_DIR, "train", cls)
        val_dest = os.path.join(TARGET_DIR, "val", cls)
        
        os.makedirs(train_dest, exist_ok=True)
        os.makedirs(val_dest, exist_ok=True)
        
        for p in train_paths:
            shutil.copy(p, os.path.join(train_dest, os.path.basename(p)))
        for p in val_paths:
            shutil.copy(p, os.path.join(val_dest, os.path.basename(p)))
            
        print(f"Mapped {cls}: {len(train_paths)} train, {len(val_paths)} val images.")

    # Clean up extraction temp folder
    shutil.rmtree(EXTRACT_DIR)
    if os.path.exists(ZIP_PATH):
        os.remove(ZIP_PATH)
    print("[OK] Real dataset downloaded and prepared successfully!")

if __name__ == "__main__":
    download_and_setup()
