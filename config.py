"""
CONFIG.PY - Cấu hình toàn hệ thống
===============================================
Quản lý:
  - GPIO pin cho relay
  - Camera ROI (Region of Interest)
  - Timer delay logic
  - Telegram bot token
  - Các threshold AI
"""

import os
from pathlib import Path

# ============================================
# 1️⃣ HARDWARE - GPIO CONFIGURATION
# ============================================

# Relay control pin (BCM numbering)
RELAY_PIN = 17  # GPIO 17 (Pin 11 trên RPi B+)
RELAY_GPIO_MODE = "BCM"  # Dùng BCM numbering

# LED status indicator (optional)
LED_PIN = 27  # GPIO 27 để báo trạng thái

# ============================================
# 2️⃣ CAMERA CONFIGURATION
# ============================================

CAMERA_INDEX = 0  # USB webcam là device 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30

# Resize nhỏ để giảm CPU
FRAME_WIDTH = 320
FRAME_HEIGHT = 240

# Region of Interest (ROI) - vùng phát hiện người
# Định dạng: (x, y, w, h) - top-left corner + width, height
ROI_X = 50
ROI_Y = 50
ROI_W = 220  # 320 - 100
ROI_H = 140  # 240 - 100

# ============================================
# 3️⃣ MOTION DETECTION
# ============================================

# Background subtraction threshold
MOTION_THRESHOLD = 500  # Pixels thay đổi để trigger
MOTION_MIN_AREA = 100   # Diện tích tối thiểu (px²)

# ============================================
# 4️⃣ FACE & EYE DETECTION
# ============================================

# Haar cascade paths (có sẵn trong OpenCV)
FACE_CASCADE = "haarcascade_frontalface_default.xml"
EYE_CASCADE = "haarcascade_eye.xml"

# Eye closure detection
EYE_CLOSED_THRESHOLD = 0.3  # Ratio mắt đóng
EYE_CLOSED_FRAMES = 150     # ~5s ở 30fps (150/30 = 5 giây)

# ============================================
# 5️⃣ POSTURE DETECTION
# ============================================

# Head angle threshold (độ)
HEAD_DOWN_THRESHOLD = 20  # Cúi quá 20° → cảnh báo
HEAD_UP_THRESHOLD = -15   # Ngẩng quá 15° → cảnh báo

# ============================================
# 6️⃣ STATE MACHINE TIMERS
# ============================================

# Khi người rời đi → chờ 10s rồi tắt đèn
PERSON_LOST_DELAY = 10  # seconds

# Study session timeout (vd: 1 giờ không có hoạt động → reset)
SESSION_TIMEOUT = 3600  # seconds

# ============================================
# 7️⃣ TELEGRAM CONFIGURATION
# ============================================

TELEGRAM_TOKEN = os.getenv(
    "TELEGRAM_TOKEN",
    "YOUR_BOT_TOKEN_HERE"  # Replace với token thật từ @BotFather
)

TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID",
    "YOUR_CHAT_ID_HERE"  # Replace với chat ID của bạn
)

# Alert settings
TELEGRAM_ALERT_COOLDOWN = 30  # seconds - tránh spam cảnh báo
SEND_PHOTO_ON_ALERT = True

# ============================================
# 8️⃣ WEB DASHBOARD
# ============================================

WEB_HOST = "0.0.0.0"  # Cho phép truy cập từ bất kỳ IP nào
WEB_PORT = 5000
WEB_DEBUG = False  # Production = False

# ============================================
# 9️⃣ LOGGING
# ============================================

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "study_system.log"
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR

# ============================================
# 🔟 PATHS
# ============================================

PROJECT_ROOT = Path(__file__).parent
VISION_DIR = PROJECT_ROOT / "vision"
CORE_DIR = PROJECT_ROOT / "core"
HARDWARE_DIR = PROJECT_ROOT / "hardware"
COMMUNICATION_DIR = PROJECT_ROOT / "communication"
WEB_DIR = PROJECT_ROOT / "web"

# Temp folder cho screenshots
TEMP_DIR = PROJECT_ROOT / "temp"
TEMP_DIR.mkdir(exist_ok=True)

# ============================================
# 1️⃣1️⃣ DEBUG FLAGS
# ============================================

DEBUG_MODE = False  # Bật để xem log chi tiết
SHOW_PREVIEW = True  # Hiển thị camera preview (nếu GUI)
SIMULATE_HARDWARE = False  # Chạy không có GPIO thật (test)

# ============================================
# VALIDATION
# ============================================

def validate_config():
    """Kiểm tra config có hợp lệ không"""
    errors = []
    
    # Check GPIO
    if RELAY_PIN < 0:
        errors.append("RELAY_PIN phải >= 0")
    
    # Check ROI
    if ROI_W > FRAME_WIDTH or ROI_H > FRAME_HEIGHT:
        errors.append("ROI vượt quá kích thước frame")
    
    # Check Telegram
    if TELEGRAM_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("⚠️  WARNING: Telegram token chưa được set. Cảnh báo sẽ KHÔNG gửi được.")
    
    # Check logs
    try:
        LOG_DIR.mkdir(exist_ok=True)
    except Exception as e:
        errors.append(f"Không thể tạo LOG_DIR: {e}")
    
    if errors:
        print("❌ CONFIG ERRORS:")
        for err in errors:
            print(f"  - {err}")
        return False
    
    print("✅ Config validated successfully")
    return True


if __name__ == "__main__":
    validate_config()
    print("\n📋 Active Configuration:")
    print(f"  Relay PIN: {RELAY_PIN}")
    print(f"  Camera: {CAMERA_WIDTH}x{CAMERA_HEIGHT} → {FRAME_WIDTH}x{FRAME_HEIGHT}")
    print(f"  ROI: ({ROI_X}, {ROI_Y}, {ROI_W}, {ROI_H})")
    print(f"  Telegram: {'✅' if TELEGRAM_TOKEN != 'YOUR_BOT_TOKEN_HERE' else '❌'}")
