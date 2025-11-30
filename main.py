import os
import requests
import random
from flask import Flask, request

app = Flask(__name__)

# CONFIGURACIÓN
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN").strip()
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

FRASES = [
    "Eres mi pixel favorito.",
    "Contigo mi ping es de 0ms.",
    "Eres la CSS de mi HTML.",
    "Te quiero más que al Wi-Fi gratis."
]

@app.route('/')
def index():
    return "Bot Detector de Fotos: ONLINE 👁️", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    datos = request.get_json(force=True, silent=True)
    if not datos or "message" not in datos:
        return "OK", 200

    # Extraemos el Chat ID para saber a quién responder
    chat_id = datos["message"]["chat"]["id"]
    
    # --- LÓGICA DE INTELIGENCIA ---

    # CASO 1: ¿El usuario envió una FOTO? (Input de imagen)
    if "photo" in datos["message"]:
        # Telegram envía un array de fotos (thumbnails + original).
        # La última [-1] es siempre la de mayor resolución.
        foto_hd = datos["message"]["photo"][-1]
        id_archivo = foto_hd["file_id"]
        
        # Responde con el ID (Prueba técnica)
        mensaje_respuesta = f"📸 ¡Imagen detectada!\n\n🆔 File ID: {id_archivo}\n\n(Guarda este ID, es la llave para que la IA analice esta foto)."
        
        requests.post(f"{BASE_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": mensaje_respuesta
        })
        
        return "OK", 200

    # Si no es foto, intentamos leer texto
    texto = datos["message"].get("text", "").lower()

    # CASO 2: El usuario pide una FOTO (Comando)
    if "/foto" in texto:
        aleatorio = random.randint(1, 1000)
        url_imagen = f"https://picsum.photos/seed/{aleatorio}/400/300"
        
        requests.post(f"{BASE_URL}/sendPhoto", json={
            "chat_id": chat_id,
            "photo": url_imagen,
            "caption": "Aquí tienes tu imagen aleatoria 🎨"
        })

    # CASO 3: Cualquier otro texto (Chat)
    else:
        frase = random.choice(FRASES)
        requests.post(f"{BASE_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": frase
        })

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
