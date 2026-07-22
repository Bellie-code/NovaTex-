from pydantic import BaseModel

class LoginSchema(BaseModel):
    employee_id: str
    password: str
