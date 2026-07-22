import os
import sys
import json
import time

# Ensure parent directory is in sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from rag.rag_engine import query_local_rag_engine


def test_rag_engine_pipeline():
    print("=" * 80)
    print(" KISAN MITRA: STANDALONE LOCAL RAG ENGINE VERIFICATION TESTS")
    print("=" * 80)

    # Simulated Farmer Context & Environmental Context
    farmer_profile = {
        "name": "Ramesh Kumar",
        "state": "Punjab",
        "district": "Ludhiana",
        "language": "Hindi",
    }

    farm_context = {
        "soil_type": "Alluvial Soil",
        "current_crop": "Rice",
        "farm_area_acres": 5.0,
        "irrigation_type": "Canal & Tubewell",
    }

    weather_data = {
        "temp_c": 31.5,
        "humidity": 82.0,
        "rainfall_mm": 25.0,
        "condition": "Heavy Rain Forecast",
    }

    market_data = {
        "commodity": "Rice (Paddy)",
        "mandi_price": "₹2,203 / Quintal",
        "msp": "₹2,183 / Quintal",
        "trend": "Upward",
    }

    test_queries = [
        "Best fertilizer for rice",
        "How to grow cotton",
        "Which soil is suitable for maize",
        "How to prevent rice blast",
        "Weather advisory for heavy rainfall",
        "Government schemes for farmers",
        "Quantum physics string theory in outer space",  # Low confidence test query
    ]

    print(f"\n* Running RAG Engine test across {len(test_queries)} target queries...")
    print("=" * 80)

    for idx, query in enumerate(test_queries, 1):
        print(f"\n[Test Query #{idx}]: '{query}'")
        print("-" * 80)

        res = query_local_rag_engine(
            query_text=query,
            farmer_profile=farmer_profile,
            farm_context=farm_context,
            weather_data=weather_data,
            market_data=market_data,
            top_k=5,
        )

        query_text = res["query"]
        answer = res["answer"]
        score = res["confidence_score"]
        conf_level = res["confidence_level"]
        category = res["category"]
        sources = res["retrieved_sources"]
        crops = res["related_crops"]
        cats_used = res["knowledge_categories_used"]
        exec_ms = res["execution_time_ms"]

        print(f"  |- Category          : {category}")
        print(f"  |- Confidence Score  : {score:.4f} ({conf_level})")
        print(f"  |- Latency           : {exec_ms:.2f} ms")
        print(f"  |- Retrieved Sources : {len(sources)} documents")
        for s in sources[:3]:
            print(f"     * [Rank {s['rank']}] {s['title']} (Score: {s['similarity_score']:.4f})")

        print(f"  |- Related Crops     : {', '.join(crops[:5]) if crops else 'N/A'}")
        print(f"  |- Categories Used   : {', '.join(cats_used)}")
        print(f"  |- Weather Applied   : {res['weather_applied']}")
        print(f"  |- Farm Applied      : {res['farm_applied']}")

        print("\n  [GENERATED ANSWER PREVIEW]:")
        print("  " + "\n  ".join(answer.split("\n")[:4]))

        # Assertions
        assert query_text == query, "Query mismatch"
        assert isinstance(score, float), "Score must be float"
        assert conf_level in ["High", "Medium", "Low"], "Invalid confidence level"
        assert len(sources) > 0, "Sources must not be empty"

        if idx == 7:  # Low confidence test query
            assert conf_level == "Low", f"Expected Low confidence for irrelevent query, got {conf_level}"
            assert "don't have enough information" in answer.lower(), "Expected low confidence fallback message"
            print("   >>> PASS: Correctly identified Low Confidence query and returned honest fallback response!")
        else:
            assert conf_level in ["High", "Medium"], f"Expected High/Medium confidence for query #{idx}"
            assert len(answer) > 50, "Answer too short"
            print("   >>> PASS: Highly relevant answer generated with retrieved context!")

    print("\n" + "=" * 80)
    print(" ALL 7/7 LOCAL RAG ENGINE VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    try:
        test_rag_engine_pipeline()
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)
