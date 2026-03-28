import cv2
import json
import os
import numpy as np

class PostureDetector:
    def __init__(self):
        self.ref_file = 'posture_ref.json'
        # Không dùng Haar Cascade nữa để tránh lỗi "Không tìm thấy mặt"
        self.ref_vector = self.load_reference()

    def load_reference(self):
        if os.path.exists(self.ref_file):
            try:
                with open(self.ref_file, 'r') as f:
                    return json.load(f)
            except: return None
        return None

    def get_centroid(self, frame):
        """Tìm trọng tâm của vùng tối nhất/khối người trong khung hình mờ"""
        # 1. Chuyển xám và làm mờ cực mạnh để khử nhiễu hạt của Cam C270
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (21, 21), 0)
        
        # 2. Ngưỡng hóa (Threshold): Tách vùng người (thường tối hơn nền)
        # Giả sử nền sáng, người tối. Nếu nền tối bạn cần đảo ngược lại.
        _, thresh = cv2.threshold(blurred, 100, 255, cv2.THRESH_BINARY_INV)
        
        # 3. Tìm Moment để tính trọng tâm khối (Centroid)
        M = cv2.moments(thresh)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            return (cX, cY), thresh
        return None, thresh

    def save_reference(self, frame):
        """Lấy mẫu: Lưu trọng tâm chuẩn vào JSON"""
        centroid, _ = self.get_centroid(frame)
        if centroid:
            self.ref_vector = {
                "cX": centroid[0],
                "cY": centroid[1]
            }
            with open(self.ref_file, 'w') as f:
                json.dump(self.ref_vector, f)
            print(f"💾 Đã lưu trọng tâm chuẩn: {self.ref_vector}")
            return True, "Đã xác nhận tư thế chuẩn!"
        return False, "Không xác định được trọng tâm người dùng."

    def check(self, frame):
        """So sánh: Nếu trọng tâm Y hạ thấp quá mức -> Sai tư thế"""
        if not self.ref_vector:
            return False, "Chờ lấy mẫu"

        curr_centroid, _ = self.get_centroid(frame)
        if curr_centroid:
            # Tính độ lệch Y (Trục dọc)
            # Nếu cY tăng tức là trọng tâm khối người đang đi xuống (cúi đầu)
            y_diff = curr_centroid[1] - self.ref_vector["cY"]
            
            # Ngưỡng lệch: Nếu hạ thấp hơn 40 pixel (tùy chỉnh theo khoảng cách ngồi)
            if y_diff > 40: 
                return True, "Sai tư thế (Cúi thấp)"
        
        return False, "OK"