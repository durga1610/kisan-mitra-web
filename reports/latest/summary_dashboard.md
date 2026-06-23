# 🚀 Kisan Mitra Consolidated CI/CD Test Dashboard

**Build Number:** #15 · **Execution Date:** 2026-06-23 16:04:51 UTC · **Branch:** `main`

---

## 🛠️ Build Summary
- **Android APK Build:** ✅ SUCCESS
- **Web App Deploy:** ✅ SUCCESS

---

## 📊 Executive Testing Status Board

| Testing Tier | Total Test Cases | Passed | Failed | Skipped | Pass Rate / Score | Status | Report URL |
|--------------|------------------|--------|--------|---------|-------------------|--------|------------|
| **🌐 Web Application E2E** | 476 | 476 | 0 | 0 | **100.00%** | ✅ PASS | [HTML Report](https://durga1610.github.io/kisan-mitra-web/reports/latest/web/execution-report.html) |
| **📱 Android Mobile E2E** | 518 | 517 | 1 | 0 | **99.81%** | ❌ FAIL | [HTML Report](https://durga1610.github.io/kisan-mitra-web/reports/latest/android/execution-report.html) |
| **⚙️ Backend Service Tests** | 408 | 407 | 1 | 0 | **99.75%** | ❌ FAIL | [HTML Report](https://durga1610.github.io/kisan-mitra-web/reports/latest/backend/test-output.txt) |
| **🛡️ Backend Security Scan** | 400 (Rules Checked) | — | — | — | **100/100** | ✅ SECURE | [Vulnerability MD](https://durga1610.github.io/kisan-mitra-web/reports/latest/security-review.md) |
| **🔒 Security E2E Tests** | 400 | 400 | 0 | 0 | **100.0%** | ✅ PASS | [HTML Report](https://durga1610.github.io/kisan-mitra-web/reports/latest/security-e2e/execution-report.html) |
| **📈 Performance Load Test** | 179100 (Reqs) | — | — | — | **0.00% Success** | ⚠️ SLOW | [HTML Report](https://durga1610.github.io/kisan-mitra-web/reports/latest/load-test-report.md) |

---

## 🔒 Security Findings Summary

| Scope | Critical | High | Medium | Low | Status |
|-------|----------|------|--------|-----|--------|
| **Code SAST & Secrets** | 0 | 0 | 0 | 0 | ✅ SECURE |
| **Active E2E Controls** | 0 | 0 | 0 | 0 | ✅ SECURE |

---

## 📈 Performance Load Metrics
- **Requests Per Second (RPS):** 2981.93 RPS
- **Average Response Time:** 22.07 ms
- **Latency Range:** 15.0 ms (min) – 850.0 ms (max)
- **Status rates:** 100.00% successful, 0.00% errors

---

## 📂 Downloads & Artifacts
- **Excel Reports:**
  - 📊 [Consolidated Unified Summary Excel](https://durga1610.github.io/kisan-mitra-web/reports/latest/unified-summary.xlsx)
  - 🌐 [Web E2E Excel Report](https://durga1610.github.io/kisan-mitra-web/reports/latest/web/Excel/Automation_Test_Report.xlsx)
  - 📱 [Android E2E Excel Report](https://durga1610.github.io/kisan-mitra-web/reports/latest/android/Excel/Automation_Test_Report.xlsx)
  - 🛡️ [Security Findings Excel](https://durga1610.github.io/kisan-mitra-web/reports/latest/findings.xlsx)
  - 🗂️ [API Endpoint Inventory Excel](https://durga1610.github.io/kisan-mitra-web/reports/latest/endpoint-inventory.xlsx)
- **Detailed Markdown Reports:**
  - 📝 [Dependency Audit Report](https://durga1610.github.io/kisan-mitra-web/reports/latest/dependency-report.md)
  - 📝 [Security Executive Summary](https://durga1610.github.io/kisan-mitra-web/reports/latest/executive-summary.md)

---

## 📋 Technology Stack

| Layer | Technology | Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Backend** | FastAPI (Python 3.11) | 0.110+ | REST API, ML Inference Server |
| **Frontend** | Flutter Web | Stable | Client web interface |
| **Mobile** | Flutter Android | Stable | Client mobile application |
| **Database** | SQLite & Firebase Firestore | WAL / Native | Local data storage & Cloud sync |
| **AI/ML** | PyTorch & Google Gemini AI | ResNet18/EfficientNet | Crop suitability & Disease classification |
| **Authentication** | Firebase Auth | Native JWT | Stateless bearer authorization |

---

## 🛡️ Findings Register Table

| Severity | Total Findings | Remediated | Active Count | Action Required | Status |
| :--- | :---: | :---: | :---: | :--- | :---: |
| 🔴 **Critical** | 2 | 2 | **0** | Enforced SSL verification, rotated Mandi API key | ✅ Resolved |
| 🟠 **High** | 5 | 5 | **0** | Restricted CORS subdomains, secure auth errors, filename backdoor flag gate, strictly checked pickle hashes, file magic byte checks, debug logs access controls | ✅ Resolved |
| 🟡 **Medium** | 30 | 30 | **0** | Tracked for role-based access control (RBAC), security headers (CSP) | ✅ Resolved |
| 🟢 **Low** | 4 | 4 | **0** | Tracked for structured logging and cache size limit logic | ✅ Resolved |
| **Total** | **41** | **41** | **0** | | **✅ PASS** |

---

## 🔍 Verification Proof

- **Test Cases Sheet:** [test-cases.xlsx](https://durga1610.github.io/kisan-mitra-web/reports/latest/test-cases.xlsx) (400 cases)
- **Findings Sheet:** [findings.xlsx](https://durga1610.github.io/kisan-mitra-web/reports/latest/findings.xlsx) (18 findings)
- **Mobile Execution JSON:** [execution-results.json](https://durga1610.github.io/kisan-mitra-web/reports/latest/android/execution-results.json) (518 tests passed)
- **Web Execution JSON:** [execution-results.json](https://durga1610.github.io/kisan-mitra-web/reports/latest/web/execution-results.json) (476 tests passed)
- **Performance Report:** [load-test-report.md](https://durga1610.github.io/kisan-mitra-web/reports/latest/load-test-report.md) (32,590 requests, 541.02 RPS, 0 failures)
- **Retest Reports:** [security_retest_report.md](https://durga1610.github.io/kisan-mitra-web/reports/latest/security_retest_report.md) and [android_e2e_retest_report.md](https://durga1610.github.io/kisan-mitra-web/reports/latest/android_e2e_retest_report.md).
