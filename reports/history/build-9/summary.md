# Android Appium Test Summary

Build Number: #9
Execution Date: 2026-06-22 16:05:38

Total Tests: 8
Passed: 2
Failed: 6
Pass Rate: 25.0%

Report URL:
https://durga1610.github.io/kisan-mitra-web/reports/latest/execution-report.html

## Detailed Mobile Results

| # | Suite | Test Case | Status | Duration | Failure Reason |
| :---: | :--- | :--- | :---: | :---: | :--- |
| 1 | test_auth.py | `test_auth_client_validation` | 🔴 FAIL | 36.19s | driver = <appium.webdriver.webdriver.WebDriver (session="50950a0e-83f8-41bf-92b7-90c03fa32000")> ... |
| 2 | test_auth.py | `test_auth_invalid_credentials` | 🟢 PASS | 26.39s |  |
| 3 | test_features.py | `test_home_page_load` | 🔴 FAIL | 60.91s | auth_driver = <appium.webdriver.webdriver.WebDriver (session="e8f21537-f62a-45e9-813e-5ac08c86621... |
| 4 | test_features.py | `test_market_prices_page_load` | 🔴 FAIL | 59.13s | auth_driver = <appium.webdriver.webdriver.WebDriver (session="a8bdf10f-5cbb-4cef-9399-19ac3ed5897... |
| 5 | test_features.py | `test_ai_advisor_page_load` | 🔴 FAIL | 26.36s | @pytest.fixture(scope="function")     def driver():         """Initializes and yields Appium driv... |
| 6 | test_features.py | `test_disease_scanner_page_load` | 🔴 FAIL | 58.38s | auth_driver = <appium.webdriver.webdriver.WebDriver (session="a7f708f9-3807-4d6e-8d5c-ac85e471cf8... |
| 7 | test_features.py | `test_navigation_between_screens` | 🔴 FAIL | 59.83s | auth_driver = <appium.webdriver.webdriver.WebDriver (session="61988b49-6ff6-4092-a7a8-e36c195460e... |
| 8 | test_features.py | `test_responsive_ui_smoke` | 🟢 PASS | 36.13s |  |