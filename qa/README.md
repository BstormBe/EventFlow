# EventFlow-QA

Projet de tests automatises de l'application EventFlow (formation Testeur QA 2026).

## Lancer l'application

Depuis la racine du depot :

```bash
docker compose up -d --build
# avec les bugs du fil rouge :
SEED_BUGS=true docker compose up -d --build
```

Remise a zero des donnees : `docker compose down -v`.

## Installer les tests

```bash
cd qa
python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install -r requirements.txt
```

## Lancer les tests

```bash
pytest tests/api                 # tests d'API
pytest -m security               # uniquement les tests de securite
pytest -m db                     # coherence base de donnees (PostgreSQL du docker compose)
```

La configuration (URL, comptes) est dans `.env`.
