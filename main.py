import time
import sys
import os
import cv2
import config
from vision.camera import Camera
from vision.motion_detector import MotionDetector
from hardware.relay import RelayController # Sử dụng class relay bạn vừa test thành công

def main():
    # Khởi tạo các module
    cam = Camera(device_id=config.CAMERA_INDEX, width=config.CAMERA_WIDTH, height=config.CAMERA_HEIGHT)
    detector = MotionDetector()
    relay = RelayController() # Class này sẽ dùng mã GPIO bạn vừa test
    
    print("🚀 HỆ THỐNG SMART STUDY DESK ĐANG CHẠY...")
    print(f"💡 Ngưỡng: {config.MOTION_THRESHOLD} | Delay tắt: {config.PERSON_LOST_DELAY}s")

    last_motion_time = time.time()
    is_light_on = False

    try:
        while True:
            success, frame = cam.read()
            if not success: continue

            # Phát hiện chuyển động
            has_motion, _ = detector.detect(frame)

            if has_motion:
                last_motion_time = time.time()
                if not is_light_on:
                    print("👤 PHÁT HIỆN NGƯỜI -> BẬT ĐÈN (CLICK!)")
                    relay.turn_on()
                    is_light_on = True
            else:
                # Nếu không thấy người, kiểm tra thời gian chờ
                elapsed = time.time() - last_motion_time
                if is_light_on and elapsed > config.PERSON_LOST_DELAY:
                    print("🌑 KHÔNG CÓ NGƯỜI -> TẮT ĐÈN (CLICK!)")
                    relay.turn_off()
                    is_light_on = False
            
            # Nghỉ một chút để Pi B+ không bị nóng
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n🛑 Đang dừng...")
    finally:
        relay.turn_off()
        cam.release()

if __name__ == "__main__":
    main()