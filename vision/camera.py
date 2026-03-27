# vision/camera.py
import cv2
import time
import logging
import os

logger = logging.getLogger(__name__)

class Camera:
    def __init__(self, device_id=0, width=160, height=120, fps=10, fourcc="MJPG"):
        self.device_id = device_id
        # Sử dụng backend CAP_V4L2 để ổn định driver Linux
        self.cap = cv2.VideoCapture(device_id, cv2.CAP_V4L2)
        
        if not self.cap.isOpened():
            raise RuntimeError(f"❌ Không thể mở camera {device_id}")

        # Tăng thời gian chờ buffer cho các dòng Pi yếu
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*fourcc))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.cap.set(cv2.CAP_PROP_FPS, fps)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        # Đợi phần cứng ổn định (Rất quan trọng cho C270)
        time.sleep(2.0)
        self._warmup()

    def _warmup(self):
        # Đọc bỏ các frame rác ban đầu
        for _ in range(10):
            self.cap.read()

    def read(self):
        # Cơ chế grab/retrieve để xóa sạch buffer cũ, tránh hình bị trễ
        self.cap.grab()
        ret, frame = self.cap.retrieve()
        return ret, frame

    def draw_roi(self, frame, roi):
        x, y, w, h = roi
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        return frame

    def release(self):
        if self.cap:
            self.cap.release()