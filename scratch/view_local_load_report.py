import os

paths = [
    "gh-pages-dir/reports/latest/load-test-report.md",
    "Vulnerability Test Results/load-test-report.md"
]

for p in paths:
    if os.path.exists(p):
        print(f"--- Content of {p} ---")
        print(open(p, "r", encoding="utf-8").read())
