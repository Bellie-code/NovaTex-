from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.database import get_db
from app.models.user import User
from app.core.dependencies import require_role

router = APIRouter(prefix="/api/admin/users", tags=["Admin Users"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ====================================
# GET ALL EMPLOYEES
# ====================================
@router.get("/")
def get_users(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):

    users = db.query(User).all()

    return [
        {
           "employee_id": u.employee_id,
            "name": u.name,
            "role": u.role,
            "face_enrolled": u.face_enrolled,
            "face_updated_at": u.face_updated_at

        }
        for u in users
    ]


# ====================================
# CREATE EMPLOYEE
# ====================================
@router.post("/")
def create_user(
    payload: dict,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):

    employee_id = payload.get("employee_id")
    name = payload.get("name")
    password = payload.get("password")
    role = payload.get("role", "employee")

    if not employee_id or not password or not name:
        raise HTTPException(
            status_code=400,
            detail="employee_id, name and password required"
        )

    existing = db.query(User).filter(User.employee_id == employee_id).first()

    if existing:
        raise HTTPException(status_code=400, detail="Employee already exists")

    user = User(
        employee_id=employee_id,
        name=name,
        password_hash=pwd_context.hash(password),
        role=role
    )

    db.add(user)
    db.commit()

    return {"message": "User created"}


# ====================================
# DELETE EMPLOYEE
# ====================================
@router.delete("/{employee_id}")
def delete_user(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):

    user = db.query(User).filter(User.employee_id == employee_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return {"message": "User deleted"}


# ====================================
# RESET PASSWORD
# ====================================
@router.put("/{employee_id}/reset-password")
def reset_password(
    employee_id: str,
    payload: dict,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):

    new_password = payload.get("password")

    user = db.query(User).filter(User.employee_id == employee_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password_hash = pwd_context.hash(new_password)

    db.commit()

    return {"message": "Password updated"}