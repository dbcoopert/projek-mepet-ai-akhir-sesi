from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
# import os

app = Flask(__name__, static_folder="static")
CORS(app)

GROQ_API_KEY = "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"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Riwayat chat
chat_history = []

# Data Produk Laptop
produk_laptops = [
    {
        "nama": "Asus ROG Strix Scar 18 (2025)",
        "deskripsi": "Laptop monster 18 inci layar Mini-Led 240hz, performa ekstream dari intel ultra 9 & RTX 5090, cocok untuk gamer dan kreator",
        "gambar": "/backend/static/images/asusrog.jpg",
        "harga": "75.000.000",
        "url": "../public/asus-rog.html"
    },
    {
        "nama": "Razer Blade 16 (2025)",
        "deskripsi": "Laptop premium super tipis dengan layar OLED QHD+ 240Hz dan GPU RTX 5090. Cocok untuk pengguna mobile yang tetap ingin power tinggi.",
        "gambar": "/backend/static/images/razerblade.jpg",
        "harga": "67.000.000",
        "url": "../public/raizer-blade.html"
    },
    {
        "nama": "MSI Raider / Titan 18 HX AI",
        "deskripsi": "Laptop high-end 18 inci dengan layar 4K Mini-LED, CPU Intel Ultra 9, dan GPU RTX 5080. Performa untuk gaming dan AI.",
        "gambar": "/backend/static/images/msiraider.jpg",
        "harga": "56.000.000",
        "url": "../public/msi-raider.html"
    },
    {
        "nama": "Alienware m18 R1",
        "deskripsi": "Laptop gaming flagship dari Dell, layar QHD+ 480Hz dan GPU RTX 50-series. Desain solid dan khas Alienware.",
        "gambar": "/backend/static/images/alienwar.jpg",
        "harga": "68.000.000",
        "url": "../public/alienware.html"
    },
    {
        "nama": "Lenovo Legion Pro 7i (Gen 10)",
        "deskripsi": "Laptop flagship 16 inci dengan RTX 5090 dan layar OLED. Build kokoh dan performa stabil, cocok untuk game & pekerjaan berat.",
        "gambar": "/backend/static/images/lenovolegion.jpg",
        "harga": "44.000.000",
        "url": "../public/lenovo-legion.html"
    }
]

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "").strip()

        # Tambahkan ke riwayat chat
        chat_history.append({"role": "user", "content": user_message})

        # Cek apakah menyebut salah satu produk
        produk_ditemukan = None
        for produk in produk_laptops:
            if produk["nama"] in user_message:
                produk_ditemukan = produk
                break

        if produk_ditemukan:
            reply = (
                f"<strong>{produk_ditemukan['nama']}</strong><br>"
                f"{produk_ditemukan['deskripsi']}<br><br>"
                f"<img src='{produk_ditemukan['gambar']}' width='100%'/><br>"
                f"Rp.{produk_ditemukan['harga']}<br>"
                f"<a href='{produk_ditemukan['url']}' style='color: blue;'>Lihat detail produk</a>"
            )
            chat_history.append({"role": "assistant", "content": reply})
            return jsonify({"reply": reply})

        # klo gda ditangani ai
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        daftar_produk_text = "\n".join(
        [f"{p['nama']}: {p['deskripsi']}" for p in produk_laptops]
        )
        
        system_prompt = (
        "Kamu adalah asisten toko laptop yang membantu pelanggan, respon dalam bahasa indonesia! dan hanya menjawab perihal yang ada di toko ini selain dari itu jangan"
        "Berikut daftar produk kami:\n" + daftar_produk_text
        )
        
        messages = [{"role": "system", "content": system_prompt}] + chat_history

        body = {
            "model": "llama3-8b-8192",
            "messages": messages,
            "temperature": 0.7
        }

        response = requests.post(GROQ_API_URL, headers=headers, json=body)
        response.raise_for_status()
        ai_reply = response.json()["choices"][0]["message"]["content"]

        chat_history.append({"role": "assistant", "content": ai_reply})
        return jsonify({"reply": ai_reply})

    except Exception as e:
        print("Error:", e)
        return jsonify({"reply": "Maaf, terjadi kesalahan saat menghubungi AI."}), 500


# Serve halaman produk HTML (opsional, bisa lewat templates juga)
@app.route('/produk-asus.html')
def produk_asus():
    return send_from_directory('templates', 'produk-asus.html')

@app.route('/produk-lenovo.html')
def produk_lenovo():
    return send_from_directory('templates', 'produk-lenovo.html')

if __name__ == "__main__":
    app.run(debug=True)
