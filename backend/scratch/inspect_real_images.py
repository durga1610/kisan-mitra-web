import os

def main():
    dataset_dir = "dataset"
    splits = ["train", "val", "test"]
    
    for split in splits:
        split_path = os.path.join(dataset_dir, split)
        if not os.path.exists(split_path):
            print(f"Directory not found: {split_path}")
            continue
            
        print(f"\n--- Split: {split} ---")
        subdirs = sorted([d for d in os.listdir(split_path) if os.path.isdir(os.path.join(split_path, d))])
        
        crop_counts = {}
        for d in subdirs:
            crop = d.split("___")[0]
            d_path = os.path.join(split_path, d)
            files = os.listdir(d_path)
            
            real_count = sum(1 for f in files if "real" in f)
            synth_count = sum(1 for f in files if "synth" in f)
            
            if crop not in crop_counts:
                crop_counts[crop] = {"real": 0, "synth": 0}
            crop_counts[crop]["real"] += real_count
            crop_counts[crop]["synth"] += synth_count
            
        for crop, counts in crop_counts.items():
            print(f"  {crop:<12} | Real: {counts['real']:<4} | Synth: {counts['synth']:<4} | Total: {counts['real'] + counts['synth']}")

if __name__ == "__main__":
    main()
