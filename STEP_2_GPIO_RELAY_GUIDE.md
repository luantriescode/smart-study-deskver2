# ⭐ STEP 2: GPIO + RELAY TESTING (0.5 ngày)

## 🎯 Mục tiêu
Kiểm thử GPIO relay hoạt động bình thường để điều khiển đèn 220V

---

## 📋 Chuẩn bị Hardware

### Relay Module
- **Relay 5V 1-channel** (JQC-3FF-S-Z hoặc tương đương)
- **Signal pin:** Nối với GPIO 17 (Raspberry Pi)
- **VCC:** Nối 5V
- **GND:** Nối GND

### Raspberry Pi Pinout
```
PIN 1  - 3V3
PIN 2  - 5V (cho relay VCC)
PIN 4  - 5V
PIN 6  - GND (cho relay GND)
PIN 11 - GPIO 17 (Signal)
PIN 17 - 3V3
PIN 20 - GND
```

### AC Light 220V
⚠️ **CÁCH ĐIỆN TỪ TẦNG:**
- IN: Dây L (nóng) từ ổ điện
- OUT: Dây L qua relay
- Neutral: Nối trực tiếp
- Ground: Nối trực tiếp

---

## 🔌 Wiring Diagram

```
Raspberry Pi                   Relay Module
═══════════════════════════════════════════════
    5V (PIN 2) ─────────────► VCC
   GND (PIN 6) ─────────────► GND
  GPIO 17 (PIN 11) ──────────► Signal (In)

Relay Module                   AC Light 220V
═══════════════════════════════════════════════
    COM ────────────────────► L (From outlet)
    NO (Normally Open) ────► L (To light)
                            N ──────────────► N
                            PE ─────────────► PE
```

### Schematic (Text)
```
AC Outlet (220V)
      │
      L (Hot wire)
      │
   ┌──┴──┐
   │ COM │ Relay
   ├─────┤  Module
   │  NO │
   └──┬──┘
      │
    Light (LED/Bulb)
```

---

## ✅ Step-by-step Testing

### 1️⃣ Hardware Connection Verification

**SSH vào Raspberry:**
```bash
ssh pi@192.168.1.100
cd ~/smart-study-desk
```

**Xác nhận GPIO pin:**
```bash
# Liệt kê GPIO pins
gpio readall

# Hoặc dùng Python
python3 << 'EOF'
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT, initial=GPIO.LOW)
print("✅ GPIO 17 initialized successfully")
GPIO.cleanup()
EOF
```

### 2️⃣ Test Relay Control (Dry Run - không có dòng điện)

**Test script - bật/tắt relay:**
```bash
python3 << 'EOF'
import RPi.GPIO as GPIO
import time

RELAY_PIN = 17

# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT, initial=GPIO.LOW)

print("Starting relay test...")
time.sleep(1)

# Turn ON
print("Turning relay ON...")
GPIO.output(RELAY_PIN, GPIO.HIGH)
time.sleep(2)

# Check state
state = GPIO.input(RELAY_PIN)
print(f"Relay state: {'ON' if state else 'OFF'}")

# Turn OFF
print("Turning relay OFF...")
GPIO.output(RELAY_PIN, GPIO.LOW)
time.sleep(2)

# Check state
state = GPIO.input(RELAY_PIN)
print(f"Relay state: {'ON' if state else 'OFF'}")

# Cleanup
GPIO.cleanup()
print("✅ Test completed")
EOF
```

**Expected output:**
```
Starting relay test...
Turning relay ON...
Relay state: 1
Turning relay OFF...
Relay state: 0
✅ Test completed
```

### 3️⃣ Test Relay Module Directly

**Kiểm tra relay click sound:**
```bash
python3 << 'EOF'
import RPi.GPIO as GPIO
import time

RELAY_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)

# Relay should "click" when switching
for i in range(10):
    GPIO.output(RELAY_PIN, GPIO.HIGH)
    print("CLICK ON", end="")
    time.sleep(0.3)
    
    GPIO.output(RELAY_PIN, GPIO.LOW)
    print(" → CLICK OFF")
    time.sleep(0.3)

GPIO.cleanup()
print("✅ Relay clicking test done")
EOF
```

**Nghe thấy:** "click...click...click" từ relay = ✅ OK

### 4️⃣ Test With Actual Light (WITH POWER)

⚠️ **DANGER:** 220V AC điện áp cao - cẩn thận!

**Step-by-step:**
1. ✅ Ngắt ổ điện 220V (Circuit breaker OFF)
2. ✅ Kiểm tra không có dòng điện bằng voltmeter
3. ✅ Nối dây L từ ổ điện vào Relay COM
4. ✅ Nối dây L từ Relay NO vào đèn
5. ✅ Nối Neutral + Ground trực tiếp
6. ✅ Bật Circuit breaker từ từ
7. ✅ Chạy test code

