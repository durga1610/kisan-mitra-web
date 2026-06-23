# Troubleshooting Guide — Android Appium E2E

Common error patterns, causes, and step-by-step solutions for mobile testing environments.

---

### 1. Emulator fails to boot on GitHub Actions runner
* **Symptom**: Step `Run Appium E2E Tests on Android Emulator` fails with timeout or boot failures.
* **Cause**: Ubuntu runner doesn't have KVM virtualization permissions enabled.
* **Fix**: Ensure the runner execution block includes:
  ```bash
  echo 'KERNEL=="kvm", GROUP="kvm", MODE="0666", OPTIONS+="static_node=kvm"' | sudo tee /etc/udev/rules.d/99-kvm4all.rules
  sudo udevadm control --reload-rules
  sudo udevadm trigger --name-match=kvm
  ```

---

### 2. Appium Connection Refused (`urllib3.exceptions.MaxRetryError`)
* **Symptom**: Python test suite crashes instantly with connection error targeting `http://localhost:4723`.
* **Cause**: Appium server has not finished booting or crashed due to incorrect configurations.
* **Fix**:
  - Run `appium --version` to verify install status.
  - Check the `appium.log` file in the repository root to see if ports are occupied.
  - Make sure to add `sleep 10` after starting the server in GHA to allow it to initialize before launching Python tests.

---

### 3. CanvasKit Rendering / Input Element Timeout
* **Symptom**: Pytest fails to find input elements (`LoginPage.EMAIL_INPUT`) and timeouts.
* **Cause**: Flutter compiles using the canvas-based CanvasKit renderer by default, which does not render native accessibility/text elements in standard HTML structures.
* **Fix**: Ensure selectors target content-descriptions or text properties (`*[@content-desc='Input']`) instead of HTML selectors, or use the `?demo=true` authentication bypass flag for rapid mock-state transitions in web E2E tests.
