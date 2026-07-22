# Security Retest Report — Kisan Mitra AI

**Date:** 2026-06-23  
**Auditor:** Lead Application Security Specialist  
**Scope:** Critical and High Security Findings Retest  

---

## 1. Overview

A post-remediation security scan and source audit was conducted on the **Kisan Mitra AI** backend repository to verify the effectiveness of the applied code fixes. The remediations successfully mitigated all 9 Critical and High severity findings.

---

## 2. Validation & Verification of Mitigations

### 🔴 FINDING-001: Hardcoded API Key in `.env`
*   **Fix Applied:** Replaced committed Gov-portal API key with environment placeholder `YOUR_MANDI_API_KEY`.
*   **Result:** **Resolved**. No active plaintext credentials exist in the workspace files.
*   **Security Verdict:** Pass.

### 🔴 FINDING-002: SSL Certificate Verification Disabled
*   **Fix Applied:** Removed check_hostname and verify_mode overrides in `backend/main.py` lines 3845–3847.
*   **Result:** **Resolved**. Outgoing network connections to `https://api.data.gov.in` now enforce strict SSL/TLS validation, preventing MITM attacks.
*   **Security Verdict:** Pass.

### 🟠 FINDING-003: Overly Permissive CORS Config
*   **Fix Applied:** Removed Vercel wildcard origin append and regex. Restrained `allow_origin_regex` to matching localhost development patterns.
*   **Result:** **Resolved**. Attacker-controlled Vercel subdomains can no longer make credentialed cross-origin requests.
*   **Security Verdict:** Pass.

### 🟠 FINDING-004: Insecure pickle.loads() Deserialization
*   **Fix Applied:** Removed skipped integrity warning blocks in `backend/security_utils.py`. The loader now throws a `RuntimeError` immediately if expected SHA-256 digests are absent.
*   **Result:** **Resolved**. Only explicitly hashing models registered in the signature table can be loaded, blocking malicious reducir payloads.
*   **Security Verdict:** Pass.

### 🟠 FINDING-005: Verbose Auth Error Detail Leakage
*   **Fix Applied:** Removed `str(exc)` details from HTTPException responses in `backend/main.py`.
*   **Result:** **Resolved**. Connection error details are suppressed from HTTP response bodies.
*   **Security Verdict:** Pass.

### 🟠 FINDING-006: Content-Type Header Spoofing
*   **Fix Applied:** Added the `check_image_signature` magic bytes inspect helper inside `/api/v1/disease/detect` in `backend/main.py`.
*   **Result:** **Resolved**. The backend validates actual file signatures (magic bytes for JPEG/PNG/WebP) and rejects fake content-type headers.
*   **Security Verdict:** Pass.

### 🟠 FINDING-007: Filename-Bypass Backdoor Flag
*   **Fix Applied:** Bound `ALLOW_FILENAME_BYPASS` to requiring `APP_ENV == "development"` in `backend/main.py`.
*   **Result:** **Resolved**. Backdoor simulation cannot be executed in production environments.
*   **Security Verdict:** Pass.

### 🟠 FINDING-008: Guest Farm IDOR in Audit Log
*   **Fix Applied:** Simplified crops audit log ownership verification block to strictly require `farm_owner == authenticated_uid` in `backend/main.py`.
*   **Result:** **Resolved**. Guest privilege bypass is deactivated.
*   **Security Verdict:** Pass.

### 🟠 FINDING-009: Debug Logs Endpoint Exposure
*   **Fix Applied:** Added validation claims checks on `/api/v1/system/debug-logs` requiring admin role claims or development context in `backend/main.py`.
*   **Result:** **Resolved**. Non-admin authenticated users are blocked from querying internal server logs.
*   **Security Verdict:** Pass.

---

## 3. Findings Register Summary

Following the audit, the active Critical and High findings count has been **reduced to zero** in the workspace.

| Finding Severity | Previous Count | Post-Remediation Count | Mitigation Status |
| :--- | :---: | :---: | :---: |
| 🔴 **Critical** | 2 | 0 | 100% Mitigated |
| 🟠 **High** | 7 | 0 | 100% Mitigated |
| 🟡 **Medium** | 5 | 5 | Tracked for release |
| 🟢 **Low** | 4 | 4 | Tracked for release |
| **Total** | **18** | **9** | **50% Reduced** |
