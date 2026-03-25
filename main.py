"""
MAIN.PY - Main Loop & System Orchestration
================================================
Quản lý:
  - Khởi tạo hardware + software
  - Vòng lặp chính (Main Loop)
  - Cleanup khi tắt
  - Error handling & recovery
"""

import sys
import time
import logging
from pathlib import Path
from datetime import datetime

# Import local modules
import config
from vision.camera import Camera
from vision.motion_detector import MotionDetector
from vision.face_detector import FaceDetector
from vision.posture_detector import PostureDetector
from core.state_machine import StateMachine
from core.study_timer import StudyTimer
from hardware.relay import RelayController
from communication.telegram_bot import TelegramBot

# ============================================
# LOGGING SETUP
# ============================================

logging.basicConfig(
    level=config.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


# ============================================
# MAIN SYSTEM CLASS
# ============================================

class SmartStudyDeskSystem:
    """Hệ thống học tập thông minh chính"""
    
    def __init__(self):
        """Khởi tạo tất cả các module"""
        logger.info("=" * 60)
        logger.info("🚀 INITIALIZING SMART STUDY DESK SYSTEM")
        logger.info("=" * 60)
        
        # Validate config
        if not config.validate_config():
            raise RuntimeError("Config validation failed!")
        
        # Hardware initialization
        logger.info("📦 Initializing hardware...")
        try:
            self.relay = RelayController(config.RELAY_PIN)
            logger.info("✅ Relay controller initialized")
        except Exception as e:
            logger.error(f"❌ Failed to init relay: {e}")
            self.relay = None
        
        # Vision pipeline initialization
        logger.info("📹 Initializing vision pipeline...")
        try:
            self.camera = Camera(
                width=config.CAMERA_WIDTH,
                height=config.CAMERA_HEIGHT,
                fps=config.CAMERA_FPS
            )
            logger.info("✅ Camera initialized")
        except Exception as e:
            logger.error(f"❌ Failed to init camera: {e}")
            raise
        
        # Motion detection
        try:
            self.motion_detector = MotionDetector()
            logger.info("✅ Motion detector initialized")
        except Exception as e:
            logger.error(f"❌ Failed to init motion detector: {e}")
            self.motion_detector = None
        
        # Face detection
        try:
            self.face_detector = FaceDetector()
            logger.info("✅ Face detector initialized")
        except Exception as e:
            logger.error(f"❌ Failed to init face detector: {e}")
            self.face_detector = None
        
        # Posture detection
        try:
            self.posture_detector = PostureDetector()
            logger.info("✅ Posture detector initialized")
        except Exception as e:
            logger.error(f"❌ Failed to init posture detector: {e}")
            self.posture_detector = None
        
        # State machine
        self.state_machine = StateMachine(relay=self.relay)
        logger.info("✅ State machine initialized")
        
        # Study timer
        self.study_timer = StudyTimer()
        logger.info("✅ Study timer initialized")
        
        # Telegram bot
        try:
            self.telegram_bot = TelegramBot()
            logger.info("✅ Telegram bot initialized")
        except Exception as e:
            logger.warning(f"⚠️  Telegram bot failed (optional): {e}")
            self.telegram_bot = None
        
        # State tracking
        self.running = False
        self.frame_count = 0
        self.start_time = time.time()
        
        logger.info("=" * 60)
        logger.info("✅ SYSTEM INITIALIZATION COMPLETE")
        logger.info("=" * 60)
    
    # ============================================
    # MAIN LOOP
    # ============================================
    
    def run(self):
        """Vòng lặp chính"""
        self.running = True
        logger.info("🎬 Starting main loop...")
        
        try:
            while self.running:
                # 1️⃣ Capture frame
                ret, frame = self.camera.read()
                if not ret:
                    logger.error("❌ Failed to read frame from camera")
                    break
                
                # 2️⃣ Resize frame
                resized = self.camera.resize_frame(
                    frame,
                    width=config.FRAME_WIDTH,
                    height=config.FRAME_HEIGHT
                )
                
                # 3️⃣ Motion detection
                person_detected = False
                if self.motion_detector:
                    person_detected, motion_mask = self.motion_detector.detect(
                        resized,
                        roi=(config.ROI_X, config.ROI_Y, config.ROI_W, config.ROI_H)
                    )
                
                # 4️⃣ Update state machine
                self.state_machine.update(person_detected)
                
                # 5️⃣ Face & Eye detection (nếu person detected)
                if person_detected and self.face_detector:
                    faces = self.face_detector.detect_faces(resized)
                    
                    if faces:
                        for face in faces:
                            # Check if eyes closed
                            is_sleeping = self.face_detector.detect_sleep(resized, face)
                            
                            if is_sleeping:
                                logger.warning("😴 SLEEP DETECTED!")
                                # Capture and alert
                                if self.telegram_bot:
                                    self.telegram_bot.alert_sleep(resized)
                                
                                # Log
                                self.study_timer.log_event("SLEEP_DETECTED")
                
                # 6️⃣ Posture detection
                if person_detected and self.posture_detector:
                    head_angle = self.posture_detector.detect_posture(resized)
                    
                    if head_angle is not None:
                        if abs(head_angle) > config.HEAD_DOWN_THRESHOLD:
                            logger.warning(f"⚠️  BAD POSTURE: Head angle = {head_angle}°")
                            
                            if self.telegram_bot:
                                self.telegram_bot.alert_posture(resized, head_angle)
                            
                            self.study_timer.log_event("BAD_POSTURE")
                
                # 7️⃣ Update study timer
                self.study_timer.update(person_detected)
                
                # 8️⃣ Logging (every 30 frames)
                self.frame_count += 1
                if self.frame_count % 30 == 0:
                    elapsed = time.time() - self.start_time
                    fps = self.frame_count / elapsed
                    state = self.state_machine.current_state
                    timer = self.study_timer.get_session_time()
                    
                    logger.debug(
                        f"Frame {self.frame_count} | FPS: {fps:.1f} | "
                        f"State: {state} | Session: {timer}s | "
                        f"Person: {person_detected}"
                    )
                
                # 9️⃣ Small delay (CPU friendly)
                time.sleep(0.01)  # ~100ms
        
        except KeyboardInterrupt:
            logger.info("⏸️  Received SIGINT, shutting down...")
        except Exception as e:
            logger.error(f"❌ Error in main loop: {e}", exc_info=True)
        finally:
            self.cleanup()
    
    # ============================================
    # CLEANUP
    # ============================================
    
    def cleanup(self):
        """Dọn dẹp tài nguyên"""
        logger.info("🧹 Cleaning up...")
        
        self.running = False
        
        # Turn off light
        if self.relay:
            self.relay.off()
            logger.info("💡 Light turned OFF")
        
        # Close camera
        if self.camera:
            self.camera.release()
            logger.info("📹 Camera released")
        
        # Save study log
        if self.study_timer:
            self.study_timer.save_log()
            logger.info("📊 Study log saved")
        
        logger.info("=" * 60)
        logger.info("✅ SYSTEM SHUTDOWN COMPLETE")
        logger.info("=" * 60)


# ============================================
# ENTRY POINT
# ============================================

def main():
    """Entry point"""
    logger.info(f"Starting at {datetime.now()}")
    
    system = SmartStudyDeskSystem()
    system.run()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
