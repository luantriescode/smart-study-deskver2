import cv2
import time
import os
import sys

# Ép Python tìm kiếm module ở thư mục hiện tại 
# Điều này giúp nhận diện config.py và folder vision
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

try:
    import config
    from vision.camera import Camera
    print("✅ Đã kết nối với config.py và vision/camera.py")
except ImportError as e:
    print(f"❌ Lỗi Import: {e}")
    print("Mẹo: Đảm bảo bạn đang đứng ở thư mục smart-study-deskver2 để chạy.")
    sys.exit(1)

def main():
    os.environ["OPENCV_LOG_LEVEL"] = "ERROR"
    
    # Khởi tạo camera với cấu hình MJPG 320x240 từ config
    cam = Camera(
        device_id=config.CAMERA_INDEX,
        width=config.CAMERA_WIDTH,
        height=config.CAMERA_HEIGHT,
        fps=config.CAMERA_FPS,
        fourcc=config.CAMERA_FOURCC
    )

    window_name = "Smart Study Desk - Live Stream"
    
    try:
        while True:
            start_time = time.time()
            ret, frame = cam.read()
            if not ret or frame is None:
                break

            # Vẽ vùng xanh ROI (50, 50, 220, 140) để căn chỉnh
            debug_frame = cam.draw_roi(frame, (config.ROI_X, config.ROI_Y, config.ROI_W, config.ROI_H))

            fps = 1.0 / (time.time() - start_time)
            cv2.putText(debug_frame, f"FPS: {fps:.1f}", (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            cv2.imshow(window_name, debug_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cam.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()