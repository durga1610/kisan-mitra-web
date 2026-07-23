with open("C:/Users/durga/.gemini/antigravity-ide/brain/91f7de9b-f1c1-4ab7-9db1-bc22cbca72c7/scratch/job_logs.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    l_lower = line.lower()
    if any(k in l_lower for k in ["uvicorn", "backend is up", "waiting for backend", "failed (non-200", "requests per second", "http 200", "status_codes.append"]):
        print(f"L{idx+1}: {line.strip()}")
