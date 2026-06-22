import time

def test_auth_guard_redirects_home(driver, base_url):
    """Test that navigating directly to /home redirects to /login when unauthenticated."""
    # Attempt direct navigation to home
    driver.get(base_url + "#/home")
    time.sleep(3)
    
    # Assert that the page redirected to login
    print(f"Current URL after direct /home navigation: {driver.current_url}")
    assert "login" in driver.current_url.lower()

def test_auth_guard_redirects_crops(driver, base_url):
    """Test that navigating directly to /crops redirects to /login when unauthenticated."""
    driver.get(base_url + "#/crops")
    time.sleep(3)
    
    print(f"Current URL after direct /crops navigation: {driver.current_url}")
    assert "login" in driver.current_url.lower()

def test_auth_guard_redirects_profile(driver, base_url):
    """Test that navigating directly to /profile redirects to /login when unauthenticated."""
    driver.get(base_url + "#/profile")
    time.sleep(3)
    
    print(f"Current URL after direct /profile navigation: {driver.current_url}")
    assert "login" in driver.current_url.lower()
