import os
import sys
import numpy as np
from PIL import Image

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import main

def scan():
    main.init_disease_model()
    folder = r"c:\Users\durga\kisan_mitra\dataset\test\Potato___Late_Blight"
    print(f"Scanning {folder} for quality_score close to 93.62%...")
    
    for fname in os.listdir(folder):
        fpath = os.path.join(folder, fname)
        if not fname.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            continue
        try:
            image = Image.open(fpath)
            ok, msg, q_score = main.check_image_quality(image)
            if abs(q_score - 93.62) < 0.5:
                print(f"File: {fname} | Quality Score: {q_score:.4f}% | Passed: {ok}")
        except Exception as e:
            pass

if __name__ == "__main__":
    scan()
