"""Envoie un rapport JUnit vers Xray Cloud (projet EF) apres une execution.

Usage : pytest --junitxml=reports/junit.xml && python utils/xray_export.py reports/junit.xml
"""
import sys

import requests

XRAY_URL = "https://xray.cloud.getxray.app/api/v2"
CLIENT_ID = "5B9E97863E8AA012D3D7E2B346A7A655"
CLIENT_SECRET = "cda177426d66d5914814028da4a158c23cef5742b83a8360068b8480fe30d762"
PROJECT_KEY = "EF"


def get_token():
    r = requests.post(f"{XRAY_URL}/authenticate", json={"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET})
    r.raise_for_status()
    return r.json()


def push_junit(path):
    token = get_token()
    with open(path, "rb") as f:
        r = requests.post(
            f"{XRAY_URL}/import/execution/junit?projectKey={PROJECT_KEY}",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/xml"},
            data=f.read(),
        )
    print(r.status_code, r.text)


if __name__ == "__main__":
    push_junit(sys.argv[1] if len(sys.argv) > 1 else "reports/junit.xml")
