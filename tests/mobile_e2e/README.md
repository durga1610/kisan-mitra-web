# Kisan Mitra - Android Appium E2E Test Automation Guide

This directory contains the Appium mobile E2E test automation framework for testing the Kisan Mitra Android client on emulators.

---

## 1. Directory Structure

```
tests/mobile_e2e/
├── conftest.py                   # Appium driver options and test capabilities
├── run_mobile_tests.py           # Main runner script to trigger pytest and compile reports
├── requirements.txt              # Python requirements
├── README.md                     # This documentation guide
│
├── pages/                        # Page Object Model (POM) layer
│   ├── base_page.py              # Common mobile gestures and visibility waits
│   ├── login_page.py             # Auth screen inputs & verification selectors
│   ├── home_page.py              # Dashboard layout and tab elements
│   ├── advisory_page.py          # Chatbot panel inputs & send triggers
│   └── disease_scan_page.py      # Leaf scan triggering elements
│
├── test_suites/                  # Functional test definitions
│   ├── test_auth.py              # Client validations & invalid credentials testing
│   └── test_features.py          # Dashboard features and device orientation rotation
│
└── reporters/                    # Result reporting engines
    ├── excel_reporter.py         # Custom Excel report compiler
    └── html_reporter.py          # Dark-theme HTML report builder
```

---

## 2. Local Setup and Execution

To run mobile E2E tests locally on an Android Emulator:

### Prerequisites
1. **Node.js (v18+)** installed.
2. **Android Studio** and **Android SDK** configured with platform tools in your system PATH.
3. **Python 3.11+** installed.
4. An active **Android Emulator** running on your system.

### Steps
1. **Build the Debug APK**:
   In the repository root folder, compile the Flutter Android debug APK:
   ```powershell
   flutter build apk --debug
   ```
   *Note: This creates the target APK at `build/app/outputs/flutter-apk/app-debug.apk`.*

2. **Install Appium Server and Driver**:
   Install the Appium Server CLI and its UiAutomator2 driver globally:
   ```powershell
   npm install -g appium
   appium driver install uiautomator2
   ```

3. **Start Appium Server**:
   Start Appium on port `4723`:
   ```powershell
   appium --port 4723
   ```

4. **Install Python E2E Requirements**:
   Navigate to the `tests/mobile_e2e` directory, create a virtual environment, and install dependencies:
   ```powershell
   cd tests/mobile_e2e
   python -m venv venv
   # On Windows:
   .\venv\Scripts\Activate.ps1
   # On macOS/Linux:
   source venv/bin/activate

   pip install -r requirements.txt
   ```

5. **Run the Test Runner**:
   Ensure your Android Emulator is booted and online (check with `adb devices`), then run:
   ```powershell
   python run_mobile_tests.py
   ```

---

## 3. CI/CD Integration (GitHub Actions)

The mobile tests are integrated in the `.github/workflows/android-e2e.yml` workflow, which triggers automatically on every push or PR targeting `main`/`master`.

### Automated Flow
1. **Build APK**: Compiles the debug APK.
2. **Boot Emulator**: Sets up an x86_64 emulator on a hardware-accelerated Linux runner (`ubuntu-latest`).
3. **Execute E2E Tests**: Boots Appium, installs the APK, and runs `run_mobile_tests.py`.
4. **Publish reports**: Commits and pushes the HTML execution reports to the `gh-pages` branch, archiving them under:
   - Latest Report: `reports/latest/execution-report.html`
   - Build History: `reports/history/build-<build_number>/execution-report.html`
5. **Actions step summary**: Outputs the test metrics and the live reports URL on the GitHub Actions interface.

---

## 4. Live Reports

Once the workflow finishes, the HTML execution dashboard is available online:
`https://durga1610.github.io/kisan-mitra-web/reports/latest/execution-report.html`
