import cv2
import numpy as np

# Supposons que tes zones soient des rectangles définis comme (x, y, w, h)
zones_postes = [
    (0, 0, 100, 200),     # Poste 1
    (100, 0, 100, 200),   # Poste 2
    (200, 0, 100, 200),   # Poste 3
    (300, 0, 100, 200),   # Poste 4
    (400, 0, 100, 200),   # Poste 5
    (500, 0, 100, 200),   # Poste 6
]

# Image de référence et image actuelle (ex : capturées)
frame_ref = cv2.imread("ref.jpg")        # Image référence
frame = cv2.imread("courante.jpg")       # Image à analyser

gray_ref = cv2.cvtColor(frame_ref, cv2.COLOR_BGR2GRAY)
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

diff = cv2.absdiff(gray_ref, gray)
_, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
thresh = cv2.GaussianBlur(thresh, (5,5), 0)  # lissage

for i, (x, y, w, h) in enumerate(zones_postes):
    zone = thresh[y:y+h, x:x+w]
    contours, _ = cv2.findContours(zone, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    aire_totale = sum(cv2.contourArea(c) for c in contours)

    if aire_totale < 500:  # seuil à ajuster selon la taille des objets/personnes
        print(f"Poste {i+1} est vide")
    else:
        print(f"Poste {i+1} est occupé")

# Optionnel : afficher les zones et contours pour debug
for (x, y, w, h) in zones_postes:
    cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)

cv2.imshow("Postes détectés", frame)
cv2.waitKey(0)
cv2.destroyAllWindows()
