import os
from dotenv import load_dotenv
from pathlib import Path

# Cargar archivo .env si existe
dotenv_path = Path(".env")
if dotenv_path.exists():
    load_dotenv(dotenv_path)
else:
    print("⚠️ No se encontró archivo .env")


# Variables de entorno requeridas
SUNO_API_KEY = os.getenv("SUNO_API_KEY")
print(f"🔑 SUNO_API_KEY: {SUNO_API_KEY}")

SUNO_ENDPOINT = os.getenv("SUNO_ENDPOINT", "https://apibox.erweima.ai/api/v1/generate")

PORT = int(os.getenv("PORT", 8000))  # Default: 8000

# Carpeta donde se guardan los audios
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "canciones")

# URL base para callbacks (lo maneja ngrok en runtime)
CALLBACK_BASE_URL = os.getenv("CALLBACK_BASE_URL", "http://localhost")
