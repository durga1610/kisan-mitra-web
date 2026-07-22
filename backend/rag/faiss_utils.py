import os
import sys
import json
import numpy as np
import faiss
import torch
from transformers import AutoTokenizer, AutoModel

# Base path configuration
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VECTOR_DB_DIR = os.path.join(BASE_DIR, "models", "vector_db")
DEFAULT_INDEX_PATH = os.path.join(VECTOR_DB_DIR, "faiss_index.bin")
DEFAULT_DOCS_PATH = os.path.join(VECTOR_DB_DIR, "documents.json")
DEFAULT_META_PATH = os.path.join(VECTOR_DB_DIR, "metadata.json")
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Singleton Caching
_FAISS_INDEX_CACHE = None
_DOCUMENTS_CACHE = None
_METADATA_CACHE = None
_QUERY_MODEL_CACHE = None
_QUERY_TOKENIZER_CACHE = None


def load_faiss_index(index_path=None, force_reload=False):
    """
    Loads and caches the FAISS vector index from binary file.
    """
    global _FAISS_INDEX_CACHE
    if _FAISS_INDEX_CACHE is not None and not force_reload:
        return _FAISS_INDEX_CACHE

    target_path = index_path or DEFAULT_INDEX_PATH
    if not os.path.exists(target_path):
        raise FileNotFoundError(f"FAISS index file not found at '{target_path}'. Run build_faiss_index.py first.")

    index = faiss.read_index(target_path)
    _FAISS_INDEX_CACHE = index
    return index


def load_documents_and_metadata(vector_db_dir=None, force_reload=False):
    """
    Loads and caches documents.json and metadata.json.
    """
    global _DOCUMENTS_CACHE, _METADATA_CACHE
    if _DOCUMENTS_CACHE is not None and _METADATA_CACHE is not None and not force_reload:
        return _DOCUMENTS_CACHE, _METADATA_CACHE

    db_dir = vector_db_dir or VECTOR_DB_DIR
    docs_path = os.path.join(db_dir, "documents.json")
    meta_path = os.path.join(db_dir, "metadata.json")

    if not os.path.exists(docs_path):
        raise FileNotFoundError(f"Documents file missing at '{docs_path}'.")
    if not os.path.exists(meta_path):
        raise FileNotFoundError(f"Metadata file missing at '{meta_path}'.")

    with open(docs_path, "r", encoding="utf-8") as f:
        documents = json.load(f)

    with open(meta_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    _DOCUMENTS_CACHE = documents
    _METADATA_CACHE = metadata
    return documents, metadata


def _get_query_model():
    """
    Lazy initialization for local Hugging Face model used in query vector encoding.
    """
    global _QUERY_MODEL_CACHE, _QUERY_TOKENIZER_CACHE
    if _QUERY_MODEL_CACHE is None or _QUERY_TOKENIZER_CACHE is None:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModel.from_pretrained(MODEL_NAME)
        model.eval()
        _QUERY_TOKENIZER_CACHE = tokenizer
        _QUERY_MODEL_CACHE = model
    return _QUERY_TOKENIZER_CACHE, _QUERY_MODEL_CACHE


def _mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0]
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)


def embed_query(query_text):
    """
    Converts input query string into L2-normalized 384-dimensional dense NumPy array.
    """
    if not query_text or not isinstance(query_text, str):
        raise ValueError("Query text must be a non-empty string.")

    tokenizer, model = _get_query_model()
    encoded_input = tokenizer([query_text], padding=True, truncation=True, max_length=512, return_tensors="pt")

    with torch.no_grad():
        model_output = model(**encoded_input)

    query_val = _mean_pooling(model_output, encoded_input["attention_mask"])
    query_val = torch.nn.functional.normalize(query_val, p=2, dim=1)
    return query_val.numpy().astype(np.float32)


def search_documents(query_embedding, top_k=5, index=None, documents=None):
    """
    Searches FAISS vector database using an input query embedding vector.

    Parameters:
    - query_embedding: NumPy array of shape (384,) or (1, 384)
    - top_k: Number of nearest neighbors to retrieve (default=5)
    - index: Preloaded FAISS index (optional)
    - documents: Preloaded documents list (optional)

    Returns:
    List of dictionaries containing document_id, similarity_score, metadata, and original document.
    """
    if index is None:
        index = load_faiss_index()

    if documents is None:
        documents, _ = load_documents_and_metadata()

    # Format query vector shape to (1, 384) float32
    query_vec = np.asarray(query_embedding, dtype=np.float32)
    if query_vec.ndim == 1:
        query_vec = np.expand_dims(query_vec, axis=0)

    if query_vec.shape[1] != 384:
        raise ValueError(f"Query vector dimension must be 384, got {query_vec.shape[1]}")

    # Normalize vector if needed
    norm = np.linalg.norm(query_vec[0])
    if norm > 0 and not np.isclose(norm, 1.0, atol=1e-3):
        query_vec = query_vec / norm

    # Execute FAISS Inner Product search
    top_k = min(top_k, index.ntotal)
    scores, indices = index.search(query_vec, top_k)

    results = []
    raw_scores = scores[0]
    raw_indices = indices[0]

    for rank in range(top_k):
        idx = int(raw_indices[rank])
        score = float(raw_scores[rank])

        if idx < 0 or idx >= len(documents):
            continue

        doc = documents[idx]
        result_item = {
            "document_id": doc.get("id", f"doc_{idx}"),
            "similarity_score": round(score, 4),
            "score": score,
            "rank": rank + 1,
            "category": doc.get("category", "general"),
            "title": doc.get("title", ""),
            "content": doc.get("content", ""),
            "keywords": doc.get("keywords", []),
            "related_crops": doc.get("related_crops", []),
            "source": doc.get("source", ""),
            "document": doc,
        }
        results.append(result_item)

    return results
