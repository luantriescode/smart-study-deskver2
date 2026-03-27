import RPi.GPIO as GPIO
import time
import config

class RelayController:
    def __init__(self, pin=None):
        # Lấy chân GPIO từ config (mặc định là 17)
        self.pin = pin or config.RELAY_PIN
        
        # Thiết lập chế độ BCM
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Thiết lập chân Relay là OUTPUT, mặc định là LOW (Tắt)
        GPIO.setup(self.pin, GPIO.OUT, initial=GPIO.LOW)
        self.state = False

    def turn_on(self):
        """Bật Relay (Đèn sáng)"""
        GPIO.output(self.pin, GPIO.HIGH)
        self.state = True
        return True

    def turn_off(self):
        """Tắt Relay (Đèn tắt)"""
        GPIO.output(self.pin, GPIO.LOW)
        self.state = False
        return True

    def cleanup(self):
        """Giải phóng GPIO khi thoát chương trình"""
        GPIO.cleanup(self.pin)

# Test nhanh module
if __name__ == "__main__":
    relay = RelayController()
    print("🔌 Đang test Relay trên GPIO 17...")
    try:
        print("💡 BẬT ĐÈN..."); relay.turn_on()
        time.sleep(2)
        print("🌑 TẮT ĐÈN..."); relay.turn_off()
        time.sleep(1)
    finally:
        relay.cleanup()