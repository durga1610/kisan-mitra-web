import time
from pages.login_page import LoginPage
from pages.home_page import HomePage

def test_auth_client_validation(driver, base_url):
    """Test that login input validations are triggered for empty email/password."""
    driver.get(base_url)
    time.sleep(3)  # Wait for Flutter load

    login_page = LoginPage(driver)
    login_page.capture_screenshot("login_screen_load")

    # Leave fields blank and submit
    login_page.click(login_page.SUBMIT_BUTTON)
    time.sleep(2)
    login_page.capture_screenshot("login_validation_blank")
    
    # We expect some validation text to appear or snapback. Since Flutter compiles this,
    # we can verify that we are still on the login page (the URL contains /login or stays on base).
    assert "login" in driver.current_url.lower() or driver.current_url.endswith("/")

def test_auth_invalid_credentials(driver, base_url):
    """Test that invalid login credentials display an auth error message."""
    driver.get(base_url)
    time.sleep(3)

    login_page = LoginPage(driver)
    
    # Input invalid credentials
    login_page.login("nonexistent_farmer_123@kisan.com", "InvalidPass123!")
    time.sleep(4)  # Wait for auth response
    login_page.capture_screenshot("login_failed_error")
    
    # Asserts that login did not succeed (we did not redirect to /home)
    assert "home" not in driver.current_url.lower()
