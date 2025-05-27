from picamera2 import Picamera2
import cv2
import numpy as np
import time
import os

# Création dossier pour sauvegarder les images
save_dir = "./captures_postes"
os.makedirs(save_dir, exist_ok=True)

# Définition des zones des 6 postes (x, y, largeur, hauteur)
zones_postes = [
    (0, 0, 100, 200),  # À ajuster selon ta caméra et poste
    (100, 0, 100, 200),
    (200, 0, 100, 200),
    (300, 0, 100, 200),
    (400, 0, 100, 200),
    (500, 0, 100, 200),
]

picam2 = Picamera2()
picam2.start()
time.sleep(2)  # Attente démarrage caméra

frame_ref = picam2.capture_array()
gray_ref = cv2.cvtColor(frame_ref, cv2.COLOR_BGR2GRAY)

compteur_images = 0

while True:
    frame = picam2.capture_array()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    diff = cv2.absdiff(gray_ref, gray)
    _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
    thresh = cv2.GaussianBlur(thresh, (5, 5), 0)

    for i, (x, y, w, h) in enumerate(zones_postes):
        zone = thresh[y:y+h, x:x+w]
        contours, _ = cv2.findContours(zone, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        aire_totale = sum(cv2.contourArea(c) for c in contours)

        # Seuil pour décider si le poste est occupé (ajuste ce seuil)
        seuil_occupation = 500

        if aire_totale >= seuil_occupation:
            print(f"Poste {i+1} est occupé. Sauvegarde de l'image...")
            # Sauvegarde la photo complète (ou la zone uniquement si tu veux)
            nom_fichier = f"{save_dir}/poste_{i+1}_capture_{compteur_images}.jpg"
            cv2.imwrite(nom_fichier, frame)
            compteur_images += 1
        else:
            print(f"Poste {i+1} est vide.")

    time.sleep(1)
