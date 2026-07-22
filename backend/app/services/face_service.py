import base64
import numpy as np
import cv2
from insightface.app import FaceAnalysis

face_app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
face_app.prepare(ctx_id=0, det_size=(640, 640))


def decode_base64_image(image_base64: str):
    if "," in image_base64:
        image_base64 = image_base64.split(",")[1]

    img_bytes = base64.b64decode(image_base64)
    np_arr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    return img


def extract_embedding(img):
    if img is None:
        return None

    faces = face_app.get(img)

    if not faces:
        return None

    return faces[0].embedding
