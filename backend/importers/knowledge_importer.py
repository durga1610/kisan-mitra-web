import os
import sys
import re
import argparse
from datetime import datetime

# Add parent directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from importers.html_importer import parse_html_content
from importers.pdf_importer import parse_pdf_content
from importers.json_exporter import export_record_to_knowledge_base

# Lexicon for automatic keyword and crop matching
CROPS_LEXICON = [
    "rice", "wheat", "maize", "corn", "cotton", "jute", "sugarcane", "tobacco",
    "groundnut", "mustard", "soybean", "chickpea", "pigeonpeas", "kidneybeans",
    "mothbeans", "mungbean", "blackgram", "lentil", "pomegranate", "banana",
    "mango", "grapes", "watermelon", "muskmelon", "apple", "orange", "papaya",
    "coconut", "spinach", "tomato", "potato", "onion", "garlic", "chilli"
]

KEYWORDS_LEXICON = [
    "fertilizer", "urea", "dap", "npk", "mop", "nitrogen", "phosphorus", "potassium",
    "irrigation", "drip", "sprinkler", "waterlogging", "drainage", "soil", "clay",
    "alluvial", "loam", "black soil", "red soil", "ph", "pest", "disease", "fungus",
    "fungicide", "pesticide", "blast", "rust", "blight", "borer", "harvest", "sowing",
    "transplanting", "rabi", "kharif", "zaid", "yield", "seed rate", "scheme", "msp"
]


def detect_category(title, content):
    """
    Automatically detects the knowledge base category from document title and text.
    """
    text = (title + " " + content).lower()

    if any(k in text for k in ["pest", "disease", "fungus", "blast", "rust", "blight", "borer", "insect", "fungicide", "pesticide"]):
        return "pest_disease_knowledge"

    if any(k in text for k in ["fertilizer", "urea", "dap", "mop", "npk", "manure", "nutrient dose"]):
        return "fertilizer_knowledge"

    if any(k in text for k in ["irrigate", "irrigation", "drip", "sprinkler", "water requirement", "watering"]):
        return "irrigation_knowledge"

    if any(k in text for k in ["soil", "black soil", "red soil", "alluvial", "clay loam", "ph level", "soil fertility"]):
        return "soil_knowledge"

    if any(k in text for k in ["scheme", "pm-kisan", "pmfby", "subsidies", "yojana", "kcc"]):
        return "government_schemes"

    if any(k in text for k in ["mandi", "msp", "market price", "procurement", "e-nam"]):
        return "market_knowledge"

    if any(k in text for k in ["weather", "rainfall", "drought", "frost", "cold wave", "heatwave", "humidity"]):
        return "weather_advisory"

    if any(k in text for k in ["faq", "frequently asked questions", "question", "how to"]):
        return "faq_dataset"

    return "crop_profiles"


def extract_keywords_and_crops(text):
    """
    Extracts relevant agricultural keywords and related crops from text.
    """
    text_lower = text.lower()

    found_crops = set()
    for crop in CROPS_LEXICON:
        if re.search(r"\b" + re.escape(crop) + r"\b", text_lower):
            found_crops.add(crop.title())

    found_keywords = set()
    for kw in KEYWORDS_LEXICON:
        if re.search(r"\b" + re.escape(kw) + r"\b", text_lower):
            found_keywords.add(kw)

    return sorted(list(found_keywords)), sorted(list(found_crops))


def generate_unique_id(title, category):
    """
    Generates a clean schema-compliant ID prefix string.
    """
    clean_title = re.sub(r"[^a-zA-Z0-9\s]", "", title.lower()).strip()
    words = clean_title.split()[:4]
    short_slug = "_".join(words) if words else "guide"

    prefix = "guide"
    if category == "crop_profiles":
        prefix = "crop"
    elif category == "pest_disease_knowledge":
        prefix = "pest"
    elif category == "fertilizer_knowledge":
        prefix = "fert"
    elif category == "irrigation_knowledge":
        prefix = "irr"
    elif category == "soil_knowledge":
        prefix = "soil"
    elif category == "government_schemes":
        prefix = "scheme"
    elif category == "market_knowledge":
        prefix = "market"
    elif category == "weather_advisory":
        prefix = "weather"

    return f"{prefix}_{short_slug}"


class KnowledgeImporter:
    """
    Master Agricultural Knowledge Importer supporting HTML, PDF, and TXT guides.
    """

    def import_file(self, file_path_or_content, source="ICAR / TNAU Agriportal", category=None, language="en"):
        """
        Parses document, extracts metadata, formats schema record, and exports to knowledge base.
        """
        if os.path.exists(file_path_or_content) and os.path.isfile(file_path_or_content):
            ext = os.path.splitext(file_path_or_content)[1].lower()
            file_path = file_path_or_content

            if ext in [".html", ".htm"]:
                title, content = parse_html_content(file_path)
            elif ext == ".pdf":
                title, content = parse_pdf_content(file_path)
            else:
                # Plain Text file
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    raw_txt = f.read()
                title = os.path.splitext(os.path.basename(file_path))[0].replace("_", " ").title()
                content = re.sub(r"[ \t]+", " ", raw_txt).strip()
        else:
            # Direct string content
            raw_text = file_path_or_content
            if "<html" in raw_text.lower() or "<body" in raw_text.lower():
                title, content = parse_html_content(raw_text)
            else:
                lines = [l.strip() for l in raw_text.splitlines() if l.strip()]
                title = lines[0] if lines else "Agricultural Guide"
                content = "\n".join(lines)

        # Detect category if not provided
        detected_category = category or detect_category(title, content)

        # Extract Keywords and Crops
        keywords, related_crops = extract_keywords_and_crops(title + " " + content)

        # Generate Unique Schema ID
        record_id = generate_unique_id(title, detected_category)

        # Build Standard Schema Record
        record = {
            "id": record_id,
            "category": detected_category,
            "title": title,
            "content": content,
            "keywords": keywords,
            "related_crops": related_crops,
            "language": language,
            "source": source,
        }

        # Export Record to Knowledge Base (Non-destructive append)
        success, msg = export_record_to_knowledge_base(record)

        return {
            "success": success,
            "message": msg,
            "record_id": record_id,
            "category": detected_category,
            "record": record if success else None,
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kisan Mitra Agricultural Knowledge Importer CLI")
    parser.add_argument("--file", type=str, required=True, help="Path to HTML, PDF, or TXT agricultural guide")
    parser.add_argument("--source", type=str, default="ICAR / TNAU Agriportal", help="Official source attribution string")
    parser.add_argument("--category", type=str, default=None, help="Target knowledge category")
    parser.add_argument("--language", type=str, default="en", help="Language code (default: en)")

    args = parser.parse_args()

    importer = KnowledgeImporter()
    res = importer.import_file(args.file, source=args.source, category=args.category, language=args.language)

    print("=" * 80)
    print(" KISAN MITRA KNOWLEDGE IMPORTER EXECUTION RESULT")
    print("=" * 80)
    print(f"Status      : {'SUCCESS' if res['success'] else 'SKIPPED / FAILED'}")
    print(f"Message     : {res['message']}")
    print(f"Record ID   : {res['record_id']}")
    print(f"Category    : {res['category']}")
    print("=" * 80)
