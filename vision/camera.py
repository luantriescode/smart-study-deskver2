"""
VISION/CAMERA.PY - Camera Handler
====================================
Quản lý:
  - Mở/đóng webcam USB
  - Đọc frame realtime
  - Resize frame
  - Frame buffer

CHANGELOG:
  v1.1 - Fix camera Jieli DV20 trên Pi B+:
         • Ép MJPG format (YUYV timeout hoàn toàn)
         • Đọc fourcc/buffer/warmup từ config
         • Suppress "Corrupt JPEG" warning (warning level, không ảnh hưởng frame)
         • Thực tế ~15fps ở 320x240 MJPG
"""

import cv2
import logging
import os
import numpy as np

logger = logging.getLogger(__name__)

# Suppress OpenCV's "Corrupt JPEG data" stderr spam
# Đây là warning của libjpeg, frame vẫn decode được bình thường
os.environ.setdefault("OPENCV_LOG_LEVEL", "ERROR")


class Camera:
    """Quản lý camera USB"""

    def __init__(self, device_id=0, width=320, height=240, fps=30,
                 fourcc="MJPG", buffer_size=1, warmup_frames=10):
        """
        Khởi tạo camera

        Args:
            device_id    : ID camera (0 = USB webcam đầu tiên)
            width        : Chiều rộng capture
            height       : Chiều cao capture
            fps          : Target FPS (thực tế ~15fps trên Pi B+ với MJPG 320x240)
            fourcc       : Pixel format — "MJPG" bắt buộc cho camera DV20
                           (YUYV bị V4L2 timeout hoàn toàn trên Pi B+)
            buffer_size  : V4L2 buffer size = 1 để tránh stale frames
            warmup_frames: Số frame bỏ qua khi khởi động
        """
        self.device_id     = device_id
        self.target_width  = width
        self.target_height = height
        self.target_fps    = fps
        self.fourcc_str    = fourcc
        self.buffer_size   = buffer_size
        self.warmup_frames = warmup_frames

        # Mở camera với V4L2 backend (tường minh, tránh GStreamer warning)
        self.cap = cv2.VideoCapture(device_id, cv2.CAP_V4L2)

        if not self.cap.isOpened():
            raise RuntimeError(f"Không mở được camera {device_id}")

        # ── Set pixel format trước khi set resolution ──────────
        # BẮT BUỘC set MJPG; nếu để mặc định OpenCV sẽ dùng YUYV → timeout
        fourcc_code = cv2.VideoWriter_fourcc(*fourcc)
        self.cap.set(cv2.CAP_PROP_FOURCC, fourcc_code)

        # ── Set resolution & FPS ────────────────────────────────
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,  width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.cap.set(cv2.CAP_PROP_FPS,          fps)

        # ── Buffer nhỏ để tránh frame cũ ────────────────────────
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, buffer_size)

        # ── Đọc lại thông số thực tế ────────────────────────────
        self.actual_width  = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.actual_fps    = self.cap.get(cv2.CAP_PROP_FPS)

        logger.info(
            f"Camera opened: {self.actual_width}x{self.actual_height} "
            f"@ {self.actual_fps:.0f}fps [{fourcc}] "
            f"(thực tế ~15fps trên Pi B+)"
        )

        # ── Warm-up: bỏ qua vài frame đầu corrupt ───────────────
        self._warmup()

        # Frame buffer
        self.last_frame  = None
        self.frame_count = 0

    # ------------------------------------------------------------------
    # INTERNAL
    # ------------------------------------------------------------------

    def _warmup(self):
        """Đọc bỏ các frame đầu để camera ổn định"""
        logger.debug(f"Camera warm-up: đọc bỏ {self.warmup_frames} frames...")
        for _ in range(self.warmup_frames):
            self.cap.read()
        logger.debug("Camera warm-up done")

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    def read(self):
        """
        Đọc frame từ camera

        Returns:
            (ret, frame) — ret=True nếu thành công, frame=numpy array BGR
        """
        ret, frame = self.cap.read()

        if ret and frame is not None:
            self.last_frame   = frame
            self.frame_count += 1

        return ret, frame

    def resize_frame(self, frame, width=None, height=None):
        """
        Resize frame

        Args:
            frame : Input frame
            width : Target width  (default: config.FRAME_WIDTH)
            height: Target height (default: config.FRAME_HEIGHT)

        Returns:
            Resized frame, hoặc frame gốc nếu đã đúng kích thước
        """
        if frame is None:
            return None

        # Nếu không truyền width/height → dùng giá trị từ config
        try:
            import config
            width  = width  or config.FRAME_WIDTH
            height = height or config.FRAME_HEIGHT
        except ImportError:
            width  = width  or 320
            height = height or 240

        # Nếu đã đúng kích thước → không resize (tiết kiệm CPU)
        h, w = frame.shape[:2]
        if w == width and h == height:
            return frame

        return cv2.resize(frame, (width, height), interpolation=cv2.INTER_LINEAR)

    def crop_roi(self, frame, roi):
        """
        Crop Region of Interest

        Args:
            frame: Input frame
            roi  : (x, y, w, h)

        Returns:
            Cropped frame
        """
        if frame is None:
            return None

        x, y, w, h   = roi
        h_f, w_f     = frame.shape[:2]

        x = max(0, min(x, w_f - 1))
        y = max(0, min(y, h_f - 1))
        w = min(w, w_f - x)
        h = min(h, h_f - y)

        return frame[y:y+h, x:x+w]

    def draw_roi(self, frame, roi, color=(0, 255, 0), thickness=2):
        """Vẽ ROI rectangle lên frame"""
        if frame is None:
            return None

        frame_copy = frame.copy()
        x, y, w, h = roi

        cv2.rectangle(frame_copy, (x, y), (x+w, y+h), color, thickness)
        cv2.putText(
            frame_copy, "ROI",
            (x + 5, y + 20),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1
        )
        return frame_copy

    def to_gray(self, frame):
        """Convert BGR → grayscale"""
        if frame is None:
            return None
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    def to_hsv(self, frame):
        """Convert BGR → HSV"""
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
            "device_id"  : self.device_id,
            "resolution" : f"{self.actual_width}x{self.actual_height}",
            "fourcc"     : self.fourcc_str,
            "target_fps" : self.target_fps,
            "actual_fps" : self.actual_fps,
            "frame_count": self.frame_count,
        }

    # Context manager
    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.release()


