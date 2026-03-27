# web_test_c270.py
import cv2
import sys
import os
import time
from flask import Flask, Response

# Fix path import
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import config
from vision.camera import Camera

app = Flask(__name__)
cam = None

def get_camera():
    global cam
    if cam is None:
        cam = Camera(
            device_id=config.CAMERA_INDEX,
            width=config.CAMERA_WIDTH,
            height=config.CAMERA_HEIGHT,
            fps=config.CAMERA_FPS
        )
    return cam

def generate_frames():
    camera = get_camera()
    while True:
        success, frame = camera.read()
        if not success:
            time.sleep(0.1)
            continue
        
        # Vẽ ROI từ config [cite: 1, 18]
        frame = camera.draw_roi(frame, (config.ROI_X, config.ROI_Y, config.ROI_W, config.ROI_H))
        
        # Nén JPEG mức 30 để truyền tải nhẹ nhất qua Ethernet
        ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 30])
        if not ret: continue
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/')
def index():
    return '<body style="background:#000;text-align:center;"><img src="/video_feed" style="margin-top:50px; border:2px solid #0f0;"></body>'

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    try:
        app.run(host=config.WEB_HOST, port=5000, threaded=True)
    finally:
        if cam: cam.release()