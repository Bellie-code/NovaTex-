import base64
import uuid
import numpy as np
import cv2
from fastapi import APIRouter, HTTPException
from app.ai.spoof_detection import SpoofDetector
from app.utils.redis_client import redis_client


router = APIRouter(prefix="/api/spoof", tags=["Spoof Detection"])
detector = SpoofDetector()


def decode_base64_image(image_base64: str):
    """
    Accepts both:
    - pure base64 string
    - data:image/jpeg;base64,...
    """

    if not image_base64:
        return None

    if "," in image_base64:
        image_base64 = image_base64.split(",")[1]

    try:
        decoded = base64.b64decode(image_base64)
        np_arr = np.frombuffer(decoded, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        return img
    except Exception:
        return None


# ----------------------------
# 1) Single frame spoof check
# ----------------------------
@router.post("/check")
def check_spoof(payload: dict):
    """
    payload = { "image": "<base64>" }
    """

    if "image" not in payload:
        raise HTTPException(status_code=400, detail="Image is required")

    frame = decode_base64_image(payload["image"])

    if frame is None:
        raise HTTPException(status_code=400, detail="Invalid image")

    result = detector.detect(frame)

    return result


# ----------------------------
# 2) Challenge generation
# ----------------------------
@router.get("/challenge")
def get_challenge():
    """
    Generates random liveness challenge
    Stored in Redis for 60 seconds
    """

    challenges = ["blink_twice", "turn_left", "turn_right"]

    challenge = np.random.choice(challenges)

    challenge_id = str(uuid.uuid4())

    expires = 60

    redis_client.setex(
        f"challenge:{challenge_id}",
        expires,
        challenge
    )

    return {
        "challenge_id": challenge_id,
        "challenge": challenge,
        "expires_in": expires
    }


# ----------------------------
# 3) Challenge verification
# ----------------------------
@router.post("/verify")
def verify_challenge(payload: dict):
    """
    payload =
    {
        "challenge_id": "...",
        "frames": ["base64img1", "base64img2", ...]
    }
    """

    if "challenge_id" not in payload or not payload["challenge_id"]:
        raise HTTPException(status_code=400, detail="challenge_id missing")

    if "frames" not in payload or not isinstance(payload["frames"], list):
        raise HTTPException(status_code=400, detail="frames missing")

    challenge_id = payload["challenge_id"]
    frames_b64 = payload["frames"]

    challenge = redis_client.get(f"challenge:{challenge_id}")

    if not challenge:
        raise HTTPException(status_code=400, detail="Challenge expired or invalid")

    # Handle Redis bytes
    if isinstance(challenge, bytes):
        challenge = challenge.decode("utf-8")

    # Reduce minimum frame requirement
    if len(frames_b64) < 3:
        raise HTTPException(
            status_code=400,
            detail="Not enough frames sent (minimum 3 required)"
        )

    decoded_frames = []

    for b64 in frames_b64:
        frame = decode_base64_image(b64)
        if frame is not None:
            decoded_frames.append(frame)

    if len(decoded_frames) < 3:
        raise HTTPException(status_code=400, detail="Frames decoding failed")

    # -------------------------------------------------
    # Main challenge detection
    # -------------------------------------------------

    try:

        result = detector.detect_sequence(decoded_frames, challenge)

    except Exception:

        result = {
            "success": False,
            "reason": "Sequence detection failed"
        }

    # -------------------------------------------------
    # Fallback: if detection fails but face exists
    # -------------------------------------------------

    if not result.get("success"):

        try:

            fallback = detector.detect(decoded_frames[-1])

            if fallback.get("is_live"):

                result = {
                    "success": True,
                    "reason": "Fallback liveness verification passed"
                }

        except Exception:
            pass

    # Delete challenge after verification
    redis_client.delete(f"challenge:{challenge_id}")

    return result