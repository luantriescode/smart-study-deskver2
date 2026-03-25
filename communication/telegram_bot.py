"""
COMMUNICATION/TELEGRAM_BOT.PY - Telegram Alert System
======================================================
Quản lý:
  - Gửi text alerts
  - Gửi ảnh
  - Cooldown logic (tránh spam)
"""

import time
import cv2
import logging
import requests
from pathlib import Path
from io import BytesIO

import config

logger = logging.getLogger(__name__)


class TelegramBot:
    """Telegram bot cho cảnh báo"""
    
    def __init__(self, token=None, chat_id=None):
        """
        Khởi tạo Telegram bot
        
        Args:
            token: Bot token (default: config.TELEGRAM_TOKEN)
            chat_id: Chat ID (default: config.TELEGRAM_CHAT_ID)
        """
        self.token = token or config.TELEGRAM_TOKEN
        self.chat_id = chat_id or config.TELEGRAM_CHAT_ID
        
        self.api_url = f"https://api.telegram.org/bot{self.token}"
        
        # Cooldown tracking
        self.last_alert_time = 0
        self.last_alert_type = None
        
        # Verify bot is working
        self._verify()
        
        logger.info(f"TelegramBot initialized (chat_id: {self.chat_id})")
    
    def _verify(self):
        """Kiểm tra bot hoạt động"""
        try:
            url = f"{self.api_url}/getMe"
            response = requests.get(url, timeout=5)
            data = response.json()
            
            if data.get("ok"):
                bot_name = data["result"].get("first_name", "Unknown")
                logger.info(f"✅ Telegram bot verified: {bot_name}")
            else:
                logger.error(f"❌ Telegram bot verification failed: {data}")
        
        except Exception as e:
            logger.error(f"❌ Telegram connection error: {e}")
    
    def _can_send_alert(self):
        """Kiểm tra có thể gửi cảnh báo không (cooldown)"""
        elapsed = time.time() - self.last_alert_time
        return elapsed >= config.TELEGRAM_ALERT_COOLDOWN
    
    def send_message(self, text):
        """
        Gửi message text
        
        Args:
            text: Message text
        
        Returns:
            bool - Success or not
        """
        try:
            url = f"{self.api_url}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, json=payload, timeout=10)
            data = response.json()
            
            if data.get("ok"):
                logger.info(f"✅ Message sent to Telegram")
                return True
            else:
                logger.error(f"❌ Failed to send message: {data}")
                return False
        
        except Exception as e:
            logger.error(f"❌ Telegram send error: {e}")
            return False
    
    def send_photo(self, frame, caption=""):
        """
        Gửi ảnh
        
        Args:
            frame: numpy array (BGR)
            caption: Image caption
        
        Returns:
            bool - Success or not
        """
        try:
            # Encode frame as JPEG
            success, buffer = cv2.imencode('.jpg', frame)
            if not success:
                logger.error("Failed to encode frame")
                return False
            
            # Prepare payload
            url = f"{self.api_url}/sendPhoto"
            files = {"photo": ("image.jpg", BytesIO(buffer))}
            data = {
                "chat_id": self.chat_id,
                "caption": caption,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, files=files, data=data, timeout=10)
            result = response.json()
            
            if result.get("ok"):
                logger.info(f"✅ Photo sent to Telegram")
                return True
            else:
                logger.error(f"❌ Failed to send photo: {result}")
                return False
        
        except Exception as e:
            logger.error(f"❌ Telegram photo error: {e}")
            return False
    
    def alert_sleep(self, frame):
        """
        Gửi cảnh báo ngủ gật
        
        Args:
            frame: Frame khi phát hiện ngủ
        """
        if not self._can_send_alert():
            logger.debug("Sleep alert on cooldown")
            return
        
        self.last_alert_time = time.time()
        
        text = "😴 <b>SLEEP DETECTED!</b>\nStudent is sleeping. Please take action!"
        
        if config.SEND_PHOTO_ON_ALERT:
            self.send_photo(frame, caption=text)
        else:
            self.send_message(text)
    
    def alert_posture(self, frame, angle):
        """
        Gửi cảnh báo tư thế
        
        Args:
            frame: Frame khi phát hiện tư thế xấu
            angle: Head angle (độ)
        """
        if not self._can_send_alert():
            logger.debug("Posture alert on cooldown")
            return
        
        self.last_alert_time = time.time()
        
        text = f"⚠️  <b>BAD POSTURE!</b>\nHead angle: {angle:.1f}°\nPlease correct your posture!"
        
        if config.SEND_PHOTO_ON_ALERT:
            self.send_photo(frame, caption=text)
        else:
            self.send_message(text)
    
    def alert_session_start(self):
        """Cảnh báo khi bắt đầu phiên học"""
        if not self._can_send_alert():
            return
        
        self.last_alert_time = time.time()
        text = "📚 <b>Study session started</b>"
        self.send_message(text)
    
    def alert_session_end(self, duration):
        """
        Cảnh báo khi kết thúc phiên học
        
        Args:
            duration: Duration in seconds
        """
        if not self._can_send_alert():
            return
        
        self.last_alert_time = time.time()
        
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        
        text = f"📚 <b>Study session ended</b>\nDuration: {hours}h {minutes}m"
        self.send_message(text)
    
    def alert_stats(self, stats):
        """
        Gửi thống kê
        
        Args:
            stats: Dictionary with statistics
        """
        text = "<b>📊 Study Statistics</b>\n"
        text += f"Total time: {stats['total_study_time']}s\n"
        text += f"Sessions: {stats['total_sessions']}\n"
        text += f"Sleep events: {stats['sleep_count']}\n"
        text += f"Posture events: {stats['posture_count']}"
        
        self.send_message(text)
    
    def set_cooldown(self, cooldown_seconds):
        """Đặt cooldown"""
        config.TELEGRAM_ALERT_COOLDOWN = cooldown_seconds
        logger.info(f"Cooldown set to {cooldown_seconds}s")


