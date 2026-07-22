import cv2
import numpy as np
import mediapipe as mp


class SpoofDetector:

    def __init__(self):

        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

        # ----------------------------
        # Blink thresholds
        # ----------------------------

        self.EAR_THRESHOLD = 0.18
        self.EAR_CONSEC_FRAMES = 2

        # ----------------------------
        # Spoof thresholds (RELAXED)
        # ----------------------------

        self.LAPLACIAN_THRESHOLD = 25.0
        self.FFT_ENERGY_THRESHOLD = 0.35
        self.EDGE_DENSITY_THRESHOLD = 0.35
        self.UNIFORMITY_THRESHOLD = 8.0


    # ---------------------------------
    # Eye aspect ratio
    # ---------------------------------

    def _eye_aspect_ratio(self, eye_points):

        A = np.linalg.norm(np.array(eye_points[1]) - np.array(eye_points[5]))
        B = np.linalg.norm(np.array(eye_points[2]) - np.array(eye_points[4]))
        C = np.linalg.norm(np.array(eye_points[0]) - np.array(eye_points[3]))

        if C == 0:
            return 0.0

        return (A + B) / (2.0 * C)


    # ---------------------------------
    # Texture score
    # ---------------------------------

    def _calculate_texture_score(self, face_gray):

        lap = cv2.Laplacian(face_gray, cv2.CV_64F)
        return float(lap.var())


    # ---------------------------------
    # FFT screen detection
    # ---------------------------------

    def _fft_screen_energy(self, face_gray):

        f = np.fft.fft2(face_gray)
        fshift = np.fft.fftshift(f)

        magnitude = np.log(np.abs(fshift) + 1)

        h, w = magnitude.shape
        center_h, center_w = h // 2, w // 2

        mask = np.ones((h, w), np.uint8)

        r = 20
        mask[center_h - r:center_h + r, center_w - r:center_w + r] = 0

        high_freq = magnitude * mask

        energy = np.mean(high_freq) / (np.mean(magnitude) + 1e-6)

        return float(energy)


    # ---------------------------------
    # Edge density
    # ---------------------------------

    def _edge_density(self, face_gray):

        edges = cv2.Canny(face_gray, 80, 160)

        density = np.sum(edges > 0) / edges.size

        return float(density)


    # ---------------------------------
    # Brightness variation
    # ---------------------------------

    def _brightness_uniformity(self, face_gray):

        return float(np.std(face_gray))


    # ---------------------------------
    # Extract face ROI
    # ---------------------------------

    def _extract_face_roi(self, frame, landmarks):

        h, w, _ = frame.shape

        xs = [int(lm.x * w) for lm in landmarks]
        ys = [int(lm.y * h) for lm in landmarks]

        x1 = max(min(xs) - 20, 0)
        x2 = min(max(xs) + 20, w)

        y1 = max(min(ys) - 20, 0)
        y2 = min(max(ys) + 20, h)

        roi = frame[y1:y2, x1:x2]

        return roi


    # ---------------------------------
    # Single frame spoof detection
    # ---------------------------------

    def detect(self, frame):

        h, w, _ = frame.shape

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = self.face_mesh.process(frame_rgb)

        if not results.multi_face_landmarks:

            return {
                "is_live": False,
                "score": 0.0,
                "reason": "No face detected",
                "details": {}
            }

        landmarks = results.multi_face_landmarks[0].landmark

        face_roi = self._extract_face_roi(frame, landmarks)

        if face_roi.size == 0:

            return {
                "is_live": False,
                "score": 0.0,
                "reason": "Face ROI empty",
                "details": {}
            }

        face_gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)

        texture_score = self._calculate_texture_score(face_gray)

        fft_energy = self._fft_screen_energy(face_gray)

        edge_density = self._edge_density(face_gray)

        uniformity = self._brightness_uniformity(face_gray)

        # ----------------------------
        # Spoof detection logic
        # ----------------------------

        suspicious = 0

        if texture_score < self.LAPLACIAN_THRESHOLD:
            suspicious += 1

        if fft_energy > self.FFT_ENERGY_THRESHOLD:
            suspicious += 1

        if edge_density > self.EDGE_DENSITY_THRESHOLD:
            suspicious += 1

        if uniformity < self.UNIFORMITY_THRESHOLD:
            suspicious += 1

        # allow some noise (false positives)
        if suspicious >= 3:

            return {
                "is_live": False,
                "score": 0.0,
                "reason": "Screen/Photo spoof suspected",
                "details": {
                    "texture": texture_score,
                    "fft": fft_energy,
                    "edges": edge_density,
                    "brightness": uniformity
                }
            }

        return {
            "is_live": True,
            "score": 1.0,
            "reason": "Looks live",
            "details": {}
        }


    # ---------------------------------
    # Challenge sequence detection
    # ---------------------------------

    def detect_sequence(self, frames, challenge):

        blink_counter = 0
        eye_closed_frames = 0

        left_turn = 0
        right_turn = 0

        for frame in frames:

            h, w, _ = frame.shape

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            results = self.face_mesh.process(rgb)

            if not results.multi_face_landmarks:
                continue

            landmarks = results.multi_face_landmarks[0].landmark

            LEFT_EYE = [33,160,158,133,153,144]
            RIGHT_EYE = [362,385,387,263,373,380]

            left_eye_pts = [(int(landmarks[i].x*w), int(landmarks[i].y*h)) for i in LEFT_EYE]
            right_eye_pts = [(int(landmarks[i].x*w), int(landmarks[i].y*h)) for i in RIGHT_EYE]

            left_ear = self._eye_aspect_ratio(left_eye_pts)
            right_ear = self._eye_aspect_ratio(right_eye_pts)

            ear = (left_ear + right_ear)/2.0

            # blink detection

            if ear < self.EAR_THRESHOLD:

                eye_closed_frames += 1

            else:

                if eye_closed_frames >= self.EAR_CONSEC_FRAMES:

                    blink_counter += 1

                eye_closed_frames = 0


            # head turn estimation

            nose = landmarks[1]
            left_cheek = landmarks[234]
            right_cheek = landmarks[454]

            nose_x = nose.x
            left_x = left_cheek.x
            right_x = right_cheek.x

            left_dist = abs(nose_x - left_x)
            right_dist = abs(nose_x - right_x)

            if left_dist < right_dist:
                right_turn += 1
            else:
                left_turn += 1


        # ----------------------------
        # Decision logic (RELAXED)
        # ----------------------------

        if challenge == "blink_twice":

            if blink_counter >= 1:
                return {"success": True, "reason": "Blink detected"}

            return {"success": False, "reason": "Blink not detected"}


        if challenge == "turn_left":

            if left_turn > right_turn:
                return {"success": True, "reason": "Turn left detected"}

            return {"success": False, "reason": "Turn left not detected"}


        if challenge == "turn_right":

            if right_turn > left_turn:
                return {"success": True, "reason": "Turn right detected"}

            return {"success": False, "reason": "Turn right not detected"}


        return {"success": False, "reason": "Unknown challenge"}