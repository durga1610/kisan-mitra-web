# Security Review — Kisan Mitra Backend
**Assessment Date:** 2026-06-22  
**Assessor:** Senior Application Security Engineer / Penetration Tester  
**Application:** Kisan Mitra AI — Agricultural Advisory & Disease Detection Platform  
**Technology Stack:** Python 3.11 · FastAPI 0.110+ · SQLite · Firebase Auth · PyTorch · Google Gemini AI  
**Deployment:** Render Free Tier · Vercel (Frontend)

---

## PHASE 1 — BACKEND INVENTORY

| Category              | Detail                                                                          |
|-----------------------|---------------------------------------------------------------------------------|
| **Framework**         | FastAPI 0.110+                                                                  |
| **Language**          | Python 3.11                                                                     |
| **API Architecture**  | REST (JSON), single monolithic `main.py` (4,290 lines)                          |
| **Authentication**    | Firebase ID Token (JWT) via `HTTPBearer` → `firebase_admin.auth.verify_id_token`|
| **Authorization**     | Flat — single `get_current_user` dependency; no RBAC layer                     |
| **Database**          | SQLite (WAL mode) at `/var/data/app_data.db` or local fallback                  |
| **ORM**               | Raw SQLite3 (no ORM)                                                            |
| **API Documentation** | Swagger/ReDoc disabled in production (`docs_url=None`, `openapi_url=None`)      |
| **Middleware**        | SecurityHeadersMiddleware, CORSMiddleware, SlowAPI rate limiter                 |
| **File Uploads**      | `POST /api/v1/disease/detect` — image upload (JPEG/PNG/WebP, 10 MB max)        |
| **Session Handling**  | Stateless JWT; no server-side sessions                                          |
| **Third-Party APIs**  | Google Gemini AI, Firebase Admin SDK, data.gov.in Mandi API, OpenWeatherMap     |
| **ML Models**         | PyTorch ResNet18 / EfficientNet-B0, scikit-learn RandomForest, sentence-transformers, FAISS |
| **Deployment**        | Docker (python:3.11-slim), Uvicorn ASGI, Render platform                        |
| **Secrets Mgmt**      | `.env` + Render environment variables                                            |

---

## PHASE 2 — API ENDPOINT INVENTORY

| # | Endpoint | Method | Auth Required | Expected Roles | File |
|---|----------|--------|---------------|----------------|------|
| 1 | `/` | GET | ❌ No | Public | main.py:626 |
| 2 | `/healthz` | GET | ❌ No | Public | main.py:631 |
| 3 | `/api/v1/disease/detect` | POST | ✅ Yes | Authenticated | main.py:1289 |
| 4 | `/api/v1/disease/feedback` | POST | ✅ Yes | Authenticated | main.py:2471 |
| 5 | `/api/v1/disease/feedback/stats` | GET | ✅ Yes | Authenticated | main.py:2568 |
| 6 | `/api/v1/dataset/stats` | GET | ✅ Yes | Authenticated | main.py:2627 |
| 7 | `/api/v1/dataset/readiness` | GET | ✅ Yes | Authenticated | main.py:2635 |
| 8 | `/api/v1/dataset/training-readiness` | GET | ✅ Yes | Authenticated | main.py:2643 |
| 9 | `/api/v1/advisory/chat` | POST | ✅ Yes | Authenticated | main.py:2656 |
| 10 | `/api/v1/advisory/generate` | POST | ✅ Yes | Authenticated | main.py:2742 |
| 11 | `/api/v1/advisory/recommendations` | POST | ✅ Yes | Authenticated | main.py:2876 |
| 12 | `/api/v1/recommendations` | POST | ✅ Yes | Authenticated | main.py:2877 |
| 13 | `/api/v1/advisory/suitability` | POST | ✅ Yes | Authenticated | main.py:3098 |
| 14 | `/api/v1/advisory/daily-guidance` | POST | ✅ Yes | Authenticated | main.py:3121 |
| 15 | `/api/v1/daily-guidance` | POST | ✅ Yes | Authenticated | main.py:3122 |
| 16 | `/api/v1/advisory/reasoning` | POST | ✅ Yes | Authenticated | main.py:3554 |
| 17 | `/api/v1/fertilizer/recommend` | POST | ✅ Yes | Authenticated | main.py:3570 |
| 18 | `/api/v1/fertilizer` | POST | ✅ Yes | Authenticated | main.py:3571 |
| 19 | `/api/v1/crops/validate-before-planting` | POST | ✅ Yes | Authenticated | main.py:3614 |
| 20 | `/api/v1/crops/regional-suitability` | POST | ✅ Yes | Authenticated | main.py:3637 |
| 21 | `/api/v1/crops/audit-log` | POST | ✅ Yes | Authenticated | main.py:3659 |
| 22 | `/api/v1/market/prices` | GET | ✅ Yes | Authenticated | main.py:3738 |
| 23 | `/api/v1/market` | GET | ✅ Yes | Authenticated | main.py:3739 |
| 24 | `/api/v1/crop-recommendation/predict` | POST | ✅ Yes | Authenticated | main.py:2843 |
| 25 | `/api/v1/optimization/stats` | GET | ✅ Yes | Authenticated | main.py:4075 |
| 26 | `/api/v1/pest` | POST | ✅ Yes | Authenticated | main.py:4087 |
| 27 | `/api/v1/system/test-gemini` | GET | ✅ Yes | Authenticated | main.py:4154 |
| 28 | `/api/v1/system/debug-logs` | GET | ✅ Yes | Authenticated | main.py:4198 |
| 29 | `/api/v1/system/gemini-status` | GET | ✅ Yes | Authenticated | main.py:4216 |

