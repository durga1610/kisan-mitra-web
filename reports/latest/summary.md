# Android Appium Test Summary

Build Number: #5
Execution Date: 2026-06-22 14:01:45

Total Tests: 8
Passed: 3
Failed: 5
Pass Rate: 37.5%

Report URL:
https://durga1610.github.io/kisan-mitra-web/reports/latest/execution-report.html

## Detailed Mobile Results

| # | Suite | Test Case | Status | Duration | Failure Reason |
| :---: | :--- | :--- | :---: | :---: | :--- |
| 1 | test_auth.py | `test_auth_client_validation` | 🟢 PASS | 19.01s |  |
| 2 | test_auth.py | `test_auth_invalid_credentials` | 🟢 PASS | 14.39s |  |
| 3 | test_features.py | `test_home_page_load` | 🟢 PASS | 19.34s |  |
| 4 | test_features.py | `test_market_prices_page_load` | 🔴 FAIL | 50.85s | auth_driver = <appium.webdriver.webdriver.WebDriver (session="6f3351bd-fceb-4cca-901a-6a1f50a7f7e... |
| 5 | test_features.py | `test_ai_advisor_page_load` | 🔴 FAIL | 49.57s | auth_driver = <appium.webdriver.webdriver.WebDriver (session="7bb29e16-7452-4c9c-a87f-6907764daf4... |
| 6 | test_features.py | `test_disease_scanner_page_load` | 🔴 FAIL | 49.57s | auth_driver = <appium.webdriver.webdriver.WebDriver (session="204841d0-8078-4f8d-a58e-8f54cc523e8... |
| 7 | test_features.py | `test_navigation_between_screens` | 🔴 FAIL | 49.74s | auth_driver = <appium.webdriver.webdriver.WebDriver (session="ee47b003-6268-4a52-be9e-3182fb8279d... |
| 8 | test_features.py | `test_responsive_ui_smoke` | 🔴 FAIL | 20.34s | auth_driver = <appium.webdriver.webdriver.WebDriver (session="40354a37-cfa0-4db9-8966-43d2f675bb9... |