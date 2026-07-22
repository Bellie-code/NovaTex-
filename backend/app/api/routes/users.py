import base64
import numpy as np
import cv2
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.core.security import hash_password
from app.ai.face import extract_face_embedding  # you must have this

router = APIRouter(prefix="/api/users", tags=["Users"])


def decode_base64_image(image_base64: str):
    if "," in image_base64:
        image_base64 = image_base64.split(",")[1]

    decoded = base64.b64decode(image_base64)
    np_arr = np.frombuffer(decoded, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return img


@router.post("/register")
def register_user(payload: dict, db: Session = Depends(get_db)):
    """
    payload = {
        "employee_id": "EMP201",
        "name": "Richa",
        "password": "12345",
        "image_base64": "data:image/jpeg;base64,..."
    }
    """

    employee_id = payload.get("employee_id")
    name = payload.get("name")
    password = payload.get("password")
    image_base64 = payload.get("image_base64")

    if not employee_id or not name or not password or not image_base64:
        raise HTTPException(status_code=400, detail="All fields required")

    # check existing
    existing = db.query(User).filter(User.employee_id == employee_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Employee ID already exists")

    frame = decode_base64_image(image_base64)

    if frame is None:
        raise HTTPException(status_code=400, detail="Invalid image")

    embedding = extract_face_embedding(frame)

    if embedding is None:
        raise HTTPException(status_code=400, detail="Face not detected properly")

    user = User(
        employee_id=employee_id,
        name=name,
        password_hash=hash_password(password),
        face_embedding=embedding.tolist(),
        role="employee"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "id": user.id,
        "employee_id": user.employee_id,
        "name": user.name,
        "message": "User registered successfully"
    }


@router.get("/all")
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()

    return [
        {
            "id": u.id,
            "employee_id": u.employee_id,
            "name": u.name,
            "role": u.role
        }
        for u in users
    ]


