from picamera2 import Picamera2
import cv2
from ultralytics import YOLO
import numpy as np
import time
import os
from datetime import datetime

# Dossier pour sauvegarder les captures
save_dir = "./captures_poste"
os.makedirs(save_dir, exist_ok=True)

# Initialiser la caméra
frame_size = (1280, 720)
picam2 = Picamera2()
config = picam2.create_still_configuration(main={"size": frame_size})
picam2.configure(config)
picam2.start()
time.sleep(2)  # Laisser la caméra se stabiliser

# Charger le modèle YOLOv8
model = YOLO("yolov8n.pt")  # Remplace par yolov8s.pt ou autre selon le modèle choisi

print("Appuyez sur 'q' pour quitter.")

try:
    while True:
        frame = picam2.capture_array()
        frame = cv2.resize(frame, frame_size)

        # Détection avec YOLO
        results = model.predict(frame, imgsz=640, conf=0.5, verbose=False)

        personne_presente = False

        for result in results:
            for box in result.boxes:
                cls = int(box.cls[0])
                if cls == 0:  # Classe 0 = personne
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
                    cv2.putText(frame, "Employe detecte", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
                    personne_presente = True

        # Si aucune personne détectée
        if not personne_presente:
            cv2.putText(frame, "Employe absent", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
            now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            nom_fichier = f"{save_dir}/poste_vide_{now}.jpg"
            cv2.imwrite(nom_fichier, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
            print("Poste vide detecte. Image sauvegardee.")
        else:
            cv2.putText(frame, "Employe present", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

        cv2.imshow("Detection Employe", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("Arret demande par l'utilisateur.")
            break

        time.sleep(0.05)

except KeyboardInterrupt:
    print("Arret force (CTRL+C) detecte.")

finally:
    picam2.stop()
    cv2.destroyAllWindows()
    print("Programme termine proprement.")
