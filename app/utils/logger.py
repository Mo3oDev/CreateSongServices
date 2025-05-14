import os
from datetime import datetime
from pathlib import Path

LOGS_DIR = Path("logs")

def log_event(message: str):
    """Escribe un mensaje en el log diario con timestamp"""
    try:
        LOGS_DIR.mkdir(exist_ok=True)  # Crea carpeta si no existe

        fecha = datetime.now().strftime("%Y-%m-%d")
        hora = datetime.now().strftime("%H:%M:%S")
        nombre_archivo = LOGS_DIR / f"log_{fecha}.txt"

        with open(nombre_archivo, "a", encoding="utf-8") as log_file:
            log_file.write(f"[{hora}] {message}\n")

    except Exception as e:
        print(f"❌ Error al escribir en el log: {e}")
