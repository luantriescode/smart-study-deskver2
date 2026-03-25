"""
CORE/STUDY_TIMER.PY - Study Session Tracking
===============================================
Quản lý:
  - Đếm thời gian học
  - Ghi log sự kiện
  - Thống kê (sleep, posture, etc.)
"""

import time
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta

import config

logger = logging.getLogger(__name__)


class StudyTimer:
    """Quản lý phiên học"""
    
    def __init__(self):
        """Khởi tạo study timer"""
        self.session_start = None
        self.session_active = False
        self.session_duration = 0
        
        # Events
        self.events = []  # List of {timestamp, type, data}
        
        # Statistics
        self.stats = {
            "total_study_time": 0,  # seconds
            "total_sessions": 0,
            "sleep_count": 0,
            "posture_count": 0,
            "max_session": 0,
        }
        
        # Load previous stats
        self._load_stats()
        
        logger.info("StudyTimer initialized")
    
    def update(self, person_detected):
        """
        Cập nhật timer
        
        Args:
            person_detected: bool
        """
        if person_detected and not self.session_active:
            # Start new session
            self.session_start = time.time()
            self.session_active = True
            
            self.log_event("SESSION_START", {})
            logger.info("📚 Study session started")
        
        elif not person_detected and self.session_active:
            # End session
            duration = time.time() - self.session_start
            self.session_duration = duration
            self.session_active = False
            
            self.stats["total_study_time"] += duration
            self.stats["total_sessions"] += 1
            self.stats["max_session"] = max(self.stats["max_session"], duration)
            
            self.log_event("SESSION_END", {"duration": duration})
            logger.info(f"📚 Study session ended ({duration:.1f}s)")
        
        # Update current session duration
        if self.session_active:
            self.session_duration = time.time() - self.session_start
    
    def get_session_time(self):
        """Lấy thời gian phiên học hiện tại (giây)"""
        if not self.session_active:
            return 0
        return time.time() - self.session_start
    
    def log_event(self, event_type, data=None):
        """
        Ghi sự kiện
        
        Args:
            event_type: str - Loại sự kiện (SESSION_START, SLEEP_DETECTED, etc.)
            data: dict - Dữ liệu bổ sung
        """
        timestamp = time.time()
        event = {
            "timestamp": timestamp,
            "datetime": datetime.now().isoformat(),
            "type": event_type,
            "data": data or {}
        }
        
        self.events.append(event)
        
        # Update statistics
        if event_type == "SLEEP_DETECTED":
            self.stats["sleep_count"] += 1
            logger.warning(f"😴 Sleep event logged (total: {self.stats['sleep_count']})")
        
        elif event_type == "BAD_POSTURE":
            self.stats["posture_count"] += 1
            logger.warning(f"⚠️  Posture event logged (total: {self.stats['posture_count']})")
    
    def get_stats(self):
        """Lấy thống kê"""
        stats_copy = self.stats.copy()
        stats_copy["current_session"] = self.get_session_time()
        return stats_copy
    
    def get_events(self, event_type=None, limit=None):
        """
        Lấy danh sách sự kiện
        
        Args:
            event_type: Filter by type (None = all)
            limit: Giới hạn số event (None = all)
        
        Returns:
            List of events
        """
        events = self.events
        
        if event_type:
            events = [e for e in events if e["type"] == event_type]
        
        if limit:
            events = events[-limit:]
        
        return events
    
    def save_log(self):
        """Lưu log vào file"""
        try:
            log_data = {
                "timestamp": datetime.now().isoformat(),
                "stats": self.stats,
                "events": self.events
            }
            
            log_file = config.LOG_DIR / f"study_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(log_file, 'w') as f:
                json.dump(log_data, f, indent=2)
            
            logger.info(f"📊 Study log saved to {log_file}")
        
        except Exception as e:
            logger.error(f"Failed to save log: {e}")
    
    def _load_stats(self):
        """Load thống kê từ file cũ (optional)"""
        # TODO: Implement if needed
        pass
    
    def reset(self):
        """Reset timer"""
        self.session_start = None
        self.session_active = False
        self.session_duration = 0
        self.events = []
        logger.info("StudyTimer reset")
    
    def format_stats(self):
        """Format thống kê thành string"""
        stats = self.get_stats()
        
        total_time = timedelta(seconds=int(stats["total_study_time"]))
        max_session = timedelta(seconds=int(stats["max_session"]))
        current = timedelta(seconds=int(stats["current_session"]))
        
        return f"""
📊 STUDY STATISTICS:
  Total Study Time: {total_time}
  Total Sessions: {stats['total_sessions']}
  Max Session: {max_session}
  Current Session: {current}
  Sleep Events: {stats['sleep_count']}
  Posture Events: {stats['posture_count']}
        """


# ============================================
# STANDALONE TEST
# ============================================

def test_study_timer():
    """Test study timer"""
    print("⏱️  Testing Study Timer...")
    
    try:
        timer = StudyTimer()
        
        # Start session
        print("\n1️⃣ Person detected...")
        timer.update(person_detected=True)
        assert timer.session_active
        
        # Simulate activity
        print("2️⃣ Simulating study (5s)...")
        for i in range(5):
            timer.update(person_detected=True)
            time.sleep(1)
        
        # Log event
        timer.log_event("SLEEP_DETECTED", {"face_id": 0})
        timer.log_event("BAD_POSTURE", {"angle": 25.5})
        
        # End session
        print("3️⃣ Person lost...")
        timer.update(person_detected=False)
        assert not timer.session_active
        
        # Get stats
        stats = timer.get_stats()
        print("\n" + timer.format_stats())
        
        # Check results
        assert stats["total_sessions"] >= 1
        assert stats["sleep_count"] >= 1
        assert stats["posture_count"] >= 1
        
        print("✅ Study timer test passed")
    
    except Exception as e:
        print(f"❌ Study timer test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_study_timer()
