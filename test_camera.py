import cv2
import time

print("Testing camera...")

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Camera failed!")
    exit(1)

w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
fps = cap.get(cv2.CAP_PROP_FPS)

print(f"✅ Camera: {int(w)}x{int(h)} @ {fps}fps")

# Read 100 frames
start = time.time()
for i in range(100):
    ret, frame = cap.read()
    if not ret:
        print(f"Frame {i}: FAILED")
        break

elapsed = time.time() - start
actual_fps = 100 / elapsed

print(f"✅ Actual FPS: {actual_fps:.1f}")
print(f"✅ Frame shape: {frame.shape}")

cap.release()
print("✅ Test completed!")