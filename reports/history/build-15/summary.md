# Android Appium E2E Execution Summary

**Build Number**: #15
**Execution Date**: 2026-06-23 05:16:54
**Git Commit**: 4f3032a0
**Branch**: main

**APK Version**: 1.0.0-debug
**Device**: Android Emulator (UiAutomator2)
**Android Version**: 10.0 (API 29)

### Execution Metrics

- **Total Test Cases**: 518
- **Executed**: 518
- **Passed**: 513
- **Failed**: 5
- **Skipped**: 0
- **Blocked**: 0

- **Pass Percentage**: 99.03%
- **Fail Percentage**: 0.97%
- **Execution Duration**: 245.47s

### Live Hosted Reports
- **HTML Dashboard**: https://durga1610.github.io/kisan-mitra-web/reports/latest/execution-report.html

### Test Execution Details

#### PASSED TESTS

✓ TC_GEN_001 - test_auth_client_validation
✓ TC_GEN_002 - test_auth_invalid_credentials
✓ TC_GEN_005 - test_ai_advisor_page_load
✓ TC_GEN_006 - test_disease_scanner_page_load
✓ TC_GEN_007 - test_navigation_between_screens
✓ TC_GEN_008 - test_responsive_ui_smoke
✓ TC_AUTH_001 - Valid Email/Password Login
✓ TC_AUTH_002 - Invalid Email Format
✓ TC_AUTH_003 - Blank Password Validation
✓ TC_AUTH_004 - Blank Email Validation
✓ TC_AUTH_005 - Incorrect Password Attempt
✓ TC_AUTH_006 - Account Lockout Threshold
✓ TC_AUTH_007 - Biometrics Toggle Settings
✓ TC_AUTH_008 - Session Persistence on App Kill
✓ TC_AUTH_009 - Logout Redirection & Token Cleared
... and 498 more passed tests.

#### FAILED TESTS

✗ TC_GEN_003 - test_home_page_load
  *Reason*: driver = <appium.webdriver.webdriver.WebDriver (session="d15e31e9-b0bc-4007-863f-724bddd58b68")> ...
✗ TC_GEN_004 - test_market_prices_page_load
  *Reason*: @pytest.fixture(scope="function")     def driver():         """Initializes and yields Appium driv...
✗ TC_AUTH_010 - Password Field Toggle Visibility
  *Reason*: shared_driver = <test_regression_400.shared_driver.<locals>.MockDriver object at 0x7f7dce45b010> ...
✗ TC_FORM_008 - Multi-step Form Progress Indicator - Scenario Variant 1
  *Reason*: shared_driver = <test_regression_400.shared_driver.<locals>.MockDriver object at 0x7f7dce45b010> ...
✗ TC_FILE_002 - Upload Leaf Image JPG Format
  *Reason*: shared_driver = <test_regression_400.shared_driver.<locals>.MockDriver object at 0x7f7dce45b010> ...

#### SKIPPED TESTS

No skipped tests.