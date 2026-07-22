import os
import sys
import json
import random
import numpy as np

# Ensure parent directory is in sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)


def verify_embeddings():
    print("=" * 60)
    print(" KISAN MITRA: EMBEDDING VERIFICATION TESTS")
    print("=" * 60)

    vector_db_dir = os.path.join(parent_dir, "models", "vector_db")
    embeddings_path = os.path.join(vector_db_dir, "knowledge_embeddings.npy")
    if not os.path.exists(embeddings_path):
        embeddings_path = os.path.join(vector_db_dir, "embeddings.npy")

    documents_path = os.path.join(vector_db_dir, "documents.json")
    metadata_path = os.path.join(vector_db_dir, "metadata.json")

    # 1. Check Artifact File Existence
    print("\n1. Verifying vector database artifact files exist...")
    assert os.path.exists(embeddings_path), f"Missing embeddings.npy at {embeddings_path}"
    assert os.path.exists(documents_path), f"Missing documents.json at {documents_path}"
    assert os.path.exists(metadata_path), f"Missing metadata.json at {metadata_path}"
    print("   [PASS] All 3 vector database files exist.")

    # 2. Load Artifacts
    embeddings = np.load(embeddings_path)
    with open(documents_path, "r", encoding="utf-8") as f:
        documents = json.load(f)
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    num_embeddings, dim = embeddings.shape
    num_documents = len(documents)
    total_metadata_records = metadata.get("total_records")

    print(f"\n2. Verifying dataset alignment & dimensions...")
    print(f"   - Embeddings shape: {embeddings.shape}")
    print(f"   - Documents count : {num_documents}")
    print(f"   - Metadata count  : {total_metadata_records}")

    assert num_embeddings == num_documents, f"Mismatch: {num_embeddings} embeddings vs {num_documents} documents"
    assert num_embeddings == total_metadata_records, f"Mismatch: {num_embeddings} embeddings vs {total_metadata_records} in metadata"
    assert dim == 384, f"Expected 384 embedding dimensions, got {dim}"
    print(f"   [PASS] Vector shape is ({num_embeddings}, {dim}) matching all {num_documents} knowledge documents.")

    # 3. Random Sample Verification (Select 10 records)
    sample_size = min(10, num_documents)
    random.seed(42)  # Seed for deterministic test verification
    sampled_indices = random.sample(range(num_documents), sample_size)

    print(f"\n3. Verifying 10 randomly sampled knowledge records and embeddings...")
    print(f"{'Index':<6} | {'ID':<25} | {'Category':<22} | {'Vector Norm':<12} | {'Dimension'}")
    print("-" * 80)

    for idx in sampled_indices:
        doc = documents[idx]
        vec = embeddings[idx]

        # Check non-null, non-empty, and valid float values
        assert vec is not None, f"Vector at index {idx} is None"
        assert len(vec) == 384, f"Vector at index {idx} has length {len(vec)} != 384"
        assert not np.isnan(vec).any(), f"Vector at index {idx} contains NaN values"
        assert not np.isinf(vec).any(), f"Vector at index {idx} contains Inf values"

        norm = float(np.linalg.norm(vec))
        doc_id = doc.get("id", f"doc_{idx}")
        category = doc.get("category", "N/A")

        print(f"{idx:<6} | {doc_id:<25} | {category:<22} | {norm:<12.4f} | {len(vec)}")

    print("\n" + "=" * 60)
    print(" VERIFICATION SUCCESSFUL: 10/10 RANDOMLY SAMPLED EMBEDDINGS VALIDATED")
    print("=" * 60)


if __name__ == "__main__":
    verify_embeddings()
