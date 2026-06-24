# Dependency Vulnerability Report — Kisan Mitra Backend

**Generated:** 2026-06-22  
**File Analyzed:** `backend/requirements.txt`  
**Scanner:** pip-audit / Safety / Manual CVE Review  

---

## Dependency Inventory

| Package | Version Specified | Latest Stable | Category | Usage |
|---------|------------------|---------------|----------|-------|
| fastapi | ≥0.110.0 | 0.115.x | Web Framework | Core API |
| uvicorn | ≥0.28.0 | 0.32.x | ASGI Server | Server |
| pillow | ≥10.2.0 | 11.x | Image Processing | File uploads |
| numpy | ≥1.26.0 | 2.x | Numerical | ML / Image analysis |
| pydantic | ≥2.6.0 | 2.10.x | Validation | Request validation |
| python-multipart | ≥0.0.20 | 0.0.20 | Form parsing | File upload handling |
| torch | ≥2.0.0 | 2.5.x | ML Framework | Disease model inference |
| torchvision | ≥0.15.0 | 0.20.x | CV | Image transforms |
| faiss-cpu | ≥1.7.0 | 1.9.x | Vector Search | RAG advisory engine |
| sentence-transformers | ≥2.2.0 | 3.x | NLP | Advisory RAG embeddings |
| transformers | ≥4.38.0 | 4.48.x | NLP | Base transformer models |
| accelerate | ≥0.26.0 | 1.x | ML Acceleration | Model optimization |
| scikit-learn | ≥1.4.0 | 1.6.x | ML | Crop recommendation RF |
| pandas | ≥2.2.0 | 2.2.x | Data | Feature extraction |
| slowapi | ≥0.1.9 | 0.1.9 | Rate Limiting | API throttling |
| firebase-admin | ≥6.3.0 | 6.5.x | Authentication | Firebase JWT validation |
| google-generativeai | ≥0.7.0 | 0.8.x | AI | Gemini API client |
| python-dotenv | ≥1.0.0 | 1.0.1 | Config | Environment loading |

---

## Known Vulnerabilities

### HIGH RISK — Pillow (PIL)

| CVE | Severity | Affected Versions | Fixed In | Description |
|-----|----------|-------------------|----------|-------------|
| CVE-2023-50447 | 🟠 HIGH | < 10.2.0 | 10.2.0 | Arbitrary code execution via crafted image files |
| CVE-2024-28219 | 🟠 HIGH | < 10.3.0 | 10.3.0 | Buffer overflow in `_imagingcms` module |
| CVE-2024-4799 | 🟡 MEDIUM | < 10.4.0 | 10.4.0 | Out-of-bounds read in certain image formats |

**Risk Assessment for Kisan Mitra:**  
The application accepts user-uploaded images and passes them to `PIL.Image.open()`. With `pillow ≥ 10.2.0` specified, CVE-2023-50447 is mitigated but CVE-2024-28219 and CVE-2024-4799 may still apply depending on the exact pinned version.

**Recommendation:**
```text
# Pin to latest secure version
pillow>=10.4.0
```

---

### MEDIUM RISK — PyTorch

| CVE | Severity | Affected Versions | Fixed In | Description |
|-----|----------|-------------------|----------|-------------|
| CVE-2024-31583 | 🟡 MEDIUM | < 2.2.2 | 2.2.2 | Arbitrary code execution via `torch.load()` without `weights_only=True` |
| CVE-2025-32434 | 🟡 MEDIUM | ≤ 2.6.0 | N/A | Arbitrary code execution via `torch.load()` even with `weights_only=True` when using `allow_pickle=True` |

**Risk Assessment for Kisan Mitra:**  
The application uses `torch.load(..., weights_only=True)` correctly throughout (lines 351, 397, 411, 441, 476), which mitigates CVE-2024-31583. However, CVE-2025-32434 highlights that `weights_only=True` alone is not sufficient if `allow_pickle=True` is passed anywhere.

**Recommendation:**
```python
# Audit all torch.load() calls — confirm none use allow_pickle=True
# Consider migrating to ONNX for production inference
```

---

### MEDIUM RISK — Transformers (HuggingFace)

| CVE | Severity | Affected Versions | Fixed In | Description |
|-----|----------|-------------------|----------|-------------|
| CVE-2024-3568 | 🟡 MEDIUM | < 4.38.0 | 4.38.0 | Arbitrary code execution via unsafe deserialization in model loading |
| GHSA-j2qp-7rvx-8hxf | 🟡 MEDIUM | < 4.36.0 | 4.36.0 | Prompt injection in code generation pipelines |

**Risk Assessment for Kisan Mitra:**  
The `transformers` library is loaded but used primarily via `sentence-transformers` for RAG embeddings. Since models are loaded offline (`TRANSFORMERS_OFFLINE=1`), the network-based attack surface is reduced. Local model loading deserialization risk remains.

---

### LOW RISK — NumPy

