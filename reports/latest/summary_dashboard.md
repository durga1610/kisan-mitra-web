## 🚀 Consolidated CI/CD Dashboard
**Last Updated:** `2026-06-23 08:31:20` | **Run Trigger:** `ANDROID` | **SHA:** `caa523d4`

### 🛠️ Technology Stack
| Layer | Technology | Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Backend** | FastAPI (Python 3.11) | 0.110+ | REST API, ML Inference Server |
| **Frontend** | Flutter Web | Stable | Client web interface |
| **Mobile** | Flutter Android | Stable | Client mobile application |
| **Database** | SQLite & Firebase Firestore | WAL / Native | Local data storage & Cloud sync |
| **AI/ML** | PyTorch & Google Gemini AI | ResNet18/EfficientNet | Crop suitability & Disease classification |
| **Authentication** | Firebase Auth | Native JWT | Stateless bearer authorization |

### 📊 Executive Testing Status Board
| Check / Test Suite | Total Run | Passed | Failed | Skipped | Pass Rate | Status | Report URL |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Web E2E** | 476 | 476 | 0 | 0 | 100.0% | 🟢 PASS | [View Report](https://durga1610.github.io/kisan-mitra-web/reports/latest/web/execution-report.html) |
| **Android E2E** | 518 | 517 | 1 | 0 | 99.81% | 🔴 FAIL | [View Report](https://durga1610.github.io/kisan-mitra-web/reports/latest/android/execution-report.html) |
| **Backend Security Scan** | 37 | 35 | 2 | - | 0.0% | 🔴 FAIL | [View Report](https://durga1610.github.io/kisan-mitra-web/reports/latest/security-review.md) |
| **Secrets Scan** | - | - | 7 | - | 0.0% | 🔴 FAIL | [View Logs](https://github.com/durga1610/kisan-mitra-web/actions/runs/28011265423) |
| **Unit Tests** | 0 | 0 | 0 | 0 | 0.0% | ➖ N/A | ➖ |
| **Load Testing** | 32590 reqs / 541.0 RPS / Avg 177.6ms | - | 0 | - | 100.0% | 🟢 PASS | [View Report](https://durga1610.github.io/kisan-mitra-web/reports/latest/load-test-report.md) |

### 🛡️ Security Findings Summary
| Severity | Count | Action Required |
| :--- | :---: | :--- |
| 🔴 **Critical** | **2** | Requires immediate remediation |
| 🟠 **High** | **5** | Remediate within 1 sprint |
| 🟡 **Medium** | **30** | Remediate within 1 month |
| 🟢 **Low** | **0** | Remediate within next release |
| **Total Findings** | **37** | |

### 🔑 Secrets Leakage Log
| Rule ID | File Name | Authors |
| :--- | :--- | :--- |
| gcp-api-key | android/app/google-services.json | durga1610 |
| gcp-api-key | backend/scratch/live_production_checklist_verifier.py | durga1610 |
| gcp-api-key | lib/firebase_options.dart | durga1610 |
| gcp-api-key | lib/firebase_options.dart | durga1610 |
| gcp-api-key | lib/firebase_options.dart | durga1610 |
| gcp-api-key | lib/firebase_options.dart | durga1610 |
| gcp-api-key | lib/firebase_options.dart | durga1610 |
