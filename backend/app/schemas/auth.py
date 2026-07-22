from pydantic import BaseModel


class RegisterRequest(BaseModel):
    employee_id: str
    name: str
    password: str





class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
