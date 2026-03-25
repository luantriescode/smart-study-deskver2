# 🏗️ SYSTEM ARCHITECTURE

## 📐 System-Level Design

```
┌─────────────────────────────────────────────────────────────────┐
│                    SMART STUDY DESK SYSTEM                      │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                       INPUT LAYER                                │
├──────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   Webcam     │    │  Manual UI   │    │  Telegram    │      │
│  │   (USB)      │    │  (Web/Phone) │    │  (Commands)  │      │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘      │
│         │                    │                    │               │
└─────────┼────────────────────┼────────────────────┼───────────────┘
          │                    │                    │
          ▼                    ▼                    ▼
┌──────────────────────────────────────────────────────────────────┐
│                      PROCESSING LAYER                            │
├──────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              VISION PIPELINE (main.py)                   │  │
│  │                                                          │  │
│  │  1. Camera.read() → Frame                               │  │
│  │  2. Camera.resize() → 320x240                           │  │
│  │  3. MotionDetector.detect() → Person detected?          │  │
│  │  4. FaceDetector.detect() → Face location               │  │
│  │  5. Eye status check → Sleep?                           │  │
│  │  6. PostureDetector.detect() → Head angle               │  │
│  │                                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              LOGIC LAYER (state_machine.py)              │  │
│  │                                                          │  │
│  │  Person detected?                                       │  │
│  │  ├─ YES → Turn light ON                                 │  │
│  │  └─ NO  → Start 10s countdown → Turn OFF                │  │
│  │                                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │            EVENT TRACKING (study_timer.py)               │  │
│  │                                                          │  │
│  │  - Track study sessions                                 │  │
│  │  - Log sleep events                                     │  │
│  │  - Log posture issues                                   │  │
│  │                                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
          │                    │                    │
          ▼                    ▼                    ▼
┌──────────────────────────────────────────────────────────────────┐
│                      OUTPUT LAYER                                │
├──────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   GPIO Relay │    │ Telegram Bot │    │ Web Server   │      │
│  │  (Light on/off)   │  (Alerts)    │    │  (Dashboard) │      │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘      │
│         │                    │                    │               │
└─────────┼────────────────────┼────────────────────┼───────────────┘
          │                    │                    │
          ▼                    ▼                    ▼
┌──────────────────────────────────────────────────────────────────┐
│                     HARDWARE/EXTERNAL                            │
├──────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │  Relay 5V    │    │ Internet API │    │ User Browser │      │
│  │  220V Light  │    │  Telegram    │    │   (HTTP)     │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📊 Data Flow Diagram

```
FRAME CAPTURE
     │
     ▼
MOTION DETECTION
     │
     ├─ Person detected? ─────────────────┐
     │                                     │
     ▼                                     ▼
   YES (Continue)                        NO (Start countdown)
     │                                     │
     ├─ FACE DETECTION                    └─ Wait 10s
     │  ├─ Detect face location              │
     │  └─ Check eye status                  ▼
     │     └─ Closed > 5s? ─ YES ─ SLEEP ALERT
     │                      │
     │                      ▼
     │                 LOG EVENT
     │                 SEND TELEGRAM
     │
     ├─ POSTURE DETECTION
     │  ├─ Detect head angle
     │  └─ Bad posture? ─ YES ─ POSTURE ALERT
     │                   │
     │                   ▼
     │              LOG EVENT
     │              SEND TELEGRAM
     │
     ├─ STATE MACHINE UPDATE
     │  └─ Light: OFF → ON
     │
     ├─ STUDY TIMER UPDATE
     │  └─ Session active = true
     │
     ▼
WEB DASHBOARD UPDATE
LOG TO FILE
NEXT FRAME
```

---

## 🔄 State Machine Diagram

```
┌─────────────────────────────────────────────┐
│           LIGHT STATE MACHINE               │
└─────────────────────────────────────────────┘

    ┌─────────┐
    │   OFF   │  Initial state
    │ (Light) │
    └────┬────┘
         │
         │ person_detected = True
         │
         ▼
    ┌─────────┐
    │   ON    │◄─────────┐
    │ (Light) │          │
    └────┬────┘          │
         │               │ person_detected = True
         │               │ (resets countdown)
         │ person_detected = False
         │
         ▼
    ┌──────────────┐
    │  COUNTDOWN   │
    │ (10s timer)  │
    └────┬─────────┘
         │
         │ 10s elapsed
         │
         ▼
    ┌─────────┐
    │   OFF   │
    │ (Light) │
    └─────────┘

