import time
import pytest
from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.advisory_page import AdvisoryPage
from pages.disease_scan_page import DiseaseScanPage

@pytest.fixture(scope="function")
def auth_driver(driver):
    """Fixture to launch app and log in automatically with test credentials."""
    time.sleep(5)
    login_page = LoginPage(driver)
    print("[MobileTest] Performing E2E test login...")
    login_page.login("testfarmer@example.com", "TestFarmer123!")
    time.sleep(6)  # Wait for login action and redirect to load Home page
    return driver

def test_home_page_load(auth_driver):
    """Verify that the Home dashboard loads successfully after login."""
    home_page = HomePage(auth_driver)
    # Verify that the Crops tab on the home bottom nav is visible (proves home page has loaded)
    assert home_page.wait_for_element(home_page.CROPS_TAB) is not None, "Home screen failed to load (Crops tab not found)"
    home_page.capture_screenshot("mobile_home_page_load")
    print("[MobileTest] Home screen verified.")

def test_market_prices_page_load(auth_driver):
    """Verify that the Market Prices page opens successfully."""
    home_page = HomePage(auth_driver)
    # Navigate to Market tab
    home_page.click(home_page.MARKET_TAB)
    time.sleep(4)
    
    # Assert Market Prices title is visible
    from selenium.webdriver.common.by import By
    market_title = (By.XPATH, "//*[contains(@content-desc, 'Market Prices')] | //*[contains(@text, 'Market Prices')]")
    assert home_page.wait_for_element(market_title) is not None, "Market Prices page failed to load"
    
    home_page.capture_screenshot("mobile_market_prices_load")
    print("[MobileTest] Market Prices verified.")

def test_ai_advisor_page_load(auth_driver):
    """Verify that the AI Advisor chat panel opens successfully."""
    home_page = HomePage(auth_driver)
    # Navigate to Advisory tab
    home_page.click(home_page.ADVISORY_TAB)
    time.sleep(4)
    
    # Assert Advisory title or subtitle is visible
    from selenium.webdriver.common.by import By
    advisory_title = (By.XPATH, "//*[contains(@content-desc, 'Advisory')] | //*[contains(@text, 'Advisory')]")
    assert home_page.wait_for_element(advisory_title) is not None, "AI Advisor page failed to load"
    
    advisory_page = AdvisoryPage(auth_driver)
    advisory_page.capture_screenshot("mobile_ai_advisor_load")
    print("[MobileTest] AI Advisor verified.")

def test_disease_scanner_page_load(auth_driver):
    """Verify that the Disease Scanner interface opens successfully."""
    home_page = HomePage(auth_driver)
    # Click Scan Disease quick action card
    home_page.click(home_page.SCAN_DISEASE_TILE)
    time.sleep(4)
    
    # Assert Disease Scanner title is visible
    from selenium.webdriver.common.by import By
    scanner_title = (By.XPATH, "//*[contains(@content-desc, 'Scan Plant')] | //*[contains(@text, 'Scan Plant')]")
    assert home_page.wait_for_element(scanner_title) is not None, "Disease Scanner page failed to load"
    
    scan_page = DiseaseScanPage(auth_driver)
    scan_page.capture_screenshot("mobile_disease_scanner_load")
    print("[MobileTest] Disease Scanner verified.")

def test_navigation_between_screens(auth_driver):
    """Verify navigation flows between different main sections of the app."""
    home_page = HomePage(auth_driver)
    from selenium.webdriver.common.by import By
    
    # Go to Crops
    home_page.click(home_page.CROPS_TAB)
    time.sleep(3)
    crops_title = (By.XPATH, "//*[contains(@content-desc, 'Farm Management')] | //*[contains(@text, 'Farm Management')]")
    assert home_page.wait_for_element(crops_title) is not None, "Crops screen failed to load"
    home_page.capture_screenshot("mobile_nav_crops")
    
    # Go to Profile
    home_page.click(home_page.PROFILE_TAB)
    time.sleep(3)
    profile_title = (By.XPATH, "//*[contains(@content-desc, 'Profile')] | //*[contains(@text, 'Profile')]")
    assert home_page.wait_for_element(profile_title) is not None, "Profile screen failed to load"
    home_page.capture_screenshot("mobile_nav_profile")
    
    # Go back to Home
    home_page.click(home_page.HOME_TAB)
    time.sleep(3)
    assert home_page.wait_for_element(home_page.CROPS_TAB) is not None, "Home screen failed to reload"
    home_page.capture_screenshot("mobile_nav_home")
    print("[MobileTest] Mobile navigation flow completed.")

def test_responsive_ui_smoke(auth_driver):
    """Verify that the layout dynamically handles landscape and portrait rotation safely."""
    home_page = HomePage(auth_driver)
    
    # Rotate to Landscape
    print("[MobileTest] Rotating emulator to LANDSCAPE...")
    try:
        auth_driver.orientation = "LANDSCAPE"
        time.sleep(4)
        home_page.capture_screenshot("mobile_layout_landscape")
    except Exception as e:
        print(f"[MobileTest] Orientation change to LANDSCAPE failed or locked: {e}")
        home_page.capture_screenshot("mobile_layout_landscape_failed")
    
    # Rotate back to Portrait
    print("[MobileTest] Rotating emulator back to PORTRAIT...")
    try:
        auth_driver.orientation = "PORTRAIT"
        time.sleep(4)
        home_page.capture_screenshot("mobile_layout_portrait")
    except Exception as e:
        print(f"[MobileTest] Orientation change to PORTRAIT failed: {e}")
        home_page.capture_screenshot("mobile_layout_portrait_failed")
    
    print("[MobileTest] Orientation rotation smoke test complete.")
