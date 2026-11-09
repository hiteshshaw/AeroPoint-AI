"""
OS Actions: Mouse, Volume, Brightness and Keyboard Controls
Optimized for low-latency and smooth execution.
"""
import math

try:
    import pyautogui
    pyautogui.FAILSAFE = False
    pyautogui.PAUSE = 0.001
except ImportError:
    pyautogui = None

try:
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    _devices = AudioUtilities.GetSpeakers()
    _interface = _devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume_control = cast(_interface, POINTER(IAudioEndpointVolume))
except Exception:
    volume_control = None

try:
    import screen_brightness_control as sbc
except Exception:
    sbc = None


class SystemController:
    def __init__(self):
        if pyautogui:
            self.screen_width, self.screen_height = pyautogui.size()
        else:
            self.screen_width, self.screen_height = 1920, 1080
            
        self.prev_x, self.prev_y = self.screen_width // 2, self.screen_height // 2
        self.is_dragging = False

    def move_cursor(self, norm_x: float, norm_y: float, smoothing: float = 0.5):
        """Move cursor with Exponential Moving Average (EMA) smoothing and relaxed active zone."""
        if not pyautogui:
            return

        import config
        margin = getattr(config, 'ACTIVE_ZONE_MARGIN', 0.12)
        # Remap from inner active zone to full screen so user doesn't have to stretch hand
        mapped_x = max(0.0, min(1.0, (norm_x - margin) / max(0.01, 1.0 - 2 * margin)))
        mapped_y = max(0.0, min(1.0, (norm_y - margin) / max(0.01, 1.0 - 2 * margin)))

        target_x = mapped_x * self.screen_width
        target_y = mapped_y * self.screen_height

        smooth_x = self.prev_x + (target_x - self.prev_x) * (1 - smoothing)
        smooth_y = self.prev_y + (target_y - self.prev_y) * (1 - smoothing)

        pyautogui.moveTo(smooth_x, smooth_y)
        self.prev_x, self.prev_y = smooth_x, smooth_y

    def click(self, button: str = 'left'):
        if pyautogui:
            pyautogui.click(button=button)

    def double_click(self):
        if pyautogui:
            pyautogui.doubleClick()

    def mouse_down(self, button: str = 'left'):
        if pyautogui and not self.is_dragging:
            pyautogui.mouseDown(button=button)
            self.is_dragging = True

    def mouse_up(self, button: str = 'left'):
        if pyautogui and self.is_dragging:
            pyautogui.mouseUp(button=button)
            self.is_dragging = False

    def press_key(self, key: str):
        if pyautogui:
            pyautogui.press(key)

    def scroll(self, amount: int):
        """Positive amount scrolls UP, negative scrolls DOWN."""
        if pyautogui:
            pyautogui.scroll(amount)

    def set_volume(self, percent: float):
        """Percent: 0.0 to 1.0"""
        if volume_control:
            percent = max(0.0, min(1.0, percent))
            volume_control.SetMasterVolumeLevelScalar(percent, None)

    def get_volume(self) -> float:
        if volume_control:
            return volume_control.GetMasterVolumeLevelScalar()
        return 0.5

    def set_brightness(self, percent: int):
        """Percent: 0 to 100"""
        if sbc:
            try:
                sbc.set_brightness(max(0, min(100, percent)))
            except Exception:
                pass

