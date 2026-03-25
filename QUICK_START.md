# 🚀 QUICK START GUIDE

## ⏱️ Thời gian: 10 phút

---

## 📋 Prerequisite

✅ Raspberry Pi đã flash OS (STEP 1 hoàn tất)
✅ SSH vào Raspberry thành công
✅ Internet connection ổn định

---

## 🎯 5 Bước Setup

### 1️⃣ Clone Project
```bash
cd ~
git clone <repo-url> smart-study-desk
cd smart-study-desk
```

### 2️⃣ Chạy Automatic Setup
```bash
bash setup.sh
```

**Script này sẽ tự động:**
- Update system
- Install dependencies
- Configure GPIO
- Create .env file
- Setup systemd service

⏱️ **Thời gian: 5-10 phút** (tùy tốc độ internet)

### 3️⃣ Configure Telegram (Optional)
```bash
# Edit config
nano .env
```

**Thêm vào:**
```
TELEGRAM_TOKEN=YOUR_BOT_TOKEN_HERE
TELEGRAM_CHAT_ID=YOUR_CHAT_ID_HERE
```

> Cách lấy token: [Telegram Setup Guide](#telegram-setup)

### 4️⃣ Test Individual Modules
```bash
# Test camera
python3 vision/camera.py

# Test motion detector
python3 vision/motion_detector.py

# Test relay
python3 hardware/relay.py

# Test state machine
python3 core/state_machine.py
```

### 5️⃣ Run Full System
```bash
# Development mode (với debug output)
python3 main.py

# Production mode (background)
nohup python3 main.py > logs/system.log 2>&1 &

# Check logs
tail -f logs/system.log
```

---

## 🌐 Access Web Dashboard

Mở browser:
```
http://192.168.1.100:5000
```

**Ghi chú:** Thay `192.168.1.100` bằng IP thật của Raspberry

---

## 🛠️ Troubleshooting

### "ModuleNotFoundError"
```bash
# Reinstall packages
pip3 install -r requirements.txt
```

### Camera not detected
```bash
# Check if camera is connected
ls /dev/video*

# Test with OpenCV
python3 -c "import cv2; cap = cv2.VideoCapture(0); print(cap.isOpened())"
```

### GPIO permission error
```bash
# Add to gpio group
sudo usermod -a -G gpio pi

# Reboot
sudo reboot
```

### Port 5000 already in use
```bash
# Kill existing process
sudo lsof -ti:5000 | xargs kill -9

# Or change port in config.py: WEB_PORT = 5001
```

---

## 📱 Telegram Setup

### Get Bot Token
1. Open [@BotFather](https://t.me/botfather)
2. Send: `/newbot`
3. Follow instructions
4. Copy your token

### Get Chat ID
1. Open [@userinfobot](https://t.me/userinfobot)
2. Copy your chat ID

### Add to .env
```bash
nano .env
```

Set:
```
TELEGRAM_TOKEN=123456:ABCDefGHijKlmnoPQRstUvwxyz
TELEGRAM_CHAT_ID=987654321
```

---

## 📊 Monitor System

### View Logs
```bash
# Real-time log
tail -f logs/study_system.log

# Search for errors
grep ERROR logs/study_system.log

# Search for sleep events
grep "SLEEP" logs/study_system.log
```

### System Health
```bash
# CPU/Memory usage
htop

# Temperature
vcgencmd measure_temp

# Disk space
df -h

# Network
ifconfig eth0
```

---

## 🎮 Web Dashboard Features

| Feature | How to Use |
|---------|-----------|
| **Light Control** | Click "Turn On" / "Turn Off" buttons |
| **View Camera** | See live feed from webcam |
| **View Stats** | Check study time, sleep events, posture alerts |
| **Recent Events** | See all detected events with timestamps |
| **System Status** | Monitor relay state, state machine status |

---

## 🔄 Auto-Start on Boot (Optional)

```bash
# Enable systemd service
sudo systemctl enable smart-study-desk

# Start service
sudo systemctl start smart-study-desk

# Check status
sudo systemctl status smart-study-desk

# View logs
sudo journalctl -u smart-study-desk -f
```

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| `main.py` | Main orchestration loop |
| `config.py` | Configuration file |
| `.env` | Secrets (Telegram token, etc) |
| `logs/study_system.log` | System log file |
| `logs/study_log_*.json` | Session history |

---

## 🧪 Quick Test Scenario

```bash
# 1. Start system
python3 main.py

# 2. In another terminal, check logs
tail -f logs/study_system.log

# 3. Move in front of camera
# → Should see: "💡 LIGHT ON"
# → Should see: "📚 Study session started"

# 4. Move away from camera
# → Should see: "⏳ COUNTDOWN START (10s)"
# → Should see: "⚫ LIGHT OFF" (after 10s)

# 5. Close your eyes for 5 seconds
# → Should see: "😴 SLEEP DETECTED!"
# → Should get Telegram alert (if configured)
```

---

## 📞 Common Commands

```bash
# Stop running process
Ctrl + C

# View system info
uname -a

# Check Python version
python3 --version

# Check pip packages
pip3 list | grep -E "opencv|flask|requests"

# Test internet
ping 8.8.8.8

# Check Raspberry model
cat /proc/device-tree/model
```

---

## 🎯 Next Steps After Setup

1. **STEP 2:** GPIO + Relay testing
2. **STEP 3:** Camera pipeline optimization
3. **STEP 4:** Person detection MVP
4. **STEP 5:** Sleep detection fine-tuning
5. **STEP 6:** Posture detection calibration
6. **STEP 7:** Telegram integration testing
7. **STEP 8:** Web dashboard enhancements
8. **STEP 9:** Full system testing (3 hours)
9. **STEP 10:** Production deployment

---

## 💡 Tips & Tricks

### Good Lighting
- Ensure adequate lighting for face detection
- Avoid backlighting or harsh shadows
- Use the light being controlled to improve vision

### Reduce Noise
- Disable WiFi interference (use Ethernet if possible)
- Avoid moving objects in background
- Keep camera stable

### Performance
- Monitor CPU usage: `watch -n1 'vcgencmd measure_temp'`
- If slow, reduce FRAME_WIDTH/HEIGHT in config.py
- Use `top` to find CPU-hungry processes

### Development
- Use `--simulate` flag to test without hardware
- Run tests: `python3 -m pytest tests/`
- Debug with logging level: `LOG_LEVEL = "DEBUG"`

---

## ✅ Checklist: You're Ready When...

- [ ] Project cloned
- [ ] setup.sh ran successfully
- [ ] .env configured with Telegram (optional)
- [ ] Camera test passed
- [ ] Motion detector test passed
- [ ] Relay test passed
- [ ] main.py runs without errors
- [ ] Web dashboard accessible
- [ ] Light turns on/off correctly
- [ ] Logs are being written

---

## 🚨 Emergency Stop

```bash
# Stop running process
pkill -f "python3 main.py"

# Disable auto-start
sudo systemctl stop smart-study-desk
sudo systemctl disable smart-study-desk

# Force off light (in case it's stuck)
# From Python:
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
GPIO.output(17, GPIO.LOW)
GPIO.cleanup()
```

---

## 📞 Get Help

1. Check logs: `tail -f logs/study_system.log`
2. Test module: `python3 <module_name>.py`
3. Check config: `python3 config.py`
4. Review documentation: `README.md`

---

**🎉 You're all set!**

Start with:
```bash
python3 main.py
```

Or enable auto-start:
```bash
sudo systemctl enable smart-study-desk
sudo systemctl start smart-study-desk
```

---

**Happy learning! 📚💡**