# ============================================
# STANDALONE TEST
# ============================================

def test_camera():
    """Test camera với cấu hình thực tế"""
    import time

    print("🎥 Testing Camera (MJPG fix)...")

    try:
        import config
        cam = Camera(
            device_id    = config.CAMERA_INDEX,
            width        = config.CAMERA_WIDTH,
            height       = config.CAMERA_HEIGHT,
            fps          = config.CAMERA_FPS,
            fourcc       = config.CAMERA_FOURCC,
            buffer_size  = config.CAMERA_BUFFER_SIZE,
            warmup_frames= config.CAMERA_WARMUP_FRAMES,
        )
    except ImportError:
        # Chạy standalone không có config
        cam = Camera()

    print(f"✅ Camera info: {cam.get_info()}")

    # Đọc 50 frames và đo FPS thực tế
    success = 0
    start   = time.time()

    for i in range(50):
        ret, frame = cam.read()
        if ret and frame is not None:
            success += 1
        else:
            print(f"  ⚠️  Frame {i}: FAILED")

    elapsed    = time.time() - start
    actual_fps = success / elapsed if elapsed > 0 else 0

    print(f"\n  Success    : {success}/50")
    print(f"  Actual FPS : {actual_fps:.1f}")
    if cam.last_frame is not None:
        print(f"  Frame shape: {cam.last_frame.shape}")

    cam.release()

    # Đánh giá
    if success >= 45 and actual_fps >= 10:
        print("\n✅ Camera test PASSED — sẵn sàng cho STEP 4!")
    elif success >= 40:
        print("\n⚠️  Camera PARTIAL — hoạt động nhưng không ổn định")
    else:
        print("\n❌ Camera test FAILED")


if __name__ == "__main__":
    test_camera()