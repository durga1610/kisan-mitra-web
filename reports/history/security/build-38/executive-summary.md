# Executive Summary — Kisan Mitra Backend Security Assessment

**Assessment Date:** 2026-06-22  
**Application:** Kisan Mitra AI — Agricultural Advisory & Disease Detection Backend  
**Framework:** FastAPI (Python 3.11) · SQLite · Firebase Auth · PyTorch · Google Gemini AI  
**Assessed By:** Senior Application Security Engineer / Penetration Tester  

---

## Total Findings

| Severity | Count | Status |
|----------|-------|--------|
| 🔴 **Critical** | **2** | Requires immediate remediation |
| 🟠 **High** | **7** | Remediate within 1 sprint |
| 🟡 **Medium** | **5** | Remediate within 1 month |
| 🟢 **Low** | **4** | Remediate within next release |
| **Total** | **18** | |

---

## Overall Security Score

```
╔══════════════════════════════════════════════════════╗
║   OVERALL SECURITY SCORE:  58 / 100                  ║
║                                                      ║
║   Authentication      ██████████████░░  88/100       ║
║   Authorization       ████████░░░░░░░░  52/100       ║
║   Input Validation    ██████████████░░  85/100       ║
║   Configuration       ███████████░░░░░  65/100       ║
║   Data Protection     ████████░░░░░░░░  48/100       ║
║   Secrets Management  ████░░░░░░░░░░░░  25/100       ║
║   Cryptography        █████████████░░░  80/100       ║
║   Error Handling      ██████████░░░░░░  62/100       ║
╚══════════════════════════════════════════════════════╝
```

**Verdict:** The application has a solid authentication foundation (Firebase JWT) and good input validation practices. However, critical gaps exist in secrets management, CORS configuration, and authorization controls that must be addressed before production hardening is considered complete.

---

## Most Critical Risks

### 1. 🔴 Hardcoded API Key Committed to Repository (`backend/.env`)
The `MANDI_API_KEY` (`579b464db66ec23bdd0000017c7ccd02bac445d36a5a228846357fa2`) is present in `backend/.env` which appears to have been committed. This key provides access to the Indian Government data.gov.in Mandi crop price API. **Immediate action: rotate this key.**

### 2. 🔴 SSL Certificate Validation Disabled for External API Call
All market price requests to `https://api.data.gov.in` are made with `ctx.verify_mode = ssl.CERT_NONE`, making every API call vulnerable to MITM attacks. An attacker positioned on the network can steal the API key mid-transmission and inject false crop market prices, causing financial harm to farmers.

### 3. 🟠 Overly Permissive CORS — Any `*.vercel.app` Domain Accepted
The wildcard regex `https://.*\.vercel\.app` combined with `allow_credentials=True` means any attacker who creates a free Vercel app (e.g., `https://evil-kisan.vercel.app`) can make authenticated cross-origin requests to the backend, bypassing the origin restriction entirely.

---

## Key Security Strengths

| Area | Assessment |
|------|-----------|
| Authentication | ✅ Firebase JWT properly enforced on 27/29 endpoints |
| SQL Injection | ✅ All queries use parameterized placeholders — no SQLi risk found |
| File Upload | ✅ MIME + extension + size + PIL content verification |
| Security Headers | ✅ HSTS, X-Frame-Options, X-Content-Type-Options, X-XSS-Protection |
| Rate Limiting | ✅ SlowAPI on all endpoints (10–60 req/min per route) |
| API Docs | ✅ Swagger/ReDoc disabled in production |
| PyTorch Safety | ✅ `weights_only=True` used in all `torch.load()` calls |
| Secrets in Logs | ✅ API keys never logged — only index labels (KEY_1, KEY_2, …) |
| Path Traversal | ✅ `os.path.basename()` applied to all uploaded filenames |
| Token Masking | ✅ JWT tokens partially masked in auth trace logs |

---

## Risk Register Summary

