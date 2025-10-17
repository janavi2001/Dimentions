from pydantic import BaseModel
from typing import Optional, List

class IdentifyResponse(BaseModel):
    """
    Returns: dict with keys:
      - status (str)
      - person_id (str | None)
      - confidence (float)
      - full_name (str | None)
    """
    status: str
    person_id: Optional[str] = None
    confidence: float
    full_name: Optional[str] = None

class RegisterResponse(BaseModel):
    """
    Returns: dict with keys:
      - person_id: str
      - ok: bool
    """
    person_id: str
    ok: bool

class IngestRequest(BaseModel):
    person_id: str
    transcript: str

class IngestResponse(BaseModel):
    chunks_added: int

class AskRequest(BaseModel):
    person_id: str
    question: str

class AskResponse(BaseModel):
    answer: str
    sources: List[dict]
