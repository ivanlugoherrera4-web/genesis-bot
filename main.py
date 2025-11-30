import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- CONFIGURACIÓN ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
# Limpiamos el token por si acaso se coló un espacio invisible
if TELEGRAM_TOKEN:
    TELEGRAM_TOKEN = TELEGRAM_TOKEN.strip()

URL_TELEGRAM = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

@app.route('/')
def index():
    return "<h1>GÉNESIS SYSTEM: ONLINE 🟢</h1>", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    # 1. Recibir datos
    try:
        datos = request.get_json(force=True, silent=True)
    except Exception as e:
        print(f"Error leyendo JSON: {e}")
        return "Error", 400
    
    if not datos or "message" not in datos:
        return "OK", 200

    # 2. Extraer información
    try:
        chat_id = datos["message"]["chat"]["id"]
        usuario = datos["message"]["chat"].get("first_name", "Humano")
        texto = datos["message"].get("text", "").lower()
        
        print(f"📩 Mensaje recibido de {usuario}: {texto}")

        # 3. Lógica
        if "hola" in texto:
            respuesta = f"¡Hola {usuario}! GÉNESIS v2 conectada."
        elif "status" in texto:
            respuesta = "Sistemas operativos y estables."
        else:
            respuesta = f"Eco: {texto}"

        # 4. Responder (CON PROTECCIÓN DE ERRORES)
        payload = {"chat_id": chat_id, "text": respuesta}
        
        # Intentamos enviar el mensaje
        r = requests.post(URL_TELEGRAM, json=payload, timeout=5)
        
        # Verificamos si Telegram aceptó el mensaje
        if r.status_code == 200:
            print("✅ Respuesta enviada con éxito.")
        else:
            print(f"⚠️ Error enviando respuesta: {r.status_code} - {r.text}")

    except Exception as e:
        print(f"❌ ERROR CRÍTICO EN EL BOT: {e}")
        # Importante: Devolvemos "OK" a Telegram para que no siga reintentando
        # enviarnos el mismo mensaje que causa error.
        return "OK", 200

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
