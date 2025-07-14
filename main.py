import cv2
import mediapipe as mp

# Inisialisasi MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

# Buka webcam
cap = cv2.VideoCapture(0)

# ID landmark ujung jari
tip_ids = [4, 8, 12, 16, 20]

gesture = "Tidak ada tangan"


while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    finger_count = 0

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            landmarks = hand_landmarks.landmark

            fingers = []

            # Thumb
            if landmarks[tip_ids[0]].x < landmarks[tip_ids[0] - 1].x:
                fingers.append(1)
            else:
                fingers.append(0)

            # Jari telunjuk - kelingking
            for id in range(1, 5):
                if landmarks[tip_ids[id]].y < landmarks[tip_ids[id] - 2].y:
                    fingers.append(1)
                else:
                    fingers.append(0)

            finger_count = sum(fingers)
            
            # Mapping jari terbuka ke gesture
            gesture = "Tidak dikenali"
            if finger_count == 0:
                gesture = "Batu"
            elif finger_count == 2:
                gesture = "Gunting"
            elif finger_count == 5:
                gesture = "Kertas"


    # Tampilkan jumlah jari
    cv2.putText(frame, f"Jari terbuka: {finger_count}", (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
    
    cv2.putText(frame, f"Gesture: {gesture}", (10, 100),
            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)

    cv2.imshow("RPS Hand Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
