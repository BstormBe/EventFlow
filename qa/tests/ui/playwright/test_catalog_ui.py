import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.ui


def test_catalog_displays_event_cards(page: Page):
    page.goto("/")
    expect(page.get_by_role("heading", name="Vivez l'evenement")).to_be_visible()
    expect(page.locator("a.card").first).to_be_visible()


def test_search_finds_the_qa_event(page: Page, qa_event):
    keyword = qa_event["title"].split()[-1]
    page.goto("/")
    page.get_by_placeholder("Rechercher un evenement").fill(keyword)
    page.get_by_role("button", name="Rechercher").click()
    cards = page.locator("a.card")
    expect(cards).to_have_count(1)
    expect(cards.first.get_by_role("heading")).to_have_text(qa_event["title"])


def test_search_without_result_shows_message(page: Page):
    page.goto("/")
    page.get_by_placeholder("Rechercher un evenement").fill("zzz-introuvable")
    page.get_by_placeholder("Rechercher un evenement").press("Enter")
    expect(page.get_by_text("Aucun evenement trouve.")).to_be_visible()


def test_event_card_opens_detail_page(page: Page, qa_event):
    page.goto(f"/events/{qa_event['id']}")
    expect(page.get_by_role("heading", name=qa_event["title"])).to_be_visible()
    expect(page.locator(".cat-row")).to_have_count(3)
