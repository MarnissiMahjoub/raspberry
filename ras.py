from picamera2 import Picamera2
import cv2
import numpy as np
import time
import os
from datetime import datetime

save_dir = "./captures_postes"
os.makedirs(save_dir, exist_ok=True)

picam2 = Picamera2()
config = picam2.create_still_configuration(main={"size": (1600, 700)})
picam2.configure(config)

picam2.start()
time.sleep(2)

frame_ref = picam2.capture_array()
gray_ref = cv2.cvtColor(frame_ref, cv2.COLOR_BGR2GRAY)

# Un seul poste pour le test : (x, y, largeur, hauteur)
zones_postes = [
    (500, 500, 800, 800),  # Poste 1 (ajuste ces valeurs selon ton setup)
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
    frame_with_rects = frame.copy()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    diff = cv2.absdiff(gray_ref, gray)
    _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
    thresh = cv2.GaussianBlur(thresh, (5, 5), 0)

    for i, (x, y, w, h) in enumerate(zones_postes):
        zone_thresh = thresh[y:y + h, x:x + w]
        zone_bgr = frame[y:y + h, x:x + w]

        contours, _ = cv2.findContours(zone_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        aire_totale = sum(cv2.contourArea(c) for c in contours)
        seuil_occupation = 1000

        bouton_rouge = detect_bouton_rouge(zone_bgr)

        # Cadre vert : grand cadre = zone du poste
        cv2.rectangle(frame_with_rects, (x, y), (x + w, y + h), (0, 255, 0), 5)

        # Cadre rouge : zone du bouton (plus petit à l'intérieur)
        pad = 50
        x_red, y_red = x + pad, y + pad
        w_red, h_red = w - 2 * pad, h - 2 * pad
        cv2.rectangle(frame_with_rects, (x_red, y_red), (x_red + w_red, y_red + h_red), (0, 0, 255), 3)

        if aire_totale >= seuil_occupation or bouton_rouge:
            print(f"Poste {i + 1} : Occupé ou bouton rouge détecté.")
        else:
            print(f"Poste {i + 1} : Vide.")

    # Sauvegarde avec timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nom_fichier = f"{save_dir}/capture_{compteur_images}_{timestamp}.jpg"
    cv2.imwrite(nom_fichier, frame_with_rects, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    print(f"Image sauvegardée : {nom_fichier}")

    # Affichage en temps réel
    cv2.imshow("Poste - Vue en direct", frame_with_rects)

    # Gestion de la fermeture (appuyer sur 'q' pour quitter à tout moment)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    compteur_images += 1
    nombre_verifications += 1
    print(f"Vérification {nombre_verifications}/{MAX_VERIFICATIONS} terminée.\n")
    time.sleep(1)

picam2.stop()
cv2.destroyAllWindows()
print("Fin du programme après 10 vérifications.")
