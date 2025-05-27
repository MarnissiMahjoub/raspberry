from picamera2 import Picamera2
import cv2
import time

picam2 = Picamera2()

try:
    picam2.start()
    time.sleep(2)

    frame_ref = picam2.capture_array()
    frame_ref_gray = cv2.cvtColor(frame_ref, cv2.COLOR_BGR2GRAY)

    SEUIL_POURCENTAGE = 5.0

    while True:
        frame = picam2.capture_array()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        diff = cv2.absdiff(frame_ref_gray, gray)
        _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

        nb_pixels_diff = cv2.countNonZero(thresh)
        total_pixels = thresh.shape[0] * thresh.shape[1]
        pourcentage_diff = (nb_pixels_diff / total_pixels) * 100

        print(f"Différence détectée : {pourcentage_diff:.2f}%")

        if pourcentage_diff > SEUIL_POURCENTAGE:
            print("⚠️ Employé absent du poste !")

        # cv2.imshow("Différences", thresh)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    picam2.stop()
    cv2.destroyAllWindows()
