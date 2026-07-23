with open("c:/Users/durga/kisan_mitra/backend/main.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "CLASSES = " in line or "def init_disease_model" in line:
        print(f"L{idx+1}: {line.strip()}")
