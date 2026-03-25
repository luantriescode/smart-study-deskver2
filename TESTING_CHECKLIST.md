# ✅ COMPLETE TESTING CHECKLIST

## 🎯 Full System Verification

Dùng document này để kiểm tra từng bước khi triển khai hệ thống.

---

# STEP 1: OS + NETWORK SETUP

## Hardware Preparation
- [ ] Raspberry Pi Model B+ (hoặc tương đương)
- [ ] MicroSD card ≥16GB
- [ ] USB power adapter 5V/2A
- [ ] Ethernet cable (hoặc WiFi adapter)
- [ ] Laptop/PC để flash OS

## OS Installation
- [ ] Raspberry Pi Imager downloaded
- [ ] MicroSD card flashed with Raspberry Pi OS Lite
- [ ] Hostname set to "smartdesk"
- [ ] SSH enabled (user: pi, password: raspberry)
- [ ] MicroSD safely ejected

## Initial Boot & Connection
- [ ] Raspberry Pi boots successfully (LED blinking)
- [ ] SSH login successful: `ssh pi@192.168.1.100`
- [ ] Can execute commands remotely
- [ ] Internet connection working: `ping 8.8.8.8` ✅

## System Updates
- [ ] `sudo apt update` completed
- [ ] `sudo apt upgrade -y` completed
- [ ] Python 3.8+ installed: `python3 --version`
- [ ] Pip3 available: `pip3 --version`

## Static IP Configuration
- [ ] IP set to static (e.g., 192.168.1.100)
- [ ] IP persistent after reboot
- [ ] Gateway configured correctly
- [ ] DNS working: `ping google.com` ✅

## System Verification
- [ ] Uptime stable: `uptime`
- [ ] Disk space adequate: `df -h` (>2GB free)
- [ ] Memory available: `free -h` (>300MB free)
- [ ] Temperature normal: `vcgencmd measure_temp` (<50°C)
- [ ] Network stable: No packet loss in `ping`

---

# STEP 2: GPIO + RELAY TESTING

## Hardware Setup
- [ ] Relay module 5V physically connected
- [ ] GPIO 17 (PIN 11) connected to relay signal
- [ ] 5V power (PIN 2 or 4) connected to relay VCC
- [ ] GND (PIN 6, 9, 14, 20, 25, 30, 34, 39) connected to relay GND
- [ ] Relay connections verified visually

## GPIO Initialization
- [ ] RPi.GPIO library installable
- [ ] GPIO can be set to BCM mode
- [ ] GPIO 17 can be configured as output
- [ ] No permission errors

## Relay Hardware Test
- [ ] Relay clicks when signal HIGH (audible)
- [ ] Relay clicks when signal LOW (audible)
- [ ] 10 consecutive toggles work correctly
- [ ] No relay heating observed

## Relay Software Test
```bash
python3 hardware/relay.py
```
- [ ] Test runs without errors
- [ ] Relay state changes reported correctly
- [ ] Toggle count increments
- [ ] Cleanup executes successfully

## Dry Run (No AC Power)
- [ ] Light logic tested without 220V
- [ ] Relay responds to commands
- [ ] No errors in logs

## AC Power Test (WITH RELAY)
⚠️ **Danger: High voltage**
- [ ] Circuit breaker OFF during setup
- [ ] Wiring checked twice (visual inspection)
- [ ] No loose connections
- [ ] Voltmeter shows 0V before powering on

**After powering on:**
- [ ] Relay correctly turns light ON
- [ ] Relay correctly turns light OFF
- [ ] Light is bright (not dim)
- [ ] No burning smell or overheating
- [ ] Repeated on/off cycles work (3x test)
- [ ] No sparking or arcing observed

## Safety Verification
- [ ] Relay temperature < 50°C after 1 hour
- [ ] No signs of damage to relay
- [ ] No signs of damage to wiring
- [ ] Fuse/circuit breaker trips normally if short
- [ ] Emergency stop works (circuit breaker OFF)

---

# STEP 3: CAMERA PIPELINE

## Camera Hardware
- [ ] USB webcam physically connected
- [ ] Camera appears in: `ls /dev/video*`
- [ ] Camera has 960p+ resolution (check specs)
- [ ] USB cable is good quality

## OpenCV Installation
- [ ] OpenCV installed: `python3 -c "import cv2; print(cv2.__version__)"`
- [ ] Version ≥ 4.0
- [ ] No import errors

