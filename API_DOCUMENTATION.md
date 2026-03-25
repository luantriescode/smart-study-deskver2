# 📡 REST API DOCUMENTATION

Smart Study Desk Web API Reference

---

## 🌐 Base URL

```
http://192.168.1.100:5000/api
```

Replace `192.168.1.100` with your Raspberry Pi's IP address.

---

## 📊 Endpoints

### 1. GET `/status` - System Status

**Description:** Get current system status

**Request:**
```bash
GET /api/status
```

**Response:**
```json
{
    "timestamp": "2024-03-19T14:55:30.123456",
    "relay": {
        "state": "ON",
        "pin": 17
    },
    "state_machine": {
        "state": "ON",
        "countdown": 0.0
    },
    "camera": {
        "status": "OK"
    }
}
```

**Status Codes:**
- `200 OK` - Success
- `500 Internal Server Error` - System error

**Examples:**

```bash
# Using curl
curl http://192.168.1.100:5000/api/status

# Using JavaScript
fetch('/api/status')
    .then(r => r.json())
    .then(data => console.log(data))
```

**Notes:**
- Updates every 2 seconds
- Relay state: "ON" or "OFF"
- State machine: "OFF", "ON", or "COUNTDOWN"
- Countdown: seconds remaining

---

### 2. GET `/stats` - Study Statistics

**Description:** Get study session statistics

**Request:**
```bash
GET /api/stats
```

**Response:**
```json
{
    "total_study_time": 3600,
    "total_sessions": 5,
    "sleep_count": 2,
    "posture_count": 3,
    "max_session": 900,
    "current_session": 120
}
```

**Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `total_study_time` | int | Total study time in seconds |
| `total_sessions` | int | Number of sessions completed |
| `sleep_count` | int | Number of sleep detections |
| `posture_count` | int | Number of bad posture detections |
| `max_session` | int | Longest session in seconds |
| `current_session` | int | Current session time in seconds |

**Examples:**

```bash
# Get stats
curl http://192.168.1.100:5000/api/stats

# JavaScript
fetch('/api/stats')
    .then(r => r.json())
    .then(stats => {
        const hours = Math.floor(stats.total_study_time / 3600);
        console.log(`Total study: ${hours}h`);
    })
```

---

### 3. POST `/light/<action>` - Light Control

**Description:** Control light on/off/toggle

**Request:**
```bash
POST /api/light/on
POST /api/light/off
POST /api/light/toggle
```

**Parameters:**
| Action | Effect |
|--------|--------|
| `on` | Turn light ON immediately |
| `off` | Turn light OFF immediately |
| `toggle` | Toggle light state |

**Response (Success):**
```json
{
    "status": "success",
    "message": "Light turned ON"
}
```

**Response (Error):**
```json
{
    "error": "Relay not initialized"
}
```

**Status Codes:**
- `200 OK` - Success
- `400 Bad Request` - Invalid action
- `500 Internal Server Error` - Relay error

**Examples:**

```bash
# Turn light ON
curl -X POST http://192.168.1.100:5000/api/light/on

# Turn light OFF
curl -X POST http://192.168.1.100:5000/api/light/off

# JavaScript
async function turnLightOn() {
    const response = await fetch('/api/light/on', {
        method: 'POST'
    });
    const data = await response.json();
    console.log(data.message);
}
```

**Rate Limiting:**
- No rate limit
- Rapid toggles allowed (but hardware limited)

---

### 4. GET `/events` - Recent Events

**Description:** Get list of recent events

**Request:**
```bash
GET /api/events
GET /api/events?limit=20
GET /api/events?type=SLEEP_DETECTED
GET /api/events?type=BAD_POSTURE&limit=10
```

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | int | 10 | Max number of events |
| `type` | str | null | Filter by event type |

**Event Types:**
- `SESSION_START` - Study session started
- `SESSION_END` - Study session ended
- `SLEEP_DETECTED` - Sleep detection triggered
- `BAD_POSTURE` - Bad posture detected

**Response:**
```json
{
    "events": [
        {
            "timestamp": 1710869730.123,
            "datetime": "2024-03-19T14:55:30.123456",
            "type": "SLEEP_DETECTED",
            "data": {}
        },
        {
            "timestamp": 1710869720.456,
            "datetime": "2024-03-19T14:55:20.456789",
            "type": "SESSION_START",
            "data": {}
        }
    ]
}
```

**Examples:**

