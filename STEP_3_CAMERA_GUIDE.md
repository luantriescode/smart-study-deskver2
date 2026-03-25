# ⭐ STEP 3: CAMERA PIPELINE (1 ngày)

## 🎯 Mục tiêu
Thiết lập webcam USB realtime streaming + optimize CPU usage

---

## 📋 Chuẩn bị

### Hardware
- USB Webcam (960p hoặc cao hơn)
- USB cable (hoặc already connected)

### Software
- OpenCV (đã cài từ STEP 1)
- Python3

---

## 🚀 Step-by-step

### 1️⃣ Verify Camera Connection

**Check camera device:**
```bash
# List cameras
ls -la /dev/video*

# Output should show:
# /dev/video0  ← USB camera
# /dev/video1  ← (optional, if using CSI camera too)
```

**If no /dev/video*, try:**
```bash
# Restart udev
sudo udevadm control --reload-rules && sudo udevadm trigger

# Or replug USB cable
```

### 2️⃣ Test Camera with OpenCV

**Simple test script:**
```bash
python3 << 'EOF'
import cv2

print("Testing camera...")
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Camera failed to open!")
    exit(1)

# Get properties
w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
fps = cap.get(cv2.CAP_PROP_FPS)

print(f"✅ Camera opened: {int(w)}x{int(h)} @ {fps:.1f}fps")

# Read 10 frames
for i in range(10):
    ret, frame = cap.read()
    if ret:
        print(f"  Frame {i}: shape={frame.shape}, dtype={frame.dtype}")
    else:
        print(f"  Frame {i}: FAILED")

cap.release()
print("✅ Camera test passed")
EOF
```

**Expected output:**
```
Testing camera...
✅ Camera opened: 640x480 @ 30.0fps
  Frame 0: shape=(480, 640, 3), dtype=uint8
  Frame 1: shape=(480, 640, 3), dtype=uint8
  ...
✅ Camera test passed
```

### 3️⃣ Test Camera Module

**Dùng project camera.py:**
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

### 4️⃣ Optimize Resolution & FPS

**Edit config.py:**
```python
# Original (high quality, high CPU)
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30

# Processing (lower quality, lower CPU)
FRAME_WIDTH = 320    # Resize for processing
FRAME_HEIGHT = 240

# Optimized (low CPU, good enough)
CAMERA_WIDTH = 320
CAMERA_HEIGHT = 240
CAMERA_FPS = 15
```

**Test different resolutions:**
```bash
python3 << 'EOF'
import cv2
import time

resolutions = [
    (640, 480),
    (480, 360),
    (320, 240),
    (160, 120)
]

for w, h in resolutions:
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
    
    start = time.time()
    for _ in range(100):
        ret, frame = cap.read()
    elapsed = time.time() - start
    
    fps = 100 / elapsed
    actual_w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    actual_h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    
    print(f"{int(actual_w)}x{int(actual_h)}: {fps:.1f}fps ({elapsed:.2f}s for 100 frames)")
    
    cap.release()
EOF
```

**Choose resolution based on:**
- ✅ >= 20 FPS for smooth detection
- ✅ < 50% CPU usage
- ✅ >= 320x240 for face detection to work

### 5️⃣ Test Frame Resize

**Resize optimization:**
```bash
python3 << 'EOF'
import cv2
import time

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Test different resize methods
methods = {
    'LINEAR': cv2.INTER_LINEAR,
    'AREA': cv2.INTER_AREA,
    'CUBIC': cv2.INTER_CUBIC,
    'NEAREST': cv2.INTER_NEAREST
}

target_size = (320, 240)

for method_name, method in methods.items():
    start = time.time()
    for _ in range(50):
        ret, frame = cap.read()
        resized = cv2.resize(frame, target_size, interpolation=method)
    elapsed = time.time() - start
    
    fps = 50 / elapsed
    print(f"{method_name}: {fps:.1f}fps")

cap.release()
EOF
```

**Recommended: INTER_LINEAR** (fast, good quality)

### 6️⃣ Test Real-time Performance

**CPU monitoring test:**
```bash
# Terminal 1: Run camera loop
python3 << 'EOF'
import cv2
import time

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

print("Running camera loop... (Press Ctrl+C to stop)")
print("Monitor CPU with: htop")

start = time.time()
frame_count = 0

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Simulate processing
        resized = cv2.resize(frame, (160, 120))
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        
        # Print every 30 frames
        if frame_count % 30 == 0:
            elapsed = time.time() - start
            fps = frame_count / elapsed
            print(f"Frame {frame_count}: {fps:.1f}fps")

except KeyboardInterrupt:
    pass

cap.release()
print("Done")
EOF

# Terminal 2: Monitor system
htop
```

**Expected CPU:**
- 320x240 @ 30fps: 20-30% CPU
- 640x480 @ 30fps: 40-60% CPU
- Temperature: <55°C

### 7️⃣ Test ROI Cropping

