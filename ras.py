from picamera2 import Picamera2
import cv2
import numpy as np
import time
import os
from datetime import datetime

# Dossier où sauvegarder les captures
save_dir = "./captures_poste"
os.makedirs(save_dir, exist_ok=True)

# Configurer la caméra
picam2 = Picamera2()
config = picam2.create_still_configuration(main={"size": (1280, 720)})  # Ajuste la taille pour un flux fluide
picam2.configure(config)
picam2.start()
time.sleep(2)  # Laisser la caméra chauffer

# Image de référence pour la détection de mouvement
frame_ref = picam2.capture_array()
gray_ref = cv2.cvtColor(frame_ref, cv2.COLOR_BGR2GRAY)

# Définition d'une seule zone (à adapter selon ta caméra)
x, y, w, h = 100, 100, 400, 300

print("Appuyez sur 'q' pour quitter le programme.")

try:
    while True:
        frame = picam2.capture_array()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Détection de mouvement
        diff = cv2.absdiff(gray_ref, gray)
        _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
        thresh = cv2.GaussianBlur(thresh, (5, 5), 0)

        zone_thresh = thresh[y:y + h, x:x + w]
        zone_bgr = frame[y:y + h, x:x + w]

        # Détection bouton rouge
        hsv = cv2.cvtColor(zone_bgr, cv2.COLOR_BGR2HSV)
        lower_red1 = np.array([0, 120, 70])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 120, 70])
        upper_red2 = np.array([180, 255, 255])
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = cv2.bitwise_or(mask1, mask2)
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        bouton_rouge_detecte = any(cv2.contourArea(c) > 500 for c in contours)

        # Détection de mouvement
        contours, _ = cv2.findContours(zone_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        aire_totale = sum(cv2.contourArea(c) for c in contours)
        seuil_occupation = 1000
        mouvement_detecte = aire_totale > seuil_occupation

        # Dessiner le cadre (vert + rouge)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)  # cadre vert = poste
        cv2.rectangle(frame, (x + 50, y + 50), (x + w - 50, y + h - 50), (0, 0, 255), 2)  # cadre rouge = bouton

        # Ajouter du texte d'état
        if bouton_rouge_detecte:
            cv2.putText(frame, "Bouton Rouge Detecte", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        elif mouvement_detecte:
            cv2.putText(frame, "Mouvement Detecte", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        else:
            cv2.putText(frame, "Poste OK", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Sauvegarde si détection
        if bouton_rouge_detecte or mouvement_detecte:
            now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            nom_fichier = f"{save_dir}/poste_capture_{now}.jpg"
            cv2.imwrite(nom_fichier, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 95])

        # Affichage en temps réel
        cv2.imshow("Flux Camera Temps Reel", frame)

        # Quitter si touche 'q' pressée
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Arrêt demandé par l'utilisateur.")
            break

        time.sleep(0.05)

except KeyboardInterrupt:
    print("Arrêt forcé (CTRL+C) détecté.")

finally:
    picam2.stop()
    cv2.destroyAllWindows()
    print("Programme terminé proprement.")
