import cv2
import numpy as np
from picamera2 import Picamera2

# Charger l'image de référence
ref_image = cv2.imread('capture.jpg')
ref_image = cv2.resize(ref_image, (640, 480))  # Adapter à la taille de capture

# Initialiser la caméra
picam2 = Picamera2()
picam2.preview_configuration.main.size = (640, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")
picam2.start()

while True:
    # Capture en temps réel
    frame = picam2.capture_array()
    frame = cv2.flip(frame, 1)

    # Convertir en niveaux de gris
    ref_gray = cv2.cvtColor(ref_image, cv2.COLOR_BGR2GRAY)
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Calcul de la différence
    diff = cv2.absdiff(ref_gray, frame_gray)
    _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

    # Morphologie (optionnel)
    kernel = np.ones((5,5), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_DILATE, kernel)

    # Combiner les affichages dans une seule image
    combined = np.hstack((frame, cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)))

    # Afficher une seule fenêtre
    cv2.imshow("Capture et différences détectées", combined)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
picam2.stop()
