from picamera2 import Picamera2
import cv2
import numpy as np
import time

# Charger les références
ref_vide = cv2.imread("./references/reference_vide.jpg")
ref_occupee = cv2.imread("./references/reference_occupee.jpg")

if ref_vide is None or ref_occupee is None:
    print("Erreur : Les références ne sont pas trouvées. Vérifiez le dossier.")
    exit()

# Redimensionner si nécessaire
frame_size = (1280, 720)
ref_vide = cv2.resize(ref_vide, frame_size)
ref_occupee = cv2.resize(ref_occupee, frame_size)

# Zone du poste
zone_poste = (300, 200, 400, 300)

# Configurer la caméra
picam2 = Picamera2()
config = picam2.create_still_configuration(main={"size": frame_size})
picam2.configure(config)
picam2.start()
time.sleep(2)

def comparer_images(img1, img2, zone):
    x, y, w, h = zone
    roi1 = img1[y:y+h, x:x+w]
    roi2 = img2[y:y+h, x:x+w]
    diff = cv2.absdiff(cv2.cvtColor(roi1, cv2.COLOR_BGR2GRAY),
                       cv2.cvtColor(roi2, cv2.COLOR_BGR2GRAY))
    score = np.mean(diff)
    return score

seuil_detection = 30  # Ajuste si nécessaire

while True:
    frame = picam2.capture_array()
    frame = cv2.resize(frame, frame_size)

    # Comparer avec les références
    score_vide = comparer_images(frame, ref_vide, zone_poste)
    score_occupee = comparer_images(frame, ref_occupee, zone_poste)

    # Résultat
    if score_vide < seuil_detection:
        statut = "Poste VIDE (employé absent)"
        color = (0, 0, 255)  # Rouge
    elif score_occupee < seuil_detection:
        statut = "Poste OCCUPE (employé présent)"
        color = (0, 255, 0)  # Vert
    else:
        statut = "INCONNU"
        color = (255, 255, 0)  # Jaune

    # Affichage des cadres
    x, y, w, h = zone_poste
    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)  # Vert global
    padding = 20
    cv2.rectangle(frame, (x+padding, y+padding), (x+w-padding, y+h-padding), (0, 0, 255), 2)  # Rouge interne

    # Texte
    cv2.putText(frame, statut, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2)

    cv2.imshow("Détection Employé", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
picam2.stop()
