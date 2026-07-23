with open("C:/Users/durga/.gemini/antigravity-ide/brain/91f7de9b-f1c1-4ab7-9db1-bc22cbca72c7/scratch/job_logs.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

print("--- PYTEST DETAILED EXECUTION OUTLINES ---")
for idx in range(138, 620):
    line = lines[idx].strip()
    # Check for test status lines (e.g. FAILED or ERROR or [ 98%])
    # Or lines containing 'FAIL' or 'AssertionError'
    if "FAIL" in line or "AssertionError" in line or "FAILED" in line or "::" in line:
        if "passed" not in line.lower() and "import" not in line.lower():
            print(f"L{idx+1}: {line}")
