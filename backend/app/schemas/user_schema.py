from pydantic import BaseModel

class UserRegisterSchema(BaseModel):
    employee_id: str
    name: str
    password: str
    image_base64: str
