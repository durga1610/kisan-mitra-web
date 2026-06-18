import os
import sys
import json

WORKSPACE_DIR = r"c:\Users\durga\kisan_mitra"
DATASET_DIR = os.path.join(WORKSPACE_DIR, "dataset")
CLASSES_PATH = os.path.join(WORKSPACE_DIR, "backend", "models", "classes.json")

def main():
    # Load class list
    with open(CLASSES_PATH, "r") as f:
        classes = json.load(f)

    splits = ["train", "val", "test"]
    stats = {}

    # Initialise stats for each class
    for cls in classes:
        stats[cls] = {
            "train": 0,
            "val": 0,
            "test": 0,
            "type": "Real" # Default, will detect based on priority crops list
        }

    # Count files
    for split in splits:
        split_dir = os.path.join(DATASET_DIR, split)
        if not os.path.exists(split_dir):
            print(f"Warning: Split folder {split_dir} does not exist.")
            continue
        for cls in classes:
            cls_dir = os.path.join(split_dir, cls)
            if os.path.exists(cls_dir):
                files = [f for f in os.listdir(cls_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
                stats[cls][split] = len(files)

    # Determine real or synthetic. 
    # Priority Crops are Rice, Cotton, Grape, Tomato, Potato (all real).
    # Others are non-priority crops which are legacy (containing synthetic).
    priority_crops = ["Rice", "Cotton", "Grape", "Tomato", "Potato"]
    for cls in classes:
        crop = cls.split("___")[0]
        if crop in priority_crops:
            stats[cls]["type"] = "Real (Rebuilt)"
        else:
            stats[cls]["type"] = "Synthetic (Legacy)"

    # Identify largest training class count
    max_train_count = max(stats[cls]["train"] for cls in classes)
    
    # Calculate imbalance ratio relative to largest class (max_train_count / class_train_count)
    # If count is 0, ratio is inf.
    for cls in classes:
        train_cnt = stats[cls]["train"]
        if train_cnt > 0:
            stats[cls]["ratio"] = max_train_count / train_cnt
        else:
            stats[cls]["ratio"] = float('inf')

    # Output report
    report = []
    report.append("="*90)
    report.append(f"{'Class Name':<35} | {'Train':<5} | {'Val':<5} | {'Test':<5} | {'Type':<18} | {'Imbalance Ratio':<15}")
    report.append("="*90)
    
    for cls in classes:
        s = stats[cls]
        ratio_str = f"{s['ratio']:.2f}x" if s['ratio'] != float('inf') else "inf"
        report.append(f"{cls:<35} | {s['train']:<5d} | {s['val']:<5d} | {s['test']:<5d} | {s['type']:<18} | {ratio_str:<15}")
        
    print("\n".join(report))

    # Save details to json for easier downstream processing if needed
    with open("dataset_gap_stats.json", "w") as f:
        json.dump(stats, f, indent=2)

if __name__ == "__main__":
    main()
