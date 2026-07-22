import os
import sys
import json
import time
from datetime import datetime
import numpy as np

# Absolute paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
KB_DIR = os.path.join(BASE_DIR, "knowledge_base")
VECTOR_DB_DIR = os.path.join(BASE_DIR, "models", "vector_db")

sys.path.insert(0, BASE_DIR)
from rag.embedding_utils import load_all_knowledge_base_records, format_searchable_text
from sentence_transformers import SentenceTransformer

def main():
    print(f"Loading KB from: {KB_DIR}")
    records = load_all_knowledge_base_records(KB_DIR)
    total_records = len(records)
    print(f"Loaded {total_records} records.")

    print("Loading SentenceTransformer model...")
    t0 = time.time()
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    print(f"Model loaded in {time.time() - t0:.2f}s")

    documents = []
    texts = []
    for idx, rec in enumerate(records):
        st = format_searchable_text(rec)
        texts.append(st)
        doc_entry = {
            "index": idx,
            "id": str(rec.get("id", f"doc_{idx}")),
            "category": str(rec.get("category", "general")),
            "title": str(rec.get("title", "")),
            "content": str(rec.get("content", "")),
            "keywords": rec.get("keywords", []),
            "related_crops": rec.get("related_crops", []),
            "language": str(rec.get("language", "en")),
            "source": str(rec.get("source", "Kisan Mitra Knowledge Base")),
            "searchable_text": st,
        }
        documents.append(doc_entry)

    print("Generating embeddings...")
    t1 = time.time()
    embeddings = model.encode(texts, show_progress_bar=False, normalize_embeddings=True, convert_to_numpy=True)
    gen_time = time.time() - t1

    print(f"Generated shape {embeddings.shape} in {gen_time:.2f}s")

    os.makedirs(VECTOR_DB_DIR, exist_ok=True)
    emb_path = os.path.join(VECTOR_DB_DIR, "embeddings.npy")
    doc_path = os.path.join(VECTOR_DB_DIR, "documents.json")
    meta_path = os.path.join(VECTOR_DB_DIR, "metadata.json")

    if os.path.exists(emb_path):
        os.remove(emb_path)
    np.save(emb_path, embeddings)

    with open(doc_path, "w", encoding="utf-8") as f:
        json.dump(documents, f, indent=2, ensure_ascii=False)

    metadata = {
        "model_name": "sentence-transformers/all-MiniLM-L6-v2",
        "embedding_dimension": int(embeddings.shape[1]),
        "total_records": total_records,
        "created_at": datetime.now().isoformat(),
        "total_generation_time_seconds": round(gen_time, 4),
        "avg_time_per_record_ms": round((gen_time / total_records) * 1000.0, 2),
        "files": {
            "embeddings": "embeddings.npy",
            "documents": "documents.json",
            "metadata": "metadata.json"
        }
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print("SUCCESSFULLY SAVED ALL ARTIFACTS!")
    print("emb_path exists:", os.path.exists(emb_path))
    print("doc_path exists:", os.path.exists(doc_path))
    print("meta_path exists:", os.path.exists(meta_path))

if __name__ == "__main__":
    main()
