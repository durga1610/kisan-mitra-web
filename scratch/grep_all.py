import os

search_dir = "c:/Users/durga/kisan_mitra/backend"
target = "diagnosis unavailable"

for root, dirs, files in os.walk(search_dir):
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            try:
                content = open(path, "r", encoding="utf-8").read()
                if target in content.lower():
                    print(f"Found in {path}")
                    # Print matching lines
                    lines = content.splitlines()
                    for idx, line in enumerate(lines):
                        if target in line.lower():
                            print(f"  L{idx+1}: {line.strip()}")
            except Exception as e:
                pass
