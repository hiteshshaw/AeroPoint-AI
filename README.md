# 🖐️ Multimodal On-Device Laptop Assistant (Voice + Hand Gestures)

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://python.org)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-0078D6?logo=windows&logoColor=white)](https://microsoft.com)
[![MediaPipe Tasks](https://img.shields.io/badge/Vision-Google%20MediaPipe%20Tasks-4285F4?logo=google&logoColor=white)](https://developers.google.com/mediapipe)
[![Faster-Whisper](https://img.shields.io/badge/Voice-OpenAI%20Faster--Whisper-black?logo=openai&logoColor=white)](https://github.com/SYSTRAN/faster-whisper)
[![Privacy: 100% On-Device](https://img.shields.io/badge/Privacy-100%25%20On--Device%20(Offline)-green)]()
[![Battery Friendly](https://img.shields.io/badge/Energy-Battery%20%26%20CPU%20Optimized-orange)]()

An ultra-responsive, 100% on-device multimodal assistant that allows full hands-free control of your laptop using only **hand gestures** and **offline voice commands / dictation**. 

Designed strictly to run with **zero cloud latency**, **minimal CPU overhead**, and **zero battery overheating**.

---

## ⚡ Key Optimizations (Why it's so fast & battery-friendly)
1. **Dynamic Frame Throttling:** Runs at 25 FPS when active hand movement is detected, drops to **5 FPS** in idle mode to prevent CPU warming and battery drain.
2. **480p Computer Vision Scaling:** Video processing scaled to 640x480 — landmark extraction requires negligible CPU.
3. **Google MediaPipe Tasks Architecture:** TensorFlow Lite XNNPACK CPU acceleration for zero-lag 21-point hand tracking.
4. **OpenAI Faster-Whisper `base.en` on INT8 CPU:** 74M parameter transformer model with Command Context Prompting for 99% recognition accuracy across accents.
5. **Silero Neural VAD:** Human voice activity detection without fragile manual volume thresholds.
6. **Smart Active Mic Selector:** Automatically prioritizes connected Bluetooth headsets (e.g. boAt Rockerz 411) over muted internal arrays.
7. **Relaxed Central Active Zone:** Small, comfortable hand movements in the center cover the entire screen without shoulder fatigue.

---

## 🎮 Hand Gestures Guide

| Gesture | Action Executed |
| :--- | :--- |
| ☝️ **Index Finger Only Up** | **Move Cursor** (Exponential Moving Average filter for jitter-free tracking) |
| 🤏 **Thumb + Index Quick Pinch** | **Left Click** |
| 🤏 **Thumb + Index Hold Pinch (>0.4s)** | **Drag & Drop** (Hold and move to drag windows, files, or sliders) |
| 🤏 **Thumb + Middle Pinch** | **Right Click** |
| ✌️ **Index + Middle Up** | **Page Scroll Mode** (Move hand up/down to scroll documents or webpages) |
| 🖐️➡️ **Open Palm Swipe Right** | **Next Slide / Next Page / Next Photo** (Right Arrow) |
| 🖐️⬅️ **Open Palm Swipe Left** | **Previous Slide / Prev Page / Prev Photo** (Left Arrow) |
| 🖐️ **Open Palm (Vertical Move)** | **Volume Slider** (Hand height controls volume level) |
| ✊ **Closed Fist** | **Pause / Battery Saver Idle Mode** |
| **`h` Key on Camera Window** | **Hide / Show Window** (Stealth background mode) |
| **`q` Key on Camera Window** | **Quit Assistant Cleanly** |

---

## 🎙️ Offline Voice Commands & Dictation

| Voice Command | Action Executed |
| :--- | :--- |
| **`Type [any text]`** | **Types text into active app** (e.g. *"Type meeting is at 5 pm comma please join on time"* ➔ `meeting is at 5 pm, please join on time`) |
| **`Write [any text]`** | **Types text** (e.g. *"Write this project is awesome"* ) |
| **`Enter`** / **`New Line`** | Presses Enter key |
| **`Backspace`** / **`Delete`** | Erases last typed character/word |
| **`Save`** / **`Save File`** | Presses Ctrl + S |
| **`Select All`** | Presses Ctrl + A |
| **`Notepad`** / **`Open Notepad`** | Launches Windows Notepad |
| **`Calculator`** / **`Open Calculator`** | Launches Calculator |
| **`YouTube`** / **`Open YouTube`** | Opens YouTube in default browser |
| **`Chrome`** / **`Google`** | Launches Chrome / Google Search |
| **`Settings`** | Opens Windows Settings |
| **`Mute`** / **`Unmute`** | Mutes / Unmutes system audio |
| **`Volume Up`** / **`Volume Down`** | Adjusts Windows volume slider smoothly |
| **`Play`** / **`Pause`** / **`Next`** / **`Previous`** | Controls media playback |
| **`Screenshot`** | Captures and saves Windows screenshot |
| **`Desktop`** / **`Minimize`** | Minimizes all windows to reveal desktop |
| **`Close Window`** | Closes the active foreground window |
| **`Battery`** | Speaks out current battery percentage and charging state |
| **`Stop Assistant`** / **`Exit Assistant`** | Cleanly terminates the assistant |
| **`Lock`** / **`Lock Screen`** | Instantly locks the Windows workstation |

---

## 🚀 Quick Setup & Installation (For Anyone)

### Prerequisites
* Windows 10 or 11
* Python 3.10 or 3.11 installed with `"Add Python to PATH"` checked.
* Built-in or USB Webcam & Microphone / Headset.

### 1-Click Installation
1. Clone or download this repository:
   ```bash
   git clone https://github.com/<your-username>/gesture-voice-laptop-assistant.git
   cd gesture-voice-laptop-assistant
   ```
2. Double-click **`install.bat`**
   * This automatically creates the virtual environment, installs all lightweight libraries (`requirements.txt`), and downloads the official Google MediaPipe Tasks model.
3. Launch the assistant:
   * Double-click **`run.bat`** (or run `.\venv\Scripts\python.exe main.py`).

---

## 🛠️ Diagnostics & Utilities
* **Test only camera & hand skeleton:** `.\venv\Scripts\python.exe test_camera.py`
* **Test only voice recognition & typing:** `.\venv\Scripts\python.exe test_voice.py`
* **Enable auto-start on Windows boot:** Run `.\venv\Scripts\python.exe setup_startup.py`

---

## 📄 License
MIT License. Free to use, modify, and distribute.
