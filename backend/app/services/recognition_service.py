import base64

import cv2
import numpy as np
from sqlalchemy.orm import Session

from app.models.user import User
from app.services.ai_client import generate_embedding
from app.services.spoof_service import spoof_check_single_frame
from app.services.recognition_cache_service import get_cached_embeddings


# =====================================================
# IMAGE DECODING
# =====================================================

def decode_base64_image(image_base64: str):
    """
    Decode a Base64-encoded image into an OpenCV BGR image.
    """

    try:
        if "," in image_base64:
            image_base64 = image_base64.split(",", 1)[1]

        image_bytes = base64.b64decode(image_base64)

        np_array = np.frombuffer(
            image_bytes,
            dtype=np.uint8,
        )

        image = cv2.imdecode(
            np_array,
            cv2.IMREAD_COLOR,
        )

        return image

    except Exception:
        return None


# =====================================================
# COSINE SIMILARITY
# =====================================================

def cosine_similarity_matrix(
    input_embedding,
    stored_embeddings,
):
    """
    Calculate cosine similarity between one input
    embedding and all stored embeddings.
    """

    input_embedding = input_embedding / np.linalg.norm(
        input_embedding
    )

    stored_embeddings = stored_embeddings / np.linalg.norm(
        stored_embeddings,
        axis=1,
        keepdims=True,
    )

    return np.dot(
        stored_embeddings,
        input_embedding,
    )


# =====================================================
# MAIN RECOGNITION FUNCTION
# =====================================================

def recognize_user(
    db: Session,
    image_base64: str,
):

    # -------------------------------------------------
    # Decode image
    # -------------------------------------------------

    img = decode_base64_image(image_base64)

    if img is None:
        return {
            "matched": False,
            "reason": "Invalid image",
            "user_id": None,
            "employee_id": None,
            "name": None,
            "confidence": 0.0,
        }

    # -------------------------------------------------
    # SPOOF / LIVENESS CHECK
    # -------------------------------------------------

    is_live, reason = spoof_check_single_frame(img)

    if not is_live:
        return {
            "matched": False,
            "reason": reason,
            "user_id": None,
            "employee_id": None,
            "name": None,
            "confidence": 0.0,
        }

    # -------------------------------------------------
    # GENERATE FACE EMBEDDING
    #
    # IMPORTANT:
    # The backend no longer runs InsightFace directly.
    # The AI service generates the embedding using
    # InsightFace buffalo_s.
    # -------------------------------------------------

    input_embedding = generate_embedding(image_base64)

    if input_embedding is None:
        return {
            "matched": False,
            "reason": "Face could not be detected or AI service failed",
            "user_id": None,
            "employee_id": None,
            "name": None,
            "confidence": 0.0,
        }

    try:
        input_embedding = np.asarray(
            input_embedding,
            dtype=np.float32,
        )

    except Exception:
        return {
            "matched": False,
            "reason": "Invalid embedding returned by AI service",
            "user_id": None,
            "employee_id": None,
            "name": None,
            "confidence": 0.0,
        }

    # -------------------------------------------------
    # VALIDATE EMBEDDING DIMENSION
    # -------------------------------------------------

    if input_embedding.size != 512:
        return {
            "matched": False,
            "reason": "Invalid face embedding dimension",
            "user_id": None,
            "employee_id": None,
            "name": None,
            "confidence": 0.0,
        }

    # -------------------------------------------------
    # LOAD EMBEDDINGS FROM REDIS CACHE
    # -------------------------------------------------

    stored_embeddings, user_ids = get_cached_embeddings()

    if stored_embeddings is None or user_ids is None:
        return {
            "matched": False,
            "reason": "Embedding cache not initialized",
            "user_id": None,
            "employee_id": None,
            "name": None,
            "confidence": 0.0,
        }

    # -------------------------------------------------
    # VECTORIZED MATCHING
    # -------------------------------------------------

    similarities = cosine_similarity_matrix(
        input_embedding,
        stored_embeddings,
    )

    best_index = int(
        np.argmax(similarities)
    )

    best_score = float(
        similarities[best_index]
    )

    # -------------------------------------------------
    # MATCHING THRESHOLD
    # -------------------------------------------------

    THRESHOLD = 0.6

    if best_score < THRESHOLD:
        return {
            "matched": False,
            "reason": "No match found",
            "user_id": None,
            "employee_id": None,
            "name": None,
            "confidence": best_score,
        }

    # -------------------------------------------------
    # FETCH USER DETAILS
    # -------------------------------------------------

    user = (
        db.query(User)
        .filter(
            User.id == user_ids[best_index]
        )
        .first()
    )

    if not user:
        return {
            "matched": False,
            "reason": "User record missing",
            "user_id": None,
            "employee_id": None,
            "name": None,
            "confidence": best_score,
        }

    # -------------------------------------------------
    # SUCCESS
    # -------------------------------------------------

    return {
        "matched": True,
        "reason": "Face matched successfully",
        "user_id": str(user.id),
        "employee_id": user.employee_id,
        "name": user.name,
        "confidence": best_score,
    }