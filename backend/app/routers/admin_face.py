from datetime import datetime

import numpy as np
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.dependencies import require_role
from app.database import get_db
from app.models.user import User
from app.services.face_service import (
    decode_base64_image,
    extract_embedding,
)
from app.services.recognition_cache_service import load_embeddings_to_cache

router = APIRouter(
    prefix="/api/admin/face",
    tags=["Admin Face"],
)


# ============================================
# Request Model
# ============================================

class FaceEnrollRequest(BaseModel):
    image_base64: str


# ============================================
# ENROLL / UPDATE FACE
# ============================================

@router.post("/enroll/{employee_id}")
async def enroll_face(
    employee_id: str,
    payload: FaceEnrollRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin")),
):

    user = db.query(User).filter(
        User.employee_id == employee_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Employee not found",
        )

    # Decode Base64 image
    image = decode_base64_image(payload.image_base64)

    if image is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid image",
        )

    # Generate embedding
    embedding = extract_embedding(image)

    if embedding is None:
        raise HTTPException(
            status_code=400,
            detail="Face not detected",
        )

    # Save embedding
    user.embedding = np.asarray(
        embedding,
        dtype=np.float32,
    ).tobytes()

    user.face_enrolled = True
    user.face_updated_at = datetime.utcnow()

    db.commit()
    db.refresh(user)

    # Refresh Redis cache
    load_embeddings_to_cache(db)

    return {
        "message": "Face enrolled successfully",
        "employee_id": employee_id,
        "face_enrolled": True,
        "face_updated_at": user.face_updated_at,
    }


# ============================================
# DELETE FACE
# ============================================

@router.delete("/delete/{employee_id}")
def delete_face(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin")),
):

    user = db.query(User).filter(
        User.employee_id == employee_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    user.embedding = None
    user.face_enrolled = False
    user.face_updated_at = None

    db.commit()
    db.refresh(user)

    # Refresh Redis cache
    load_embeddings_to_cache(db)

    return {
        "message": "Face deleted successfully"
    }