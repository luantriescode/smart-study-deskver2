import cv2
import json
import os

class PostureDetector:
    def __init__(self):
        # Load model face nhẹ cho Pi B+
        self.face_cascade = cv2.CascadeClassifier(os.path.join(os.getcwd(), 'haarcascade_frontalface_default.xml'))
        self.ref_file = 'posture_ref.json'
        # Tự động nạp dữ liệu cũ nếu có
        self.ref_vector = self.load_reference()

    def load_reference(self):
        """Đọc dữ liệu từ file JSON"""
        if os.path.exists(self.ref_file):
            try:
                with open(self.ref_file, 'r') as f:
                    data = json.load(f)
                    print(f"✅ [AI] Đã nạp tư thế chuẩn: Y={data['y_center']}, Ratio={data['ratio']}")
                    return data
            except Exception as e:
                print(f"⚠️ Lỗi đọc file JSON: {e}")
                return None
        return None

    def save_reference(self, frame):
        """Phân tích và tự sinh file JSON mới"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) > 0:
            (x, y, w, h) = faces[0]
            # Vector hóa: Tâm mặt, Tỷ lệ khung hình, Chiều cao tương đối
            self.ref_vector = {
                "y_center": int(y + h/2),
                "ratio": round(h/w, 2),
                "h": int(h)
            }
            # Ghi đè file JSON để lưu vĩnh viễn
            with open(self.ref_file, 'w') as f:
                json.dump(self.ref_vector, f)
            return True, "Đã cập nhật tư thế mới vào JSON"
        return False, "Không tìm thấy khuôn mặt để lấy mẫu"

    def check(self, frame):
        """So sánh thực tế với mẫu trong RAM/JSON"""
        if not self.ref_vector:
            return False, "Chờ lấy mẫu"

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)

        if len(faces) > 0:
            (x, y, w, h) = faces[0]
            curr_y = y + h/2
            curr_ratio = h/w
            
            # Tính độ lệch dựa trên Vector chuẩn
            y_diff = abs(curr_y - self.ref_vector["y_center"]) / frame.shape[0]
            r_diff = abs(curr_ratio - self.ref_vector["ratio"])
            
            # Ngưỡng (Threshold): Lệch > 15% vị trí hoặc > 20% tỷ lệ hình dáng
            if y_diff > 0.15 or r_diff > 0.2:
                return True, "Sai tư thế"
        return False, "OK"