from picamera2 import Picamera2
import cv2
import numpy as np
import time
import os
from datetime import datetime

# Création dossier
save_dir = "./captures_poste"
os.makedirs(save_dir, exist_ok=True)

picam2 = Picamera2()
config = picam2.create_still_configuration(main={"size": (3280, 2464)})
picam2.configure(config)
picam2.start()
time.sleep(2)

# Capture référence
frame_ref = picam2.capture_array()
gray_ref = cv2.cvtColor(frame_ref, cv2.COLOR_BGR2GRAY)

# Définir la zone du poste (par exemple un carré)
zone_poste = (500, 0, 500, 800)  # (x, y, w, h)
(x, y, w, h) = zone_poste

# Boucle infinie (interrompue par 'q')
while True:
    frame = picam2.capture_array()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

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

    # Détection mouvement
    contours, _ = cv2.findContours(zone_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    aire_totale = sum(cv2.contourArea(c) for c in contours)
    seuil_occupation = 1000
    mouvement_detecte = aire_totale > seuil_occupation

    # Affichage des cadres
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)  # cadre vert
    cv2.rectangle(frame, (x + 50, y + 50), (x + w - 50, y + h - 50), (0, 0, 255), 2)  # cadre rouge à l'intérieur

    if bouton_rouge_detecte or mouvement_detecte:
        print("Poste occupé ou bouton rouge détecté. Sauvegarde...")
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        nom_fichier = f"{save_dir}/poste_capture_{now}.jpg"
        cv2.imwrite(nom_fichier, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 95])

    # Redimensionner pour affichage
    frame_resized = cv2.resize(frame, (1280, 720))
    cv2.imshow("Poste en temps réel", frame_resized)

    # Quitter avec 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    time.sleep(0.1)  # Pause courte pour un flux plus fluide

picam2.stop()
cv2.destroyAllWindows()
