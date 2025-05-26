import cv2

# Remplace par l'IP de ton Raspberry Pi
raspberry_ip = "192.168.1.42"  # Exemple
raspberry_port = 8888

# Pipeline GStreamer pour décoder le flux H.264 et le lire dans OpenCV
gst_pipeline = f"tcpclientsrc host={raspberry_ip} port={raspberry_port} ! h264parse ! avdec_h264 ! videoconvert ! appsink"

cap = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)

if not cap.isOpened():
    print("Erreur : impossible d'ouvrir le flux.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Erreur lors de la lecture du flux.")
        break

    cv2.imshow("Flux vidéo", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
