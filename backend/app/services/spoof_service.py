import cv2
import numpy as np
import mediapipe as mp


# =====================================================
# INITIALIZE MEDIAPIPE FACE MESH
# =====================================================

mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
    static_image_mode=True,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5
)


# =====================================================
# EYE ASPECT RATIO (EAR)
# =====================================================

def eye_aspect_ratio(eye_points):

    A = np.linalg.norm(eye_points[1] - eye_points[5])
    B = np.linalg.norm(eye_points[2] - eye_points[4])
    C = np.linalg.norm(eye_points[0] - eye_points[3])

    if C == 0:
        return 0.0

    return (A + B) / (2.0 * C)


def detect_eye_openness(landmarks, img_w, img_h):

    LEFT_EYE = [33, 160, 158, 133, 153, 144]
    RIGHT_EYE = [362, 385, 387, 263, 373, 380]

    left_eye = np.array(
        [(landmarks[i].x * img_w, landmarks[i].y * img_h) for i in LEFT_EYE],
        dtype=np.float32
    )

    right_eye = np.array(
        [(landmarks[i].x * img_w, landmarks[i].y * img_h) for i in RIGHT_EYE],
        dtype=np.float32
    )

    left_ear = eye_aspect_ratio(left_eye)
    right_ear = eye_aspect_ratio(right_eye)

    avg_ear = (left_ear + right_ear) / 2.0

    return avg_ear


# =====================================================
# MAIN SPOOF CHECK
# =====================================================

def spoof_check_single_frame(img):
    """
    Basic spoof check.

    Since the system already uses challenge-response
    (blink / turn_left / turn_right / nod),
    we only verify that:

    1. A face exists
    2. Eyes are open

    Challenge verification will confirm liveness.
    """

    if img is None:
        return False, "Invalid image"

    img_h, img_w, _ = img.shape

    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    results = mp_face_mesh.process(rgb)

    # -------------------------------------------------
    # Face Detection
    # -------------------------------------------------

    if not results.multi_face_landmarks:
        return False, "No face detected"

    face_landmarks = results.multi_face_landmarks[0].landmark

    # -------------------------------------------------
    # Eye openness check
    # -------------------------------------------------

    ear_value = detect_eye_openness(face_landmarks, img_w, img_h)

    # Relaxed threshold to avoid false negatives
    if ear_value < 0.08:
        return False, "Eyes closed"

    # -------------------------------------------------
    # Passed basic checks
    # -------------------------------------------------

    return True, "Live face detected"