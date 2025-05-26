import cv2

# Initialiser le détecteur de personnes HOG + SVM pré-entraîné
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

# Ouvrir la caméra (index 0 par défaut)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Erreur : impossible d'ouvrir la caméra")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Erreur lors de la lecture de la vidéo")
        break

    # Redimensionner pour accélérer la détection (optionnel)
    frame_resized = cv2.resize(frame, (640, 480))

    # Détecter les personnes (paramètres modifiables)
    boxes, weights = hog.detectMultiScale(frame_resized, winStride=(8,8))

    # Dessiner des rectangles autour des personnes détectées
    for (x, y, w, h) in boxes:
        cv2.rectangle(frame_resized, (x, y), (x+w, y+h), (0, 255, 0), 2)

    # Afficher le nombre de personnes détectées
    cv2.putText(frame_resized, f'Personnes: {len(boxes)}', (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Afficher la vidéo
    cv2.imshow('Detection Personnes', frame_resized)

    # Quitter avec la touche 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
