"""
VISION/CAMERA.PY - Camera Handler
====================================
Quản lý:
  - Mở/đóng webcam USB
  - Đọc frame realtime
  - Resize frame
  - Frame buffer
"""

import cv2
import logging
import numpy as np

logger = logging.getLogger(__name__)


class Camera:
    """Quản lý camera"""
    
    def __init__(self, device_id=0, width=640, height=480, fps=30):
        """
        Khởi tạo camera
        
        Args:
            device_id: ID của camera (0 = USB webcam đầu tiên)
            width: Chiều rộng frame gốc
            height: Chiều cao frame gốc
            fps: Frame per second (target)
        """
        self.device_id = device_id
        self.target_width = width
        self.target_height = height
        self.target_fps = fps
        
        # Mở camera
        self.cap = cv2.VideoCapture(device_id)
        
        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open camera {device_id}")
        
        # Set resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.cap.set(cv2.CAP_PROP_FPS, fps)
        
        # Get actual resolution
        self.actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
        
        logger.info(
            f"Camera initialized: {self.actual_width}x{self.actual_height} "
            f"@ {self.actual_fps} FPS"
        )
        
        # Frame buffer
        self.last_frame = None
        self.frame_count = 0
    
    def read(self):
        """
        Đọc frame từ camera
        
        Returns:
            (ret, frame) - ret=True if success, frame=numpy array (BGR)
        """
        ret, frame = self.cap.read()
        
        if ret:
            self.last_frame = frame
            self.frame_count += 1
        
        return ret, frame
    
    def resize_frame(self, frame, width=320, height=240):
        """
        Resize frame
        
        Args:
            frame: Input frame (numpy array)
            width: Target width
            height: Target height
        
        Returns:
            Resized frame
        """
        if frame is None:
            return None
        
        resized = cv2.resize(frame, (width, height), interpolation=cv2.INTER_LINEAR)
        return resized
    
    def crop_roi(self, frame, roi):
        """
        Crop Region of Interest (ROI)
        
        Args:
            frame: Input frame
            roi: (x, y, w, h) - top-left corner + width, height
        
        Returns:
            Cropped frame
        """
        if frame is None:
            return None
        
        x, y, w, h = roi
        h_frame, w_frame = frame.shape[:2]
        
        # Clamp to frame bounds
        x = max(0, min(x, w_frame - 1))
        y = max(0, min(y, h_frame - 1))
        w = min(w, w_frame - x)
        h = min(h, h_frame - y)
        
        return frame[y:y+h, x:x+w]
    
    def draw_roi(self, frame, roi, color=(0, 255, 0), thickness=2):
        """
        Vẽ ROI rectangle lên frame
        
        Args:
            frame: Input frame
            roi: (x, y, w, h)
            color: BGR color tuple
            thickness: Line thickness
        
        Returns:
            Frame with ROI drawn
        """
        if frame is None:
            return None
        
        frame_copy = frame.copy()
        x, y, w, h = roi
        
        # Draw rectangle
        cv2.rectangle(frame_copy, (x, y), (x+w, y+h), color, thickness)
        
        # Draw label
        cv2.putText(
            frame_copy,
            "ROI",
            (x + 5, y + 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            1
        )
        
        return frame_copy
    
    def to_gray(self, frame):
        """Convert BGR to grayscale"""
        if frame is None:
            return None
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    def to_hsv(self, frame):
        """Convert BGR to HSV"""
        if frame is None:
            return None
        return cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    def release(self):
        """Đóng camera"""
        if self.cap is not None:
            self.cap.release()
            logger.info("Camera released")
    
    def get_info(self):
        """Lấy thông tin camera"""
        return {
            "device_id": self.device_id,
            "resolution": f"{self.actual_width}x{self.actual_height}",
            "fps": self.actual_fps,
            "frame_count": self.frame_count
        }
    
    def __enter__(self):
        """Context manager support"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup"""
        self.release()


# ============================================
# STANDALONE TEST
# ============================================

def test_camera():
    """Test camera"""
    import config
    
    print("🎥 Testing Camera...")
    
    try:
        camera = Camera(
            width=config.CAMERA_WIDTH,
            height=config.CAMERA_HEIGHT,
            fps=config.CAMERA_FPS
        )
        
        print(f"✅ Camera info: {camera.get_info()}")
        
        # Read 10 frames
        for i in range(10):
            ret, frame = camera.read()
            if ret:
                print(f"  Frame {i}: {frame.shape}")
            else:
                print(f"  Frame {i}: FAILED")
        
        camera.release()
        print("✅ Camera test passed")
    
    except Exception as e:
        print(f"❌ Camera test failed: {e}")


if __name__ == "__main__":
    test_camera()