```bash
# Get last 10 events
curl http://192.168.1.100:5000/api/events

# Get last 20 sleep events
curl http://192.168.1.100:5000/api/events?limit=20&type=SLEEP_DETECTED

# JavaScript
fetch('/api/events?limit=50')
    .then(r => r.json())
    .then(data => {
        data.events.forEach(event => {
            console.log(`${event.type} at ${event.datetime}`);
        });
    })
```

---

### 5. GET `/screenshot` - Latest Frame

**Description:** Get latest camera frame as JPEG

**Request:**
```bash
GET /api/screenshot
```

**Response:**
- Content-Type: `image/jpeg`
- Binary JPEG image data

**Status Codes:**
- `200 OK` - Frame available
- `404 Not Found` - No frame yet

**Examples:**

```bash
# Save screenshot
curl http://192.168.1.100:5000/api/screenshot > screenshot.jpg

# JavaScript
fetch('/api/screenshot')
    .then(r => r.blob())
    .then(blob => {
        const url = URL.createObjectURL(blob);
        document.getElementById('img').src = url;
    })
```

**Notes:**
- Updates every frame
- Latest frame only (not buffered)
- JPEG quality: 80%

---

### 6. GET `/config` - System Configuration

**Description:** Get current system configuration

**Request:**
```bash
GET /api/config
```

**Response:**
```json
{
    "camera": {
        "width": 320,
        "height": 240,
        "roi": {
            "x": 50,
            "y": 50,
            "w": 220,
            "h": 140
        }
    },
    "thresholds": {
        "motion": 500,
        "eye_closed_frames": 150,
        "head_down": 20
    },
    "timers": {
        "person_lost_delay": 10,
        "session_timeout": 3600
    }
}
```

**Examples:**

```bash
# Get config
curl http://192.168.1.100:5000/api/config

# JavaScript
fetch('/api/config')
    .then(r => r.json())
    .then(config => {
        console.log(`ROI: ${config.camera.roi}`);
        console.log(`Motion threshold: ${config.thresholds.motion}`);
    })
```

**Notes:**
- Read-only (changes require manual config file edit)
- Useful for UI configuration

---

## 🎬 Streaming Endpoints

### GET `/video_feed` - Camera Stream

**Description:** MJPEG video stream

**Request:**
```bash
GET /video_feed
```

**Response:**
- Content-Type: `multipart/x-mixed-replace; boundary=frame`
- MJPEG stream of frames

**Usage:**
```html
<!-- HTML img tag -->
<img src="http://192.168.1.100:5000/video_feed" width="320" height="240">
```

```javascript
// JavaScript fetch (won't work for streaming, use img tag instead)
// Note: Better to use <img> tag for streaming
```

**Notes:**
- Real-time camera feed
- ~2-5fps due to compression
- JPEG quality: 80%
- Can be viewed in any browser

---

## 🔐 Security

### API Keys
Currently no authentication required (LAN only).

**Recommended for future:**
```python
# Add to requests
headers = {
    'Authorization': 'Bearer YOUR_API_KEY'
}
```

### Rate Limiting
Not implemented yet. Implement if:
- Exposed to internet
- Multiple concurrent clients
- DoS protection needed

---

## 📋 Response Format

All responses (except streaming/images) are JSON:

```json
{
    "status": "success",
    "data": { ... },
    "error": null,
    "timestamp": "2024-03-19T14:55:30"
}
```

**Error Response:**
```json
{
    "status": "error",
    "error": "Error message here",
    "timestamp": "2024-03-19T14:55:30"
}
```

---

## 🧪 Testing with curl

### Test all endpoints
```bash
#!/bin/bash

IP="192.168.1.100"
BASE="http://$IP:5000/api"

echo "Testing Smart Study Desk API..."

echo -e "\n1. Status:"
curl -s "$BASE/status" | jq .

echo -e "\n2. Stats:"
curl -s "$BASE/stats" | jq .

echo -e "\n3. Events:"
curl -s "$BASE/events?limit=5" | jq .

echo -e "\n4. Config:"
curl -s "$BASE/config" | jq .

echo -e "\n5. Light ON:"
curl -s -X POST "$BASE/light/on" | jq .

echo -e "\n6. Status (should be ON):"
curl -s "$BASE/status" | jq .

echo -e "\n7. Light OFF:"
curl -s -X POST "$BASE/light/off" | jq .

echo -e "\nAPI Test Complete!"
```

