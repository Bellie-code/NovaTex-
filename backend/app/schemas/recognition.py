from pydantic import BaseModel
from typing import Optional


class RecognizeRequest(BaseModel):
    image_base64: str


class RecognizeResponse(BaseModel):
    matched: bool
    user_id: Optional[str] = None
    employee_id: Optional[str] = None
    name: Optional[str] = None
    confidence: float
