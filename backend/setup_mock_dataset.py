import os
from PIL import Image, ImageDraw
import random

# --- CONFIGURATION ---
DATASET_DIR = "dataset"
CLASSES = ["rice_blast", "tomato_early_blight"]
SPLITS = {"train": 20, "val": 5}

def generate_synthetic_leaf(class_name, filename):
    # Create base green image (representing the leaf)
    img = Image.new("RGB", (256, 256), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    if class_name == "rice_blast":
        # Draw long, grass-like rice leaf (elongated green polygon)
        # Randomize shape slightly
        offset = random.randint(-10, 10)
        leaf_pts = [
            (110 + offset, 240),  # bottom left
            (146 + offset, 240),  # bottom right
            (138 + offset, 30),   # tip right
            (118 + offset, 30)    # tip left
        ]
        draw.polygon(leaf_pts, fill=(34, 139, 34)) # Forest Green
        
        # Add brown blast spots (spindle-shaped lesions)
        for _ in range(5):
            cx = random.randint(120, 136) + offset
            cy = random.randint(60, 200)
            # draw brown oval representing spot
            draw.ellipse([cx - 4, cy - 8, cx + 4, cy + 8], fill=(139, 69, 19)) # Saddle Brown
            
    elif class_name == "tomato_early_blight":
        # Draw round, wide tomato leaf (large oval)
        offset_x = random.randint(-15, 15)
        offset_y = random.randint(-15, 15)
        draw.ellipse([50 + offset_x, 50 + offset_y, 206 + offset_x, 206 + offset_y], fill=(46, 139, 87)) # Sea Green
        
        # Add concentric blight rings (brown circles)
        for _ in range(3):
            cx = random.randint(90, 160) + offset_x
            cy = random.randint(90, 160) + offset_y
            # Concentric rings
            draw.ellipse([cx - 15, cy - 15, cx + 15, cy + 15], outline=(101, 67, 33), width=2)
            draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], outline=(139, 69, 19), width=2)
            draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(80, 50, 20))
            
    img.save(filename, "JPEG")

def setup_all():
    print("Setting up synthetic plant disease dataset...")
    for split, count in SPLITS.items():
        for cls in CLASSES:
            class_dir = os.path.join(DATASET_DIR, split, cls)
            os.makedirs(class_dir, exist_ok=True)
            for i in range(count):
                filepath = os.path.join(class_dir, f"leaf_{i:03d}.jpg")
                generate_synthetic_leaf(cls, filepath)
                
    print(f"[OK] Synthetic dataset created successfully in '{DATASET_DIR}/' folder.")
    print("Structure:")
    print(f"  - {SPLITS['train']} images per class in dataset/train/")
    print(f"  - {SPLITS['val']} images per class in dataset/val/")

if __name__ == "__main__":
    setup_all()
