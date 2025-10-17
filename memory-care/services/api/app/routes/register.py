from fastapi import APIRouter, UploadFile, File, Form
from ..schemas.models import RegisterResponse
from ..services.face import add_face_embedding
import uuid
router = APIRouter()
@router.post('/register', response_model=RegisterResponse)
async def register(full_name: str = Form(...), relationship_note: str = Form(''), consent_text: str = Form(''), face_image: UploadFile = File(...)):
    person_id = str(uuid.uuid4())
    img = await face_image.read()
    add_face_embedding(person_id, img)
    return RegisterResponse(person_id=person_id, ok=True)
