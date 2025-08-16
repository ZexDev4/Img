from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import base64
import re

app = Flask(__name__)
CORS(app)

PIXELCUT_URL = "https://api2.pixelcut.app"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/upscale", methods=["POST"])
def upscale():
    try:
        # Jika request pakai file upload
        if "image" in request.files:
            image_file = request.files["image"]
            content_data = image_file.read()
        else:
            # Jika request pakai JSON (URL gambar)
            data = request.get_json()
            q = data.get("url") if data else None
            if not q:
                return jsonify({"error": "URL gambar wajib diisi"}), 400

            url_pattern = re.compile(r"^https?://")
            if url_pattern.match(q):
                try:
                    content_data = requests.get(q, timeout=30).content
                except Exception as e:
                    return jsonify({"error": f"Gagal ambil gambar dari URL: {str(e)}"}), 400
            else:
                try:
                    content_data = base64.b64decode(q)
                except Exception:
                    return jsonify({"error": "Base64 tidak valid"}), 400

        # Kirim ke Pixelcut API Upscale
        files = {
            "image": ("image.png", content_data, "image/png"),
            "scale": (None, "2"),
        }
        headers = {
            "authority": "api2.pixelcut.app",
            "accept": "application/json",
            "origin": "https://www.pixelcut.ai",
            "referer": "https://www.pixelcut.ai/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/124.0.0.0 Safari/537.36",
            "x-client-version": "web",
            "x-locale": "en",
        }

        response = requests.post(
            f"{PIXELCUT_URL}/image/upscale/v1",
            headers=headers,
            files=files,
            timeout=60
        )

        if response.status_code == 200:
            result_url = response.json().get("result_url")
            if result_url:
                return jsonify({"image": result_url})

        return jsonify({
            "error": "Upscale gagal",
            "details": response.text
        }), 500

    except Exception as e:
        return jsonify({"error": "Terjadi error internal", "details": str(e)}), 500


@app.route("/api/removebg", methods=["POST"])
def removebg():
    try:
        # Jika request pakai file upload
        if "image" in request.files:
            image_file = request.files["image"]
            content_data = image_file.read()
        else:
            # Jika request pakai JSON (URL gambar)
            data = request.get_json()
            q = data.get("url") if data else None
            if not q:
                return jsonify({"error": "URL gambar wajib diisi"}), 400

            url_pattern = re.compile(r"^https?://")
            if url_pattern.match(q):
                try:
                    content_data = requests.get(q, timeout=30).content
                except Exception as e:
                    return jsonify({"error": f"Gagal ambil gambar dari URL: {str(e)}"}), 400
            else:
                try:
                    content_data = base64.b64decode(q)
                except Exception:
                    return jsonify({"error": "Base64 tidak valid"}), 400

        # Kirim ke Pixelcut API Remove BG
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.6815.83 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'id,en-US;q=0.7,en;q=0.3',
            'x-client-version': 'web',
            'x-locale': 'en',
            'Origin': 'https://www.pixelcut.ai',
            'Connection': 'keep-alive',
            'Referer': 'https://www.pixelcut.ai/',
        }

        files = {
            'image': ('blob', content_data, 'image/jpeg'),
            'format': (None, 'png'),
            'model': (None, 'v1'),
        }

        response = requests.post(
            f"{PIXELCUT_URL}/image/matte/v1",
            headers=headers,
            files=files,
            timeout=60
        )

        if response.status_code == 200:
            # Kembalikan image PNG langsung
            return response.content, 200, {'Content-Type': 'image/png'}

        return jsonify({
            "error": "Remove background gagal",
            "details": response.text
        }), 500

    except Exception as e:
        return jsonify({"error": "Terjadi error internal", "details": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
