import cv2
import sys
import os
import time
from flask import Flask, Response

# Ép Python tìm đúng đường dẫn module [cite: 1]
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import config
from vision.camera import Camera

app = Flask(__name__)
# Khởi tạo camera ngoài vòng lặp để tránh treo driver
cam = None

def get_camera():
    global cam
    if cam is None:
        try:
            # Logitech C270 chạy ổn nhất ở 160x120 trên Pi B+
            cam = Camera(
                device_id=config.CAMERA_INDEX,
                width=config.CAMERA_WIDTH,
                height=config.CAMERA_HEIGHT,
                fps=config.CAMERA_FPS,
                fourcc=config.CAMERA_FOURCC
            )
        except Exception as e:
            print(f"❌ Lỗi khởi tạo Camera: {e}")
    return cam

def generate_frames():
    camera = get_camera()
    if not camera:
        return

    while True:
        # Sử dụng cơ chế grab/retrieve để giảm độ trễ (latency)
        success, frame = camera.read()
        
        if not success or frame is None:
            time.sleep(0.1) # Nghỉ ngắn để driver phục hồi nếu bị timeout
            continue
        
        # Vẽ khung ROI (vùng nhận diện) để bạn căn chỉnh [cite: 1, 15]
        frame_display = camera.draw_roi(frame, (config.ROI_X, config.ROI_Y, config.ROI_W, config.ROI_H))
        
        # Nén JPEG mức 30: Ảnh hơi mờ nhưng cực nhẹ, giúp Pi truyền đi mượt mà
        ret, buffer = cv2.imencode('.jpg', frame_display, [int(cv2.IMWRITE_JPEG_QUALITY), 30])
        
        if not ret:
            continue
            
        frame_bytes = buffer.tobytes()
        
        # Yield dữ liệu theo chuẩn MJPEG stream
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    # Giao diện web tối giản, không tải thêm CSS nặng
    return f"""
    <html>
        <head><title>Pi B+ Stream</title></head>
        <body style="background:#000; color:#0f0; text-align:center; font-family:monospace;">
            <h2>🚀 SMART STUDY DESK - C270 LIVE</h2>
            <p>Resolution: {config.CAMERA_WIDTH}x{config.CAMERA_HEIGHT} | Host: {config.WEB_HOST}</p>
            <img src="/video_feed" style="border:2px solid #0f0; width:320px;">
            <p>Khung xanh: Vùng ROI để bắt chuyển động</p>
        </body>
    </html>
    """

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), 
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    print(f"📡 Đang mở server tại http://{config.WEB_HOST}:5000")
    try:
        # Chạy Flask ở chế độ threaded để không chặn luồng camera
        app.run(host=config.WEB_HOST, port=5000, threaded=True, debug=False)
    finally:
        if cam:
            cam.release()