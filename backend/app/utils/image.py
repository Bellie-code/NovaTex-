import base64
import cv2
import numpy as np


def decode_base64_image(image_base64: str):
    """
    Decode a Base64-encoded image into an OpenCV BGR image.
    This utility performs image decoding only.
    It does NOT load any face-recognition model.
    """

    try:
        if "," in image_base64:
            image_base64 = image_base64.split(",", 1)[1]

        decoded = base64.b64decode(image_base64)
        np_arr = np.frombuffer(decoded, np.uint8)

        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        return image

    except Exception:
        return None