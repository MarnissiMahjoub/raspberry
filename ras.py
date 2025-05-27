from picamera2 import Picamera2
import cv2
import time
import os

save_dir = "./captures"
os.makedirs(save_dir, exist_ok=True)

picam2 = Picamera2()

config = picam2.create_still_configuration(main={"size": (4056, 3040)})
picam2.configure(config)

try:
    picam2.start()
    time.sleep(2)

    frame_ref = picam2.capture_array()
    frame_ref_gray = cv2.cvtColor(frame_ref, cv2.COLOR_BGR2GRAY)

    SEUIL_POURCENTAGE = 1.0  # seuil de différence par poste
    SEUIL_CONSECUTIF = 3  # nombre de détections consécutives avant alerte
    compteur_images = 0
    nombre_verifications = 0
    MAX_VERIFICATIONS = 15

    detections_consecutives = [0] * 6  # compteur pour chaque poste

    height, width = frame_ref_gray.shape
    zone_width = width // 6  # largeur d’une zone poste

    while nombre_verifications < MAX_VERIFICATIONS:
        frame = picam2.capture_array()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        for i in range(6):
            x_start = i * zone_width
            x_end = (i + 1) * zone_width if i < 5 else width  # pour la dernière zone

            zone_ref = frame_ref_gray[:, x_start:x_end]
            zone_current = gray[:, x_start:x_end]

            diff = cv2.absdiff(zone_ref, zone_current)
            _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

            nb_pixels_diff = cv2.countNonZero(thresh)
            total_pixels = thresh.shape[0] * thresh.shape[1]
            pourcentage_diff = (nb_pixels_diff / total_pixels) * 100

            print(f"Poste {i + 1} différence : {pourcentage_diff:.2f}%")

            if pourcentage_diff > SEUIL_POURCENTAGE:
                detections_consecutives[i] += 1
                if detections_consecutives[i] >= SEUIL_CONSECUTIF:
                    print(f"⚠️ Poste {i + 1} vide détecté ! Sauvegarde de l'image...")
                    nom_fichier = f"{save_dir}/capture_poste_{i + 1}_{compteur_images}.jpg"
                    cv2.imwrite(nom_fichier, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
                    compteur_images += 1
                    detections_consecutives[i] = 0  # reset pour ce poste
            else:
                detections_consecutives[i] = 0  # reset compteur si différence faible

        nombre_verifications += 1
        time.sleep(1)

except KeyboardInterrupt:
    print("Programme arrêté par l'utilisateur.")

finally:
    picam2.stop()
    print("Fin du programme après", nombre_verifications, "vérifications.")
