import RPi.GPIO as GPIO
import time

RELAY_PIN = 17

# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT, initial=GPIO.LOW)

print("🔌 Testing relay...")
time.sleep(1)

# Turn ON
print("Turning relay ON (nghe CLICK?)...")
GPIO.output(RELAY_PIN, GPIO.HIGH)
time.sleep(2)

# Turn OFF
print("Turning relay OFF (nghe CLICK?)...")
GPIO.output(RELAY_PIN, GPIO.LOW)
time.sleep(1)

GPIO.cleanup()
print("✅ Test completed")