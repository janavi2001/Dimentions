from fastapi import APIRouter
from ..schemas.models import IngestRequest, IngestResponse
from ..services.text import upsert_chunks
router = APIRouter()
@router.post('/ingest_conversation', response_model=IngestResponse)
async def ingest(req: IngestRequest):
    added = upsert_chunks(req.person_id, req.transcript)
    return IngestResponse(chunks_added=added)
