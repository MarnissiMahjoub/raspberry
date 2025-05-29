from picamera2 import Picamera2
import cv2
import numpy as np
import time
import os
from datetime import datetime

# Dossier pour sauvegarder les captures et les références
save_dir = "./captures_poste"
ref_dir = "./references"
os.makedirs(save_dir, exist_ok=True)
os.makedirs(ref_dir, exist_ok=True)

# Fichiers des références
ref_vide_path = os.path.join(ref_dir, "reference_vide.jpg")
ref_present_path = os.path.join(ref_dir, "reference_present.jpg")

# Charger la référence vide
if os.path.exists(ref_vide_path):
    ref_vide = cv2.imread(ref_vide_path)
    print("Référence vide chargée.")
else:
    ref_vide = None
    print("Aucune référence vide trouvée. Appuyez sur 'v' pour capturer.")

# Charger la référence employé présent
if os.path.exists(ref_present_path):
    ref_present = cv2.imread(ref_present_path)
    print("Référence employé présent chargée.")
else:
    ref_present = None
    print("Aucune référence employé présent trouvée. Appuyez sur 'p' pour capturer.")

frame_size = (1280, 720)

# Configurer la caméra
picam2 = Picamera2()
config = picam2.create_still_configuration(main={"size": frame_size})
picam2.configure(config)
picam2.start()
time.sleep(2)  # Laisser la caméra se stabiliser

# Zone du poste
x, y, w, h = 100, 100, 400, 300  # Ajuste si besoin

seuil_detection = 30

print("Appuyez sur 'q' pour quitter.")
print("Appuyez sur 'v' pour enregistrer la référence vide.")
print("Appuyez sur 'p' pour enregistrer la référence employé présent.")

try:
    while True:
        frame = picam2.capture_array()
        frame = cv2.resize(frame, frame_size)

        if ref_vide is not None:
            # Comparer avec la référence vide
            roi_frame = frame[y:y+h, x:x+w]
            roi_ref_vide = ref_vide[y:y+h, x:x+w]

            diff_vide = cv2.absdiff(cv2.cvtColor(roi_frame, cv2.COLOR_BGR2GRAY),
                                    cv2.cvtColor(roi_ref_vide, cv2.COLOR_BGR2GRAY))
            score_vide = np.mean(diff_vide)
            employe_present = score_vide > seuil_detection
        else:
            employe_present = True  # Par défaut, si pas de référence vide

        # Affichage des cadres
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

        # Texte d'état
        statut = "Employe Present" if employe_present else "Absence"
        cv2.putText(frame, statut, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 255, 0) if employe_present else (0, 255, 255), 2)

        # Sauvegarde si absence détectée
        if not employe_present:
            now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            nom_fichier = f"{save_dir}/poste_vide_{now}.jpg"
            cv2.imwrite(nom_fichier, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
            print("Poste vide detecte. Image sauvegardee.")

        # Affichage du flux
        cv2.imshow("Flux Camera Temps Reel", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            print("Arret demande par l'utilisateur.")
            break
        elif key == ord('v'):
            ref_vide = frame.copy()
            cv2.imwrite(ref_vide_path, ref_vide)
            print("Nouvelle référence vide enregistrée.")
        elif key == ord('p'):
            ref_present = frame.copy()
            cv2.imwrite(ref_present_path, ref_present)
            print("Nouvelle référence employé présent enregistrée.")

        time.sleep(0.05)

except KeyboardInterrupt:
    print("Arret force (CTRL+C) detecte.")

finally:
    picam2.stop()
    cv2.destroyAllWindows()
    print("Programme termine proprement.")
