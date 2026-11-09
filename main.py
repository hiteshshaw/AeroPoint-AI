"""
On-Device Multimodal Assistant (Gesture + Voice Controller)
Ultra-low CPU & Battery-Optimized Architecture
"""
import cv2
import time
import sys
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

            # Process Hand Landmarks
            debug_frame, hands = tracker.process_frame(frame)

            current_time = time.time()
            status_text = "Idle (Battery Saver)"

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

                elif action == 'CLICK':
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
                    status_text = "Right Click"
                    if current_time - last_click_time > click_cooldown:
                        sys_ctrl.click('right')
                        last_click_time = current_time
                    pinch_start_time = None
                    prev_scroll_y = None

                elif action == 'SCROLL_MODE':
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
                    status_text = "Swipe Right (Next Slide)"
                    sys_ctrl.press_key('right')
                    pinch_start_time = None
                    prev_scroll_y = None

                elif action == 'SWIPE_LEFT':
                    status_text = "Swipe Left (Prev Slide)"
                    sys_ctrl.press_key('left')
                    pinch_start_time = None
                    prev_scroll_y = None

                elif action == 'OPEN_PALM':
                    status_text = f"Volume: {int(gesture['volume_level'] * 100)}%"
                    sys_ctrl.set_volume(gesture['volume_level'])
                    if is_dragging:
                        sys_ctrl.mouse_up('left')
                        is_dragging = False
                    pinch_start_time = None
                    prev_scroll_y = None

                elif action == 'FIST':
                    status_text = "Paused (Fist)"
                    if is_dragging:
                        sys_ctrl.mouse_up('left')
                        is_dragging = False
                    pinch_start_time = None
                    prev_scroll_y = None
            else:
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
                cv2.putText(debug_frame, f"Gesture: {status_text}", (20, 35),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                voice_msg = voice_listener.latest_heard if voice_listener.latest_heard else "Listening..."
                cv2.putText(debug_frame, f"Voice: {voice_msg}", (20, 65),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 200, 0), 2)

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

