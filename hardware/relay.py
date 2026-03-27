import sys
import os
import time

# Đoạn code xử lý đường dẫn để chạy trên Windows không lỗi gạch đỏ
try:
    import RPi.GPIO as GPIO
except (ImportError, RuntimeError):
    from unittest.mock import MagicMock
    GPIO = MagicMock()
    # type: ignore

# Thêm đường dẫn để tìm thấy config.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config

class RelayController:
    def __init__(self, pin=None):
        # Lấy chân PIN từ config (17), nếu không có thì dùng mặc định 17
        self.pin = pin or getattr(config, 'RELAY_PIN', 17)
        
        # Thiết lập GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.pin, GPIO.OUT, initial=GPIO.LOW)
        self.is_on = False
        print(f"✅ Relay đã sẵn sàng trên chân GPIO {self.pin}")

    def turn_on(self):
        """Bật Relay (Đèn sáng)"""
        GPIO.output(self.pin, GPIO.HIGH)
        self.is_on = True
        # print("💡 Relay ON")

    def turn_off(self):
        """Tắt Relay (Đèn tắt)"""
        GPIO.output(self.pin, GPIO.LOW)
        self.is_on = False
        # print("🌑 Relay OFF")

    def cleanup(self):
        """Dọn dẹp GPIO khi thoát"""
        GPIO.output(self.pin, GPIO.LOW)
        GPIO.cleanup(self.pin)

# --- PHẦN TEST (Giữ lại đoạn tạch tạch của bạn để chạy độc lập) ---
if __name__ == "__main__":
    relay = RelayController()
    try:
        print("🔌 Testing relay class...")
        relay.turn_on()  # Nghe CLICK?
        time.sleep(2)
        relay.turn_off() # Nghe CLICK?
        time.sleep(1)
        print("✅ Test completed")
    finally:
        relay.cleanup()