import os
import json

CATEGORY_FILE_MAP = {
    "crop_profiles": "crop_profiles.json",
    "soil_knowledge": "soil_knowledge.json",
    "fertilizer_knowledge": "fertilizer_knowledge.json",
    "irrigation_knowledge": "irrigation_knowledge.json",
    "weather_advisory": "weather_advisory.json",
    "pest_disease_knowledge": "pest_disease_knowledge.json",
    "government_schemes": "government_schemes.json",
    "market_knowledge": "market_knowledge.json",
    "faq_dataset": "faq_dataset.json",
    "faq": "faq_dataset.json",
}

REQUIRED_SCHEMA_KEYS = [
    "id",
    "category",
    "title",
    "content",
    "keywords",
    "related_crops",
    "language",
    "source",
]


def export_record_to_knowledge_base(record, target_dir=None):
    """
    Appends a new record to the corresponding dataset JSON file in backend/knowledge_base/.
    Deduplicates records based on ID and Title. Preserves all existing records.

    Returns:
    tuple: (success: bool, message: str)
    """
    if not isinstance(record, dict):
        return False, "Record must be a valid JSON dictionary."

    # Validate Schema Keys
    for key in REQUIRED_SCHEMA_KEYS:
        if key not in record:
            return False, f"Missing required schema field: '{key}'"

    category = record.get("category", "crop_profiles").lower()
    target_filename = CATEGORY_FILE_MAP.get(category, "crop_profiles.json")

    if target_dir is None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        target_dir = os.path.abspath(os.path.join(current_dir, "..", "knowledge_base"))

    os.makedirs(target_dir, exist_ok=True)
    target_filepath = os.path.join(target_dir, target_filename)

    # Read existing records
    existing_records = []
    if os.path.exists(target_filepath):
        try:
            with open(target_filepath, "r", encoding="utf-8") as f:
                existing_records = json.load(f)
                if not isinstance(existing_records, list):
                    existing_records = []
        except Exception as e:
            existing_records = []

    # Check for Duplicate ID or Title
    rec_id = record["id"].strip().lower()
    rec_title = record["title"].strip().lower()

    for item in existing_records:
        existing_id = str(item.get("id", "")).strip().lower()
        existing_title = str(item.get("title", "")).strip().lower()

        if rec_id == existing_id:
            return False, f"Duplicate ID '{record['id']}' already exists in '{target_filename}'."
        if rec_title == existing_title:
            return False, f"Duplicate Title '{record['title']}' already exists in '{target_filename}'."

    # Append new record & write to file
    existing_records.append(record)

    with open(target_filepath, "w", encoding="utf-8") as f:
        json.dump(existing_records, f, indent=2, ensure_ascii=False)

    return True, f"Successfully appended record '{record['id']}' to '{target_filename}'."
