import numpy as np
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, date

from app.database import get_db
from app.models.attendance import (
    Attendance,
    AttendanceStatus,
    SpoofStatus
)

from app.services.ai_client import generate_embedding
from app.services.spoof_service import spoof_check_single_frame
from app.services.face_service import decode_base64_image
from app.services.recognition_cache_service import get_cached_embeddings

from app.schemas.attendance import AttendanceMarkRequest
from app.core.dependencies import require_role
from app.routers.auth import get_current_user
from fastapi import Query
from app.models.user import User

router = APIRouter(prefix="/api/attendance", tags=["Attendance"])


# =====================================================
# VECTOR MATCHING
# =====================================================

def match_embedding(input_embedding, stored_embeddings, threshold=0.6):

    input_embedding = input_embedding / np.linalg.norm(input_embedding)

    stored_embeddings = stored_embeddings / np.linalg.norm(
        stored_embeddings,
        axis=1,
        keepdims=True
    )

    similarities = np.dot(stored_embeddings, input_embedding)

    best_index = int(np.argmax(similarities))
    best_score = float(similarities[best_index])

    if best_score >= threshold:
        return best_index, best_score

    return None, best_score


# =====================================================
# MARK ATTENDANCE
# =====================================================

@router.post("/mark")
def mark_attendance(
    payload: AttendanceMarkRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

   

    # Allow only admin or employee
    if current_user.role not in ["admin", "employee"]:
        raise HTTPException(
            status_code=403,
            detail="Access denied"
    )

    image_base64 = payload.image_base64
    device = payload.device

    # -----------------------------------------------
    # STEP 1: Decode Image
    # -----------------------------------------------

    img = decode_base64_image(image_base64)

    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image")

    # -----------------------------------------------
    # STEP 2: Spoof Detection
    # -----------------------------------------------

    is_live, reason = spoof_check_single_frame(img)

    if not is_live:

        attendance = Attendance(
            user_id=None,
            status=AttendanceStatus.REJECTED,
            spoof_status=SpoofStatus.SPOOF,
            confidence=0.0,
            device=device
        )

        db.add(attendance)
        db.commit()

        return {
            "status": "REJECTED",
            "reason": reason,
            "spoof_status": "SPOOF"
        }

    # -----------------------------------------------
    # STEP 3: Generate Embedding
    # -----------------------------------------------

    embedding_list = generate_embedding(image_base64)

    if embedding_list is None:
        raise HTTPException(status_code=400, detail="Face not detected")

    input_embedding = np.array(embedding_list, dtype=np.float32)

    # -----------------------------------------------
    # STEP 4: Load Cached Embeddings
    # -----------------------------------------------

    stored_embeddings, user_ids = get_cached_embeddings()

    if stored_embeddings is None:
        raise HTTPException(
            status_code=500,
            detail="Embedding cache not initialized"
        )

    # -----------------------------------------------
    # STEP 5: Match Face
    # -----------------------------------------------

    match_index, confidence = match_embedding(
        input_embedding,
        stored_embeddings
    )

    if match_index is None:

        attendance = Attendance(
            user_id=None,
            status=AttendanceStatus.REJECTED,
            spoof_status=SpoofStatus.REAL,
            confidence=confidence,
            device=device
        )

        db.add(attendance)
        db.commit()

        return {
            "status": "REJECTED",
            "reason": "Face not recognized",
            "confidence": confidence
        }

    matched_user_id = user_ids[match_index]

    # -----------------------------------------------
    # STEP 6: Prevent Duplicate Attendance
    # -----------------------------------------------

    today_start = datetime.combine(date.today(), datetime.min.time())
    today_end = datetime.combine(date.today(), datetime.max.time())

    existing = db.query(Attendance).filter(
        Attendance.user_id == matched_user_id,
        Attendance.timestamp >= today_start,
        Attendance.timestamp <= today_end,
        Attendance.status == AttendanceStatus.SUCCESS
    ).first()

    if existing:

        return {
            "status": "ALREADY_MARKED",
            "confidence": confidence
        }

    # -----------------------------------------------
    # STEP 7: Save SUCCESS
    # -----------------------------------------------

    attendance = Attendance(
        user_id=matched_user_id,
        status=AttendanceStatus.SUCCESS,
        spoof_status=SpoofStatus.REAL,
        confidence=confidence,
        device=device
    )

    db.add(attendance)
    db.commit()

    return {
        "status": "SUCCESS",
        "user_id": matched_user_id,
        "confidence": confidence
    }


# =====================================================
# ADMIN VIEW RECORDS
# =====================================================



@router.get("/records")
def view_attendance(
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    employee_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):

    query = (
        db.query(
            Attendance,
            User.employee_id,
            User.name
        )
        .outerjoin(User, Attendance.user_id == User.id)
    )

    # -----------------------------
    # Date Filter
    # -----------------------------
    if start_date:
        query = query.filter(
            Attendance.timestamp >= start_date
        )

    if end_date:
        query = query.filter(
            Attendance.timestamp <= end_date
        )

    # -----------------------------
    # Employee Filter
    # -----------------------------
    if employee_id:
        query = query.filter(
            User.employee_id.ilike(f"%{employee_id}%")
        )

    # -----------------------------
    # Latest First
    # -----------------------------
    records = query.order_by(
        Attendance.timestamp.desc()
    ).all()

    return [

        {
            "id": str(attendance.id),

            "employee_id": emp_id,

            "name": name,

            "timestamp": attendance.timestamp,

            "status": attendance.status.value,

            "spoof_status": attendance.spoof_status.value,

            "confidence": round(
                attendance.confidence,
                3
            ),

            "device": attendance.device

        }

        for attendance, emp_id, name in records

    ]