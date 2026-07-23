with open("C:/Users/durga/.gemini/antigravity-ide/brain/91f7de9b-f1c1-4ab7-9db1-bc22cbca72c7/scratch/job_logs.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx in range(2129, min(len(lines), 2195)):
    print(f"L{idx+1}: {lines[idx].strip()}")
