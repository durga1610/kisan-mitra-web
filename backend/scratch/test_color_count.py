import os
from PIL import Image
import numpy as np

LEAVES_DIR = r"c:\Users\durga\kisan_mitra\dataset\test\Plant_Healthy"

# Let's generate some sample audit images
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from false_acceptance_audit import GENERATORS

print("--- ANALYZING GENERATED IMAGES ---")
for name, gen_fn in GENERATORS.items():
    img_bytes = gen_fn(0)
    import io
    img = Image.open(io.BytesIO(img_bytes))
    
    # 1. Colors count at 16x16 Nearest
    small_nearest = img.resize((16, 16), Image.NEAREST)
    colors_nearest_16 = len(small_nearest.getcolors(maxcolors=256) or [])
    
    # 2. Laplacian variance
    gray = img.convert("L")
    gray_np = np.array(gray).astype(float)
    laplacian = np.abs(gray_np[1:-1, 1:-1] * 4 - gray_np[:-2, 1:-1] - gray_np[2:, 1:-1] - gray_np[1:-1, :-2] - gray_np[1:-1, 2:])
    variance = np.var(laplacian)
    
    # 3. Colors after converting to 16 colors palette
    quantized_16 = img.convert("P", palette=Image.Palette.ADAPTIVE, colors=16)
    colors_quant_16 = len(quantized_16.getcolors(maxcolors=256) or [])
    
    # 4. Colors after converting to 8 colors palette
    quantized_8 = img.convert("P", palette=Image.Palette.ADAPTIVE, colors=8)
    colors_quant_8 = len(quantized_8.getcolors(maxcolors=256) or [])
    
    print(f"[{name}] 16x16: {colors_nearest_16}, Var: {variance:.2f}, Q16: {colors_quant_16}, Q8: {colors_quant_8}")

print("\n--- ANALYZING REAL LEAF IMAGES ---")
files = [f for f in os.listdir(LEAVES_DIR) if f.lower().endswith((".jpg", ".jpeg", ".png"))][:10]
for f in files:
    path = os.path.join(LEAVES_DIR, f)
    img = Image.open(path)
    
    small_nearest = img.resize((16, 16), Image.NEAREST)
    colors_nearest_16 = len(small_nearest.getcolors(maxcolors=256) or [])
    
    gray = img.convert("L")
    gray_np = np.array(gray).astype(float)
    laplacian = np.abs(gray_np[1:-1, 1:-1] * 4 - gray_np[:-2, 1:-1] - gray_np[2:, 1:-1] - gray_np[1:-1, :-2] - gray_np[1:-1, 2:])
    variance = np.var(laplacian)
    
    quantized_16 = img.convert("P", palette=Image.Palette.ADAPTIVE, colors=16)
    colors_quant_16 = len(quantized_16.getcolors(maxcolors=256) or [])
    
    quantized_8 = img.convert("P", palette=Image.Palette.ADAPTIVE, colors=8)
    colors_quant_8 = len(quantized_8.getcolors(maxcolors=256) or [])
    
    print(f"[{f}] 16x16: {colors_nearest_16}, Var: {variance:.2f}, Q16: {colors_quant_16}, Q8: {colors_quant_8}")


