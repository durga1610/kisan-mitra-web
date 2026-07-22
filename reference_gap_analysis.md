# Reference Gap Analysis — TrackBack vs. Kisan Mitra

This document outlines the architectural and reporting gaps identified between the reference repository (`TrackBack-Web-PDD`) and the target repository (`Kisan Mitra`), detailing how each gap will be bridged.

---

## 1. Workflow Architecture & Stage Ordering

| Reference Stage Structure (8 Jobs) | Current Kisan Mitra Status | Gap Identified | Remediation Plan |
| :--- | :--- | :--- | :--- |
| `security-scan` | Implemented | None | Keep job and run static tools (Semgrep, Bandit, pip-audit, safety, Trivy, custom check). |
| `build-web` | Implemented | None | Build and deploy Flutter web client. |
| `verify-web` | Implemented | None | Verify HTTP status code 200 from GitHub Pages. |
| `web-e2e` | Implemented | Runs E2E & Load test together. | Split load test execution visually in the dashboard. |
| `build-apk` | Implemented | None | Compile Flutter debug APK. |
| `android-e2e` | Implemented | None | Run Appium tests on Android emulator. |
| `backend-tests` | Implemented | None | Run Pytest backend test suite. |
| `unified-summary` | Implemented | Missing `unified-summary-reports` artifact upload. | Add step to upload `unified-summary-reports` zipped folder. |

---

## 2. Artifact & Directory Structure Gaps

On the runner during the `unified-summary` job:
- **Reference Directory Pattern:**
  - `web-reports/` -> Downloads `selenium-e2e-reports`
  - `android-reports/` -> Downloads `android-e2e-reports`
  - `backend-reports/` -> Downloads `backend-test-reports`
  - `security-reports/` -> Downloads `security-reports`
  - `load-test-reports/` -> Downloads `load-test-reports`
- **Kisan Mitra Directory Pattern:**
  - `all-artifacts/selenium-e2e-reports/`
  - `all-artifacts/android-e2e-reports/`
  - `all-artifacts/backend-test-reports/`
  - `all-artifacts/security-reports/`
  - `all-artifacts/load-test-reports/`
- **Gap:** Kisan Mitra's summary generator `tests/generate_consolidated_summary.py` expects the `all-artifacts/` prefix, which diverges from the reference paths.
- **Remediation:** We will align the download paths in `consolidated-pipeline.yml` to use the exact reference folder names (`web-reports/`, `android-reports/`, `backend-reports/`, `security-reports/`, `load-test-reports/`), and update `tests/generate_consolidated_summary.py` to parse from these aligned directories.

---

## 3. Summary Dashboard Layout Gaps

- **Reference Sections:**
  - `Build Summary` (Android / Web statuses)
  - `Executive Testing Status Board` (Testing Tier, Total Cases, Passed, Failed, Skipped, Pass Rate / Score, Status, Report URL)
  - `Security Findings Summary` (Code SAST & Secrets vs. Active E2E Controls)
  - `Performance Load Metrics` (RPS, Average Response, Latency Range, Success/Error rates)
  - `Downloads & Artifacts` (Excel Reports, Detailed Markdown Reports links)
- **Kisan Mitra Sections:**
  - `Technology Stack`
  - `Testing & Validation Status Board`
  - `Security Findings & Vulnerabilities Summary`
  - `Findings Register Table`
  - `Verification Proof`
- **Gap:** The visual structure and headings in Kisan Mitra's summary dashboard do not match the reference dashboard format.
- **Remediation:** We will update `tests/generate_consolidated_summary.py` to output the exact visual dashboard layout of the reference (matching headers, tables, and styling), while appending the `Technology Stack` and `Findings Register Table` to provide a complete, verified picture of Kisan Mitra's real audit metrics.

---

## 4. Test Suite Coverage & Execution Gaps

1. **Security Validation Suite (Phase 6 & 9):**
   - **Gap:** The reference has 300 static scan rules. Kisan Mitra has **400 security validation test cases** (defined in `test-cases.xlsx`). The dashboard must reflect these 400 test cases and their execution pass rate from actual results.
   - **Remediation:** Parse the actual execution statistics of the 400 validation cases. Ensure findings count (18 total, 9 critical/high resolved, 9 medium/low open) is strictly separated from the execution test case count.
2. **Web E2E (Phase 7):**
   - **Gap:** Expanding Selenium coverage to ensure all real user flows (Login, Weather, Market, AI Advisor, Disease Scanner, Farm Management, Settings, etc.) are tested.
   - **Remediation:** Ensure Selenium tests execute these flows against the deployed web app and save actual execution states to `execution-results.json` and Excel reports.
3. **Android E2E (Phase 8):**
   - **Gap:** Expanding Appium coverage for mobile flows.
   - **Remediation:** Run Appium tests covering Authentication, Navigation, Prices, Weather, AI Advisor, Disease, Profile, Settings, and Orientation on the Android emulator runner.
4. **Performance Testing (Phase 10):**
   - **Gap:** Run actual backend load testing and capture throughput, latency, and error metrics.
   - **Remediation:** Execute the local load test tool (`tests/perf_load_test.py`), dump results into `Vulnerability Test Results/load-test-report.md`, and parse them dynamically.
