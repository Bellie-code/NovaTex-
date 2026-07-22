from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
import redis
import time

from app.database import get_db
from app.models.user import User
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    validate_token_type
)
from app.core.config import settings


# =====================================================
# REDIS CLIENT (Memurai)
# =====================================================

redis_client = redis.Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True
)


router = APIRouter(prefix="/api/auth", tags=["Auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# =====================================================
# LOGIN
# =====================================================

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.employee_id == form_data.username
    ).first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid employee_id or password"
        )

    access_token = create_access_token({
        "sub": user.employee_id,
        "role": user.role
    })

    refresh_token = create_refresh_token({
        "sub": user.employee_id,
        "role": user.role
    })

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "role": user.role
    }


# =====================================================
# LOGOUT (TOKEN BLACKLIST)
# =====================================================

@router.post("/logout")
def logout(token: str = Depends(oauth2_scheme)):

    payload = decode_token(token)

    if not payload or not validate_token_type(payload, "access"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    exp_timestamp = payload.get("exp")

    if not exp_timestamp:
        raise HTTPException(status_code=400, detail="Invalid token")

    # Calculate remaining time until expiration
    ttl = exp_timestamp - int(time.time())

    if ttl > 0:
        redis_client.setex(
            f"blacklist:{token}",
            ttl,
            "revoked"
        )

    return {"message": "Logged out successfully"}


# =====================================================
# REFRESH TOKEN
# =====================================================

class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/refresh")
def refresh_token_endpoint(payload: RefreshRequest):

    decoded = decode_token(payload.refresh_token)

    if not decoded or not validate_token_type(decoded, "refresh"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    new_access_token = create_access_token({
        "sub": decoded["sub"],
        "role": decoded["role"]
    })

    return {"access_token": new_access_token}


# =====================================================
# GET CURRENT USER
# =====================================================

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    # Check blacklist
    if redis_client.exists(f"blacklist:{token}"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked"
        )

    payload = decode_token(token)

    if not payload or not validate_token_type(payload, "access"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    employee_id = payload.get("sub")

    if employee_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    user = (
        db.query(User)
        .filter(User.employee_id == employee_id)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user