import time
import uuid

import allure
import pytest
from selenium.webdriver.common.by import By

from tests.ui.selenium_backoffice.pages.promos_page import PromosPage

pytestmark = [pytest.mark.selenium, allure.epic("Back-office"), allure.feature("Codes promo")]


def login_orga(driver):
    driver.get("http://localhost:5173/login")
    driver.find_element(By.CSS_SELECTOR, "input[type=email]").clear()
    email = driver.find_element(By.CSS_SELECTOR, "input[type=email]")
    email.send_keys("a")  # ctrl+a
    email.send_keys("orga@eventflow.test")
    pwd = driver.find_element(By.CSS_SELECTOR, "input[type=password]")
    pwd.send_keys("a")
    pwd.send_keys("orga1234")
    driver.find_element(By.XPATH, "//button[text()='Se connecter']").click()
    time.sleep(3)


def test_seed_promo_codes_are_listed(driver):
    login_orga(driver)
    page = PromosPage(driver).open()
    codes = page.codes()
    assert "WELCOME10" in codes
    assert "EXPIRED" in codes


def test_expired_code_is_inactive(driver):
    login_orga(driver)
    page = PromosPage(driver).open()
    assert page.status("EXPIRED") == "inactif"


@allure.story("Cycle de vie d'un code")
def test_create_and_disable_promo_code(driver):
    login_orga(driver)
    page = PromosPage(driver).open()
    code = "SEL" + uuid.uuid4().hex[:5].upper()

    page.create(code, 15, 20)
    assert page.status(code) == "actif"

    page.disable(code)
    assert page.status(code) == "inactif"