| Finding ID | Title | Severity | OWASP Category | Remediation Effort |
|------------|-------|----------|----------------|-------------------|
| FINDING-001 | Hardcoded API Key in `.env` | 🔴 Critical | A02: Cryptographic Failures | Low — rotate key, remove file |
| FINDING-002 | SSL Verification Disabled | 🔴 Critical | A02: Cryptographic Failures | Low — remove 3 lines |
| FINDING-003 | Wildcard CORS `*.vercel.app` | 🟠 High | A05: Security Misconfiguration | Low — update allowlist |
| FINDING-004 | `pickle.loads()` Warn-Only Mode | 🟠 High | A08: Software/Data Integrity | Medium — enforce all hashes |
| FINDING-005 | Auth Error Leaks Exception Detail | 🟠 High | A09: Security Logging Failures | Low — strip error detail |
| FINDING-006 | MIME Type Trust (Client Header) | 🟠 High | A03: Injection | Medium — add python-magic |
| FINDING-007 | Filename-Bypass Backdoor Flag | 🟠 High | A04: Insecure Design | Low — add env guard |
| FINDING-008 | IDOR on Guest Farm Audit Log | 🟠 High | A01: Broken Access Control | Low — strict ownership check |
| FINDING-009 | Debug Logs Exposed to All Users | 🟠 High | A02: Cryptographic Failures | Low — add admin check |
| FINDING-010 | Gemini Test Endpoint Leaks Key Info | 🟡 Medium | A02: Cryptographic Failures | Low — admin restriction |
| FINDING-011 | No RBAC / Role Differentiation | 🟡 Medium | A01: Broken Access Control | High — design + implement |
| FINDING-012 | Missing Content-Security-Policy | 🟡 Medium | A05: Security Misconfiguration | Low — add header |
| FINDING-013 | CORS `allow_methods=["*"]` | 🟡 Medium | A05: Security Misconfiguration | Low — restrict methods |
| FINDING-014 | Blocking I/O in Async Handlers | 🟡 Medium | A04: Insecure Design | Medium — wrap in thread pool |
| FINDING-015 | Unbounded Cache Growth | 🟢 Low | A04: Insecure Design | Low — add LIMIT/DELETE |
| FINDING-016 | Broad Exception Handling | 🟢 Low | A09: Logging Failures | Medium — structured logging |
| FINDING-017 | Audit Log Silently Swallows Errors | 🟢 Low | A09: Logging Failures | Low — return error status |
| FINDING-018 | Raw Exception in HTTP 500 Response | 🟢 Low | A02: Cryptographic Failures | Low — generic error message |

---

## Immediate Action Plan (Next 48 Hours)

```
Priority 1 — CRITICAL (Do Today)
  □ Rotate MANDI_API_KEY immediately on data.gov.in portal
  □ Remove backend/.env from git tracking: git rm --cached backend/.env
  □ Remove ctx.check_hostname = False and ctx.verify_mode = ssl.CERT_NONE (3 lines)

Priority 2 — HIGH (This Sprint)
  □ Replace wildcard CORS regex with explicit origin allowlist
  □ Add admin-only restriction to /api/v1/system/* endpoints
  □ Strip exception details from HTTP 401 error responses
  □ Add APP_ENV guard to KISAN_ALLOW_FILENAME_BYPASS
  □ Enforce pickle integrity hash for ALL .pkl files (no warn-only)
  □ Add server-side MIME detection via python-magic

Priority 3 — MEDIUM (This Month)
  □ Design and implement RBAC with Firebase custom claims
  □ Add Content-Security-Policy header to SecurityHeadersMiddleware
  □ Restrict CORS allow_methods to ["GET", "POST", "OPTIONS"]
  □ Wrap blocking ML inference in asyncio.to_thread()
```

---

## Compliance Mapping

| Standard | Status | Gap Areas |
|----------|--------|-----------|
| OWASP Top 10 2021 | ⚠️ Partial | A01 (Access Control), A02 (Secrets), A05 (CORS/CSP) |
| NIST SP 800-53 | ⚠️ Partial | AC-3 (Access Control), SC-8 (Transmission Integrity) |
| PCI DSS v4 | ❌ Not Ready | Secrets Management, Audit Logging, Access Control |
| GDPR | ⚠️ Partial | Data minimization in logs, access control for personal data |
| ISO 27001 | ⚠️ Partial | A.9 Access Control, A.10 Cryptography, A.12 Operations |

---

*This report was generated via automated static analysis and manual code review. Dynamic testing (DAST) with a live environment is recommended as a follow-up to validate runtime behavior of authentication, rate limiting, and IDOR protections.*
