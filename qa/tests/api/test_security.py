"""Tests de securite inspires de l'OWASP API Security Top 10 (2023)."""
import jwt
import pytest

from utils import config
from utils.api_client import ApiClient
from utils.factories import category, create_event, register_user

pytestmark = [pytest.mark.api, pytest.mark.security]


@pytest.fixture
def victim_order(new_client_api, qa_event):
    plein = category(qa_event, "Plein tarif")
    order = new_client_api.create_order(qa_event["id"], [{"category_id": plein["id"], "quantity": 1}]).json()
    new_client_api.pay(order["id"], config.CARD_OK)
    return order


@pytest.fixture
def attacker_api():
    api = ApiClient()
    email, password = register_user(api)
    api.login(email, password)
    return api


# --- API1:2023 Broken Object Level Authorization (RM7 / B3) ------------------
def test_idor_cannot_read_order_of_another_user(attacker_api, victim_order):
    r = attacker_api.get(f"/api/orders/{victim_order['id']}")
    assert r.status_code == 404, f"IDOR : commande d'autrui lisible (B3) -> {r.status_code}"


def test_idor_cannot_download_ticket_of_another_user(attacker_api, victim_order):
    r = attacker_api.get(f"/api/orders/{victim_order['id']}/ticket")
    assert r.status_code == 404, f"IDOR : billet d'autrui telechargeable (B3) -> {r.status_code}"


def test_idor_cannot_pay_order_of_another_user(attacker_api, new_client_api, qa_event):
    plein = category(qa_event, "Plein tarif")
    order = new_client_api.create_order(qa_event["id"], [{"category_id": plein["id"], "quantity": 1}]).json()
    assert attacker_api.pay(order["id"], config.CARD_OK).status_code == 404


# --- API2:2023 Broken Authentication (B9) -------------------------------------
def test_jwt_contains_expiration_claim(anonymous_api):
    token = anonymous_api.login(config.CLIENT_EMAIL, config.CLIENT_PASSWORD).json()["access_token"]
    claims = jwt.decode(token, options={"verify_signature": False})
    assert "exp" in claims, f"Jeton emis sans expiration (B9) : {claims}"


@pytest.mark.parametrize("token", ["abc.def.ghi", "", "Bearer"])
def test_invalid_token_is_rejected(token):
    api = ApiClient(token=token)
    assert api.get("/api/orders/me").status_code == 401


# --- API5:2023 Broken Function Level Authorization ----------------------------
@pytest.mark.parametrize("path", ["/api/admin/summary", "/api/admin/events", "/api/admin/promo"])
def test_client_cannot_access_back_office(client_api, path):
    assert client_api.get(path).status_code == 403


@pytest.mark.parametrize("path", ["/api/admin/summary", "/api/orders/me"])
def test_anonymous_must_authenticate(anonymous_api, path):
    assert anonymous_api.get(path).status_code == 401


# --- Injection (B10) ----------------------------------------------------------
SQLI_PAYLOADS = [
    "%' OR title LIKE '%",
    "' OR '1'='1",
    "x%' OR 1=1 --",
]


@pytest.fixture(scope="module")
def draft_event(admin_api):
    return create_event(admin_api, status="draft")


@pytest.mark.parametrize("payload", SQLI_PAYLOADS)
def test_search_is_not_injectable(anonymous_api, draft_event, payload):
    r = anonymous_api.get("/api/events", params={"q": payload})
    assert r.status_code == 200
    titles = [e["title"] for e in r.json()]
    assert draft_event["title"] not in titles, f"Injection SQL : le brouillon fuit avec {payload!r} (B10)"
    assert all(e["status"] == "published" for e in r.json())