**Total Endpoints: 29 | Public: 2 | Protected: 27**

---

## PHASE 3 — STATIC APPLICATION SECURITY TESTING (SAST)

---

### FINDING-001 — HARDCODED API KEY IN `.env` FILE COMMITTED TO REPOSITORY

| Attribute | Value |
|-----------|-------|
| **Severity** | 🔴 CRITICAL |
| **Type** | Sensitive Data Exposure / Secret Leakage |
| **File** | `backend/.env` (line 7) |
| **Endpoint** | N/A |

**Description:**  
The file `backend/.env` contains a real, active `MANDI_API_KEY` value (`579b464db66ec23bdd0000017c7ccd02bac445d36a5a228846357fa2`) and is committed directly to the repository. While the `.gitignore` is present and lists `.env`, the file exists in the workspace and was likely committed at some point. Any developer with repository access — or any attacker who gains read access — can obtain this key.

**Exploitation Scenario:**  
An attacker clones the repository or accesses historical git commits and extracts the `MANDI_API_KEY`. They then make unlimited calls to the data.gov.in Mandi API on behalf of the project, potentially exhausting rate limits or abusing the API account.

**Impact:**  
API key abuse, rate limit exhaustion, potential account suspension from data.gov.in, regulatory concerns if the key grants access to sensitive government data.

**Recommended Fix:**
```bash
# 1. Remove .env from git history
git rm --cached backend/.env
git commit -m "remove .env from tracking"

# 2. Rotate the MANDI_API_KEY immediately
# 3. Ensure .env is in .gitignore (already present but verify)
# 4. Use git-secrets or pre-commit hooks to prevent re-occurrence
```

---

### FINDING-002 — SSL CERTIFICATE VALIDATION DISABLED IN MANDI API CALL

| Attribute | Value |
|-----------|-------|
| **Severity** | 🔴 CRITICAL |
| **Type** | Improper Certificate Validation / MITM Vulnerability |
| **File** | `backend/main.py` (lines 3849–3851) |
| **Endpoint** | `GET /api/v1/market/prices` |

**Description:**  
The Mandi market prices API call explicitly disables SSL hostname verification and certificate verification:
```python
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
```
This makes every live API call to `https://api.data.gov.in` vulnerable to Man-in-the-Middle (MITM) attacks where an attacker positioned on the network can intercept the API key and tamper with the market price data returned to farmers.

**Exploitation Scenario:**  
On a compromised network (e.g., shared hosting, CDN edge), an attacker presents a forged TLS certificate. The backend accepts it without validation, allowing the attacker to: (1) capture the `MANDI_API_KEY` in transit, (2) return falsified crop prices to farmers, causing financial harm.

**Impact:**  
API key theft, data integrity violations, financial harm to farmers relying on market prices.

