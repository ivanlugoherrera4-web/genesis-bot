import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- CONFIGURACIÓN ---
# El token lo pondremos en las variables de entorno de Koyeb para seguridad
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
URL_TELEGRAM = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

@app.route('/')
def index():
    # Esto sirve para ver si el servidor está vivo desde el navegador
    return "<h1>GÉNESIS SYSTEM: ONLINE 🟢</h1><p>Bot operando en Koyeb.</p>", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    # 1. Seguridad: Si no hay token configurado, error.
    if not TELEGRAM_TOKEN:
        return jsonify({"error": "Token no configurado"}), 500

    # 2. Recibir datos de Telegram
    try:
        datos = request.get_json(force=True)
    except:
        return "Error JSON", 400
    
    # Si no es un mensaje de texto, lo ignoramos amablemente
    if not datos or "message" not in datos:
        return "OK", 200

    # 3. Extraer información
    chat_id = datos["message"]["chat"]["id"]
    usuario = datos["message"]["chat"].get("first_name", "Humano")
    texto = datos["message"].get("text", "").lower()

    print(f"📩 Mensaje recibido de {usuario}: {texto}")

    # 4. CEREBRO DEL BOT (Tu lógica va aquí)
    if "hola" in texto:
        respuesta = f"¡Hola {usuario}! Soy GÉNESIS v1.0, tu bot serverless."
    elif "status" in texto:
        respuesta = "Sistemas nominales. Ejecutándose en la nube de Koyeb."
    elif "precio" in texto:
        respuesta = "Estoy operando con costo $0.00 MXN."
    else:
        respuesta = f"Recibí: '{texto}'. Aún estoy aprendiendo."

    # 5. Responder a Telegram
    payload = {
        "chat_id": chat_id,
        "text": respuesta
    }
    requests.post(URL_TELEGRAM, json=payload)

    return "OK", 200

# Koyeb inyecta el puerto automáticamente
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
