import os
import sys
import time
from datetime import datetime

# Add parent directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from rag.faiss_utils import embed_query, search_documents, load_faiss_index, load_documents_and_metadata
from rag.context_builder import build_rag_context
from rag.response_generator import generate_local_response, classify_query_intent


def query_local_rag_engine(
    query_text,
    farmer_profile=None,
    farm_context=None,
    weather_data=None,
    market_data=None,
    top_k=5,
):
    """
    Master RAG Engine pipeline orchestrator.

    Pipeline sequence:
    1. Query embedding generation (384-d, L2 normalized)
    2. FAISS Index search (top_k nearest neighbor documents)
    3. Context aggregation (Knowledge + Farmer Profile + Farm Specs + Weather + Market)
    4. Deterministic response generation & confidence scoring
    """
    t_start = time.perf_counter()

    if not query_text or not isinstance(query_text, str):
        raise ValueError("query_text must be a non-empty string.")

    # Step 1: Query Embedding
    query_vec = embed_query(query_text)

    # Step 2: FAISS Vector Search
    retrieved_docs = search_documents(query_vec, top_k=top_k)

    # Step 3: Context Building
    context_data = build_rag_context(
        retrieved_docs=retrieved_docs,
        farmer_profile=farmer_profile,
        farm_context=farm_context,
        weather_data=weather_data,
        market_data=market_data,
    )

    # Step 4: Local Response Generation
    response = generate_local_response(query_text, context_data)


    total_time_ms = (time.perf_counter() - t_start) * 1000.0

    retrieved_ids = [s.get("id") for s in response["retrieved_sources"]]
    sim_scores = [round(float(s.get("similarity_score", 0.0)), 4) for s in response["retrieved_sources"]]

    print(
        f"[RAG Telemetry Log] Query: '{query_text}' | "
        f"Sim Scores: {sim_scores} | "
        f"Doc IDs: {retrieved_ids} | "
        f"Response Time: {total_time_ms:.2f} ms"
    )


    return {
        "query": query_text,
        "answer": response["answer"],
        "confidence_score": response["confidence_score"],
        "confidence_level": response["confidence_level"],
        "category": response["category"],
        "retrieved_sources": response["retrieved_sources"],
        "retrieved_doc_ids": retrieved_ids,
        "similarity_scores": sim_scores,
        "related_crops": response["related_crops"],
        "knowledge_categories_used": response["knowledge_categories_used"],
        "weather_applied": response["weather_applied"],
        "farm_applied": response["farm_applied"],
        "execution_time_ms": round(total_time_ms, 2),
        "timestamp": datetime.now().isoformat(),
    }



if __name__ == "__main__":
    print("Testing Standalone RAG Engine...")
    sample_query = "Best fertilizer for rice"
    res = query_local_rag_engine(sample_query)
    print(f"\nQuery: {res['query']}")
    print(f"Category: {res['category']} | Confidence: {res['confidence_score']} ({res['confidence_level']})")
    print(f"Sources: {[s['title'] for s in res['retrieved_sources']]}")
    print(f"Answer:\n{res['answer']}")
