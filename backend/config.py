import os

# Base directory of the backend package
_BASE = os.path.dirname(os.path.abspath(__file__))

# Phase 1: Database Path config
# KISAN_DATABASE_PATH defaults to /var/data/app_data.db on Render,
# but falls back to backend/app_data.db locally to support out-of-the-box development.
DB_PATH = os.getenv("KISAN_DATABASE_PATH")
if not DB_PATH:
    # If /var/data directory exists and is writable, use it as default (standard Render Volume)
    if os.path.isdir("/var/data") or (os.name != 'nt' and os.path.exists("/var")):
        DB_PATH = "/var/data/app_data.db"
    else:
        DB_PATH = os.path.join(_BASE, "app_data.db")

# Phase 2: Dataset Path configs
DATASET_V2_DIR = os.getenv("KISAN_DATASET_V2_PATH")
if not DATASET_V2_DIR:
    if os.path.isdir("/var/data") or (os.name != 'nt' and os.path.exists("/var")):
        DATASET_V2_DIR = "/var/data/dataset_v2"
    else:
        DATASET_V2_DIR = os.path.join(_BASE, "dataset_v2")

HARD_CASES_DIR = os.getenv("KISAN_HARD_CASES_PATH")
if not HARD_CASES_DIR:
    if os.path.isdir("/var/data") or (os.name != 'nt' and os.path.exists("/var")):
        HARD_CASES_DIR = "/var/data/hard_cases"
    else:
        HARD_CASES_DIR = os.path.join(_BASE, "hard_cases")

# Auto-create directory structure on import
for directory in [os.path.dirname(DB_PATH), DATASET_V2_DIR, HARD_CASES_DIR]:
    if directory:
        try:
            os.makedirs(directory, exist_ok=True)
        except Exception:
            # Squelch permissions errors during early import/startup if directories aren't immediately writable
            pass
