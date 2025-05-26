import cv2

# Charger le classificateur HaarCascade (pour la détection de visages)
haar_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Lire l'image capturée
img = cv2.imread('capture.jpg')

if img is None:
    print("Erreur : L'image n'a pas été trouvée.")
    exit()

# Convertir en niveaux de gris
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Détecter les visages dans l'image
faces = haar_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

# Afficher les résultats
for (x, y, w, h) in faces:
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

print(f"Nombre de personnes détectées : {len(faces)}")

# Afficher l'image
cv2.imshow('Détection de visage', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