**Test code:**
```bash
python3 << 'EOF'
import RPi.GPIO as GPIO
import time

RELAY_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT, initial=GPIO.LOW)

print("⚠️  LIGHT TEST - Relay will toggle")
print("🔴 Make sure 220V is connected!")
time.sleep(2)

for cycle in range(3):
    print(f"\nCycle {cycle + 1}/3:")
    
    print("  Turning light ON...")
    GPIO.output(RELAY_PIN, GPIO.HIGH)
    time.sleep(3)
    
    print("  Turning light OFF...")
    GPIO.output(RELAY_PIN, GPIO.LOW)
    time.sleep(2)

GPIO.cleanup()
print("\n✅ Light test completed!")
EOF
```

### 5️⃣ Test Relay Controller Module

**Dùng project relay.py:**
```bash
python3 hardware/relay.py
```

**Expected output:**
```
🔌 Testing Relay Controller...
1️⃣ Turn relay ON...
  State: {'pin': 17, 'state': 'ON', 'simulate': False, 'toggle_count': 1, 'last_toggle': 0.0}
2️⃣ Turn relay OFF...
  State: {'pin': 17, 'state': 'OFF', 'simulate': False, 'toggle_count': 2, 'last_toggle': 0.1}
3️⃣ Toggle...
  State: {'pin': 17, 'state': 'ON', 'simulate': False, 'toggle_count': 3, 'last_toggle': 0.1}

✅ Relay test passed
```

---

## 🧪 Advanced Tests

### Test Relay Safety
```bash
python3 << 'EOF'
from hardware.relay import RelaySafetyMonitor, RelayController
import time

relay = RelayController()
monitor = RelaySafetyMonitor(
    relay,
    max_on_time=60,           # Max 60s continuous
    max_toggles_per_minute=20
)

for i in range(25):  # Test toggle limit
    relay.toggle()
    monitor.record_toggle()
    time.sleep(1)
    
    if not monitor.check_safe():
        print(f"⚠️  Safety limit reached at toggle {i+1}")
        break

relay.cleanup()
EOF
```

### Test Long-term Reliability
```bash
python3 << 'EOF'
from hardware.relay import RelayController
import time

relay = RelayController()

print("Testing relay for 10 minutes (100 cycles)...")
start = time.time()

for cycle in range(100):
    relay.on()
    time.sleep(3)
    relay.off()
    time.sleep(3)
    
    if cycle % 10 == 0:
        elapsed = time.time() - start
        print(f"  Cycle {cycle}: {elapsed:.0f}s elapsed")

relay.cleanup()
print("✅ Long-term test passed!")
EOF
```

---

## 📊 Troubleshooting

### Relay không bật
```bash
# 1. Check GPIO pin
gpio readall | grep "17"

# 2. Check voltage
python3 << 'EOF'
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
GPIO.output(17, GPIO.HIGH)
print("Check GPIO 17 with voltmeter (should be ~3.3V)")
input("Press enter when done...")
GPIO.cleanup()
EOF

# 3. Check relay VCC/GND
# Nếu không có 5V, check power supply
```

### Relay bị kẹt (stuck)
```bash
# Reset GPIO
python3 << 'EOF'
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
GPIO.output(17, GPIO.LOW)
time.sleep(5)
GPIO.cleanup()
print("GPIO reset")
EOF

# Hoặc reboot Raspberry
sudo reboot
```

### Light không bật dù relay OK
```
❌ Troubleshoot:
1. Kiểm tra 220V có vào relay không (voltmeter)
2. Kiểm tra dây nối
3. Kiểm tra đèn có hoạt động không (test với plug trực tiếp)
4. Kiểm tra fuse trong circuit breaker
5. Gọi thợ điện nếu cần
```

### Relay quá nóng
```
⚠️ Danger signs:
- Relay nóng quá (>50°C)
- Mùi cháy
- Khó bật/tắt

⚠️ Action:
1. Tắt ngay circuit breaker
2. Để lạnh
3. Thay relay mới
4. Kiểm tra có short circuit không
```

---

## 📈 Performance Metrics

| Metric | Expected | Tolerance |
|--------|----------|-----------|
| Turn-on time | <50ms | ±10ms |
| Turn-off time | <50ms | ±10ms |
| Voltage drop | <0.1V | ±0.05V |
| Current draw | <100mA @ 5V | ±10mA |
| Relay life | >1M cycles | Min 100k |

---

## ✅ STEP 2 Checklist

- [ ] Relay module physically connected
- [ ] GPIO pin verified (Pin 11 = GPIO 17)
- [ ] Relay "clicks" when toggled
- [ ] Relay voltage test passed
- [ ] Dry run test passed (no AC power)
- [ ] Light turns on/off correctly
- [ ] Relay.py test passed
- [ ] Long-term reliability verified
- [ ] No overheating observed

---

## 🎉 STEP 2 Complete!

Relay hoạt động bình thường → sẵn sàng cho **STEP 3: Camera Pipeline**

### Tiếp theo:
```bash
# Chạy camera test
python3 vision/camera.py
```

---

**⏱️ Thời gian: 0.5 - 1 giờ**
**🔧 Tools cần: Voltmeter (nếu có), Screwdriver**
**💡 Safety: Cơn nguy hiểm - nên có người bên cạnh**
