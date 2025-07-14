import cv2
import mediapipe as mp
import time
import random

# Inisialisasi MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

# Setup game
game_state = "countdown"
start_time = time.time()
delay = 3
gesture = "-"
computer_choice = "-"
result = "-"

# Webcam
cap = cv2.VideoCapture(0)
tip_ids = [4, 8, 12, 16, 20]

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result_mp = hands.process(rgb)

    current_time = time.time()
    elapsed = current_time - start_time

    if game_state == "countdown":
        remaining = int(delay - elapsed)
        cv2.putText(frame, f"Siap-siap dalam: {remaining}", (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)

        if remaining <= 0:
            # Ambil gesture
            gesture = "Tidak terdeteksi"
            if result_mp.multi_hand_landmarks:
                handedness = result_mp.multi_handedness[0].classification[0].label
                for hand_landmarks in result_mp.multi_hand_landmarks:
                    landmarks = hand_landmarks.landmark
                    fingers = []

                    # Jempol
                    if handedness == "Right":
                        fingers.append(1 if landmarks[4].x < landmarks[3].x else 0)
                    else:
                        fingers.append(1 if landmarks[4].x > landmarks[3].x else 0)

                    # Telunjuk–kelingking
                    for i in range(1, 5):
                        fingers.append(1 if landmarks[tip_ids[i]].y < landmarks[tip_ids[i] - 2].y else 0)

                    finger_count = sum(fingers)

                    # Mapping gesture
                    if finger_count == 0:
                        gesture = "Batu"
                    elif finger_count == 2:
                        gesture = "Gunting"
                    elif finger_count == 5:
                        gesture = "Kertas"

            # Komputer pilih
            computer_choice = random.choice(["Batu", "Gunting", "Kertas"])

            # Hitung hasil
            if gesture == computer_choice:
                result = "Seri 🤝"
            elif (
                (gesture == "Batu" and computer_choice == "Gunting") or
                (gesture == "Gunting" and computer_choice == "Kertas") or
                (gesture == "Kertas" and computer_choice == "Batu")
            ):
                result = "Kamu Menang!"
            else:
                result = "Kamu Kalah"

            game_state = "show_result"
            start_time = current_time

    elif game_state == "show_result":
        # Tampilkan hasil
        cv2.putText(frame, f"Gesture: {gesture}", (10, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)
        cv2.putText(frame, f"Komputer: {computer_choice}", (10, 150),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 0), 2)
        cv2.putText(frame, f"Hasil: {result}", (10, 200),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0, 255, 255), 3)

        if elapsed > 2:
            game_state = "countdown"
            start_time = current_time

    # Tampilkan frame
    cv2.imshow("RPS Countdown", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
