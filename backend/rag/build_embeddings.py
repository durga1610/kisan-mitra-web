import os
import sys
import time
import json
from datetime import datetime
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel

# Add parent directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from rag.embedding_utils import load_all_knowledge_base_records, format_searchable_text

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0]
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)


def generate_knowledge_embeddings():
    print("=" * 60)
    print(" KISAN MITRA: RAG SEMANTIC EMBEDDING GENERATION")
    print("=" * 60)

    base_dir = parent_dir
    kb_dir = os.path.join(base_dir, "knowledge_base")
    vector_db_dir = os.path.join(base_dir, "models", "vector_db")
    os.makedirs(vector_db_dir, exist_ok=True)

    print(f"* Loading knowledge base from: {kb_dir}")
    records = load_all_knowledge_base_records(kb_dir)
    total_records = len(records)
    print(f"* Loaded {total_records} total knowledge base records.")

    print(f"\n* Initializing Hugging Face Transformers model: '{MODEL_NAME}'...")
    model_load_start = time.perf_counter()
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModel.from_pretrained(MODEL_NAME)
    model.eval()
    model_load_time = time.perf_counter() - model_load_start
    print(f"* Model loaded in {model_load_time:.2f} seconds.")

    print("\n* Formatting searchable texts and building document list...")
    documents = []
    texts_to_encode = []

    for idx, rec in enumerate(records):
        searchable_text = format_searchable_text(rec)
        texts_to_encode.append(searchable_text)

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
            "searchable_text": searchable_text,
        }
        documents.append(doc_entry)

    print(f"\n* Generating 384-dimensional embeddings for {total_records} records...")
    gen_start_time = time.perf_counter()

    all_embeddings = []
    batch_size = 16

    for i in range(0, total_records, batch_size):
        batch_texts = texts_to_encode[i : i + batch_size]
        encoded_input = tokenizer(batch_texts, padding=True, truncation=True, max_length=512, return_tensors="pt")

        with torch.no_grad():
            model_output = model(**encoded_input)

        sentence_embeddings = mean_pooling(model_output, encoded_input["attention_mask"])
        sentence_embeddings = torch.nn.functional.normalize(sentence_embeddings, p=2, dim=1)
        all_embeddings.append(sentence_embeddings.numpy())

    embeddings = np.vstack(all_embeddings)
    total_gen_time = time.perf_counter() - gen_start_time
    avg_time_per_record = (total_gen_time / total_records) * 1000.0 if total_records > 0 else 0.0
    embedding_dim = int(embeddings.shape[1])

    print("\n" + "=" * 60)
    print(" EMBEDDING GENERATION STATISTICS")
    print("=" * 60)
    print(f"  |- Total Knowledge Records : {total_records}")
    print(f"  |- Embedding Model          : {MODEL_NAME}")
    print(f"  |- Embedding Dimension      : {embedding_dim}")
    print(f"  |- Total Generation Time    : {total_gen_time:.3f} seconds")
    print(f"  |- Avg Time Per Record      : {avg_time_per_record:.2f} ms")
    print(f"  |- Output Array Shape       : {embeddings.shape}")
    print(f"  |- Sample Index 0 Norm     : {np.linalg.norm(embeddings[0]):.4f}")

    # Save Artifacts
    embeddings_path = os.path.join(vector_db_dir, "embeddings.npy")
    documents_path = os.path.join(vector_db_dir, "documents.json")
    metadata_path = os.path.join(vector_db_dir, "metadata.json")

    print("\n* Saving vector database artifacts...")
    with open(embeddings_path, "wb") as f_emb:
        np.save(f_emb, embeddings)

    with open(documents_path, "w", encoding="utf-8") as f:
        json.dump(documents, f, indent=2, ensure_ascii=False)

    metadata = {
        "model_name": MODEL_NAME,
        "embedding_dimension": embedding_dim,
        "total_records": total_records,
        "created_at": datetime.now().isoformat(),
        "total_generation_time_seconds": round(total_gen_time, 4),
        "avg_time_per_record_ms": round(avg_time_per_record, 2),
        "files": {
            "embeddings": "embeddings.npy",
            "documents": "documents.json",
            "metadata": "metadata.json",
        },
    }

    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f" [+] Saved Embeddings : {embeddings_path}")
    print(f" [+] Saved Documents  : {documents_path}")
    print(f" [+] Saved Metadata   : {metadata_path}")

    print("\nSemantic embeddings generated and saved successfully!")
    return {
        "total_records": total_records,
        "embedding_dimension": embedding_dim,
        "model_name": MODEL_NAME,
        "total_gen_time": total_gen_time,
        "avg_time_per_record_ms": avg_time_per_record,
    }


if __name__ == "__main__":
    try:
        generate_knowledge_embeddings()
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)
