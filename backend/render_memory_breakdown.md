# Render Startup Memory Breakdown Report

This report presents a complete memory profiling audit of the Kisan Mitra backend on startup, tracking RSS (Resident Set Size) memory across the initialization of various components.

---

## 1. Startup Memory Timeline (Measured RSS)

| Phase | Memory (RSS) | Marginal RAM Used | Description |
| :--- | :--- | :--- | :--- |
| **Baseline (FastAPI + SQLite)** | **17.67 MB** | **+17.67 MB** | Initial python process startup, loading FastAPI, Uvicorn, and standard libraries. |
| **Firebase Admin SDK** | **17.70 MB** | **+0.03 MB** | Initializing Firebase Admin SDK app instance (lazy-loading credentials). |
| **PyTorch Library Import** | **196.04 MB** | **+178.34 MB** | Loading `torch` library binary into process memory. |
| **SQLite Connection Check** | **196.51 MB** | **+0.47 MB** | Initing SQLite database schemas and verifying tables. |
| **Advisory Engine Import** | **250.88 MB** | **+54.37 MB** | Importing `advisory_engine.py` modules (including `sentence-transformers` imports). |
| **SentenceTransformer + FAISS Load** | **575.49 MB** | **+324.61 MB** | Loading `all-MiniLM-L6-v2` embeddings weights and reading `index.faiss`. |
| **Default ResNet18 Disease Model** | **595.07 MB** | **+19.58 MB** | Loading ResNet18 CNN weights for primary disease classification. |
| **Legacy ResNet18 Disease Model** | **673.33 MB** | **+78.26 MB** | Loading backup ResNet18 CNN weights for apple/peach/cherry rollback routing. |

---

## 2. Component RAM Footprint Summary

Based on the marginal increases recorded, here is the net memory cost of each distinct system component:

*   **FastAPI Core & Uvicorn**: **~17.67 MB**
*   **Firebase Admin SDK**: **< 1.0 MB** (Startup)
*   **SQLite Client**: **< 0.5 MB**
*   **PyTorch Base (No models)**: **~178.34 MB** (Heavy binary footprint)
*   **ResNet18 Disease Model**: **~19.58 MB**
*   **SentenceTransformer & FAISS**: **~324.61 MB**
*   **Legacy Disease Model**: **~78.26 MB**
*   **Dataset Collector & Gemini Fallback**: **< 2.0 MB** (Import overhead)

---

## 3. Key Observations & Bottlenecks

1.  **PyTorch Import Overhead**: The largest single driver of baseline memory is simply importing the `torch` module (**178.34 MB**). Keeping PyTorch out of the startup sequence is crucial to stay under the 250 MB limit.
2.  **SentenceTransformer & FAISS Weights**: Initializing text embeddings and loading vector chunks consumes **~324.61 MB** of RAM. If loaded on startup along with PyTorch and ResNet18, the total process exceeds the 512 MB Free Tier ceiling immediately.
