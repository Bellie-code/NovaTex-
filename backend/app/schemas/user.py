from pydantic import BaseModel
from uuid import UUID


class UserResponse(BaseModel):
    id: UUID
    employee_id: str
    name: str
    role: str

    class Config:
        from_attributes = True
