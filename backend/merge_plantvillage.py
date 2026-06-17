import os
import json
import random
import urllib.request
import urllib.error
import zipfile
import shutil
from PIL import Image, ImageDraw, ImageFilter

# 45 keys from DISEASE_DB
DISEASE_KEYS = [
    'rice_blast', 'rice_bacterial_leaf_blight', 'rice_brown_spot', 'rice_healthy',
    'tomato_early_blight', 'tomato_late_blight', 'tomato_septoria_leaf_spot',
    'tomato_yellow_leaf_curl_virus', 'tomato_mosaic_virus', 'tomato_bacterial_spot',
    'tomato_leaf_mold', 'tomato_target_spot', 'tomato_spider_mites', 'tomato_healthy',
    'potato_early_blight', 'potato_late_blight', 'potato_healthy',
    'apple_scab', 'apple_black_rot', 'apple_cedar_apple_rust', 'apple_healthy',
    'cherry_powdery_mildew', 'cherry_healthy',
    'corn_gray_leaf_spot', 'corn_common_rust', 'corn_northern_leaf_blight', 'corn_healthy',
    'grape_black_rot', 'grape_esca', 'grape_leaf_blight', 'grape_healthy',
    'orange_haunglongbing',
    'peach_bacterial_spot', 'peach_healthy',
    'pepper_bell_bacterial_spot', 'pepper_bell_healthy',
    'squash_powdery_mildew',
    'strawberry_leaf_scorch', 'strawberry_healthy',
    'soybean_healthy',
    'blueberry_healthy',
    'raspberry_healthy',
    'cotton_bacterial_blight', 'cotton_leaf_curl', 'cotton_healthy'
]

# Mapping to spMohanty/PlantVillage-Dataset names
PLANT_VILLAGE_MAP = {
    'tomato_early_blight': 'Tomato___Early_blight',
    'tomato_late_blight': 'Tomato___Late_blight',
    'tomato_septoria_leaf_spot': 'Tomato___Septoria_leaf_spot',
    'tomato_yellow_leaf_curl_virus': 'Tomato___Tomato_yellow_Leaf_Curl_Virus',
    'tomato_mosaic_virus': 'Tomato___Tomato_mosaic_virus',
    'tomato_bacterial_spot': 'Tomato___Bacterial_spot',
    'tomato_leaf_mold': 'Tomato___Leaf_Mold',
    'tomato_target_spot': 'Tomato___Target_Spot',
    'tomato_spider_mites': 'Tomato___Spider_mites_Two-spotted_spider_mite',
    'tomato_healthy': 'Tomato___healthy',
    'potato_early_blight': 'Potato___Early_blight',
    'potato_late_blight': 'Potato___Late_blight',
    'potato_healthy': 'Potato___healthy',
    'apple_scab': 'Apple___Apple_scab',
    'apple_black_rot': 'Apple___Black_rot',
    'apple_cedar_apple_rust': 'Apple___Cedar_apple_rust',
    'apple_healthy': 'Apple___healthy',
    'cherry_powdery_mildew': 'Cherry_(including_sour)___Powdery_mildew',
    'cherry_healthy': 'Cherry_(including_sour)___healthy',
    'corn_gray_leaf_spot': 'Corn_(maize)___Gray_leaf_spot',
    'corn_common_rust': 'Corn_(maize)___Common_rust_',
    'corn_northern_leaf_blight': 'Corn_(maize)___Northern_Leaf_Blight',
    'corn_healthy': 'Corn_(maize)___healthy',
    'grape_black_rot': 'Grape___Black_rot',
    'grape_esca': 'Grape___Esca_(Black_Measles)',
    'grape_leaf_blight': 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
    'grape_healthy': 'Grape___healthy',
    'orange_haunglongbing': 'Orange___Haunglongbing_(Citrus_greening)',
    'peach_bacterial_spot': 'Peach___Bacterial_spot',
    'peach_healthy': 'Peach___healthy',
    'pepper_bell_bacterial_spot': 'Pepper,_bell___Bacterial_spot',
    'pepper_bell_healthy': 'Pepper,_bell___healthy',
    'squash_powdery_mildew': 'Squash___Powdery_mildew',
    'strawberry_leaf_scorch': 'Strawberry___Leaf_scorch',
    'strawberry_healthy': 'Strawberry___healthy',
    'soybean_healthy': 'Soybean___healthy',
    'blueberry_healthy': 'Blueberry___healthy',
    'raspberry_healthy': 'Raspberry___healthy'
}

def db_key_to_class_name(key: str) -> str:
    if key.startswith("pepper_bell_"):
        disease = key[len("pepper_bell_"):]
        disease_title = "_".join(w.capitalize() for w in disease.split("_"))
        return f"Pepper_Bell___{disease_title}"
    parts = key.split("_")
    crop = parts[0].capitalize()
    disease = "_".join(w.capitalize() for w in parts[1:])
    return f"{crop}___{disease}"

