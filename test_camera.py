"""
Camera & Hand Tracking Visual Diagnostic Tool:
Displays camera feed with real-time MediaPipe skeletal landmarks without moving the mouse.
Useful for checking camera permissions, lighting, and tracking accuracy.
"""
import cv2
import time
from vision.hand_tracker import HandTracker


def test_camera():
    print("[DIAGNOSTIC] Initializing Hand Tracker & Probing webcam...")
    tracker = HandTracker()
    cap = cv2.VideoCapture(0)

    # Set 640x480 for lightweight processing
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not cap.isOpened():
        print("[FAIL] Camera could not be opened.")
        print("Tip: Check if your Lenovo laptop camera privacy shutter is closed, or press Fn+F9 to enable camera.")
        return

    print("[SUCCESS] Camera and Tracker active!")
    print("Press 'q' in the window to close.")

    prev_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[WARN] Failed to grab frame.")
            break

        curr_time = time.time()
        fps = 1.0 / (curr_time - prev_time) if curr_time > prev_time else 0
        prev_time = curr_time

        # Mirror frame
        frame = cv2.flip(frame, 1)

        # Process landmarks
        debug_frame, hands = tracker.process_frame(frame)

        hand_status = f"Hands Detected: {len(hands)}"
        cv2.putText(debug_frame, f"FPS: {int(fps)} | {hand_status}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(debug_frame, "Press 'q' to exit diagnostic mode", (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        cv2.imshow("Hand Tracking Diagnostic", debug_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("[DIAGNOSTIC] Closed cleanly.")


if __name__ == '__main__':
    test_camera()
