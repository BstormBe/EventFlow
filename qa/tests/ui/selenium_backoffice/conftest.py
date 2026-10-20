import os

import allure
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from tests.ui.selenium_backoffice.pages.login_page import LoginPage
from utils import config


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


@pytest.fixture
def driver(request):
    options = webdriver.ChromeOptions()
    if os.getenv("HEADLESS", "true").lower() == "true":
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1366,900")
    options.add_argument("--lang=fr-BE")
    # Executables personnalises (sinon Selenium Manager trouve/telecharge Chrome et le driver)
    if os.getenv("CHROME_BINARY"):
        options.binary_location = os.getenv("CHROME_BINARY")
    service = Service(os.getenv("CHROMEDRIVER_PATH")) if os.getenv("CHROMEDRIVER_PATH") else None

    drv = webdriver.Chrome(options=options, service=service)
    drv.implicitly_wait(5)
    yield drv

    if getattr(request.node, "rep_call", None) and request.node.rep_call.failed:
        allure.attach(drv.get_screenshot_as_png(), name="capture-echec", attachment_type=allure.attachment_type.PNG)
    drv.quit()


@pytest.fixture
def orga_driver(driver):
    LoginPage(driver).open().login(config.ORGA_EMAIL, config.ORGA_PASSWORD)
    return driver
