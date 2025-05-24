import cv2

# Initialiser la caméra
cap = cv2.VideoCapture(0)  # 0 pour USB, 0 ou 1 pour caméra Pi, à tester selon ton matériel

# Vérifie si la caméra fonctionne
if not cap.isOpened():
    print("Erreur : Impossible d'ouvrir la caméra")
    exit()

# Initialiser le soustracteur de fond
fgbg = cv2.createBackgroundSubtractorMOG2()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Erreur lors de la lecture de la caméra")
        break

    # Redimensionner pour moins de charge sur le Pi
    frame = cv2.resize(frame, (640, 480))

    # Appliquer le soustracteur de fond
    fgmask = fgbg.apply(frame)

    # Seuillage pour nettoyer
    _, thresh = cv2.threshold(fgmask, 244, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    dilated = cv2.dilate(thresh, kernel, iterations=2)

    # Chercher les contours
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    presence_detected = False

    for contour in contours:
        if cv2.contourArea(contour) > 1000:  # Ajuste selon ta scène
            presence_detected = True
            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    if presence_detected:
        cv2.putText(frame, "Presence detectee!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    else:
        cv2.putText(frame, "Aucune presence", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    # Affichage du résultat
    cv2.imshow("Detection de presence", frame)

    # Quitter en appuyant sur 'q'
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

# Nettoyage
cap.release()
cv2.destroyAllWindows()
