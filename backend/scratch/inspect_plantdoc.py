from datasets import load_dataset
import os

print("Loading PlantDoc dataset...")
try:
    dataset = load_dataset("agyaatcoder/PlantDoc", trust_remote_code=True)
    print("Dataset loaded successfully!")
    print("Splits:", list(dataset.keys()))
    
    # inspect train split
    train_data = dataset["train"]
    print("Number of images in train:", len(train_data))
    
    # Print a few examples features
    print("Features:", train_data.features)
    
    # Count classes
    classes_count = {}
    for i in range(min(500, len(train_data))):
        item = train_data[i]
        # check if it has labels or tags
        for label_id in item.get("objects", {}).get("category", []):
            label = train_data.features["objects"].feature["category"].int2str(label_id)
            classes_count[label] = classes_count.get(label, 0) + 1
            
    print("Some classes in first 500 items:")
    for k, v in sorted(classes_count.items()):
        print(f"  {k}: {v}")
except Exception as e:
    print("Error:", e)
