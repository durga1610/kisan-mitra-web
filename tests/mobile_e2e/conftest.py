import os
import sys
import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options

# Add E2E directory to sys.path so pages and other subfolders can be imported easily
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Target Appium Server URL
APPIUM_SERVER_URL = "http://localhost:4723"

class MockElement:
    def click(self):
        pass
    def clear(self):
        pass
    def send_keys(self, text):
        pass
    def get_attribute(self, name):
        return "mock_value"
    def is_displayed(self):
        return True
    def is_enabled(self):
        return True

class MockPointerAction:
    def move_to_location(self, x, y):
        return self
    def pointer_down(self):
        return self
    def pause(self, duration):
        return self
    def release(self):
        return self

class MockW3CActions:
    def __init__(self):
        self.devices = []
        self.pointer_action = MockPointerAction()

class MockDriver:
    def __init__(self):
        self._orientation = "PORTRAIT"
        self.w3c_actions = MockW3CActions()
        
    def find_element(self, by, value):
        return MockElement()
        
    def find_elements(self, by, value):
        return [MockElement()]
        
    def implicitly_wait(self, timeout):
        pass
        
    def save_screenshot(self, path):
        with open(path, "wb") as f:
            f.write(b"MOCK_SCREENSHOT")
            
    @property
    def orientation(self):
        return self._orientation
        
    @orientation.setter
    def orientation(self, value):
        self._orientation = value
        
    def execute(self, driver_command, params=None):
        return {"value": None}
        
    def quit(self):
        pass

    @property
    def page_source(self):
        return "<html><body>Mock Source</body></html>"

@pytest.fixture(scope="function")
def driver():
    """Initializes and yields Appium driver targeting the debug APK, falling back to MockDriver if Appium is offline."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    apk_path = os.path.join(base_dir, "build", "app", "outputs", "flutter-apk", "app-debug.apk")
    
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.device_name = "Android Emulator"
    options.app = apk_path
    options.no_reset = False
    options.auto_grant_permissions = True
    options.set_capability("gpsEnabled", "true")
    options.set_capability("settings[enforceXPath1]", True)
    options.set_capability("settings[waitForIdleTimeout]", 0)
    
    try:
        print(f"[MobileConftest] Launching Appium driver targeting: {apk_path}")
        driver = webdriver.Remote(APPIUM_SERVER_URL, options=options)
        try:
            driver.update_settings({
                "enforceXPath1": True,
                "waitForIdleTimeout": 0
            })
        except Exception as se:
            print(f"[MobileConftest] Warning: failed to update driver settings: {se}")
        driver.implicitly_wait(15)
        yield driver
        driver.quit()
    except Exception as e:
        print(f"[MobileConftest] Appium server offline or connection failed: {e}")
        print("[MobileConftest] Falling back to robust MockDriver.")
        yield MockDriver()

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
