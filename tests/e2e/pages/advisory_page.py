from selenium.webdriver.common.by import By
from pages.base_page import BasePage
import time

class AdvisoryPage(BasePage):
    CHAT_INPUT = (By.XPATH, "//input[contains(@placeholder, 'crops')] | //input[contains(@placeholder, 'Ask')] | //flt-semantics[@role='textbox']//input")
    SEND_BUTTON = (By.XPATH, "//*[contains(@aria-label, 'send')] | //flt-semantics[contains(@aria-label, 'Send')] | //flt-semantics[@role='button' and contains(., 'send')]")
    THINKING_INDICATOR = (By.XPATH, "//*[contains(text(), 'thinking')] | //*[contains(text(), 'thinking')]")
    MESSAGE_BUBBLES = (By.XPATH, "//flt-semantics[contains(@aria-label, 'Kisan Mitra')] | //flt-semantics[contains(@aria-label, 'Hello')]")

    def send_message(self, message):
        """Send chat message to Kisan Mitra AI chatbot."""
        self.send_keys(self.CHAT_INPUT, message)
        # Wait a moment for input updating
        time.sleep(0.5)
        self.click(self.SEND_BUTTON)

    def wait_for_response(self, timeout=30):
        """Wait for typing indicator to disappear and get response."""
        # Wait for thinking indicator if visible, then wait for it to disappear
        time.sleep(2)
        # Wait for the response message bubble to appear
        time.sleep(5)
        # Get all visible messages
        elements = self.driver.find_elements(By.XPATH, "//*[contains(@aria-label, 'Mitra') or contains(@aria-label, 'Assistant') or contains(@aria-label, 'farm')]")
        if elements:
            # Return the text or aria-label of the last message bubble
            last_msg = elements[-1]
            return last_msg.get_attribute("aria-label") or last_msg.text
        return ""
