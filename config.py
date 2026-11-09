"""
Project Configuration: Lightweight & Battery-Optimized Settings
"""
import os
import tempfile

# Suppress Matplotlib cache warnings
os.environ['MPLCONFIGDIR'] = os.path.join(tempfile.gettempdir(), 'mpl_cache')

# Camera & Vision Settings
CAMERA_INDEX = 0
CAMERA_WIDTH = 640       # 480p equivalent for minimum CPU load
CAMERA_HEIGHT = 480
TARGET_FPS = 25          # Smooth tracking without overheating
IDLE_FPS = 5             # Battery saver when hand is not in frame
SHOW_CAMERA_FEED = True  # Set to False for stealth background mode (no popup window)

# Gesture Sensitivity & Smoothing
SMOOTHING_FACTOR = 0.5   # Exponential Moving Average for jitter-free cursor
CLICK_DISTANCE_THRESHOLD = 0.05  # Normalized distance between thumb and index tip
DRAG_HOLD_TIME_SEC = 0.4 # Hold pinch longer than this to start dragging
SCROLL_SPEED = 20
ACTIVE_ZONE_MARGIN = 0.12 # Relaxed hand box: no need to stretch hand to camera edge

# Accessibility: Dwell Click (Hover-to-Click for Tremor/Motor Impairment)
ENABLE_DWELL_CLICK = True
DWELL_TIME_SEC = 1.0     # Time in seconds holding pointer still before auto-clicking
DWELL_RADIUS_NORM = 0.03 # Normalized motion tolerance window for tremor filtering
DWELL_COOLDOWN_SEC = 1.2 # Cooldown after dwell click before another dwell click can fire

# Power Management
AUTO_SLEEP_TIMEOUT_SEC = 10  # Seconds of inactivity before sleeping camera
AUDIO_ENERGY_THRESHOLD = 300 # Audio activity trigger threshold


