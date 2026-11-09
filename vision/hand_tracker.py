"""
Hand Tracker: High-performance Google MediaPipe Tasks API.
Optimized for zero-lag and minimum CPU overhead.
"""
import os
import cv2
import time
from typing import List, Tuple, Dict
import mediapipe as mp
from mediapipe.tasks.python import vision

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = vision.HandLandmarker
HandLandmarkerOptions = vision.HandLandmarkerOptions
VisionRunningMode = vision.RunningMode

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),        # Thumb
    (0, 5), (5, 6), (6, 7), (7, 8),        # Index
    (5, 9), (9, 10), (10, 11), (11, 12),   # Middle
    (9, 13), (13, 14), (14, 15), (15, 16), # Ring
    (13, 17), (17, 18), (18, 19), (19, 20),# Pinky
    (0, 17)                                # Palm base
]


class HandTracker:
    def __init__(self, model_path: str = "hand_landmarker.task", max_hands: int = 1, detection_con: float = 0.6, track_con: float = 0.5):
        if not os.path.isabs(model_path):
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(base_dir, model_path)

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at: {model_path}")

        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=VisionRunningMode.VIDEO,
            num_hands=max_hands,
            min_hand_detection_confidence=detection_con,
            min_tracking_confidence=track_con
        )
        self.landmarker = HandLandmarker.create_from_options(options)
        self.start_time = time.time()
        self.last_timestamp = 0

    def process_frame(self, frame) -> Tuple[any, List[List[Dict]]]:
        """
        Processes BGR frame using MediaPipe Tasks Vision.
        Returns visual debug frame & normalized 21 landmark points.
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        # Monotonically increasing timestamp in ms
        timestamp_ms = int((time.time() - self.start_time) * 1000)
        if timestamp_ms <= self.last_timestamp:
            timestamp_ms = self.last_timestamp + 1
        self.last_timestamp = timestamp_ms

        result = self.landmarker.detect_for_video(mp_image, timestamp_ms)

        landmarks_list = []
        h, w, _ = frame.shape

        if result.hand_landmarks:
            for hand in result.hand_landmarks:
                landmarks = []
                coords = []
                for idx, lm in enumerate(hand):
                    landmarks.append({
                        'id': idx,
                        'x': lm.x,
                        'y': lm.y,
                        'z': lm.z
                    })
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    coords.append((cx, cy))
                    cv2.circle(frame, (cx, cy), 4, (0, 255, 0), -1)

                # Draw hand skeleton connections
                for start_idx, end_idx in HAND_CONNECTIONS:
                    if start_idx < len(coords) and end_idx < len(coords):
                        cv2.line(frame, coords[start_idx], coords[end_idx], (0, 200, 255), 2)

                landmarks_list.append(landmarks)

        return frame, landmarks_list
