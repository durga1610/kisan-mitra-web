import os, sys, io, json, traceback
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["TESTING"] = "1"

from services.gemini_fallback import execute_gemini_call
from PIL import Image, ImageDraw

# Make test leaf image
img = Image.new("RGB", (300, 300), "#2d6a4f")
draw = ImageDraw.Draw(img)
draw.ellipse([50, 30, 250, 270], fill="#388e3c", outline="#1b5e20", width=2)
draw.ellipse([100, 100, 130, 130], fill="#8B4513")
buf = io.BytesIO()
img.convert("RGB").save(buf, "JPEG")
img_bytes = buf.getvalue()

schema = '{"disease_name":"...","confidence":85,"severity":"Medium","symptoms":"...","treatment":"...","prevention":"...","organic_solution":"...","chemical_solution":"..."}'

print("=== DISEASE VISION RAW RESPONSE ===")
try:
    text = execute_gemini_call(
        f"Analyze this crop leaf image. Reply ONLY with valid JSON matching this exact schema. No markdown, no code fences, no explanation. Schema: {schema}",
        is_vision=True,
        image_bytes=img_bytes
    )
    print("RAW REPR:", repr(text[:400]))
    print("Starts with backtick:", text.strip().startswith("`"))
    try:
        parsed = json.loads(text.strip())
        print("JSON PARSE: SUCCESS", list(parsed.keys()))
    except Exception as je:
        # Try stripping markdown
        cleaned = text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
        try:
            parsed2 = json.loads(cleaned)
            print("JSON PARSE AFTER STRIP: SUCCESS", list(parsed2.keys()))
        except Exception as je2:
            print(f"JSON PARSE FAILED: {je}")
            print(f"After strip also failed: {je2}")
            print("Cleaned text:", repr(cleaned[:200]))
except Exception as e:
    print(f"ERROR: {e}")
    traceback.print_exc()

fert_schema = '{"crop":"Banana","stage":"Vegetative","age":45,"recommendation":"...","dosage":"...","organicAlternative":"...","timing":"...","precautions":"..."}'

print()
print("=== FERTILIZER RAW RESPONSE ===")
try:
    text2 = execute_gemini_call(
        f"Fertilizer recommendation for Banana, 45 days old, Vegetative stage, Alluvial soil, Hot and humid weather. "
        f"Reply ONLY with valid JSON. No markdown. No explanation. Schema: {fert_schema}"
    )
    print("RAW REPR:", repr(text2[:400]))
    print("Starts with backtick:", text2.strip().startswith("`"))
    try:
        parsed = json.loads(text2.strip())
        print("JSON PARSE: SUCCESS", list(parsed.keys()))
    except Exception as je:
        cleaned = text2.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
        try:
            parsed2 = json.loads(cleaned)
            print("JSON PARSE AFTER STRIP: SUCCESS", list(parsed2.keys()))
        except Exception as je2:
            print(f"JSON PARSE FAILED: {je}")
            print("Cleaned:", repr(cleaned[:200]))
except Exception as e:
    print(f"ERROR: {e}")
    traceback.print_exc()
