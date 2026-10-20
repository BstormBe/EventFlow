import pytest

from utils import config
from utils.api_client import ApiClient
from utils.factories import create_event, register_user


@pytest.fixture(scope="session")
def admin_api():
    api = ApiClient()
    r = api.login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD)
    assert r.status_code == 200, "Login admin impossible : l'application tourne-t-elle ?"
    return api


@pytest.fixture
def anonymous_api():
    return ApiClient()


@pytest.fixture
def client_api():
    """Client du jeu de demo (client@eventflow.test)."""
    api = ApiClient()
    api.login(config.CLIENT_EMAIL, config.CLIENT_PASSWORD)
    return api


@pytest.fixture
def new_client_api():
    """Client fraichement inscrit : aucune commande, aucun effet de bord."""
    api = ApiClient()
    email, password = register_user(api)
    api.login(email, password)
    return api


@pytest.fixture(scope="session")
def qa_event(admin_api):
    """Evenement publie, cree une fois par session, pour isoler les tests du jeu de demo."""
    return create_event(admin_api)
