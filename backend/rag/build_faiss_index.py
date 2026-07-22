import os
import sys
import time
import json
import numpy as np
import faiss

# Add parent directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from rag.faiss_utils import VECTOR_DB_DIR, DEFAULT_INDEX_PATH, DEFAULT_DOCS_PATH, DEFAULT_META_PATH


def build_faiss_vector_index():
    print("=" * 60)
    print(" KISAN MITRA: FAISS VECTOR DATABASE INDEX BUILDER")
    print("=" * 60)

    emb_path = os.path.join(VECTOR_DB_DIR, "embeddings.npy")

    print("\n1. Loading existing vector database artifacts...")
    if not os.path.exists(emb_path):
        raise FileNotFoundError(f"Missing embeddings matrix at '{emb_path}'")
    if not os.path.exists(DEFAULT_DOCS_PATH):
        raise FileNotFoundError(f"Missing documents store at '{DEFAULT_DOCS_PATH}'")
    if not os.path.exists(DEFAULT_META_PATH):
        raise FileNotFoundError(f"Missing metadata registry at '{DEFAULT_META_PATH}'")

    embeddings = np.load(emb_path).astype(np.float32)
    with open(DEFAULT_DOCS_PATH, "r", encoding="utf-8") as f:
        documents = json.load(f)
    with open(DEFAULT_META_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    total_records, dimension = embeddings.shape
    print(f"   [PASS] Loaded {total_records} embeddings with dimension={dimension}.")
    print(f"   [PASS] Loaded {len(documents)} document records and metadata.")

    # Validate alignment
    assert total_records == len(documents), f"Mismatch: {total_records} embeddings vs {len(documents)} documents"
    assert dimension == 384, f"Expected 384 dimensions, got {dimension}"

    # 2. Build FAISS Index (IndexFlatIP for exact Cosine Similarity on L2-normalized vectors)
    print("\n2. Initializing FAISS IndexFlatIP (Inner Product)...")
    build_start_time = time.perf_counter()

    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    build_time = time.perf_counter() - build_start_time
    assert index.ntotal == total_records, f"FAISS index count mismatch: {index.ntotal} vs {total_records}"

    print(f"   [PASS] Added {index.ntotal} vectors into FAISS IndexFlatIP in {build_time*1000.0:.3f} ms.")

    # 3. Save FAISS Index Binary File
    print("\n3. Saving FAISS index binary file...")
    if os.path.exists(DEFAULT_INDEX_PATH):
        try:
            os.remove(DEFAULT_INDEX_PATH)
        except Exception:
            pass

    faiss.write_index(index, DEFAULT_INDEX_PATH)
    file_size_bytes = os.path.getsize(DEFAULT_INDEX_PATH)
    file_size_kb = file_size_bytes / 1024.0
    print(f"   [PASS] Saved FAISS index binary to '{DEFAULT_INDEX_PATH}' ({file_size_kb:.2f} KB).")

    # 4. Measure Benchmark & Performance Statistics
    print("\n4. Running retrieval benchmark statistics...")
    # Warmup query
    dummy_query = embeddings[0:1]
    index.search(dummy_query, 5)

    # Benchmark 1,000 search queries
    n_benchmark = 1000
    b_start = time.perf_counter()
    for _ in range(n_benchmark):
        index.search(dummy_query, 5)
    total_b_time = time.perf_counter() - b_start

    avg_search_latency_us = (total_b_time / n_benchmark) * 1000000.0
    queries_per_sec = n_benchmark / total_b_time

    # Update metadata registry with FAISS details
    metadata["faiss"] = {
        "index_type": "IndexFlatIP",
        "index_file": "faiss_index.bin",
        "total_vectors": index.ntotal,
        "dimension": dimension,
        "index_size_bytes": file_size_bytes,
        "build_time_ms": round(build_time * 1000.0, 3),
        "avg_search_latency_us": round(avg_search_latency_us, 2),
        "queries_per_second": round(queries_per_sec, 2),
    }

    with open(DEFAULT_META_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print(" FAISS VECTOR INDEX PERFORMANCE STATISTICS")
    print("=" * 60)
    print(f"  |- Total Indexed Documents  : {index.ntotal}")
    print(f"  |- FAISS Index Type         : IndexFlatIP (Cosine Similarity)")
    print(f"  |- Embedding Dimension      : {dimension}")
    print(f"  |- Index Build Time         : {build_time*1000.0:.3f} ms")
    print(f"  |- Index File Size          : {file_size_kb:.2f} KB ({file_size_bytes} bytes)")
    print(f"  |- Average Search Latency   : {avg_search_latency_us:.2f} microseconds ({avg_search_latency_us/1000.0:.4f} ms)")
    print(f"  |- Retrieval Throughput     : {queries_per_sec:,.0f} queries/second")
    print("=" * 60)

    print("\nFAISS Index built, benchmarked, and saved successfully!")
    return metadata["faiss"]


if __name__ == "__main__":
    try:
        build_faiss_vector_index()
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)
