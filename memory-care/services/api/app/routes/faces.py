"""
Face utility routes:
- POST /faces/add   (add additional sample for an existing person)
"""
from fastapi import APIRouter, UploadFile, File, Form
from ..services.face import add_face_embedding

router = APIRouter()

@router.post("/faces/add")
async def add_face(
    person_id: str = Form(...),
    face_image: UploadFile = File(...),
):
    """
    Returns: dict with keys:
      - ok (bool)
      - person_id (str)
    """
    img = await face_image.read()
    add_face_embedding(person_id, img)
    return {"ok": True, "person_id": person_id}
