import os
import requests
import random  # <--- Importamos el módulo del azar
from flask import Flask, request

app = Flask(__name__)

# CONFIGURACIÓN
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN").strip()
URL_TELEGRAM = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

# --- TUS 10 FRASES DE AMOR ---
# Puedes editar el texto dentro de las comillas como tú quieras
FRASES_DE_AMOR = [
    "Eres mi notificación favorita. ❤️",
    "Mi mundo es mejor porque tú estás en él.",
    "Si fueras un error de código, no te corregiría nunca.",
    "Pienso en ti en cada línea de código que escribo.",
    "Eres la dueña de mi corazón y de mis servidores.",
    "Contigo tengo conexión estable y latencia cero. ⚡",
    "Te quiero más que a un viernes sin errores.",
    "Eres mi constante en un mundo de variables.",
    "Tu sonrisa reinicia mi sistema.",
    "Haces que mi corazón vaya a 1000 iteraciones por segundo."
]

@app.route('/')
def index():
    return "Bot Cupido: ONLINE 💘", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    # 1. Recibir datos
    datos = request.get_json(force=True, silent=True)
    if not datos or "message" not in datos:
        return "OK", 200

    chat_id = datos["message"]["chat"]["id"]
    
    # 2. ELIJE UNA FRASE AL AZAR
    mensaje_romantico = random.choice(FRASES_DE_AMOR)

    # 3. Enviar la frase
    payload = {
        "chat_id": chat_id,
        "text": mensaje_romantico
    }
    requests.post(URL_TELEGRAM, json=payload)

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
