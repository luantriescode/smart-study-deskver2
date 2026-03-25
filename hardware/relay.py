"""
HARDWARE/RELAY.PY - Relay Control
===================================
Quản lý:
  - GPIO relay control
  - On/Off logic
  - Safety features
  - Simulation mode
"""

import logging
import time

import config

logger = logging.getLogger(__name__)


class RelayController:
    """Điều khiển relay qua GPIO"""
    
    def __init__(self, pin=None, simulate=None):
        """
        Khởi tạo relay controller
        
        Args:
            pin: GPIO pin number (default: config.RELAY_PIN)
            simulate: Use simulation mode? (default: config.SIMULATE_HARDWARE)
        """
        self.pin = pin or config.RELAY_PIN
        self.simulate = simulate if simulate is not None else config.SIMULATE_HARDWARE
        
        self.is_on = False
        self.last_toggle_time = time.time()
        self.toggle_count = 0
        
        if self.simulate:
            logger.info(f"⚠️  RELAY SIMULATION MODE (pin {self.pin})")
        else:
            self._init_gpio()
            logger.info(f"✅ Relay initialized on GPIO {self.pin}")
    
    def _init_gpio(self):
        """Khởi tạo GPIO"""
        try:
            import RPi.GPIO as GPIO
            
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin, GPIO.OUT, initial=GPIO.LOW)
            
            logger.info(f"GPIO {self.pin} initialized (mode: BCM, initial: LOW)")
        
        except ImportError:
            logger.error("RPi.GPIO not installed. Falling back to simulation.")
            self.simulate = True
        
        except Exception as e:
            logger.error(f"Failed to init GPIO: {e}. Falling back to simulation.")
            self.simulate = True
    
    def on(self):
        """Bật relay (bật đèn)"""
        if self.is_on:
            return  # Already on
        
        try:
            if not self.simulate:
                import RPi.GPIO as GPIO
                GPIO.output(self.pin, GPIO.HIGH)
            
            self.is_on = True
            self.last_toggle_time = time.time()
            self.toggle_count += 1
            
            logger.info(f"🔌 RELAY ON (pin {self.pin})")
        
        except Exception as e:
            logger.error(f"Failed to turn relay ON: {e}")
    
    def off(self):
        """Tắt relay (tắt đèn)"""
        if not self.is_on:
            return  # Already off
        
        try:
            if not self.simulate:
                import RPi.GPIO as GPIO
                GPIO.output(self.pin, GPIO.LOW)
            
            self.is_on = False
            self.last_toggle_time = time.time()
            self.toggle_count += 1
            
            logger.info(f"🔌 RELAY OFF (pin {self.pin})")
        
        except Exception as e:
            logger.error(f"Failed to turn relay OFF: {e}")
    
    def toggle(self):
        """Đảo trạng thái relay"""
        if self.is_on:
            self.off()
        else:
            self.on()
    
    def get_state(self):
        """Lấy trạng thái (True = on, False = off)"""
        return self.is_on
    
    def get_info(self):
        """Lấy thông tin relay"""
        return {
            "pin": self.pin,
            "state": "ON" if self.is_on else "OFF",
            "simulate": self.simulate,
            "toggle_count": self.toggle_count,
            "last_toggle": time.time() - self.last_toggle_time
        }
    
    def cleanup(self):
        """Dọn dẹp GPIO"""
        try:
            if not self.simulate:
                import RPi.GPIO as GPIO
                GPIO.cleanup(self.pin)
                logger.info(f"GPIO {self.pin} cleaned up")
        
        except Exception as e:
            logger.warning(f"Failed to cleanup GPIO: {e}")


# ============================================
# ADVANCED: PWM BRIGHTNESS CONTROL
# ============================================

