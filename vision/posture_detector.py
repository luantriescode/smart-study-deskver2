import cv2
import json
import os

class PostureDetector:
    def __init__(self):
        # SỬA: Sử dụng model bắt Upper Body (Đầu/Vai) hoặc Face lỏng hơn cho Pi B+
        cascade_name = 'haarcascade_frontalface_alt.xml' # Model này nhạy hơn với ảnh mờ
        self.cascade_path = os.path.join(os.getcwd(), cascade_name)
        
        # Nếu chưa có file xml này, Pi sẽ báo lỗi, mình sẽ chỉ bạn cách tải ở dưới
        self.face_cascade = cv2.CascadeClassifier(self.cascade_path)
        
        if self.face_cascade.empty():
            print(f"❌ AI ERROR: Không load được model {cascade_name}!")
            # Fallback về model mặc định nếu mờ quá không load được
            self.cascade_path = os.path.join(os.getcwd(), 'haarcascade_frontalface_default.xml')
            self.face_cascade = cv2.CascadeClassifier(self.cascade_path)

        self.ref_file = 'posture_ref.json'
        self.ref_vector = self.load_reference()

    def load_reference(self):
        """Load Vector cũ từ file JSON"""
        if os.path.exists(self.ref_file):
            try:
                with open(self.ref_file, 'r') as f:
                    data = json.load(f)
                    print(f"✅ [AI] Đã nạp hình khối chuẩn: Y={data['y_center']}, Ratio={data['ratio']}")
                    return data
            except: return None
        return None

    def save_reference(self, frame):
        """Chụp hình, phân tích HÌNH KHỐI và tự sinh file JSON"""
        # SỬA: Resize ảnh nhỏ hơn và làm mờ nhẹ để giảm nhiễu trước khi xử lý (Tối ưu cho ảnh mờ)
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0) # Giảm nhiễu hạt
        
        # SỬA: Giảm minNeighbors xuống 1 để 'bắt' được hình khối dù không rõ nét
        faces = self.face_cascade.detectMultiScale(gray, 1.05, 1)
        
        if len(faces) > 0:
            # Lấy hình khối lớn nhất (thường là đầu)
            faces = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)
            (x, y, w, h) = faces[0]
            
            # Nhân ngược lại tỷ lệ resize 0.5
            x, y, w, h = x*2, y*2, w*2, h*2
            
            self.ref_vector = {
                "y_center": int(y + h/2),
                "ratio": round(h/w, 2), # Tỷ lệ Cao/Rộng của hình khối
                "h_ref": int(h)
            }
            # Ghi đè vào file JSON vĩnh viễn
            with open(self.ref_file, 'w') as f:
                json.dump(self.ref_vector, f)
            print(f"💾 Đã lưu hình khối chuẩn mới: {self.ref_vector}")
            return True, "Đã cập nhật tư thế mới"
        
        return False, "Ảnh quá mờ, không bắt được hình khối. Hãy chỉnh góc Cam!"

    def check(self, frame):
        """So sánh thực tế với mẫu JSON (Chỉ Cảnh báo sai tư thế)"""
        if not self.ref_vector:
            return False, "Chờ lấy mẫu"

        # Tiền xử lý tương tự save_reference
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Bắt hình khối thực tế
        faces = self.face_cascade.detectMultiScale(gray, 1.05, 1)

        if len(faces) > 0:
            # Lấy khối lớn nhất
            faces = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)
            (x, y, w, h) = faces[0]
            
            curr_y = (y + h/2) * 2
            curr_ratio = h/w
            
            # Tính độ lệch vector so với mẫu JSON
            # y_diff: Lệch vị trí cao thấp (so với chiều cao ảnh 480px)
            y_diff = abs(curr_y - self.ref_vector["y_center"]) / 480
            
            # r_diff: Lệch tỷ lệ hình khối (Cao/Rộng)
            r_diff = abs(curr_ratio - self.ref_vector["ratio"])
            
            # Ngưỡng lệch (Threshold)
            # Tăng ngưỡng lên 0.2 và 0.25 để giảm báo động giả do ảnh mờ
            if y_diff > 0.20 or r_diff > 0.25:
                return True, "Sai tư thế"
        return False, "OK"