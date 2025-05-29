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
x, y, w, h = 100, 100, 400, 300  # Zone du poste (cadre vert)

# Chargement des images de référence (poste vide et poste occupé)
ref_empty_path = "poste_vide.jpg"
ref_present_path = "poste_occupé.jpg"

# Fonction pour sauvegarder l’image de référence
def save_reference_image(path, image):
    cv2.imwrite(path, image, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    print(f"Image de référence sauvegardée: {path}")

print("Appuyez sur 'q' pour quitter, 'v' pour capturer poste vide, 'p' pour capturer poste occupé.")

try:
    while True:
        frame = picam2.capture_array()
        frame_blur = cv2.GaussianBlur(frame, (5,5), 0)

        # Zone du poste
        zone = frame_blur[y:y+h, x:x+w]
        gray_zone = cv2.cvtColor(zone, cv2.COLOR_BGR2GRAY)
        _, mask_occup = cv2.threshold(gray_zone, 30, 255, cv2.THRESH_BINARY)

        nb_pixels_total = mask_occup.size
        nb_pixels_occupe = cv2.countNonZero(mask_occup)
        ratio_occupe = nb_pixels_occupe / nb_pixels_total
        seuil_presence = 0.05  # seuil pour présence

        poste_ok = ratio_occupe > seuil_presence

        # Détection contours dans la zone
        contours, _ = cv2.findContours(mask_occup, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        employe_dehors = False

        if contours:
            c = max(contours, key=cv2.contourArea)
            x_c, y_c, w_c, h_c = cv2.boundingRect(c)

            # Dessiner le rectangle englobant de l’employé (zone détectée)
            cv2.rectangle(zone, (x_c, y_c), (x_c + w_c, y_c + h_c), (255, 255, 0), 2)

            # Vérifier si bounding box dépasse le cadre vert (zone poste)
            if x_c < 0 or y_c < 0 or (x_c + w_c) > w or (y_c + h_c) > h:
                employe_dehors = True
        else:
            employe_dehors = True  # Pas de contour détecté, donc absent

        # Dessiner le cadre vert du poste sur l’image globale
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

        # Affichage du statut
        if employe_dehors:
            status_text = "Employe hors poste - Absent"
            color = (0, 0, 255)  # rouge
        elif poste_ok:
            status_text = "Poste OK - Employe Present"
            color = (0, 255, 0)  # vert
        else:
            status_text = "Poste Vide"
            color = (0, 255, 255)  # jaune

        cv2.putText(frame, status_text, (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        # Sauvegarde si poste vide ou absent (employé hors cadre)
        if employe_dehors or not poste_ok:
            now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            nom_fichier = f"{save_dir}/poste_capture_{now}.jpg"
            cv2.imwrite(nom_fichier, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 95])

        # Affichage flux temps réel
        cv2.imshow("Flux Camera Temps Reel", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            print("Arrêt demandé par l'utilisateur.")
            break
        elif key == ord('v'):
            save_reference_image(ref_empty_path, frame[y:y+h, x:x+w])
        elif key == ord('p'):
            save_reference_image(ref_present_path, frame[y:y+h, x:x+w])

        time.sleep(0.05)

except KeyboardInterrupt:
    print("Arrêt forcé (CTRL+C) détecté.")

finally:
    picam2.stop()
    cv2.destroyAllWindows()
    print("Programme terminé proprement.")
