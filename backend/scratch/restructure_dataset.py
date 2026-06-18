import os
import shutil
import json

WORKSPACE_DIR = r"c:\Users\durga\kisan_mitra"
DATASET_DIR = os.path.join(WORKSPACE_DIR, "dataset")
LEGACY_DATASET_DIR = os.path.join(WORKSPACE_DIR, "dataset_legacy")
BACKEND_DIR = os.path.join(WORKSPACE_DIR, "backend")
CLASSES_JSON_PATH = os.path.join(BACKEND_DIR, "models", "classes.json")

# Define target taxonomy mapping
LEGACY_CROPS = ["Apple", "Peach", "Cherry", "Orange"]
REMOVED_CROPS = ["Blueberry", "Raspberry", "Squash", "Strawberry"]
ACTIVE_CROPS = ["Rice", "Cotton", "Grape", "Tomato", "Potato", "Corn", "Pepper_Bell", "Soybean"]

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
    "Corn___Common_Rust",
    "Corn___Gray_Leaf_Spot",
    "Corn___Northern_Leaf_Blight",
    "Pepper_Bell___Bacterial_Spot",
    "Plant_Healthy"
]

def restructure():
    print("Starting taxonomy restructuring...")
    splits = ["train", "val", "test"]

    # Ensure legacy dataset directory exists
    os.makedirs(LEGACY_DATASET_DIR, exist_ok=True)

    for split in splits:
        split_dir = os.path.join(DATASET_DIR, split)
        if not os.path.exists(split_dir):
            print(f"Split folder {split_dir} not found. Skipping.")
            continue

        # Create Plant_Healthy directory for the split
        plant_healthy_dir = os.path.join(split_dir, "Plant_Healthy")
        os.makedirs(plant_healthy_dir, exist_ok=True)

        for folder in os.listdir(split_dir):
            folder_path = os.path.join(split_dir, folder)
            if not os.path.isdir(folder_path):
                continue

            crop = folder.split("___")[0]

            # 1. Check if crop is removed entirely
            if crop in REMOVED_CROPS:
                print(f"Removing deprecated class folder: {folder_path}")
                shutil.rmtree(folder_path)
                continue

            # 2. Check if crop is moved to legacy support
            if crop in LEGACY_CROPS:
                legacy_dest_dir = os.path.join(LEGACY_DATASET_DIR, split, folder)
                print(f"Moving legacy support class folder: {folder} -> {legacy_dest_dir}")
                os.makedirs(os.path.dirname(legacy_dest_dir), exist_ok=True)
                if os.path.exists(legacy_dest_dir):
                    shutil.rmtree(legacy_dest_dir)
                shutil.move(folder_path, legacy_dest_dir)
                continue

            # 3. Check if folder represents a Healthy class to merge
            if folder.endswith("___Healthy"):
                print(f"Merging healthy class folder: {folder} -> Plant_Healthy")
                for f in os.listdir(folder_path):
                    if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                        src_file = os.path.join(folder_path, f)
                        # Avoid collision by prefixing crop name
                        dest_file = os.path.join(plant_healthy_dir, f"{crop.lower()}_healthy_{f}")
                        shutil.copy2(src_file, dest_file)
                # Remove original folder after files copied
                shutil.rmtree(folder_path)

    # Write updated classes.json
    print(f"Writing updated classes.json with {len(ACTIVE_CLASSES)} classes...")
    os.makedirs(os.path.dirname(CLASSES_JSON_PATH), exist_ok=True)
    with open(CLASSES_JSON_PATH, "w") as f:
        json.dump(ACTIVE_CLASSES, f)

    print("Taxonomy restructuring completed successfully.")

if __name__ == "__main__":
    restructure()
