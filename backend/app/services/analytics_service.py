from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from datetime import datetime, timedelta

from app.models.user import User
from app.models.attendance import AttendanceLog


def get_dashboard_stats(db: Session):
    today = datetime.utcnow().date()
    week_start = today - timedelta(days=6)
    six_months_ago = today - timedelta(days=180)

    total_users = db.query(User).count()

    today_attendance = db.query(AttendanceLog).filter(
        cast(AttendanceLog.timestamp, Date) == today,
        AttendanceLog.status == "SUCCESS"
    ).count()

    spoof_attempts_today = db.query(AttendanceLog).filter(
        cast(AttendanceLog.timestamp, Date) == today,
        AttendanceLog.spoof_status == "SPOOF"
    ).count()

    rejected_attendance_today = db.query(AttendanceLog).filter(
        cast(AttendanceLog.timestamp, Date) == today,
        AttendanceLog.status == "REJECTED"
    ).count()

    weekly_data = db.query(
        cast(AttendanceLog.timestamp, Date).label("date"),
        func.count(AttendanceLog.id).label("count")
    ).filter(
        cast(AttendanceLog.timestamp, Date) >= week_start,
        AttendanceLog.status == "SUCCESS"
    ).group_by("date").order_by("date").all()

    weekly_stats = [{"date": str(row.date), "count": row.count} for row in weekly_data]

    monthly_data = db.query(
        func.to_char(AttendanceLog.timestamp, "YYYY-MM").label("month"),
        func.count(AttendanceLog.id).label("count")
    ).filter(
        AttendanceLog.timestamp >= six_months_ago,
        AttendanceLog.status == "SUCCESS"
    ).group_by("month").order_by("month").all()

    monthly_stats = [{"month": row.month, "count": row.count} for row in monthly_data]

    return {
        "total_users": total_users,
        "today_attendance": today_attendance,
        "spoof_attempts_today": spoof_attempts_today,
        "rejected_attendance_today": rejected_attendance_today,
        "weekly_stats": weekly_stats,
        "monthly_stats": monthly_stats
    }


def get_attendance_logs(db: Session, limit: int = 200):
    logs = db.query(AttendanceLog).order_by(AttendanceLog.timestamp.desc()).limit(limit).all()
    return logs
