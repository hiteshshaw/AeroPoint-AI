@echo off
title On-Device Gesture & Voice Assistant
cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    echo ======================================================================
    echo   First time setup needed!
    echo   Please run "install.bat" first to set up the environment.
    echo ======================================================================
    pause
    exit /b 1
)

echo ======================================================================
echo   Starting On-Device Gesture and Voice Assistant...
echo   100%% Local - Ultra-Low CPU - Battery Optimized
echo ======================================================================
.\venv\Scripts\python.exe main.py
pause
