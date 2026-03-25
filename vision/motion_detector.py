"""
VISION/MOTION_DETECTOR.PY - Motion & Person Detection
========================================================
Quản lý:
  - Background subtraction
  - Motion detection trong ROI
  - Filtering & morphology
"""

import cv2
import numpy as np
import logging

import config

logger = logging.getLogger(__name__)


class MotionDetector:
    """Phát hiện chuyển động/người trong ROI"""
    
    def __init__(self, history=30):
        """
        Khởi tạo motion detector
        
        Args:
            history: Số frame dùng để build background model
        """
        # Background subtractor
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            detectShadows=True,
            varThreshold=16
        )
        
        self.history = history
        self.frame_count = 0
        self.warmup_frames = history
        
        # Morphological kernel
        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        
        logger.info(f"MotionDetector initialized (history={history} frames)")
    
    def detect(self, frame, roi=None):
        """
        Phát hiện motion trong frame (hoặc ROI)
        
        Args:
            frame: Input frame (BGR)
            roi: (x, y, w, h) - nếu None thì detect toàn frame
        
        Returns:
            (is_person_detected, motion_mask)
                is_person_detected: bool
                motion_mask: Binary mask của motion
        """
        if frame is None:
            return False, None
        
        self.frame_count += 1
        
        # Crop ROI nếu có
        if roi is not None:
            x, y, w, h = roi
            h_frame, w_frame = frame.shape[:2]
            
            # Clamp ROI
            x = max(0, min(x, w_frame - 1))
            y = max(0, min(y, h_frame - 1))
            w = min(w, w_frame - x)
            h = min(h, h_frame - y)
            
            frame_roi = frame[y:y+h, x:x+w]
        else:
            frame_roi = frame
        
        # Background subtraction
        fg_mask = self.bg_subtractor.apply(frame_roi)
        
        # Remove shadows (MOG2 puts shadows as 128)
        fg_mask[fg_mask == 127] = 0  # 127 = shadow
        
        # Morphological operations
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, self.kernel, iterations=1)
        fg_mask = cv2.dilate(fg_mask, self.kernel, iterations=2)
        
        # Count non-zero pixels
        motion_pixels = cv2.countNonZero(fg_mask)
        
        # Warmup phase (skip first few frames)
        if self.frame_count < self.warmup_frames:
            return False, fg_mask
        
        # Threshold check
        is_person_detected = motion_pixels > config.MOTION_THRESHOLD
        
        return is_person_detected, fg_mask
    
    def detect_contours(self, frame, roi=None, min_area=None):
        """
        Phát hiện motion + trả về contours
        
        Args:
            frame: Input frame
            roi: ROI tuple
            min_area: Diện tích tối thiểu (default: config.MOTION_MIN_AREA)
        
        Returns:
            (is_detected, contours, mask)
        """
        if min_area is None:
            min_area = config.MOTION_MIN_AREA
        
        is_detected, fg_mask = self.detect(frame, roi)
        
        if not is_detected:
            return False, [], fg_mask
        
        # Find contours
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter by min area
        large_contours = [c for c in contours if cv2.contourArea(c) > min_area]
        
        is_detected = len(large_contours) > 0
        
        return is_detected, large_contours, fg_mask
    
    def draw_motion(self, frame, fg_mask, roi=None, color=(0, 255, 0)):
        """
        Vẽ motion visualization lên frame
        
        Args:
            frame: Input frame
            fg_mask: Foreground mask
            roi: ROI tuple (để vẽ ROI boundary)
            color: BGR color
        
        Returns:
            Annotated frame
        """
        if frame is None:
            return None
        
        frame_copy = frame.copy()
        
        # Convert mask to 3-channel
        if len(fg_mask.shape) == 2:
            mask_3ch = cv2.cvtColor(fg_mask, cv2.COLOR_GRAY2BGR)
        else:
            mask_3ch = fg_mask
        
        # Overlay motion
        frame_copy = cv2.addWeighted(frame_copy, 0.7, mask_3ch, 0.3, 0)
        
        # Draw ROI if provided
        if roi is not None:
            x, y, w, h = roi
            cv2.rectangle(frame_copy, (x, y), (x+w, y+h), color, 2)
        
        # Add text
        motion_pixels = cv2.countNonZero(fg_mask)
        is_detected = motion_pixels > config.MOTION_THRESHOLD
        
        status = "DETECTED" if is_detected else "EMPTY"
        status_color = (0, 255, 0) if is_detected else (0, 0, 255)
        
        cv2.putText(
            frame_copy,
            f"Motion: {status} ({motion_pixels}px)",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            status_color,
            2
        )
        
        return frame_copy
    
    def reset(self):
        """Reset background model"""
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            detectShadows=True,
            varThreshold=16
        )
        self.frame_count = 0
        logger.info("MotionDetector reset")


# ============================================
# STANDALONE TEST
# ============================================

def test_motion_detector():
    """Test motion detection"""
    import time
    
    print("🎬 Testing Motion Detector...")
    
    try:
        from vision.camera import Camera
        
        camera = Camera(
            width=config.CAMERA_WIDTH,
            height=config.CAMERA_HEIGHT
        )
        
        detector = MotionDetector()
        
        roi = (config.ROI_X, config.ROI_Y, config.ROI_W, config.ROI_H)
        
        print("Reading 30 frames to build background...")
        for i in range(30):
            ret, frame = camera.read()
            if ret:
                resized = camera.resize_frame(frame, config.FRAME_WIDTH, config.FRAME_HEIGHT)
                is_person, mask = detector.detect(resized, roi)
                print(f"  Frame {i}: Person={is_person}")
        
        print("✅ Motion detector test passed")
        
        camera.release()
    
    except Exception as e:
        print(f"❌ Motion detector test failed: {e}")


if __name__ == "__main__":
    test_motion_detector()
