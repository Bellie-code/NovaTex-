from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.attendance import AttendanceMarkRequest, AttendanceMarkResponse
from app.services.attendance_service import mark_attendance
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/attendance", tags=["Attendance"])


@router.post("/mark", response_model=AttendanceMarkResponse)
def mark_attendance_api(
    payload: AttendanceMarkRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        result = mark_attendance(db, payload.image_base64)

        return AttendanceMarkResponse(
            success=True,
            message="Attendance marked successfully",
            employee_id=result["employee_id"],
            name=result["name"],
            timestamp=result["timestamp"],
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
