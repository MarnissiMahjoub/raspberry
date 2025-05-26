import cv2
import numpy as np
from picamera2 import Picamera2

# Charger l'image de référence (déjà enregistrée)
ref_image = cv2.imread('capture.jpg')
if ref_image is None:
    print("Image capture.jpg introuvable. Vérifie le chemin.")
    exit()

# Redimensionner pour uniformiser
target_size = (320, 240)
ref_image = cv2.resize(ref_image, target_size)
ref_gray = cv2.cvtColor(ref_image, cv2.COLOR_BGR2GRAY)

# Initialiser la caméra
picam2 = Picamera2()
picam2.preview_configuration.main.size = target_size
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")
picam2.start()

# Attendre un peu que la caméra se stabilise
import time
time.sleep(2)

# Prendre une seule photo (capture actuelle)
frame = picam2.capture_array()
frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

# Comparer avec la référence
diff = cv2.absdiff(ref_gray, frame_gray)
_, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

# Calculer le pourcentage de différence
diff_percent = (np.sum(thresh > 0) / thresh.size) * 100
print(f"Différence détectée : {diff_percent:.2f}%")

# Déterminer s'il y a un changement
if diff_percent > 5:  # Seuil ajustable
    print("⚠️ Changement détecté entre les images !")
    # Sauvegarder la nouvelle image avec un nom unique
    cv2.imwrite("nouvelle_capture.jpg", frame)
else:
    print("✅ Pas de changement significatif détecté.")

# Afficher la différence pour vérifier visuellement (optionnel)
cv2.imshow("Différence détectée", thresh)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Fermer la caméra proprement
picam2.stop()
