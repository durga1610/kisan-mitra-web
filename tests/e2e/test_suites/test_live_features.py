import time
import os
from selenium.webdriver.common.by import By

def save_test_screenshot(driver, name):
    """Utility to capture and store screenshots in the Test Results/Screenshots folder."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    screenshots_dir = os.path.join(base_dir, "Test Results", "Screenshots")
    os.makedirs(screenshots_dir, exist_ok=True)
    filepath = os.path.join(screenshots_dir, f"{name}.png")
    try:
        driver.save_screenshot(filepath)
        print(f"[LiveTest] Captured screenshot: {filepath}")
    except Exception as e:
        print(f"[LiveTest] Failed to capture screenshot {name}: {e}")

def test_home_page_load(driver, base_url):
    """Verify that the Home page loads successfully in demo mode without redirecting."""
    target_url = base_url + "?demo=true#/home"
    print(f"Navigating to: {target_url}")
    driver.get(target_url)
    time.sleep(5)  # Wait for flutter compilation and routing
    
    save_test_screenshot(driver, "home_page_load")
    
    current_url = driver.current_url.lower()
    print(f"Current URL: {current_url}")
    assert "login" not in current_url, "Redirected to login page from Home screen"

def test_market_prices_page_load(driver, base_url):
    """Verify that the Market Prices page loads successfully in demo mode."""
    target_url = base_url + "?demo=true#/market"
    print(f"Navigating to: {target_url}")
    driver.get(target_url)
    time.sleep(4)
    
    save_test_screenshot(driver, "market_prices_load")
    
    current_url = driver.current_url.lower()
    print(f"Current URL: {current_url}")
    assert "login" not in current_url, "Redirected to login page from Market Prices screen"

def test_ai_advisor_page_load(driver, base_url):
    """Verify that the AI Advisor page loads successfully in demo mode."""
    target_url = base_url + "?demo=true#/ai-advisory"
    print(f"Navigating to: {target_url}")
    driver.get(target_url)
    time.sleep(4)
    
    save_test_screenshot(driver, "ai_advisor_load")
    
    current_url = driver.current_url.lower()
    print(f"Current URL: {current_url}")
    assert "login" not in current_url, "Redirected to login page from AI Advisor screen"

def test_disease_scanner_page_load(driver, base_url):
    """Verify that the Disease Scanner page loads successfully in demo mode."""
    target_url = base_url + "?demo=true#/disease-detection"
    print(f"Navigating to: {target_url}")
    driver.get(target_url)
    time.sleep(4)
    
    save_test_screenshot(driver, "disease_scanner_load")
    
    current_url = driver.current_url.lower()
    print(f"Current URL: {current_url}")
    assert "login" not in current_url, "Redirected to login page from Disease Scanner screen"

def test_navigation_between_screens(driver, base_url):
    """Verify navigation transitions between different sections of the app (Home, Crops, Profile)."""
    # Start on Home
    driver.get(base_url + "?demo=true#/home")
    time.sleep(3)
    save_test_screenshot(driver, "nav_step_home")
    assert "login" not in driver.current_url.lower()

    # Move to Crops
    driver.get(base_url + "?demo=true#/crops")
    time.sleep(3)
    save_test_screenshot(driver, "nav_step_crops")
    assert "login" not in driver.current_url.lower()

    # Move to Profile
    driver.get(base_url + "?demo=true#/profile")
    time.sleep(3)
    save_test_screenshot(driver, "nav_step_profile")
    assert "login" not in driver.current_url.lower()

def test_responsive_ui_smoke(driver, base_url):
    """Verify that the application layout is responsive and scales safely to mobile dimensions."""
    # Set to a typical mobile dimensions (375x812 is iPhone X size)
    driver.set_window_size(375, 812)
    time.sleep(1)
    
    target_url = base_url + "?demo=true#/home"
    print(f"Navigating to mobile view: {target_url}")
    driver.get(target_url)
    time.sleep(4)
    
    save_test_screenshot(driver, "responsive_mobile_home")
    
    # Check that it loads without login redirects
    assert "login" not in driver.current_url.lower()
    
    # Restore standard window size
    driver.set_window_size(1280, 1024)
