from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.dependencies import require_role
from app.database import get_db
from app.models.user import User
from app.services.ai_client import generate_embedding
from app.services.recognition_cache_service import load_embeddings_to_cache


router = APIRouter(
    prefix="/api/admin/face",
    tags=["Admin Face"],
)


# ============================================
# REQUEST MODEL
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

    # Generate embedding through the centralized AI service.
    # The AI service uses InsightFace buffalo_s.
    embedding = generate_embedding(payload.image_base64)

    if embedding is None:
        raise HTTPException(
            status_code=400,
            detail="Face could not be detected or AI service failed",
        )

    try:
        import numpy as np

        embedding_array = np.asarray(
            embedding,
            dtype=np.float32,
        )

        if embedding_array.size != 512:
            raise HTTPException(
                status_code=400,
                detail="Invalid face embedding dimension",
            )

        user.embedding = embedding_array.tobytes()
        user.face_enrolled = True
        user.face_updated_at = datetime.utcnow()

        db.commit()
        db.refresh(user)

        # Refresh Redis recognition cache.
        load_embeddings_to_cache(db)

        return {
            "message": "Face enrolled successfully",
            "employee_id": employee_id,
            "face_enrolled": True,
            "face_updated_at": user.face_updated_at,
            "embedding_dim": int(embedding_array.size),
            "model": "insightface_buffalo_s",
        }

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Face enrollment failed: {str(e)}",
        )


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

    # Refresh Redis cache.
    load_embeddings_to_cache(db)

    return {
        "message": "Face deleted successfully",
        "employee_id": employee_id,
    }