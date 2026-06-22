from selenium.webdriver.common.by import By
from pages.base_page import BasePage

class HomePage(BasePage):
    DASHBOARD_TITLE = (By.XPATH, "//*[contains(@content-desc, 'Kisan Mitra')] | //*[contains(@text, 'Kisan Mitra')]")
    HOME_TAB = (By.XPATH, "//*[contains(@content-desc, 'Home')] | //*[contains(@text, 'Home')]")
    CROPS_TAB = (By.XPATH, "//*[contains(@content-desc, 'Crops')] | //*[contains(@text, 'Crops')]")
    PROFILE_TAB = (By.XPATH, "//*[contains(@content-desc, 'Profile')] | //*[contains(@text, 'Profile')]")
    MARKET_TAB = (By.XPATH, "//*[contains(@content-desc, 'Market')] | //*[contains(@text, 'Market')]")
    ADVISORY_TAB = (By.XPATH, "//*[contains(@content-desc, 'Advisory')] | //*[contains(@text, 'Advisory')]")
    SCAN_DISEASE_TILE = (By.XPATH, "//*[contains(@content-desc, 'Scan')] | //*[contains(@text, 'Scan')]")
