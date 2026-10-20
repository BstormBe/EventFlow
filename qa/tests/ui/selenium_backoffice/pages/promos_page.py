import time

from selenium.webdriver.common.by import By

from .base_page import BasePage


class PromosPage(BasePage):
    path = "/admin/promos"

    CODE = (By.CSS_SELECTOR, "input[placeholder='SUMMER20']")
    CREATE = (By.XPATH, "//form//button[contains(., 'Creer')]")
    ROWS = (By.XPATH, "/html/body/div[1]/div/div/table/tbody/tr")
    ERROR = (By.CSS_SELECTOR, ".notice-err")

    def create(self, code, percent, max_uses):
        self.type(self.CODE, code)
        self.type(self.field("Reduction (%)"), str(percent))
        self.type(self.field("Usages max"), str(max_uses))
        self.click(self.CREATE)
        time.sleep(1)

    def _row(self, code):
        return self.find((By.XPATH, f"//tr[td[normalize-space()='{code}']]"))

    def codes(self):
        return self.texts(self.ROWS, "td.mono")

    def status(self, code):
        return self._row(code).find_element(By.CSS_SELECTOR, ".badge").text

    def disable(self, code):
        self._row(code).find_element(By.XPATH, ".//button[contains(., 'Desactiver')]").click()
        time.sleep(1)
