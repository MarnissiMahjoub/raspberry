import cv2

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Impossible d'ouvrir la caméra")
else:
    ret, frame = cap.read()
    if ret:
        print("Image capturée OK")
    else:
        print("Impossible de lire une image")
cap.release()
