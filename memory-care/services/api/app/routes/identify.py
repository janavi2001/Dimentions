from fastapi import APIRouter, UploadFile, File
from ..schemas.models import IdentifyResponse          # <-- relative import
from ..services.face import search_face
from ..core.ml_settings import MATCH_SIM, UNSURE_SIM   # if you used Option A

router = APIRouter()

@router.post("/identify", response_model=IdentifyResponse)
async def identify(face_image: UploadFile = File(...)):
    img = await face_image.read()
    sim, meta = search_face(img)
    if not meta:
        return IdentifyResponse(status="unknown", person_id=None, confidence=0.0)
    if sim >= MATCH_SIM:
        return IdentifyResponse(status="match", person_id=meta["person_id"], confidence=sim)
    if sim >= UNSURE_SIM:
        return IdentifyResponse(status="unsure", person_id=meta["person_id"], confidence=sim)
    return IdentifyResponse(status="unknown", person_id=None, confidence=sim)