**Recommended Fix:**
```python
# Remove the insecure SSL bypass entirely
# The default ssl.create_default_context() validates certificates automatically
ctx = ssl.create_default_context()
# Do NOT set ctx.check_hostname = False or ctx.verify_mode = ssl.CERT_NONE
```

---

### FINDING-003 — OVERLY PERMISSIVE CORS CONFIGURATION WITH WILDCARD REGEX

| Attribute | Value |
|-----------|-------|
| **Severity** | 🟠 HIGH |
| **Type** | Broken Access Control / CORS Misconfiguration |
| **File** | `backend/main.py` (lines 166–184) |
| **Endpoint** | All endpoints |

**Description:**  
The CORS configuration uses a broad regex that matches any `*.vercel.app` subdomain and any localhost port:
```python
allow_origin_regex=r"https://.*\.vercel\.app|https?://(localhost|127\.0\.0\.1)(:\d+)?"
```
Additionally, `allow_credentials=True` and `allow_headers=["*"]` are set. This means any attacker who hosts a malicious site on `*.vercel.app` (which is trivially possible using the Vercel free tier) can make credentialed cross-origin requests to the backend API.

**Exploitation Scenario:**  
An attacker creates `https://evil-app.vercel.app`, hosts a JavaScript payload that makes authenticated requests to the Kisan Mitra API using the victim's Firebase token (obtained via XSS or other means), and exfiltrates sensitive farm data. The CORS policy will allow this.

**Impact:**  
Cross-origin data theft, unauthorized API access from attacker-controlled Vercel apps.

**Recommended Fix:**
```python
ALLOWED_ORIGINS = [
    "https://kisan-mitra.vercel.app",
    "https://kisan-mitra-web-olive.vercel.app",
    "http://localhost:3000",
    "http://localhost:8080",
]
# Remove the wildcard *.vercel.app regex — use explicit origin allowlist only
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Restrict to only used methods
    allow_headers=["Authorization", "Content-Type"],
)
```

---

### FINDING-004 — INSECURE DESERIALIZATION VIA `pickle.loads()` IN SECURITY UTILITY

| Attribute | Value |
|-----------|-------|
| **Severity** | 🟠 HIGH |
| **Type** | Insecure Deserialization (CWE-502) |
| **File** | `backend/security_utils.py` (line 98) |
| **Endpoint** | Startup model loading |

**Description:**  
`security_utils.py` performs a SHA-256 integrity check on `.pkl` files before calling `pickle.loads(data)`. While the hash check provides some protection, there are two significant issues:
1. The `safe_pickle_load` function has a **warn-only mode** where if a filename is not in `KNOWN_MODEL_HASHES`, it logs a warning but still calls `pickle.loads()`. Any `.pkl` file without a known hash is deserialized without integrity enforcement.
2. The underlying `pickle` format is inherently unsafe — if an attacker bypasses the hash check (e.g., by corrupting `KNOWN_MODEL_HASHES` or exploiting a TOCTOU race), RCE is possible.

**Exploitation Scenario:**  
If an attacker gains write access to the `models/` directory (e.g., via a path traversal vulnerability or compromised build pipeline), they can replace a `.pkl` file. If the filename is not in `KNOWN_MODEL_HASHES`, the warn-only mode loads it without verification, executing arbitrary Python code via `__reduce__`.

**Impact:**  
Remote Code Execution (RCE) on the server if malicious pickle payload is loaded.

**Recommended Fix:**
```python
# Option 1: Enforce hash for ALL pkl files — never warn-only
if not expected_digest:
    raise RuntimeError(f"No known hash for '{fname}'. Refusing to load.")

# Option 2: Replace pickle entirely with safer alternatives
import joblib  # safer than pickle for sklearn models
# or use torch.load(..., weights_only=True) for PyTorch models
```

---

### FINDING-005 — VERBOSE ERROR DETAIL LEAKAGE IN AUTH FAILURES

| Attribute | Value |
|-----------|-------|
| **Severity** | 🟠 HIGH |
| **Type** | Information Disclosure |
| **File** | `backend/main.py` (lines 299–305) |
| **Endpoint** | All authenticated endpoints |

