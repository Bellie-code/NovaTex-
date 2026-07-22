import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.face_embedding import FaceEmbedding
from app.schemas.face import FaceEnrollRequest, FaceEnrollResponse
from app.services.face_service import decode_base64_image, extract_embedding
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/face", tags=["Face Enrollment"])



@router.post("/enroll", response_model=FaceEnrollResponse)
def enroll_face(
    payload: FaceEnrollRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        img = decode_base64_image(payload.image_base64)

        if img is None:
            raise ValueError("Invalid image data")

        embedding = extract_embedding(img)

        if embedding is None:
            raise ValueError("No face detected in the image")

        embedding_str = json.dumps(embedding.tolist())

        existing = (
            db.query(FaceEmbedding)
            .filter(FaceEmbedding.user_id == current_user.id)
            .first()
        )

        if existing:
            existing.embedding = embedding_str
            db.commit()
            return FaceEnrollResponse(
                message="Face embedding updated",
                embedding_dim=len(embedding),
            )

        new_embedding = FaceEmbedding(
            user_id=current_user.id,
            embedding=embedding_str,
            model_version="insightface_buffalo_l",
        )

        db.add(new_embedding)
        db.commit()

        return FaceEnrollResponse(
            message="Face enrolled successfully",
            embedding_dim=len(embedding),
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
