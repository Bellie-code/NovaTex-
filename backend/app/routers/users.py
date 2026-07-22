import base64
import numpy as np
import cv2
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services.ai_client import generate_embedding
from app.core.security import hash_password
from app.schemas.user_schema import UserRegisterSchema
from app.core.dependencies import require_role

# Redis embedding refresh
from app.services.recognition_cache_service import load_embeddings_to_cache

router = APIRouter(prefix="/api/users", tags=["Users"])


# =====================================================
# BASE64 IMAGE DECODER
# =====================================================

def decode_base64_image(image_base64: str):
    try:
        if "," in image_base64:
            image_base64 = image_base64.split(",")[1]

        decoded = base64.b64decode(image_base64)
        np_arr = np.frombuffer(decoded, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        return img

    except Exception:
        return None


# =====================================================
# REGISTER USER + FACE ENROLLMENT (ADMIN ONLY)
# =====================================================

@router.post("/register")
def register_user(
    payload: UserRegisterSchema,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("admin"))
):

    employee_id = payload.employee_id.strip()
    name = payload.name.strip()
    password = payload.password
    image_base64 = payload.image_base64

    # -------------------------------------------------
    # PASSWORD VALIDATION
    # -------------------------------------------------

    if len(password.encode("utf-8")) > 72:
        raise HTTPException(
            status_code=400,
            detail="Password cannot be longer than 72 bytes"
        )

    # -------------------------------------------------
    # CHECK IF USER EXISTS
    # -------------------------------------------------

    existing = db.query(User).filter(
        User.employee_id == employee_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Employee already exists"
        )

    # -------------------------------------------------
    # VALIDATE IMAGE
    # -------------------------------------------------

    frame = decode_base64_image(image_base64)

    if frame is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid image data"
        )

    # -------------------------------------------------
    # GENERATE FACE EMBEDDING
    # -------------------------------------------------

    embedding_list = generate_embedding(image_base64)

    if embedding_list is None:
        raise HTTPException(
            status_code=400,
            detail="Face not detected"
        )

    embedding = np.array(embedding_list, dtype=np.float32)

    # -------------------------------------------------
    # SAVE USER
    # -------------------------------------------------

    try:

        user = User(
            employee_id=employee_id,
            name=name,
            password_hash=hash_password(password),
            embedding=embedding.tobytes(),
            role="employee"
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        # 🔥 Refresh Redis embedding cache
        load_embeddings_to_cache(db)

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Database error"
        )

    return {
        "message": "User registered successfully",
        "employee_id": user.employee_id,
        "name": user.name
    }


# =====================================================
# GET ALL USERS (ADMIN ONLY)
# =====================================================

@router.get("/all")
def get_all_users(
    db: Session = Depends(get_db),
    current_user = Depends(require_role("admin"))
):

    users = db.query(User).all()

    return [
        {
            "employee_id": u.employee_id,
            "name": u.name,
            "role": u.role
        }
        for u in users
    ]


# =====================================================
# DELETE USER (ADMIN ONLY)
# =====================================================

@router.delete("/{employee_id}")
def delete_user(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("admin"))
):

    user = db.query(User).filter(
        User.employee_id == employee_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    db.delete(user)
    db.commit()

    # Refresh embedding cache
    load_embeddings_to_cache(db)

    return {
        "message": "User deleted successfully",
        "employee_id": employee_id
    }