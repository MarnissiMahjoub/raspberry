python3 -c "import cv2; cap = cv2.VideoCapture(0); ret, frame = cap.read(); print(ret, frame.shape if ret else 'Erreur'); cap.release()"
