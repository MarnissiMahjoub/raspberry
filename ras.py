from picamera2 import Picamera2, Preview
import cv2
import time
import os

save_dir = "./captures"
os.makedirs(save_dir, exist_ok=True)

picam2 = Picamera2()

# Configurer la résolution (exemple 4056x3040, à adapter selon ta caméra)
config = picam2.create_still_configuration(main={"size": (4056, 3040)})
picam2.configure(config)

try:
    picam2.start()
    time.sleep(2)

    frame_ref = picam2.capture_array()
    frame_ref_gray = cv2.cvtColor(frame_ref, cv2.COLOR_BGR2GRAY)

    SEUIL_POURCENTAGE = 1.0  # seuil à 1%
    compteur_images = 0
    nombre_verifications = 0
    MAX_VERIFICATIONS = 30

    while nombre_verifications < MAX_VERIFICATIONS:
        frame = picam2.capture_array()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        diff = cv2.absdiff(frame_ref_gray, gray)
        _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

        nb_pixels_diff = cv2.countNonZero(thresh)
        total_pixels = thresh.shape[0] * thresh.shape[1]
        pourcentage_diff = (nb_pixels_diff / total_pixels) * 100

        print(f"Différence détectée : {pourcentage_diff:.2f}%")

        if pourcentage_diff > SEUIL_POURCENTAGE:
            print("⚠️ Employé absent du poste ! Sauvegarde de l'image...")
            nom_fichier = f"{save_dir}/capture_{compteur_images}.jpg"
            # Pour la qualité JPEG (0-100, 100 = meilleur), ajouter paramètre:
            cv2.imwrite(nom_fichier, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
            compteur_images += 1

        nombre_verifications += 1
        time.sleep(1)  # pause 1 seconde

except KeyboardInterrupt:
    print("Programme arrêté par l'utilisateur.")

finally:
    picam2.stop()
    print("Fin du programme après", nombre_verifications, "vérifications.")
