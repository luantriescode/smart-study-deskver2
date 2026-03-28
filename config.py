import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent
load_dotenv(PROJECT_ROOT / ".env")

# --- HARDWARE ---
RELAY_PIN = 17 

# --- CAMERA (Logitech C270) ---
CAMERA_INDEX = 0
CAMERA_WIDTH  = 160
CAMERA_HEIGHT = 120
CAMERA_FPS    = 10
CAMERA_FOURCC = "MJPG"

# --- ROI ---
ROI_X, ROI_Y = 20, 20
ROI_W, ROI_H = 120, 80

# --- DETECTION THRESHOLDS (Cần thiết cho MotionDetector) ---
MOTION_THRESHOLD = 500   # Ngưỡng diện tích chuyển động
PERSON_LOST_DELAY = 3   # Thời gian chờ tắt đèn (giây)

# --- NETWORK ---
WEB_HOST = os.getenv("WEB_HOST", "192.168.1.8")
WEB_PORT = os.getenv("WEB_PORT","5000")