from fastapi import APIRouter
from ..schemas.models import AskRequest, AskResponse
from ..services.rag import answer_name, compose_relationship_answer
from ..services.text import search_person_chunks
router = APIRouter()
@router.post('/ask', response_model=AskResponse)
async def ask(req: AskRequest):
    q = req.question.lower()
    if 'name' in q:
        return AskResponse(**answer_name('Your stored name'))
    cands = search_person_chunks(req.person_id, req.question, k=6)
    return AskResponse(**compose_relationship_answer(cands))
