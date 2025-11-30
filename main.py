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

client = Together(api_key=TOGETHER_API_KEY)

@app.route('/')
def index():
    return "GÉNESIS VISION (Qwen): ONLINE 👁️", 200

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
            # 1. Obtener URL de la foto
            foto_hd = datos["message"]["photo"][-1]
            file_id = foto_hd["file_id"]
            
            r_path = requests.get(f"{BASE_URL}/getFile?file_id={file_id}")
            resp_path = r_path.json()
            
            if not resp_path.get("ok"):
                raise Exception("Fallo al obtener ruta de Telegram")

            file_path = resp_path["result"]["file_path"]
            url_imagen = f"{BASE_FILE_URL}/{file_path}"

            # 2. LLAMADA A TOGETHER AI (MODELO QWEN)
            # Este modelo 'Qwen2-VL-72B' es muy estable en Serverless
            response = client.chat.completions.create(
                model="Qwen/Qwen2-VL-72B-Instruct", 
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Describe detalladamente qué ves en esta imagen (en español)."},
                            {"type": "image_url", "image_url": {"url": url_imagen}}
                        ]
                    }
                ],
                max_tokens=500,
                temperature=0.7,
                stream=False
            )

            analisis = response.choices[0].message.content
            
            requests.post(f"{BASE_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": f"👁️ **Análisis Qwen-VL:**\n\n{analisis}",
                "parse_mode": "Markdown"
            })

        except Exception as e:
            error_msg = str(e)
            print(f"Error IA: {error_msg}")
            # Si el error es de modelo, avisamos específicamente
            if "model_not_available" in error_msg:
                texto_error = "⚠️ El modelo de IA está ocupado. Intenta en 1 minuto."
            else:
                texto_error = f"❌ Error: {error_msg}"
                
            requests.post(f"{BASE_URL}/sendMessage", json={
                "chat_id": chat_id, "text": texto_error
            })
        
        return "OK", 200

    # Texto normal
    texto = datos["message"].get("text", "")
    if texto:
        requests.post(f"{BASE_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": "Envíame una foto para probar mi nuevo cerebro Qwen."
        })

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
