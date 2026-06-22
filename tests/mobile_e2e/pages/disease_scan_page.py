from selenium.webdriver.common.by import By
from pages.base_page import BasePage

class DiseaseScanPage(BasePage):
    CAMERA_TRIGGER = (By.XPATH, "//*[contains(@content-desc, 'Camera')] | //*[contains(@text, 'Camera')]")
    GALLERY_TRIGGER = (By.XPATH, "//*[contains(@content-desc, 'Gallery')] | //*[contains(@text, 'Gallery')]")
    DIAGNOSIS_OUTPUT = (By.XPATH, "//*[contains(@content-desc, 'Diagnosis')] | //*[contains(@text, 'Diagnosis')]")