Run:
```bash
bash test_api.sh
```

---

## 🔄 Polling Recommendations

For dashboard updates, use these intervals:

| Resource | Interval | Reason |
|----------|----------|--------|
| Status | 2s | Light state, countdown |
| Stats | 5s | Study time updates |
| Events | 10s | Event log heavy |
| Screenshot | 5s | Real-time feed |
| Config | 60s | Rarely changes |

**Example:**
```javascript
// Update dashboard
setInterval(() => {
    fetch('/api/status').then(r => r.json())
        .then(data => updateStatus(data));
}, 2000);

setInterval(() => {
    fetch('/api/stats').then(r => r.json())
        .then(data => updateStats(data));
}, 5000);

setInterval(() => {
    fetch('/api/events').then(r => r.json())
        .then(data => updateEvents(data));
}, 10000);
```

---

## 💡 Integration Examples

### Python Client
```python
import requests

BASE_URL = "http://192.168.1.100:5000/api"

# Get status
response = requests.get(f"{BASE_URL}/status")
status = response.json()
print(f"Light: {status['relay']['state']}")

# Turn light on
requests.post(f"{BASE_URL}/light/on")

# Get stats
stats = requests.get(f"{BASE_URL}/stats").json()
print(f"Study time: {stats['total_study_time']}s")
```

### JavaScript Fetch
```javascript
const BASE_URL = "http://192.168.1.100:5000/api";

// Get status
const status = await fetch(`${BASE_URL}/status`).then(r => r.json());
console.log(`Light: ${status.relay.state}`);

// Control light
await fetch(`${BASE_URL}/light/on`, { method: 'POST' });

// Get stats
const stats = await fetch(`${BASE_URL}/stats`).then(r => r.json());
console.log(`Sessions: ${stats.total_sessions}`);
```

### Postman Collection
```json
{
    "info": {
        "name": "Smart Study Desk API",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    },
    "item": [
        {
            "name": "GET Status",
            "request": {
                "method": "GET",
                "url": {
                    "raw": "http://192.168.1.100:5000/api/status",
                    "protocol": "http",
                    "host": ["192", "168", "1", "100"],
                    "port": "5000",
                    "path": ["api", "status"]
                }
            }
        }
    ]
}
```

---

## 🐛 Debugging

### Enable API logging
```python
# In app.py
app.logger.setLevel(logging.DEBUG)

# Check logs
tail -f logs/study_system.log | grep API
```

### Test endpoint
```bash
# Verbose curl output
curl -v http://192.168.1.100:5000/api/status

# With timing
curl -w "@curl-format.txt" http://192.168.1.100:5000/api/status
```

### Common Issues

**"Connection refused"**
```bash
# Check if server running
ps aux | grep python3

# Check port
sudo lsof -i :5000
```

**"No route to host"**
```bash
# Check IP
hostname -I

# Check network
ping 192.168.1.100
```

**"Timeout"**
```bash
# Server might be busy/crashed
# Restart: sudo systemctl restart smart-study-desk

# Check logs
sudo journalctl -u smart-study-desk -f
```

---

## 📈 API Monitoring

### Health Check
```bash
# Simple health check
curl -f http://192.168.1.100:5000/api/status > /dev/null && echo "OK" || echo "FAIL"

# In cron
*/5 * * * * curl -f http://192.168.1.100:5000/api/status > /dev/null || mail -s "API Down" admin@example.com
```

### Metrics
```bash
# Response time
curl -w "Time: %{time_total}s\n" http://192.168.1.100:5000/api/status

# Throughput (100 requests)
for i in {1..100}; do curl -s http://192.168.1.100:5000/api/status > /dev/null; done
```

---

## 🚀 Future API Features

- [ ] Webhook support for events
- [ ] WebSocket for real-time updates
- [ ] Advanced filtering and sorting
- [ ] Data export (CSV/JSON)
- [ ] Historical data queries
- [ ] Analytics endpoints
- [ ] Multi-user support
- [ ] API authentication
- [ ] Rate limiting

---

## 📚 References

- [REST API Best Practices](https://restfulapi.net/)
- [HTTP Status Codes](https://httpwg.org/specs/rfc9110.html)
- [JSON Schema](https://json-schema.org/)
- [OpenAPI 3.0](https://spec.openapis.org/)

---

**API Version:** 1.0
**Last Updated:** March 2024
**Status:** Stable