**Test ROI performance:**
```bash
python3 << 'EOF'
import cv2
from config import ROI_X, ROI_Y, ROI_W, ROI_H
import time

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

roi = (ROI_X, ROI_Y, ROI_W, ROI_H)

print(f"ROI: {roi}")
print("Grabbing 100 frames with ROI crop...")

start = time.time()
for i in range(100):
    ret, frame = cap.read()
    if not ret:
        break
    
    # Crop ROI
    x, y, w, h = roi
    roi_frame = frame[y:y+h, x:x+w]

elapsed = time.time() - start
fps = 100 / elapsed

print(f"FPS: {fps:.1f}")
print(f"ROI size: {roi_frame.shape}")

cap.release()
EOF
```

### 8️⃣ Save Sample Frames

**For debugging later:**
```bash
python3 << 'EOF'
import cv2
from pathlib import Path

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

sample_dir = Path("./logs/samples")
sample_dir.mkdir(exist_ok=True)

print("Saving 10 sample frames...")
for i in range(10):
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(f"{sample_dir}/frame_{i:03d}.jpg", frame)
        print(f"  Saved frame_{i:03d}.jpg")

cap.release()
print("✅ Samples saved to logs/samples/")
EOF
```

---

## 🔧 Fine-tuning

### Exposure Adjustment
```python
# If too dark/bright
cap.set(cv2.CAP_PROP_EXPOSURE, -5)  # Range: -13 to 0
cap.set(cv2.CAP_PROP_BRIGHTNESS, 50) # Range: 0-100
cap.set(cv2.CAP_PROP_CONTRAST, 50)   # Range: 0-100
```

### Focus Lock
```python
# Auto-focus
cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)

# Manual focus (if supported)
cap.set(cv2.CAP_PROP_FOCUS, 0)
```

### FPS Control
```python
# Set target FPS
cap.set(cv2.CAP_PROP_FPS, 30)

# Verify actual FPS
actual_fps = cap.get(cv2.CAP_PROP_FPS)
print(f"FPS: {actual_fps}")
```

---

## 📊 Benchmarking

### Full Test Suite

```bash
python3 << 'EOF'
import cv2
import time
import numpy as np

print("="*50)
print("CAMERA PIPELINE BENCHMARKS")
print("="*50)

cap = cv2.VideoCapture(0)

# Test different resolutions
configs = [
    ("640x480 Full Quality", 640, 480),
    ("480x360 High", 480, 360),
    ("320x240 Medium", 320, 240),
    ("160x120 Low", 160, 120),
]

for name, w, h in configs:
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
    
    start = time.time()
    for _ in range(100):
        ret, frame = cap.read()
    
    elapsed = time.time() - start
    fps = 100 / elapsed
    
    print(f"\n{name}:")
    print(f"  FPS: {fps:.1f}")
    print(f"  Time/frame: {elapsed/100*1000:.1f}ms")
    print(f"  Size: {frame.nbytes/1024/1024:.1f}MB per second")

cap.release()
print("\n" + "="*50)
EOF
```

---

## 📈 Optimization Checklist

- [ ] Camera detected (/dev/video0 exists)
- [ ] Can read frames at 30fps
- [ ] Resize working correctly
- [ ] ROI crop tested
- [ ] CPU usage < 50%
- [ ] Temperature < 60°C
- [ ] FPS stable (no drops)
- [ ] Frame quality acceptable
- [ ] Sample frames saved

---

## 🐛 Troubleshooting

### "Cannot open camera"
```bash
# 1. Check if camera is mounted
lsusb | grep Camera

# 2. Check if being used elsewhere
lsof /dev/video0

# 3. Try different device
python3 -c "import cv2; cap = cv2.VideoCapture(1); print(cap.isOpened())"

# 4. Replug USB
```

### Low FPS
```bash
# 1. Check resolution
cap.get(cv2.CAP_PROP_FRAME_WIDTH)

# 2. Reduce resolution in config.py

# 3. Check for USB bandwidth issues
# Use different USB port

# 4. Check if other processes using camera
ps aux | grep -i camera
```

### Dark/Blurry frames
```bash
# 1. Clean camera lens
# 2. Adjust lighting
# 3. Adjust exposure:
cap.set(cv2.CAP_PROP_EXPOSURE, -5)
cap.set(cv2.CAP_PROP_BRIGHTNESS, 60)

# 4. Focus adjustment (if supported)
cap.set(cv2.CAP_PROP_FOCUS, 0)
```

### High CPU usage
```bash
# 1. Reduce resolution
# 2. Reduce FPS
# 3. Use INTER_AREA for resize
# 4. Check for background processes
top
```

---

## 🎉 STEP 3 Complete!

Camera pipeline working smoothly → sẵn sàng cho **STEP 4: Person Detection MVP**

### Next:
```bash
python3 vision/motion_detector.py
```

---

**⏱️ Thời gian: 1-2 giờ**
**📊 Target: 320x240 @ 25fps, <40% CPU**
