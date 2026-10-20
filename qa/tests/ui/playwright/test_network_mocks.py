"""Isoler l'interface du back-end en interceptant les appels reseau (page.route)."""
import re

import pytest
from playwright.sync_api import Page, Route, expect

from utils.data_loader import load_json

pytestmark = pytest.mark.ui


def test_catalog_renders_mocked_events(page: Page):
    page.route("**/api/events", lambda route: route.fulfill(json=load_json("mock_events.json")))
    page.goto("/")
    cards = page.locator("a.card")
    expect(cards).to_have_count(1)
    expect(cards.first).to_contain_text("Evenement simule par le test")
    expect(cards.first).to_contain_text("Namur")


def test_catalog_handles_server_error(page: Page):
    page.route("**/api/events", lambda route: route.fulfill(status=500, body="Internal Server Error"))
    page.goto("/")
    expect(page.get_by_text("Aucun evenement trouve.")).to_be_visible()


def test_payment_gateway_timeout_message(logged_in_page: Page, qa_event):
    def gateway_down(route: Route):
        route.fulfill(status=504, json={"detail": "Passerelle de paiement indisponible"})

    logged_in_page.route(re.compile(r".*/api/orders/\d+/pay$"), gateway_down)
    logged_in_page.goto(f"/events/{qa_event['id']}")
    logged_in_page.locator(".cat-row").filter(has_text="Plein tarif").get_by_role("button", name="+").click()
    logged_in_page.get_by_role("button", name="Continuer vers le paiement").click()
    logged_in_page.get_by_placeholder("Camille Client").fill("QA Bot")
    logged_in_page.get_by_role("button", name=re.compile("^Payer")).click()
    expect(logged_in_page.locator(".notice-err")).to_have_text("Passerelle de paiement indisponible")


def test_payment_request_payload(logged_in_page: Page, qa_event):
    """On espionne la requete envoyee au back-end sans la modifier."""
    logged_in_page.goto(f"/events/{qa_event['id']}")
    logged_in_page.locator(".cat-row").filter(has_text="Plein tarif").get_by_role("button", name="+").click()
    logged_in_page.get_by_role("button", name="Continuer vers le paiement").click()
    logged_in_page.get_by_placeholder("Camille Client").fill("QA Bot")
    with logged_in_page.expect_request(re.compile(r".*/api/orders/\d+/pay$")) as req_info:
        logged_in_page.get_by_role("button", name=re.compile("^Payer")).click()
    payload = req_info.value.post_data_json
    assert payload["card_number"] == "4242 4242 4242 4242"
    assert payload["exp_month"] == 12
    assert payload["cardholder"] == "QA Bot"
