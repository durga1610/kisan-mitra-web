import os
import json

DATASET_DIR = "dataset"
CLASSES_JSON = "models/classes.json"
WORKSPACE_REPORT_PATH = "../Vulnerability Test Results/dataset_gap_report.md"
BRAIN_REPORT_PATH = "C:/Users/durga/.gemini/antigravity-ide/brain/ffa2701b-34c2-4911-b6a3-3afe2b289ce5/dataset_gap_report.md"

def main():
    if not os.path.exists(CLASSES_JSON):
        print(f"Error: {CLASSES_JSON} not found.")
        return
        
    with open(CLASSES_JSON, "r") as f:
        classes = json.load(f)
        
    splits = ["train", "val", "test"]
    class_stats = {c: {"real": 0, "synth": 0} for c in classes}
    
    for split in splits:
        split_path = os.path.join(DATASET_DIR, split)
        if not os.path.exists(split_path):
            continue
            
        for c in classes:
            c_dir = os.path.join(split_path, c)
            if os.path.exists(c_dir):
                files = os.listdir(c_dir)
                real_count = sum(1 for f in files if "real" in f)
                synth_count = sum(1 for f in files if "synth" in f)
                
                class_stats[c]["real"] += real_count
                class_stats[c]["synth"] += synth_count

    # Generate Markdown Content
    lines = []
    lines.append("# 📊 Kisan Mitra Disease Model Dataset Gap Analysis")
    lines.append("\nThis report inventories the current dataset classes, classifies them by sample origin (real-world vs. synthetic), identifies critical data gaps, and defines a dataset acquisition plan to improve model generalization.")
    lines.append("\n---")
    
    # 1. Classes count summary
    under_100 = []
    under_200 = []
    under_500 = []
    
    for c, stats in class_stats.items():
        total = stats["real"] + stats["synth"]
        if total < 100:
            under_100.append(c)
        if total < 200:
            under_200.append(c)
        if total < 500:
            under_500.append(c)
            
    lines.append("\n## 🔍 Gap Threshold Identification")
    lines.append(f"\n*   **Classes with < 100 images**: **{len(under_100)}** / {len(classes)} classes")
    lines.append(f"*   **Classes with < 200 images**: **{len(under_200)}** / {len(classes)} classes")
    lines.append(f"*   **Classes with < 500 images**: **{len(under_500)}** / {len(classes)} classes")
    
    lines.append("\n---")
    lines.append("\n## 📋 Detailed Class Inventory Table")
    lines.append("\n| Class Name | Real Image Count | Synthetic Image Count | Total Image Count | Status |")
    lines.append("| :--- | :---: | :---: | :---: | :--- |")
    
    for c in sorted(classes):
        stats = class_stats[c]
        total = stats["real"] + stats["synth"]
        
        status = "🔴 Extremely Low (<100)" if total < 100 else ("🟡 Medium (<200)" if total < 200 else "🟢 Good")
        # Overwrite status if real images are extremely low
        if stats["real"] == 0:
            status = "❌ Zero Real Images"
        elif stats["real"] < 20:
            status += " (Insufficient Real)"
            
        lines.append(f"| {c} | {stats['real']} | {stats['synth']} | {total} | {status} |")
        
    lines.append("\n---")
    lines.append("\n## 🚀 Recommended Real-World Datasets to Fill Gaps")
    lines.append("\nTo replace synthetic data with high-fidelity real-world farmer-style images, the following dataset sources are recommended for each crop:")
    lines.append("\n### 1. Potato, Tomato, Apple, Grape, Peach, Cherry, Pepper Bell, Strawberry")
    lines.append("*   **Source**: **spMohanty/PlantVillage-Dataset** (or CrowdAI PlantVillage)")
    lines.append("*   **Details**: Provides over 54,000 images of healthy and diseased leaves across 38 crop-disease pairs.")
    lines.append("*   **Action**: Use the existing `merge_plantvillage.py` script to fetch more samples from the raw color folders of this dataset on GitHub/Kaggle, raising the target count per class to at least **150+ real images**.")
    
    lines.append("\n### 2. Rice Leaf Diseases")
    lines.append("*   **Source**: **AveyBD/rice-leaf-diseases-detection** (GitHub) / Kaggle **Rice Leaf Diseases Dataset**")
    lines.append("*   **Details**: Contains real-world field photos of Rice Blast, Bacterial Leaf Blight, and Brown Spot.")
    lines.append("*   **Action**: Scale up downloading of these assets to include at least **100+ images per class**.")
    
    lines.append("\n### 3. Cotton Leaf Diseases")
    lines.append("*   **Source**: **Kaggle Cotton Disease Dataset** (e.g. by Akshay Kumar or Shirsh Mall)")
    lines.append("*   **Details**: Features real-world, mobile-captured images of Cotton Bacterial Blight, Cotton Leaf Curl, and Healthy Cotton Leaves.")
    lines.append("*   **Action**: Download and integrate this dataset into `dataset/train/Cotton*` to replace the 100% synthetic Cotton dataset.")
    
    lines.append("\n---")
    lines.append("\n## 📈 Target Acquisition Plan")
    lines.append("\n1.  **Phased Replacement**: Progressively remove all `synth_*.jpg` files from the dataset.")
    lines.append("2.  **Minimum Class Thresholds**: Target a minimum of **200 real images per class** for training, and **50 real images per class** for testing/validation splits.")
    lines.append("3.  **Real-World Image Augmentations**: Instead of using clean/synthetic shape generation, apply standard albumentations/torchvision augmentations (crops, perspective shifts, color jitter, sensor noise simulation) **only on real leaf images**.")

    report_content = "\n".join(lines)
    
    # Save to Workspace
    os.makedirs(os.path.dirname(WORKSPACE_REPORT_PATH), exist_ok=True)
    with open(WORKSPACE_REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report_content)
    print(f"Saved report to workspace: {WORKSPACE_REPORT_PATH}")
    
    # Save to Brain Artifacts
    os.makedirs(os.path.dirname(BRAIN_REPORT_PATH), exist_ok=True)
    with open(BRAIN_REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report_content)
    print(f"Saved report to brain: {BRAIN_REPORT_PATH}")

if __name__ == "__main__":
    main()
