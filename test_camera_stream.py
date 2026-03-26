import cv2
import time
import os
import sys

# Import config và Camera handler từ source code của bạn
try:
    import config
    from vision.camera import Camera
except ImportError:
    print("❌ Lỗi: Không tìm thấy config.py hoặc vision/camera.py")
    sys.exit(1)

def main():
    # Khử log cảnh báo để màn hình terminal sạch sẽ 
    os.environ["OPENCV_LOG_LEVEL"] = "ERROR"
    
    print("🚀 Đang khởi động Camera Test (Local Stream)...")
    print(f"📡 Cấu hình: {config.CAMERA_WIDTH}x{config.CAMERA_HEIGHT} | Format: {config.CAMERA_FOURCC}")
    print("💡 Nhấn phím 'q' để đóng cửa sổ.")

    # Khởi tạo camera với các thông số tối ưu cho Pi B+ 
    cam = Camera(
        device_id=config.CAMERA_INDEX,
        width=config.CAMERA_WIDTH,
        height=config.CAMERA_HEIGHT,
        fps=config.CAMERA_FPS,
        fourcc=config.CAMERA_FOURCC,
        buffer_size=config.CAMERA_BUFFER_SIZE
    )

    window_name = "Smart Study Desk - Live Preview"
    cv2.namedWindow(window_name)

    try:
        while True:
            start_time = time.time()
            
            # Đọc frame từ webcam [cite: 3]
            ret, frame = cam.read()
            if not ret or frame is None:
                print("⚠️ Không thể đọc frame từ camera.")
                break

            # Vẽ vùng ROI (vùng nhận diện người) từ config [cite: 1, 12]
            # Mặc định ROI là: (50, 50, 220, 140)
            debug_frame = cam.draw_roi(frame, (config.ROI_X, config.ROI_Y, config.ROI_W, config.ROI_H))

            # Tính toán và hiển thị FPS thực tế [cite: 3]
            # Mục tiêu đạt ~15fps trên Pi B+ 
            fps = 1.0 / (time.time() - start_time)
            cv2.putText(debug_frame, f"FPS: {fps:.1f}", (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
            cv2.putText(debug_frame, "Status: Testing", (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            # Đẩy hình ảnh ra cửa sổ màn hình
            cv2.imshow(window_name, debug_frame)

            # Thoát nếu nhấn phím 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("\n🛑 Đã dừng bởi người dùng.")
    finally:
        cam.release()
        cv2.destroyAllWindows()
        print("✅ Đã đóng camera và giải phóng tài nguyên.")

if __name__ == "__main__":
    main()