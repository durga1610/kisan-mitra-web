import os
import sys
import glob
import json
import re
import subprocess
from datetime import datetime

# Add parent directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from importers.knowledge_importer import KnowledgeImporter, extract_keywords_and_crops

from importers.html_importer import parse_html_content
from importers.pdf_importer import parse_pdf_content
from importers.json_exporter import export_record_to_knowledge_base, CATEGORY_FILE_MAP


def extract_sections_from_content(title, content, source_name):
    """
    Splits large comprehensive guides into specialized sub-records for specific categories
    (e.g., Crop Profile, Fertilizer & Nutrient Management, Pest & Disease Management, Irrigation).
    """
    sections = []
    lines = content.splitlines()

    # Determine main crop name from title
    crop_match = re.search(r"\b(Rice|Cotton|Banana|Mango|Groundnut|Sugarcane|Wheat|Maize|Corn)\b", title, re.IGNORECASE)
    crop_name = crop_match.group(1).title() if crop_match else "General Crop"

    # Section accumulators
    cur_cat = "crop_profiles"
    cur_title = title
    cur_lines = []

    def flush_section():
        if cur_lines:
            text = "\n".join(cur_lines).strip()
            if len(text) > 80:
                # Generate specific sub-record title
                if cur_cat == "pest_disease_knowledge":
                    sub_title = f"{crop_name} Pest & Disease Management Guide"
                elif cur_cat == "fertilizer_knowledge":
                    sub_title = f"{crop_name} Fertilizer & Nutrient Management Guide"
                elif cur_cat == "irrigation_knowledge":
                    sub_title = f"{crop_name} Irrigation & Water Management Guide"
                elif cur_cat == "soil_knowledge":
                    sub_title = f"{crop_name} Suitable Soil & Land Preparation"
                else:
                    sub_title = f"{crop_name} Crop Profile & Cultivation Guide"

                sections.append({
                    "category": cur_cat,
                    "title": sub_title,
                    "content": text,
                    "source": source_name,
                    "crop_name": crop_name
                })

    for line in lines:
        line_lower = line.lower()

        # Category Section Heading Detectors
        if any(h in line_lower for h in ["pest management", "disease management", "insect control", "ipm", "fungal disease", "weed management"]):
            flush_section()
            cur_cat = "pest_disease_knowledge"
            cur_lines = [line]
        elif any(h in line_lower for h in ["fertilizer", "nutrient management", "npk", "urea", "manure application", "dap dose"]):
            flush_section()
            cur_cat = "fertilizer_knowledge"
            cur_lines = [line]
        elif any(h in line_lower for h in ["irrigation", "water requirement", "watering schedule", "drip irrigation"]):
            flush_section()
            cur_cat = "irrigation_knowledge"
            cur_lines = [line]
        elif any(h in line_lower for h in ["soil", "land preparation", "soil type", "ph requirement"]):
            flush_section()
            cur_cat = "soil_knowledge"
            cur_lines = [line]
        else:
            cur_lines.append(line)

    flush_section()

    if not sections:
        sections.append({
            "category": "crop_profiles",
            "title": title,
            "content": content,
            "source": source_name,
            "crop_name": crop_name
        })

    return sections


