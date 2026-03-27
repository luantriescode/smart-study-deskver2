import cv2
import os

class FaceDetector:
    def __init__(self):
        # Load model nhận diện khuôn mặt mặc định của OpenCV [cite: 5]
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

    def analyze_pose(self, frame):
        """Trả về: (is_bad_posture, face_coords) [cite: 6, 18]"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # detectMultiScale tối ưu cho Pi B+
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        is_bad_posture = False
        face_data = None

        for (x, y, w, h) in faces:
            face_data = (x, y, w, h)
            # Logic Step 6: Nếu tọa độ Y của mặt thấp hơn 60% chiều cao khung hình [cite: 6, 18]
            # (Đang cúi đầu quá thấp hoặc gục xuống bàn)
            if y > (frame.shape[0] * 0.6):
                is_bad_posture = True
            break # Chỉ lấy khuôn mặt đầu tiên
            
        return is_bad_posture, face_data