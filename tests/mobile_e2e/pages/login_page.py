from selenium.webdriver.common.by import By
from pages.base_page import BasePage

class LoginPage(BasePage):
    # Flexible locators for Flutter Android UiAutomator2 semantics
    EMAIL_INPUT = (By.XPATH, "//android.widget.EditText[contains(@text, 'Email')] | //android.view.View[contains(@content-desc, 'Email')] | //android.widget.EditText")
    PASSWORD_INPUT = (By.XPATH, "//android.widget.EditText[contains(@text, 'Password')] | //android.view.View[contains(@content-desc, 'Password')] | //android.view.View[@text='Password']")
    SUBMIT_BUTTON = (By.XPATH, "//android.widget.Button | //android.view.View[contains(@content-desc, 'Login')] | //android.view.View[@text='Login']")
    REGISTER_BUTTON = (By.XPATH, "//android.view.View[contains(@content-desc, 'Register')] | //android.view.View[@text='Register']")

    def login(self, email, password):
        """Type credentials and click login."""
        self.send_keys(self.EMAIL_INPUT, email)
        self.send_keys(self.PASSWORD_INPUT, password)
        self.click(self.SUBMIT_BUTTON)

    def navigate_to_register(self):
        """Toggle to registration screen."""
        self.click(self.REGISTER_BUTTON)
