from pydantic import BaseModel
from datetime import datetime


class AttendanceMarkRequest(BaseModel):
    image_base64: str
    device: str = "WEB_CAM"

class AttendanceMarkResponse(BaseModel):
    success: bool
    message: str
    employee_id: str
    name: str
    timestamp: datetime
