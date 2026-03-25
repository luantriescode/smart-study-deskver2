# 📦 PROJECT MANIFEST

Smart Study Desk System - Complete File Listing

---

## 📋 Project Overview

```
smart-study-desk/
├── Documentation (8 files)
├── Configuration (1 file)
├── Main Application (1 file)
├── Setup Script (1 file)
├── Python Modules (11 files)
├── Web Assets (1 file)
└── Logs Directory (empty)
```

---

## 📄 Documentation Files

### Core Documentation

| File | Purpose | Status |
|------|---------|--------|
| `README.md` | Project overview, quick start, features | ✅ Complete |
| `QUICK_START.md` | 10-minute setup guide | ✅ Complete |
| `PROJECT_MANIFEST.md` | This file - complete listing | ✅ Complete |

### Deployment Guides

| File | Purpose | Status |
|------|---------|--------|
| `STEP_1_DEPLOYMENT_GUIDE.md` | OS + Network setup (1 day) | ✅ Complete |
| `STEP_2_GPIO_RELAY_GUIDE.md` | GPIO + Relay testing (0.5 day) | ✅ Complete |
| `STEP_3_CAMERA_GUIDE.md` | Camera pipeline optimization (1 day) | ✅ Complete |

### Technical Documentation

| File | Purpose | Status |
|------|---------|--------|
| `SYSTEM_ARCHITECTURE.md` | System design, data flows, algorithms | ✅ Complete |
| `TESTING_CHECKLIST.md` | 150+ test items for full verification | ✅ Complete |
| `API_DOCUMENTATION.md` | REST API reference for web dashboard | ✅ Complete |

---

## 🔧 Configuration & Setup

### `config.py`
**Purpose:** Central configuration file

**Content:**
- GPIO pin configuration (relay, LED)
- Camera settings (resolution, FPS, ROI)
- Motion detection thresholds
- Face & eye detection settings
- Posture detection thresholds
- State machine timers
- Telegram bot credentials
- Web server settings
- Logging configuration
- Validation function

**Usage:**
```python
import config
print(config.RELAY_PIN)  # 17
print(config.FRAME_WIDTH)  # 320
```

### `requirements.txt`
**Purpose:** Python package dependencies

**Packages:**
- `opencv-python==4.8.0.76` - Computer vision
- `Flask==3.0.0` - Web framework
- `requests==2.31.0` - HTTP library
- `RPi.GPIO==0.7.0` - GPIO control (Raspberry Pi)
- `numpy==1.24.3` - Numerical computing
- `python-dotenv==1.0.0` - Environment variables

### `setup.sh`
**Purpose:** Automated setup script for Raspberry Pi

**What it does:**
1. Updates system packages
2. Installs system dependencies
3. Installs Python packages
4. Configures GPIO
5. Creates .env file
6. Sets up systemd service
7. Tests installations

**Usage:**
```bash
bash setup.sh
```

---

## 🚀 Main Application

### `main.py`
**Purpose:** Main system orchestrator

**Responsibilities:**
- Initialize all modules (camera, detectors, relay, etc.)
- Implement main processing loop
- Coordinate vision pipeline
- Manage state machine updates
- Handle logging
- Cleanup on shutdown

**Entry Point:**
```bash
python3 main.py
```

**Key Classes:**
- `SmartStudyDeskSystem` - Main orchestrator

---

## 👁️ Vision Pipeline Modules

Located in `vision/` directory

### `vision/camera.py`
**Purpose:** Manage USB webcam

**Key Functions:**
- `Camera.read()` - Read frame from camera
- `Camera.resize_frame()` - Resize frame
- `Camera.crop_roi()` - Crop Region of Interest
- `Camera.to_gray()` - Convert BGR to grayscale
- `Camera.to_hsv()` - Convert BGR to HSV

**Usage:**
```python
from vision.camera import Camera

camera = Camera(width=640, height=480)
ret, frame = camera.read()
resized = camera.resize_frame(frame, 320, 240)
camera.release()
```

**Test:**
```bash
python3 vision/camera.py
```

