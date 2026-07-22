from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.analytics_service import get_dashboard_stats, get_attendance_logs

router = APIRouter(prefix="/api/admin", tags=["Admin Analytics"])


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    return get_dashboard_stats(db)


@router.get("/attendance-logs")
def attendance_logs(db: Session = Depends(get_db)):
    logs = get_attendance_logs(db)

    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "timestamp": log.timestamp,
            "status": log.status,
            "spoof_status": log.spoof_status,
            "confidence": log.confidence,
            "device": log.device
        }
        for log in logs
    ]
