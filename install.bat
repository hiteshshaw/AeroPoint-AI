@echo off
title Setup - On-Device Multimodal Assistant
cd /d "%~dp0"

echo ======================================================================
echo   INSTALLING ON-DEVICE GESTURE ^& VOICE ASSISTANT
echo ======================================================================

:: 1. Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.10 or 3.11 from python.org and check "Add Python to PATH".
    pause
    exit /b 1
)

:: 2. Create Virtual Environment
if not exist "venv" (
    echo [1/3] Creating Python Virtual Environment (venv)...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create venv.
        pause
        exit /b 1
    )
) else (
    echo [1/3] Virtual environment already exists.
)

:: 3. Install Dependencies
echo [2/3] Installing lightweight libraries (OpenCV, MediaPipe, Faster-Whisper, PyAutoGUI)...
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install requirements.
    pause
    exit /b 1
)

:: 4. Verify Google MediaPipe Model
echo [3/3] Verifying AI Models...
if not exist "hand_landmarker.task" (
    echo Downloading hand_landmarker.task model (8 MB)...
    .\venv\Scripts\python.exe -c "import urllib.request; urllib.request.urlretrieve('https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task', 'hand_landmarker.task')"
)

echo ======================================================================
echo   SETUP COMPLETE!
echo   You can now launch the assistant anytime by double-clicking run.bat
echo ======================================================================
pause

