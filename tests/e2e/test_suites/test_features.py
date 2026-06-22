import time

def test_disease_detection_guarded(driver, base_url):
    """Test that navigating directly to disease detection redirects to /login when unauthenticated."""
    driver.get(base_url + "#/disease-detection")
    time.sleep(3)
    
    print(f"Current URL after direct /disease-detection navigation: {driver.current_url}")
    assert "login" in driver.current_url.lower()

def test_ai_advisory_guarded(driver, base_url):
    """Test that navigating directly to AI advisory chat redirects to /login when unauthenticated."""
    driver.get(base_url + "#/ai-advisory")
    time.sleep(3)
    
    print(f"Current URL after direct /ai-advisory navigation: {driver.current_url}")
    assert "login" in driver.current_url.lower()

def test_ai_assistant_guarded(driver, base_url):
    """Test that navigating directly to AI assistant redirects to /login when unauthenticated."""
    driver.get(base_url + "#/ai-assistant")
    time.sleep(3)
    
    print(f"Current URL after direct /ai-assistant navigation: {driver.current_url}")
    assert "login" in driver.current_url.lower()
