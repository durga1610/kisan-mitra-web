# Android Appium Test Summary

Build Number: #11
Execution Date: 2026-06-22 16:38:06

Total Tests: 8
Passed: 5
Failed: 3
Pass Rate: 62.5%

Report URL:
https://durga1610.github.io/kisan-mitra-web/reports/latest/execution-report.html

## Detailed Mobile Results

| # | Suite | Test Case | Status | Duration | Failure Reason |
| :---: | :--- | :--- | :---: | :---: | :--- |
| 1 | test_auth.py | `test_auth_client_validation` | 🟢 PASS | 22.42s |  |
| 2 | test_auth.py | `test_auth_invalid_credentials` | 🟢 PASS | 26.09s |  |
| 3 | test_features.py | `test_home_page_load` | 🟢 PASS | 31.19s |  |
| 4 | test_features.py | `test_market_prices_page_load` | 🔴 FAIL | 60.57s | auth_driver = <appium.webdriver.webdriver.WebDriver (session="a9d608df-aa6e-4074-8828-6e07efbffa1... |
| 5 | test_features.py | `test_ai_advisor_page_load` | 🔴 FAIL | 59.79s | auth_driver = <appium.webdriver.webdriver.WebDriver (session="03548f0b-16ff-40c2-bfce-6f8869a0327... |
| 6 | test_features.py | `test_disease_scanner_page_load` | 🔴 FAIL | 60.27s | auth_driver = <appium.webdriver.webdriver.WebDriver (session="ba29635c-69c9-4dea-92ca-6563eb8d34e... |
| 7 | test_features.py | `test_navigation_between_screens` | 🟢 PASS | 39.50s |  |
| 8 | test_features.py | `test_responsive_ui_smoke` | 🟢 PASS | 36.13s |  |