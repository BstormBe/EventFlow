import re

import pytest
from playwright.sync_api import Page, expect

from utils import config

pytestmark = pytest.mark.ui


def fill_login(page: Page, email, password):
    page.goto("/login")
    page.locator("input[type=email]").fill(email)
    page.locator("input[type=password]").fill(password)
    page.get_by_role("button", name="Se connecter").click()


@pytest.mark.smoke
def test_login_success_shows_my_tickets_link(page: Page):
    fill_login(page, config.CLIENT_EMAIL, config.CLIENT_PASSWORD)
    expect(page).to_have_url(re.compile(r"/$"))
    expect(page.get_by_role("link", name="Mes billets")).to_be_visible()


def test_login_wrong_password_shows_error(page: Page):
    fill_login(page, config.CLIENT_EMAIL, "mauvais")
    expect(page.locator(".notice-err")).to_have_text("Incorrect email or password")
    expect(page).to_have_url(re.compile(r"/login$"))


def test_logout(logged_in_page: Page):
    logged_in_page.goto("/")
    logged_in_page.get_by_role("button", name="Deconnexion").click()
    expect(logged_in_page.get_by_role("link", name="Connexion")).to_be_visible()


def test_protected_page_redirects_to_login(page: Page):
    page.goto("/tickets")
    expect(page).to_have_url(re.compile(r"/login$"))


def test_client_does_not_see_back_office_link(logged_in_page: Page):
    logged_in_page.goto("/")
    expect(logged_in_page.get_by_role("link", name="Mes billets")).to_be_visible()
    expect(logged_in_page.get_by_role("link", name=re.compile("Back-office"))).to_have_count(0)
