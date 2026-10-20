import pytest

from utils.schema import schema_errors

pytestmark = pytest.mark.api


@pytest.mark.schema
def test_catalog_items_match_event_schema(anonymous_api):
    """B11 : chaque evenement du catalogue doit respecter le contrat (dont 'capacity')."""
    r = anonymous_api.get("/api/events")
    assert r.status_code == 200
    events = r.json()
    assert events, "Le catalogue ne devrait pas etre vide"
    errors = {e.get("id"): schema_errors(e, "event.schema.json") for e in events}
    errors = {k: v for k, v in errors.items() if v}
    assert not errors, f"Reponses non conformes au schema : {errors}"


@pytest.mark.schema
def test_event_detail_matches_schema(anonymous_api, qa_event):
    r = anonymous_api.get(f"/api/events/{qa_event['id']}")
    assert r.status_code == 200
    assert schema_errors(r.json(), "event_detail.schema.json") == []


def test_catalog_only_lists_published_events(anonymous_api):
    events = anonymous_api.get("/api/events").json()
    assert {e["status"] for e in events} == {"published"}


def test_search_by_keyword(anonymous_api, qa_event):
    keyword = qa_event["title"].split()[-1]  # suffixe unique de l'evenement de test
    r = anonymous_api.get("/api/events", params={"q": keyword})
    assert r.status_code == 200
    titles = [e["title"] for e in r.json()]
    assert titles == [qa_event["title"]]


@pytest.mark.parametrize("city", ["Bruxelles", "Gand", "Liege"])
def test_filter_by_city(anonymous_api, city):
    events = anonymous_api.get("/api/events", params={"city": city}).json()
    assert events, f"Aucun evenement a {city} dans le jeu de demo"
    assert all(e["city"] == city for e in events)


def test_unknown_event_returns_404(anonymous_api):
    assert anonymous_api.get("/api/events/999999").status_code == 404


def test_event_availability_is_sum_of_categories(anonymous_api, qa_event):
    detail = anonymous_api.get(f"/api/events/{qa_event['id']}").json()
    assert detail["available"] == sum(c["available"] for c in detail["categories"])
