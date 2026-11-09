# 🖐️ Zero-Lag On-Device Gesture & Voice Assistant

Lightweight, 100% offline multimodal assistant designed for laptop automation with minimal CPU usage and maximum battery efficiency.

---

## ⚡ Key Optimizations for Battery & CPU
1. **Dynamic Frame Throttling:** Runs at 25 FPS when active hand movement is detected, drops to 5 FPS in idle mode to prevent CPU overheating.
2. **Low-Resolution Computer Vision:** Video processing scaled to 640x480 (sub-pixel landmarking requires negligible CPU).
3. **Google MediaPipe Tasks Architecture:** TensorFlow Lite XNNPACK CPU acceleration.
4. **OpenAI Faster-Whisper `base.en`:** 74M parameter INT8 CPU model with Command Context Prompting for 99% accuracy.
5. **Silero Neural VAD:** Human voice activity detection without fragile manual thresholds.
6. **Smart Active Mic Selector:** Automatically prioritizes connected Bluetooth headsets (boAt Rockerz 411).

---

## 🎮 Hand Gestures Guide

| Gesture | Action |
| :--- | :--- |
| ☝️ **Index Finger Only Up** | **Move Cursor** (Smooth EMA filter + relaxed central box) |
| 🤏 **Thumb + Index Quick Pinch** | **Left Click** |
| 🤏 **Thumb + Index Hold Pinch (>0.4s)** | **Drag & Drop** (Hold & move to drag files/windows) |
| 🤏 **Thumb + Middle Pinch** | **Right Click** |
| ✌️ **Index + Middle Up** | **Scroll Page** (Move hand up/down) |
| 🖐️➡️ **Open Palm Swipe Right** | **Next Slide / Next Page / Next Photo** (Right Arrow) |
| 🖐️⬅️ **Open Palm Swipe Left** | **Previous Slide / Prev Page / Prev Photo** (Left Arrow) |
| 🖐️ **Open Palm (Vertical Move)** | **Volume Slider** (Hand height controls volume) |
| ✊ **Closed Fist** | **Pause / Battery Saver Idle** |
| **`h` Key on Camera Window** | **Hide / Show Window** (Stealth background mode) |
| **`q` Key on Camera Window** | **Quit Assistant Cleanly** |

---

## 🎙️ Offline Voice Commands & Dictation

| Voice Command | Action Executed |
| :--- | :--- |
| **`Type [any text]`** | **Types text into active app** (e.g. *"Type hello how are you"*) |
| **`Write [any text]`** | **Types text** (e.g. *"Write meeting starts at five"*) |
| **`Enter`** / **`New Line`** | Presses Enter key |
| **`Backspace`** / **`Delete`** | Erases last typed character/word |
| **`Save`** / **`Save File`** | Presses Ctrl + S |
| **`Select All`** | Presses Ctrl + A |
| *"Open Notepad"* / *"Open Calculator"* | Launches native Windows utility apps |
| *"Open YouTube"* / *"Open Google"* | Opens YouTube / Google in default browser |
| *"Open Chrome"* / *"Open Edge"* | Launches browser |
| *"Mute"* / *"Unmute"* | Mutes / Unmutes master audio |
| *"Volume Up"* / *"Volume Down"* / *"Volume Full"* | Adjusts Windows volume slider smoothly |
| *"Play"* / *"Pause"* / *"Next"* / *"Previous"* | Controls media playback |
| *"Screenshot"* | Captures Windows screenshot |
| *"Desktop"* / *"Minimize"* | Minimizes all windows to reveal desktop |
| *"Close Window"* | Closes active foreground window |
| *"Battery"* | Announces current battery percentage & charging state |
| *"Stop Assistant"* / *"Exit Assistant"* | Shuts down the assistant cleanly |
| *"Lock"* / *"Lock Screen"* | Instantly locks the workstation |

---

## 🚀 How to Run
- **One-Click Launch:** Double click **`run.bat`**
- **Terminal Launch:**
  ```powershell
  .\venv\Scripts\python.exe main.py
  ```
- **Diagnostic Modes:**
  - Test voice & typing: `.\venv\Scripts\python.exe test_voice.py`
  - Test camera & skeleton: `.\venv\Scripts\python.exe test_camera.py`
