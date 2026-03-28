import time
import cv2
import threading
from flask import Flask, Response
import config
from vision.camera import Camera
from vision.motion_detector import MotionDetector
from vision.face_detector import FaceDetector
from hardware.relay import RelayController
from communication.telegram_bot import TelegramBot

app = Flask(__name__)
cam = Camera(device_id=config.CAMERA_INDEX, width=config.CAMERA_WIDTH, height=config.CAMERA_HEIGHT)
motion_engine = MotionDetector()
face_engine = FaceDetector()
relay = RelayController()
bot = TelegramBot()

latest_frame = None
is_light_on = False
last_motion_time = time.time()
slouch_start_time = 0
warning_cooldown = 0

def logic_thread():
    global latest_frame, is_light_on, last_motion_time, slouch_start_time, warning_cooldown
    
    print("🧠 Hệ thống bắt đầu quét...")
    while True:
        success, frame = cam.read()
        if not success: continue
        
        latest_frame = frame.copy()
        person_present, _ = motion_engine.detect(frame)

        # --- LOGIC BẬT/TẮT ĐÈN (Step 4) ---
        if person_present:
            last_motion_time = time.time()
            if not is_light_on:
                relay.turn_on()
                is_light_on = True
                msg = "💡 Đèn đã BẬT (Phát hiện người)"
                print(msg)
                bot.send_alert(msg) # Thông báo trạng thái đèn về Tele

            # --- LOGIC AI TƯ THẾ (Step 5, 6) ---
            is_bad, face_box = face_engine.analyze_pose(frame)
            if is_bad:
                if slouch_start_time == 0: slouch_start_time = time.time()
                duration = time.time() - slouch_start_time
                print(f"⚠️ Đang sai tư thế: {int(duration)}s")
                
                if duration > 5 and time.time() > warning_cooldown:
                    print("📤 Gửi cảnh báo tư thế về Telegram...")
                    bot.send_alert("🔴 CẢNH BÁO: Bạn đang ngồi sai tư thế!", frame)
                    warning_cooldown = time.time() + 60 
            else:
                if slouch_start_time != 0:
                    print("✅ Tư thế đã đúng trở lại")
                slouch_start_time = 0
        else:
            # Tắt đèn sau thời gian delay
            if is_light_on and (time.time() - last_motion_time > config.PERSON_LOST_DELAY):
                relay.turn_off()
                is_light_on = False
                msg = "🌑 Đèn đã TẮT (Không có người)"
                print(msg)
                bot.send_alert(msg) # Thông báo trạng thái đèn về Tele

        time.sleep(0.1)

def generate_frames():
    global latest_frame
    while True:
        if latest_frame is None: continue
        # Vẽ khung ROI xanh để dễ căn chỉnh trên Web
        frame_web = latest_frame.copy()
        cv2.rectangle(frame_web, (config.ROI_X, config.ROI_Y), 
                      (config.ROI_X + config.ROI_W, config.ROI_Y + config.ROI_H), (0, 255, 0), 2)
        
        ret, buffer = cv2.imencode('.jpg', frame_web, [int(cv2.IMWRITE_JPEG_QUALITY), 35])
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/')
def index():
    return "<html><body style='background:#000;color:#0f0;text-align:center;'><h2>Smart Desk Monitor</h2><img src='/video_feed'></body></html>"

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    t = threading.Thread(target=logic_thread)
    t.daemon = True
    t.start()
    app.run(host=config.WEB_HOST, port=5000, threaded=True, debug=False)