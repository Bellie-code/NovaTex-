from pydantic import BaseModel
from typing import List

class DailyAttendanceStats(BaseModel):
    date: str
    count: int

class MonthlyAttendanceStats(BaseModel):
    month: str
    count: int

class DashboardStats(BaseModel):
    total_users: int
    today_attendance: int
    spoof_attempts_today: int
    rejected_attendance_today: int
    weekly_stats: List[DailyAttendanceStats]
    monthly_stats: List[MonthlyAttendanceStats]