### `vision/motion_detector.py`
**Purpose:** Detect person in ROI using background subtraction

**Key Functions:**
- `MotionDetector.detect()` - Detect motion in ROI
- `MotionDetector.detect_contours()` - Get motion contours
- `MotionDetector.draw_motion()` - Visualize motion
- `MotionDetector.reset()` - Reset background model

**Algorithm:** MOG2 (Mixture of Gaussians)

**Usage:**
```python
from vision.motion_detector import MotionDetector

detector = MotionDetector()
is_person, mask = detector.detect(frame, roi=(50, 50, 220, 140))
```

**Test:**
```bash
python3 vision/motion_detector.py
```

### `vision/face_detector.py`
**Purpose:** Detect faces and eyes (for sleep detection)

**Key Functions:**
- `FaceDetector.detect_faces()` - Detect face location
- `FaceDetector.detect_eyes_in_face()` - Detect eyes in face
- `FaceDetector.is_eyes_closed()` - Check if eyes closed
- `FaceDetector.detect_sleep()` - Detect sustained eye closure
- `FaceDetector.draw_faces()` - Visualize detections

**Algorithm:** Haar Cascade Classifiers

**Usage:**
```python
from vision.face_detector import FaceDetector

detector = FaceDetector()
faces = detector.detect_faces(frame)
for face in faces:
    is_sleeping = detector.detect_sleep(frame, face)
```

**Test:**
```bash
python3 vision/face_detector.py
```

### `vision/posture_detector.py`
**Purpose:** Detect head angle and bad posture

**Key Functions:**
- `PostureDetector.detect_posture()` - Get head angle
- `PostureDetector.is_bad_posture()` - Check if posture bad
- `PostureDetector.draw_posture()` - Visualize posture
- `PostureDetectorAdvanced` - DLib-based (optional)

**Algorithm:** Face detection + head angle estimation

**Usage:**
```python
from vision.posture_detector import PostureDetector

detector = PostureDetector()
angle = detector.detect_posture(frame)
if detector.is_bad_posture(frame):
    print("Bad posture!")
```

**Test:**
```bash
python3 vision/posture_detector.py
```

---

## 🧠 Core Logic Modules

Located in `core/` directory

### `core/state_machine.py`
**Purpose:** Control light state and logic

**States:**
- `OFF` - Light off
- `ON` - Light on
- `COUNTDOWN` - Waiting to turn off

**Key Functions:**
- `StateMachine.update()` - Update state based on person detection
- `StateMachine.get_state()` - Get current state
- `StateMachine.force_on()` - Manual override on
- `StateMachine.force_off()` - Manual override off

**Usage:**
```python
from core.state_machine import StateMachine

sm = StateMachine(relay=relay_controller)
sm.update(person_detected=True)  # Light ON
sm.update(person_detected=False) # Start countdown
```

**Test:**
```bash
python3 core/state_machine.py
```

### `core/study_timer.py`
**Purpose:** Track study sessions and log events

**Key Functions:**
- `StudyTimer.update()` - Update session state
- `StudyTimer.log_event()` - Log event (sleep, posture, etc.)
- `StudyTimer.get_stats()` - Get current statistics
- `StudyTimer.get_events()` - Get event list
- `StudyTimer.save_log()` - Save log to JSON file
- `StudyTimer.format_stats()` - Format stats as string

**Usage:**
```python
from core.study_timer import StudyTimer

timer = StudyTimer()
timer.update(person_detected=True)
timer.log_event("SLEEP_DETECTED", {"face_id": 0})
stats = timer.get_stats()
timer.save_log()
```

**Test:**
```bash
python3 core/study_timer.py
```

---

## ⚡ Hardware Control Module

Located in `hardware/` directory

### `hardware/relay.py`
**Purpose:** Control GPIO relay for light

**Key Classes:**
- `RelayController` - Basic relay control
- `PWMRelayController` - PWM brightness control
- `RelaySafetyMonitor` - Safety monitoring

**Key Functions:**
- `RelayController.on()` - Turn relay ON
- `RelayController.off()` - Turn relay OFF
- `RelayController.toggle()` - Toggle relay
- `RelayController.get_state()` - Get relay state
- `RelayController.get_info()` - Get relay info

