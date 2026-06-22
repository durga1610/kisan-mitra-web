import os
import sys
import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options

# Add E2E directory to sys.path so pages and other subfolders can be imported easily
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Target Appium Server URL
APPIUM_SERVER_URL = "http://localhost:4723"

@pytest.fixture(scope="function")
def driver():
    """Initializes and yields Appium driver targeting the debug APK."""
    # Resolve APK path relative to conftest.py
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    apk_path = os.path.join(base_dir, "build", "app", "outputs", "flutter-apk", "app-debug.apk")
    
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.device_name = "Android Emulator"
    options.app = apk_path
    options.no_reset = False
    options.auto_grant_permissions = True
    
    # Optional settings to allow file/camera access mock
    options.set_capability("gpsEnabled", "true")
    
    print(f"[MobileConftest] Launching Appium driver targeting: {apk_path}")
    driver = webdriver.Remote(APPIUM_SERVER_URL, options=options)
    driver.implicitly_wait(15)
    
    yield driver
    
    driver.quit()

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Captures screenshot when Appium mobile E2E tests fail."""
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        try:
            if "driver" in item.fixturenames:
                driver = item.funcargs["driver"]
                results_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "Test Results", "Screenshots"))
                os.makedirs(results_dir, exist_ok=True)
                filename = f"fail_{item.name}_{int(call.start)}.png"
                filepath = os.path.join(results_dir, filename)
                driver.save_screenshot(filepath)
                print(f"[MobileConftest] Captured failure screenshot: {filepath}")
        except Exception as e:
            print(f"[MobileConftest] Failed to capture screenshot: {e}")
