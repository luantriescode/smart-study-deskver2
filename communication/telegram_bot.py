import os
import requests
import cv2
from dotenv import load_dotenv

# Load biến môi trường từ file .env ở thư mục gốc
load_dotenv()

class TelegramBot:
    def __init__(self):
        # Gọi biến môi trường 
        self.token = os.getenv("TELEGRAM_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    def send_alert(self, message, frame=None):
        """Gửi thông báo văn bản và hình ảnh bằng chứng [cite: 13, 15]"""
        if not self.token or not self.chat_id:
            print("❌ Lỗi: Chưa cấu hình Token hoặc Chat ID trong .env")
            return

        try:
            # Gửi tin nhắn Text
            requests.post(f"{self.base_url}/sendMessage", 
                         data={"chat_id": self.chat_id, "text": message}, timeout=5)
            
            # Gửi ảnh (nén JPEG để tiết kiệm băng thông Pi B+) [cite: 3, 13]
            if frame is not None:
                _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
                files = {'photo': ('alert.jpg', buffer.tobytes())}
                requests.post(f"{self.base_url}/sendPhoto", 
                             data={"chat_id": self.chat_id}, files=files, timeout=10)
                print(f"📩 Đã gửi cảnh báo Telegram: {message}")
        except Exception as e:
            print(f"⚠️ Telegram Alert Error: {e}")