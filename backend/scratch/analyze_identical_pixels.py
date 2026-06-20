import os
from PIL import Image
import numpy as np

LEAVES_DIR = r"c:\Users\durga\kisan_mitra\dataset\test\Plant_Healthy"

# Let's generate sample audit images
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from false_acceptance_audit import GENERATORS

def get_identical_fraction(img):
    img_np = np.array(img.convert("RGB"))
    h, w, c = img_np.shape
    # Count how many pixels are identical to their right neighbor
    diff_r = np.all(img_np[:, :-1, :] == img_np[:, 1:, :], axis=2)
    # Count how many pixels are identical to their bottom neighbor
    diff_d = np.all(img_np[:-1, :, :] == img_np[1:, :, :], axis=2)
    
    total_r = img_np[:, :-1, :].shape[0] * img_np[:, :-1, :].shape[1]
    total_d = img_np[:-1, :, :].shape[0] * img_np[:-1, :, :].shape[1]
    
    frac_r = np.sum(diff_r) / total_r
    frac_d = np.sum(diff_d) / total_d
    
    return max(frac_r, frac_d)

print("--- ANALYZING GENERATED IMAGES ---")
for name, gen_fn in GENERATORS.items():
    img_bytes = gen_fn(0)
    import io
    img = Image.open(io.BytesIO(img_bytes))
    frac = get_identical_fraction(img)
    print(f"[{name}]: {frac*100:.2f}% identical neighbors")

print("\n--- ANALYZING REAL LEAF IMAGES ---")
files = [f for f in os.listdir(LEAVES_DIR) if f.lower().endswith((".jpg", ".jpeg", ".png"))][:20]
for f in files:
    path = os.path.join(LEAVES_DIR, f)
    img = Image.open(path)
    frac = get_identical_fraction(img)
    print(f"[{f}]: {frac*100:.2f}% identical neighbors")
