import os
import sys
import json
import logging
import numpy as np
import faiss
import onnxruntime as ort
from transformers import AutoTokenizer

logger = logging.getLogger(__name__)

# Base path configuration
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VECTOR_DB_DIR = os.path.join(BASE_DIR, "models", "vector_db")
DEFAULT_INDEX_PATH = os.path.join(VECTOR_DB_DIR, "faiss_index.bin")
DEFAULT_DOCS_PATH = os.path.join(VECTOR_DB_DIR, "documents.json")
DEFAULT_META_PATH = os.path.join(VECTOR_DB_DIR, "metadata.json")
ONNX_MODEL_PATH = os.path.join(VECTOR_DB_DIR, "all-MiniLM-L6-v2.onnx")
EMBEDDING_DIMENSION = 384

# Singleton Caching
_FAISS_INDEX_CACHE = None
_DOCUMENTS_CACHE = None
_METADATA_CACHE = None
_ONNX_SESSION_CACHE = None
_ONNX_TOKENIZER_CACHE = None


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


def _get_onnx_session():
    """
    Loads and caches ONNX Runtime CPU InferenceSession and Tokenizer once at startup.
    Zero PyTorch runtime dependency during query embedding generation.
    """
    global _ONNX_SESSION_CACHE, _ONNX_TOKENIZER_CACHE
    if _ONNX_SESSION_CACHE is None or _ONNX_TOKENIZER_CACHE is None:
        if not os.path.exists(ONNX_MODEL_PATH):
            raise FileNotFoundError(f"ONNX model file missing at '{ONNX_MODEL_PATH}'. Run export_onnx_model.py first.")

        # Load local tokenizer from VECTOR_DB_DIR or fallback to hub ID
        if os.path.exists(os.path.join(VECTOR_DB_DIR, "tokenizer_config.json")):
            tokenizer = AutoTokenizer.from_pretrained(VECTOR_DB_DIR)
        else:
            tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

        opts = ort.SessionOptions()
        opts.intra_op_num_threads = 1
        opts.inter_op_num_threads = 1
        session = ort.InferenceSession(ONNX_MODEL_PATH, sess_options=opts, providers=["CPUExecutionProvider"])

        _ONNX_TOKENIZER_CACHE = tokenizer
        _ONNX_SESSION_CACHE = session

        startup_msg = (
            f"[Embedding Backend] Engine: ONNX Runtime CPU | "
            f"Model: all-MiniLM-L6-v2.onnx | "
            f"Dimension: {EMBEDDING_DIMENSION} | "
            f"Status: ONNX Loaded Successfully"
        )
        print(startup_msg)
        logger.info(startup_msg)

    return _ONNX_TOKENIZER_CACHE, _ONNX_SESSION_CACHE


def embed_query(query_text: str) -> np.ndarray:
    """
    Converts query text into a 384-dimensional L2-normalized vector using ONNX Runtime CPU.
    Zero PyTorch computational footprint.
    """
    if not query_text or not isinstance(query_text, str):
        raise ValueError("Query text must be a non-empty string.")

    tokenizer, session = _get_onnx_session()
    encoded = tokenizer([query_text], padding=True, truncation=True, max_length=128, return_tensors="np")

    inputs = {
        "input_ids": encoded["input_ids"].astype(np.int64),
        "attention_mask": encoded["attention_mask"].astype(np.int64),
        "token_type_ids": encoded.get("token_type_ids", np.zeros_like(encoded["input_ids"])).astype(np.int64),
    }

    # Execute ONNX CPU Inference
    outputs = session.run(None, inputs)
    last_hidden_state = outputs[0]  # Shape: (1, seq_len, 384)

    # Pure NumPy Mean Pooling
    attention_mask = encoded["attention_mask"]
    input_mask_expanded = np.expand_dims(attention_mask, -1).astype(np.float32)
    sum_embeddings = np.sum(last_hidden_state * input_mask_expanded, axis=1)
    sum_mask = np.clip(input_mask_expanded.sum(axis=1), a_min=1e-9, a_max=None)
    mean_pooled = sum_embeddings / sum_mask

    # Pure NumPy L2 Normalization
    norm = np.linalg.norm(mean_pooled, axis=1, keepdims=True)
    norm = np.where(norm == 0, 1e-9, norm)
    query_vector = (mean_pooled / norm).astype(np.float32)

    return query_vector


def search_documents(query_embedding, top_k=5, index=None, documents=None):
    """
    Searches FAISS vector database using an input query embedding vector.
    """
    if index is None:
        index = load_faiss_index()

    if documents is None:
        documents, _ = load_documents_and_metadata()

    # Format query vector shape to (1, 384) float32
    query_vec = np.asarray(query_embedding, dtype=np.float32)
    if query_vec.ndim == 1:
        query_vec = np.expand_dims(query_vec, axis=0)

    if query_vec.shape[1] != EMBEDDING_DIMENSION:
        raise ValueError(f"Query vector dimension must be {EMBEDDING_DIMENSION}, got {query_vec.shape[1]}")

    # Normalize vector if needed
    norm = np.linalg.norm(query_vec[0])
    if norm > 0 and not np.isclose(norm, 1.0, atol=1e-3):
        query_vec = query_vec / norm

    # Execute FAISS Inner Product search
    scores, indices = index.search(query_vec, top_k)

    results = []
    for rank, (score, idx) in enumerate(zip(scores[0], indices[0]), 1):
        if idx < 0 or idx >= len(documents):
            continue

        doc = documents[idx]
        results.append({
            "rank": rank,
            "document_id": doc.get("id", f"doc_{idx}"),
            "similarity_score": float(score),
            "title": doc.get("title", ""),
            "category": doc.get("category", ""),
            "content": doc.get("content", ""),
            "keywords": doc.get("keywords", []),
            "related_crops": doc.get("related_crops", []),
            "source": doc.get("source", ""),
        })

    return results
