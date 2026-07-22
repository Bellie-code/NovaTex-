from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.attendance import Attendance
from app.services.recognition_service import recognize_user


DUPLICATE_WINDOW_MINUTES = 2


def can_mark_attendance(db: Session, user_id):
    window_start = datetime.utcnow() - timedelta(minutes=DUPLICATE_WINDOW_MINUTES)

    existing = (
        db.query(Attendance)
        .filter(Attendance.user_id == user_id)
        .filter(Attendance.timestamp >= window_start)
        .first()
    )

    return existing is None


def mark_attendance(db: Session, image_base64: str):
    result = recognize_user(db, image_base64)

    if not result["matched"]:
        raise ValueError("Face not recognized")

    user_id = result["user_id"]

    if not can_mark_attendance(db, user_id):
        raise ValueError("Duplicate attendance detected (wait 2 minutes)")

    attendance = Attendance(user_id=user_id)
    db.add(attendance)
    db.commit()
    db.refresh(attendance)

    return {
        "employee_id": result["employee_id"],
        "name": result["name"],
        "timestamp": attendance.timestamp,
    }
