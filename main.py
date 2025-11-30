import os
import requests
import random
from flask import Flask, request

app = Flask(__name__)

# CONFIGURACIÓN
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN").strip()

# URL base para COMANDOS (mandar mensajes)
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# URL base para DESCARGAS (ojo al '/file/')
BASE_FILE_URL = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}"

FRASES = [
    "Recibido, cambio y fuera.",
    "Procesando solicitud...",
    "Conexión establecida.",
    "Bits y bytes en orden."
]

@app.route('/')
def index():
    return "Sistema de Enlace de Archivos: ACTIVO 🔗", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    datos = request.get_json(force=True, silent=True)
    if not datos or "message" not in datos:
        return "OK", 200

    chat_id = datos["message"]["chat"]["id"]

    # --- LÓGICA MAESTRA ---

    # CASO 1: FOTO DETECTADA (El Canje del Boleto)
    if "photo" in datos["message"]:
        # 1. Obtener el ID de la foto más grande
        foto_hd = datos["message"]["photo"][-1]
        file_id = foto_hd["file_id"]
        
        # 2. EL HANDSHAKE: Preguntarle a Telegram la ruta (path)
        # Hacemos una petición GET al método getFile
        r_path = requests.get(f"{BASE_URL}/getFile?file_id={file_id}")
        resp_path = r_path.json()
        
        if resp_path["ok"]:
            file_path = resp_path["result"]["file_path"]
            
            # 3. LA URL MÁGICA
            # Construimos el link final combinando la base de archivos + el path
            url_descarga = f"{BASE_FILE_URL}/{file_path}"
            
            mensaje = (
                f"✅ **Enlace Generado**\n\n"
                f"🔗 **Link Directo:**\n{url_descarga}\n\n"
                f"⚠️ *Nota: Este link expira en 1 hora por seguridad de Telegram.*"
            )
        else:
            mensaje = "❌ Error recuperando la ruta del archivo."

        requests.post(f"{BASE_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": mensaje,
            "parse_mode": "Markdown" # Para que se vea bonito con negritas
        })
        
        return "OK", 200

    # CASO 2: TEXTO NORMAL (Frases)
    texto = datos["message"].get("text", "").lower()
    
    if "/foto" in texto:
        # Tu lógica anterior de foto random
        aleatorio = random.randint(1, 1000)
        requests.post(f"{BASE_URL}/sendPhoto", json={
            "chat_id": chat_id,
            "photo": f"https://picsum.photos/seed/{aleatorio}/400/300",
            "caption": "Imagen de prueba generada"
        })
    else:
        # Frase random
        requests.post(f"{BASE_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": random.choice(FRASES)
        })

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
