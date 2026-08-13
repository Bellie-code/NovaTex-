from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import get_current_user
from app.schemas.recognition import RecognizeRequest, RecognizeResponse
from app.services.recognition_service import recognize_user


router = APIRouter(
    prefix="/api/recognition",
    tags=["Recognition"],
)


@router.post(
    "/recognize",
    response_model=RecognizeResponse,
)
def recognize_face_api(
    payload: RecognizeRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return recognize_user(
        db,
        payload.image_base64,
    )