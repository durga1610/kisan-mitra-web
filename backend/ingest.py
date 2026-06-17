import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer

# Check if faiss is available
try:
    import faiss
    HAS_FAISS = True
    print("[INFO] FAISS is available.")
except ImportError:
    HAS_FAISS = False
    print("[WARNING] FAISS not found or failed to load. Falling back to NumPy-based Cosine-Similarity.")

DOCS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "documents")
DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "vector_db")

def chunk_document(text, filename):
    # Split by double newlines to keep paragraphs intact as coherent units
    paragraphs = text.strip().split("\n\n")
    chunks = []
    for p in paragraphs:
        p_clean = p.strip()
        if p_clean:
            chunks.append({
                "text": p_clean,
                "source": filename
            })
    return chunks

def build_index():
    os.makedirs(DB_DIR, exist_ok=True)
    
    # 1. Load documents
    chunks = []
    if not os.path.exists(DOCS_DIR):
        print(f"Docs directory not found: {DOCS_DIR}")
        return
        
    for fname in os.listdir(DOCS_DIR):
        if fname.endswith(".txt"):
            fpath = os.path.join(DOCS_DIR, fname)
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
            doc_chunks = chunk_document(content, fname)
            chunks.extend(doc_chunks)
            print(f"Loaded {len(doc_chunks)} chunks from {fname}")
            
    if not chunks:
        print("No chunks to index.")
        return
        
    print(f"Total chunks to index: {len(chunks)}")
    
    # Save chunks to json
    chunks_path = os.path.join(DB_DIR, "chunks.json")
    with open(chunks_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    print(f"Saved chunks to {chunks_path}")
        
    # 2. Generate embeddings
    print("Loading sentence-transformers/all-MiniLM-L6-v2...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    
    # Save raw embeddings for NumPy fallback
    emb_path = os.path.join(DB_DIR, "embeddings.npy")
    np.save(emb_path, embeddings)
    print(f"Saved NumPy embeddings to {emb_path}")
    
    # 3. Save to FAISS if available
    if HAS_FAISS:
        try:
            dimension = embeddings.shape[1]
            faiss_embeddings = embeddings.copy()
            # Normalize vectors for cosine similarity (Inner Product of normalized vectors is cosine similarity)
            norms = np.linalg.norm(faiss_embeddings, axis=1, keepdims=True)
            norms = np.where(norms == 0, 1.0, norms)
            faiss_embeddings = faiss_embeddings / norms
            
            index = faiss.IndexFlatIP(dimension)
            index.add(faiss_embeddings)
            faiss_path = os.path.join(DB_DIR, "index.faiss")
            faiss.write_index(index, faiss_path)
            print(f"Successfully built and saved FAISS index to {faiss_path}")
        except Exception as e:
            print(f"[ERROR] Failed to save FAISS index: {e}. NumPy fallback will be used.")
    else:
        print("[INFO] NumPy embeddings saved. Custom cosine-similarity will be used at query time.")

if __name__ == "__main__":
    build_index()
