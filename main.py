import os
import requests
from flask import Flask, request

app = Flask(__name__)

# CONFIGURACIÓN
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN").strip()
URL_TELEGRAM = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

@app.route('/')
def index():
    return "Bot Hola Mundo: ACTIVO", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    # 1. Recibir la información de Telegram
    datos = request.get_json(force=True, silent=True)
    
    # Si no es un mensaje válido, no hacemos nada
    if not datos or "message" not in datos:
        return "OK", 200

    # 2. Obtener el ID del chat (para saber a quién responder)
    chat_id = datos["message"]["chat"]["id"]

    # 3. ENVIAR "HOLA MUNDO" (Sin pensar, respuesta directa)
    payload = {
        "chat_id": chat_id,
        "text": "Hola Mundo"
    }
    
    requests.post(URL_TELEGRAM, json=payload)

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
