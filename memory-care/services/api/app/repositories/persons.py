"""
Tiny JSON-backed profile store.
All functions return JSON-safe dicts and primitives.
"""
import os, json, uuid, datetime
from typing import Dict, Any, List

# Default path: <repo-root>/memory-care/data/persons.json
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
DATA_DIR = os.path.join(REPO_ROOT, "data")
os.makedirs(DATA_DIR, exist_ok=True)
PERSONS_JSON = os.path.join(DATA_DIR, "persons.json")

def _load() -> Dict[str, Any]:
    """
    Returns: dict {'persons': {person_id: {...}}}
    """
    if not os.path.exists(PERSONS_JSON):
        return {"persons": {}}
    with open(PERSONS_JSON, "r", encoding="utf-8") as f:
        return json.load(f)

def _save(doc: Dict[str, Any]) -> None:
    with open(PERSONS_JSON, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2)

def create_person(full_name: str, relationship_note: str = "", caregiver_contacts: List[Dict[str,str]] | None = None, consent_text: str = "") -> Dict[str, Any]:
    """
    Returns: dict with keys: person_id (str), full_name (str), relationship_note (str), caregiver_contacts (list), consent_text (str), created_at (str)
    """
    doc = _load()
    pid = str(uuid.uuid4())
    person = {
        "person_id": pid,
        "full_name": full_name,
        "relationship_note": relationship_note,
        "caregiver_contacts": caregiver_contacts or [],
        "consent_text": consent_text,
        "created_at": datetime.datetime.utcnow().isoformat(),
        "updated_at": datetime.datetime.utcnow().isoformat(),
    }
    doc["persons"][pid] = person
    _save(doc)
    return person

def get_person(person_id: str) -> Dict[str, Any]:
    """
    Returns: dict for the person_id, or {} if not found
    """
    doc = _load()
    return doc["persons"].get(person_id, {})

def update_person(person_id: str, patch: Dict[str, Any]) -> Dict[str, Any]:
    """
    Returns: dict of updated person or {} if not found
    """
    doc = _load()
    if person_id not in doc["persons"]:
        return {}
    doc["persons"][person_id].update(patch)
    doc["persons"][person_id]["updated_at"] = datetime.datetime.utcnow().isoformat()
    _save(doc)
    return doc["persons"][person_id]
