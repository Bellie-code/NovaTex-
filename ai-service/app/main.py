from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import base64
import cv2

from insightface.app import FaceAnalysis

app = FastAPI(title="AI Face Service")

face_app = FaceAnalysis(name="buffalo_s")
face_app.prepare(ctx_id=1, det_size=(640, 640))


class EmbedRequest(BaseModel):
    image_base64: str


def decode_base64_image(image_base64: str):
    try:
        if "," in image_base64:
            image_base64 = image_base64.split(",")[1]

        decoded = base64.b64decode(image_base64)
        np_arr = np.frombuffer(decoded, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        return img
    except Exception:
        return None


@app.get("/")
def root():
    return {"message": "AI Service Running"}


@app.post("/embed")
def generate_embedding(payload: EmbedRequest):
    frame = decode_base64_image(payload.image_base64)

    if frame is None:
        raise HTTPException(status_code=400, detail="Invalid image")

    faces = face_app.get(frame)

    if len(faces) == 0:
        raise HTTPException(status_code=400, detail="No face detected")

    embedding = faces[0].embedding
    embedding = np.array(embedding, dtype=np.float32)

    return {"embedding": embedding.tolist()}
