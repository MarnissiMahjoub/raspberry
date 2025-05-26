from picamera2 import Picamera2
import cv2

# Initialiser la caméra
picam2 = Picamera2()
picam2.preview_configuration.main.size = (640, 480)  # Taille de l'image
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")

# Démarrer la caméra
picam2.start()

while True:
    frame = picam2.capture_array()  # Capture une image
    cv2.imshow("Camera Pi", frame)

    # Quitter si on appuie sur 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Fermer les fenêtres
cv2.destroyAllWindows()
picam2.stop()
