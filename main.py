import time
import cv2
import threading
from flask import Flask, Response
import config

# Import đúng cấu trúc thư mục [cite: 9]
from vision.camera import Camera
from vision.motion_detector import MotionDetector
from vision.face_detector import FaceDetector
from hardware.relay import RelayController
from communication.telegram_bot import TelegramBot

# --- KHỞI TẠO ---
app = Flask(__name__)
cam = Camera(device_id=config.CAMERA_INDEX, width=config.CAMERA_WIDTH, height=config.CAMERA_HEIGHT)
motion_engine = MotionDetector()
face_engine = FaceDetector()
relay = RelayController()
bot = TelegramBot()

# Biến chia sẻ giữa các luồng
latest_frame = None
is_light_on = False
last_motion_time = time.time()
slouch_start_time = 0
warning_cooldown = 0

def logic_thread():
    """Luồng xử lý AI, Relay và Telegram [cite: 11, 12, 13]"""
    global latest_frame, is_light_on, last_motion_time, slouch_start_time, warning_cooldown
    
    print("🧠 AI & Logic Thread đang chạy...")
    while True:
        success, frame = cam.read()
        if not success: continue
        
        # Cập nhật frame cho Web Stream
        latest_frame = frame.copy()

        # 1. Phát hiện người (Step 4) [cite: 15, 18]
        person_present, _ = motion_engine.detect(frame)

        if person_present:
            # Logic bật đèn (Đã chạy OK) [cite: 4, 15]
            if not is_light_on:
                relay.turn_on()
                is_light_on = True

            # Check tư thế (Step 6) [cite: 6, 11]
            is_bad, face_box = face_engine.analyze_pose(frame)
            
            if is_bad:
                if slouch_start_time == 0: 
                    slouch_start_time = time.time()
                
                duration = time.time() - slouch_start_time
                # Nếu ngồi sai tư thế quá 3 giây (Step 5/6) [cite: 15, 18]
                if duration > 3 and time.time() > warning_cooldown:
                    print("📤 Đang gửi tin nhắn Telegram...") [cite: 7, 13]
                    bot.send_alert("🔴 CẢNH BÁO: Bạn đang ngồi sai tư thế hoặc ngủ gật!", frame)
                    # Chờ 30 giây mới cho phép gửi lại để tránh treo mạng Pi [cite: 1, 13]
                    warning_cooldown = time.time() + 30 
            else:
                slouch_start_time = 0
        else:
            # Logic tắt đèn sau 10s (Step 4) [cite: 15, 18]
            if is_light_on and (time.time() - last_motion_time > config.PERSON_LOST_DELAY):
                relay.turn_off()
                is_light_on = False
                print("🌑 Đèn TẮT")

        time.sleep(0.1) # Rất quan trọng để Pi B+ không treo

def generate_frames():
    """Luồng đẩy ảnh lên Web Dashboard (Step 8) [cite: 7]"""
    global latest_frame
    while True:
        if latest_frame is None: continue
        
        # Vẽ khung ROI và Face để debug trực tiếp trên Web
        frame_web = latest_frame.copy()
        cv2.rectangle(frame_web, (config.ROI_X, config.ROI_Y), 
                      (config.ROI_X + config.ROI_W, config.ROI_Y + config.ROI_H), (0, 255, 0), 2)
        
        ret, buffer = cv2.imencode('.jpg', frame_web, [int(cv2.IMWRITE_JPEG_QUALITY), 30])
        if not ret: continue
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/')
def index():
    return "<html><body style='background:#000;color:#0f0;text-align:center;'><h2>Smart Desk Monitor</h2><img src='/video_feed'></body></html>"

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    # Chạy Logic AI ở background
    t = threading.Thread(target=logic_thread)
    t.daemon = True
    t.start()

    # Chạy Web Server ở luồng chính (Step 8) [cite: 7]
    print(f"📡 Web Dashboard: http://{config.WEB_HOST}:5000")
    try:
        app.run(host=config.WEB_HOST, port=5000, threaded=True, debug=False)
    finally:
        relay.turn_off()
        cam.release()