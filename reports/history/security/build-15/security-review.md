# Security Scan Report — Kisan Mitra

**Generated:** 2026-06-23 15:53 UTC  |  **Commit:** 8a16edd7  |  **Branch:** main

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