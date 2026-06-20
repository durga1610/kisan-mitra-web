# CORS Audit Report: Render ↔ Vercel Preflight Configuration

This report details the audit and fix for the CORS preflight (OPTIONS) failure observed when connecting the Vercel frontend to the Render backend.

## 1. Active Middleware Configuration
The backend application has exactly two registered middlewares:
1. **`CORSMiddleware`** (FastAPI / Starlette standard):
   - Intercepts and handles CORS preflight (`OPTIONS`) requests.
   - Evaluates incoming `Origin` against explicit allowlists and regular expressions.
   - Short-circuits preflight requests and returns a status of `HTTP 200 OK` directly without invoking downstream dependencies (e.g. Firebase Token Validation, route handlers).
2. **`SecurityHeadersMiddleware`** (Custom `BaseHTTPMiddleware`):
   - Injected on the response stack to append standard security headers (`X-Content-Type-Options`, `X-Frame-Options`, etc.).
   - Passes the request down to the endpoint or prior middlewares, and does not block/intercept `OPTIONS` requests.

No other custom router-level interceptors, custom handlers, or auth dependencies intercept incoming `OPTIONS` requests.

---

## 2. Allowed Origins & CORS Configuration Settings
The FastAPI backend `app` is now configured with the following CORS parameters in [backend/main.py](file:///c:/Users/durga/kisan_mitra/backend/main.py):

* **Explicit Allowed Origins (`allow_origins`)**:
  - `https://kisan-mitra-web-olive.vercel.app` (Target frontend origin)
  - `https://*.vercel.app` (Wildcard wildcard subdomain)
  - `https://kisan-mitra.vercel.app`
  - `http://localhost:3000`
  - `http://localhost:8080`
* **Allowed Origin Pattern (`allow_origin_regex`)**:
  - `r"https://.*\.vercel\.app|https?://(localhost|127\.0\.0\.1)(:\d+)?"`
  - *Note: Standard browsers block wildcard subdomains when `allow_credentials=True`. Compiling the regex dynamic match ensures all `*.vercel.app` subdomains successfully pass preflight checks with credentials enabled.*
* **Credentials Support (`allow_credentials`)**: `True` (Required for Firebase Bearer Token headers)
* **Allowed HTTP Methods (`allow_methods`)**: `["*"]` (Supports standard `GET`, `POST`, `OPTIONS`, `PUT`, `DELETE`, and custom methods)
* **Allowed HTTP Headers (`allow_headers`)**: `["*"]` (Permits standard and client custom headers like `authorization`, `content-type`)

---

## 3. Local Preflight Validation Results

A local preflight test was executed against the backend server running on `http://127.0.0.1:8000` using the target Vercel domain.

### Command:
```bash
curl -i -X OPTIONS http://127.0.0.1:8000/api/v1/advisory/chat \
  -H "Origin: https://kisan-mitra-web-olive.vercel.app" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: authorization,content-type"
```

### Resulting Output Headers:
```http
HTTP/1.1 200 OK
date: Sat, 20 Jun 2026 06:34:21 GMT
server: uvicorn
vary: Origin
access-control-allow-methods: DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT
access-control-max-age: 600
access-control-allow-credentials: true
access-control-allow-origin: https://kisan-mitra-web-olive.vercel.app
access-control-allow-headers: authorization,content-type
content-length: 2
content-type: text/plain; charset=utf-8

OK
```

**Audit Status**: **PASS** (Local validation returned `HTTP 200 OK` with credentials and allowed headers configured correctly).

---

## 4. Final Verification Instructions (From Vercel / Live Deployment)

Once the changes are pushed and auto-deployed on Render, verify the configuration by executing the following curl command:

```bash
curl -i -X OPTIONS https://kisan-mitra-backend-p21a.onrender.com/api/v1/advisory/chat \
  -H "Origin: https://kisan-mitra-web-olive.vercel.app" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: authorization,content-type"
```

### Expected Response:
1. Status code must be `HTTP/1.1 200 OK` or `HTTP/2 200`.
2. Header `access-control-allow-origin` must match `https://kisan-mitra-web-olive.vercel.app`.
3. Header `access-control-allow-credentials` must be `true`.
4. Header `access-control-allow-headers` must echo back or allow `authorization,content-type` (or `*`).
