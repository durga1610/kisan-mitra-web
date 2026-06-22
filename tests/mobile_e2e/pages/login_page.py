import time
from selenium.webdriver.common.by import By
from pages.base_page import BasePage

class LoginPage(BasePage):
    # Flexible locators for Flutter Android UiAutomator2 semantics
    EMAIL_INPUT = (By.XPATH, "(//android.widget.EditText)[1]")
    PASSWORD_INPUT = (By.XPATH, "(//android.widget.EditText)[2]")
    SUBMIT_BUTTON = (By.XPATH, "//android.widget.Button[contains(@content-desc, 'Login') or contains(@text, 'Login')] | //android.view.View[contains(@content-desc, 'Login') or contains(@text, 'Login')]")
    REGISTER_BUTTON = (By.XPATH, "//android.view.View[contains(@content-desc, 'Register')] | //android.view.View[@text='Register']")

    def login(self, email, password):
        """Type credentials and click login, hiding keyboard to prevent overlap."""
        self.send_keys(self.EMAIL_INPUT, email)
        try:
            if self.driver.is_keyboard_shown():
                self.driver.hide_keyboard()
                time.sleep(0.5)
        except Exception:
            try:
                self.driver.back() # fallback back-button press to dismiss keyboard
                time.sleep(0.5)
            except Exception:
                pass
            
        self.send_keys(self.PASSWORD_INPUT, password)
        try:
            if self.driver.is_keyboard_shown():
                self.driver.hide_keyboard()
                time.sleep(0.5)
        except Exception:
            try:
                self.driver.back() # fallback back-button press
                time.sleep(0.5)
            except Exception:
                pass
            
        # Debug: Print page source and list matched elements for the login button
        try:
            print("--- DEBUG LOGIN PAGE SOURCE ---")
            print(self.driver.page_source)
            print("--- END DEBUG LOGIN PAGE SOURCE ---")
            buttons = self.driver.find_elements(*self.SUBMIT_BUTTON)
            print(f"[DEBUG] Found {len(buttons)} matching submit buttons.")
            for i, btn in enumerate(buttons):
                print(f"  [{i}] class: {btn.get_attribute('class')}, text: {btn.get_attribute('text')}, desc: {btn.get_attribute('content-desc') or btn.get_attribute('contentDescription')}, resource-id: {btn.get_attribute('resource-id') or btn.get_attribute('resourceId')}, displayed: {btn.is_displayed()}")
        except Exception as e:
            print(f"[DEBUG] Error logging details: {e}")

        self.click(self.SUBMIT_BUTTON)

    def navigate_to_register(self):
        """Toggle to registration screen."""
        self.click(self.REGISTER_BUTTON)
