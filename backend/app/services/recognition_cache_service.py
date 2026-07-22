import redis
import numpy as np
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User


# Create Redis client
redis_client = redis.Redis.from_url(
    settings.REDIS_URL,
    decode_responses=False
)


# =====================================================
# LOAD EMBEDDINGS INTO REDIS CACHE
# =====================================================

def load_embeddings_to_cache(db: Session):

    users = db.query(User).all()

    embeddings = []
    user_ids = []

    for user in users:

        # Skip users without enrolled faces
        if user.embedding is None:
            print(f"Skipping {user.employee_id} (no face enrolled)")
            continue

        try:
            emb = np.frombuffer(user.embedding, dtype=np.float32)

            # Validate embedding length
            if emb.size != 512:
                print(f"Skipping {user.employee_id} (invalid embedding)")
                continue

            embeddings.append(emb)
            user_ids.append(str(user.id))

        except Exception as e:
            print(f"Skipping {user.employee_id}: {e}")

    if len(embeddings) == 0:
        print("⚠ No enrolled face embeddings found.")
        redis_client.delete("face_embeddings")
        redis_client.delete("face_user_ids")
        return

    embeddings = np.vstack(embeddings)

    redis_client.set(
        "face_embeddings",
        embeddings.astype(np.float32).tobytes()
    )

    redis_client.set(
        "face_user_ids",
        ",".join(user_ids)
    )

    print(f"✅ Cached {len(user_ids)} face embeddings.")

# =====================================================
# GET EMBEDDINGS FROM CACHE
# =====================================================

def get_cached_embeddings():
    embeddings_bytes = redis_client.get("face_embeddings")
    user_ids_bytes = redis_client.get("face_user_ids")

    if not embeddings_bytes or not user_ids_bytes:
        return None, None

    embeddings = np.frombuffer(embeddings_bytes, dtype=np.float32)
    embeddings = embeddings.reshape(-1, 512)

    user_ids = user_ids_bytes.decode().split(",")

    return embeddings, user_ids