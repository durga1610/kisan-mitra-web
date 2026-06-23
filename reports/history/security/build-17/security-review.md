# Security Scan Report — Kisan Mitra

**Generated:** 2026-06-23 17:36 UTC  |  **Commit:** 024c7ccb  |  **Branch:** main

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