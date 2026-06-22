from selenium.webdriver.common.by import By
from pages.base_page import BasePage

class LoginPage(BasePage):
    # Flexible locators for Flutter Web semantics
    EMAIL_INPUT = (By.XPATH, "//input[@type='email'] | //input[contains(@placeholder, 'example.com')] | //flt-semantics[@aria-label='Email']//input")
    PASSWORD_INPUT = (By.XPATH, "//input[@type='password'] | //input[contains(@placeholder, 'password')] | //flt-semantics[@aria-label='Password']//input")
    SUBMIT_BUTTON = (By.XPATH, "//*[text()='Login'] | //flt-semantics[@aria-label='Login'] | //flt-semantics[contains(@aria-label, 'Login')]")
    REGISTER_BUTTON = (By.XPATH, "//*[text()='Register'] | //flt-semantics[contains(@aria-label, 'Register')]")

    def login(self, email, password):
        """Perform login action with given credentials."""
        self.send_keys(self.EMAIL_INPUT, email)
        self.send_keys(self.PASSWORD_INPUT, password)
        self.click(self.SUBMIT_BUTTON)

    def navigate_to_register(self):
        """Click the registration link/button."""
        self.click(self.REGISTER_BUTTON)
