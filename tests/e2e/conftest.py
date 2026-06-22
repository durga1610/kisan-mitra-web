import os
import sys
import pytest

# Add E2E directory to sys.path so pages and other subfolders can be imported easily
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Target base URL from environment or fallback to production GitHub Pages URL
DEFAULT_URL = "https://durga1610.github.io/kisan-mitra-web/"
BASE_URL = os.getenv("BASE_URL", DEFAULT_URL)

@pytest.fixture(scope="session")
def base_url():
    return BASE_URL

@pytest.fixture(scope="function")
def driver():
    """Sets up headless Chrome WebDriver for E2E web testing."""
    options = Options()
    options.add_argument("--headless=new")  # Use the modern headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,1024")
    
    # Optional settings to allow file upload to work correctly on web
    prefs = {"profile.default_content_setting_values.media_stream_mic": 1, 
             "profile.default_content_setting_values.media_stream_camera": 1}
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    
    yield driver
    
    driver.quit()

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hooks into pytest to capture screenshot when E2E tests fail."""
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        try:
            # Retrieve driver from item context if available
            if "driver" in item.fixturenames:
                driver = item.funcargs["driver"]
                results_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "Test Results", "Screenshots"))
                os.makedirs(results_dir, exist_ok=True)
                filename = f"fail_{item.name}_{int(call.start)}.png"
                filepath = os.path.join(results_dir, filename)
                driver.save_screenshot(filepath)
                print(f"[conftest] Captured failure screenshot: {filepath}")
        except Exception as e:
            print(f"[conftest] Failed to capture failure screenshot: {e}")
