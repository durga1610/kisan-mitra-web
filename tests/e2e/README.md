# Kisan Mitra - E2E Selenium Test Automation Guide

This directory contains the Selenium E2E test automation framework for testing the Kisan Mitra web client. The tests are designed to execute against the live deployment of the application (e.g., GitHub Pages) rather than localhost.

---

## 1. Directory Structure

```
tests/e2e/
├── conftest.py                   # WebDriver setup and hooks (screenshot on fail)
├── run_tests.py                  # Main orchestrator running tests and compiling reports
├── requirements.txt              # Python packages required
├── README.md                     # This documentation guide
│
├── pages/                        # Page Object Model (POM) layer
│   ├── base_page.py              # Common locator and browser actions
│   ├── login_page.py             # Authentication page selectors & helpers
│   ├── home_page.py              # Home/dashboard layout elements
│   ├── advisory_page.py          # AI advisory chat elements
│   └── disease_scan_page.py      # Leaf scan file upload & Grad-CAM outputs
│
├── test_suites/                  # Test suites targeting specific features
│   ├── test_auth.py              # Client validations & invalid credentials
│   ├── test_navigation.py        # Unauthenticated URL redirect checks
│   └── test_features.py          # Navigation guards on sub-features
│
└── reporters/                    # Result reporting engines
    ├── excel_reporter.py         # Standard Excel report compiler
    └── html_reporter.py          # Interactive HTML dark-mode report compiler
```

---

## 2. Local Setup and Execution

To run tests locally against a deployed environment:

### Prerequisites
1. **Python 3.11+** installed on your system.
2. **Google Chrome** browser.
3. **Chrome WebDriver** (matching your Chrome browser version). Ensure it's in your system PATH, or let Selenium Manager handle it automatically (default in Selenium 4+).

### Steps
1. Navigate to the `tests/e2e` directory:
   ```powershell
   cd tests/e2e
   ```

2. Create a virtual environment and activate it (optional but recommended):
   ```powershell
   python -m venv venv
   # On Windows:
   .\venv\Scripts\Activate.ps1
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install the required dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

4. Execute the tests:
   - To test against the default live URL (`https://durga1610.github.io/kisan-mitra-web/`):
     ```powershell
     python run_tests.py
     ```
   - To test against a custom environment/URL, set the `BASE_URL` environment variable:
     ```powershell
     # Windows PowerShell:
     $env:BASE_URL="https://example.github.io/kisan-mitra-web/"
     python run_tests.py

     # macOS/Linux Bash:
     BASE_URL="https://example.github.io/kisan-mitra-web/" python run_tests.py
     ```

---

## 3. CI/CD Integration (GitHub Actions)

The framework is integrated into the `.github/workflows/deploy-and-test.yml` workflow, which runs automatically on every push and pull request targeting the `main` or `master` branches.

### Workflow Stages
1. **Build & Deploy Web Client**: Compiles the Flutter web application using the standard HTML renderer and `/kisan-mitra-web/` base href, then deploys to GitHub Pages.
2. **Availability Probe**: Actively curls the deployed GitHub Pages URL until it returns HTTP `200` (up to 30 attempts, 10s delay).
3. **Run E2E Tests**: Spawns a headless Chrome browser, sets the `BASE_URL` environment variable, and runs `run_tests.py`.
4. **Publish Step Summary**: Appends the test metrics summary from `summary.md` directly to the GitHub Actions job run interface.
5. **Publish Artifacts**: Uploads the complete `tests/e2e/Test Results/` folder as a build artifact.

---

## 4. Test Results & Reports

After execution completes, the results are formatted and stored in the following folder structure under `tests/e2e/Test Results/`:

- **Excel Report**: `Test Results/Excel/Automation_Test_Report.xlsx`  
  *A professional spreadsheet showing overall dashboard statistics and detailed test metadata.*
- **HTML Report**: `Test Results/HTML/execution-report.html`  
  *An interactive HTML dashboard styled in a premium dark mode.*
- **Screenshots**: `Test Results/Screenshots/`  
  *Contains screenshots taken automatically when any assertion or wait condition fails.*
- **Execution Logs**: `Test Results/Logs/execution.log`  
  *A detailed log file replicating standard stdout/stderr outputs from the test suite.*
- **Markdown Summary**: `Test Results/Summary/summary.md`  
  *A clean text summary used to present status directly in the GitHub Actions runner dashboard.*
