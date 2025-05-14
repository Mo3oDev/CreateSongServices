import os
from fastapi import FastAPI
from contextlib import asynccontextmanager
from pyngrok import ngrok
from app.utils.logger import log_event
from app.core.config import SUNO_API_KEY, UPLOAD_FOLDER


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manejador de ciclo de vida de la app FastAPI"""

    # === Startup ===
    if not SUNO_API_KEY:
        print("⚠️ ADVERTENCIA: No se encontró SUNO_API_KEY en las variables de entorno")
        print("Por favor, crea un archivo .env con tu API key de Suno")

    port = int(os.getenv("PORT", 8000))
    tunnel = ngrok.connect(port, proto="http", bind_tls=True)
    public_url = tunnel.public_url
    os.environ["CALLBACK_BASE_URL"] = public_url

    print(f"[startup] ngrok túnel público HTTPS: {public_url}")
    log_event("=== Servidor iniciado ===")
    print(f"🎵 API Generador de Canciones iniciado en http://localhost:{port}")
    print(f"📂 Archivos de audio en: {os.path.abspath(UPLOAD_FOLDER)}")
    print(f"📝 Logs en: {os.path.abspath('logs')}")

    yield  # Aquí arranca FastAPI

    # === Shutdown ===
    ngrok.kill()
    log_event("=== Servidor detenido ===")
    print("[shutdown] ngrok terminado")
    print("🚀 Servidor detenido")