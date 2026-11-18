import time

import requests

URL = "http://localhost:8000"


def get_token():
    r = requests.post(
        URL + "/api/auth/token",
        data={"username": "admin@eventflow.test", "password": "admin1234"},
        timeout=5,
    )
    return r.json()["access_token"]


def test_1():
    token = get_token()
    h = {"Authorization": "Bearer " + token}
    r = requests.post(
        URL + "/api/admin/promo",
        headers=h,
        json={"code": "TEST" + str(int(time.time())), "percent_off": 20, "max_uses": 5},
        timeout=5,
    )
    print(r.json())
    assert r.status_code == 201


def test_promo2():
    token = get_token()
    h = {"Authorization": "Bearer " + token}
    r = requests.get(URL + "/api/admin/promo", headers=h, timeout=5)
    promos = r.json()
    for p in promos:
        if p["code"] == "WELCOME10":
            assert p["percent_off"] == 10


def test_disable_promo():
    token = get_token()
    h = {"Authorization": "Bearer " + token}
    r = requests.post(
        URL + "/api/admin/promo",
        headers=h,
        json={"code": "DIS" + str(int(time.time())), "percent_off": 5, "max_uses": 1},
        timeout=5,
    )
    id = r.json()["id"]
    r2 = requests.post(URL + "/api/admin/promo/" + str(id) + "/disable", headers=h, timeout=5)
    assert r2.json()["expires_at"] != None


def test_client_cant_see_promos():
    r = requests.post(
        URL + "/api/auth/token",
        data={"username": "client@eventflow.test", "password": "client1234"},
        timeout=5,
    )
    token = r.json()["access_token"]
    r = requests.get(URL + "/api/admin/promo", headers={"Authorization": "Bearer " + token}, timeout=5)
    assert r.status_code == 403
