"""
Feedback routes:
- POST /feedback/misidentify  (user says "Not you?")
Logs a misidentification so you can inspect later.
"""
import os, json, datetime
from fastapi import APIRouter, Form
from typing import Optional

router = APIRouter()

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
LOGS_DIR = os.path.join(REPO_ROOT, "data")
os.makedirs(LOGS_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOGS_DIR, "misidentify.log")

@router.post("/feedback/misidentify")
async def misidentify(candidate_person_id: str = Form(...), note: Optional[str] = Form(None)):
    """
    Returns: dict with keys:
      - ok (bool)
    """
    event = {
        "candidate_person_id": candidate_person_id,
        "note": note or "",
        "timestamp": datetime.datetime.utcnow().isoformat(),
    }
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
    except Exception:
        pass
    return {"ok": True}
