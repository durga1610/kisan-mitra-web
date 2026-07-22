import os
import json


def validate():
    kb_dir = os.path.dirname(os.path.abspath(__file__))
    required_keys = {"id", "category", "title", "content", "keywords", "related_crops", "language", "source"}
    
    files = [f for f in os.listdir(kb_dir) if f.endswith(".json")]
    print(f"Found {len(files)} JSON knowledge base files in {kb_dir}:")
    
    total_records = 0
    for file_name in sorted(files):
        file_path = os.path.join(kb_dir, file_name)
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        if not isinstance(data, list):
            raise ValueError(f"File {file_name} must contain a top-level JSON array of objects.")
            
        print(f"  - {file_name:30s}: {len(data)} records")
        total_records += len(data)
        
        for idx, item in enumerate(data):
            missing = required_keys - set(item.keys())
            if missing:
                raise ValueError(f"File {file_name} item #{idx} (id={item.get('id')}) is missing keys: {missing}")
                
    print("=" * 60)
    print(f"All {len(files)} knowledge base files validated successfully! Total records: {total_records}")


if __name__ == "__main__":
    validate()
