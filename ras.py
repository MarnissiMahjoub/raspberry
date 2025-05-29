from picamera2 import Picamera2
import cv2
import numpy as np
import time
import os
from datetime import datetime

# Dossier pour sauvegarder les captures
save_dir = "./captures_poste"
os.makedirs(save_dir, exist_ok=True)

# Configurer la caméra
picam2 = Picamera2()
config = picam2.create_still_configuration(main={"size": (1280, 720)})
picam2.configure(config)
picam2.start()
time.sleep(2)  # Laisser le temps à la caméra de se stabiliser

# Définition d'une seule zone (à adapter selon ta caméra)
x, y, w, h = 100, 100, 400, 300  # Zone du poste

print("Appuyez sur 'q' pour quitter le programme.")

try:
    while True:
        frame = picam2.capture_array()
        frame_blur = cv2.GaussianBlur(frame, (5,5), 0)

        # Détection de la zone verte (le poste)
        zone = frame_blur[y:y+h, x:x+w]
        gray_zone = cv2.cvtColor(zone, cv2.COLOR_BGR2GRAY)
        _, mask_occup = cv2.threshold(gray_zone, 30, 255, cv2.THRESH_BINARY)  # Seuil pour considérer un pixel comme "occupé"

        nb_pixels_total = mask_occup.size
        nb_pixels_occupe = cv2.countNonZero(mask_occup)

        ratio_occupe = nb_pixels_occupe / nb_pixels_total
        seuil_presence = 0.05  # 5% au minimum pour dire que la zone est occupée

        poste_ok = ratio_occupe > seuil_presence

        # Détection bouton rouge
        hsv = cv2.cvtColor(zone, cv2.COLOR_BGR2HSV)
        lower_red1 = np.array([0, 120, 70])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 120, 70])
        upper_red2 = np.array([180, 255, 255])
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask_red = cv2.bitwise_or(mask1, mask2)
        kernel = np.ones((5, 5), np.uint8)
        mask_red = cv2.morphologyEx(mask_red, cv2.MORPH_OPEN, kernel)
        bouton_rouge_detecte = cv2.countNonZero(mask_red) > 500

        # Dessiner les cadres
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)  # cadre vert
        cv2.rectangle(frame, (x + 50, y + 50), (x + w - 50, y + h - 50), (0, 0, 255), 2)  # cadre rouge

        # Affichage du statut
        if bouton_rouge_detecte:
            cv2.putText(frame, "Bouton Rouge Detecte", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        elif poste_ok:
            cv2.putText(frame, "Poste OK - Employe Present", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "Attention: Poste Vide", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        # Sauvegarde si besoin
        if bouton_rouge_detecte or not poste_ok:
            now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            nom_fichier = f"{save_dir}/poste_capture_{now}.jpg"
            cv2.imwrite(nom_fichier, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 95])

        # Affichage du flux en temps réel
        cv2.imshow("Flux Camera Temps Reel", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Arret demande par l'utilisateur.")
            break

        time.sleep(0.05)

except KeyboardInterrupt:
    print("Arret force (CTRL+C) detecte.")

finally:
    picam2.stop()
    cv2.destroyAllWindows()
    print("Programme termine proprement.")
