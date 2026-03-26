import cv2
import sys
import os
from flask import Flask, Response

# Thêm đường dẫn để Python tìm thấy config.py và vision/
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

try:
    import config
    from vision.camera import Camera
    print("✅ Hệ thống đã sẵn sàng.")
except ImportError as e:
    print(f"❌ Lỗi: {e}")
    sys.exit(1)

app = Flask(__name__)

# Khởi tạo camera với MJPG 320x240 để tiết kiệm CPU
cam = Camera(
    device_id=config.CAMERA_INDEX,
    width=config.CAMERA_WIDTH,
    height=config.CAMERA_HEIGHT,
    fps=config.CAMERA_FPS,
    fourcc=config.CAMERA_FOURCC
)

def generate_frames():
    while True:
        success, frame = cam.read()
        if not success or frame is None:
            continue
        
        # 1. Resize nhỏ lại thêm một chút để giảm tải (tùy chọn)
        # frame = cv2.resize(frame, (160, 120)) # Thử nếu vẫn đứt hình
        
        # 2. Vẽ ROI
        frame_display = cam.draw_roi(frame, (config.ROI_X, config.ROI_Y, config.ROI_W, config.ROI_H))
        
        # 3. Nén JPEG mạnh hơn (quality=50) để giảm dung lượng gói tin truyền qua mạng
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]
        ret, buffer = cv2.imencode('.jpg', frame_display, encode_param)
        
        if not ret:
            continue
            
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return """
    <html>
        <head><title>Smart Study Desk - Stream</title></head>
        <body style="background:#000; color:#fff; text-align:center;">
            <h1>🎥 Live Stream (320x240 MJPG)</h1>
            <img src="/video_feed" style="border:3px solid #0f0;">
            <p>Khung xanh: Vùng nhận diện người (ROI)</p>
        </body>
    </html>
    """

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    # Load HOST từ .env (192.168.1.8) [cite: 1]
    print(f"📡 Truy cập web tại: http://{config.WEB_HOST}:5000")
    try:
        app.run(host=config.WEB_HOST, port=5000, threaded=True)
    finally:
        cam.release()