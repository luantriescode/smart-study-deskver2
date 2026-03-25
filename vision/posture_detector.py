"""
VISION/POSTURE_DETECTOR.PY - Posture Detection
================================================
Quản lý:
  - Detect head position
  - Detect head angle (cúi/ngẩng)
  - Bad posture alert
"""

import cv2
import numpy as np
import logging

import config

logger = logging.getLogger(__name__)


class PostureDetector:
    """Phát hiện tư thế - đặc biệt là cúi đầu"""
    
    def __init__(self):
        """Khởi tạo posture detector"""
        # Load face cascade để detect mặt trước
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        if self.face_cascade.empty():
            raise RuntimeError("Failed to load face cascade")
        
        # Load profile face cascade để detect mặt từ cạnh
        self.profile_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_profileface.xml'
        )
        
        # Tracking
        self.head_angles = []  # Lịch sử góc đầu
        self.max_history = 5
        
        logger.info("PostureDetector initialized")
    
    def detect_posture(self, frame):
        """
        Phát hiện tư thế đầu
        
        Args:
            frame: Input frame (BGR)
        
        Returns:
            Head angle (độ) hoặc None nếu không detect được
            - 0° = chuẩn
            - > 0° = cúi xuống
            - < 0° = ngẩng lên
        """
        if frame is None:
            return None
        
        # Convert to gray
        if len(frame.shape) == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = frame
        
        gray = cv2.equalizeHist(gray)
        
        # Detect frontal face
        frontal_faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.3,
            minNeighbors=4,
            minSize=(30, 30)
        )
        
        # Detect profile face
        profile_faces = self.profile_cascade.detectMultiScale(
            gray,
            scaleFactor=1.3,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        # Simple heuristic:
        # - Nếu detect được frontal face → chuẩn (angle ≈ 0°)
        # - Nếu detect được profile face nhưng không frontal → cúi/ngẩng
        
        if len(frontal_faces) > 0:
            # Frontal face detected
            angle = 0.0
        elif len(profile_faces) > 0:
            # Profile face - estimate cúi xuống
            angle = 25.0
        else:
            # Không detect → return None
            return None
        
        # Add to history
        self.head_angles.append(angle)
        if len(self.head_angles) > self.max_history:
            self.head_angles.pop(0)
        
        # Smooth angle (average)
        smooth_angle = np.mean(self.head_angles)
        
        return smooth_angle
    
    def is_bad_posture(self, frame, threshold=None):
        """
        Kiểm tra tư thế có xấu không
        
        Args:
            frame: Input frame
            threshold: Custom threshold (default: config.HEAD_DOWN_THRESHOLD)
        
        Returns:
            bool - True if bad posture
        """
        if threshold is None:
            threshold = config.HEAD_DOWN_THRESHOLD
        
        angle = self.detect_posture(frame)
        
        if angle is None:
            return False
        
        # Bad posture if cúi quá nhiều hoặc ngẩng quá nhiều
        is_bad = abs(angle) > threshold
        
        return is_bad
    
    def draw_posture(self, frame, angle=None, frontal_faces=None, profile_faces=None,
                     color_good=(0, 255, 0), color_bad=(0, 0, 255)):
        """
        Vẽ posture info lên frame
        
        Args:
            frame: Input frame
            angle: Head angle (độ)
            frontal_faces: List of frontal face detections
            profile_faces: List of profile face detections
            color_good: BGR color for good posture
            color_bad: BGR color for bad posture
        
        Returns:
            Annotated frame
        """
        if frame is None:
            return None
        
        frame_copy = frame.copy()
        
        # Draw detections
        if frontal_faces is not None:
            for (x, y, w, h) in frontal_faces:
                cv2.rectangle(frame_copy, (x, y), (x+w, y+h), color_good, 2)
        
        if profile_faces is not None:
            for (x, y, w, h) in profile_faces:
                cv2.rectangle(frame_copy, (x, y), (x+w, y+h), color_bad, 2)
        
        # Draw angle
        if angle is not None:
            is_bad = abs(angle) > config.HEAD_DOWN_THRESHOLD
            color = color_bad if is_bad else color_good
            
            cv2.putText(
                frame_copy,
                f"Head Angle: {angle:.1f}°",
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2
            )
            
            # Status
            status = "❌ BAD POSTURE" if is_bad else "✅ GOOD POSTURE"
            cv2.putText(
                frame_copy,
                status,
                (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2
            )
        
        return frame_copy
    
    def reset(self):
        """Reset posture history"""
        self.head_angles = []
        logger.info("PostureDetector reset")


# ============================================
# ALTERNATIVE: Using Face Landmarks (More Accurate)
# ============================================

class PostureDetectorAdvanced:
    """Advanced posture detection using face landmarks (requires dlib)"""
    
    def __init__(self):
        """Khởi tạo advanced posture detector"""
        try:
            import dlib
            self.dlib = dlib
            self.detector = dlib.get_frontal_face_detector()
            
            # Download shape predictor model từ:
            # http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
            predictor_path = config.PROJECT_ROOT / "models" / "shape_predictor_68_face_landmarks.dat"
            
            if not predictor_path.exists():
                logger.warning(
                    f"Shape predictor not found at {predictor_path}. "
                    "Advanced posture detection disabled."
                )
                self.predictor = None
            else:
                self.predictor = dlib.shape_predictor(str(predictor_path))
            
            logger.info("PostureDetectorAdvanced initialized")
        
        except ImportError:
            logger.warning("dlib not installed. Advanced posture detection disabled.")
            self.dlib = None
            self.predictor = None
    
    def detect_head_angle(self, frame):
        """
        Detect head angle using face landmarks
        
        Args:
            frame: Input frame (BGR)
        
        Returns:
            (yaw_angle, pitch_angle, roll_angle) hoặc (None, None, None)
        """
        if self.predictor is None:
            return None, None, None
        
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.detector(gray, 1)
        
        if len(faces) == 0:
            return None, None, None
        
        face = faces[0]
        
        # Get landmarks
        landmarks = self.predictor(gray, face)
        
        # Extract key points (simplified)
        # Point 30 = nose tip
        # Point 8 = chin
        # Point 0, 16 = left/right ear
        
        nose = np.array([landmarks.part(30).x, landmarks.part(30).y])
        chin = np.array([landmarks.part(8).x, landmarks.part(8).y])
        left_ear = np.array([landmarks.part(0).x, landmarks.part(0).y])
        right_ear = np.array([landmarks.part(16).x, landmarks.part(16).y])
        
        # Calculate angles
        pitch = np.arctan2(chin[1] - nose[1], chin[0] - nose[0]) * 180 / np.pi - 90
        yaw = np.arctan2(right_ear[1] - left_ear[1], right_ear[0] - left_ear[0]) * 180 / np.pi
        roll = 0  # Simplified
        
        return yaw, pitch, roll


# ============================================
# STANDALONE TEST
# ============================================

def test_posture_detector():
    """Test posture detection"""
    print("🧍 Testing Posture Detector...")
    
    try:
        from vision.camera import Camera
        
        camera = Camera(
            width=config.CAMERA_WIDTH,
            height=config.CAMERA_HEIGHT
        )
        
        detector = PostureDetector()
        
        print("Reading 30 frames...")
        for i in range(30):
            ret, frame = camera.read()
            if ret:
                resized = camera.resize_frame(frame, config.FRAME_WIDTH, config.FRAME_HEIGHT)
                angle = detector.detect_posture(resized)
                
                if angle is not None:
                    is_bad = detector.is_bad_posture(resized)
                    print(f"  Frame {i}: Angle={angle:.1f}° | Bad={is_bad}")
        
        print("✅ Posture detector test passed")
        
        camera.release()
    
    except Exception as e:
        print(f"❌ Posture detector test failed: {e}")


if __name__ == "__main__":
    test_posture_detector()