Transitions:
- OFF + person_detected = ON
- ON + no_person = COUNTDOWN
- COUNTDOWN + timeout = OFF
- COUNTDOWN + person_detected = ON (reset countdown)
```

---

## 🧩 Module Dependencies

```
main.py (Orchestrator)
  │
  ├─ config.py (Configuration)
  │
  ├─ vision/camera.py
  │  └─ opencv-python
  │
  ├─ vision/motion_detector.py
  │  ├─ camera.py
  │  └─ opencv-python
  │
  ├─ vision/face_detector.py
  │  ├─ camera.py
  │  └─ opencv-python
  │
  ├─ vision/posture_detector.py
  │  ├─ camera.py
  │  ├─ opencv-python
  │  └─ dlib (optional, for advanced)
  │
  ├─ core/state_machine.py
  │  ├─ hardware/relay.py
  │  └─ config.py
  │
  ├─ core/study_timer.py
  │  └─ config.py
  │
  ├─ hardware/relay.py
  │  ├─ RPi.GPIO (Raspberry Pi)
  │  └─ config.py
  │
  ├─ communication/telegram_bot.py
  │  ├─ requests
  │  ├─ opencv-python
  │  └─ config.py
  │
  └─ web/app.py
     ├─ Flask
     ├─ vision/camera.py
     ├─ core/state_machine.py
     ├─ core/study_timer.py
     ├─ hardware/relay.py
     └─ communication/telegram_bot.py
```

---

## 📈 Processing Pipeline Detailed

### Frame Processing Loop (Main)

```python
while running:
    # 1. Capture (10ms)
    ret, frame = camera.read()
    
    # 2. Resize (5ms)
    resized = camera.resize_frame(frame, 320, 240)
    
    # 3. Motion Detection (15ms)
    person_detected, motion_mask = motion_detector.detect(
        resized,
        roi=(50, 50, 220, 140)
    )
    
    # 4. State Update (1ms)
    state_machine.update(person_detected)
    
    # 5. Face Detection (20ms) [if person detected]
    if person_detected:
        faces = face_detector.detect_faces(resized)
        for face in faces:
            is_sleeping = face_detector.detect_sleep(resized, face)
            
            if is_sleeping:
                telegram_bot.alert_sleep(resized)
                study_timer.log_event("SLEEP_DETECTED")
    
    # 6. Posture Detection (15ms) [if person detected]
    if person_detected:
        head_angle = posture_detector.detect_posture(resized)
        
        if head_angle and abs(head_angle) > threshold:
            telegram_bot.alert_posture(resized, head_angle)
            study_timer.log_event("BAD_POSTURE")
    
    # 7. Timer Update (1ms)
    study_timer.update(person_detected)
    
    # 8. Logging (1ms)
    if frame_count % 30 == 0:
        logger.debug(f"FPS: {fps}, State: {state}")
    
    # Total: ~70ms per frame
    # → ~14fps processing intensive work
    # → Lightweight motion detection allows 25fps
```

### Timing Budget (320x240 frame)

| Task | Time | Notes |
|------|------|-------|
| Camera.read() | 10ms | Bottleneck |
| Resize | 5ms | Linear interpolation |
| Motion Detection | 15ms | Background subtraction + morphology |
| Face Detection | 20ms | Haar cascade (heavy, skip if not needed) |
| Eye Detection | 10ms | Within face region |
| Posture Detection | 15ms | Face detection + angle calculation |
| State Update | 1ms | Simple logic |
| Telegram Send | 2000ms | **Async only!** |
| Logging | 1ms | Every 30 frames |
| **Total (sync)** | **76ms** | ~13fps |
| **Total (async telegram)** | **76ms** | ~13fps |

---

## 🔐 Data Flow & Safety

### Sensitive Data Handling

```
User Input (Web/Telegram)
    │
    ├─ Validate command
    ├─ Check permissions
    │
    ▼
State Update
    │
    ├─ Rate limiting
    ├─ Safety checks
    │
    ▼
Hardware Control (Relay)
    │
    ├─ Verify state before action
    ├─ Timeout protection
    ├─ Logging
    │
    ▼
Physical Output (Light)
```

### Security Measures

1. **Input Validation**
   - Sanitize Telegram commands
   - Validate web requests
   - Type checking

2. **Access Control**
   - Telegram token protection
   - Web session management
   - GPIO permission checking

3. **Logging & Audit**
   - All actions logged
   - Timestamp recorded
   - User/source tracked

4. **Failsafe**
   - Relay defaults to OFF
   - Timeout auto-off (if system freezes)
   - Manual circuit breaker

---

## 🧠 AI/ML Pipeline

### Motion Detection Algorithm

```
Background Subtraction (MOG2)
    │
    ├─ Build background model (first 30 frames)
    │
    ├─ For each new frame:
    │  ├─ Subtract background
    │  ├─ Remove shadows (threshold 127)
    │  ├─ Morphological open (remove noise)
    │  ├─ Dilate (connect components)
    │  ├─ Count non-zero pixels
    │  └─ Compare with threshold
    │
    ▼
