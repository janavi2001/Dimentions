from fastapi import APIRouter, UploadFile, File
from ..schemas.models import IdentifyResponse
from ..services.face import search_face
router = APIRouter()
@router.post('/identify', response_model=IdentifyResponse)
async def identify(face_image: UploadFile = File(...)):
    img = await face_image.read()
    sim, meta = search_face(img)
    if not meta: return IdentifyResponse(status='unknown', person_id=None, confidence=0.0)
    if sim >= 0.65: return IdentifyResponse(status='match', person_id=meta['person_id'], confidence=sim)
    if sim >= 0.55: return IdentifyResponse(status='unsure', person_id=meta['person_id'], confidence=sim)
    return IdentifyResponse(status='unknown', person_id=None, confidence=sim)
