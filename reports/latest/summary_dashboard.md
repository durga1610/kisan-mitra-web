## 🚀 Consolidated CI/CD Dashboard
**Last Updated:** `2026-06-23 05:39:18` | **Run Trigger:** `ANDROID` | **SHA:** `8d2cfb92`

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
| **Android E2E** | 518 | 515 | 3 | 0 | 99.42% | 🔴 FAIL | [View Report](https://durga1610.github.io/kisan-mitra-web/reports/latest/android/execution-report.html) |
| **Backend Security Scan** | 37 | 35 | 2 | - | 0.0% | 🔴 FAIL | [View Report](https://durga1610.github.io/kisan-mitra-web/reports/latest/security-review.md) |
| **Secrets Scan** | - | - | 0 | - | 100.0% | 🟢 PASS | [View Logs](https://github.com/durga1610/kisan-mitra-web/actions/runs/28004352166) |
| **Unit Tests** | 0 | 0 | 0 | 0 | 0.0% | ➖ N/A | ➖ |

### 🛡️ Security Findings Summary
| Severity | Count | Action Required |
| :--- | :---: | :--- |
| 🔴 **Critical** | **2** | Requires immediate remediation |
| 🟠 **High** | **5** | Remediate within 1 sprint |
| 🟡 **Medium** | **30** | Remediate within 1 month |
| 🟢 **Low** | **0** | Remediate within next release |
| **Total Findings** | **37** | |

### 🔑 Secrets Leakage Log
🟢 **No secrets leakage detected in this repository.**
