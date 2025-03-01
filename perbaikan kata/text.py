from flask import Flask, request, jsonify
import requests
import os
import fitz  # PyMuPDF untuk membaca PDF
from docx import Document
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# API Key OpenRouter
API_KEY = "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"
BASE_URL = "https://openrouter.ai/api/v1"
MODEL = "anthropic/claude-3-sonnet"

# Fungsi untuk mengoreksi teks
def correct_text(text):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "Anda adalah AI yang mengoreksi tata bahasa sesuai PUEBI."},
            {"role": "user", "content": f"""Perbaiki tata bahasa dan ejaan dalam teks berikut:
{text}"""}
        ]
    }
    
    response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload)
    
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return "Gagal mendapatkan koreksi."

# Fungsi membaca dokumen
def read_file(file_path):
    ext = os.path.splitext(file_path)[1]
    text = ""
    
    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    elif ext == ".pdf":
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text("text")
    elif ext == ".docx":
        doc = Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    
    return text

# Route untuk input teks manual
@app.route("/correct", methods=["POST"])
def correct():
    data = request.json
    text = data.get("text", "")
    corrected_text = correct_text(text)
    return jsonify({"corrected_text": corrected_text})

# Route untuk upload file
@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files["file"]
    file_path = os.path.join("uploads", file.filename)
    file.save(file_path)
    
    text = read_file(file_path)
    corrected_text = correct_text(text)
    
    return jsonify({"corrected_text": corrected_text})

if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)
    app.run(debug=True)