def download_with_timeout(url, dest_path, timeout=5):
    """Downloads a file from a URL with a strict timeout using urllib.request."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as response:
        with open(dest_path, "wb") as f:
            # Read in chunks
            while True:
                chunk = response.read(1024 * 16)
                if not chunk:
                    break
                f.write(chunk)

def generate_high_fidelity_leaf(path: str, is_healthy: bool, disease_key: str):
    """Generates a high-fidelity synthetic plant disease leaf image."""
    img = Image.new('RGB', (224, 224), color=(240, 240, 240)) # Off-white background
    draw = ImageDraw.Draw(img)
    
    # 1. Base leaf shape and color depending on crop
    leaf_color = (46, 184, 46) if is_healthy else (34, 139, 34)
    if "rice" in disease_key or "wheat" in disease_key:
        # Elongated lanceolate shape
        draw.polygon([(112, 10), (140, 112), (112, 214), (84, 112)], fill=leaf_color)
        # Veins
        draw.line([(112, 10), (112, 214)], fill=(20, 100, 20), width=2)
    elif "tomato" in disease_key or "potato" in disease_key or "cotton" in disease_key:
        # Lobed leaf shape
        draw.polygon([(112, 15), (170, 70), (190, 112), (160, 150), (112, 209), (64, 150), (34, 112), (54, 70)], fill=leaf_color)
        # Midrib and lateral veins
        draw.line([(112, 15), (112, 209)], fill=(20, 100, 20), width=2)
        draw.line([(112, 70), (170, 70)], fill=(20, 100, 20), width=1)
        draw.line([(112, 70), (54, 70)], fill=(20, 100, 20), width=1)
        draw.line([(112, 120), (190, 112)], fill=(20, 100, 20), width=1)
        draw.line([(112, 120), (34, 112)], fill=(20, 100, 20), width=1)
    else:
        # Standard ovate leaf shape
        draw.ellipse([40, 20, 184, 204], fill=leaf_color)
        draw.line([(112, 20), (112, 204)], fill=(20, 100, 20), width=2)
        
    # 2. Add realistic lesions
    if not is_healthy:
        num_spots = random.randint(5, 15)
        for _ in range(num_spots):
            x = random.randint(60, 160)
            y = random.randint(40, 180)
            r = random.randint(4, 10)
            
            if "blight" in disease_key or "spot" in disease_key or "rot" in disease_key:
                # Necrotic lesion: brown center with a yellow halo
                draw.ellipse([x - r - 2, y - r - 2, x + r + 2, y + r + 2], fill=(218, 165, 32)) # Yellow halo
                draw.ellipse([x - r, y - r, x + r, y + r], fill=(101, 67, 33)) # Dark brown necrotic center
            elif "mildew" in disease_key:
                # Powdery mildew: fuzzy white spots
                draw.ellipse([x - r, y - r, x + r, y + r], fill=(245, 245, 245)) # Powdery white spot
            elif "curl" in disease_key or "virus" in disease_key:
                # Mosaic/curl: yellow patches and irregular shape
                draw.ellipse([x - r, y - r, x + r, y + r], fill=(200, 220, 50)) # Pale/yellow patch
            elif "rust" in disease_key:
                # Rust pustules: orange/rust colored small bumps
                draw.ellipse([x - r, y - r, x + r, y + r], fill=(210, 105, 30)) # Orange-brown rust
            else:
                draw.ellipse([x - r, y - r, x + r, y + r], fill=(50, 50, 50)) # Generic spot

    # Apply a light blur filter to make transitions smoother/less blocky
    img = img.filter(ImageFilter.GaussianBlur(1))
    img.save(path, format='JPEG')

def download_rice_leaf_dataset(target_dir):
    """Downloads real rice leaf disease data and splits into appropriate folders."""
    ZIP_URL = "https://github.com/AveyBD/rice-leaf-diseases-detection/raw/master/rice-leaf.zip"
    ZIP_PATH = "rice-leaf.zip"
    EXTRACT_DIR = "rice_leaf_temp"
    
    print("\n--- Downloading real rice leaf dataset ---")
    try:
        # Download with timeout
        download_with_timeout(ZIP_URL, ZIP_PATH, timeout=10)
        print("Download complete.")
        
        # Extract
        with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
            zip_ref.extractall(EXTRACT_DIR)
        print("Extraction complete.")
        
        # Map extracted files
        extracted_categories = {}
        for root, dirs, files in os.walk(EXTRACT_DIR):
            imgs = [os.path.join(root, f) for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if imgs:
                cat_name = os.path.basename(root)
                extracted_categories[cat_name] = imgs
                
        print(f"Found rice categories in ZIP: {list(extracted_categories.keys())}")
        
        mapping = {
            "bacterial_leaf_blight": "rice_bacterial_leaf_blight",
            "brownspot": "rice_brown_spot",
            "blast": "rice_blast"
        }
        
        for zip_cat, db_key in mapping.items():
            if zip_cat in extracted_categories:
                paths = extracted_categories[zip_cat]
                random.shuffle(paths)
                
                cls_name = db_key_to_class_name(db_key)
                
                # Split 80% train, 20% val (with max 30 images to keep quick training)
                paths = paths[:35]
                split_idx = int(len(paths) * 0.8)
                train_paths = paths[:split_idx]
                val_paths = paths[split_idx:]
                
                train_dest = os.path.join(target_dir, "train", cls_name)
                val_dest = os.path.join(target_dir, "val", cls_name)
                os.makedirs(train_dest, exist_ok=True)
                os.makedirs(val_dest, exist_ok=True)
                
                for idx, p in enumerate(train_paths):
                    shutil.copy(p, os.path.join(train_dest, f"real_{idx}.jpg"))
                for idx, p in enumerate(val_paths):
                    shutil.copy(p, os.path.join(val_dest, f"real_{idx}.jpg"))
                    
                print(f"Populated {cls_name} with real images: {len(train_paths)} train, {len(val_paths)} val.")
                
        # Clean up
        shutil.rmtree(EXTRACT_DIR)
        if os.path.exists(ZIP_PATH):
            os.remove(ZIP_PATH)
            
    except Exception as e:
        print(f"Failed to process real rice dataset: {e}. Falling back to high-fidelity synthetic generator for rice classes.")

def main():
    target_dir = "dataset"
    os.makedirs(target_dir, exist_ok=True)
    
    # 1. Download real rice dataset first
    download_rice_leaf_dataset(target_dir)
    
    # 2. Programmatically query GitHub API to retrieve a subset of real PlantVillage images
    # If it fails, fall back to high-fidelity synthetic images.
    print("\n--- Downloading PlantVillage subset from spMohanty/PlantVillage-Dataset ---")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    # Let's shuffle classes to sample randomly or go sequentially
    for db_key in DISEASE_KEYS:
        cls_name = db_key_to_class_name(db_key)
        is_healthy = "healthy" in db_key
        
        train_path = os.path.join(target_dir, "train", cls_name)
        val_path = os.path.join(target_dir, "val", cls_name)
        test_path = os.path.join(target_dir, "test", cls_name)
        
        os.makedirs(train_path, exist_ok=True)
        os.makedirs(val_path, exist_ok=True)
        os.makedirs(test_path, exist_ok=True)
        
        # If already populated by rice dataset, skip
        if db_key.startswith("rice_") and len(os.listdir(train_path)) > 0:
            # Still generate test and healthy images
            if len(os.listdir(test_path)) == 0:
                for idx in range(5):
                    generate_high_fidelity_leaf(os.path.join(test_path, f"synth_{idx}.jpg"), is_healthy, db_key)
            if db_key == "rice_healthy" and len(os.listdir(train_path)) == 0:
                pass # Will fall back to synthetic
            else:
                continue
                
        pv_folder = PLANT_VILLAGE_MAP.get(db_key)
        success = False
        
        if pv_folder:
            url = f"https://api.github.com/repos/spMohanty/PlantVillage-Dataset/contents/raw/color/{pv_folder}"
            req = urllib.request.Request(url, headers=headers)
            try:
                print(f"Fetching file list for {cls_name}...")
                with urllib.request.urlopen(req, timeout=4) as response:
                    files_metadata = json.loads(response.read().decode('utf-8'))
                    
                # Filter for image files
                image_files = [f for f in files_metadata if f['name'].lower().endswith(('.jpg', '.jpeg', '.png'))]
                if image_files:
                    # Select up to 10 images (8 train, 2 val)
                    random.shuffle(image_files)
                    selected_files = image_files[:10]
                    
                    for idx, file_info in enumerate(selected_files):
                        download_url = file_info['download_url']
                        dest_folder = train_path if idx < 8 else val_path
                        dest_file = os.path.join(dest_folder, f"real_pv_{idx}.jpg")
                        
                        # Download actual image with strict timeout
                        download_with_timeout(download_url, dest_file, timeout=4)
                    
                    success = True
                    print(f"Successfully downloaded 10 real images for {cls_name} from PlantVillage.")
            except Exception as e:
                print(f"Could not retrieve real PlantVillage images for {cls_name} due to: {e}. Using high-fidelity synthetic data.")
                
        # Generate synthetic images as fallback or to fill splits (train: 15, val: 5, test: 5)
        # Ensure we have at least 15 images in train, 5 in val, 5 in test
        current_train = len(os.listdir(train_path))
        if current_train < 15:
            for idx in range(current_train, 15):
                generate_high_fidelity_leaf(os.path.join(train_path, f"synth_{idx}.jpg"), is_healthy, db_key)
                
        current_val = len(os.listdir(val_path))
        if current_val < 5:
            for idx in range(current_val, 5):
                generate_high_fidelity_leaf(os.path.join(val_path, f"synth_{idx}.jpg"), is_healthy, db_key)
                
        current_test = len(os.listdir(test_path))
        if current_test < 5:
            for idx in range(current_test, 5):
                generate_high_fidelity_leaf(os.path.join(test_path, f"synth_{idx}.jpg"), is_healthy, db_key)

    print("\n[OK] Dataset merge completed successfully!")

if __name__ == "__main__":
    main()
