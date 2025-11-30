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

# Inicializamos el cliente de Together
client = Together(api_key=TOGETHER_API_KEY)

@app.route('/')
def index():
    return "GÉNESIS VISION (Gemma 3n): ONLINE 💎", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    datos = request.get_json(force=True, silent=True)
    if not datos or "message" not in datos:
        return "OK", 200

    chat_id = datos["message"]["chat"]["id"]

    # --- LÓGICA DE VISIÓN ---
    if "photo" in datos["message"]:
        # Avisamos que estamos "escribiendo"
        requests.post(f"{BASE_URL}/sendChatAction", json={"chat_id": chat_id, "action": "typing"})

        try:
            # 1. Obtener URL de la foto desde Telegram
            foto_hd = datos["message"]["photo"][-1]
            file_id = foto_hd["file_id"]
            
            r_path = requests.get(f"{BASE_URL}/getFile?file_id={file_id}")
            resp_path = r_path.json()
            
            if not resp_path.get("ok"):
                raise Exception("Error ruta Telegram")

            file_path = resp_path["result"]["file_path"]
            url_imagen = f"{BASE_FILE_URL}/{file_path}"

            # 2. LLAMADA A TOGETHER AI (MODELO GEMMA 3n)
            # Este es el modelo que encontraste: google/gemma-3n-E4B-it
            response = client.chat.completions.create(
                model="google/gemma-3n-E4B-it", 
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Describe qué ves en esta imagen en español detalladamente."},
                            {"type": "image_url", "image_url": {"url": url_imagen}}
                        ]
                    }
                ],
                max_tokens=500,
                temperature=0.7,
                stream=False
            )

            # 3. Obtener respuesta
            if response.choices:
                analisis = response.choices[0].message.content
                mensaje_final = f"💎 **Análisis Gemma 3n:**\n\n{analisis}"
            else:
                mensaje_final = "⚠️ La IA no devolvió respuesta."

            # 4. Enviar a Telegram
            requests.post(f"{BASE_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": mensaje_final,
                "parse_mode": "Markdown"
            })

        except Exception as e:
            error_msg = str(e)
            print(f"❌ ERROR: {error_msg}")
            
            # Mensaje de error amigable
            requests.post(f"{BASE_URL}/sendMessage", json={
                "chat_id": chat_id, 
                "text": f"❌ Error de Sistema: {error_msg}"
            })
        
        return "OK", 200

    # Lógica para texto normal
    texto = datos["message"].get("text", "")
    if texto:
        requests.post(f"{BASE_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": "Envíame una foto 📸. Quiero probar mis nuevos ojos (Gemma)."
        })

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
