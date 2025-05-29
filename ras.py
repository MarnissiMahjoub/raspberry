from picamera2 import Picamera2
import cv2
import os
import time

# Créer un dossier pour les références
ref_dir = "./references"
os.makedirs(ref_dir, exist_ok=True)

# Configurer la caméra
picam2 = Picamera2()
config = picam2.create_still_configuration(main={"size": (1280, 720)})
picam2.configure(config)
picam2.start()
time.sleep(2)  # Temps pour stabiliser

print("Appuyez sur 'v' pour capturer la reference VIDE")
print("Appuyez sur 'o' pour capturer la reference OCCUPEE")
print("Appuyez sur 'q' pour quitter")

while True:
    frame = picam2.capture_array()
    cv2.imshow("Flux Camera", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('v'):
        cv2.imwrite(f"{ref_dir}/reference_vide.jpg", frame)
        print("Référence VIDE enregistrée.")
    elif key == ord('o'):
        cv2.imwrite(f"{ref_dir}/reference_occupee.jpg", frame)
        print("Référence OCCUPEE enregistrée.")
    elif key == ord('q'):
        print("Fin du programme.")
        break

cv2.destroyAllWindows()
picam2.stop()
