from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func,Time
from datetime import time

from app.database import get_db
from app.models.attendance import Attendance, AttendanceStatus
from app.models.user import User
from app.core.dependencies import require_role


router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


# =====================================================
# 1️⃣ DAILY ATTENDANCE COUNT
# =====================================================

@router.get("/daily")
def daily_attendance(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):

    results = (
        db.query(
            func.date(Attendance.timestamp).label("day"),
            func.count().label("count")
        )
        .filter(Attendance.status == AttendanceStatus.SUCCESS)
        .group_by(func.date(Attendance.timestamp))
        .order_by(func.date(Attendance.timestamp))
        .all()
    )

    return [
        {"date": str(r.day), "count": r.count}
        for r in results
    ]


# =====================================================
# 2️⃣ REAL vs SPOOF ATTEMPTS
# =====================================================

@router.get("/spoof-summary")
def spoof_summary(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):

    results = (
        db.query(
            Attendance.spoof_status,
            func.count().label("count")
        )
        .group_by(Attendance.spoof_status)
        .all()
    )

    return {
        str(r.spoof_status): r.count
        for r in results
    }


# =====================================================
# 3️⃣ SUCCESS RATE %
# =====================================================

@router.get("/success-rate")
def success_rate(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):

    total_attempts = db.query(func.count(Attendance.id)).scalar()

    success_count = (
        db.query(func.count(Attendance.id))
        .filter(Attendance.status == AttendanceStatus.SUCCESS)
        .scalar()
    )

    if total_attempts == 0:
        return {"success_rate_percent": 0}

    rate = (success_count / total_attempts) * 100

    return {
        "total_attempts": total_attempts,
        "success_count": success_count,
        "success_rate_percent": round(rate, 2)
    }


# =====================================================
# 4️⃣ EMPLOYEE ATTENDANCE HISTORY
# =====================================================

@router.get("/employee/{employee_id}")
def employee_history(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):

    user = db.query(User).filter(
        User.employee_id == employee_id
    ).first()

    if not user:
        return {"error": "User not found"}

    records = (
        db.query(Attendance)
        .filter(Attendance.user_id == user.id)
        .order_by(Attendance.timestamp.desc())
        .all()
    )

    return [
        {
            "timestamp": r.timestamp,
            "status": r.status,
            "spoof_status": r.spoof_status,
            "confidence": r.confidence,
            "device": r.device
        }
        for r in records
    ]


# =====================================================
# 5️⃣ LATE DETECTION LOGIC
# =====================================================

@router.get("/late-report")
def late_report(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):
    """
    Employee is late if first attendance of the day
    is after 9:30 AM
    """

    LATE_TIME = time(9, 30)

    # Step 1: get first attendance per user per day
    subquery = (
        db.query(
            Attendance.user_id,
            func.date(Attendance.timestamp).label("day"),
            func.min(Attendance.timestamp).label("first_entry")
        )
        .filter(Attendance.status == AttendanceStatus.SUCCESS)
        .group_by(
            Attendance.user_id,
            func.date(Attendance.timestamp)
        )
        .subquery()
    )

    # Step 2: filter late arrivals
    results = (
        db.query(
            subquery.c.user_id,
            subquery.c.day,
            subquery.c.first_entry
        )
        .filter(subquery.c.first_entry.cast(Time) > LATE_TIME)        
        .all()
    )

    return [
        {
            "user_id": str(r.user_id),
            "date": str(r.day),
            "first_entry": r.first_entry
        }
        for r in results
    ]