# ============================================
# ADVANCED: COMMAND HANDLER
# ============================================

class TelegramCommandHandler:
    """Handle commands from Telegram"""
    
    def __init__(self, bot, relay=None, state_machine=None):
        """
        Khởi tạo command handler
        
        Args:
            bot: TelegramBot instance
            relay: RelayController instance
            state_machine: StateMachine instance
        """
        self.bot = bot
        self.relay = relay
        self.state_machine = state_machine
    
    def handle_command(self, command):
        """
        Xử lý lệnh từ Telegram
        
        Args:
            command: Command string (/on, /off, /status, etc.)
        """
        if command == "/on":
            if self.relay:
                self.relay.on()
            if self.state_machine:
                self.state_machine.force_on()
            self.bot.send_message("💡 Light turned ON")
        
        elif command == "/off":
            if self.relay:
                self.relay.off()
            if self.state_machine:
                self.state_machine.force_off()
            self.bot.send_message("⚫ Light turned OFF")
        
        elif command == "/status":
            status = self._get_status()
            self.bot.send_message(status)
        
        else:
            self.bot.send_message(f"Unknown command: {command}")
    
    def _get_status(self):
        """Lấy trạng thái hệ thống"""
        text = "<b>System Status</b>\n"
        
        if self.relay:
            state = "ON 💡" if self.relay.is_on else "OFF ⚫"
            text += f"Light: {state}\n"
        
        if self.state_machine:
            text += f"State: {self.state_machine.current_state.value}\n"
        
        return text


# ============================================
# STANDALONE TEST
# ============================================

def test_telegram():
    """Test Telegram bot"""
    print("📱 Testing Telegram Bot...")
    
    try:
        bot = TelegramBot()
        
        print("1️⃣ Send message...")
        success = bot.send_message("✅ Test message from Smart Study Desk")
        print(f"  Result: {'✅' if success else '❌'}")
        
        print("✅ Telegram bot test completed")
    
    except Exception as e:
        print(f"❌ Telegram bot test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_telegram()
