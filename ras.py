from picamera2 import Picamera2
import cv2
import numpy as np
import time
import os

save_dir = "./captures_poste_et_bouton"
os.makedirs(save_dir, exist_ok=True)

picam2 = Picamera2()

# Configuration haute résolution
config = picam2.create_still_configuration(main={"size": (3280, 2464)})
picam2.configure(config)

picam2.start()
time.sleep(2)

# Capture de référence (poste vide)
frame_ref = picam2.capture_array()
gray_ref = cv2.cvtColor(frame_ref, cv2.COLOR_BGR2GRAY)

# Zone du poste (à ajuster)
poste_zone = (100, 100, 500, 800)

compteur_images = 0
nombre_verifications = 0
MAX_VERIFICATIONS = 15

SEUIL_OCCUPATION = 1000  # seuil à ajuster selon ton setup

def detect_bouton_rouge(roi_bgr):
    hsv = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2HSV)
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
    for c in contours:
        if cv2.contourArea(c) > 500:
            return True
    return False

while nombre_verifications < MAX_VERIFICATIONS:
    frame = picam2.capture_array()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    x, y, w, h = poste_zone

    zone_ref = gray_ref[y:y + h, x:x + w]
    zone_actuelle = gray[y:y + h, x:x + w]

    # Détection occupation par différence d’image
    diff = cv2.absdiff(zone_ref, zone_actuelle)
    _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
    thresh = cv2.GaussianBlur(thresh, (5, 5), 0)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    aire_totale = sum(cv2.contourArea(c) for c in contours)

    zone_bgr = frame[y:y + h, x:x + w]
    bouton_rouge = detect_bouton_rouge(zone_bgr)

    if aire_totale < SEUIL_OCCUPATION:
        print("Poste vide.")
    else:
        if bouton_rouge:
            print("Poste occupé et bouton rouge détecté.")
            nom_fichier = f"{save_dir}/capture_{compteur_images}.jpg"
            cv2.imwrite(nom_fichier, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
            compteur_images += 1
        else:
            print("Poste occupé mais bouton rouge non détecté.")

    nombre_verifications += 1
    time.sleep(1)

picam2.stop()
print(f"Fin du programme après {MAX_VERIFICATIONS} vérifications.")
