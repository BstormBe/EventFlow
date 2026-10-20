"""Test de charge "flash sale" : beaucoup d'acheteurs sur une categorie a tres petit quota (RM1 / B1).

Lancement (application demarree) :
    cd qa
    locust -f tests/performance/locustfile.py --host http://localhost:8000 \
           --headless -u 50 -r 10 -t 1m --html reports/locust.html

A la fin, le script verifie en base qu'aucune categorie n'a ete survendue.
"""
import uuid

import requests
from locust import HttpUser, between, events, task

from utils import config, db

FLASH = {}


@events.test_start.add_listener
def create_flash_sale(environment, **_):
    host = environment.host or config.API_URL
    token = requests.post(f"{host}/api/auth/token", timeout=10, data={
        "username": config.ADMIN_EMAIL, "password": config.ADMIN_PASSWORD}).json()["access_token"]
    r = requests.post(f"{host}/api/admin/events", timeout=10, headers={"Authorization": f"Bearer {token}"}, json={
        "title": f"Flash sale {uuid.uuid4().hex[:6]}", "city": "Bruxelles", "venue": "Forest National",
        "starts_at": "2027-01-15T20:00:00", "capacity": 20, "status": "published",
        "categories": [{"name": "Fosse", "price_cents": 4900, "quota": 20}],
    })
    event = r.json()
    FLASH["event_id"] = event["id"]
    FLASH["category_id"] = event["categories"][0]["id"]
    print(f"Flash sale creee : evenement {FLASH['event_id']}")


@events.test_stop.add_listener
def check_oversell(environment, **_):
    rows = db.fetch_all(
        """SELECT c.quota, COALESCE(SUM(i.quantity), 0) AS reserved
           FROM ticket_categories c
           LEFT JOIN order_items i ON i.category_id = c.id
           LEFT JOIN orders o ON o.id = i.order_id AND o.status IN ('paid', 'pending')
           WHERE c.id = :cid GROUP BY c.quota""",
        cid=FLASH.get("category_id"),
    )
    if rows and rows[0]["reserved"] > rows[0]["quota"]:
        print(f"SURVENTE DETECTEE (B1) : {rows[0]['reserved']} billets pour un quota de {rows[0]['quota']}")
        environment.process_exit_code = 1
    else:
        print(f"Pas de survente : {rows}")


class Buyer(HttpUser):
    wait_time = between(0.5, 2)

    def on_start(self):
        email = f"load-{uuid.uuid4().hex[:10]}@example.com"
        self.client.post("/api/auth/register", json={"email": email, "password": "Passw0rd!"}, name="/api/auth/register")
        r = self.client.post("/api/auth/token", data={"username": email, "password": "Passw0rd!"}, name="/api/auth/token")
        self.client.headers["Authorization"] = f"Bearer {r.json()['access_token']}"

    @task(3)
    def browse_catalog(self):
        self.client.get("/api/events", name="/api/events")

    @task(2)
    def view_flash_event(self):
        self.client.get(f"/api/events/{FLASH['event_id']}", name="/api/events/[id]")

    @task(1)
    def buy(self):
        with self.client.post("/api/orders", name="/api/orders", catch_response=True, json={
            "event_id": FLASH["event_id"], "items": [{"category_id": FLASH["category_id"], "quantity": 2}],
        }) as r:
            if r.status_code == 409:
                r.success()  # stock epuise : comportement attendu, pas une erreur de performance
            elif r.status_code == 201:
                self.client.post(f"/api/orders/{r.json()['id']}/pay", name="/api/orders/[id]/pay", json={
                    "card_number": config.CARD_OK, "exp_month": 12, "exp_year": 2030, "cvc": "123"})
