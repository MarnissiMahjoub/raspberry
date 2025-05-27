from picamera2 import Picamera2
import cv2
import numpy as np
import time
import os

save_dir = "./captures_poste_unique"
os.makedirs(save_dir, exist_ok=True)

picam2 = Picamera2()

# Configurer la caméra pour une résolution plus élevée si possible
config = picam2.create_still_configuration(main={"size": (3280, 2464)})
picam2.configure(config)

picam2.start()
time.sleep(2)

# Définir la zone du poste (x, y, largeur, hauteur)
poste_zone = (100, 100, 500, 800)  # à adapter selon ta caméra / poste

compteur_images = 0
nombre_verifications = 0
MAX_VERIFICATIONS = 15

def detect_bouton_rouge(roi_bgr):
    hsv = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2HSV)
    lower_red1 = np.array([0, 70, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 70, 50])
    upper_red2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)

    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    # Affichage pour debug
    cv2.imshow("Masque rouge", mask)
    cv2.waitKey(1)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in contours:
        if cv2.contourArea(c) > 100:  # seuil adapté pour bouton visible
            return True
    return False


try:
    while nombre_verifications < MAX_VERIFICATIONS:
        frame = picam2.capture_array()

        x, y, w, h = poste_zone
        zone_bgr = frame[y:y + h, x:x + w]

        bouton_rouge = detect_bouton_rouge(zone_bgr)

        if bouton_rouge:
            print("Bouton rouge détecté.")
            nom_fichier = f"{save_dir}/poste_capture_{compteur_images}.jpg"
            cv2.imwrite(nom_fichier, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
            compteur_images += 1
        else:
            print("Bouton rouge non détecté.")

        nombre_verifications += 1
        time.sleep(1)

except KeyboardInterrupt:
    print("Programme arrêté par l'utilisateur.")

finally:
    picam2.stop()
    cv2.destroyAllWindows()
    print(f"Fin du programme après {nombre_verifications} vérifications.")
