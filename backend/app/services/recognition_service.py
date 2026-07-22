import numpy as np
from sqlalchemy.orm import Session

from app.models.user import User
from app.services.face_service import decode_base64_image, face_app
from app.services.spoof_service import spoof_check_single_frame
from app.services.recognition_cache_service import get_cached_embeddings


# =====================================================
# COSINE SIMILARITY (VECTORIZED)
# =====================================================

def cosine_similarity_matrix(input_embedding, stored_embeddings):
    input_embedding = input_embedding / np.linalg.norm(input_embedding)
    stored_embeddings = stored_embeddings / np.linalg.norm(
        stored_embeddings, axis=1, keepdims=True
    )

    return np.dot(stored_embeddings, input_embedding)


# =====================================================
# MAIN RECOGNITION FUNCTION
# =====================================================

def recognize_user(db: Session, image_base64: str):

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
    # SPOOF CHECK
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
    # FACE DETECTION + EMBEDDING
    # -------------------------------------------------

    faces = face_app.get(img)

    if not faces:
        return {
            "matched": False,
            "reason": "No face detected",
            "user_id": None,
            "employee_id": None,
            "name": None,
            "confidence": 0.0,
        }

    input_embedding = faces[0].embedding.astype(np.float32)

    # -------------------------------------------------
    # LOAD EMBEDDINGS FROM REDIS CACHE
    # -------------------------------------------------

    stored_embeddings, user_ids = get_cached_embeddings()

    if stored_embeddings is None:
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
        stored_embeddings
    )

    best_index = int(np.argmax(similarities))
    best_score = float(similarities[best_index])

    # Configurable threshold
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

    user = db.query(User).filter(
        User.id == user_ids[best_index]
    ).first()

    if not user:
        return {
            "matched": False,
            "reason": "User record missing",
            "user_id": None,
            "employee_id": None,
            "name": None,
            "confidence": best_score,
        }

    return {
        "matched": True,
        "reason": "Face matched successfully",
        "user_id": str(user.id),
        "employee_id": user.employee_id,
        "name": user.name,
        "confidence": best_score,
    }