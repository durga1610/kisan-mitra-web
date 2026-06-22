import os
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions import interaction

class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.timeout = 20

    def wait_for_element(self, locator):
        """Wait for mobile element to be visible and return it."""
        try:
            return WebDriverWait(self.driver, self.timeout).until(
                EC.visibility_of_element_located(locator)
            )
        except Exception as e:
            self.capture_screenshot(f"fail_wait_{int(time.time())}")
            raise e

    def click(self, locator):
        """Wait for element and click it."""
        element = self.wait_for_element(locator)
        element.click()

    def send_keys(self, locator, text):
        """Clear text and type in element."""
        element = self.wait_for_element(locator)
        element.clear()
        element.send_keys(text)

    def capture_screenshot(self, name):
        """Capture screenshot and store in Test Results/Screenshots."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        screenshots_dir = os.path.join(base_dir, "Test Results", "Screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)
        filepath = os.path.join(screenshots_dir, f"{name}.png")
        try:
            self.driver.save_screenshot(filepath)
            print(f"[MobileScreenshot] Saved screenshot: {filepath}")
        except Exception as e:
            print(f"[MobileScreenshot] Failed to capture: {e}")
        return filepath

    def swipe(self, start_x, start_y, end_x, end_y, duration_ms=250):
        """Perform standard W3C Actions drag-and-drop / swipe."""
        actions = ActionChains(self.driver)
        # Use W3C pointer action for swipe
        pointer = PointerInput(interaction.POINTER_TOUCH, "finger")
        actions.w3c_actions.devices.append(pointer)
        
        actions.w3c_actions.pointer_action.move_to_location(start_x, start_y)
        actions.w3c_actions.pointer_action.pointer_down()
        actions.w3c_actions.pointer_action.pause(duration_ms / 1000)
        actions.w3c_actions.pointer_action.move_to_location(end_x, end_y)
        actions.w3c_actions.pointer_action.release()
        
        actions.perform()
        time.sleep(1) # Wait for animation to settle