**Description:**  
When Firebase token verification fails, the raw exception message is included in the HTTP 401 response body:
```python
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail=f"Invalid or expired authentication token. Error: {str(exc)}",
)
```
Firebase SDK exceptions can contain internal implementation details, Google API error codes, and stack traces that aid attackers in understanding the authentication mechanism.

**Exploitation Scenario:**  
An attacker probing authentication receives error details revealing Firebase project IDs, SDK version, token format requirements, or clock skew information that helps craft valid-looking tokens.

**Impact:**  
Information leakage aiding authentication bypass attempts.

**Recommended Fix:**
```python
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid or expired authentication token.",  # Generic message only
    headers={"WWW-Authenticate": "Bearer"},
)
# Log the actual error internally only
logger.warning("[Auth] Token verification failed: %s", exc)
```

---

### FINDING-006 — CONTENT-TYPE HEADER SPOOFING IN FILE UPLOADS (CLIENT-TRUSTED MIME)

| Attribute | Value |
|-----------|-------|
| **Severity** | 🟠 HIGH |
| **Type** | Unsafe File Upload / Input Validation |
| **File** | `backend/main.py` (lines 1299–1308) |
| **Endpoint** | `POST /api/v1/disease/detect` |

**Description:**  
File upload validation checks `file.content_type` which is a client-supplied HTTP header, not a server-side magic-byte inspection. A malicious client can send any file with a forged `Content-Type: image/jpeg` header, bypassing the MIME type check:
```python
if file.content_type not in ALLOWED_MIME_TYPES:
    raise HTTPException(400, ...)
```
While PIL `Image.open()` + `image.verify()` provides some additional protection, a crafted polyglot file (valid image + embedded payload) can pass both checks.

**Impact:**  
Potential bypass of upload validation, upload of non-image content disguised as images.

**Recommended Fix:**
```python
import magic  # python-magic library
contents = await file.read(MAX_FILE_SIZE + 1)
# Server-side magic byte inspection
detected_mime = magic.from_buffer(contents[:2048], mime=True)
if detected_mime not in ALLOWED_MIME_TYPES:
    raise HTTPException(400, f"Invalid file content. Detected: {detected_mime}")
```

---

### FINDING-007 — FILENAME-BYPASS BACKDOOR FLAG (`KISAN_ALLOW_FILENAME_BYPASS`)

| Attribute | Value |
|-----------|-------|
| **Severity** | 🟠 HIGH |
| **Type** | Business Logic Vulnerability / Configuration Risk |
| **File** | `backend/main.py` (lines 76, 1747) |
| **Endpoint** | `POST /api/v1/disease/detect` |

**Description:**  
A hidden bypass mechanism exists via the environment variable `KISAN_ALLOW_FILENAME_BYPASS`. When set to `"1"`, the disease detection pipeline skips ML model inference and returns a 98% confidence prediction based solely on the filename of the uploaded image:
```python
matched_class = match_filename_to_disease(file.filename) if ALLOW_FILENAME_BYPASS else None
```
If accidentally enabled in production (or if an attacker can set environment variables), any user can manipulate disease detection results by naming their upload file `tomato_early_blight.jpg`.

**Exploitation Scenario:**  
A misconfiguration or insider attacker sets `KISAN_ALLOW_FILENAME_BYPASS=1` in production. Any authenticated user can then obtain arbitrary disease predictions with 98% confidence by crafting filenames, bypassing the ML models entirely.

**Impact:**  
Complete bypass of AI disease detection system, potential for fraudulent insurance claims or misdiagnosis.

**Recommended Fix:**
```python
# Remove entirely from production code or add additional guards
ALLOW_FILENAME_BYPASS = (
    os.getenv("KISAN_ALLOW_FILENAME_BYPASS", "0") == "1"
    and os.getenv("APP_ENV", "production") == "development"
)
```

---

### FINDING-008 — IDOR: AUDIT LOG ENDPOINT ALLOWS "GUEST" FARM ACCESS BY ALL USERS

| Attribute | Value |
|-----------|-------|
| **Severity** | 🟠 HIGH |
| **Type** | Insecure Direct Object Reference (IDOR) / Broken Access Control |
| **File** | `backend/main.py` (lines 3695–3705) |
| **Endpoint** | `POST /api/v1/crops/audit-log` |

