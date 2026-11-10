"""
On-Device Multimodal Assistant (Gesture + Voice Controller)
Ultra-low CPU & Battery-Optimized Architecture
"""
import cv2
import time
import sys
import math
import threading

import config
from vision.hand_tracker import HandTracker
from vision.gesture_recognizer import GestureRecognizer
from controller.os_actions import SystemController
from voice.speech_engine import VoiceIntentEngine
from voice.whisper_listener import WhisperVoiceListener


def run_assistant():
    print("=" * 60)
    print("  ON-DEVICE LIGHTWEIGHT ASSISTANT STARTING...")
    print("  Controls:")
    print("  - Index finger up: Move cursor")
    print("  - Pinch (Thumb + Index): Left click")
    print("  - Pinch (Thumb + Middle): Right click")
    print("  - Index + Middle up: Scroll mode")
    print("  - Open Palm: Volume adjustment (up/down)")
    print("  - Voice: 'Open YouTube', 'Mute', 'Volume Up', 'Lock Screen'")
    print("  - Press 'q' in camera window to quit")
    print("=" * 60)

    # Initialize Modules
    sys_ctrl = SystemController()
    tracker = HandTracker(max_hands=1, detection_con=0.6, track_con=0.5)
    recognizer = GestureRecognizer(click_thresh=config.CLICK_DISTANCE_THRESHOLD)
    voice_engine = VoiceIntentEngine(system_controller=sys_ctrl)

    # Start High-Accuracy Whisper Voice Listener Thread
    voice_listener = WhisperVoiceListener(intent_engine=voice_engine)
    voice_listener.start()

    # Initialize Webcam with lightweight resolution
    cap = cv2.VideoCapture(config.CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)

    if not cap.isOpened():
        print("[ERROR] Camera could not be opened. Please ensure camera privacy shutter is OPEN.")
        return

    last_hand_time = time.time()
    last_click_time = 0
    pinch_start_time = None
    is_dragging = False
    click_cooldown = 0.35  # Prevent accidental double clicks

    # Accessibility: Dwell Click (Hover-to-Click) State Variables
    dwell_anchor_x = None
    dwell_anchor_y = None
    dwell_start_time = None
    last_dwell_click_time = 0
    dwell_progress = 0.0

    prev_scroll_y = None
    show_window = True

    try:
        while cap.isOpened():
            start_time = time.time()

            ret, frame = cap.read()
            if not ret:
                time.sleep(0.05)
                continue

            # Mirror frame for natural gesture control
            frame = cv2.flip(frame, 1)

            # Process Hand Landmarks (if enabled in active profile)
            if getattr(config, 'CAMERA_ENABLED', True):
                debug_frame, hands = tracker.process_frame(frame)
            else:
                debug_frame = frame
                hands = []
                time.sleep(1.0 / config.IDLE_FPS)

            current_time = time.time()
            status_text = "Idle (Battery Saver)" if getattr(config, 'CAMERA_ENABLED', True) else "Hands-Busy (Voice Only)"
            gesture = {'action': 'NONE'}

            if hands:
                last_hand_time = current_time
                landmarks = hands[0]
                gesture = recognizer.identify_gesture(landmarks)
                action = gesture.get('action', 'NONE')

                if action == 'MOVE':
                    status_text = "Moving Cursor"
                    norm_x, norm_y = gesture['norm_x'], gesture['norm_y']
                    sys_ctrl.move_cursor(norm_x, norm_y, smoothing=config.SMOOTHING_FACTOR)
                    if is_dragging:
                        sys_ctrl.mouse_up('left')
                        is_dragging = False
                    pinch_start_time = None
                    prev_scroll_y = None

                    # Accessibility: Dwell Click (Hover-to-Click for Motor Tremor/Parkinson's)
                    if getattr(config, 'ENABLE_DWELL_CLICK', True):
                        if dwell_anchor_x is None:
                            dwell_anchor_x, dwell_anchor_y = norm_x, norm_y
                            dwell_start_time = current_time
                            dwell_progress = 0.0
                        else:
                            dist = math.hypot(norm_x - dwell_anchor_x, norm_y - dwell_anchor_y)
                            if dist > getattr(config, 'DWELL_RADIUS_NORM', 0.03):
                                dwell_anchor_x, dwell_anchor_y = norm_x, norm_y
                                dwell_start_time = current_time
                                dwell_progress = 0.0
                            else:
                                elapsed = current_time - dwell_start_time
                                dwell_target = getattr(config, 'DWELL_TIME_SEC', 1.0)
                                dwell_progress = min(1.0, elapsed / dwell_target)
                                if current_time - last_dwell_click_time > getattr(config, 'DWELL_COOLDOWN_SEC', 1.2):
                                    if dwell_progress >= 1.0:
                                        sys_ctrl.click('left')
                                        last_dwell_click_time = current_time
                                        status_text = "🎯 DWELL CLICK!"
                                        dwell_anchor_x = None
                                        dwell_start_time = None
                                        dwell_progress = 0.0
                                    else:
                                        status_text = f"Dwell Hover ({int(dwell_progress * 100)}%)"

                elif action == 'CLICK':
                    dwell_anchor_x, dwell_anchor_y, dwell_start_time, dwell_progress = None, None, None, 0.0
                    norm_x, norm_y = gesture.get('norm_x', 0.5), gesture.get('norm_y', 0.5)
                    sys_ctrl.move_cursor(norm_x, norm_y, smoothing=config.SMOOTHING_FACTOR)

                    if pinch_start_time is None:
                        pinch_start_time = current_time

                    # If pinch is held longer than DRAG_HOLD_TIME_SEC, initiate drag
                    if current_time - pinch_start_time > config.DRAG_HOLD_TIME_SEC:
                        if not is_dragging:
                            sys_ctrl.mouse_down('left')
                            is_dragging = True
                        status_text = "Dragging..."
                    else:
                        status_text = "Pinch"

                    prev_scroll_y = None

                elif action == 'RIGHT_CLICK':
                    dwell_anchor_x, dwell_anchor_y, dwell_start_time, dwell_progress = None, None, None, 0.0
                    status_text = "Right Click"
                    if current_time - last_click_time > click_cooldown:
                        sys_ctrl.click('right')
                        last_click_time = current_time
                    pinch_start_time = None
                    prev_scroll_y = None

                elif action == 'SCROLL_MODE':
                    dwell_anchor_x, dwell_anchor_y, dwell_start_time, dwell_progress = None, None, None, 0.0
                    status_text = "Scrolling"
                    curr_y = gesture['y']
                    if prev_scroll_y is not None:
                        diff = prev_scroll_y - curr_y
                        if abs(diff) > 0.02:
                            scroll_amount = int(diff * 500)
                            sys_ctrl.scroll(scroll_amount)
                    prev_scroll_y = curr_y
                    pinch_start_time = None

                elif action == 'SWIPE_RIGHT':
                    dwell_anchor_x, dwell_anchor_y, dwell_start_time, dwell_progress = None, None, None, 0.0
                    status_text = "Swipe Right (Next Slide)"
                    sys_ctrl.press_key('right')
                    pinch_start_time = None
                    prev_scroll_y = None

                elif action == 'SWIPE_LEFT':
                    dwell_anchor_x, dwell_anchor_y, dwell_start_time, dwell_progress = None, None, None, 0.0
                    status_text = "Swipe Left (Prev Slide)"
                    sys_ctrl.press_key('left')
                    pinch_start_time = None
                    prev_scroll_y = None

                elif action == 'OPEN_PALM':
                    dwell_anchor_x, dwell_anchor_y, dwell_start_time, dwell_progress = None, None, None, 0.0
                    status_text = f"Volume: {int(gesture['volume_level'] * 100)}%"
                    sys_ctrl.set_volume(gesture['volume_level'])
                    if is_dragging:
                        sys_ctrl.mouse_up('left')
                        is_dragging = False
                    pinch_start_time = None
                    prev_scroll_y = None

                elif action == 'FIST':
                    dwell_anchor_x, dwell_anchor_y, dwell_start_time, dwell_progress = None, None, None, 0.0
                    status_text = "Paused (Fist)"
                    if is_dragging:
                        sys_ctrl.mouse_up('left')
                        is_dragging = False
                    pinch_start_time = None
                    prev_scroll_y = None
            else:
                dwell_anchor_x, dwell_anchor_y, dwell_start_time, dwell_progress = None, None, None, 0.0
                if is_dragging:
                    sys_ctrl.mouse_up('left')
                    is_dragging = False
                pinch_start_time = None
                prev_scroll_y = None
                # Battery Saver: If no hand seen for AUTO_SLEEP_TIMEOUT_SEC, throttle frame rate
                if current_time - last_hand_time > config.AUTO_SLEEP_TIMEOUT_SEC:
                    time.sleep(1.0 / config.IDLE_FPS)

            # Handle mouse click release when pinch ended quickly
            if gesture.get('action') != 'CLICK' and pinch_start_time is not None:
                if current_time - pinch_start_time <= config.DRAG_HOLD_TIME_SEC:
                    if current_time - last_click_time > click_cooldown:
                        sys_ctrl.click('left')
                        last_click_time = current_time
                pinch_start_time = None

            # Display HUD on Camera Window
            if show_window:
                # Render Dwell Progress Ring if user is hovering
                if dwell_progress > 0.0 and dwell_anchor_x is not None:
                    cx = int(dwell_anchor_x * config.CAMERA_WIDTH)
                    cy = int(dwell_anchor_y * config.CAMERA_HEIGHT)
                    # Outer guide circle
                    cv2.circle(debug_frame, (cx, cy), 22, (80, 80, 80), 2)
                    # Progress arc
                    end_angle = int(dwell_progress * 360)
                    cv2.ellipse(debug_frame, (cx, cy), (22, 22), 0, -90, -90 + end_angle, (0, 255, 255), 3)

                cv2.putText(debug_frame, f"Gesture: {status_text}", (20, 35),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                if getattr(voice_listener, 'is_speaking', False):
                    voice_msg = "Voice: [HEARING YOU SPEAK...]"
                    voice_color = (0, 255, 255)
                elif voice_listener.latest_heard:
                    voice_msg = f"Voice: '{voice_listener.latest_heard}'"
                    voice_color = (0, 255, 0)
                else:
                    voice_msg = "Voice: Ready (Speak into mic)"
                    voice_color = (255, 200, 0)

                cv2.putText(debug_frame, voice_msg, (20, 65),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, voice_color, 2)

                cv2.putText(debug_frame, f"Profile: {getattr(config, 'ACTIVE_PROFILE', 'DEFAULT')}", (20, 92),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (220, 220, 255), 1)

                cv2.imshow("On-Device Assistant", debug_frame)

            # Keyboard controls: 'q' to quit, 'h' to toggle window visibility
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('h'):
                show_window = not show_window
                if not show_window:
                    cv2.destroyAllWindows()
                    print("[INFO] Camera window hidden (Background stealth mode). Press Ctrl+C in terminal to quit.")

    finally:
        voice_listener.stop()
        cap.release()
        cv2.destroyAllWindows()
        print("[INFO] Assistant stopped cleanly.")


if __name__ == '__main__':
    run_assistant()

