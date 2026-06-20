import os
import sys
import torch
import numpy as np
from PIL import Image

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import main
from disease_transforms import DISEASE_TRANSFORM as inference_transforms

def main_run():
    main.init_disease_model()
    
    s_dir = r"C:\Users\durga\.gemini\antigravity-ide\brain\ffa2701b-34c2-4911-b6a3-3afe2b289ce5\.tempmediaStorage"
    print(f"Analyzing all files in {s_dir}...")
    
    for fname in os.listdir(s_dir):
        fpath = os.path.join(s_dir, fname)
        if not fpath.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            continue
            
        try:
            image = Image.open(fpath)
            quality_ok, msg, q_score = main.check_image_quality(image)
            
            tensor_img = inference_transforms(image).unsqueeze(0)
            with torch.no_grad():
                outputs = main.DISEASE_MODEL(tensor_img)
                probs = torch.softmax(outputs, dim=1)[0]
                top_prob, top_idx = torch.max(probs, dim=0)
                pred_class = main.CLASSES[top_idx.item()]
                confidence = top_prob.item() * 100
                
                print(f"File: {fname} | Quality Score: {q_score:.2f}% | Class: {pred_class} | Confidence: {confidence:.2f}%")
        except Exception as e:
            import traceback
            traceback.print_exc()
            break

if __name__ == "__main__":
    main_run()
