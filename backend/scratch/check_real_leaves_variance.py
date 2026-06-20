import os
from PIL import Image
import numpy as np

LEAVES_DIR = r"c:\Users\durga\kisan_mitra\dataset\test\Plant_Healthy"
files = [f for f in os.listdir(LEAVES_DIR) if f.lower().endswith((".jpg", ".jpeg", ".png"))]

high_variance_count = 0
total_checked = 0

print("--- SCANNING REAL LEAVES FOR LAPLACIAN VARIANCE ---")
for f in files[:200]:
    path = os.path.join(LEAVES_DIR, f)
    img = Image.open(path)
    gray = img.convert("L")
    gray_np = np.array(gray).astype(float)
    laplacian = np.abs(gray_np[1:-1, 1:-1] * 4 - gray_np[:-2, 1:-1] - gray_np[2:, 1:-1] - gray_np[1:-1, :-2] - gray_np[1:-1, 2:])
    variance = np.var(laplacian)
    total_checked += 1
    if variance > 500.0:
        print(f"[HIGH VAR] {f}: {variance:.2f}")
        high_variance_count += 1
    elif total_checked <= 10:
        print(f"{f}: {variance:.2f}")

print(f"Total checked: {total_checked}, High variance (>500): {high_variance_count}")
