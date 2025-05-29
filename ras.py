from picamera2 import Picamera2
import cv2
import numpy as np
import time
import os
from datetime import datetime

# Dossier pour sauvegarder les captures
save_dir = "./captures_poste"
os.makedirs(save_dir, exist_ok=True)

# Charger les références
ref_vide = cv2.imread("./references/reference_vide.jpg")
ref_occupee = cv2.imread("./references/reference_occupee.jpg")
if ref_vide is None or ref_occupee is None:
    print("Erreur : Les références ne sont pas trouvées. Vérifiez le dossier.")
    exit()

frame_size = (1280, 720)
ref_vide = cv2.resize(ref_vide, frame_size)
ref_occupee = cv2.resize(ref_occupee, frame_size)

# Configurer la caméra
picam2 = Picamera2()
config = picam2.create_still_configuration(main={"size": frame_size})
picam2.configure(config)
picam2.start()
time.sleep(2)  # Laisser le temps à la caméra de se stabiliser

# Zone du poste
x, y, w, h = 100, 100, 400, 300  # Ajuste ces valeurs pour ta caméra

seuil_detection = 30  # Ajuste si nécessaire

def comparer_images(img1, img2, zone):
    x, y, w, h = zone
    roi1 = img1[y:y+h, x:x+w]
    roi2 = img2[y:y+h, x:x+w]
    diff = cv2.absdiff(cv2.cvtColor(roi1, cv2.COLOR_BGR2GRAY),
                       cv2.cvtColor(roi2, cv2.COLOR_BGR2GRAY))
    score = np.mean(diff)
    return score

print("Appuyez sur 'q' pour quitter le programme.")

try:
    while True:
        frame = picam2.capture_array()
        frame = cv2.resize(frame, frame_size)

        # Comparaison avec les références
        score_vide = comparer_images(frame, ref_vide, (x, y, w, h))
        score_occupee = comparer_images(frame, ref_occupee, (x, y, w, h))

        # Détection bouton rouge (dans la zone)
        zone = frame[y:y+h, x:x+w]
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

        # Déterminer l'état du poste
        if bouton_rouge_detecte:
            statut = "Bouton Rouge Detecte"
            color = (0, 0, 255)
        elif score_vide < seuil_detection:
            statut = "Attention: Poste Vide"
            color = (0, 255, 255)
        elif score_occupee < seuil_detection:
            statut = "Poste OK - Employe Present"
            color = (0, 255, 0)
        else:
            statut = "Inconnu"
            color = (255, 255, 0)

        # Affichage des cadres
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)  # Cadre vert
        cv2.rectangle(frame, (x + 50, y + 50), (x + w - 50, y + h - 50), (0, 0, 255), 2)  # Cadre rouge
        cv2.putText(frame, statut, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        # Sauvegarde si nécessaire
        if bouton_rouge_detecte or statut == "Attention: Poste Vide":
            now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            nom_fichier = f"{save_dir}/poste_capture_{now}.jpg"
            cv2.imwrite(nom_fichier, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 95])

        # Affichage
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
