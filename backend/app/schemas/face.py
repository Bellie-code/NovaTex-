from pydantic import BaseModel


class FaceEnrollRequest(BaseModel):
    image_base64: str


class FaceEnrollResponse(BaseModel):
    message: str
    embedding_dim: int
