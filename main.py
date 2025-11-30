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
    return "GÉNESIS VISION (90B): ONLINE 👁️", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    datos = request.get_json(force=True, silent=True)
    if not datos or "message" not in datos:
        return "OK", 200

    chat_id = datos["message"]["chat"]["id"]

    # --- LÓGICA DE VISIÓN ---
    if "photo" in datos["message"]:
        # 1. Avisar al usuario que estamos pensando (Typing...)
        requests.post(f"{BASE_URL}/sendChatAction", json={"chat_id": chat_id, "action": "typing"})

        try:
            # 2. Obtener la URL del archivo
            foto_hd = datos["message"]["photo"][-1]
            file_id = foto_hd["file_id"]
            
            # Pedimos la ruta a Telegram
            r_path = requests.get(f"{BASE_URL}/getFile?file_id={file_id}")
            resp_path = r_path.json()
            
            if not resp_path.get("ok"):
                raise Exception("No pude obtener la ruta de Telegram")

            file_path = resp_path["result"]["file_path"]
            url_imagen = f"{BASE_FILE_URL}/{file_path}"

            # 3. LLAMADA A TOGETHER AI (VISION) 🧠
            # CAMBIO IMPORTANTE: Usamos el modelo 90B que suele estar activo en Serverless
            response = client.chat.completions.create(
                model="meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo", 
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Describe qué ves en esta imagen en español. Sé detallado."},
                            {"type": "image_url", "image_url": {"url": url_imagen}}
                        ]
                    }
                ],
                max_tokens=500,
                temperature=0.7,
                stream=False
            )

            # 4. Extraer la respuesta de la IA
            analisis = response.choices[0].message.content
            
            # 5. Enviar respuesta a Telegram
            requests.post(f"{BASE_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": f"👁️ **Análisis GÉNESIS (90B):**\n\n{analisis}",
                "parse_mode": "Markdown"
            })

        except Exception as e:
            print(f"Error IA: {e}")
            # Enviamos el error al chat para que sepas qué pasó sin mirar logs
            requests.post(f"{BASE_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": f"❌ Error de Sistema: {str(e)}"
            })
        
        return "OK", 200

    # Lógica para texto normal
    texto = datos["message"].get("text", "")
    if texto:
        requests.post(f"{BASE_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": "Envíame una foto para que mis ojos (Llama 3.2 Vision) la analicen."
        })

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
