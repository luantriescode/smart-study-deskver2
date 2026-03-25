# 📚 Smart Study Desk System

Hệ thống IoT tự động hóa bàn học với AI vision trên Raspberry Pi.

## 🎯 Tính năng chính

### 1. **Tự động hóa ánh sáng** 💡
- Phát hiện người ngồi học → Tự bật đèn
- Người rời đi → Đếm ngược 10s rồi tắt đèn
- Manual control qua web dashboard

### 2. **Giám sát hành vi học** 👁️
- Phát hiện **ngủ gật** (mắt đóng > 5s)
- Phát hiện **sai tư thế** (cúi đầu quá)
- Cảnh báo realtime qua Telegram

### 3. **Thống kê học tập** 📊
- Đếm giờ học
- Ghi log sự kiện
- Dashboard hiển thị stats

### 4. **Điều khiển từ xa** 🌐
- Web dashboard (http://192.168.1.100:5000)
- Telegram bot commands
- Voice control (planned)

---

## 📋 Yêu cầu hệ thống

### Hardware
- **Raspberry Pi B+** (hoặc tương đương)
- **USB Webcam** (960p hoặc cao hơn)
- **Relay Module 5V** (để điều khiển đèn 220V)
- **LED 220V** (tùy chọn)
- **Ethernet cable** hoặc WiFi adapter

### Software
- **Python 3.8+**
- **OpenCV** (vision processing)
- **Flask** (web server)
- **RPi.GPIO** (GPIO control)

### Network
- Router với DHCP hoặc cấu hình static IP
- Internet để Telegram bot hoạt động

---

## 🚀 Quick Start

### 1. Chuẩn bị Raspberry Pi (STEP 1)

```bash
# SSH vào Raspberry
ssh pi@192.168.1.100

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-dev git

# Install Python packages
pip3 install -r requirements.txt
```

Xem chi tiết: [STEP_1_DEPLOYMENT_GUIDE.md](STEP_1_DEPLOYMENT_GUIDE.md)

### 2. Clone project

```bash
git clone <repo-url> ~/smart-study-desk
cd ~/smart-study-desk
```

### 3. Cấu hình

```bash
# Copy config template
cp config.py config_local.py

# Edit config
nano config_local.py
```

**Cấu hình quan trọng:**
```python
# GPIO
RELAY_PIN = 17

# Camera
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# Telegram
TELEGRAM_TOKEN = "YOUR_BOT_TOKEN_HERE"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID_HERE"

# Web
WEB_HOST = "0.0.0.0"
WEB_PORT = 5000
```

### 4. Chạy hệ thống

```bash
# Mode development
python3 main.py

# Mode production (với logging)
nohup python3 main.py > logs/system.log 2>&1 &
```

### 5. Truy cập web dashboard

```
http://192.168.1.100:5000
```

---

## 📁 Project Structure

```
smart-study-desk/
│
├── main.py                           # Main loop + orchestration
├── config.py                         # Configuration
├── requirements.txt                  # Python dependencies
│
├── vision/
│   ├── camera.py                    # Webcam handler
│   ├── motion_detector.py           # Person detection
│   ├── face_detector.py             # Face & eye detection
│   └── posture_detector.py          # Posture detection
│
├── core/
│   ├── state_machine.py             # Light control logic
│   └── study_timer.py               # Session tracking
│
├── hardware/
│   └── relay.py                     # GPIO relay control
│
├── communication/
│   └── telegram_bot.py              # Telegram alerts
│
├── web/
│   ├── app.py                       # Flask web server
│   ├── templates/
│   │   └── index.html               # Dashboard UI
│   └── static/                      # CSS, JS
│
└── logs/                            # Log files

```

---

## 🔄 Deployment Roadmap

### ✅ STEP 1: OS + Network (COMPLETED)
- Flash Raspberry Pi OS
- Setup SSH
- Configure static IP
- Verify internet

### 📌 STEP 2: GPIO + Relay (Next)
- Install GPIO library
- Test relay control
- Test light 220V

### 📌 STEP 3: Camera Pipeline
- Install OpenCV
- Test webcam streaming
- CPU load optimization

### 📌 STEP 4: Person Detection MVP
- Motion detection
- Auto light control
- State machine

### 📌 STEP 5: Sleep Detection
- Face detection
- Eye closed detection
- Telegram alerts

### 📌 STEP 6: Posture Detection
- Head angle tracking
- Bad posture detection

### 📌 STEP 7: Telegram Integration
- Bot token setup
- Message + photo sending

### 📌 STEP 8: Web Dashboard
- Flask server
- Camera stream
- Control buttons

### 📌 STEP 9: System Testing
- 3-hour stress test
- Threshold tuning
- Optimization

### 📌 STEP 10: Production Mode
- Auto-start service
- Log rotation
- Monitoring

---

## 🧪 Testing

### Unit tests
```bash
# Test individual modules
python3 -m pytest tests/

# Or test specific module
python3 vision/camera.py        # Test camera
python3 vision/motion_detector.py
python3 hardware/relay.py
```

### Integration test
```bash
# Full system test (short)
python3 main.py --test --duration=60
```

### Performance monitoring
```bash
# Check CPU/Memory/Temp
htop
vcgencmd measure_temp
```

---

## 🔧 Configuration Guide

### Camera ROI (Region of Interest)
```python
# Define the area where person should be detected
ROI_X = 50          # pixels from left
ROI_Y = 50          # pixels from top
ROI_W = 220         # width
ROI_H = 140         # height
```

### Motion Threshold
```python
# Sensitivity of motion detection (pixels changed)
MOTION_THRESHOLD = 500      # Higher = less sensitive
MOTION_MIN_AREA = 100       # Minimum area to trigger
```

### Sleep Detection
```python
# Eyes closed for how long = sleeping?
EYE_CLOSED_FRAMES = 150     # ~5s at 30fps
```

### Timers
```python
# After person leaves, wait how long before turning off?
PERSON_LOST_DELAY = 10      # seconds
```

---

## 📱 Telegram Setup

### 1. Create Bot
1. Chat with [@BotFather](https://t.me/botfather)
2. Send: `/newbot`
3. Follow instructions
4. Copy your token

### 2. Get Chat ID
1. Chat with [@userinfobot](https://t.me/userinfobot)
2. Copy your chat ID

### 3. Configure
```bash
# Set environment variables
export TELEGRAM_TOKEN="YOUR_TOKEN_HERE"
export TELEGRAM_CHAT_ID="YOUR_CHAT_ID_HERE"

# Or in config.py
TELEGRAM_TOKEN = "YOUR_TOKEN_HERE"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID_HERE"
```

---

## 🐛 Troubleshooting

### Camera not detected
```bash
# List cameras
ls -la /dev/video*

# Test with OpenCV
python3 -c "import cv2; cap = cv2.VideoCapture(0); print(cap.get(cv2.CAP_PROP_FRAME_WIDTH))"
```

### GPIO permission error
```bash
# Add user to gpio group
sudo usermod -a -G gpio pi

# Reboot
sudo reboot
```

### No motion detected
- Check ROI configuration
- Adjust MOTION_THRESHOLD
- Check lighting conditions
- Verify camera is working

### Telegram not sending
- Verify token and chat ID
- Check internet connection
- Test with: `curl https://api.telegram.org/bot<TOKEN>/getMe`

---

## 📊 Performance Metrics

| Metric | Target | Typical |
|--------|--------|---------|
| FPS | 25-30 | 28 |
| CPU Usage | <70% | 45% |
| Memory | <300MB | 180MB |
| Latency | <200ms | 100ms |
| Temperature | <60°C | 45°C |

---

## 🔒 Security Notes

⚠️ **Important:**
- Change default password: `sudo passwd pi`
- Use firewall: `sudo ufw enable`
- Run as non-root if possible
- Use environment variables for secrets (not hardcoded)
- Keep Raspberry Pi OS updated

---

## 📚 Additional Resources

- [Raspberry Pi Official](https://www.raspberrypi.com/)
- [OpenCV Documentation](https://docs.opencv.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [GPIO Documentation](https://www.raspberrypi.com/documentation/computers/os.html#gpio-and-the-40-pin-header)

---

## 📝 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

Created for automated learning environment control system.

**Status:** 🚀 In Development

---

## 📞 Support

For issues and questions:
1. Check logs: `tail -f logs/study_system.log`
2. Run tests: `python3 vision/camera.py`
3. Check documentation
4. Create issue on GitHub

---

**Last Updated:** March 2024
**Version:** 0.1.0 (ALPHA)
