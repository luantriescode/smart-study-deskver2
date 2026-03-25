# ⭐ STEP 1: DEPLOY OS + NETWORK (1 ngày)

## 🎯 Mục tiêu
Chuẩn bị Raspberry Pi hoàn toàn sẵn sàng:
- ✅ Flash Raspberry Pi OS Lite
- ✅ Enable SSH
- ✅ Kết nối LAN DHCP
- ✅ Update hệ thống
- ✅ Set IP tĩnh
- ✅ Verify kết nối

---

## 📋 Chuẩn bị

### Hardware cần thiết:
- Raspberry Pi Model B+
- MicroSD card (≥16GB, Class 10)
- USB adapter + cáp MicroUSB (cấp điện)
- Ethernet cable hoặc WiFi adapter
- Laptop/PC để flash OS

### Software cần thiết:
- **Raspberry Pi Imager** (https://www.raspberrypi.com/software/)
- **SSH client** (MobaXTerm, PuTTY, hoặc Terminal)

---

## 🚀 Step-by-step

### 1️⃣ Flash Raspberry Pi OS

**1.1 Tải Raspberry Pi Imager**
```bash
# macOS
brew install --cask raspberry-pi-imager

# Linux
sudo apt install rpi-imager

# Windows
# Download from: https://www.raspberrypi.com/software/
```

**1.2 Mở Imager và cấu hình**
```
1. Click "CHOOSE DEVICE" → Chọn "Raspberry Pi B+"
2. Click "CHOOSE OS" → Chọn "Raspberry Pi OS (other)" → "Raspberry Pi OS Lite (32-bit)"
3. Click "CHOOSE STORAGE" → Chọn MicroSD card của bạn
4. Click "⚙️ NEXT" → Advanced options:
   - ✅ Set hostname: "smartdesk"
   - ✅ Enable SSH: Username "pi", Password "raspberry"
   - ✅ Configure wireless LAN: (nếu dùng WiFi)
   - ✅ Set locale: "Asia/Ho_Chi_Minh" (hoặc timezone của bạn)
5. Click "WRITE" → Chờ 5-10 phút
```

**1.3 Eject MicroSD**
```
⚠️ Đợi Imager hiển thị "Write successful"
Eject MicroSD một cách an toàn
```

---

### 2️⃣ Boot Raspberry Pi

**2.1 Cắm linh kiện**
```
1. Cắm MicroSD vào slot của Raspberry
2. Cắm Ethernet cable vào router (hoặc WiFi đã cấu hình)
3. Cắm USB power adapter → Raspberry sẽ boot
```

**2.2 Chờ boot xong**
```
⏱️ Chờ khoảng 1-2 phút để Raspberry hoàn tất boot
Đèn LED sẽ nhấp nháy → sau đó ổn định
```

---

### 3️⃣ SSH Login

**3.1 Tìm IP của Raspberry**

**Cách 1: Dùng router admin panel**
```
1. Mở http://192.168.1.1 (hoặc IP router của bạn)
2. Đăng nhập vào admin panel
3. Tìm "Connected Devices" → tìm "smartdesk"
4. Ghi lại IP (ví dụ: 192.168.1.100)
```

**Cách 2: Dùng nmap (Linux/macOS)**
```bash
sudo nmap -sn 192.168.1.0/24 | grep -i "smartdesk\|raspberry"
```

**Cách 3: Dùng arp**
```bash
arp -a | grep -i "b8:27:eb\|dc:a6:32"  # MAC prefix Raspberry
```

**3.2 SSH vào Raspberry**
```bash
# Username: pi
# Password: raspberry (hoặc password bạn đặt)
# IP: thay 192.168.1.100 bằng IP thực tế

ssh pi@192.168.1.100

# Nếu được hỏi "Are you sure?", gõ: yes
# Enter password khi được hỏi
```

**Kết quả thành công:**
```
pi@smartdesk:~ $
```

---

### 4️⃣ Update Hệ thống

```bash
# Update package list
sudo apt update

# Upgrade packages
sudo apt upgrade -y

# Install useful tools
sudo apt install -y \
    python3-pip \
    python3-dev \
    git \
    nano \
    htop \
    curl \
    wget

# Reboot
sudo reboot

# Chờ 30s rồi SSH lại
```

---

### 5️⃣ Set IP Tĩnh (Static IP)

**5.1 Xem cấu hình hiện tại**
```bash
ip addr show
# Ghi lại:
# - Interface name (thường là eth0 hoặc wlan0)
# - Gateway IP
# - DNS servers

1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host noprefixroute
       valid_lft forever preferred_lft forever
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether b8:27:eb:5c:3c:b1 brd ff:ff:ff:ff:ff:ff
    inet 192.168.1.8/24 brd 192.168.1.255 scope global dynamic noprefixroute eth0
       valid_lft 3461sec preferred_lft 3461sec
    inet6 fe80::ba27:ebff:fe5c:3cb1/64 scope link noprefixroute
       valid_lft forever preferred_lft forever
```
**5.2 Chỉnh sửa `/etc/dhcpcd.conf`**
```bash
sudo nano /etc/dhcpcd.conf
```

**Thêm ở cuối file:**
```
# Static IP configuration
interface eth0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=8.8.8.8 8.8.4.4
```

> **Lưu ý:**
> - `192.168.1.100` → Đổi thành IP bạn muốn
> - `192.168.1.1` → Đổi thành gateway của bạn
> - Nếu dùng WiFi, đổi `eth0` thành `wlan0`

**5.3 Save & Reboot**
```bash
# Save: CTRL+X → Y → ENTER
# Reboot
sudo reboot

# Chờ 30s, SSH lại với IP mới
ssh pi@192.168.1.100
```

---

### 6️⃣ Verify Kết nối

```bash
# ✅ Check IP
ip addr show

# ✅ Check internet
ping 8.8.8.8

# ✅ Check DNS
ping google.com

# ✅ Check time sync
timedatectl

# ✅ Check uptime
uptime

# ✅ Check disk space
df -h

# ✅ Check RAM
free -h
```

**Output mong muốn:**
```
PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.
64 bytes from 8.8.8.8: icmp_seq=1 ttl=119 time=25.3 ms
```

---

## 📦 Optional: Cấu hình thêm

### Thay đổi hostname (nếu cần)
```bash
sudo raspi-config
# Select: System Options → Hostname
```

### Thay đổi timezone
```bash
sudo timedatectl set-timezone Asia/Ho_Chi_Minh
```

### Enable 1-wire (nếu dùng sensors)
```bash
sudo raspi-config
# Select: Interface Options → 1-Wire → Enable
```

### Cấu hình WiFi (nếu không có Ethernet)
```bash
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf

# Thêm:
network={
    ssid="YOUR_WIFI_NAME"
    psk="YOUR_PASSWORD"
}
```

---

## ✅ Checklist STEP 1 Complete

- [ ] MicroSD card được flash thành công
- [ ] Raspberry Pi boot lên được
- [ ] SSH login thành công
- [ ] Kết nối internet ổn định (ping thành công)
- [ ] IP tĩnh đã set (không thay đổi)
- [ ] System updated (apt upgrade hoàn tất)
- [ ] Hostname set thành "smartdesk"

---

## 🐛 Troubleshooting

### SSH connection refused
```bash
# Kiểm tra SSH service
sudo systemctl status ssh

# Nếu không chạy, enable nó
sudo systemctl enable ssh
sudo systemctl start ssh
```

### IP không thay đổi sau reboot
```bash
# Kiểm tra file config
cat /etc/dhcpcd.conf | grep -A5 "interface"

# Kiểm tra IP hiện tại
ip addr show
```

### No internet connection
```bash
# Kiểm tra network status
sudo ip link show

# Khởi động lại networking
sudo systemctl restart networking

# Kiểm tra gateway
ip route show
```

### Forgot password?
```
# Boot từ MicroSD, mount nó từ máy tính khác
# Thay đổi /etc/shadow nếu cần
# (Hoặc flash lại OS từ Imager)
```

---

## 📊 Performance Check

```bash
# Verify Raspberry Pi specifications
cat /proc/cpuinfo | grep -E "processor|Model|Revision"

# Verify memory
cat /proc/meminfo | head -5

# Check temperature
vcgencmd measure_temp

# Monitor in real-time
htop
```

---

## 🎉 STEP 1 Done!

Raspberry Pi của bạn giờ đã sẵn sàng cho **STEP 2: GPIO + Relay Testing**.

### Tiếp theo:
```bash
# Chuẩn bị cho STEP 2
# Clone project repo
git clone <repo-url> ~/smart-study-desk
cd ~/smart-study-desk
```

---

**⏱️ Thời gian dự kiến: 1-2 giờ**
**💾 Dung lượng cần: ~3GB**
**🔌 Yêu cầu điện: USB 5V/2A stabil**
