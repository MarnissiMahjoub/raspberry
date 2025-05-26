import cv2
import numpy as np
from picamera2 import Picamera2
import time

# Taille plus grande (augmenter selon ton besoin et la puissance du Raspberry)
target_size = (1280, 720)  # Full HD possible aussi : (1920, 1080)

# Charger l'image de référence (déjà enregistrée)
ref_image = cv2.imread('capture.jpg')
if ref_image is None:
    print("Image capture.jpg introuvable. Vérifie le chemin.")
    exit()

ref_image = cv2.resize(ref_image, target_size)
ref_gray = cv2.cvtColor(ref_image, cv2.COLOR_BGR2GRAY)

# Initialiser la caméra
picam2 = Picamera2()
picam2.preview_configuration.main.size = target_size
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")
picam2.start()

# Attendre un peu que la caméra se stabilise
time.sleep(2)

# Capturer une seule image
frame = picam2.capture_array()
frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

# Comparer avec la référence
diff = cv2.absdiff(ref_gray, frame_gray)
_, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

# Calculer le pourcentage de différence
diff_percent = (np.sum(thresh > 0) / thresh.size) * 100
print(f"Différence détectée : {diff_percent:.2f}%")

# Déterminer s'il y a un changement
if diff_percent > 2:  # Seuil ajusté (2% pour être plus sensible avec la HD)
    print("⚠️ Changement détecté entre les images !")
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    cv2.imwrite(f"nouvelle_capture_{timestamp}.jpg", frame)
else:
    print("✅ Pas de changement significatif détecté.")

# Afficher le résultat (optionnel)
cv2.imshow("Différence détectée", thresh)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Fermer la caméra proprement
picam2.stop()
