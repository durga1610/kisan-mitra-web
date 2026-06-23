# Local Execution Guide — Kisan Mitra Mobile E2E

This guide details the setup and execution steps to run the mobile E2E Appium tests locally.

## Prerequsite Requirements
1. **Python 3.10+** (Ensure Python is in your system PATH).
2. **Node.js v18+** & npm.
3. **Android Studio** with Android SDK, Emulator, and Command Line Tools configured.
4. **Appium 2.x** server:
   ```bash
   npm install -g appium
   appium driver install uiautomator2
   ```

## Local Installation Setup
1. Clone the repository and navigate to the mobile testing root:
   ```bash
   cd tests/mobile_e2e
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Executing the Test Suite
1. Ensure an Android Emulator is running:
   ```bash
   emulator -avd <Your_AVD_Name>
   ```
2. Build the latest debug APK in the flutter directory:
   ```bash
   flutter build apk --debug
   ```
3. Start the Appium Server:
   ```bash
   appium --port 4723
   ```
4. Execute the Python mobile test runner:
   ```bash
   python run_mobile_tests.py
   ```

## Viewing Test Results
After execution completes, view the output files in `tests/mobile_e2e/Test Results/`:
- **HTML Grid Dashboard**: `HTML/execution-report.html`
- **Charts Dashboard**: `HTML/dashboard.html`
- **Trends History**: `HTML/trends.html`
- **Spreadsheets**: `Excel/Automation_Test_Report.xlsx`
- **Console execution log**: `Logs/execution.log`