**Description:**  
The audit log endpoint performs farm ownership verification, but explicitly allows access to any farm whose `owner_id` is `"guest"`:
```python
if farm_owner not in (authenticated_uid, "guest") and authenticated_uid not in (farm_owner, "guest"):
    raise HTTPException(403, "You do not have permission...")
```
The seed data inserts a `"default"` farm with `owner_id = "guest"` accessible to all authenticated users. Any authenticated user can write audit records for the guest farm, and depending on the DB schema, potentially query other users' farms using the default farm ID.

**Impact:**  
Unauthorized data writes to shared farm records; potential for data pollution in audit logs.

**Recommended Fix:**
```python
# Strict ownership check — no guest exceptions
if farm_owner != authenticated_uid:
    raise HTTPException(403, "You do not have permission to access this farm.")
# Remove "guest" farm seed data or restrict it to admin users only
```

---

### FINDING-009 — SYSTEM DEBUG LOGS ENDPOINT EXPOSES SENSITIVE INTERNAL STATE

| Attribute | Value |
|-----------|-------|
| **Severity** | 🟠 HIGH |
| **Type** | Sensitive Data Exposure / Information Disclosure |
| **File** | `backend/main.py` (lines 4198–4213) |
| **Endpoint** | `GET /api/v1/system/debug-logs` |

**Description:**  
The `/api/v1/system/debug-logs` endpoint returns the last 200 lines of `stderr.log` to any authenticated user. This log file contains detailed internal server information including:
- Masked (but partially visible) API key fragments: `KEY_1...abc4`
- Firebase UID values of authenticated users
- Internal model inference timings
- Database query details
- Stack traces from errors

**Exploitation Scenario:**  
A low-privilege authenticated user (any farmer with a Firebase account) calls `GET /api/v1/system/debug-logs` and inspects the log contents to extract partial API keys, UIDs of other users, internal database paths, or error patterns useful for crafting attacks.

**Impact:**  
Information leakage aiding further attacks, partial API key exposure, user UID enumeration.

**Recommended Fix:**
```python
# Restrict to admin role only OR remove entirely from production
# Add admin check:
if user.get("uid") not in ADMIN_UIDS:
    raise HTTPException(403, "Insufficient permissions.")
# OR: Remove endpoint from production (APP_ENV check)
if APP_ENV != "development":
    raise HTTPException(404, "Not found.")
```

---

### FINDING-010 — GEMINI TEST ENDPOINT EXPOSES ACTIVE API KEY INDEX AND RESPONSE

| Attribute | Value |
|-----------|-------|
| **Severity** | 🟡 MEDIUM |
| **Type** | Sensitive Data Exposure |
| **File** | `backend/main.py` (lines 4154–4195) |
| **Endpoint** | `GET /api/v1/system/test-gemini` |

**Description:**  
The `/api/v1/system/test-gemini` endpoint returns:
- `active_key` label (e.g., `KEY_1`, `KEY_2`)
- HTTP response status from Gemini API
- Latency timing
- Raw response text from Gemini (first 400 characters)

This allows any authenticated user to probe the AI key rotation pool, understand which key is active, and potentially deduce quota exhaustion patterns.

**Impact:**  
Information leakage about internal API key management; could enable targeted quota exhaustion attacks.

**Recommended Fix:**  
Restrict to admin-only role, or remove from production deployment.

---

### FINDING-011 — NO ROLE-BASED ACCESS CONTROL (RBAC)

| Attribute | Value |
|-----------|-------|
| **Severity** | 🟡 MEDIUM |
| **Type** | Missing RBAC / Broken Access Control |
| **File** | `backend/main.py` (lines 261–308) |
| **Endpoint** | All endpoints |

**Description:**  
All 27 protected endpoints use the same single `get_current_user` dependency which only verifies that a valid Firebase token exists. There is no role differentiation between:
- Regular farmers (should access only their own farm data)
- Administrators (should access system status, debug logs, all farms)
- Internal services (ML model management, dataset endpoints)

System administration endpoints (`/api/v1/system/*`, `/api/v1/dataset/*`, `/api/v1/optimization/stats`) are accessible to any valid Firebase user.

**Impact:**  
Horizontal privilege escalation — any farmer can access admin/system endpoints.

