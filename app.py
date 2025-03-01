import cv2
import mediapipe as mp
import json
import requests  # Gunakan requests untuk panggilan API

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

        # Debug: Cetak data pose
        print("Pose Data:", json.dumps(pose_data, indent=2))

        # Kirim data ke OpenRouter API
        try:
            payload = {
                "model": "anthropic/claude-3-sonnet",
                "messages": [
                    {"role": "system", "content": "Anda adalah AI yang menganalisis manusia sedang melakukan aktifitas apa  pada gambar atau video yang ada, amati sumua objek yang bersangkutan denga  orang itu dan menghasilkan deskripsi aktivitas."},
                    {"role": "user", "content": f"Berikan deskripsi aktivitas orang berdasarkan gambar atau video yang ada: {json.dumps(pose_data)}"}
                ]
            }

            response = requests.post(API_URL, headers=HEADERS, json=payload)
            response_data = response.json()

            # Debug: Cetak respons API
            print("Response:", response_data)

            if "choices" in response_data:
                activity_description = response_data["choices"][0]["message"]["content"]
            else:
                activity_description = "Gagal mendapatkan deskripsi."

        except Exception as e:
            print("Error:", e)
            activity_description = "Gagal mendapatkan deskripsi."

        # Tampilkan hasil di layar
        cv2.putText(frame, activity_description[:50], (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    cv2.imshow("AI CCTV", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
