# Android Appium Test Summary

Build Number: #7
Execution Date: 2026-06-22 15:11:53

Total Tests: 8
Passed: 4
Failed: 4
Pass Rate: 50.0%

Report URL:
https://durga1610.github.io/kisan-mitra-web/reports/latest/execution-report.html

## Detailed Mobile Results

| # | Suite | Test Case | Status | Duration | Failure Reason |
| :---: | :--- | :--- | :---: | :---: | :--- |
| 1 | test_auth.py | `test_auth_client_validation` | 🟢 PASS | 24.03s |  |
| 2 | test_auth.py | `test_auth_invalid_credentials` | 🟢 PASS | 27.03s |  |
| 3 | test_features.py | `test_home_page_load` | 🟢 PASS | 31.21s |  |
| 4 | test_features.py | `test_market_prices_page_load` | 🔴 FAIL | 60.52s | auth_driver = <appium.webdriver.webdriver.WebDriver (session="87b6fdad-5641-4e94-8183-d66139b7d64... |
| 5 | test_features.py | `test_ai_advisor_page_load` | 🔴 FAIL | 61.10s | auth_driver = <appium.webdriver.webdriver.WebDriver (session="87662c3f-c966-48ff-bfad-0e551c3f7a4... |
| 6 | test_features.py | `test_disease_scanner_page_load` | 🔴 FAIL | 60.34s | auth_driver = <appium.webdriver.webdriver.WebDriver (session="4f1c4792-b29d-4af0-a83e-fe427eb9679... |
| 7 | test_features.py | `test_navigation_between_screens` | 🔴 FAIL | 60.59s | auth_driver = <appium.webdriver.webdriver.WebDriver (session="982bd95b-60a1-416f-b178-6b6da97ba89... |
| 8 | test_features.py | `test_responsive_ui_smoke` | 🟢 PASS | 36.23s |  |