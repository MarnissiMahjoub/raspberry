from picamera2 import Picamera2
import cv2
import numpy as np
import time

# Définition des zones des 6 postes (x, y, largeur, hauteur)
zones_postes = [
    (0, 0, 100, 200),  # Ajuste ces valeurs à ta config
    (100, 0, 100, 200),
    (200, 0, 100, 200),
    (300, 0, 100, 200),
    (400, 0, 100, 200),
    (500, 0, 100, 200),
]

picam2 = Picamera2()
picam2.start()
time.sleep(2)  # Temps pour que la caméra soit prête

# Capture image de référence (poste occupés sans personne)
frame_ref = picam2.capture_array()
gray_ref = cv2.cvtColor(frame_ref, cv2.COLOR_BGR2GRAY)

while True:
    frame = picam2.capture_array()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    diff = cv2.absdiff(gray_ref, gray)
    _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
    thresh = cv2.GaussianBlur(thresh, (5,5), 0)

    for i, (x, y, w, h) in enumerate(zones_postes):
        zone = thresh[y:y+h, x:x+w]
        contours, _ = cv2.findContours(zone, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        aire_totale = sum(cv2.contourArea(c) for c in contours)

        if aire_totale < 500:
            print(f"Poste {i+1} est vide")
        else:
            print(f"Poste {i+1} est occupé")

    time.sleep(1)
