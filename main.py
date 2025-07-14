import cv2
import mediapipe as mp
import time
import random

# Inisialisasi MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

# Webcam
cap = cv2.VideoCapture(0)
tip_ids = [4, 8, 12, 16, 20]

# Game state
game_state = "start"
start_time = time.time()
delay = 3
gesture = "-"
computer_choice = "-"
result = "-"

# Draw teks dengan background (biar lebih jelas)
def draw_text(img, text, pos, scale=1.2, color=(255, 255, 255), bg=(0, 0, 0), thickness=2):
    x, y = pos
    (w, h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, scale, thickness)
    cv2.rectangle(img, (x - 10, y - h - 10), (x + w + 10, y + 10), bg, -1)
    cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, scale, color, thickness)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result_mp = hands.process(rgb)
    current_time = time.time()
    elapsed = current_time - start_time

    # --- START SCREEN ---
    if game_state == "start":
        draw_text(frame, "✋ GUNTING BATU KERTAS ✊", (50, 100), 1.3, (0, 255, 255), (50, 50, 50))
        draw_text(frame, "Tekan SPASI atau tunjukkan 1 jari untuk mulai", (50, 180), 0.9, (255, 255, 255), (60, 60, 60))

        if result_mp.multi_hand_landmarks:
            for hand_landmarks in result_mp.multi_hand_landmarks:
                landmarks = hand_landmarks.landmark
                fingers = []
                if landmarks[8].y < landmarks[6].y:
                    fingers.append(1)
                if sum(fingers) == 1:
                    game_state = "countdown"
                    start_time = current_time

    # Alternatif: pakai tombol spasi juga
    key = cv2.waitKey(1)
    if key & 0xFF == ord(' '):
        if game_state == "start":
            game_state = "countdown"
            start_time = current_time
    if key & 0xFF == ord('q'):
        break

    # --- COUNTDOWN ---
    if game_state == "countdown":
        remaining = int(delay - elapsed)
        draw_text(frame, f"Siap-siap dalam: {remaining}", (50, 100), 1.5, (255, 255, 255), (0, 0, 0))

        if remaining <= 0:
            gesture = "Tidak terdeteksi"
            if result_mp.multi_hand_landmarks:
                handedness = result_mp.multi_handedness[0].classification[0].label
                for hand_landmarks in result_mp.multi_hand_landmarks:
                    landmarks = hand_landmarks.landmark
                    fingers = []
                    if handedness == "Right":
                        fingers.append(1 if landmarks[4].x < landmarks[3].x else 0)
                    else:
                        fingers.append(1 if landmarks[4].x > landmarks[3].x else 0)
                    for i in range(1, 5):
                        fingers.append(1 if landmarks[tip_ids[i]].y < landmarks[tip_ids[i] - 2].y else 0)
                    finger_count = sum(fingers)
                    if finger_count == 0:
                        gesture = "Batu"
                    elif finger_count == 2:
                        gesture = "Gunting"
                    elif finger_count == 5:
                        gesture = "Kertas"

            computer_choice = random.choice(["Batu", "Gunting", "Kertas"])
            if gesture == computer_choice:
                result = "Seri 🤝"
            elif (
                (gesture == "Batu" and computer_choice == "Gunting") or
                (gesture == "Gunting" and computer_choice == "Kertas") or
                (gesture == "Kertas" and computer_choice == "Batu")
            ):
                result = "Kamu Menang! 🎉"
            else:
                result = "Kamu Kalah 😭"

            game_state = "show_result"
            start_time = current_time

    # --- TAMPILKAN HASIL ---
    elif game_state == "show_result":
        draw_text(frame, f"Kamu: {gesture}", (50, 100), 1.2, (0, 255, 0))
        draw_text(frame, f"Komputer: {computer_choice}", (50, 160), 1.2, (255, 255, 0))
        draw_text(frame, f"Hasil: {result}", (50, 230), 1.5, (0, 255, 255), (30, 30, 30))

        if elapsed > 2.5:
            game_state = "countdown"
            start_time = current_time

    # --- Tampilkan frame ---
    cv2.imshow("Gunting Batu Kertas", frame)

cap.release()
cv2.destroyAllWindows()
