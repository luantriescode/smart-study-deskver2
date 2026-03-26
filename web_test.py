from flask import Flask, Response
import cv2
import config
from vision.camera import Camera

app = Flask(__name__)
cam = Camera(device_id=config.CAMERA_INDEX, width=config.CAMERA_WIDTH, 
             height=config.CAMERA_HEIGHT, fourcc=config.CAMERA_FOURCC)

def gen():
    while True:
        ret, frame = cam.read()
        if not ret: break
        # Vẽ ROI để căn chỉnh [cite: 15]
        frame = cam.draw_roi(frame, (config.ROI_X, config.ROI_Y, config.ROI_W, config.ROI_H))
        _, jpeg = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')

@app.route('/')
def video_feed():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    # Dùng IP từ .env/config
    app.run(host=config.WEB_HOST, port=5000)