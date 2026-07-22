from pydantic import BaseModel
from typing import Optional, Dict

class SpoofResult(BaseModel):
    is_live: bool
    score: float
    reason: str
    details: Optional[Dict] = None
