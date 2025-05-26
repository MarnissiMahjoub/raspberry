import cv2
import numpy as np
from picamera2 import Picamera2
import time

# Configuration
target_size = (1280, 720)  # Taille de l'image (augmente si besoin)
seuil_diff = 2  # Seuil en % pour détecter un changement
intervalle_capture = 5  # Temps entre chaque capture (en secondes)

# Initialiser la caméra
picam2 = Picamera2()
picam2.preview_configuration.main.size = target_size
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")
picam2.start()

# Attendre un peu que la caméra se stabilise
time.sleep(2)

# Prendre la première image de référence
ancienne_image = picam2.capture_array()
ancienne_image_gray = cv2.cvtColor(ancienne_image, cv2.COLOR_BGR2GRAY)

print("🚀 Surveillance en cours...")

try:
    while True:
        # Attendre 5 secondes
        time.sleep(intervalle_capture)

        # Capturer une nouvelle image
        nouvelle_image = picam2.capture_array()
        nouvelle_image_gray = cv2.cvtColor(nouvelle_image, cv2.COLOR_BGR2GRAY)

        # Comparer avec l'image précédente
        diff = cv2.absdiff(ancienne_image_gray, nouvelle_image_gray)
        _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
        diff_percent = (np.sum(thresh > 0) / thresh.size) * 100
        print(f"Différence : {diff_percent:.2f}%")

        # Si changement détecté
        if diff_percent > seuil_diff:
            print("⚠️ Changement détecté !")
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            cv2.imwrite(f"changement_detecte_{timestamp}.jpg", nouvelle_image)
            cv2.imshow("Changement détecté", nouvelle_image)
            cv2.waitKey(1)  # Petite pause pour afficher

        # Mettre à jour l'image précédente
        ancienne_image_gray = nouvelle_image_gray

except KeyboardInterrupt:
    print("\nArrêt du script.")
    picam2.stop()
    cv2.destroyAllWindows()
