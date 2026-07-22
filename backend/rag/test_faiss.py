import os
import sys
import time
import json
import numpy as np

# Ensure parent directory is in sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from rag.faiss_utils import load_faiss_index, load_documents_and_metadata, embed_query, search_documents


def test_faiss_search_retrieval():
    print("=" * 70)
    print(" KISAN MITRA: FAISS VECTOR DATABASE RETRIEVAL VERIFICATION TESTS")
    print("=" * 70)

    # 1. Load Index and Documents
    print("\n1. Loading FAISS index and document store...")
    index = load_faiss_index()
    documents, metadata = load_documents_and_metadata()

    print(f"   [PASS] FAISS index loaded ({index.ntotal} vectors, type={metadata.get('faiss', {}).get('index_type')}).")
    print(f"   [PASS] Documents store loaded ({len(documents)} records).")

    assert index.ntotal == len(documents), f"Mismatch: {index.ntotal} vectors vs {len(documents)} documents"

    # 2. Test Queries List
    test_queries = [
        "Best fertilizer for rice",
        "Soil suitable for cotton",
        "How to irrigate wheat",
        "High humidity disease prevention",
        "Government schemes for farmers",
    ]

    print(f"\n2. Executing semantic search across {len(test_queries)} agricultural queries...")
    query_latencies = []

    for idx, query in enumerate(test_queries, 1):
        print("\n" + "-" * 70)
        print(f" Query #{idx}: '{query}'")
        print("-" * 70)

        # Generate query vector
        t0 = time.perf_counter()
        query_vec = embed_query(query)
        q_gen_time = (time.perf_counter() - t0) * 1000.0

        # Perform FAISS search
        t1 = time.perf_counter()
        results = search_documents(query_vec, top_k=3, index=index, documents=documents)
        search_latency_ms = (time.perf_counter() - t1) * 1000.0
        query_latencies.append(search_latency_ms)

        print(f" Embed Time: {q_gen_time:.2f} ms | FAISS Latency: {search_latency_ms:.3f} ms ({search_latency_ms*1000:.1f} us)")
        print(f"{'Rank':<5} | {'Sim Score':<10} | {'Category':<20} | {'ID':<25} | {'Title'}")
        print("-" * 70)

        assert len(results) > 0, f"No results returned for query '{query}'"

        for r in results:
            rank = r["rank"]
            sim_score = r["similarity_score"]
            cat = r["category"]
            doc_id = r["document_id"]
            title = r["title"][:30] + "..." if len(r["title"]) > 30 else r["title"]

            # Verify score validity (Inner Product of L2 normalized vectors is Cosine Similarity, bounded in [-1.0, 1.0])
            assert -1.0 <= sim_score <= 1.0, f"Invalid similarity score {sim_score}"
            # Check required dict keys
            assert "document_id" in r and "similarity_score" in r and "document" in r

            print(f"{rank:<5} | {sim_score:<10.4f} | {cat:<20} | {doc_id:<25} | {title}")

        top_match = results[0]
        print(f" [TOP RESULT CONTENT SUMMARY]: {top_match['content'][:100]}...")

    avg_latency_ms = np.mean(query_latencies)
    avg_latency_us = avg_latency_ms * 1000.0

    print("\n" + "=" * 70)
    print(" VERIFICATION TEST SUMMARY & LATENCY REPORT")
    print("=" * 70)
    print(f"  |- Total Queries Tested     : {len(test_queries)}")
    print(f"  |- All Queries Passed      : YES (5/5)")
    print(f"  |- Avg Search Latency      : {avg_latency_us:.2f} us ({avg_latency_ms:.4f} ms)")
    print("=" * 70)
    print("\nFAISS Vector Database retrieval tests PASSED successfully!")


if __name__ == "__main__":
    try:
        test_faiss_search_retrieval()
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)
