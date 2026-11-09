"""
Windows Auto-Start Manager:
Allows setting up the assistant to start automatically on Windows boot.
"""
import os
import sys

STARTUP_FOLDER = os.path.join(os.environ['APPDATA'], r'Microsoft\Windows\Start Menu\Programs\Startup')
VBS_LAUNCHER_PATH = os.path.join(STARTUP_FOLDER, 'LaunchAssistant.vbs')
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
BATCH_PATH = os.path.join(PROJECT_DIR, 'run.bat')

def enable_autostart():
    # VBScript allows launching the batch file silently in the background without popping up an ugly cmd window
    vbs_content = f'''Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "{PROJECT_DIR}"
WshShell.Run chr(34) & "{BATCH_PATH}" & chr(34), 0
Set WshShell = Nothing
'''
    try:
        with open(VBS_LAUNCHER_PATH, 'w') as f:
            f.write(vbs_content)
        print(f"[SUCCESS] Auto-start enabled! The assistant will launch silently in background on Windows boot.")
        print(f"Created startup entry at: {VBS_LAUNCHER_PATH}")
    except Exception as e:
        print(f"[ERROR] Failed to enable auto-start: {e}")

def disable_autostart():
    try:
        if os.path.exists(VBS_LAUNCHER_PATH):
            os.remove(VBS_LAUNCHER_PATH)
            print("[SUCCESS] Auto-start disabled. The assistant will no longer launch on boot.")
        else:
            print("[INFO] Auto-start was not enabled.")
    except Exception as e:
        print(f"[ERROR] Failed to disable auto-start: {e}")

if __name__ == '__main__':
    print("=" * 60)
    print("  WINDOWS AUTO-START CONFIGURATION")
    print("=" * 60)
    print("1. Enable Auto-Start on Windows Boot (Silent Background)")
    print("2. Disable Auto-Start")
    choice = input("\nEnter choice (1 or 2): ").strip()
    if choice == '1':
        enable_autostart()
    elif choice == '2':
        disable_autostart()
    else:
        print("Invalid choice.")

