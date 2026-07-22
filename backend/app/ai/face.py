import cv2
import numpy as np
import face_recognition


def get_face_embedding(image_bgr):
    """
    Takes OpenCV BGR image
    Returns 128D face embedding list
    """

    rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb)

    if len(face_locations) == 0:
        return None

    encodings = face_recognition.face_encodings(rgb, face_locations)

    if len(encodings) == 0:
        return None

    return encodings[0].tolist()
