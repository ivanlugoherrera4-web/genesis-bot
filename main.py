import os
import requests
import random
from flask import Flask, request

app = Flask(__name__)

# CONFIGURACIÓN
# Aseguramos que el token esté limpio de espacios
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
BASE_FILE_URL = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}"

@app.route('/')
def index():
    return "Bot Debugger: ONLINE 🕵️‍♂️", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    datos = request.get_json(force=True, silent=True)
    if not datos or "message" not in datos:
        return "OK", 200

    chat_id = datos["message"]["chat"]["id"]

    # CASO: FOTO DETECTADA
    if "photo" in datos["message"]:
        foto_hd = datos["message"]["photo"][-1]
        file_id = foto_hd["file_id"]
        
        # 1. Pedir ruta a Telegram
        r_path = requests.get(f"{BASE_URL}/getFile?file_id={file_id}")
        resp_path = r_path.json()
        
        print(f"🔍 DEBUG TELEGRAM RESPUESTA: {resp_path}") # <--- ESTO SALDRÁ EN LOS LOGS

        if resp_path.get("ok"):
            file_path = resp_path["result"]["file_path"]
            
            # 2. Construir URL
            url_descarga = f"{BASE_FILE_URL}/{file_path}"
            
            print(f"🔗 URL GENERADA: {url_descarga}") # <--- ESTO TAMBIÉN
            
            mensaje = f"Link generado:\n{url_descarga}"
        else:
            mensaje = f"❌ Error de Telegram: {resp_path}"

        requests.post(f"{BASE_URL}/sendMessage", json={
            "chat_id": chat_id, "text": mensaje
        })
        return "OK", 200

    # RESPUESTA SIMPLE PARA QUE NO SE QUEDE CALLADO
    requests.post(f"{BASE_URL}/sendMessage", json={
        "chat_id": chat_id, "text": "Envíame una foto para probar."
    })

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
