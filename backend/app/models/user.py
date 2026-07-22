import uuid
from sqlalchemy import Column, String, LargeBinary, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database import Base
from sqlalchemy import Boolean


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    employee_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)

    password_hash = Column(String, nullable=False)

    role = Column(String, default="employee")  # employee / admin

    embedding = Column(LargeBinary, nullable=True)  # face embedding bytes
    
    face_enrolled = Column(Boolean, default=False)

    face_updated_at = Column(DateTime(timezone=True), nullable=True)
    
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