## Basic Camera Test
```bash
python3 vision/camera.py
```
- [ ] Camera opened successfully
- [ ] Resolution correct (640x480)
- [ ] FPS reported (≥20fps)
- [ ] 10 frames read successfully
- [ ] No error messages

## Performance Benchmarks
```bash
python3 << 'EOF'
import cv2
cap = cv2.VideoCapture(0)
# Read 100 frames and measure time
EOF
```
- [ ] 640x480: ≥20fps
- [ ] 320x240: ≥25fps
- [ ] CPU usage: ≤50%
- [ ] Temperature: <55°C

## Frame Quality
- [ ] Image is bright (not too dark)
- [ ] Colors are accurate
- [ ] No motion blur
- [ ] Sharpness acceptable
- [ ] No dead pixels visible

## Resize Functionality
- [ ] Resize 640x480 → 320x240 works
- [ ] INTER_LINEAR provides good quality
- [ ] Resize time <5ms
- [ ] No artifacts in resized frames

## ROI Cropping
- [ ] ROI extraction works (defined in config)
- [ ] ROI region is correct
- [ ] No boundary issues
- [ ] Cropping time negligible

## Long-term Stability
- [ ] Run 300 frames: no crashes
- [ ] No memory leaks
- [ ] FPS stable (doesn't gradually decrease)
- [ ] No frame drops

## Sample Frames
```bash
mkdir -p logs/samples
# Save 10 frames for analysis
```
- [ ] Samples saved to logs/samples/
- [ ] Can view in image viewer
- [ ] Quality acceptable

---

# STEP 4: PERSON DETECTION MVP

## Motion Detector Initialization
```bash
python3 vision/motion_detector.py
```
- [ ] MotionDetector initializes without error
- [ ] First 30 frames build background model
- [ ] No errors reported

## Motion Detection Accuracy
- [ ] Person sitting: Detected ✅
- [ ] Person moving: Detected ✅
- [ ] Static objects: Not detected (no false positive)
- [ ] Shadows: Not detected (filtered)
- [ ] Camera noise: Not detected (filtered)

## ROI Configuration
- [ ] ROI defines study area correctly
- [ ] ROI size appropriate (~50% of frame)
- [ ] Person in ROI detected reliably
- [ ] Person outside ROI not detected

## State Machine
```bash
python3 core/state_machine.py
```
- [ ] Initial state: OFF
- [ ] Person detected → state: ON
- [ ] Person lost → state: COUNTDOWN
- [ ] Countdown expires → state: OFF
- [ ] Countdown reset if person returns

## Light Control
- [ ] Light turns ON when person detected
- [ ] Light turns OFF when countdown expires
- [ ] Manual ON/OFF works
- [ ] No relay errors

## Timer
```bash
python3 core/study_timer.py
```
- [ ] Session starts when person detected
- [ ] Session time counts correctly
- [ ] Session ends when person leaves
- [ ] Stats recorded correctly

## Log Output
- [ ] Logs written to `logs/study_system.log`
- [ ] Events include timestamps
- [ ] No sensitive data in logs

## 3-Hour Stability Test
- [ ] Run system for 3 hours continuously
- [ ] No crashes
- [ ] Light on/off cycles: >10
- [ ] Memory usage stable
- [ ] Temperature < 60°C
- [ ] CPU usage < 70%

---

# STEP 5: SLEEP DETECTION

## Face Detector Initialization
```bash
python3 vision/face_detector.py
```
- [ ] Haar cascades loaded successfully
- [ ] Face detector ready

## Face Detection
- [ ] Frontal face detected when visible
- [ ] Face location accurate
- [ ] Multiple faces detected if present
- [ ] Scale-invariant (face size doesn't matter)

## Eye Detection
- [ ] Eyes detected within face region
- [ ] 2 eyes detected when open
- [ ] 0 eyes detected when closed
- [ ] Sensitive to eye closure

## Sleep Detection
- [ ] Eyes closed <1 second: Not detected
- [ ] Eyes closed 3 seconds: Not detected
- [ ] Eyes closed 5 seconds: Detected ✅
- [ ] Eyes closed 10+ seconds: Detected ✅

## Sleep Alert
- [ ] Telegram alert sent on sleep detection
- [ ] Alert includes frame image
- [ ] Alert not spammed (cooldown works)
- [ ] Log event recorded

## Posture Detector
```bash
python3 vision/posture_detector.py
```
- [ ] Head straight: Detected correctly
- [ ] Head cocked left: Detected
- [ ] Head cocked right: Detected
- [ ] Head down: Detected as "bad posture"
- [ ] Head up: Detected as "bad posture"

## Posture Alert
- [ ] Alert sent for bad posture
- [ ] Alert includes frame + angle
- [ ] Log event recorded

---

# STEP 6: TELEGRAM INTEGRATION

## Telegram Bot Setup
- [ ] Bot created with @BotFather
- [ ] Token obtained: `123456:ABC...`
- [ ] Chat ID obtained: `987654321`
- [ ] Token added to config.py or .env

## Bot Verification
```bash
python3 communication/telegram_bot.py
```
- [ ] Bot connection successful
- [ ] "Bot verified" message appears
- [ ] No connection errors

## Message Sending
- [ ] Text alert sends successfully
- [ ] Alert appears in Telegram chat
- [ ] Timestamp correct
- [ ] No errors reported

## Photo Sending
- [ ] Photo uploads successfully
- [ ] Image appears in chat
- [ ] Quality acceptable
- [ ] Timestamp correct

## Cooldown Logic
- [ ] Multiple alerts sent: only 1 per 30s
- [ ] Spam prevented
- [ ] Log shows cooldown active

## Integration with Main System
- [ ] Sleep detected → Telegram alert sent
- [ ] Posture detected → Telegram alert sent
- [ ] Session start → Telegram alert (optional)
- [ ] Session end → Telegram stats (optional)

---

# STEP 7: WEB DASHBOARD

## Flask Server Startup
```bash
python3 web/app.py
```
- [ ] Server starts without error
- [ ] Running on `0.0.0.0:5000`
- [ ] No port conflicts

## Web Dashboard Access
- [ ] Browser: `http://192.168.1.100:5000`
- [ ] Dashboard loads
- [ ] All buttons visible
- [ ] No JavaScript errors (check console)

## Status Display
- [ ] Light status shows ON/OFF
- [ ] State machine status displays
- [ ] Camera status shows OK/ERROR
- [ ] Auto-refresh working (~2s)

## Statistics Display
- [ ] Current session time displays
- [ ] Total sessions count correct
- [ ] Sleep events count correct
- [ ] Posture events count correct
- [ ] Updates every 5 seconds

## Light Control
- [ ] "Turn On" button works
- [ ] "Turn Off" button works
- [ ] Light status updates immediately
- [ ] Web UI responsive

## Video Stream
- [ ] Camera feed visible
- [ ] Stream smooth (no freezing)
- [ ] Updates in real-time
- [ ] Quality acceptable

## Recent Events
- [ ] Events list displays
- [ ] Latest events shown first
- [ ] Timestamps correct
- [ ] Updates every 10 seconds

## Responsive Design
- [ ] Desktop view: fully functional
- [ ] Tablet view: usable
- [ ] Mobile view: readable
- [ ] No layout issues

## API Endpoints
```bash
curl http://192.168.1.100:5000/api/status
curl http://192.168.1.100:5000/api/stats
curl http://192.168.1.100:5000/api/events
```
- [ ] All return valid JSON
- [ ] No 404 errors
- [ ] Data format correct

---

# STEP 8: SYSTEM INTEGRATION TEST

## End-to-End Flow
1. **Person detection:**
   - [ ] Person in ROI → Light ON ✅
   - [ ] State machine: OFF → ON ✅
   - [ ] Study timer: Session starts ✅

2. **Study session:**
   - [ ] Timer counts correctly ✅
   - [ ] Events logged ✅

3. **Sleep detection:**
   - [ ] Eyes closed >5s → Sleep detected ✅
   - [ ] Telegram alert sent ✅
   - [ ] Image uploaded ✅
   - [ ] Log recorded ✅

4. **Posture detection:**
   - [ ] Bad posture detected ✅
   - [ ] Alert sent ✅
   - [ ] Log recorded ✅

5. **Person leaves:**
   - [ ] Motion stops → Countdown starts ✅
   - [ ] After 10s → Light OFF ✅
   - [ ] Session ends ✅
   - [ ] Final stats logged ✅

6. **Web Dashboard:**
   - [ ] All stats update correctly ✅
   - [ ] Events display in real-time ✅
   - [ ] Controls responsive ✅

## Stress Testing
- [ ] 1-hour continuous run: ✅ Stable
- [ ] 3-hour continuous run: ✅ No issues
- [ ] Repeated on/off: ✅ 50+ cycles
- [ ] Manual controls: ✅ Responsive
- [ ] No memory leaks: ✅ Stable memory

## Log Analysis
```bash
grep ERROR logs/study_system.log
grep WARNING logs/study_system.log
```
- [ ] No ERROR entries
- [ ] WARNINGs expected and normal
- [ ] All sessions logged
- [ ] Timestamps accurate

---

# STEP 9: PRODUCTION READINESS

## Auto-Start Service
```bash
sudo systemctl enable smart-study-desk
sudo systemctl start smart-study-desk
```
- [ ] Service enables successfully
- [ ] Service starts automatically on boot
- [ ] Status shows "active (running)"
- [ ] Logs accessible: `sudo journalctl -u smart-study-desk -f`

## Log Rotation
```bash
# Check log file
ls -lh logs/study_system.log
```
- [ ] Log file size reasonable (<100MB)
- [ ] Old logs rotated if needed
- [ ] No disk space issues

## Performance Under Load
- [ ] CPU usage: consistently <70%
- [ ] Memory usage: <400MB
- [ ] Temperature: <65°C
- [ ] No thermal throttling

## Reboot Behavior
```bash
sudo reboot
# Wait 2 minutes
ssh pi@192.168.1.100
```
- [ ] System boots successfully
- [ ] Smart Study Desk service starts automatically
- [ ] All systems online
- [ ] Camera functional
- [ ] Relay functional

## Graceful Shutdown
```bash
sudo systemctl stop smart-study-desk
```
- [ ] Light turns OFF
- [ ] Logs saved
- [ ] No errors
- [ ] Clean shutdown

## Network Resilience
- [ ] Works without internet (local only)
- [ ] Reconnects when internet returns
- [ ] Telegram works when internet available
- [ ] Web dashboard accessible on LAN

---

# OPTIONAL: ADVANCED FEATURES

## PWM Brightness Control
- [ ] Can set light brightness 0-100%
- [ ] Smooth dimming works
- [ ] Fade effects work

## Advanced Pose Estimation
- [ ] dlib installed (if enabled)
- [ ] 68-point landmarks detected
- [ ] Head angle calculated accurately
- [ ] Performance acceptable

## Database Integration
- [ ] SQLite created
- [ ] Sessions logged to database
- [ ] Historical data queryable
- [ ] No performance impact

## Mobile App
- [ ] App connects to dashboard
- [ ] Controls work from phone
- [ ] Stats display correctly
- [ ] Responsive design

---

# TROUBLESHOOTING REFERENCE

## If camera doesn't work:
- [ ] Check `/dev/video0` exists
- [ ] Check USB cable connection
- [ ] Try different USB port
- [ ] Run: `python3 vision/camera.py`
- [ ] Check OpenCV import

## If relay doesn't work:
- [ ] Check GPIO pin correct (17)
- [ ] Check relay VCC/GND
- [ ] Test: `gpio readall`
- [ ] Listen for "click" sound
- [ ] Check RPi.GPIO permissions

## If motion not detected:
- [ ] Check ROI configured
- [ ] Increase lighting
- [ ] Adjust MOTION_THRESHOLD
- [ ] Check background subtraction

## If sleep detection not working:
- [ ] Check face detected first
- [ ] Check eye detection threshold
- [ ] Test: `python3 vision/face_detector.py`
- [ ] Improve lighting
- [ ] Adjust EYE_CLOSED_FRAMES

## If Telegram not sending:
- [ ] Verify token: `echo $TELEGRAM_TOKEN`
- [ ] Check internet: `ping 8.8.8.8`
- [ ] Test: `python3 communication/telegram_bot.py`
- [ ] Verify chat ID correct

## If web dashboard not loading:
- [ ] Check Flask running: `ps aux | grep python3`
- [ ] Check port 5000: `sudo lsof -i :5000`
- [ ] Test: `curl http://192.168.1.100:5000/api/status`
- [ ] Check browser console for errors

---

# 🎉 FINAL VERIFICATION

After completing all tests:

- [ ] All STEP 1-9 tests passed
- [ ] No critical errors remaining
- [ ] Performance acceptable
- [ ] Security verified
- [ ] Documentation complete
- [ ] Ready for production deployment

**System Status: ✅ READY FOR DEPLOYMENT**

---

**Checklist Version:** 1.0
**Last Updated:** March 2024
**Total Tests:** 150+
