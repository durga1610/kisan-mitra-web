# Kisan Mitra RAG-based Agriculture Expert Advisor

This module provides a production-ready Agriculture Expert Advisor utilizing Retrieval-Augmented Generation (RAG) running entirely on CPU. It replaces the previous keyword-matching advisory mock responses.

## Key Features

1. **Structured Knowledge Base**: Curated reference documents on Crop Cultivation, Plant Diseases, Pest Management, Fertilizers, Soil Health, Irrigation, Organic Farming, Crop Nutrition, Weather Impact, and Harvesting Practices.
2. **Dense Vector Database**: Uses `sentence-transformers/all-MiniLM-L6-v2` to create 384-dimensional text embeddings, indexed via **FAISS** (with a native **NumPy Cosine-Similarity** fallback).
3. **CPU-Optimized Model Loading**: Loads a lightweight local model (`TinyLlama/TinyLlama-1.1B-Chat-v1.0`) on demand.
4. **Deterministic Generative Fallback**: Implements a zero-delay structured response fallback if local resources or network constraints prevent downloading the full LLM.
5. **Session Memory**: Tracks conversation history (up to the last 5 turns) for context-aware chat.
6. **Strict Topic Restriction**: Filters and rejects off-topic queries, redirecting users to agricultural assistance only.
7. **Multilingual Interface**: Built-in translation mappings for Telugu and Hindi.

---

## Directory Structure

*   `documents/`: Text files containing raw domain knowledge.
*   `models/vector_db/`: Output directory for serialized FAISS index and chunk coordinates.
*   `ingest.py`: Chunking and embedding generation pipeline script.
*   `advisory_engine.py`: Vector search, memory manager, prompts, LLM loader, and fallbacks.
*   `main.py`: FastAPI server running `/api/v1/advisory/chat`.
*   `test_api.py`: Automated testing suite.

---

## Getting Started

### 1. Ingestion Pipeline
To compile/update the vector database index:
```bash
python ingest.py
```

### 2. Standalone Query Test
Verify search results directly via terminal:
```bash
python -c "from advisory_engine import query_rag; print(query_rag('How to treat rice blast?'))"
```

### 3. Running API Tests
Execute the test suite to validate FastAPI endpoints and RAG compatibility:
```bash
python test_api.py
```

### 4. Running the Backend Server
Start the Uvicorn service:
```bash
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
*   Enable local LLM download: Set environment variable `KISAN_MITRA_DOWNLOAD_LLM=1` before startup.

---

## Production Deployment via Docker

Build the Docker image:
```bash
docker build -t kisan-mitra-backend .
```

Run the container:
```bash
docker run -p 8000:8000 kisan-mitra-backend
```