**Recommended Fix:**
```python
# Add role claims to Firebase custom tokens
# Create admin dependency
async def require_admin(user: Dict = Depends(get_current_user)):
    if not user.get("admin"):  # Custom claim set via Firebase Admin SDK
        raise HTTPException(403, "Admin access required.")
    return user

# Apply to system endpoints
@router.get("/api/v1/system/debug-logs")
async def get_debug_logs(user: Dict = Depends(require_admin)):
    ...
```

---

### FINDING-012 — MISSING CONTENT SECURITY POLICY (CSP) HEADER

| Attribute | Value |
|-----------|-------|
| **Severity** | 🟡 MEDIUM |
| **Type** | Missing Security Headers / Configuration |
| **File** | `backend/main.py` (lines 150–163) |
| **Endpoint** | All endpoints |

**Description:**  
The `SecurityHeadersMiddleware` sets several security headers correctly but is missing the `Content-Security-Policy` header. Without CSP, any XSS vulnerability in a frontend consuming this API would have no additional browser-level protection.

**Recommended Fix:**
```python
response.headers["Content-Security-Policy"] = (
    "default-src 'self'; "
    "script-src 'self'; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data: blob:; "
    "connect-src 'self' https://*.firebaseapp.com https://*.googleapis.com"
)
```

---

### FINDING-013 — MISSING `allow_methods` RESTRICTION IN CORS

| Attribute | Value |
|-----------|-------|
| **Severity** | 🟡 MEDIUM |
| **Type** | CORS Misconfiguration |
| **File** | `backend/main.py` (line 182) |
| **Endpoint** | All endpoints |

**Description:**  
The CORS middleware uses `allow_methods=["*"]`, permitting all HTTP methods from cross-origin requests including `PUT`, `DELETE`, `PATCH`, and `OPTIONS` — none of which are used by the API.

**Recommended Fix:**
```python
allow_methods=["GET", "POST", "OPTIONS"],  # Only what's actually used
```

---

### FINDING-014 — SYNCHRONOUS BLOCKING I/O IN ASYNC ROUTE HANDLERS

| Attribute | Value |
|-----------|-------|
| **Severity** | 🟡 MEDIUM |
| **Type** | Business Logic / Availability Risk |
| **File** | `backend/main.py` (lines 2656, multiple locations) |
| **Endpoint** | `POST /api/v1/advisory/chat` |

**Description:**  
Several `async def` route handlers perform synchronous blocking operations (SQLite queries, ML model inference, file I/O) without using `asyncio.to_thread()` or a thread pool executor. The `/api/v1/advisory/chat` handler is `async def` but calls blocking `query_rag()` synchronously. This blocks the event loop and degrades concurrency under load.

**Impact:**  
Denial of Service under moderate load — all concurrent requests stall while one request is executing blocking I/O.

**Recommended Fix:**
```python
import asyncio

result, confidence, source = await asyncio.to_thread(
    query_rag, body.message, language=body.language, ...
)
```

---

### FINDING-015 — GEMINI RESPONSE CACHE HAS NO SIZE LIMIT

| Attribute | Value |
|-----------|-------|
| **Severity** | 🟢 LOW |
| **Type** | Resource Exhaustion / DoS |
| **File** | `backend/services/gemini_fallback.py` (lines 371–377) |
| **Endpoint** | Any endpoint using Gemini AI |

**Description:**  
The Gemini response cache (`gemini_response_cache` SQLite table) grows unboundedly. Every unique query generates a new cache row with up to 4,096 token responses stored. Over time, this can exhaust disk space on the Render free tier (which has limited persistent storage).

**Recommended Fix:**
```python
# Add cache size enforcement after insertion
fire_and_forget_write(
    "DELETE FROM gemini_response_cache WHERE id NOT IN "
    "(SELECT id FROM gemini_response_cache ORDER BY cached_at DESC LIMIT 10000)",
    ()
)
```

---

### FINDING-016 — OVERLY BROAD EXCEPTION HANDLING MASKS SECURITY ERRORS

| Attribute | Value |
|-----------|-------|
| **Severity** | 🟢 LOW |
| **Type** | Error Handling / Information Hiding |
| **File** | `backend/main.py` (multiple locations) |
| **Endpoint** | Multiple |

