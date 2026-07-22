from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.db.session import get_db
from app.schemas.auth import RegisterRequest, TokenResponse
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/register")
def register_user(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.employee_id == payload.employee_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Employee ID already exists")

    user = User(
        employee_id=payload.employee_id,
        name=payload.name,
        password_hash=hash_password(payload.password),
        role="user"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "User registered successfully",
             "user_id": str(user.id)}


@router.post("/login")
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.employee_id == form_data.username).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id)})

    return {"access_token": token, "token_type": "bearer"}
