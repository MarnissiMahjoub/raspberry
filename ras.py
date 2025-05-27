import cv2

# Initialiser caméra
cap = cv2.VideoCapture(0)  # Modifier si nécessaire

# Lire une frame de référence (background)
ret, frame_ref = cap.read()
frame_ref_gray = cv2.cvtColor(frame_ref, cv2.COLOR_BGR2GRAY)

while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    diff = cv2.absdiff(frame_ref_gray, gray)
    _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

    # Diviser l'image en 6 zones
    h, w = thresh.shape
    step = w // 6

    for i in range(6):
        roi = thresh[:, i*step:(i+1)*step]
        non_zero = cv2.countNonZero(roi)
        if non_zero > 500:  # Ajuster ce seuil
            status = "Présent"
        else:
            status = "Absent"
        print(f"Poste {i+1}: {status}")

    cv2.imshow('Différence', thresh)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
