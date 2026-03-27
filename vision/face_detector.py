import cv2
import os
import config

class FaceDetector:
    def __init__(self):
        # Trỏ trực tiếp vào file nằm ở thư mục gốc dự án
        cascade_path = os.path.join(os.getcwd(), 'haarcascade_frontalface_default.xml')
        
        if not os.path.exists(cascade_path):
            print(f"❌ Cảnh báo: Không tìm thấy {cascade_path}. Vui lòng chạy lệnh wget để tải file.")
            
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

    def analyze_pose(self, frame):
        """Trả về: (is_bad_posture, face_coords)"""
        if self.face_cascade.empty():
            return False, None

        # Resize nhỏ để giảm tải cho Pi B+ (Step 3 Optimization) [cite: 3]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # detectMultiScale: tìm khuôn mặt
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        is_bad_posture = False
        face_data = None

        for (x, y, w, h) in faces:
            face_data = (x, y, w, h)
            # Step 6: Nếu mặt thấp hơn 60% khung hình [cite: 6]
            if y > (frame.shape[0] * 0.6):
                is_bad_posture = True
            break 
            
        return is_bad_posture, face_data