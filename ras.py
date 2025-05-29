from picamera2 import Picamera2
import cv2
import numpy as np
import time
import os
from datetime import datetime

# Dossier pour sauvegarder les captures
save_dir = "./captures_poste"
os.makedirs(save_dir, exist_ok=True)

# Charger la référence "poste vide"
ref_vide = cv2.imread("./references/reference_vide.jpg")
if ref_vide is None:
    print("Erreur : La référence vide n'est pas trouvée. Vérifiez le dossier.")
    exit()

frame_size = (1280, 720)
ref_vide = cv2.resize(ref_vide, frame_size)

# Configurer la caméra
picam2 = Picamera2()
config = picam2.create_still_configuration(main={"size": frame_size})
picam2.configure(config)
picam2.start()
time.sleep(2)  # Laisser le temps à la caméra de se stabiliser

# Zone du poste
x, y, w, h = 100, 100, 400, 300  # Ajuste selon la caméra

seuil_detection = 30  # Seuil pour considérer le poste comme vide
delai_absence = 10  # Délai en secondes pour confirmer l'absence

# Variables de suivi
absence_start_time = None
poste_vide_confirme = False

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

        # Comparaison avec la référence vide
        score_vide = comparer_images(frame, ref_vide, (x, y, w, h))
        employe_present = score_vide > seuil_detection

        # Gestion du délai d'absence
        if not employe_present:
            if absence_start_time is None:
                absence_start_time = time.time()
            elif time.time() - absence_start_time >= delai_absence:
                if not poste_vide_confirme:
                    poste_vide_confirme = True
                    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    nom_fichier = f"{save_dir}/poste_vide_{now}.jpg"
                    cv2.imwrite(nom_fichier, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
                    print("Poste vide détecté depuis 10 secondes. Image sauvegardée.")
        else:
            absence_start_time = None
            poste_vide_confirme = False

        # Affichage des cadres et texte
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)  # Cadre vert
        statut = "Employe Present" if employe_present else "Absence en cours..."
        cv2.putText(frame, statut, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0) if employe_present else (0, 255, 255), 2)

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
