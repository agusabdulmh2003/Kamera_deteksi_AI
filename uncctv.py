import cv2
import mediapipe as mp
import json
import requests

# API OpenRouter
API_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Inisialisasi MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# Buka kamera
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # Konversi frame ke RGB untuk MediaPipe
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(frame_rgb)
    
    if results.pose_landmarks:
        # Ambil koordinat landmark tubuh
        landmarks = results.pose_landmarks.landmark
        pose_data = {i: {"x": lm.x, "y": lm.y, "z": lm.z} for i, lm in enumerate(landmarks)}

        # Ambil koordinat kepala & tangan
        nose = landmarks[0]  # Hidung (indikasi arah kepala)
        left_eye = landmarks[2]  # Mata kiri
        right_eye = landmarks[5]  # Mata kanan
        left_hand = landmarks[15]  # Tangan kiri
        right_hand = landmarks[16]  # Tangan kanan

        # Logika sederhana untuk mendeteksi mencontek
        cheating_detected = False
        warning_text = ""

        # Jika kepala menoleh ke samping secara signifikan
        if abs(nose.x - left_eye.x) > 0.1 or abs(nose.x - right_eye.x) > 0.1:
            cheating_detected = True
            warning_text = "⚠️ Menoleh ke samping!"

        # Jika tangan dekat dengan wajah (indikasi menulis sambil melihat jawaban)
        if abs(nose.y - left_hand.y) < 0.2 or abs(nose.y - right_hand.y) < 0.2:
            cheating_detected = True
            warning_text = "⚠️ Tangan mencurigakan!"

        # Jika gerakan mencurigakan terdeteksi, kirim ke AI
        if cheating_detected:
            try:
                payload = {
                    "model": "anthropic/claude-3-sonnet",
                    "messages": [
                        {"role": "system", "content": "Anda adalah AI yang mendeteksi kecurangan mencontek dalam ujian."},
                        {"role": "user", "content": f"Analisis apakah orang ini sedang mencontek berdasarkan pose: {json.dumps(pose_data)}"}
                    ]
                }

                response = requests.post(API_URL, headers=HEADERS, json=payload)
                response_data = response.json()

                if "choices" in response_data:
                    warning_text = response_data["choices"][0]["message"]["content"]
                else:
                    warning_text = "⚠️ Kecurigaan Mencontek!"

            except Exception as e:
                print("Error:", e)
                warning_text = "⚠️ Tidak dapat mendeteksi!"

        # Tampilkan hasil di layar
        cv2.putText(frame, warning_text[:50], (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    cv2.imshow("Deteksi Mencontek AI", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
