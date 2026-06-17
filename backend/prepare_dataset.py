import os
import argparse
import random
import urllib.request
import zipfile
import shutil
from PIL import Image, ImageDraw

# All 45 keys from DISEASE_DB
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

def db_key_to_class_name(key: str) -> str:
    if key.startswith("pepper_bell_"):
        disease = key[len("pepper_bell_"):]
        disease_title = "_".join(w.capitalize() for w in disease.split("_"))
        return f"Pepper_Bell___{disease_title}"
    parts = key.split("_")
    crop = parts[0].capitalize()
    disease = "_".join(w.capitalize() for w in parts[1:])
    return f"{crop}___{disease}"

def generate_synthetic_leaf(path: str, is_healthy: bool, disease_type: str):
    """Generates a synthetic green leaf image with optional spots to represent diseases."""
    img = Image.new('RGB', (224, 224), color=(34, 139, 34)) # Forest green background
    draw = ImageDraw.Draw(img)
    
    # Draw a leaf shape (ellipse/polygon)
    draw.polygon([(112, 10), (200, 112), (112, 214), (24, 112)], fill=(46, 184, 46))
    
    if not is_healthy:
        # Draw spots
        num_spots = random.randint(5, 20)
        for _ in range(num_spots):
            x = random.randint(40, 180)
            y = random.randint(40, 180)
            r = random.randint(3, 12)
            
            # Select spot color based on disease category
            if "blight" in disease_type or "rot" in disease_type or "spot" in disease_type:
                color = (139, 69, 19) # Brown spots
            elif "yellow" in disease_type or "curl" in disease_type or "mildew" in disease_type:
                color = (235, 235, 120) # Yellowish spots
            elif "rust" in disease_type:
                color = (210, 105, 30) # Orange/rust spots
            else:
                color = (50, 50, 50) # Dark spots
                
            draw.ellipse([x-r, y-r, x+r, y+r], fill=color)
            
            # Add secondary outer halos
            if random.random() > 0.5:
                draw.ellipse([x-r-2, y-r-2, x+r+2, y+r+2], outline=(200, 180, 50), width=1)
                
    img.save(path, format='JPEG')

def setup_dataset(mock=False):
    base_dir = "dataset"
    splits = ["train", "val", "test"]
    
    print("Preparing directories...")
    for split in splits:
        split_dir = os.path.join(base_dir, split)
        if os.path.exists(split_dir):
            shutil.rmtree(split_dir)
        os.makedirs(split_dir, exist_ok=True)
        
    class_names = [db_key_to_class_name(k) for k in DISEASE_KEYS]
    
    for cls in class_names:
        for split in splits:
            os.makedirs(os.path.join(base_dir, split, cls), exist_ok=True)
            
    print(f"Set up directory structure for {len(class_names)} classes.")

    # Generate synthetic dataset
    print("Generating synthetic dataset images...")
    # Train: 15 images/class, Val: 5 images/class, Test: 5 images/class
    samples = {"train": 15, "val": 5, "test": 5}
    
    for key in DISEASE_KEYS:
        cls_name = db_key_to_class_name(key)
        is_healthy = "healthy" in key
        
        for split, count in samples.items():
            for idx in range(count):
                path = os.path.join(base_dir, split, cls_name, f"synth_{idx}.jpg")
                generate_synthetic_leaf(path, is_healthy, key)
                
    print(f"[OK] Generated synthetic images under 'dataset/' split directory.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mock", action="store_true", default=True, help="Use mock synthetic generator (default: True)")
    args = parser.parse_args()
    setup_dataset(mock=args.mock)
