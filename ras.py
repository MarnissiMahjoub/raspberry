import cv2
import numpy as np
from picamera2 import Picamera2

# Charger l'image de référence enregistrée (capture.jpg)
ref_image = cv2.imread('capture.jpg')
ref_image = cv2.resize(ref_image, (640, 480))  # Adapter à la taille de capture

# Initialiser la caméra
picam2 = Picamera2()
picam2.preview_configuration.main.size = (640, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")
picam2.start()

while True:
    # Capturer une image en temps réel
    frame = picam2.capture_array()
    frame = cv2.flip(frame, 1)

    # Convertir les deux images en niveaux de gris
    ref_gray = cv2.cvtColor(ref_image, cv2.COLOR_BGR2GRAY)
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Calculer la différence absolue
    diff = cv2.absdiff(ref_gray, frame_gray)

    # Seuillage pour rendre la différence visible
    _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

    # (optionnel) Morphologie pour réduire le bruit
    kernel = np.ones((5,5), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_DILATE, kernel)

    # Afficher les résultats
    cv2.imshow("Capture en temps réel", frame)
    cv2.imshow("Différence (grayscale)", diff)
    cv2.imshow("Différences détectées", thresh)

    # Quitter en appuyant sur 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Fermer proprement
cv2.destroyAllWindows()
picam2.stop()
