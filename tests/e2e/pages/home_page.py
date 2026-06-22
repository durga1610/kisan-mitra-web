from selenium.webdriver.common.by import By
from pages.base_page import BasePage

class HomePage(BasePage):
    # Tab navigation locators
    HOME_TAB = (By.XPATH, "//flt-semantics[contains(@aria-label, 'Home')] | //*[text()='Home']")
    CROPS_TAB = (By.XPATH, "//flt-semantics[contains(@aria-label, 'Crops')] | //*[text()='Crops']")
    PROFILE_TAB = (By.XPATH, "//flt-semantics[contains(@aria-label, 'Profile')] | //*[text()='Profile']")

    # Quick action tiles
    AI_ASSISTANT_TILE = (By.XPATH, "//*[text()='AI Assistant'] | //flt-semantics[contains(@aria-label, 'AI Assistant')]")
    SCAN_DISEASE_TILE = (By.XPATH, "//*[text()='Scan Disease'] | //flt-semantics[contains(@aria-label, 'Scan Disease')]")
    FERTILIZER_TILE = (By.XPATH, "//*[text()='Fertilizer'] | //flt-semantics[contains(@aria-label, 'Fertilizer')]")
    WEATHER_TILE = (By.XPATH, "//*[text()='Weather'] | //flt-semantics[contains(@aria-label, 'Weather')]")
    MARKET_TILE = (By.XPATH, "//*[text()='Market'] | //flt-semantics[contains(@aria-label, 'Market')]")
    AI_ADVISORY_TILE = (By.XPATH, "//*[text()='AI Advisory'] | //flt-semantics[contains(@aria-label, 'AI Advisory')]")
    PROFIT_TILE = (By.XPATH, "//*[text()='Profit'] | //flt-semantics[contains(@aria-label, 'Profit')]")

    # Header / Info components
    DASHBOARD_HEADER = (By.XPATH, "//flt-semantics[contains(@aria-label, 'Farmer')] | //flt-semantics[contains(@aria-label, 'Field')]")
    WEATHER_CARD = (By.XPATH, "//flt-semantics[contains(@aria-label, 'Detecting location')] | //flt-semantics[contains(@aria-label, 'Sunny')] | //flt-semantics[contains(@aria-label, 'rain')]")

    def is_dashboard_loaded(self):
        """Check if dashboard header or weather card is visible."""
        return self.is_visible(self.DASHBOARD_HEADER) or self.is_visible(self.WEATHER_CARD) or self.is_visible(self.AI_ASSISTANT_TILE)

    def click_crops_tab(self):
        self.click(self.CROPS_TAB)

    def click_profile_tab(self):
        self.click(self.PROFILE_TAB)

    def click_scan_disease(self):
        self.click(self.SCAN_DISEASE_TILE)

    def click_ai_advisory(self):
        self.click(self.AI_ADVISORY_TILE)

    def click_ai_assistant(self):
        self.click(self.AI_ASSISTANT_TILE)
