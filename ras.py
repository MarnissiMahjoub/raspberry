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

# Définir les 6 zones (ajuste les coordonnées à ton espace)
zones = [
    (100, 100, 300, 400),
    (320, 100, 520, 400),
    (540, 100, 740, 400),
    (760, 100, 960, 400),
    (980, 100, 1180, 400),
    (1200, 100, 1400, 400)
]

print("Appuyez sur 'q' pour quitter.")

try:
    while True:
        frame = picam2.capture_array()
        frame = cv2.resize(frame, frame_size)

        # Détection avec YOLO
        results = model.predict(frame, imgsz=640, conf=0.5, verbose=False)

        presence = [False] * len(zones)

        for result in results:
            for box in result.boxes:
                cls = int(box.cls[0])
                if cls == 0:  # Classe 0 = personne
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cx = (x1 + x2) // 2
                    cy = (y1 + y2) // 2
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)

                    # Vérifier dans quelle zone se trouve le centre de la détection
                    for i, (zx1, zy1, zx2, zy2) in enumerate(zones):
                        if zx1 <= cx <= zx2 and zy1 <= cy <= zy2:
                            presence[i] = True

        # Affichage des zones et du statut
        for i, (zx1, zy1, zx2, zy2) in enumerate(zones):
            color = (0, 255, 0) if presence[i] else (0, 0, 255)
            label = f"Employe {i+1}: Present" if presence[i] else f"Employe {i+1}: Absent"
            cv2.rectangle(frame, (zx1, zy1), (zx2, zy2), color, 2)
            cv2.putText(frame, label, (zx1 + 5, zy1 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            # Sauvegarde si absence détectée
            if not presence[i]:
                now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                nom_fichier = f"{save_dir}/poste_{i+1}_vide_{now}.jpg"
                cv2.imwrite(nom_fichier, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 95])

        cv2.imshow("Detection Employes", frame)

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
