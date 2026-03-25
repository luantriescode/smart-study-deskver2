# 🚀 HƯỚNG DẪN TRIỂN KHAI CHI TIẾT - TỪNG BƯỚC

**Tài liệu này hướng dẫn cách triển khai Smart Study Desk từ A đến Z**

---

## 📋 MỤC LỤC

1. [CHUẨN BỊ BAN ĐẦU](#chuẩn-bị-ban-đầu)
2. [BƯỚC 1: OS + NETWORK (1 ngày)](#bước-1-os--network-1-ngày)
3. [BƯỚC 2: GPIO + RELAY (0.5 ngày)](#bước-2-gpio--relay-05-ngày)
4. [BƯỚC 3: CAMERA (1 ngày)](#bước-3-camera-1-ngày)
5. [BƯỚC 4: MOTION DETECTION (2 ngày)](#bước-4-motion-detection-2-ngày)
6. [BƯỚC 5: SLEEP DETECTION (2 ngày)](#bước-5-sleep-detection-2-ngày)
7. [BƯỚC 6: POSTURE DETECTION (1 ngày)](#bước-6-posture-detection-1-ngày)
8. [BƯỚC 7: TELEGRAM (1 ngày)](#bước-7-telegram-1-ngày)
9. [BƯỚC 8: WEB DASHBOARD (2 ngày)](#bước-8-web-dashboard-2-ngày)
10. [BƯỚC 9: TESTING (2 ngày)](#bước-9-testing-2-ngày)
11. [BƯỚC 10: PRODUCTION (1 ngày)](#bước-10-production-1-ngày)

---

## 🎯 CHUẨN BỊ BAN ĐẦU

### Hardware cần thiết:
- ✅ Raspberry Pi Model B+
- ✅ MicroSD card ≥16GB (Class 10)
- ✅ USB Webcam (960p+)
- ✅ Relay Module 5V (1-channel)
- ✅ LED/Light 220V (có cắm được vào ổ điện)
- ✅ Ethernet cable
- ✅ USB power adapter 5V/2A
- ✅ Laptop/PC (để flash OS)

### Software cần thiết:
- ✅ Raspberry Pi Imager (để flash OS)
- ✅ SSH client (MobaXTerm, PuTTY, hoặc Terminal)
- ✅ Text editor (để sửa file)

### Kiến thức cần có:
- ✅ Biết dùng terminal/command line cơ bản
- ✅ Biết dùng SSH login
- ✅ Biết sơ lược về Linux
- ✅ Biết Python cơ bản (không cần giỏi)

### Thời gian dự kiến:
- **BƯỚC 1-3:** 2-3 ngày (Chuẩn bị hardware)
- **BƯỚC 4-7:** 5-7 ngày (Lập trình AI)
- **BƯỚC 8-10:** 5-7 ngày (Integration + Testing)
- **TOTAL:** 2-3 tuần

---

# 🟢 BƯỚC 1: OS + NETWORK (1 ngày)

## Mục tiêu:
- ✅ Raspberry Pi chạy bình thường
- ✅ Có SSH login được
- ✅ Có internet stable
- ✅ IP tĩnh được set

## Chi tiết các công việc:

### 1️⃣ Flash Raspberry Pi OS

**Bước 1.1: Tải Raspberry Pi Imager**
```
Vào: https://www.raspberrypi.com/software/
Download Imager cho hệ điều hành của bạn
```

**Bước 1.2: Flash OS**
```
1. Mở Raspberry Pi Imager
2. Click "CHOOSE DEVICE" → Chọn "Raspberry Pi B+"
3. Click "CHOOSE OS" → Chọn "Raspberry Pi OS (other)" 
                     → "Raspberry Pi OS Lite (32-bit)"
4. Click "CHOOSE STORAGE" → Chọn MicroSD card
5. Click "⚙️ NEXT" → Cấu hình:
   ✅ Set hostname: "smartdesk"
   ✅ Enable SSH: username "pi", password "raspberry"
   ✅ Configure wireless LAN: (nếu dùng WiFi)
   ✅ Set locale: "Asia/Ho_Chi_Minh"
6. Click "WRITE" → Chờ 5-10 phút
7. Eject MicroSD an toàn
```

**Checkpoint 1.1:**
- ✅ MicroSD được flash thành công
- ✅ Có dòng "Write successful" từ Imager

---

### 2️⃣ Boot Raspberry Pi

**Bước 2.1: Cắm linh kiện**
```
1. Cắm MicroSD vào slot của Raspberry Pi
2. Cắm Ethernet cable vào router (LAN)
3. Cắm USB power adapter → Raspberry boot
4. Đợi ~2 phút để boot hoàn tất
   (LED sẽ nhấp nháy, sau đó ổn định)
```

**Bước 2.2: Tìm IP của Raspberry**

**Cách 1: Dùng router admin panel (dễ nhất)**
```
1. Mở browser
2. Vào http://192.168.1.1 (hoặc IP router của bạn)
3. Đăng nhập vào admin panel
4. Tìm "Connected Devices" hoặc "Devices"
5. Tìm "smartdesk" hoặc "Raspberry Pi"
6. Ghi lại IP (ví dụ: 192.168.1.100)
```

**Cách 2: Dùng nmap (Linux/macOS)**
```bash
sudo nmap -sn 192.168.1.0/24 | grep -i smartdesk
```

**Cách 3: Dùng arp (macOS/Linux)**
```bash
arp -a | grep -i "b8:27:eb\|dc:a6:32"
```

**Checkpoint 2.2:**
- ✅ Biết được IP của Raspberry (vd: 192.168.1.100)

---

### 3️⃣ SSH Login

**Bước 3.1: SSH vào Raspberry**
```bash
# Mở Terminal/PowerShell/MobaXTerm
ssh pi@192.168.1.100
# Nhập password: raspberry
# Bạn sẽ thấy: pi@smartdesk:~ $
```

**Bước 3.2: Verify kết nối**
```bash
# Kiểm tra hostname
hostname
# Output: smartdesk ✅

# Kiểm tra IP
ip addr show eth0
# Output: inet 192.168.1.100/24 ✅

# Kiểm tra internet
ping 8.8.8.8
# Output: bytes from 8.8.8.8 ✅
```

**Checkpoint 3.2:**
- ✅ SSH login thành công
- ✅ Hostname: smartdesk
- ✅ Internet: ping thành công

---

### 4️⃣ Update hệ thống

**Bước 4.1: Update package list & upgrade**
```bash
# Update
sudo apt update

# Upgrade (mất 5-10 phút)
sudo apt upgrade -y

# Install useful tools
sudo apt install -y python3-pip python3-dev git nano htop curl wget

# Verify Python
python3 --version
# Output: Python 3.9.x hoặc cao hơn ✅

# Verify pip
pip3 --version
# Output: pip 20.x hoặc cao hơn ✅
```

**Bước 4.2: Reboot**
```bash
sudo reboot
# Raspberry tắt và khởi động lại
# Chờ ~1 phút, sau đó SSH lại

ssh pi@192.168.1.100
```

**Checkpoint 4.2:**
- ✅ System updated
- ✅ Python 3.8+ cài được
- ✅ Pip3 cài được

---

### 5️⃣ Set IP tĩnh (Static IP)

**Bước 5.1: Xem cấu hình hiện tại**
```bash
ip addr show
# Ghi lại:
# - Interface name (eth0 hoặc wlan0)
# - Current IP (vd: 192.168.1.100)

ip route show
# Ghi lại Gateway (vd: 192.168.1.1)
```

**Bước 5.2: Chỉnh sửa dhcpcd.conf**
```bash
sudo nano /etc/dhcpcd.conf

# Scroll xuống dưới cùng, thêm:
# ─────────────────────────────────
# Static IP configuration
interface eth0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=8.8.8.8 8.8.4.4
# ─────────────────────────────────

# Lưu: CTRL+X → Y → ENTER
```

**Bước 5.3: Reboot & Verify**
```bash
sudo reboot
# Chờ 30s, SSH lại

ssh pi@192.168.1.100
# Kiểm tra IP không thay đổi
ip addr show eth0
```

**Checkpoint 5.3:**
- ✅ IP tĩnh được set (192.168.1.100)
- ✅ IP không thay đổi sau reboot

---

### 6️⃣ Final Verification

```bash
# Check uptime
uptime
# Output: up X:XX

# Check disk
df -h
# Output: /dev/mmcblk0p2  > 2GB free ✅

# Check memory
free -h
# Output: Mem: > 300MB free ✅

# Check temperature
vcgencmd measure_temp
# Output: temp=45'C (< 60°C) ✅

# Check network stable
ping -c 5 8.8.8.8
# Output: 0% packet loss ✅
```

**Checkpoint 6:**
- ✅ Disk space ≥ 2GB
- ✅ Memory available ≥ 300MB
- ✅ Temperature < 60°C
- ✅ No packet loss

---

## ✅ BƯỚC 1 DONE!

**Thời gian:** ~2-3 giờ
**Output:** Raspberry Pi online & stable
**Next:** BƯỚC 2 - GPIO + Relay Testing

---

---

# 🟢 BƯỚC 2: GPIO + RELAY (0.5 ngày)

## Mục tiêu:
- ✅ GPIO 17 hoạt động
- ✅ Relay bật/tắt được
- ✅ Đèn 220V sáng/tắt được

## Chi tiết các công việc:

### 1️⃣ Cắm dây relay

**Bước 1.1: Xác nhận pinout**
```
Raspberry Pi B+ Pinout:
PIN 2  → 5V (cho relay VCC)
PIN 6  → GND (cho relay GND)
PIN 11 → GPIO 17 (cho relay Signal)
PIN 4  → 5V (alternative)
PIN 9  → GND (alternative)
```

**Bước 1.2: Nối dây**
```
Relay Module:
- VCC → Raspberry Pi PIN 2 (5V)
- GND → Raspberry Pi PIN 6 (GND)
- IN  → Raspberry Pi PIN 11 (GPIO 17)

Hoặc dùng:
- VCC → Raspberry Pi PIN 4 (5V)
- GND → Raspberry Pi PIN 9 (GND)
- IN  → Raspberry Pi PIN 11 (GPIO 17)
```

**Bước 1.3: Kiểm tra kết nối**
```bash
# Kiểm tra GPIO pins
gpio readall | grep "17"
# Nếu không thấy, cài thêm:
sudo apt install -y wiringpi

# Sau đó:
gpio readall | grep "17"
```

**Checkpoint 1.3:**
- ✅ GPIO 17 nhìn thấy trong gpio readall

---

### 2️⃣ Test relay (Dry run - không có 220V)

**Bước 2.1: Simple GPIO test**
```bash
python3 << 'EOF'
import RPi.GPIO as GPIO
import time

RELAY_PIN = 17

# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT, initial=GPIO.LOW)

print("Testing relay...")
time.sleep(1)

# Turn ON
print("Turning relay ON...")
GPIO.output(RELAY_PIN, GPIO.HIGH)
print("Listen for CLICK sound!")
time.sleep(2)

# Turn OFF
print("Turning relay OFF...")
GPIO.output(RELAY_PIN, GPIO.LOW)
time.sleep(1)

# Cleanup
GPIO.cleanup()
print("✅ Test completed")
EOF
```

**Bước 2.2: Verify test**
- ✅ Nghe thấy "click" khi relay bật
- ✅ Nghe thấy "click" khi relay tắt
- ✅ Không có error message

**Checkpoint 2.2:**
- ✅ Relay click được

---

### 3️⃣ Nối dây 220V (ĐỐI TƯỢNG!)

⚠️ **CẢN TẬN - ĐÂY LÀ ĐIỆN CAO!**

**Bước 3.1: Chuẩn bị**
```
1. ⚠️ NGẮT circuit breaker OFF
2. ⚠️ Dùng voltmeter kiểm tra 0V
3. ⚠️ Không tiếp xúc dây điện trần
4. ⚠️ Nên có thợ điện bên cạnh
```

**Bước 3.2: Nối dây**
```
AC Outlet (220V):
- Dây L (nóng) → Relay COM
- Dây N (trung tính) → LED Neutral
- Dây PE (nối đất) → LED Ground

Relay → LED:
- Relay NO (Normally Open) → LED L
- LED N → AC Outlet N
- LED PE → AC Outlet PE
```

**Bước 3.3: Kiểm tra trước khi bật**
```
1. Circuit breaker: OFF
2. Voltmeter: 0V trên Relay COM ✅
3. Không có dây trần ✅
4. Tất cả nối chắc ✅
```

**Bước 3.4: Bật 220V từ từ**
```
1. Bật circuit breaker từ từ
2. Kiểm tra Relay COM: có ~220V không?
3. LED sáng chưa? (chưa, vì relay OFF)
```

**Checkpoint 3.4:**
- ✅ Relay COM có ~220V
- ✅ LED chưa sáng (vì relay OFF)

---

### 4️⃣ Test relay với 220V

**Bước 4.1: Test bật/tắt đèn**
```bash
python3 << 'EOF'
import RPi.GPIO as GPIO
import time

RELAY_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT, initial=GPIO.LOW)

print("⚠️ 220V TEST - Light will toggle")
time.sleep(2)

for cycle in range(3):
    print(f"\nCycle {cycle + 1}/3:")
    
    print("  Turning light ON...")
    GPIO.output(RELAY_PIN, GPIO.HIGH)
    time.sleep(3)
    print("  ✅ Light should be ON")
    
    print("  Turning light OFF...")
    GPIO.output(RELAY_PIN, GPIO.LOW)
    time.sleep(2)
    print("  ✅ Light should be OFF")

GPIO.cleanup()
print("\n✅ Test completed!")
EOF
```

**Bước 4.2: Verify**
- ✅ LED sáng khi relay ON
- ✅ LED tắt khi relay OFF
- ✅ 3 lần ON/OFF thành công
- ✅ Không có chập điện, không có khói

**Checkpoint 4.2:**
- ✅ Relay điều khiển đèn 220V thành công

---

### 5️⃣ Test relay.py module

**Bước 5.1: Extract project**
```bash
# Từ folder chứa smart-study-desk.tar.gz
tar -xzf smart-study-desk.tar.gz
cd smart-study-desk
```

**Bước 5.2: Test relay module**
```bash
python3 hardware/relay.py
```

**Expected output:**
```
🔌 Testing Relay Controller...
1️⃣ Turn relay ON...
  State: {'pin': 17, 'state': 'ON', ...}
2️⃣ Turn relay OFF...
  State: {'pin': 17, 'state': 'OFF', ...}
✅ Relay test passed
```

**Checkpoint 5.2:**
- ✅ relay.py test thành công
- ✅ ON/OFF logic hoạt động

---

### 6️⃣ Long-term reliability test

**Bước 6.1: 30-phút liên tục bật/tắt**
```bash
python3 << 'EOF'
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)

print("Running 30-minute relay stress test...")
start = time.time()

cycle = 0
while time.time() - start < 1800:  # 30 minutes
    GPIO.output(17, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(17, GPIO.LOW)
    time.sleep(1)
    
    cycle += 1
    if cycle % 60 == 0:
        elapsed = time.time() - start
        print(f"  {elapsed:.0f}s: {cycle} cycles completed")

GPIO.cleanup()
print("✅ Stress test passed!")
EOF
```

**Checkpoint 6.1:**
- ✅ 30 phút liên tục không lỗi
- ✅ Relay không nóng (< 50°C)
- ✅ LED sáng/tắt bình thường

---

## ✅ BƯỚC 2 DONE!

**Thời gian:** ~4-5 giờ
**Output:** Relay & Light control working
**Next:** BƯỚC 3 - Camera Pipeline

---

---

# 🟢 BƯỚC 3: CAMERA (1 ngày)

## Mục tiêu:
- ✅ Camera USB detect được
- ✅ Frame capture 25+ FPS
- ✅ Tối ưu resolution & CPU

## Chi tiết:

### 1️⃣ Cắm USB Webcam

**Bước 1.1: Physical connection**
```
1. Cắm USB webcam vào cổng USB của Raspberry
2. Chờ 2 giây
3. Check device:

sudo ls -la /dev/video*
# Output: /dev/video0, /dev/video1, etc. ✅
```

**Checkpoint 1.1:**
- ✅ /dev/video0 hoặc /dev/video1 xuất hiện

---

### 2️⃣ Install OpenCV

**Bước 2.1: Cài OpenCV**
```bash
# Install system dependencies
sudo apt install -y \
    libatlas-base-dev \
    libjasper-dev \
    libtiff-dev \
    libharfbuzz0b \
    libwebp6

# Install python-opencv
pip3 install opencv-python==4.8.0.76 --break-system-packages

# Verify
python3 -c "import cv2; print(cv2.__version__)"
# Output: 4.8.0 ✅
```

**Checkpoint 2.1:**
- ✅ OpenCV 4.8+ installed

---

### 3️⃣ Test camera capture

**Bước 3.1: Simple test**
```bash
python3 << 'EOF'
import cv2
import time

print("Testing camera capture...")

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Camera failed to open!")
    exit(1)

# Get properties
w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
fps = cap.get(cv2.CAP_PROP_FPS)

print(f"✅ Camera opened: {int(w)}x{int(h)} @ {fps:.1f}fps")

# Read 30 frames and measure FPS
start = time.time()
for i in range(100):
    ret, frame = cap.read()
    if not ret:
        print(f"❌ Frame {i}: FAILED")
        break

elapsed = time.time() - start
actual_fps = 100 / elapsed

print(f"✅ FPS: {actual_fps:.1f}")
print(f"✅ Frame shape: {frame.shape}")

cap.release()
print("✅ Camera test passed!")
EOF
```

**Expected output:**
```
✅ Camera opened: 640x480 @ 30.0fps
✅ FPS: 28.5
✅ Frame shape: (480, 640, 3)
✅ Camera test passed!
```

**Checkpoint 3.1:**
- ✅ FPS ≥ 20fps
- ✅ Frame shape correct

---

### 4️⃣ Test camera.py module

**Bước 4.1: Test**
```bash
python3 vision/camera.py
```

**Expected:**
```
🎥 Testing Camera...
✅ Camera info: {'device_id': 0, 'resolution': '640x480', 'fps': 30.0, 'frame_count': 10}
  Frame 0: (480, 640, 3)
  Frame 1: (480, 640, 3)
  ...
✅ Camera test passed
```

**Checkpoint 4.1:**
- ✅ camera.py test thành công

---

### 5️⃣ Optimize resolution & CPU

**Bước 5.1: Edit config.py**
```bash
nano config.py

# Tìm:
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
FRAME_WIDTH = 320
FRAME_HEIGHT = 240

# Nếu CPU cao (>70%), giảm xuống:
CAMERA_WIDTH = 320
CAMERA_HEIGHT = 240
FRAME_WIDTH = 160
FRAME_HEIGHT = 120

# Save: CTRL+X → Y → ENTER
```

**Bước 5.2: Test FPS**
```bash
python3 << 'EOF'
import cv2
import time

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

start = time.time()
for i in range(100):
    ret, frame = cap.read()
    
elapsed = time.time() - start
fps = 100 / elapsed

print(f"FPS: {fps:.1f}")
cap.release()
EOF
```

**Target:**
- ✅ FPS ≥ 20fps
- ✅ CPU < 50%
- ✅ Temperature < 55°C

**Checkpoint 5.2:**
- ✅ FPS stable ≥ 20fps
- ✅ CPU usage acceptable

---

### 6️⃣ Full camera test

**Bước 6.1: Run 5-phút test**
```bash
python3 << 'EOF'
import cv2
import time

print("Running 5-minute camera test...")
cap = cv2.VideoCapture(0)

start = time.time()
frame_count = 0

while time.time() - start < 300:  # 5 minutes
    ret, frame = cap.read()
    if not ret:
        print(f"❌ Frame read failed at {frame_count}")
        break
    
    frame_count += 1
    
    if frame_count % 150 == 0:
        elapsed = time.time() - start
        fps = frame_count / elapsed
        print(f"  {elapsed:.0f}s: {frame_count} frames, {fps:.1f}fps")

cap.release()
print("✅ Camera test passed!")
EOF
```

**Checkpoint 6.1:**
- ✅ 5 phút liên tục không lỗi
- ✅ FPS stable

---

## ✅ BƯỚC 3 DONE!

**Thời gian:** ~3-4 giờ
**Output:** Camera streaming stable 25+ FPS
**Next:** BƯỚC 4 - Motion Detection

---

(Các bước tiếp theo sẽ tương tự chi tiết như vậy...)

---

## 📌 CẤU TRÚC CÁC BƯỚC TIẾP THEO

### BƯỚC 4: MOTION DETECTION (2 ngày)
- Test motion_detector.py
- Tune MOTION_THRESHOLD
- Test ROI detection
- Verify 25+ FPS with detection

### BƯỚC 5: SLEEP DETECTION (2 ngày)
- Test face_detector.py
- Test eye detection
- Tune EYE_CLOSED_FRAMES
- Telegram test (optional)

### BƯỚC 6: POSTURE DETECTION (1 ngày)
- Test posture_detector.py
- Tune HEAD_DOWN_THRESHOLD
- Test head angle estimation

### BƯỚC 7: TELEGRAM (1 ngày)
- Create Telegram bot (@BotFather)
- Get token & chat ID
- Configure in config.py
- Test message sending

### BƯỚC 8: WEB DASHBOARD (2 ngày)
- Run web/app.py
- Access http://192.168.1.100:5000
- Test all buttons
- Test camera stream

### BƯỚC 9: FULL SYSTEM TEST (2 ngày)
- Run main.py
- 3-hour stress test
- Verify all detection
- Check logs

### BƯỚC 10: PRODUCTION (1 ngày)
- Setup systemd service
- Enable auto-start
- Verify reboot behavior
- Final documentation

---

## 📊 TIMELINE TỔNG HỢP

```
TUẦN 1:
  Mon-Tue: BƯỚC 1-3 (Setup hardware)
  Wed: BƯỚC 4 (Motion detection)

TUẦN 2:
  Mon-Tue: BƯỚC 5-6 (Sleep & posture)
  Wed-Thu: BƯỚC 7-8 (Telegram & web)

TUẦN 3:
  Mon-Tue: BƯỚC 9 (Testing)
  Wed: BƯỚC 10 (Production)

TOTAL: 2-3 TUẦN
```

---

**Document này là hướng dẫn chi tiết từng bước!**
**Cách sử dụng:**
1. Làm xong BƯỚC 1 → Kiểm tra checkpoint
2. Nếu ✅ → Tiếp tục BƯỚC 2
3. Nếu ❌ → Sửa lỗi, làm lại

**Happy learning! 📚💡**