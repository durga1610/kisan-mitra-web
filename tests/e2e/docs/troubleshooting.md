# Troubleshooting Guide — Web Selenium E2E

Common error patterns, causes, and step-by-step solutions for Selenium browser testing.

---

### 1. WebDriverException: DevToolsActivePort file doesn't exist
* **Symptom**: Selenium crashes instantly during initialization of Google Chrome.
* **Cause**: Chrome is running in a sandbox environment that restricts resource access.
* **Fix**: Ensure options include `--no-sandbox` and `--disable-dev-shm-usage`:
  ```python
  options.add_argument("--no-sandbox")
  options.add_argument("--disable-dev-shm-usage")
  ```

---

### 2. Deployment Availability Timeout (HTTP 404 or 403)
* **Symptom**: Step `Wait for Deployment Availability` fails after 30 attempts.
* **Cause**: The GitHub Pages build is delayed, or the source settings in repository options are misconfigured.
* **Fix**: Verify your GitHub Pages build under the Actions tab. Make sure the deployment source is configured as **GitHub Actions** in repository settings.

---

### 3. SessionNotCreatedException: chromedriver version mismatch
* **Symptom**: The runner fails to start the driver locally because Chrome version differs from chromedriver version.
* **Fix**: Remove hardcoded drivers from the `drivers/` folder and rely on Selenium 4.x's built-in **Selenium Manager**, which automatically fetches the compatible chromedriver for your current Chrome installation.
