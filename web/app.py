"""
WEB/APP.PY - Flask Web Dashboard
=================================
Quản lý:
  - Web server
  - Camera stream
  - Control buttons (light on/off)
  - Statistics display
"""

import cv2
import logging
import threading
from flask import Flask, render_template, jsonify, request
from datetime import datetime

import config
from vision.camera import Camera
from core.state_machine import StateMachine
from core.study_timer import StudyTimer
from hardware.relay import RelayController
from communication.telegram_bot import TelegramBot

logger = logging.getLogger(__name__)


# ============================================
# FLASK APP SETUP
# ============================================

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config['JSON_SORT_KEYS'] = False

# Global state
state = {
    "camera": None,
    "relay": None,
    "state_machine": None,
    "study_timer": None,
    "telegram_bot": None,
    "streaming": False,
    "last_frame": None
}


# ============================================
# INITIALIZATION
# ============================================

def init_system():
    """Khởi tạo hệ thống"""
    logger.info("Initializing web system...")
    
    try:
        state["camera"] = Camera(
            width=config.CAMERA_WIDTH,
            height=config.CAMERA_HEIGHT
        )
        logger.info("✅ Camera initialized")
    except Exception as e:
        logger.error(f"❌ Camera init failed: {e}")
    
    try:
        state["relay"] = RelayController()
        logger.info("✅ Relay initialized")
    except Exception as e:
        logger.error(f"❌ Relay init failed: {e}")
    
    try:
        state["state_machine"] = StateMachine(relay=state["relay"])
        logger.info("✅ State machine initialized")
    except Exception as e:
        logger.error(f"❌ State machine init failed: {e}")
    
    try:
        state["study_timer"] = StudyTimer()
        logger.info("✅ Study timer initialized")
    except Exception as e:
        logger.error(f"❌ Study timer init failed: {e}")
    
    try:
        state["telegram_bot"] = TelegramBot()
        logger.info("✅ Telegram bot initialized")
    except Exception as e:
        logger.warning(f"⚠️  Telegram bot init failed (optional): {e}")


# ============================================
# CAMERA STREAMING
# ============================================

def generate_frames():
    """Generate frames for video streaming"""
    if not state["camera"]:
        return
    
    while state["streaming"]:
        try:
            ret, frame = state["camera"].read()
            
            if not ret:
                logger.error("Failed to read frame")
                break
            
            # Resize frame
            frame = state["camera"].resize_frame(
                frame,
                width=config.FRAME_WIDTH,
                height=config.FRAME_HEIGHT
            )
            
            # Store last frame
            state["last_frame"] = frame
            
            # Encode frame to JPEG
            success, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            
            # MJPEG streaming format
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n'
                   b'Content-Length: ' + str(len(frame_bytes)).encode() + b'\r\n\r\n'
                   + frame_bytes + b'\r\n')
        
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            break


# ============================================
# ROUTES
# ============================================

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    """Video stream endpoint"""
    state["streaming"] = True
    return None, 206, {
        'Content-Type': 'multipart/x-mixed-replace; boundary=frame'
    }


@app.route('/api/status')
def api_status():
    """Get system status"""
    status = {
        "timestamp": datetime.now().isoformat(),
        "relay": {
            "state": "ON" if state["relay"] and state["relay"].is_on else "OFF",
            "pin": config.RELAY_PIN
        } if state["relay"] else None,
        "state_machine": {
            "state": state["state_machine"].current_state.value,
            "countdown": state["state_machine"].get_countdown_remaining()
        } if state["state_machine"] else None,
        "camera": {
            "status": "OK" if state["camera"] else "ERROR"
        }
    }
    
    return jsonify(status)


@app.route('/api/stats')
def api_stats():
    """Get study statistics"""
    stats = state["study_timer"].get_stats() if state["study_timer"] else {}
    return jsonify(stats)


@app.route('/api/light/<action>', methods=['POST'])
def api_light_control(action):
    """Control light"""
    if not state["relay"] or not state["state_machine"]:
        return jsonify({"error": "Relay not initialized"}), 500
    
    try:
        if action == "on":
            state["state_machine"].force_on()
            result = "Light turned ON"
        
        elif action == "off":
            state["state_machine"].force_off()
            result = "Light turned OFF"
        
        elif action == "toggle":
            state["relay"].toggle()
            result = "Light toggled"
        
        else:
            return jsonify({"error": f"Unknown action: {action}"}), 400
        
        logger.info(f"💡 Web control: {result}")
        
        if state["telegram_bot"]:
            state["telegram_bot"].send_message(f"💡 Web Control: {result}")
        
        return jsonify({"status": "success", "message": result})
    
    except Exception as e:
        logger.error(f"Light control error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/events')
def api_events():
    """Get recent events"""
    limit = request.args.get('limit', 10, type=int)
    event_type = request.args.get('type', None)
    
    events = state["study_timer"].get_events(
        event_type=event_type,
        limit=limit
    ) if state["study_timer"] else []
    
    return jsonify({"events": events})


@app.route('/api/screenshot')
def api_screenshot():
    """Get latest screenshot"""
    if state["last_frame"] is None:
        return jsonify({"error": "No frame available"}), 404
    
    success, buffer = cv2.imencode('.jpg', state["last_frame"])
    frame_bytes = buffer.tobytes()
    
    return frame_bytes, 200, {'Content-Type': 'image/jpeg'}


@app.route('/api/config')
def api_config():
    """Get configuration"""
    config_data = {
        "camera": {
            "width": config.FRAME_WIDTH,
            "height": config.FRAME_HEIGHT,
            "roi": {
                "x": config.ROI_X,
                "y": config.ROI_Y,
                "w": config.ROI_W,
                "h": config.ROI_H
            }
        },
        "thresholds": {
            "motion": config.MOTION_THRESHOLD,
            "eye_closed_frames": config.EYE_CLOSED_FRAMES,
            "head_down": config.HEAD_DOWN_THRESHOLD
        },
        "timers": {
            "person_lost_delay": config.PERSON_LOST_DELAY,
            "session_timeout": config.SESSION_TIMEOUT
        }
    }
    
    return jsonify(config_data)


# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def not_found(e):
    """404 handler"""
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(e):
    """500 handler"""
    return jsonify({"error": "Server error"}), 500


# ============================================
# CLEANUP
# ============================================

def cleanup():
    """Cleanup resources"""
    logger.info("Cleaning up web server...")
    
    state["streaming"] = False
    
    if state["camera"]:
        state["camera"].release()
    
    if state["relay"]:
        state["relay"].off()
    
    if state["study_timer"]:
        state["study_timer"].save_log()


# ============================================
# MAIN
# ============================================

def main():
    """Run web server"""
    init_system()
    
    try:
        logger.info(f"Starting Flask server on {config.WEB_HOST}:{config.WEB_PORT}")
        app.run(
            host=config.WEB_HOST,
            port=config.WEB_PORT,
            debug=config.WEB_DEBUG,
            threaded=True
        )
    
    except Exception as e:
        logger.error(f"Server error: {e}")
    
    finally:
        cleanup()


if __name__ == "__main__":
    main()
