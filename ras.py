import cv2

cap = cv2.VideoCapture(0)  # Vérifie si c'est bien la caméra
print(cap)
ret, frame_ref = cap.read()
if not ret or frame_ref is None:
    print("Erreur : Impossible de capturer l'image depuis la caméra.")
    cap.release()
    exit(1)

frame_ref_gray = cv2.cvtColor(frame_ref, cv2.COLOR_BGR2GRAY)

while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        print("Erreur : Problème lors de la lecture de l'image.")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    diff = cv2.absdiff(frame_ref_gray, gray)
    _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

    cv2.imshow('Diff', thresh)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