**Usage:**
```python
from hardware.relay import RelayController

relay = RelayController(pin=17)
relay.on()   # Turn on light
relay.off()  # Turn off light
relay.cleanup()
```

**Test:**
```bash
python3 hardware/relay.py
```

---

## 📱 Communication Module

Located in `communication/` directory

### `communication/telegram_bot.py`
**Purpose:** Send alerts and notifications via Telegram

**Key Classes:**
- `TelegramBot` - Bot for sending alerts
- `TelegramCommandHandler` - Handle Telegram commands

**Key Functions:**
- `TelegramBot.send_message()` - Send text alert
- `TelegramBot.send_photo()` - Send photo with caption
- `TelegramBot.alert_sleep()` - Alert on sleep detected
- `TelegramBot.alert_posture()` - Alert on bad posture
- `TelegramBot.alert_stats()` - Send statistics

**Usage:**
```python
from communication.telegram_bot import TelegramBot

bot = TelegramBot()
bot.send_message("Hello from Smart Study Desk!")
bot.send_photo(frame, "Sleep detected!")
```

**Test:**
```bash
python3 communication/telegram_bot.py
```

---

## 🌐 Web Dashboard Module

Located in `web/` directory

### `web/app.py`
**Purpose:** Flask web server for dashboard

**Key Endpoints:**
- `GET /` - Main dashboard page
- `GET /api/status` - System status
- `GET /api/stats` - Study statistics
- `POST /api/light/<action>` - Light control
- `GET /api/events` - Event history
- `GET /api/screenshot` - Latest frame
- `GET /api/config` - Configuration
- `GET /video_feed` - MJPEG stream

**Usage:**
```bash
python3 web/app.py
```

**Access:** `http://192.168.1.100:5000`

### `web/templates/index.html`
**Purpose:** Dashboard UI template

**Features:**
- Light control buttons
- System status display
- Study statistics
- Camera live feed
- Recent events list
- Responsive design

---

## 📦 Package Structure

### `vision/__init__.py`
Empty init file for vision package

### `core/__init__.py`
Empty init file for core package

### `hardware/__init__.py`
Empty init file for hardware package

### `communication/__init__.py`
Empty init file for communication package

### `web/__init__.py`
Empty init file for web package

---

## 📊 File Statistics

```
Python Files:        11
Documentation Files:  8
Configuration Files:  2
Setup Scripts:        1
Web Templates:        1
────────────────────────
Total Files:         23

Lines of Code:       ~3,500
Documentation:       ~2,500 lines
Total:               ~6,000 lines
```

---

## 🗂️ Directory Structure

```
smart-study-desk/
│
├── 📄 README.md                          (Project overview)
├── 📄 QUICK_START.md                     (10-min setup)
├── 📄 SYSTEM_ARCHITECTURE.md             (Technical design)
├── 📄 TESTING_CHECKLIST.md               (150+ tests)
├── 📄 API_DOCUMENTATION.md               (REST API)
├── 📄 PROJECT_MANIFEST.md                (This file)
├── 📄 STEP_1_DEPLOYMENT_GUIDE.md         (OS setup)
├── 📄 STEP_2_GPIO_RELAY_GUIDE.md         (Relay test)
├── 📄 STEP_3_CAMERA_GUIDE.md             (Camera setup)
│
├── 🐍 config.py                          (Configuration)
├── 🐍 main.py                            (Main loop)
├── 🐍 requirements.txt                   (Dependencies)
├── 📜 setup.sh                           (Setup script)
│
├── 📂 vision/                            (Computer vision)
│   ├── __init__.py
│   ├── camera.py                         (Webcam)
│   ├── motion_detector.py                (Person detection)
│   ├── face_detector.py                  (Face + eyes)
│   └── posture_detector.py               (Head angle)
│
├── 📂 core/                              (Core logic)
│   ├── __init__.py
│   ├── state_machine.py                  (Light control)
│   └── study_timer.py                    (Session tracking)
│
├── 📂 hardware/                          (Hardware control)
│   ├── __init__.py
│   └── relay.py                          (GPIO relay)
│
├── 📂 communication/                     (External comm)
│   ├── __init__.py
│   └── telegram_bot.py                   (Alerts)
│
├── 📂 web/                               (Web server)
│   ├── __init__.py
│   ├── app.py                            (Flask app)
│   ├── templates/
│   │   └── index.html                    (Dashboard UI)
│   └── static/                           (CSS, JS - optional)
│
└── 📂 logs/                              (Log files)
    └── (Created on first run)
```

