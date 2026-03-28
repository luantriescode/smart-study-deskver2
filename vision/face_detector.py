import cv2
import os

class FaceDetector:
    def __init__(self):
        self.cascade_path = os.path.join(os.getcwd(), 'haarcascade_frontalface_default.xml')
        self.face_cascade = cv2.CascadeClassifier(self.cascade_path)
        if self.face_cascade.empty():
            print("❌ AI ERROR: Không load được file XML!")
        else:
            print("✅ AI READY: Model nhận diện mặt đã sẵn sàng.")

    def analyze_pose(self, frame):
        if self.face_cascade.empty(): return False, None
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Giảm minNeighbors xuống 2 để nhạy hơn, cân chỉnh scaleFactor 1.1
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 2)
        
        is_bad_posture = False
        face_data = None

        if len(faces) > 0:
            (x, y, w, h) = faces[0]
            face_data = (x, y, w, h)
            # Ngưỡng y > 50% khung hình là sai tư thế
            if y > (frame.shape[0] * 0.5):
                is_bad_posture = True
            
        return is_bad_posture, face_data