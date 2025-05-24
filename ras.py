import cv2
import numpy as np
import math

# Initialisation de la caméra avec une grande résolution
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)


# Fonction pour améliorer la clarté de l'image
def enhance_image(image):
    # Netteté
    kernel_sharpen = np.array([[0, -1, 0],
                               [-1, 5, -1],
                               [0, -1, 0]])
    sharpened = cv2.filter2D(image, -1, kernel_sharpen)

    # Contraste et luminosité
    alpha = 1.7  # Contraste
    beta = 40  # Luminosité
    contrast = cv2.convertScaleAbs(sharpened, alpha=alpha, beta=beta)

    # Correction gamma (pour éviter une image sombre)
    gamma = 1.2  # Augmenter un peu la luminosité naturelle
    gamma_correction = np.array([((i / 255.0) ** (1 / gamma)) * 255 for i in np.arange(256)]).astype("uint8")
    corrected = cv2.LUT(contrast, gamma_correction)

    return corrected


while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)  # Effet miroir

    # Améliorer la clarté
    frame = enhance_image(frame)

    # Zone ROI plus grande
    roi = frame[50:600, 50:800]  # Ajuste la taille si besoin
    cv2.rectangle(frame, (50, 50), (800, 600), (0, 255, 0), 2)

    # Conversion en HSV
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    # Plage de couleur de la peau
    lower_skin = np.array([0, 20, 70], dtype=np.uint8)
    upper_skin = np.array([20, 255, 255], dtype=np.uint8)

    # Masque
    mask = cv2.inRange(hsv, lower_skin, upper_skin)
    mask = cv2.GaussianBlur(mask, (5, 5), 0)
    mask = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=2)

    # Trouver les contours
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        cnt = max(contours, key=cv2.contourArea)
        hull = cv2.convexHull(cnt)

        cv2.drawContours(roi, [cnt], -1, (0, 255, 0), 2)
        cv2.drawContours(roi, [hull], -1, (0, 0, 255), 2)

        hull_indices = cv2.convexHull(cnt, returnPoints=False)
        if len(hull_indices) > 3:
            defects = cv2.convexityDefects(cnt, hull_indices)
            if defects is not None:
                count_defects = 0
                for i in range(defects.shape[0]):
                    s, e, f, d = defects[i, 0]
                    start = tuple(cnt[s][0])
                    end = tuple(cnt[e][0])
                    far = tuple(cnt[f][0])

                    a = math.dist(start, end)
                    b = math.dist(start, far)
                    c = math.dist(end, far)
                    angle = math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) * 57

                    if angle <= 90:
                        count_defects += 1
                        cv2.circle(roi, far, 5, [0, 0, 255], -1)

                fingers = count_defects + 1
                cv2.putText(frame, f"Doigts: {fingers}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    # Affichage
    cv2.imshow("Frame", frame)
    cv2.imshow("Mask", mask)

    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # Touche 'ESC' pour quitter
        break

cap.release()
cv2.destroyAllWindows()
