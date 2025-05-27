from picamera2 import Picamera2
import cv2
import time

picam2 = Picamera2()
picam2.start()
time.sleep(2)  # Laisse le temps à la caméra de démarrer

frame_ref = picam2.capture_array()
frame_ref_gray = cv2.cvtColor(frame_ref, cv2.COLOR_BGR2GRAY)

while True:
    frame = picam2.capture_array()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    diff = cv2.absdiff(frame_ref_gray, gray)
    _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

    cv2.imshow('Diff', thresh)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
