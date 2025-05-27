from picamera2 import Picamera2
import cv2
import numpy as np
import time
import os

save_dir = "./captures_postes"
os.makedirs(save_dir, exist_ok=True)

picam2 = Picamera2()

# Config haute résolution (ajuste la résolution selon ta caméra)
config = picam2.create_still_configuration(main={"size": (3280, 2464)})
picam2.configure(config)

picam2.start()
time.sleep(2)

frame_ref = picam2.capture_array()
gray_ref = cv2.cvtColor(frame_ref, cv2.COLOR_BGR2GRAY)

zones_postes = [
    (0, 0, 500, 800),  # exemple, ajuste selon ta capture plus grande
    (500, 0, 500, 800),
    (1000, 0, 500, 800),
    (1500, 0, 500, 800),
    (2000, 0, 500, 800),
    (2500, 0, 500, 800),
]

compteur_images = 0
nombre_verifications = 0
MAX_VERIFICATIONS = 15

while nombre_verifications < MAX_VERIFICATIONS:
    frame = picam2.capture_array()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    diff = cv2.absdiff(gray_ref, gray)
    _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
    thresh = cv2.GaussianBlur(thresh, (5, 5), 0)

    for i, (x, y, w, h) in enumerate(zones_postes):
        zone = thresh[y:y+h, x:x+w]
        contours, _ = cv2.findContours(zone, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        aire_totale = sum(cv2.contourArea(c) for c in contours)

        seuil_occupation = 1000  # à ajuster

        if aire_totale >= seuil_occupation:
            print(f"Poste {i+1} est occupé. Sauvegarde de l'image...")
            nom_fichier = f"{save_dir}/poste_{i+1}_capture_{compteur_images}.jpg"
            # Sauvegarde en JPEG avec qualité 95%
            cv2.imwrite(nom_fichier, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
            compteur_images += 1
        else:
            print(f"Poste {i+1} est vide.")

    nombre_verifications += 1
    print(f"Vérification {nombre_verifications}/{MAX_VERIFICATIONS} terminée.\n")
    time.sleep(1)

picam2.stop()
print("Fin du programme après 15 vérifications.")
