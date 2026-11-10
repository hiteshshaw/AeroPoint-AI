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

# Access Profiles: Adaptive Operating Modes
ACCESS_PROFILES = {
    "DEFAULT": {
        "DWELL_TIME_SEC": 1.0,
        "DWELL_RADIUS_NORM": 0.03,
        "SMOOTHING_FACTOR": 0.5,
        "ACTIVE_ZONE_MARGIN": 0.12,
        "CAMERA_ENABLED": True,
        "VERBAL_CONFIRMATION": False
    },
    "MOTOR_SUPPORT": {
        "DWELL_TIME_SEC": 1.2,
        "DWELL_RADIUS_NORM": 0.045, # Wider tremor tolerance
        "SMOOTHING_FACTOR": 0.7,    # Extra jitter smoothing
        "ACTIVE_ZONE_MARGIN": 0.15,
        "CAMERA_ENABLED": True,
        "VERBAL_CONFIRMATION": True
    },
    "HANDS_BUSY": {
        "DWELL_TIME_SEC": 1.0,
        "DWELL_RADIUS_NORM": 0.03,
        "SMOOTHING_FACTOR": 0.5,
        "ACTIVE_ZONE_MARGIN": 0.12,
        "CAMERA_ENABLED": False,    # Vision paused, 100% voice priority
        "VERBAL_CONFIRMATION": False
    },
    "LOW_FATIGUE": {
        "DWELL_TIME_SEC": 0.9,
        "DWELL_RADIUS_NORM": 0.025,
        "SMOOTHING_FACTOR": 0.6,
        "ACTIVE_ZONE_MARGIN": 0.18, # Tighter box for micro-movements
        "CAMERA_ENABLED": True,
        "VERBAL_CONFIRMATION": False
    },
    "STERILE_ENVIRONMENT": {
        "DWELL_TIME_SEC": 1.0,
        "DWELL_RADIUS_NORM": 0.03,
        "SMOOTHING_FACTOR": 0.5,
        "ACTIVE_ZONE_MARGIN": 0.12,
        "CAMERA_ENABLED": True,     # Touch prohibited, swipe & voice only
        "VERBAL_CONFIRMATION": True
    }
}

ACTIVE_PROFILE = "DEFAULT"

def apply_profile(profile_name: str) -> bool:
    global ACTIVE_PROFILE, DWELL_TIME_SEC, DWELL_RADIUS_NORM, SMOOTHING_FACTOR, ACTIVE_ZONE_MARGIN
    name = profile_name.upper().replace(" ", "_")
    if name in ACCESS_PROFILES:
        ACTIVE_PROFILE = name
        cfg = ACCESS_PROFILES[name]
        DWELL_TIME_SEC = cfg["DWELL_TIME_SEC"]
        DWELL_RADIUS_NORM = cfg["DWELL_RADIUS_NORM"]
        SMOOTHING_FACTOR = cfg["SMOOTHING_FACTOR"]
        ACTIVE_ZONE_MARGIN = cfg["ACTIVE_ZONE_MARGIN"]
        print(f"  🎯 [ACCESS PROFILE APPLIED]: '{name}'")
        return True
    return False

# Power Management
AUTO_SLEEP_TIMEOUT_SEC = 10  # Seconds of inactivity before sleeping camera
AUDIO_ENERGY_THRESHOLD = 300 # Audio activity trigger threshold


