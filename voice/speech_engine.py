"""
Offline Voice Intent Engine:
Executes system commands with microsecond latency using direct OS & Shell calls.
Includes Contextual Prefix Joining ('open' + 'notepad' -> 'open notepad')
and Standalone Keyword Launching ('notepad' -> launches notepad).
"""
import os
import time
import subprocess
import webbrowser
import psutil
from typing import Optional, Dict

try:
    import pyautogui
except ImportError:
    pyautogui = None

try:
    from controller.os_actions import SystemController
except ImportError:
    SystemController = None


class VoiceIntentEngine:
    def __init__(self, system_controller=None):
        if system_controller is None and SystemController is not None:
            self.sys = SystemController()
        else:
            self.sys = system_controller

        self.last_prefix = ""
        self.last_prefix_time = 0

        self.apps = {
            'notepad': 'notepad.exe',
            'calculator': 'calc.exe',
            'calc': 'calc.exe',
            'cmd': 'cmd.exe',
            'terminal': 'cmd.exe',
            'explorer': 'explorer.exe',
            'files': 'explorer.exe',
            'task manager': 'taskmgr.exe',
            'taskmgr': 'taskmgr.exe',
            'chrome': 'chrome',
            'edge': 'msedge',
            'settings': 'ms-settings:'
        }

    def execute_command(self, text: str) -> Dict[str, str]:
        text = text.lower().strip()
        if not text:
            return {'status': 'ignored', 'message': ''}

        now = time.time()

        # Contextual Join: If previous word was "open" or "type" within 3 seconds
        if self.last_prefix and (now - self.last_prefix_time) < 3.0:
            combined = f"{self.last_prefix} {text}".strip()
            print(f"  🔗 [CONTEXT JOIN]: '{self.last_prefix}' + '{text}' -> '{combined}'")
            text = combined
            self.last_prefix = ""

        # If user spoke just "open", remember it for 3 seconds
        if text in ['open', 'launch', 'start']:
            self.last_prefix = "open"
            self.last_prefix_time = now
            print("  ⏳ [WAITING]: Said 'Open'. Speak app name (e.g. 'notepad', 'chrome', 'youtube')...")
            return {'status': 'waiting', 'message': 'Say app name...'}

        if text in ['type', 'write', 'dictate']:
            self.last_prefix = "type"
            self.last_prefix_time = now
            print("  ⏳ [WAITING]: Said 'Type'. Speak what to type...")
            return {'status': 'waiting', 'message': 'Say text to type...'}

        print(f"\n⚡ [INTENT MATCHING]: Evaluating '{text}'...")

        # 0. Voice Typing & Dictation
        for trigger in ['type ', 'write ', 'dictate ']:
            if text.startswith(trigger):
                content = text[len(trigger):].strip()
                if content:
                    punctuations = {
                        ' comma': ',', 'comma ': ', ', ' comma ': ', ',
                        ' period': '.', ' full stop': '.', ' dot': '.',
                        ' question mark': '?', ' exclamation mark': '!',
                        ' colon': ':', ' semicolon': ';'
                    }
                    for p_word, p_symbol in punctuations.items():
                        content = content.replace(p_word, p_symbol)

                    print(f"  -> Executing: Typing into active window: '{content}'")
                    if pyautogui:
                        pyautogui.write(content + " ", interval=0.005)
                    return {'status': 'success', 'message': f'Typed: "{content}"'}

        # 0.1 Multimodal Fusion: Voice Mouse & Cursor Actions (Point + Speak)
        if text in ['click', 'left click', 'tap', 'press']:
            print("  -> 🎯 [MULTIMODAL FUSION]: Voice Left Click at cursor position...")
            if self.sys:
                self.sys.click('left')
            return {'status': 'success', 'message': 'Voice Left Click'}

        if text in ['double click', 'open this']:
            print("  -> 🎯 [MULTIMODAL FUSION]: Voice Double Click at cursor position...")
            if self.sys:
                self.sys.double_click()
            return {'status': 'success', 'message': 'Voice Double Click'}

        if text in ['right click', 'context menu']:
            print("  -> 🎯 [MULTIMODAL FUSION]: Voice Right Click at cursor position...")
            if self.sys:
                self.sys.click('right')
            return {'status': 'success', 'message': 'Voice Right Click'}

        if text in ['drag', 'drag this', 'hold mouse']:
            print("  -> 🎯 [MULTIMODAL FUSION]: Voice Drag (Mouse Down)...")
            if self.sys:
                self.sys.mouse_down('left')
            return {'status': 'success', 'message': 'Dragging started'}

        if text in ['drop', 'release', 'release mouse', 'drop here']:
            print("  -> 🎯 [MULTIMODAL FUSION]: Voice Drop (Mouse Up)...")
            if self.sys:
                self.sys.mouse_up('left')
            return {'status': 'success', 'message': 'Released drop'}

        if text in ['scroll down', 'page down']:
            print("  -> 🎯 [MULTIMODAL FUSION]: Voice Scroll Down...")
            if self.sys:
                self.sys.scroll(-500)
            return {'status': 'success', 'message': 'Scrolled down'}

        if text in ['scroll up', 'page up']:
            print("  -> 🎯 [MULTIMODAL FUSION]: Voice Scroll Up...")
            if self.sys:
                self.sys.scroll(500)
            return {'status': 'success', 'message': 'Scrolled up'}

        if text in ['maximize', 'maximize window', 'full screen']:
            print("  -> Executing: Maximize Window (Win+Up)...")
            if pyautogui:
                pyautogui.hotkey('win', 'up')
            return {'status': 'success', 'message': 'Maximized window'}

        # Keyboard editing keys
        if text in ['press enter', 'new line', 'enter']:
            print("  -> Executing: Enter key...")
            if pyautogui:
                pyautogui.press('enter')
            return {'status': 'success', 'message': 'Pressed Enter'}

        if text in ['press backspace', 'delete', 'backspace', 'erase']:
            print("  -> Executing: Backspace key...")
            if pyautogui:
                pyautogui.press('backspace')
            return {'status': 'success', 'message': 'Pressed Backspace'}

        if text in ['save file', 'save document', 'save']:
            print("  -> Executing: Save (Ctrl+S)...")
            if pyautogui:
                pyautogui.hotkey('ctrl', 's')
            return {'status': 'success', 'message': 'Saved file'}

        if text in ['select all']:
            print("  -> Executing: Select All (Ctrl+A)...")
            if pyautogui:
                pyautogui.hotkey('ctrl', 'a')
            return {'status': 'success', 'message': 'Selected all'}

        # 1. Websites & Media
        if any(w in text for w in ['youtube', 'u tube', 'you tube']):
            print("  -> Executing: Launching YouTube in Browser...")
            try:
                os.system('start https://www.youtube.com')
            except Exception:
                webbrowser.open('https://www.youtube.com')
            return {'status': 'success', 'message': 'Opening YouTube'}

        if any(w in text for w in ['google', 'goggle']):
            print("  -> Executing: Launching Google...")
            try:
                os.system('start https://www.google.com')
            except Exception:
                webbrowser.open('https://www.google.com')
            return {'status': 'success', 'message': 'Opening Google'}

        # 2. Local Applications (Supports "open notepad" OR just "notepad")
        for app_name, exe_name in self.apps.items():
            if f'open {app_name}' in text or f'launch {app_name}' in text or text == app_name or f'start {app_name}' in text or app_name in text:
                print(f"  -> Executing: Launching {app_name.capitalize()}...")
                subprocess.Popen(f'start {exe_name}', shell=True)
                return {'status': 'success', 'message': f'Opening {app_name.capitalize()}'}

        # 3. Audio & Volume Controls
        if any(w in text for w in ['mute', 'moot', 'mut', 'unmute']):
            print("  -> Executing: Muting/Unmuting Audio...")
            if self.sys:
                current_vol = self.sys.get_volume()
                new_vol = 0.5 if current_vol == 0.0 else 0.0
                self.sys.set_volume(new_vol)
            return {'status': 'success', 'message': 'Muted audio'}

        if any(w in text for w in ['volume full', 'max volume', 'full volume']):
            print("  -> Executing: Setting Volume to 100%...")
            if self.sys:
                self.sys.set_volume(1.0)
            return {'status': 'success', 'message': 'Volume set to 100 percent'}

        if any(w in text for w in ['volume up', 'increase volume', 'raise volume', 'louder', 'volume high']):
            print("  -> Executing: Increasing Volume...")
            if self.sys:
                current = self.sys.get_volume()
                self.sys.set_volume(min(1.0, current + 0.15))
            return {'status': 'success', 'message': 'Volume increased'}

        if any(w in text for w in ['volume down', 'decrease volume', 'lower volume', 'reduce volume', 'quieter']):
            print("  -> Executing: Decreasing Volume...")
            if self.sys:
                current = self.sys.get_volume()
                self.sys.set_volume(max(0.0, current - 0.15))
            return {'status': 'success', 'message': 'Volume decreased'}

        # 4. Media & System Controls
        if pyautogui:
            if any(w in text for w in ['play', 'pause']):
                print("  -> Executing: Play/Pause key...")
                pyautogui.press('playpause')
                return {'status': 'success', 'message': 'Toggled Play Pause'}

            if 'next' in text:
                print("  -> Executing: Next Track...")
                pyautogui.press('nexttrack')
                return {'status': 'success', 'message': 'Next Track'}

            if 'previous' in text:
                print("  -> Executing: Previous Track...")
                pyautogui.press('prevtrack')
                return {'status': 'success', 'message': 'Previous Track'}

            if any(w in text for w in ['screenshot', 'screen shot', 'capture screen', 'snip']):
                print("  -> Executing: Taking Screenshot...")
                pyautogui.hotkey('win', 'prtscr')
                return {'status': 'success', 'message': 'Screenshot captured'}

            if any(w in text for w in ['desktop', 'minimize all', 'minimise']):
                print("  -> Executing: Showing Desktop...")
                pyautogui.hotkey('win', 'd')
                return {'status': 'success', 'message': 'Showing Desktop'}

            if 'close window' in text:
                print("  -> Executing: Closing Window...")
                pyautogui.hotkey('alt', 'f4')
                return {'status': 'success', 'message': 'Closed window'}

        # 5. Battery Status
        if 'battery' in text:
            battery = psutil.sensors_battery()
            if battery:
                percent = int(battery.percent)
                plugged = "plugged in" if battery.power_plugged else "on battery"
                msg = f'Battery is at {percent} percent and {plugged}'
                print(f"  -> Executing: {msg}")
                return {'status': 'success', 'message': msg}

        # 6. Exit / Stop Assistant
        if any(w in text for w in ['stop assistant', 'exit assistant', 'quit assistant', 'stop system']):
            print("\n[INFO] Stop command received from voice. Exiting assistant...")
            os._exit(0)

        # 7. Lock Screen
        if 'lock' in text:
            print("  -> Executing: Locking Windows...")
            os.system('rundll32.exe user32.dll,LockWorkStation')
            return {'status': 'success', 'message': 'Locking screen'}

        print(f"  ⚠️ [NO MATCH]: '{text}' did not match any predefined voice command.")
        return {'status': 'unrecognized', 'message': ''}
