import os
import requests
from flask import Flask, request
from together import Together

app = Flask(__name__)

# --- CONFIGURACIÓN ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
TOGETHER_API_KEY = os.environ.get("TOGETHER_API_KEY", "").strip()

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
BASE_FILE_URL = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}"

# 1. Inicializamos el cliente como tú indicaste
client = Together(api_key=TOGETHER_API_KEY)

@app.route('/')
def index():
    return "GÉNESIS (Together Stream): ONLINE 🌊", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    datos = request.get_json(force=True, silent=True)
    if not datos or "message" not in datos:
        return "OK", 200

    chat_id = datos["message"]["chat"]["id"]

    # --- LÓGICA DE VISIÓN ---
    if "photo" in datos["message"]:
        requests.post(f"{BASE_URL}/sendChatAction", json={"chat_id": chat_id, "action": "typing"})

        try:
            # Obtener URL de la foto
            foto_hd = datos["message"]["photo"][-1]
            file_id = foto_hd["file_id"]
            
            r_path = requests.get(f"{BASE_URL}/getFile?file_id={file_id}")
            resp_path = r_path.json()
            
            if not resp_path.get("ok"):
                raise Exception("Error ruta Telegram")

            file_path = resp_path["result"]["file_path"]
            url_imagen = f"{BASE_FILE_URL}/{file_path}"

            # 2. TU CÓDIGO (Adaptado para Visión)
            # Usamos stream=True como pediste
            response = client.chat.completions.create(
                model="meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Describe esta imagen en español."},
                            {"type": "image_url", "image_url": {"url": url_imagen}}
                        ]
                    }
                ],
                stream=True  # <--- TU REQUISITO
            )

            # 3. ACUMULADOR DE STREAM
            # Como Telegram no acepta texto letra por letra, lo juntamos aquí
            texto_completo = ""
            
            for token in response:
                if hasattr(token, 'choices'):
                    delta = token.choices[0].delta.content
                    if delta:
                        texto_completo += delta  # Vamos pegando las letras

            # 4. ENVIAR RESULTADO FINAL
            requests.post(f"{BASE_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": f"👁️ **Análisis (Stream):**\n\n{texto_completo}",
                "parse_mode": "Markdown"
            })

        except Exception as e:
            requests.post(f"{BASE_URL}/sendMessage", json={
                "chat_id": chat_id, 
                "text": f"❌ Error: {str(e)}"
            })
        
        return "OK", 200

    # Si es texto normal
    texto = datos["message"].get("text", "")
    if texto:
        requests.post(f"{BASE_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": "Manda foto 📸"
        })

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
