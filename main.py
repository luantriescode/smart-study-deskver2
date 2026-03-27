import time
import cv2
import threading
from flask import Flask, Response
import config
from vision.camera import Camera
from vision.motion_detector import MotionDetector
from hardware.relay import RelayController

# --- KHỞI TẠO CÁC MODULE ---
app = Flask(__name__)
cam = Camera(device_id=config.CAMERA_INDEX, width=config.CAMERA_WIDTH, height=config.CAMERA_HEIGHT)
detector = MotionDetector()
relay = RelayController()

# Biến toàn cục để chia sẻ trạng thái
latest_frame = None
last_motion_time = time.time()
is_light_on = False

def logic_thread():
    global latest_frame, last_motion_time, is_light_on
    print("🚀 Logic tự động đang chạy...")
    
    while True:
        success, frame = cam.read()
        if not success:
            continue
        
        # Lưu frame để Web Stream sử dụng
        latest_frame = frame.copy()

        # 1. Phát hiện chuyển động trong ROI
        has_motion, _ = detector.detect(frame)

        # 2. Xử lý Logic Relay
        if has_motion:
            last_motion_time = time.time()
            if not is_light_on:
                print("👤 PHÁT HIỆN NGƯỜI -> BẬT ĐÈN")
                relay.turn_on()
                is_light_on = True
        else:
            elapsed = time.time() - last_motion_time
            if is_light_on and elapsed > config.PERSON_LOST_DELAY:
                print(f"🌑 KHÔNG CÓ NGƯỜI ({int(elapsed)}s) -> TẮT ĐÈN")
                relay.turn_off()
                is_light_on = False
        
        time.sleep(0.1) # Giảm tải CPU cho Pi B+

def generate_frames():
    global latest_frame
    while True:
        if latest_frame is None:
            continue
        
        # Vẽ ROI lên frame để bạn xem trên Web và căn chỉnh
        frame_display = cam.draw_roi(latest_frame.copy(), 
                                    (config.ROI_X, config.ROI_Y, config.ROI_W, config.ROI_H))
        
        # Nén JPEG để truyền qua Web
        ret, buffer = cv2.imencode('.jpg', frame_display, [int(cv2.IMWRITE_JPEG_QUALITY), 30])
        if not ret: continue
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/')
def index():
    return f"<html><body style='background:#000;color:#0f0;text-align:center;'><h2>Smart Desk Monitor</h2><img src='/video_feed' style='border:2px solid #0f0;'><p>Ngồi vào khung xanh để test Relay!</p></body></html>"

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    # Chạy Logic ở luồng riêng
    t = threading.Thread(target=logic_thread)
    t.daemon = True
    t.start()

    # Chạy Web Server ở luồng chính
    print(f"📡 Truy cập web tại: http://{config.WEB_HOST}:5000")
    try:
        app.run(host=config.WEB_HOST, port=5000, threaded=True, debug=False)
    finally:
        relay.turn_off()
        cam.release()