---

## 📖 File Dependencies

```
main.py
  ├─ config.py
  ├─ vision/camera.py
  ├─ vision/motion_detector.py
  ├─ vision/face_detector.py
  ├─ vision/posture_detector.py
  ├─ core/state_machine.py
  ├─ core/study_timer.py
  ├─ hardware/relay.py
  ├─ communication/telegram_bot.py
  └─ logging (Python standard)

web/app.py
  ├─ config.py
  ├─ vision/camera.py
  ├─ core/state_machine.py
  ├─ core/study_timer.py
  ├─ hardware/relay.py
  ├─ communication/telegram_bot.py
  └─ Flask
```

---

## 🚀 Execution Flow

1. **Startup:** `python3 main.py`
   - Load config.py
   - Initialize modules
   - Start main loop

2. **Main Loop:**
   - Read frame from camera
   - Detect motion/person
   - Detect face/eyes
   - Detect posture
   - Update state machine
   - Log events
   - Send alerts (if needed)

3. **Web Server:** `python3 web/app.py`
   - Flask server starts on port 5000
   - Serves dashboard UI
   - Provides REST API
   - Streams camera feed

---

## 📝 File Modification Guide

### To customize:

| Change | File |
|--------|------|
| GPIO pin | `config.py` RELAY_PIN |
| Camera resolution | `config.py` CAMERA_WIDTH/HEIGHT |
| Motion threshold | `config.py` MOTION_THRESHOLD |
| Sleep detection time | `config.py` EYE_CLOSED_FRAMES |
| Telegram token | `config.py` TELEGRAM_TOKEN |
| Web port | `config.py` WEB_PORT |
| UI design | `web/templates/index.html` |

---

## ✅ Completeness Checklist

- ✅ All documentation complete
- ✅ All source code implemented
- ✅ All modules tested individually
- ✅ Integration tested
- ✅ API documented
- ✅ Setup automated
- ✅ Configuration centralized
- ✅ Logging implemented
- ✅ Error handling included
- ✅ Security considered

---

## 📦 Distribution

### Archive Contents
- All source files (.py)
- All documentation (.md)
- Configuration template (.txt)
- Setup script (.sh)
- No log files or temporary files

### Extract:
```bash
tar -xzf smart-study-desk.tar.gz
cd smart-study-desk
```

### Size:
- Uncompressed: ~500KB
- Compressed: ~50KB
- With logs: Varies

---

## 🔄 Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2024-03-19 | Initial release |
| | | - STEP 1-3 complete |
| | | - Core functionality |
| | | - Full documentation |

---

## 🎯 Next Steps

After deploying this package:

1. Follow `QUICK_START.md` (10 min)
2. Run `setup.sh` (5-10 min)
3. Complete `STEP_1_DEPLOYMENT_GUIDE.md` (1 day)
4. Complete `STEP_2_GPIO_RELAY_GUIDE.md` (0.5 day)
5. Complete `STEP_3_CAMERA_GUIDE.md` (1 day)
6. Use `TESTING_CHECKLIST.md` for verification
7. Reference `SYSTEM_ARCHITECTURE.md` for technical details
8. Use `API_DOCUMENTATION.md` for integration

---

## 📞 Support

- Check logs: `tail -f logs/study_system.log`
- Test modules: `python3 <module>.py`
- Review documentation: See list above
- Check API: `curl http://192.168.1.100:5000/api/status`

---

**Document Version:** 1.0
**Last Updated:** March 2024
**Status:** Complete - Ready for Deployment
