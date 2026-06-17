from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# ─────────────────────────────────────────────
# Helper
# ─────────────────────────────────────────────
def chat(message: str, language: str = "en", farm: dict = None) -> dict:
    body = {"message": message, "language": language}
    if farm:
        body["farm"] = farm
    response = client.post("/api/v1/advisory/chat", json=body)
    assert response.status_code == 200, f"HTTP {response.status_code}: {response.text}"
    return response.json()


def is_rejected(res_text: str) -> bool:
    """Return True if the response is a domain-rejection message."""
    return "Kisan Mitra AI Advisor" in res_text or "Supported topics:" in res_text or "I can only answer farming" in res_text


# ─────────────────────────────────────────────
# 1. In-Domain: Fertilizer Queries
# ─────────────────────────────────────────────
def test_grape_fertilizer():
    print("\nTest 1 – Best fertilizers for grape crop")
    res = chat("Best fertilizers for grape crop")
    text = res["text"]
    print(f"Response:\n{text}\n")
    assert not is_rejected(text), "Expected an in-domain farming answer, got rejection"
    assert "grape" in text.lower()
    assert any(w in text.lower() for w in ["potassium", "nitrogen", "npk", "fertilizer", "50:50:100"])


def test_banana_fertilizer():
    print("\nTest 2 – Best fertilizers for banana crop")
    res = chat("Best fertilizers for banana crop")
    text = res["text"]
    print(f"Response:\n{text}\n")
    assert not is_rejected(text), "Expected an in-domain farming answer, got rejection"
    assert "banana" in text.lower()
    assert any(w in text.lower() for w in ["phosphorus", "nitrogen", "npk", "fertilizer", "110:35:140"])


def test_tomato_fertilizer():
    print("\nTest 3 – Best fertilizer for tomato")
    res = chat("Best fertilizer for tomato")
    text = res["text"]
    print(f"Response:\n{text}\n")
    assert not is_rejected(text), "Expected an in-domain farming answer, got rejection"
    assert "tomato" in text.lower()
    assert any(w in text.lower() for w in ["npk", "urea", "fertilizer"])


# ─────────────────────────────────────────────
# 2. In-Domain: Irrigation / Water
# ─────────────────────────────────────────────
def test_papaya_water():
    print("\nTest 4 – Water requirement of papaya")
    res = chat("Water requirement of papaya")
    text = res["text"]
    print(f"Response:\n{text}\n")
    assert not is_rejected(text), "Expected an in-domain farming answer, got rejection"
    assert "papaya" in text.lower()
    assert any(w in text.lower() for w in ["drainage", "drip", "irrigation"])


# ─────────────────────────────────────────────
# 3. In-Domain: Disease Queries
# ─────────────────────────────────────────────
def test_rose_diseases():
    print("\nTest 5 – Diseases affecting rose plants")
    res = chat("Diseases affecting rose plants")
    text = res["text"]
    print(f"Response:\n{text}\n")
    assert not is_rejected(text), "Expected an in-domain farming answer, got rejection"
    assert "rose" in text.lower()
    assert any(w in text.lower() for w in ["black spot", "mildew", "dieback", "disease", "fungal"])


# ─────────────────────────────────────────────
# 4. In-Domain: Pest Management
# ─────────────────────────────────────────────
def test_pomegranate_pest():
    print("\nTest 6 – Pest management for pomegranate")
    res = chat("Pest management for pomegranate")
    text = res["text"]
    print(f"Response:\n{text}\n")
    assert not is_rejected(text), "Expected an in-domain farming answer, got rejection"
    assert "pomegranate" in text.lower()
    assert any(w in text.lower() for w in ["butterfly", "thrips", "spinosad", "pest", "management"])


# ─────────────────────────────────────────────
# 5. In-Domain: Weather
# ─────────────────────────────────────────────
def test_weather_at_farm():
    print("\nTest 7 – Weather at my farm")
    res = chat("Weather at my farm", farm={"id": "farm_1", "name": "Green Acres"})
    text = res["text"]
    print(f"Response:\n{text}\n")
    assert not is_rejected(text), "Expected weather info, got rejection"
    assert any(w in text.lower() for w in ["weather", "temperature", "rain", "forecast", "°c"])


# ─────────────────────────────────────────────
# 6. In-Domain: Crop Soil Requirement Query (NEW INTENT)
# ─────────────────────────────────────────────
def test_crop_soil_requirement_rice():
    print("\nTest 8 – Best soil for rice (CROP_SOIL_REQUIREMENT_QUERY)")
    res = chat("best soil for rice")
    text = res["text"]
    print(f"Response:\n{text}\n")
    assert not is_rejected(text), "Expected soil requirement info for rice, got rejection"
    assert any(w in text.lower() for w in ["soil", "clay", "loam", "rice", "requirement"])


def test_crop_soil_requirement_wheat():
    print("\nTest 9 – Soil requirements for wheat crop")
    res = chat("soil requirements for wheat crop")
    text = res["text"]
    print(f"Response:\n{text}\n")
    assert not is_rejected(text), "Expected soil requirement info for wheat, got rejection"
    assert any(w in text.lower() for w in ["soil", "loam", "wheat", "requirement", "sandy", "clay"])


def test_crop_soil_requirement_tomato():
    print("\nTest 10 – What type of soil is best for tomato")
    res = chat("what type of soil is best for tomato")
    text = res["text"]
    print(f"Response:\n{text}\n")
    assert not is_rejected(text), "Expected soil requirement info for tomato, got rejection"
    assert any(w in text.lower() for w in ["soil", "tomato", "loam", "well-drained", "ph"])


