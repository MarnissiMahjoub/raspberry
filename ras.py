import cv2
import numpy as np
from picamera2 import Picamera2

# Initialisation caméra
picam2 = Picamera2()
picam2.preview_configuration.main.size = (3280, 2464)  # Résolution max pour IMX219
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")
picam2.start()

while True:
    frame = picam2.capture_array()
    frame = cv2.flip(frame, 1)  # Miroir

    # Convertir en HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Masque couleur peau (ajuste si besoin)
    lower_skin = np.array([0, 30, 60], dtype=np.uint8)
    upper_skin = np.array([20, 150, 255], dtype=np.uint8)
    mask = cv2.inRange(hsv, lower_skin, upper_skin)

    # Amélioration du masque
    mask = cv2.GaussianBlur(mask, (5, 5), 100)

    # Trouver les contours
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        # Plus grand contour = main
        cnt = max(contours, key=lambda x: cv2.contourArea(x))
        epsilon = 0.0005 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)

        # Trouver les points extrêmes (convex hull)
        hull = cv2.convexHull(cnt)
        cv2.drawContours(frame, [hull], -1, (0, 255, 0), 2)

        # Compter les défauts de convexité (doigts)
        hull_indices = cv2.convexHull(cnt, returnPoints=False)
        defects = cv2.convexityDefects(cnt, hull_indices)

        fingers = 0
        if defects is not None:
            for i in range(defects.shape[0]):
                s, e, f, d = defects[i, 0]
                start = tuple(cnt[s][0])
                end = tuple(cnt[e][0])
                far = tuple(cnt[f][0])

                # Angle (simple estimation)
                a = np.linalg.norm(np.array(end) - np.array(start))
                b = np.linalg.norm(np.array(far) - np.array(start))
                c = np.linalg.norm(np.array(end) - np.array(far))
                angle = np.arccos((b**2 + c**2 - a**2)/(2*b*c))

                if angle <= np.pi / 2:  # angle < 90 degrés, c'est probablement un doigt
                    fingers += 1
                    cv2.circle(frame, far, 8, [211, 84, 0], -1)

        cv2.putText(frame, f"Doigts leves: {fingers+1}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow('Frame', frame)
    cv2.imshow('Mask', mask)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
picam2.stop()
