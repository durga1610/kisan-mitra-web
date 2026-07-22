import os
import sys
import json
import time
from unittest.mock import MagicMock

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from rag.rag_engine import query_local_rag_engine
from main import app, chat_advisory, ChatRequest, FarmContext, WeatherContext



from starlette.requests import Request

def get_test_request():
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/api/v1/advisory/chat",
        "headers": [],
        "app": app,
        "client": ("127.0.0.1", 50000),
    }
    req = Request(scope)
    req.state.start_time = time.perf_counter()
    req.state.auth_time = 0.001
    return req


def test_e2e_local_rag_chat_integration():
    print("=" * 80)
    print(" KISAN MITRA: END-TO-END LOCAL RAG CHAT API INTEGRATION TESTS")
    print("=" * 80)

    mock_user = {
        "uid": "test_farmer_123",
        "email": "ramesh.kumar@example.com",
        "name": "Ramesh Kumar"
    }

    sample_farm = FarmContext(
        id="farm_001",
        name="Green Acres",
        soil="Alluvial Soil",
        crop="Rice",
        area=4.5
    )

    sample_weather = WeatherContext(
        condition="Cloudy with light rain",
        temperature=30.0,
        season="Kharif",
        humidity=78.0,
        rainChance=40.0
    )

    test_cases = [
        ("Crop Questions", "How to grow cotton", "Crop Selection"),
        ("Fertilizer Questions", "Best fertilizer for rice", "Fertilizer"),
        ("Weather Questions", "Weather advisory for heavy rainfall", "Weather"),
        ("Market Questions", "Mandi prices and MSP for rice", "Market"),
        ("Government Schemes", "Government schemes for farmers", "Government Schemes"),
        ("Pest Questions", "How to prevent rice blast", "Pest & Disease"),
        ("Out-of-domain Questions", "Quantum physics theory in space", "Soil"),
    ]

    print("\n* Testing /api/v1/advisory/chat function across 7 category scenarios...")
    print("=" * 80)

    for idx, (category_name, query_text, expected_intent) in enumerate(test_cases, 1):
        print(f"\n[Scenario #{idx}: {category_name}] -> Query: '{query_text}'")
        print("-" * 80)

        body = ChatRequest(
            message=query_text,
            language="en",
            farm=sample_farm,
            weather=sample_weather
        )

        t0 = time.perf_counter()
        res = chat_advisory(request=get_test_request(), body=body, user=mock_user)
        latency_ms = (time.perf_counter() - t0) * 1000.0


        assert isinstance(res, dict), "Response must be a dictionary"
        print(f"  |- Total Latency    : {latency_ms:.2f} ms")
        print(f"  |- Source Flag      : {res.get('source')}")
        print(f"  |- Confidence Score : {res.get('confidence'):.4f}")
        print(f"  |- Timing Metrics   : {res.get('timing')}")

        text_content = res.get("text", "")
        source_flag = res.get("source", "")

        # Key Contract Assertions for Flutter
        assert "text" in res, "Response missing 'text' key"
        assert "confidence" in res, "Response missing 'confidence' key"
        assert "source" in res, "Response missing 'source' key"
        assert "timing" in res, "Response missing 'timing' key"
        assert "LOCAL_RAG_ENGINE" in source_flag, f"Source must indicate LOCAL_RAG_ENGINE, got {source_flag}"

        # Assert zero Gemini API dependency
        assert "GEMINI" not in source_flag and "GEMINI_FALLBACK" not in source_flag, "Gemini was invoked!"

        if idx == 7:  # Out of domain query
            assert "don't have enough information" in text_content.lower(), "Expected low confidence fallback message"
            print("   >>> PASS: Low confidence query returned honest fallback message successfully!")
        else:
            assert len(text_content) > 50, "Response text too short"
            print("   >>> PASS: High/Medium confidence response generated from Local RAG Engine!")

        print("\n  [RESPONSE TEXT PREVIEW]:")
        print("  " + "\n  ".join(text_content.split("\n")[:4]))

    print("\n" + "=" * 80)
    print(" ALL 7/7 END-TO-END LOCAL RAG CHAT API INTEGRATION TESTS PASSED PERFECTLY!")
    print("=" * 80)


if __name__ == "__main__":
    try:
        test_e2e_local_rag_chat_integration()
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)
