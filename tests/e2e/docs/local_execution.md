# Local Execution Guide — Kisan Mitra Web E2E

This guide details the setup and execution steps to run the Web E2E Selenium tests locally.

## Prerequsite Requirements
1. **Python 3.10+** (Ensure Python is in your system PATH).
2. **Google Chrome browser** installed.
3. **Chromedriver** corresponding to your Chrome version (or let Selenium WebDriver manager fetch it automatically).

## Local Installation Setup
1. Clone the repository and navigate to the E2E web testing root:
   ```bash
   cd tests/e2e
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Executing the Test Suite
1. Ensure the web application is running, or set `BASE_URL` to target the live site:
   ```bash
   # Set target URL
   $env:BASE_URL="https://durga1610.github.io/kisan-mitra-web/"
   ```
2. Execute the Python web test runner:
   ```bash
   python run_tests.py
   ```

## Viewing Test Results
After execution completes, view the output files in `tests/e2e/Test Results/`:
- **HTML Grid Dashboard**: `HTML/execution-report.html`
- **Charts Dashboard**: `HTML/dashboard.html`
- **Spreadsheets**: `Excel/Automation_Test_Report.xlsx`
- **Console execution log**: `Logs/execution.log`
