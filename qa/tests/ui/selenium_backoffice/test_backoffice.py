import uuid

import allure
import pytest
from selenium.webdriver.support.ui import WebDriverWait

from tests.ui.selenium_backoffice.pages.dashboard_page import DashboardPage
from tests.ui.selenium_backoffice.pages.event_pages import EventFormPage
from tests.ui.selenium_backoffice.pages.login_page import LoginPage
from utils import config

pytestmark = [pytest.mark.selenium, allure.epic("Back-office"), allure.feature("Evenements")]

CREATED_TITLE = None


@allure.story("Connexion organisateur")
def test_organizer_reaches_back_office(orga_driver):
    dashboard = DashboardPage(orga_driver).open()
    assert dashboard.title() == "Back-office"


@allure.story("Tableau de bord")
def test_dashboard_metrics_are_consistent(orga_driver):
    dashboard = DashboardPage(orga_driver).open()
    events = int(dashboard.metric("Evenements"))
    published = int(dashboard.metric("Publies"))
    assert events >= 4
    assert published <= events


@allure.story("Creation d'evenement")
def test_create_event_and_add_category(orga_driver):
    global CREATED_TITLE
    CREATED_TITLE = f"Concert Selenium {uuid.uuid4().hex[:6]}"
    with allure.step("Remplir le formulaire de creation"):
        form = EventFormPage(orga_driver).open()
        form.fill(CREATED_TITLE, "Mons", "2027-03-14T20:30", 250, venue="Theatre Royal")
    with allure.step("Valider et verifier la page de gestion"):
        manage = form.submit()
        assert manage.title() == CREATED_TITLE
    with allure.step("Ajouter une categorie Balcon"):
        manage.add_category("Balcon", "45.00", 30)
        assert "Balcon" in manage.category_names()


@allure.story("Creation d'evenement")
def test_created_event_is_listed_in_dashboard(orga_driver):
    dashboard = DashboardPage(orga_driver).open()
    assert CREATED_TITLE in dashboard.event_titles()


@allure.story("Controle d'acces")
def test_client_is_redirected_away_from_admin(driver):
    LoginPage(driver).open().login(config.CLIENT_EMAIL, config.CLIENT_PASSWORD)
    driver.get(config.BASE_URL + "/admin")
    WebDriverWait(driver, 10).until(lambda d: not d.current_url.endswith("/admin"))
    assert driver.current_url.rstrip("/") == config.BASE_URL.rstrip("/")


@allure.story("Connexion organisateur")
def test_login_with_wrong_password_shows_error(driver):
    page = LoginPage(driver).open().login(config.ORGA_EMAIL, "pas-le-bon")
    assert page.error_message() == "Incorrect email or password"