**Description:**  
Many routes use `except Exception as e:` with broad catch-all blocks that return safe defaults or log at WARNING level. While this prevents HTTP 500 errors, it can mask genuine security events (e.g., SQL injection attempts triggering SQLite errors, authentication bypass attempts).

**Recommended Fix:**  
Log all exceptions at ERROR level with structured context (user UID, endpoint, request ID) to enable security monitoring and alerting.

---

### FINDING-017 — AUDIT LOG FALLBACK SILENTLY SUCCEEDS ON DB FAILURE

| Attribute | Value |
|-----------|-------|
| **Severity** | 🟢 LOW |
| **Type** | Business Logic / Audit Integrity |
| **File** | `backend/main.py` (lines 3728–3730) |
| **Endpoint** | `POST /api/v1/crops/audit-log` |

**Description:**  
If the audit log INSERT fails, the endpoint returns `{"status": "partial", "message": "...crop planting can proceed"}` instead of an error. This means audit records can be silently lost without the caller knowing, compromising the integrity of the audit trail.

**Recommended Fix:**  
Return HTTP 500 or 503 when audit logging fails — audit trails should be non-optional for compliance.

---

### FINDING-018 — INTERNAL SERVER ERROR DETAIL EXPOSED ON GEMINI STATUS ENDPOINT

| Attribute | Value |
|-----------|-------|
| **Severity** | 🟢 LOW |
| **Type** | Information Disclosure |
| **File** | `backend/main.py` (lines 4281–4283) |
| **Endpoint** | `GET /api/v1/system/gemini-status` |

**Description:**  
```python
raise HTTPException(status_code=500, detail=str(e))
```
The raw Python exception message is returned to the caller in HTTP 500 responses, potentially leaking internal paths, database errors, or configuration state.

**Recommended Fix:**
```python
raise HTTPException(status_code=500, detail="Internal service error. Please try again.")
logger.error("[Status API] Error: %s", e)
```

---

## PHASE 4 — DYNAMIC TESTING NOTES (STATIC ANALYSIS ONLY)

No live environment URL was available for active DAST testing. The following observations are based on static code review of expected runtime behavior:

| Test Case | Expected Result | Finding |
|-----------|----------------|---------|
| Missing Bearer token | HTTP 401 | ✅ Correctly handled via `HTTPBearer(auto_error=False)` |
| Invalid/expired token | HTTP 401 | ✅ Firebase `verify_id_token` rejects |
| Rate limit exceeded (>10/min on detect) | HTTP 429 | ✅ SlowAPI limiter active |
| File upload >10MB | HTTP 413 | ✅ Size check implemented |
| Non-image MIME type upload | HTTP 400 | ⚠️ Client-header only — see FINDING-006 |
| Accessing another user's farm (IDOR) | HTTP 403 | ⚠️ Only audit-log endpoint checks ownership |
| SQL Injection in query params | Parameterized queries | ✅ All SQLite queries use parameterized `?` placeholders |
| Path traversal in filename | `os.path.basename()` used | ✅ Sanitized at line 1383 |
| Token replay | No token revocation | ⚠️ Firebase tokens valid for 1 hour — no server-side revocation list |

---

## SECURITY POSITIVES (WHAT IS DONE WELL)

- ✅ Firebase JWT authentication on all non-public endpoints
- ✅ SQL injection prevented via parameterized queries throughout
- ✅ File upload: MIME type + extension + size + PIL verification + content analysis
- ✅ Security headers: X-Content-Type-Options, X-Frame-Options, HSTS, X-XSS-Protection
- ✅ Rate limiting via SlowAPI on all endpoints (10–60/min per endpoint)
- ✅ API docs (Swagger/ReDoc) disabled in production
- ✅ Sensitive keys masked in logs (`KEY_1` not actual key values)
- ✅ Pydantic input validation with length constraints (max_length on all string fields)
- ✅ `torch.load(..., weights_only=True)` used for PyTorch model loading
- ✅ `os.path.basename()` on uploaded filenames to prevent path traversal
- ✅ WAL mode + busy_timeout on SQLite prevents lock issues
- ✅ Gemini API keys never logged (only index labels)
- ✅ `stdout`/`stderr` redirected to log file (not printed to terminal)
- ✅ Docker image uses `python:3.11-slim` (minimal attack surface)
- ✅ IDOR check implemented on audit-log endpoint (partial)