def run_batch_import(input_dir=None):
    """
    Executes batch import across all HTML and PDF files in backend/importers/inputs/.
    Rebuilds vector database embeddings and FAISS index post-import.
    """
    if input_dir is None:
        input_dir = os.path.join(current_dir, "inputs")

    kb_dir = os.path.abspath(os.path.join(current_dir, "..", "knowledge_base"))

    print("=" * 80)
    print(" KISAN MITRA: BATCH AGRICULTURAL KNOWLEDGE IMPORTER")
    print("=" * 80)
    print(f"Input Directory         : {input_dir}")
    print(f"Target Knowledge Base   : {kb_dir}")
    print("=" * 80)

    # 1. Count pre-import records
    pre_counts = {}
    for cat, filename in CATEGORY_FILE_MAP.items():
        filepath = os.path.join(kb_dir, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    pre_counts[filename] = len(data) if isinstance(data, list) else 0
            except Exception:
                pre_counts[filename] = 0
        else:
            pre_counts[filename] = 0

    total_pre_records = sum(pre_counts.values())

    # 2. Gather Files
    html_files = [f for f in glob.glob(os.path.join(input_dir, "*.html")) if not f.endswith("_files")]
    pdf_files = glob.glob(os.path.join(input_dir, "*.pdf"))

    print(f"\nDiscovered {len(html_files)} HTML guides and {len(pdf_files)} PDF guides.")
    print("-" * 80)

    importer = KnowledgeImporter()

    records_added = 0
    duplicates_skipped = 0
    html_processed = 0
    pdf_processed = 0

    # Process HTML Guides
    for html_path in sorted(html_files):
        filename = os.path.basename(html_path)
        print(f"\n[Processing HTML]: '{filename}'")
        title, content = parse_html_content(html_path)

        source_name = f"TNAU Agriportal / ICAR ({filename})"
        sections = extract_sections_from_content(title, content, source_name)

        for sec in sections:
            # Format & Export via Knowledge Importer
            rec_title = sec["title"]
            rec_cat = sec["category"]
            rec_content = sec["content"]

            keywords, crops = extract_keywords_and_crops(rec_title + " " + rec_content)
            clean_crop = sec["crop_name"]
            if clean_crop not in crops and clean_crop != "General Crop":
                crops.append(clean_crop)

            slug = re.sub(r"[^a-zA-Z0-9]", "_", rec_title.lower()).strip("_")
            rec_id = f"{rec_cat[:4]}_{slug[:40]}"

            record = {
                "id": rec_id,
                "category": rec_cat,
                "title": rec_title,
                "content": rec_content,
                "keywords": keywords,
                "related_crops": crops,
                "language": "en",
                "source": source_name
            }

            success, msg = export_record_to_knowledge_base(record, target_dir=kb_dir)
            if success:
                records_added += 1
                print(f"  + Added [{rec_cat}]: '{rec_title}'")
            else:
                duplicates_skipped += 1
                print(f"  - Skipped (Duplicate): '{rec_title}'")

        html_processed += 1

    # Process PDF Guides
    for pdf_path in sorted(pdf_files):
        filename = os.path.basename(pdf_path)
        print(f"\n[Processing PDF]: '{filename}'")
        title, content = parse_pdf_content(pdf_path)

        source_name = f"ICAR IPM Manual ({filename})"
        sections = extract_sections_from_content(title, content, source_name)

        for sec in sections:
            rec_title = sec["title"]
            rec_cat = sec["category"]
            rec_content = sec["content"]

            keywords, crops = extract_keywords_and_crops(rec_title + " " + rec_content)
            clean_crop = sec["crop_name"]
            if clean_crop not in crops and clean_crop != "General Crop":
                crops.append(clean_crop)

            slug = re.sub(r"[^a-zA-Z0-9]", "_", rec_title.lower()).strip("_")
            rec_id = f"{rec_cat[:4]}_{slug[:40]}"

            record = {
                "id": rec_id,
                "category": rec_cat,
                "title": rec_title,
                "content": rec_content,
                "keywords": keywords,
                "related_crops": crops,
                "language": "en",
                "source": source_name
            }

            success, msg = export_record_to_knowledge_base(record, target_dir=kb_dir)
            if success:
                records_added += 1
                print(f"  + Added [{rec_cat}]: '{rec_title}'")
            else:
                duplicates_skipped += 1
                print(f"  - Skipped (Duplicate): '{rec_title}'")

        pdf_processed += 1

    # Count post-import records
    post_counts = {}
    for cat, filename in CATEGORY_FILE_MAP.items():
        filepath = os.path.join(kb_dir, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    post_counts[filename] = len(data) if isinstance(data, list) else 0
            except Exception:
                post_counts[filename] = 0
        else:
            post_counts[filename] = 0

    total_post_records = sum(post_counts.values())

    print("\n" + "=" * 80)
    print(" BATCH KNOWLEDGE IMPORT SUMMARY REPORT")
    print("=" * 80)
    print(f"  |- HTML Files Processed      : {html_processed}")
    print(f"  |- PDF Files Processed       : {pdf_processed}")
    print(f"  |- New Records Added         : {records_added}")
    print(f"  |- Duplicate Records Skipped : {duplicates_skipped}")
    print(f"  |- Baseline Records Count    : {total_pre_records}")
    print(f"  |- Updated Total Records     : {total_post_records}")
    print("-" * 80)
    print("  Knowledge Base Dataset File Breakdown:")
    for fname, count in post_counts.items():
        diff = count - pre_counts.get(fname, 0)
        print(f"   * {fname:30s}: {count:3d} records ({'+' if diff >= 0 else ''}{diff} new)")
    print("=" * 80)

    # 3. Post-Import Vector DB Update (STEP 9)
    print("\n[Post-Import Vector DB Update]: Regenerating Embeddings & FAISS Index...")
    print("-" * 80)

    rag_dir = os.path.abspath(os.path.join(current_dir, "..", "rag"))
    build_emb_script = os.path.join(rag_dir, "build_embeddings.py")
    build_faiss_script = os.path.join(rag_dir, "build_faiss_index.py")

    print(f"Running: python {build_emb_script}")
    emb_proc = subprocess.run([sys.executable, build_emb_script], capture_output=True, text=True)
    if emb_proc.returncode == 0:
        print(" -> Embeddings regeneration SUCCESSFUL!")
    else:
        print(f" -> Embeddings regeneration ERROR: {emb_proc.stderr}")

    print(f"Running: python {build_faiss_script}")
    faiss_proc = subprocess.run([sys.executable, build_faiss_script], capture_output=True, text=True)
    if faiss_proc.returncode == 0:
        print(" -> FAISS binary index rebuild SUCCESSFUL!")
    else:
        print(f" -> FAISS rebuild ERROR: {faiss_proc.stderr}")

    print("\n" + "=" * 80)
    print(" BATCH IMPORT & RAG VECTOR DB REBUILD COMPLETED SUCCESSFULLY!")
    print("=" * 80)

    return {
        "html_processed": html_processed,
        "pdf_processed": pdf_processed,
        "records_added": records_added,
        "duplicates_skipped": duplicates_skipped,
        "baseline_total_records": total_pre_records,
        "updated_total_records": total_post_records,
        "category_counts": post_counts,
        "embeddings_status": "SUCCESS" if emb_proc.returncode == 0 else "FAILED",
        "faiss_status": "SUCCESS" if faiss_proc.returncode == 0 else "FAILED",
    }


if __name__ == "__main__":
    try:
        run_batch_import()
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)
