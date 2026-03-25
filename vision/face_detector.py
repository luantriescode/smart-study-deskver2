"""
VISION/FACE_DETECTOR.PY - Face & Eye Detection
================================================
Quản lý:
  - Detect khuôn mặt (Haar cascade)
  - Detect mắt
  - Detect mắt đóng (ngủ gật)
"""

import cv2
import numpy as np
import logging

import config

logger = logging.getLogger(__name__)


class FaceDetector:
    """Phát hiện khuôn mặt và mắt"""
    
    def __init__(self):
        """Khởi tạo face detector"""
        # Load Haar cascades
        cascade_path = cv2.data.haarcascades
        
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        self.eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_eye.xml'
        )
        
        if self.face_cascade.empty():
            raise RuntimeError("Failed to load face cascade")
        
        if self.eye_cascade.empty():
            logger.warning("Eye cascade not loaded - sleep detection disabled")
        
        # Eye closure tracking
        self.eye_closed_counter = 0
        self.last_eye_status = False  # False = open, True = closed
        
        logger.info("FaceDetector initialized")
    
    def detect_faces(self, frame, scale_factor=1.3, min_neighbors=4):
        """
        Phát hiện khuôn mặt
        
        Args:
            frame: Input frame (BGR or Gray)
            scale_factor: Cascade scale factor
            min_neighbors: Minimum neighbors
        
        Returns:
            List of (x, y, w, h) tuples
        """
        if frame is None:
            return []
        
        # Convert to grayscale if needed
        if len(frame.shape) == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = frame
        
        # Equalize histogram (improve detection)
        gray = cv2.equalizeHist(gray)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=scale_factor,
            minNeighbors=min_neighbors,
            minSize=(30, 30)
        )
        
        return faces
    
    def detect_eyes_in_face(self, face_roi, scale_factor=1.1, min_neighbors=4):
        """
        Phát hiện mắt trong face region
        
        Args:
            face_roi: Face region (BGR or Gray)
            scale_factor: Cascade scale factor
            min_neighbors: Minimum neighbors
        
        Returns:
            List of (x, y, w, h) tuples (trong tọa độ face_roi)
        """
        if face_roi is None or face_roi.size == 0:
            return []
        
        # Convert to grayscale if needed
        if len(face_roi.shape) == 3:
            gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
        else:
            gray = face_roi
        
        # Detect eyes
        eyes = self.eye_cascade.detectMultiScale(
            gray,
            scaleFactor=scale_factor,
            minNeighbors=min_neighbors,
            minSize=(15, 15)
        )
        
        return eyes
    
    def is_eyes_closed(self, face_roi):
        """
        Kiểm tra mắt có đóng không
        
        Args:
            face_roi: Face region
        
        Returns:
            bool - True if eyes closed
        """
        if face_roi is None or face_roi.size == 0:
            return False
        
        # Detect eyes
        eyes = self.detect_eyes_in_face(face_roi)
        
        # Nếu không detect được mắt → mắt đóng
        if len(eyes) < 2:
            return True
        
        # Nếu detect được 2 mắt → mắt mở
        return False
    
    def detect_sleep(self, frame, face):
        """
        Phát hiện ngủ gật (mắt đóng quá lâu)
        
        Args:
            frame: Full frame (để crop face)
            face: Face tuple (x, y, w, h)
        
        Returns:
            bool - True if sleeping
        """
        if frame is None or face is None:
            return False
        
        x, y, w, h = face
        h_frame, w_frame = frame.shape[:2]
        
        # Clamp face region
        x = max(0, x)
        y = max(0, y)
        w = min(w, w_frame - x)
        h = min(h, h_frame - y)
        
        face_roi = frame[y:y+h, x:x+w]
        
        # Check if eyes closed
        eyes_closed = self.is_eyes_closed(face_roi)
        
        if eyes_closed:
            self.eye_closed_counter += 1
        else:
            self.eye_closed_counter = 0
        
        # Threshold: mắt đóng quá lâu → ngủ gật
        is_sleeping = self.eye_closed_counter > config.EYE_CLOSED_FRAMES
        
        if is_sleeping and not self.last_eye_status:
            logger.warning(f"Sleep detected! Eyes closed for {self.eye_closed_counter} frames")
        
        self.last_eye_status = is_sleeping
        
        return is_sleeping
    
    def draw_faces(self, frame, faces, color=(255, 0, 0), thickness=2):
        """
        Vẽ khuôn mặt detected lên frame
        
        Args:
            frame: Input frame
            faces: List of (x, y, w, h)
            color: BGR color
            thickness: Line thickness
        
        Returns:
            Annotated frame
        """
        if frame is None:
            return None
        
        frame_copy = frame.copy()
        
        for (x, y, w, h) in faces:
            # Draw face rectangle
            cv2.rectangle(frame_copy, (x, y), (x+w, y+h), color, thickness)
            
            # Draw label
            cv2.putText(
                frame_copy,
                "Face",
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                1
            )
        
        return frame_copy
    
    def draw_eyes(self, face_roi, eyes, color=(0, 255, 0), thickness=2):
        """
        Vẽ mắt detected lên face region
        
        Args:
            face_roi: Face region
            eyes: List of (x, y, w, h) (trong tọa độ face_roi)
            color: BGR color
            thickness: Line thickness
        
        Returns:
            Annotated face region
        """
        if face_roi is None:
            return None
        
        face_copy = face_roi.copy()
        
        for (x, y, w, h) in eyes:
            # Draw eye rectangle
            cv2.rectangle(face_copy, (x, y), (x+w, y+h), color, thickness)
        
        return face_copy
    
    def reset_sleep_counter(self):
        """Reset eye closed counter"""
        self.eye_closed_counter = 0
        self.last_eye_status = False


# ============================================
# STANDALONE TEST
# ============================================

def test_face_detector():
    """Test face detection"""
    print("👤 Testing Face Detector...")
    
    try:
        from vision.camera import Camera
        
        camera = Camera(
            width=config.CAMERA_WIDTH,
            height=config.CAMERA_HEIGHT
        )
        
        detector = FaceDetector()
        
        print("Reading 30 frames...")
        for i in range(30):
            ret, frame = camera.read()
            if ret:
                resized = camera.resize_frame(frame, config.FRAME_WIDTH, config.FRAME_HEIGHT)
                faces = detector.detect_faces(resized)
                
                if len(faces) > 0:
                    print(f"  Frame {i}: {len(faces)} face(s) detected")
                    
                    for face in faces:
                        is_sleeping = detector.detect_sleep(resized, face)
                        print(f"    Face: {face} | Sleeping: {is_sleeping}")
        
        print("✅ Face detector test passed")
        
        camera.release()
    
    except Exception as e:
        print(f"❌ Face detector test failed: {e}")


if __name__ == "__main__":
    test_face_detector()
