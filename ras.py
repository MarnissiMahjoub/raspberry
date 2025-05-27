from picamera2 import Picamera2
import cv2
import time
import numpy as np

# Initialisation
picam2 = Picamera2()
picam2.start()
time.sleep(2)  # Laisse la caméra démarrer

# Capture image de référence
frame_ref = picam2.capture_array()
frame_ref_gray = cv2.cvtColor(frame_ref, cv2.COLOR_BGR2GRAY)

# Seuil de détection (à ajuster selon le cas)
SEUIL_POURCENTAGE = 5.0  # % de différence autorisée

while True:
    frame = picam2.capture_array()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Calcul des différences
    diff = cv2.absdiff(frame_ref_gray, gray)
    _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

    # Calcul du pourcentage de différences
    nb_pixels_diff = cv2.countNonZero(thresh)
    total_pixels = thresh.shape[0] * thresh.shape[1]
    pourcentage_diff = (nb_pixels_diff / total_pixels) * 100

    print(f"Différence détectée : {pourcentage_diff:.2f}%")

    # Détection du départ de l'employé
    if pourcentage_diff > SEUIL_POURCENTAGE:
        print("⚠️ Employé absent du poste !")

    # Affichage ou sauvegarde (si besoin)
    cv2.imshow("Différences", thresh)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
