from fastapi import APIRouter, UploadFile, File, Form
from ..schemas.models import RegisterResponse
from ..services.face import add_face_embedding
from ..repositories.persons import create_person
import uuid

router = APIRouter()

@router.post("/register", response_model=RegisterResponse)
async def register(
    full_name: str = Form(...),
    relationship_note: str = Form(""),
    consent_text: str = Form(""),
    face_image: UploadFile = File(...),
):
    """
    Returns: RegisterResponse with person_id (str), ok (bool)
    """
    # 1) Create profile
    person = create_person(full_name=full_name, relationship_note=relationship_note, caregiver_contacts=None, consent_text=consent_text)
    person_id = person["person_id"]

    # 2) Store first face embedding
    img = await face_image.read()
    add_face_embedding(person_id, img)

    return RegisterResponse(person_id=person_id, ok=True)
