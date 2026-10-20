import re
import time

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.ui


@pytest.mark.flaky(reruns=3)
def test_full_booking_flow_until_confirmation(logged_in_page: Page, qa_event):
    page = logged_in_page
    page.goto(f"/events/{qa_event['id']}")
    page.locator(".cat-row").filter(has_text="Plein tarif").get_by_role("button", name="+").click()
    page.get_by_role("button", name="Continuer vers le paiement").click()

    expect(page.get_by_text(re.compile(r"Reservation tenue encore \d{2}:\d{2}"))).to_be_visible()
    page.get_by_placeholder("Camille Client").fill("QA Bot")
    time.sleep(2)  # le bouton payer ne marche pas toujours du premier coup, on attend un peu
    page.get_by_role("button", name=re.compile("^Payer")).click()

    expect(page.get_by_role("heading", name="Paiement confirme")).to_be_visible(timeout=10000)
    expect(page.get_by_text(re.compile(r"REF-\d{5}"))).to_be_visible()


@pytest.mark.flaky(reruns=3)
def test_ticket_is_listed_in_my_tickets_after_payment(logged_in_page: Page, qa_event):
    page = logged_in_page
    page.goto(f"/events/{qa_event['id']}")
    page.locator(".cat-row").filter(has_text="Early bird").get_by_role("button", name="+").click()
    page.get_by_role("button", name="Continuer vers le paiement").click()
    page.get_by_placeholder("Camille Client").fill("QA Bot")
    page.get_by_role("button", name=re.compile("^Payer")).click()
    reference = page.get_by_text(re.compile(r"REF-\d{5}")).inner_text().split()[-1]

    page.get_by_role("link", name="Mes billets").first.click()
    ticket = page.locator(".panel").filter(has_text=reference)
    expect(ticket).to_contain_text("Paye")
    expect(ticket.get_by_role("button", name="Telecharger le billet")).to_be_visible()

    with page.expect_download() as dl:
        ticket.get_by_role("button", name="Telecharger le billet").click()
    assert dl.value.suggested_filename.endswith(".pdf")
