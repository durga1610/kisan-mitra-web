# Security Scan Report — Kisan Mitra

**Generated:** 2026-06-24 06:01 UTC  |  **Commit:** b7e72e15  |  **Branch:** main

## Scan Summary

| Scanner | Status |
|---------|--------|
| Semgrep SAST | Completed |
| Bandit SAST | Completed |
| pip-audit | Completed |
| Gitleaks | Completed |
| Trivy | Completed |
| API Security Check | Completed |

## API Security Findings

**Total Issues:** 1  |  **Critical:** 0

| Severity | File | Finding |
|----------|------|---------|
| 🟠 HIGH | main.py | File upload endpoint detected — check MIME/size validation |