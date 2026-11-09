"""
Gesture Recognizer: Computes finger states and triggers actions
- Cursor Move: Index finger pointed UP, others down
- Left Click: Thumb and Index tips pinched together (< threshold)
- Drag & Drop: Hold pinch and move
- Right Click: Middle and Thumb pinched together
- Scroll: Two fingers (Index + Middle) moving up/down
- Swipe: Fast lateral palm movement (Next/Previous slide)
- Volume: Open palm vertical adjustment
- Fist: Sleep/Pause mode
"""
import time
import math
from typing import List, Dict, Optional


class GestureRecognizer:
    def __init__(self, click_thresh: float = 0.05):
        self.click_thresh = click_thresh
        self.palm_history = []  # (x, timestamp)
        self.last_swipe_time = 0

    @staticmethod
    def euclidean_dist(p1: Dict, p2: Dict) -> float:
        return math.hypot(p1['x'] - p2['x'], p1['y'] - p2['y'])

    def get_finger_status(self, landmarks: List[Dict]) -> Dict[str, bool]:
        """Returns True if the finger is raised/extended."""
        status = {}
        # Thumb
        status['thumb'] = landmarks[4]['x'] < landmarks[3]['x'] if landmarks[17]['x'] > landmarks[5]['x'] else landmarks[4]['x'] > landmarks[3]['x']
        
        # Fingers 4 (Index, Middle, Ring, Pinky)
        status['index'] = landmarks[8]['y'] < landmarks[6]['y']
        status['middle'] = landmarks[12]['y'] < landmarks[10]['y']
        status['ring'] = landmarks[16]['y'] < landmarks[14]['y']
        status['pinky'] = landmarks[20]['y'] < landmarks[18]['y']
        return status

    def check_swipe(self, palm_x: float) -> Optional[str]:
        """Detects fast lateral hand swipe movement across frames."""
        now = time.time()
        self.palm_history.append((palm_x, now))
        # Keep last 0.35 seconds
        self.palm_history = [(x, t) for x, t in self.palm_history if now - t < 0.35]

        if len(self.palm_history) >= 4 and now - self.last_swipe_time > 0.8:
            start_x, start_t = self.palm_history[0]
            dx = palm_x - start_x
            dt = now - start_t
            if dt > 0.05:
                velocity = dx / dt
                if velocity > 1.2:  # Fast right swipe
                    self.last_swipe_time = now
                    self.palm_history.clear()
                    return 'SWIPE_RIGHT'
                elif velocity < -1.2:  # Fast left swipe
                    self.last_swipe_time = now
                    self.palm_history.clear()
                    return 'SWIPE_LEFT'
        return None

    def identify_gesture(self, landmarks: List[Dict]) -> Dict:
        if not landmarks or len(landmarks) < 21:
            return {'action': 'NONE'}

        fingers = self.get_finger_status(landmarks)
        index_tip = landmarks[8]
        thumb_tip = landmarks[4]
        middle_tip = landmarks[12]
        palm_center = landmarks[9]

        thumb_index_dist = self.euclidean_dist(thumb_tip, index_tip)
        thumb_middle_dist = self.euclidean_dist(thumb_tip, middle_tip)

        # 1. Swipe Check on Open Palm
        if all(fingers.values()):
            swipe = self.check_swipe(palm_center['x'])
            if swipe:
                return {'action': swipe}
            return {
                'action': 'OPEN_PALM',
                'volume_level': max(0.0, min(1.0, 1.0 - index_tip['y']))
            }

        # 2. Pinch Click / Drag (Thumb + Index close)
        if thumb_index_dist < self.click_thresh:
            return {
                'action': 'CLICK',
                'distance': thumb_index_dist,
                'norm_x': index_tip['x'],
                'norm_y': index_tip['y']
            }

        # 3. Right Click (Thumb + Middle close)
        if thumb_middle_dist < self.click_thresh:
            return {
                'action': 'RIGHT_CLICK',
                'distance': thumb_middle_dist,
                'point': (middle_tip['x'], middle_tip['y'])
            }

        # 4. Two fingers up: Scroll mode
        if fingers['index'] and fingers['middle'] and not fingers['ring'] and not fingers['pinky']:
            return {
                'action': 'SCROLL_MODE',
                'y': index_tip['y']
            }

        # 5. Only Index finger up: Move Cursor
        if fingers['index'] and not fingers['middle'] and not fingers['ring'] and not fingers['pinky']:
            return {
                'action': 'MOVE',
                'norm_x': index_tip['x'],
                'norm_y': index_tip['y']
            }

        # 6. Fist: Stop / Sleep
        if not any(fingers.values()):
            return {'action': 'FIST'}

        return {'action': 'NONE'}
