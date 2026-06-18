"""
Fix remaining print() statements in advisory_engine.py and suitability_engine.py
and fix remaining pickle.load calls in advisory_engine.py (lines ~1757, 1759).
"""
import re

# ── advisory_engine.py ────────────────────────────────────────────────────
with open("advisory_engine.py", "r", encoding="utf-8") as f:
    text = f.read()

# --- Replace remaining pickle.load calls (lines ~1757, 1759) ----------------
text = text.replace(
    '                with open(model_path, "rb") as f:\n                    _crop_recommendation_model = pickle.load(f)',
    '                _crop_recommendation_model = safe_pickle_load(model_path)  # F-05',
)
text = text.replace(
    '                with open(preprocessors_path, "rb") as f:\n                    _crop_preprocessors = pickle.load(f)',
    '                _crop_preprocessors = safe_pickle_load(preprocessors_path)  # F-05',
)

# --- Bulk print -> logger replacements --------------------------------------
# Strategy: replace f-string prints with logger calls preserving the message.

def replace_print(m):
    inner = m.group(1)
    # Categorise by severity hint
    if any(kw in inner for kw in ["Failed", "ERROR", "Error", "WARNING", "WARNING", "not found", "failed"]):
        # Convert f-string to %-style lazily (keep as info for simplicity, actual f-string stays)
        return f'logger.warning({inner})'
    elif any(kw in inner for kw in ["DEBUG LOG", "DOMAIN CHECK", "AUDIT LOG", "--- AUDIT", "Intent:", "Handler:", "chunk", "Final chunk", "---"]):
        return f'logger.debug({inner})'
    else:
        return f'logger.info({inner})'

# Match print(anything) — single-argument print calls
text = re.sub(r'\bprint\(([^\n]+)\)', replace_print, text)

with open("advisory_engine.py", "w", encoding="utf-8") as f:
    f.write(text)

print("advisory_engine.py: print() replacements done")

# ── suitability_engine.py ─────────────────────────────────────────────────
with open("suitability_engine.py", "r", encoding="utf-8") as f:
    text = f.read()

# Add logging import if not present
if "import logging" not in text:
    text = "import logging\n" + text
if "logger = logging.getLogger" not in text:
    # Insert after the import block (after last import line)
    text = text.replace(
        "import pickle\n",
        "import pickle\n\nlogger = logging.getLogger(__name__)\n",
        1
    )

# Replace pickle.load calls
text = text.replace(
    'with open(PREPROCESSORS_PATH, "rb") as f:\n            preprocessors = pickle.load(f)',
    'preprocessors = safe_pickle_load(PREPROCESSORS_PATH)  # F-05',
)
text = text.replace(
    'with open(MODEL_PATH, "rb") as f:\n            model = pickle.load(f)',
    'model = safe_pickle_load(MODEL_PATH)  # F-05',
)

# Add security_utils import if missing
if "from security_utils import" not in text:
    text = text.replace(
        "import pickle\n",
        "import pickle\nfrom security_utils import safe_pickle_load\n",
        1,
    )

# Bulk print -> logger
text = re.sub(r'\bprint\(([^\n]+)\)', replace_print, text)

with open("suitability_engine.py", "w", encoding="utf-8") as f:
    f.write(text)

print("suitability_engine.py: all fixes done")
