import cv2
import numpy as np
import config

class MotionDetector:
    def __init__(self):
        # Thuật toán trừ nền tối ưu cho phần cứng yếu
        self.fgbg = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=16, detectShadows=False)
        # Ngưỡng diện tích chuyển động (pixel) từ config
        self.min_area = config.MOTION_THRESHOLD 

    def detect(self, frame):
        # 1. Cắt vùng ROI để xử lý (Tiết kiệm CPU)
        roi_frame = frame[config.ROI_Y:config.ROI_Y+config.ROI_H, 
                          config.ROI_X:config.ROI_X+config.ROI_W]
        
        # 2. Làm mờ để giảm nhiễu
        gray = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # 3. Áp dụng thuật toán trừ nền
        fgmask = self.fgbg.apply(blur)
        
        # 4. Tìm các vùng chuyển động (Contours)
        contours, _ = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        motion_detected = False
        for contour in contours:
            if cv2.contourArea(contour) > self.min_area:
                motion_detected = True
                break
                
        return motion_detected, fgmask