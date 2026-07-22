import uuid
from sqlalchemy import (
    Column,
    String,
    Float,
    DateTime,
    ForeignKey,
    Enum,
    Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base
import enum


# =====================================================
# ENUMS (Production Safe)
# =====================================================

class AttendanceStatus(str, enum.Enum):
    SUCCESS = "SUCCESS"
    REJECTED = "REJECTED"


class SpoofStatus(str, enum.Enum):
    REAL = "REAL"
    SPOOF = "SPOOF"
    UNKNOWN = "UNKNOWN"


class AttendanceType(str, enum.Enum):
    CHECK_IN = "CHECK_IN"
    CHECK_OUT = "CHECK_OUT"


# =====================================================
# ATTENDANCE MODEL
# =====================================================

class Attendance(Base):
    __tablename__ = "attendance_logs"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True   # Nullable only for REJECTED cases
    )

    timestamp = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True
    )

    status = Column(
        Enum(AttendanceStatus),
        default=AttendanceStatus.SUCCESS,
        nullable=False
    )

    spoof_status = Column(
        Enum(SpoofStatus),
        default=SpoofStatus.UNKNOWN,
        nullable=False
    )

    attendance_type = Column(
        Enum(AttendanceType),
        default=AttendanceType.CHECK_IN,
        nullable=False
    )

    confidence = Column(
        Float,
        default=0.0,
        nullable=False
    )

    device = Column(
        String,
        default="WEB_CAM",
        nullable=False
    )

    # =================================================
    # INDEXES FOR PERFORMANCE
    # =================================================

    __table_args__ = (
        Index("idx_user_timestamp", "user_id", "timestamp"),
    )