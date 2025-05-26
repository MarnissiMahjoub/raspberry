import cv2

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Impossible d'ouvrir la caméra")
    exit()

ret, frame = cap.read()
if ret:
    print("Image capturée OK")
    cv2.imshow("Test", frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print("Impossible de lire une image")

cap.release()
