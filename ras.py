from picamera2 import Picamera2
import cv2
import numpy as np
import time
import os

save_dir = "./captures_postes"
os.makedirs(save_dir, exist_ok=True)

picam2 = Picamera2()
config = picam2.create_still_configuration(main={"size": (3280, 2464)})
picam2.configure(config)

picam2.start()
time.sleep(2)

frame_ref = picam2.capture_array()
gray_ref = cv2.cvtColor(frame_ref, cv2.COLOR_BGR2GRAY)

zones_postes = [
    (0, 0, 500, 800),
    (500, 0, 500, 800),
    (1000, 0, 500, 800),
    (1500, 0, 500, 800),
    (2000, 0, 500, 800),
    (2500, 0, 500, 800),
]

compteur_images = 0
nombre_verifications = 0
MAX_VERIFICATIONS = 10

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
    frame_with_rects = frame.copy()  # Copie pour ajouter les rectangles
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    diff = cv2.absdiff(gray_ref, gray)
    _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
    thresh = cv2.GaussianBlur(thresh, (5, 5), 0)

    poste_occupes = []

    for i, (x, y, w, h) in enumerate(zones_postes):
        zone_thresh = thresh[y:y + h, x:x + w]
        zone_bgr = frame[y:y + h, x:x + w]

        contours, _ = cv2.findContours(zone_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        aire_totale = sum(cv2.contourArea(c) for c in contours)
        seuil_occupation = 1000

        bouton_rouge = detect_bouton_rouge(zone_bgr)

        # Dessiner le grand cadre VERT (zone du poste)
        cv2.rectangle(frame_with_rects, (x, y), (x + w, y + h), (0, 255, 0), 5)

        # Dessiner le petit cadre ROUGE à l'intérieur (zone caméra)
        pad = 50  # marge intérieure pour le cadre rouge (ajuste si besoin)
        x_red, y_red = x + pad, y + pad
        w_red, h_red = w - 2 * pad, h - 2 * pad
        cv2.rectangle(frame_with_rects, (x_red, y_red), (x_red + w_red, y_red + h_red), (0, 0, 255), 3)

        if aire_totale >= seuil_occupation or bouton_rouge:
            print(f"Poste {i + 1} est occupé (par mouvement ou bouton rouge détecté).")
            poste_occupes.append(i)

    # Sauvegarde l'image avec les rectangles
    nom_fichier = f"{save_dir}/capture_{compteur_images}.jpg"
    cv2.imwrite(nom_fichier, frame_with_rects, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    print(f"Image sauvegardée : {nom_fichier}")
    compteur_images += 1

    nombre_verifications += 1
    print(f"Vérification {nombre_verifications}/{MAX_VERIFICATIONS} terminée.\n")
    time.sleep(1)

picam2.stop()
print("Fin du programme après 10 vérifications.")
