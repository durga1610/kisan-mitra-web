import os
import json
from typing import List, Dict, Any


def format_searchable_text(record: Dict[str, Any]) -> str:
    """
    Converts a structured knowledge base record into a single rich searchable text document.
    Combines Title, Category, Content, Keywords, and Related Crops.
    """
    title = record.get("title", "").strip()
    category = record.get("category", "").strip()
    content = record.get("content", "").strip()
    
    # Process keywords list or string
    raw_keywords = record.get("keywords", [])
    if isinstance(raw_keywords, list):
        keywords_str = ", ".join(str(k) for k in raw_keywords)
    else:
        keywords_str = str(raw_keywords)

    # Process related crops list or string
    raw_crops = record.get("related_crops", [])
    if isinstance(raw_crops, list):
        crops_str = ", ".join(str(c) for c in raw_crops)
    else:
        crops_str = str(raw_crops)

    searchable_doc = (
        f"Title: {title}\n"
        f"Category: {category}\n"
        f"Content: {content}\n"
        f"Keywords: {keywords_str}\n"
        f"Related Crops: {crops_str}"
    )
    return searchable_doc


def load_all_knowledge_base_records(kb_dir: str) -> List[Dict[str, Any]]:
    """
    Loads and merges all JSON records from all .json files in the knowledge_base directory.
    """
    if not os.path.exists(kb_dir):
        raise FileNotFoundError(f"Knowledge base directory not found at: {kb_dir}")

    all_records = []
    json_files = [f for f in os.listdir(kb_dir) if f.endswith(".json")]

    for file_name in sorted(json_files):
        file_path = os.path.join(kb_dir, file_name)
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                for item in data:
                    item["_source_file"] = file_name
                    all_records.append(item)

    return all_records
