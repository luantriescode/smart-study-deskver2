import cv2
import os

class FaceDetector:
    def __init__(self):
        # Đường dẫn mặc định của Haar Cascades trên Raspberry Pi OS
        cascade_path = '/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml'
        
        # Nếu đường dẫn trên không tồn tại, thử đường dẫn dự phòng
        if not os.path.exists(cascade_path):
            cascade_path = '/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml'
            
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        if self.face_cascade.empty():
            print("❌ Lỗi: Không tìm thấy file Haar Cascade XML!")

    def analyze_pose(self, frame):
        """Trả về: (is_bad_posture, face_coords) """
        # Resize nhỏ lại để Pi B+ xử lý nhanh hơn (Step 3 Optimization) [cite: 3]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # detectMultiScale: tìm khuôn mặt [cite: 5]
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        is_bad_posture = False
        face_data = None

        for (x, y, w, h) in faces:
            face_data = (x, y, w, h)
            # Logic Step 6: Nếu mặt thấp hơn 60% khung hình ROI [cite: 6, 18]
            if y > (frame.shape[0] * 0.6):
                is_bad_posture = True
            break 
            
        return is_bad_posture, face_data