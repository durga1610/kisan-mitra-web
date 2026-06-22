import os
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.timeout = 15

    def wait_for_element(self, locator):
        """Wait for element to be visible and return it."""
        try:
            return WebDriverWait(self.driver, self.timeout).until(
                EC.visibility_of_element_located(locator)
            )
        except Exception as e:
            # Capture screenshot on wait failure
            self.capture_screenshot(f"fail_wait_{int(time.time())}")
            raise e

    def wait_for_clickable(self, locator):
        """Wait for element to be clickable and return it."""
        try:
            return WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable(locator)
            )
        except Exception as e:
            self.capture_screenshot(f"fail_clickable_{int(time.time())}")
            raise e

    def click(self, locator):
        """Click on the element."""
        element = self.wait_for_clickable(locator)
        element.click()

    def send_keys(self, locator, text):
        """Type text into the element after clearing it."""
        element = self.wait_for_element(locator)
        element.clear()
        element.send_keys(text)

    def get_text(self, locator):
        """Get visible text of element."""
        element = self.wait_for_element(locator)
        return element.text

    def get_attribute(self, locator, attr):
        """Get attribute of element."""
        element = self.wait_for_element(locator)
        return element.get_attribute(attr)

    def is_visible(self, locator):
        """Check if element is visible on the page."""
        try:
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except Exception:
            return False

    def capture_screenshot(self, name):
        """Capture screenshot and save in Screenshots output folder."""
        # Create Screenshots directory relative to current page run
        results_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Test Results", "Screenshots"))
        os.makedirs(results_dir, exist_ok=True)
        filepath = os.path.join(results_dir, f"{name}.png")
        try:
            self.driver.save_screenshot(filepath)
            print(f"[Screenshot] Saved screenshot: {filepath}")
        except Exception as e:
            print(f"[Screenshot] Failed to capture screenshot: {e}")
        return filepath
