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
            
        self.click(self.SUBMIT_BUTTON)

    def navigate_to_register(self):
        """Toggle to registration screen."""
        self.click(self.REGISTER_BUTTON)
