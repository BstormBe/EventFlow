"""Configuration centrale des tests (lue depuis qa/.env ou l'environnement)."""
import os

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

API_URL = os.getenv("API_URL", "http://localhost:8000")
BASE_URL = os.getenv("BASE_URL", "http://localhost:5173")
DB_URL = os.getenv("DB_URL", "postgresql+psycopg2://eventflow:eventflow@localhost:5432/eventflow")

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@eventflow.test")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin1234")
ORGA_EMAIL = os.getenv("ORGA_EMAIL", "orga@eventflow.test")
ORGA_PASSWORD = os.getenv("ORGA_PASSWORD", "orga1234")
CLIENT_EMAIL = os.getenv("CLIENT_EMAIL", "client@eventflow.test")
CLIENT_PASSWORD = os.getenv("CLIENT_PASSWORD", "client1234")

# Cartes de test de la passerelle de paiement simulee
CARD_OK = "4242 4242 4242 4242"
CARD_DECLINED = "4000 0000 0000 0002"
