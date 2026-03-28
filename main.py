import time
import cv2
import threading
import os
from flask import Flask, Response, jsonify
import config

# --- IMPORT MODULES (Step 1-7) ---
from vision.camera import Camera
from vision.motion_detector import MotionDetector
from vision.face_detector import FaceDetector
from vision.posture_detector import PostureDetector
from hardware.relay import RelayController
from communication.telegram_bot import TelegramBot

# --- KHỞI TẠO HỆ THỐNG ---
app = Flask(__name__)

# Khởi tạo Camera với cơ chế chống treo
try:
    cam = Camera(device_id=config.CAMERA_INDEX, width=config.CAMERA_WIDTH, height=config.CAMERA_HEIGHT)
except Exception:
    cam = Camera(device_id=1, width=config.CAMERA_WIDTH, height=config.CAMERA_HEIGHT)

# Khởi tạo các Engine xử lý
motion_engine = MotionDetector()
face_engine = FaceDetector()
posture_engine = PostureDetector() # Đã thêm để fix lỗi Undefined
relay = RelayController()
bot = TelegramBot()

# Biến toàn cục chia sẻ giữa các luồng
latest_frame = None
is_light_on = False
last_motion_time = time.time()
slouch_start_time = 0
warning_cooldown = 0

# --- LOGIC XỬ LÝ CHÍNH (Thread) ---
def logic_thread():
    global latest_frame, is_light_on, last_motion_time, slouch_start_time, warning_cooldown
    
    print("🧠 [Hệ thống] Đang chạy giám sát Tư thế & Đèn...")
    
    while True:
        success, frame = cam.read()
        if not success:
            continue
        
        latest_frame = frame.copy()

        # 1. Phát hiện người (Step 4)
        person_present, _ = motion_engine.detect(frame)

        if person_present:
            last_motion_time = time.time()
            if not is_light_on:
                relay.turn_on()
                is_light_on = True
                msg_on = "💡 [Telegram] Đèn bàn đã BẬT: Phát hiện có người."
                print(msg_on)
                bot.send_alert(msg_on)

            # 2. Kiểm tra tư thế dựa trên Vector JSON (Step 6)
            is_bad, status_msg = posture_engine.check(frame)
            
            if is_bad:
                if slouch_start_time == 0:
                    slouch_start_time = time.time()
                
                duration = time.time() - slouch_start_time
                # Nếu sai tư thế > 5s và hết thời gian chờ spam (Step 7)
                if duration > 5 and time.time() > warning_cooldown:
                    alert_text = "🔴 CẢNH BÁO: Bạn đang ngồi sai tư thế!"
                    print(f"📤 {alert_text}")
                    bot.send_alert(alert_text, frame)
                    warning_cooldown = time.time() + 60 
            else:
                slouch_start_time = 0
        else:
            # 3. Tắt đèn sau khoảng thời gian delay (Step 4)
            if is_light_on and (time.time() - last_motion_time > config.PERSON_LOST_DELAY):
                relay.turn_off()
                is_light_on = False
                msg_off = "🌑 [Telegram] Đèn bàn đã TẮT: Không có người."
                print(msg_off)
                bot.send_alert(msg_off)

        time.sleep(0.1) # Giảm tải CPU cho Pi B+

# --- WEB DASHBOARD ROUTES (Step 8) ---
@app.route('/')
def index():
    return """
    <html>
        <body style="background:#1a1a1a; color:#00ff00; text-align:center; font-family:sans-serif;">
            <h2>Smart Study Desk Dashboard</h2>
            <div style="margin-bottom: 20px;">
                <img src="/video_feed" style="border:2px solid #00ff00; width:80%; max-width:640px;">
            </div>
            <button onclick="setPosture()" style="padding:15px 30px; font-size:18px; cursor:pointer; background:#00ff00; border:none; border-radius:5px;">
                XÁC NHẬN TƯ THẾ CHUẨN (LƯU JSON)
            </button>
            <p id="status"></p>
            <script>
                function setPosture() {
                    document.getElementById('status').innerText = "Đang xử lý...";
                    fetch('/set_posture', {method: 'POST'})
                    .then(response => response.json())
                    .then(data => {
                        alert(data.message);
                        document.getElementById('status').innerText = data.message;
                    });
                }
            </script>
        </body>
    </html>
    """

@app.route('/video_feed')
def video_feed():
    def generate():
        while True:
            if latest_frame is None: continue
            # Nén ảnh để stream mượt trên mạng nội bộ
            ret, buffer = cv2.imencode('.jpg', latest_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 35])
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/set_posture', methods=['POST'])
def set_posture():
    """API cập nhật tư thế mẫu vào file JSON"""
    global latest_frame
    if latest_frame is not None:
        success, message = posture_engine.save_reference(latest_frame)
        if success:
            return jsonify({"status": "success", "message": message})
        return jsonify({"status": "error", "message": message}), 400
    return jsonify({"status": "error", "message": "Camera chưa sẵn sàng"}), 500

if __name__ == "__main__":
    # Chạy luồng AI xử lý ngầm
    t = threading.Thread(target=logic_thread)
    t.daemon = True
    t.start()
    
    # Chạy Web Server
    print(f"📡 Web Dashboard online tại: http://{config.WEB_HOST}:{config.WEB_PORT}")
    try:
        app.run(host=config.WEB_HOST, port=config.WEB_PORT, threaded=True, debug=False)
    finally:
        relay.turn_off()
        cam.release()