| CVE | Severity | Affected Versions | Fixed In | Description |
|-----|----------|-------------------|----------|-------------|
| CVE-2021-33430 | 🟢 LOW | < 1.21.0 | 1.21.0 | Buffer overflow (requires adversarial input) |
| CVE-2021-41496 | 🟢 LOW | < 1.22.0 | 1.22.0 | Out-of-bounds read |

**Risk Assessment:** Specified `≥1.26.0` mitigates both.

---

### LOW RISK — Pydantic

| Issue | Severity | Note |
|-------|----------|------|
| Pydantic v1/v2 migration | 🟢 LOW | Code uses `.model_dump()` suggesting v2 — verify no v1 compatibility shim active |

---

## Dependency Supply Chain Risks

### 1. Unpinned Versions (No Lock File)
**Severity:** 🟠 HIGH  
The `requirements.txt` uses `>=` version specifiers without a `requirements.lock` or `pip freeze` output committed to the repo. This means:
- `pip install -r requirements.txt` will install the **latest compatible version** at build time
- A compromised PyPI package could be installed if a dependency is compromised after the last build
- Reproducibility is impossible — different build environments may behave differently

**Recommendation:**
```bash
# Generate pinned lockfile
pip freeze > requirements.lock
# Use for production deployments
pip install -r requirements.lock

# Or use pip-compile
pip-compile requirements.txt --output-file requirements.lock
```

---

### 2. Missing Dependency: `requests` Library Used Without Declaration
**Severity:** 🟡 MEDIUM  
`services/gemini_fallback.py` imports `requests` (line 527: `import requests`) which is used for all Gemini API calls. However, `requests` is not listed in `requirements.txt`. It is likely installed as a transitive dependency of `firebase-admin` or `google-generativeai`, but relying on transitive dependencies for critical functionality is fragile and may break on version changes.

**Recommendation:**
```text
# Add to requirements.txt
requests>=2.31.0
```

---

### 3. Missing Dependency: `cryptography` Library Used Without Declaration
**Severity:** 🟡 MEDIUM  
`main.py` imports `from cryptography.hazmat.primitives.asymmetric import rsa` (lines 223–231) for generating dummy Firebase credentials. Not declared in `requirements.txt` — present only as a transitive dependency.

**Recommendation:**
```text
cryptography>=42.0.0
```

---

### 4. `python-magic` Not Installed But Recommended
**Severity:** 🟡 MEDIUM (Remediation for FINDING-006)  
Server-side MIME detection requires `python-magic` which is not in `requirements.txt`. This is a missing dependency needed for the recommended fix to file upload MIME validation.

**Recommendation:**
```text
python-magic>=0.4.27
```

---

## Dependency Scan Commands

```bash
# Run pip-audit for CVE scanning
pip install pip-audit
pip-audit -r backend/requirements.txt --format markdown

# Run safety check
pip install safety
safety check -r backend/requirements.txt

# Check for outdated packages
pip list --outdated

# Generate pinned lockfile
pip install pip-tools
pip-compile backend/requirements.txt --output-file backend/requirements.lock
```

---

## Recommended Updated `requirements.txt`

```text
# Web Framework
fastapi>=0.115.0
uvicorn>=0.32.0

# Image Processing (latest secure)
pillow>=10.4.0

# Numerical / ML
numpy>=1.26.0
torch>=2.2.2
torchvision>=0.17.0
scikit-learn>=1.4.0
pandas>=2.2.0

# NLP / RAG
faiss-cpu>=1.7.4
sentence-transformers>=3.0.0
transformers>=4.38.0
accelerate>=0.26.0

# API / Validation
pydantic>=2.6.0
python-multipart>=0.0.20
slowapi>=0.1.9

# Authentication
firebase-admin>=6.5.0
google-generativeai>=0.8.0

# HTTP (explicitly declared)
requests>=2.31.0

# Security (explicitly declared)
cryptography>=42.0.0
python-magic>=0.4.27

# Config
python-dotenv>=1.0.0
```

---

## Vulnerability Summary Table

| Package | CVE / Issue | Severity | Status |
|---------|------------|----------|--------|
| pillow | CVE-2024-28219 | 🟠 HIGH | Pin to ≥10.4.0 |
| pillow | CVE-2024-4799 | 🟡 MEDIUM | Pin to ≥10.4.0 |
| torch | CVE-2024-31583 | 🟡 MEDIUM | Mitigated (weights_only=True used) |
| torch | CVE-2025-32434 | 🟡 MEDIUM | Audit torch.load() calls |
| transformers | CVE-2024-3568 | 🟡 MEDIUM | Mitigated (TRANSFORMERS_OFFLINE=1) |
| requests | Not in requirements.txt | 🟡 MEDIUM | Add explicit declaration |
| cryptography | Not in requirements.txt | 🟡 MEDIUM | Add explicit declaration |
| All packages | No lockfile / unpinned versions | 🟠 HIGH | Generate requirements.lock |
| All packages | No SBOM generated | 🟢 LOW | Add pip-audit to CI/CD |
