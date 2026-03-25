"""
CORE/STATE_MACHINE.PY - State Machine for Light Control
==========================================================
Quản lý:
  - Trạng thái hệ thống (OFF, ON, COUNTDOWN)
  - Logic bật/tắt đèn
  - Delay 10s khi người rời đi
  - Transitions
"""

import time
import logging
from enum import Enum

import config

logger = logging.getLogger(__name__)


class LightState(Enum):
    """Các trạng thái của đèn"""
    OFF = "OFF"              # Đèn tắt
    ON = "ON"                # Đèn bật
    COUNTDOWN = "COUNTDOWN"  # Đếm ngược trước khi tắt


class StateMachine:
    """Máy trạng thái điều khiển đèn"""
    
    def __init__(self, relay=None):
        """
        Khởi tạo state machine
        
        Args:
            relay: RelayController instance
        """
        self.relay = relay
        self.current_state = LightState.OFF
        self.last_person_time = None
        self.state_change_time = time.time()
        
        logger.info("StateMachine initialized")
    
    def update(self, person_detected):
        """
        Cập nhật trạng thái dựa trên phát hiện người
        
        Args:
            person_detected: bool - Có phát hiện người không
        """
        current_time = time.time()
        
        if person_detected:
            self.last_person_time = current_time
            
            # Người detected → bật đèn ngay
            if self.current_state != LightState.ON:
                self._transition_to_on(current_time)
        
        else:
            # Người không detected
            if self.current_state == LightState.ON:
                # Switch to countdown
                self._transition_to_countdown(current_time)
            
            elif self.current_state == LightState.COUNTDOWN:
                # Check if countdown expired
                elapsed = current_time - self.state_change_time
                
                if elapsed >= config.PERSON_LOST_DELAY:
                    # Countdown complete → tắt đèn
                    self._transition_to_off(current_time)
    
    def _transition_to_on(self, timestamp):
        """Chuyển sang trạng thái ON"""
        if self.current_state == LightState.ON:
            return  # Already ON
        
        self.current_state = LightState.ON
        self.state_change_time = timestamp
        
        # Bật relay
        if self.relay:
            self.relay.on()
        
        logger.info("💡 LIGHT ON")
    
    def _transition_to_countdown(self, timestamp):
        """Chuyển sang trạng thái COUNTDOWN"""
        if self.current_state == LightState.COUNTDOWN:
            return  # Already counting down
        
        self.current_state = LightState.COUNTDOWN
        self.state_change_time = timestamp
        
        logger.info(f"⏳ COUNTDOWN START ({config.PERSON_LOST_DELAY}s)")
    
    def _transition_to_off(self, timestamp):
        """Chuyển sang trạng thái OFF"""
        if self.current_state == LightState.OFF:
            return  # Already OFF
        
        self.current_state = LightState.OFF
        self.state_change_time = timestamp
        
        # Tắt relay
        if self.relay:
            self.relay.off()
        
        logger.info("⚫ LIGHT OFF")
    
    def get_state(self):
        """Lấy trạng thái hiện tại"""
        return self.current_state.value
    
    def get_countdown_remaining(self):
        """Lấy thời gian còn lại trong countdown (giây)"""
        if self.current_state != LightState.COUNTDOWN:
            return 0
        
        elapsed = time.time() - self.state_change_time
        remaining = config.PERSON_LOST_DELAY - elapsed
        
        return max(0, remaining)
    
    def force_on(self):
        """Bắt buộc bật đèn (manual override)"""
        self._transition_to_on(time.time())
    
    def force_off(self):
        """Bắt buộc tắt đèn (manual override)"""
        self._transition_to_off(time.time())
    
    def force_countdown(self):
        """Bắt buộc bắt đầu countdown"""
        self._transition_to_countdown(time.time())
    
    def reset(self):
        """Reset về trạng thái OFF"""
        self._transition_to_off(time.time())


# ============================================
# ADVANCED STATE MACHINE (Optional)
# ============================================

class AdvancedStateMachine:
    """State machine nâng cao với thêm trạng thái"""
    
    def __init__(self, relay=None):
        """Khởi tạo advanced state machine"""
        self.relay = relay
        self.state = "OFF"
        self.state_time = time.time()
        
        # Statistics
        self.stats = {
            "lights_on_count": 0,
            "total_on_time": 0,
            "session_start_time": None,
        }
    
    def to_dict(self):
        """Convert state to dict"""
        return {
            "state": self.state,
            "state_time": self.state_time,
            "stats": self.stats
        }


# ============================================
# STANDALONE TEST
# ============================================

def test_state_machine():
    """Test state machine"""
    print("🔄 Testing State Machine...")
    
    try:
        # Create state machine without relay
        sm = StateMachine(relay=None)
        
        print("Initial state:", sm.get_state())
        assert sm.get_state() == "OFF"
        
        # Person detected → turn on
        print("\n1️⃣ Person detected...")
        sm.update(person_detected=True)
        print("State:", sm.get_state())
        assert sm.get_state() == "ON"
        
        # Person lost → start countdown
        print("\n2️⃣ Person lost...")
        sm.update(person_detected=False)
        print("State:", sm.get_state())
        assert sm.get_state() == "COUNTDOWN"
        
        # Wait for countdown
        print(f"\n3️⃣ Waiting for countdown ({config.PERSON_LOST_DELAY}s)...")
        for i in range(config.PERSON_LOST_DELAY + 1):
            sm.update(person_detected=False)
            remaining = sm.get_countdown_remaining()
            if i % 2 == 0:
                print(f"  {remaining:.1f}s remaining")
            time.sleep(1)
        
        print("State:", sm.get_state())
        assert sm.get_state() == "OFF"
        
        # Manual override
        print("\n4️⃣ Manual override...")
        sm.force_on()
        print("State:", sm.get_state())
        assert sm.get_state() == "ON"
        
        sm.force_off()
        print("State:", sm.get_state())
        assert sm.get_state() == "OFF"
        
        print("\n✅ State machine test passed")
    
    except Exception as e:
        print(f"❌ State machine test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_state_machine()
