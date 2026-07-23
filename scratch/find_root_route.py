with open("c:/Users/durga/kisan_mitra/backend/main.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if '"/"' in line or "'/'" in line:
        if "@app." in line or "@router." in line:
            print(f"L{idx+1}: {line.strip()}")
