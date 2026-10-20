import pytest
from playwright.sync_api import Page

from utils import config
from utils.api_client import ApiClient


@pytest.fixture(scope="session")
def base_url():
    return config.BASE_URL


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {**browser_context_args, "locale": "fr-BE", "viewport": {"width": 1366, "height": 900}}


@pytest.fixture
def logged_in_page(page: Page) -> Page:
    """Connexion rapide : on obtient le jeton par l'API et on l'injecte dans le localStorage
    avant le chargement de la SPA (evite de repasser par l'ecran de login a chaque test)."""
    token = ApiClient().login(config.CLIENT_EMAIL, config.CLIENT_PASSWORD).json()["access_token"]
    page.add_init_script(f"window.localStorage.setItem('ef_token', '{token}')")
    return page
