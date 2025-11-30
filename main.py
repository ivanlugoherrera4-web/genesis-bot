import os
import requests
import random
from flask import Flask, request

app = Flask(__name__)

# CONFIGURACIÓN
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN").strip()
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# Frases para cuando NO piden foto
FRASES = [
    "Eres mi pixel favorito.",
    "Contigo mi ping es de 0ms.",
    "Eres la CSS de mi HTML.",
    "Te quiero más que al Wi-Fi gratis."
]

@app.route('/')
def index():
    return "Bot Multimedia: ONLINE 📸", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    datos = request.get_json(force=True, silent=True)
    if not datos or "message" not in datos:
        return "OK", 200

    chat_id = datos["message"]["chat"]["id"]
    texto = datos["message"].get("text", "").lower() # Convertimos a minúsculas
    
    # --- LÓGICA DE COMANDOS ---
    
    # CASO 1: El usuario pide una FOTO (/foto)
    if "/foto" in texto:
        # Generamos un número al azar para que la foto cambie siempre
        aleatorio = random.randint(1, 1000)
        url_imagen = f"https://picsum.photos/seed/{aleatorio}/400/300"
        
        # Usamos el método sendPhoto
        url_api = f"{BASE_URL}/sendPhoto"
        payload = {
            "chat_id": chat_id,
            "photo": url_imagen,
            "caption": "Aquí tienes tu imagen aleatoria 🎨" # Pie de foto opcional
        }
        requests.post(url_api, json=payload)

    # CASO 2: Cualquier otra cosa (Respondemos con frase)
    else:
        frase = random.choice(FRASES)
        url_api = f"{BASE_URL}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": frase
        }
        requests.post(url_api, json=payload)

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