Person Detected = (pixel_count > MOTION_THRESHOLD)
```

**Threshold tuning:**
- Too low: False positives (shadows, camera noise)
- Too high: Missed detections (slow movement)
- Recommended: ~500 pixels for 320x240 frame

### Face Detection Algorithm

```
Face Cascade (Haar Features)
    │
    ├─ Grayscale conversion
    ├─ Histogram equalization (improve contrast)
    │
    ├─ Multi-scale detection
    │  ├─ Scale 1.0 (actual size)
    │  ├─ Scale 1.3 (smaller objects)
    │  ├─ Scale 1.6 (even smaller)
    │  └─ ... until too small
    │
    ├─ For each scale:
    │  ├─ Scan sliding window
    │  ├─ Calculate Haar features
    │  ├─ Classify as face/not-face
    │  ├─ Keep high-confidence matches
    │  └─ Remove overlaps (NMS)
    │
    ▼
List of faces (x, y, w, h)
```

### Eye Detection (Within Face)

```
Face Region → Extract eye region (upper half)
    │
    ├─ Search for eyes (using Eye Cascade)
    │
    ├─ If eyes found (2):
    │  └─ Eyes OPEN
    │
    ├─ If eyes not found (0):
    │  └─ Eyes CLOSED
    │
    ▼
Sleep = Eyes closed for 150 consecutive frames (~5s @ 30fps)
```

---

## 🔧 Configuration Tuning Guide

### Motion Threshold
```python
# If false positives (shadows, noise):
MOTION_THRESHOLD = 1000  # Increase

# If missed detections:
MOTION_THRESHOLD = 200   # Decrease

# Recommended:
MOTION_THRESHOLD = 500   # ~10% of frame area @ 320x240
```

### Face Detection Sensitivity
```python
# If missed faces:
scale_factor=1.1  # Smaller steps
min_neighbors=3   # Less strict

# If false positives:
scale_factor=1.5  # Larger steps
min_neighbors=6   # More strict

# Recommended:
scale_factor=1.3  # Good balance
min_neighbors=4   # Default
```

### Sleep Detection
```python
# If too sensitive (triggers too early):
EYE_CLOSED_FRAMES = 300  # ~10s

# If too lenient (doesn't detect):
EYE_CLOSED_FRAMES = 75   # ~2.5s

# Recommended:
EYE_CLOSED_FRAMES = 150  # ~5s @ 30fps
```

---

## 📊 Performance Considerations

### CPU Budget (Raspberry Pi B+)

```
Total Budget: 100%
├─ System OS: 10%
├─ Python Runtime: 10%
├─ Camera I/O: 20%
├─ Motion Detection: 15%
├─ Face Detection: 20%
├─ Misc (logging, etc): 10%
└─ Headroom: 15%
────────────────
Total: ~100%
```

### Memory Usage

```
Python Process: ~150MB
├─ opencv: ~50MB
├─ Flask (if running): ~40MB
├─ numpy: ~30MB
├─ Frame buffers: ~5MB
└─ Models (Haar): ~5MB

System Total: ~450MB / 512MB available
```

### Network Bandwidth

```
Video streaming (disabled by default)
├─ 320x240 MJPEG @ 1fps: ~30KB/s
├─ 320x240 MJPEG @ 5fps: ~150KB/s
├─ 320x240 MJPEG @ 15fps: ~450KB/s

Telegram alerts: 1-5 per hour (~100KB each)
```

---

## 🚀 Scalability & Future

### V2 Enhancements
- [ ] Dual camera (front + side view)
- [ ] Advanced pose estimation (PoseNet)
- [ ] Fatigue detection (eye tracking)
- [ ] Sound detection (ambient noise)
- [ ] Database backend (study history)

### V3+ Features
- [ ] Multi-desk management (3+ desks)
- [ ] Cloud sync + analytics
- [ ] Mobile app
- [ ] AI personalization
- [ ] VR/AR integration

---

## 📖 References

- OpenCV: https://docs.opencv.org/
- Haar Cascades: https://docs.opencv.org/master/db/d28/tutorial_cascade_classifier.html
- MOG2 Background Subtraction: https://docs.opencv.org/3.4/d7/df3/classcv_1_1BackgroundSubtractorMOG2.html
- Flask: https://flask.palletsprojects.com/
- RPi.GPIO: https://pypi.org/project/RPi.GPIO/

---

**Document Version:** 1.0
**Last Updated:** March 2024