class PWMRelayController(RelayController):
    """Relay controller with PWM support (brightness control)"""
    
    def __init__(self, pin=None, frequency=1000, simulate=None):
        """
        Khởi tạo PWM relay
        
        Args:
            pin: GPIO pin
            frequency: PWM frequency (Hz)
            simulate: Simulation mode
        """
        super().__init__(pin, simulate)
        
        self.frequency = frequency
        self.brightness = 100  # 0-100%
        self.pwm = None
        
        if not self.simulate:
            self._init_pwm()
    
    def _init_pwm(self):
        """Khởi tạo PWM"""
        try:
            import RPi.GPIO as GPIO
            
            self.pwm = GPIO.PWM(self.pin, self.frequency)
            self.pwm.start(100)  # Start at 100%
            
            logger.info(f"PWM initialized on GPIO {self.pin} ({self.frequency}Hz)")
        
        except Exception as e:
            logger.error(f"Failed to init PWM: {e}")
            self.pwm = None
    
    def set_brightness(self, brightness):
        """
        Đặt độ sáng (0-100%)
        
        Args:
            brightness: 0-100
        """
        brightness = max(0, min(100, brightness))
        
        if self.brightness == brightness:
            return
        
        self.brightness = brightness
        
        try:
            if not self.simulate and self.pwm:
                self.pwm.ChangeDutyCycle(brightness)
            
            logger.info(f"💡 Brightness set to {brightness}%")
        
        except Exception as e:
            logger.error(f"Failed to set brightness: {e}")
    
    def cleanup(self):
        """Dọn dẹp"""
        try:
            if self.pwm:
                self.pwm.stop()
        except:
            pass
        
        super().cleanup()


# ============================================
# SAFETY MONITOR
# ============================================

class RelaySafetyMonitor:
    """Giám sát an toàn relay (chống quá tải, quá nhiệt, etc.)"""
    
    def __init__(self, relay, max_on_time=3600, max_toggles_per_minute=10):
        """
        Khởi tạo safety monitor
        
        Args:
            relay: RelayController instance
            max_on_time: Max liên tục bật (giây)
            max_toggles_per_minute: Max bật/tắt mỗi phút
        """
        self.relay = relay
        self.max_on_time = max_on_time
        self.max_toggles_per_minute = max_toggles_per_minute
        
        self.on_start_time = None
        self.toggle_times = []  # List of recent toggle times
    
    def check_safe(self):
        """Kiểm tra relay có an toàn không"""
        # Check on time
        if self.relay.is_on:
            on_duration = time.time() - (self.on_start_time or time.time())
            
            if on_duration > self.max_on_time:
                logger.warning(f"⚠️  Relay ON for {on_duration}s (max: {self.max_on_time}s)")
                return False
        
        # Check toggle frequency
        now = time.time()
        self.toggle_times = [t for t in self.toggle_times if now - t < 60]
        
        if len(self.toggle_times) > self.max_toggles_per_minute:
            logger.warning(
                f"⚠️  Too many toggles ({len(self.toggle_times)} in 60s)"
            )
            return False
        
        return True
    
    def record_toggle(self):
        """Record relay toggle"""
        self.toggle_times.append(time.time())
        
        if self.relay.is_on:
            self.on_start_time = time.time()


# ============================================
# STANDALONE TEST
# ============================================

def test_relay():
    """Test relay control"""
    print("🔌 Testing Relay Controller...")
    
    try:
        # Test in simulation mode
        relay = RelayController(simulate=True)
        
        print("1️⃣ Turn relay ON...")
        relay.on()
        assert relay.get_state() == True
        print("  State:", relay.get_info())
        
        print("2️⃣ Turn relay OFF...")
        relay.off()
        assert relay.get_state() == False
        print("  State:", relay.get_info())
        
        print("3️⃣ Toggle...")
        relay.toggle()
        print("  State:", relay.get_info())
        
        relay.toggle()
        print("  State:", relay.get_info())
        
        relay.cleanup()
        
        print("\n✅ Relay test passed")
    
    except Exception as e:
        print(f"❌ Relay test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_relay()
