@echo off
title Build Standalone Executable
cd /d "%~dp0"

echo ======================================================================
echo   BUILDING STANDALONE EXECUTABLE (.EXE)
echo ======================================================================

echo [1/3] Installing PyInstaller in virtual environment...
.\venv\Scripts\python.exe -m pip install pyinstaller

echo [2/3] Building GestureAssistant.exe...
.\venv\Scripts\pyinstaller.exe --noconfirm --onedir --windowed ^
    --add-data "hand_landmarker.task;." ^
    --add-data "config.py;." ^
    --add-data "vision;vision" ^
    --add-data "voice;voice" ^
    --add-data "controller;controller" ^
    --name "GestureAssistant" ^
    main.py

echo [3/3] Build finished!
echo Output executable is located in: dist\GestureAssistant\GestureAssistant.exe
echo ======================================================================
pause