# ─────────────────────────────────────────────
# 7. Out-of-Domain: Movie Queries (MUST be rejected)
# ─────────────────────────────────────────────
def test_reject_ntr_movie():
    print("\nTest 11 – Tell me about NTR upcoming movie (MUST be rejected)")
    res = chat("Tell me about NTR upcoming movie")
    text = res["text"]
    print(f"Response:\n{text}\n")
    assert is_rejected(text), f"Expected domain-rejection but got: {text}"


def test_reject_suggest_movie():
    print("\nTest 12 – suggest me a movie (MUST be rejected)")
    res = chat("suggest me a movie")
    text = res["text"]
    print(f"Response:\n{text}\n")
    assert is_rejected(text), f"Expected domain-rejection but got: {text}"


def test_reject_bollywood():
    print("\nTest 13 – best bollywood movies 2024 (MUST be rejected)")
    res = chat("best bollywood movies 2024")
    text = res["text"]
    print(f"Response:\n{text}\n")
    assert is_rejected(text), f"Expected domain-rejection but got: {text}"


# ─────────────────────────────────────────────
# 8. Out-of-Domain: Technology (MUST be rejected)
# ─────────────────────────────────────────────
def test_reject_laptop():
    print("\nTest 14 – best laptop under 50000 (MUST be rejected)")
    res = chat("best laptop under 50000")
    text = res["text"]
    print(f"Response:\n{text}\n")
    assert is_rejected(text), f"Expected domain-rejection but got: {text}"


def test_reject_iphone():
    print("\nTest 15 – compare iphone 15 vs samsung s24 (MUST be rejected)")
    res = chat("compare iphone 15 vs samsung s24")
    text = res["text"]
    print(f"Response:\n{text}\n")
    assert is_rejected(text), f"Expected domain-rejection but got: {text}"


# ─────────────────────────────────────────────
# 9. Out-of-Domain: Politics (MUST be rejected)
# ─────────────────────────────────────────────
def test_reject_prime_minister():
    print("\nTest 16 – Who is the Prime Minister of India? (MUST be rejected)")
    res = chat("Who is the Prime Minister of India?")
    text = res["text"]
    print(f"Response:\n{text}\n")
    assert is_rejected(text), f"Expected domain-rejection but got: {text}"


def test_reject_election():
    print("\nTest 17 – When are the next elections? (MUST be rejected)")
    res = chat("When are the next elections?")
    text = res["text"]
    print(f"Response:\n{text}\n")
    assert is_rejected(text), f"Expected domain-rejection but got: {text}"


# ─────────────────────────────────────────────
# 10. Out-of-Domain: Sports (MUST be rejected)
# ─────────────────────────────────────────────
def test_reject_ipl():
    print("\nTest 18 – IPL points table 2024 (MUST be rejected)")
    res = chat("IPL points table 2024")
    text = res["text"]
    print(f"Response:\n{text}\n")
    assert is_rejected(text), f"Expected domain-rejection but got: {text}"


def test_reject_cricket_score():
    print("\nTest 19 – India vs Australia cricket score (MUST be rejected)")
    res = chat("India vs Australia cricket score")
    text = res["text"]
    print(f"Response:\n{text}\n")
    assert is_rejected(text), f"Expected domain-rejection but got: {text}"


# ─────────────────────────────────────────────
# 11. Out-of-Domain: General Knowledge (MUST be rejected)
# ─────────────────────────────────────────────
def test_reject_time():
    print("\nTest 20 – What time is it? (MUST be rejected)")
    res = chat("What time is it?")
    text = res["text"]
    print(f"Response:\n{text}\n")
    assert is_rejected(text), f"Expected domain-rejection but got: {text}"


def test_reject_capital():
    print("\nTest 21 – What is the capital of France? (MUST be rejected)")
    res = chat("What is the capital of France?")
    text = res["text"]
    print(f"Response:\n{text}\n")
    assert is_rejected(text), f"Expected domain-rejection but got: {text}"


# ─────────────────────────────────────────────
# 12. Greeting (should be accepted)
# ─────────────────────────────────────────────
def test_greeting():
    print("\nTest 22 – Hello (should be accepted as greeting)")
    res = chat("hello")
    text = res["text"]
    print(f"Response:\n{text}\n")
    assert not is_rejected(text), f"Greeting should be accepted but got rejection: {text}"


# ─────────────────────────────────────────────
# Master runner
# ─────────────────────────────────────────────
def test_universal_advisor():
    """Run all verification queries in sequence."""
    print("\n" + "="*60)
    print("Running Universal Crop Advisor validation queries...")
    print("="*60)

    # In-domain
    test_grape_fertilizer()
    test_banana_fertilizer()
    test_tomato_fertilizer()
    test_papaya_water()
    test_rose_diseases()
    test_pomegranate_pest()
    test_weather_at_farm()

    # New CROP_SOIL_REQUIREMENT_QUERY intent
    test_crop_soil_requirement_rice()
    test_crop_soil_requirement_wheat()
    test_crop_soil_requirement_tomato()

    # Out-of-domain rejections
    test_reject_ntr_movie()
    test_reject_suggest_movie()
    test_reject_bollywood()
    test_reject_laptop()
    test_reject_iphone()
    test_reject_prime_minister()
    test_reject_election()
    test_reject_ipl()
    test_reject_cricket_score()
    test_reject_time()
    test_reject_capital()

    # Greeting
    test_greeting()

    print("\n" + "="*60)
    print("ALL Universal Crop Advisor verification queries PASSED!")
    print("="*60)


if __name__ == "__main__":
    test_universal_advisor()
