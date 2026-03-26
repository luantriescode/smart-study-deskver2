import os
from pathlib import Path
from dotenv import load_dotenv

# Load các biến từ file .env
load_dotenv()

# ============================================
# 1️⃣ HARDWARE - GPIO CONFIGURATION
# ============================================
RELAY_PIN = 17 
RELAY_GPIO_MODE = "BCM"

# ============================================
# 2️⃣ CAMERA CONFIGURATION (Fixed for Pi B+)
# ============================================
CAMERA_INDEX = 0
CAMERA_WIDTH  = 320
CAMERA_HEIGHT = 240
CAMERA_FPS    = 30
CAMERA_FOURCC = "MJPG"
FRAME_WIDTH  = 320
FRAME_HEIGHT = 240
CAMERA_BUFFER_SIZE = 1
CAMERA_WARMUP_FRAMES = 10

# ROI - vùng phát hiện người [cite: 15, 18]
ROI_X, ROI_Y = 50, 50
ROI_W, ROI_H = 220, 140

# ============================================
# 3️⃣ AI THRESHOLDS [cite: 12, 18]
# ============================================
MOTION_THRESHOLD = 500
EYE_CLOSED_FRAMES = 75  # ~5s @ 15fps [cite: 5]
PERSON_LOST_DELAY = 10  # [cite: 12]

# ============================================
# 4️⃣ SENSITIVE DATA (Đọc từ .env) 
# ============================================
# Nếu không tìm thấy trong .env, sẽ để trống hoặc báo lỗi
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

WEB_HOST = os.getenv("WEB_HOST", "0.0.0.0")
WEB_PORT = int(os.getenv("WEB_PORT", 5000))

# ============================================
# 5️⃣ PATHS & LOGGING
# ============================================
PROJECT_ROOT = Path(__file__).parent
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

def validate_config():
    """Kiểm tra config quan trọng"""
    if not TELEGRAM_TOKEN or "AAEuNbl" in TELEGRAM_TOKEN:
        print("⚠️  WARNING: Telegram Token chưa được cấu hình đúng trong .env")
    else:
        print("✅ Telegram Config: LOADED from .env")
    return True

if __name__ == "__main__":
    validate_config()