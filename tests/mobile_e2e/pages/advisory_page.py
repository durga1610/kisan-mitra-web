from selenium.webdriver.common.by import By
from pages.base_page import BasePage

class AdvisoryPage(BasePage):
    CHAT_INPUT = (By.XPATH, "//android.widget.EditText | //*[contains(@placeholder, 'Ask')]")
    SEND_BUTTON = (By.XPATH, "//*[contains(@content-desc, 'Send')] | //*[contains(@text, 'Send')]")
    CHAT_BUBBLE = (By.XPATH, "//*[contains(@content-desc, 'Advisor')] | //*[contains(@text, 'Advisor')]")
