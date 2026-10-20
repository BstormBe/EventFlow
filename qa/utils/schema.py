"""Validation de reponses JSON contre les schemas du dossier qa/schemas."""
import json
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas"


def _registry():
    resources = []
    for f in SCHEMA_DIR.glob("*.json"):
        content = json.loads(f.read_text(encoding="utf-8"))
        resources.append((f.name, Resource.from_contents(content)))
        resources.append((content["$id"], Resource.from_contents(content)))
    return Registry().with_resources(resources)


def schema_errors(instance, schema_name):
    """Retourne la liste des erreurs (vide si conforme) - plus lisible qu'une exception."""
    schema = json.loads((SCHEMA_DIR / schema_name).read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, registry=_registry())
    return [f"{'/'.join(map(str, e.path)) or '<racine>'}: {e.message}" for e in validator.iter_errors(instance)]
