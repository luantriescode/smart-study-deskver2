import os
from dotenv import load_dotenv
load_dotenv()


RELAY_PIN = 17 

CAMERA_INDEX = 0
CAMERA_WIDTH  = 160  # Hạ xuống mức thấp nhất để tránh timeout
CAMERA_HEIGHT = 120
CAMERA_FPS    = 21  # Giảm FPS để ổn định dòng điện
CAMERA_FOURCC = "MJPG"
ROI_X, ROI_Y = 20, 20
ROI_W, ROI_H = 120, 80
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
WEB_HOST = os.getenv("WEB_HOST", "192.168.1.8")
WEB_PORT = 5000