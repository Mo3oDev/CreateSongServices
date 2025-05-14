import os
import uuid
import requests
from datetime import datetime
from fastapi import BackgroundTasks
from app.utils.logger import log_event
from app.core.config import SUNO_ENDPOINT, SUNO_API_KEY

# Estado en memoria (puedes reemplazar con DB)
song_status = []


def iniciar_generacion(request_data, background_tasks: BackgroundTasks):
    """
    Inicia la generación de la canción en segundo plano.
    Retorna (song_id, callback_url).
    """
    song_id = str(uuid.uuid4())
    song_status.append({
        "id": song_id,
        "prompt": request_data.prompt,
        "style": request_data.style,
        "title": request_data.title,
        "status": "pending",
        "progress": 0.0,
        "timestamp": datetime.now().isoformat()
    })

    payload = request_data.dict(exclude_unset=True)
    # Forzar valores por defecto requeridos por SUNO
    if payload.get("instrumental") is None:
        payload["instrumental"] = False
    if payload.get("customMode") is None:
        payload["customMode"] = True
    if payload.get("model") is None:
        payload["model"] = "V3_5"
    if payload.get("duration") is None:
        payload["duration"] = 45
    payload["model"] = request_data.model or "V3_5"
    payload["callBackUrl"] = f"{os.getenv('CALLBACK_BASE_URL')}/callback"

    background_tasks.add_task(_process_song_generation, song_id, payload)
    return song_id, payload["callBackUrl"]


def _process_song_generation(song_id: str, payload: dict):
    """
    Función que envía el payload a la API de Suno y actualiza el estado.
    """
    song_item = next((it for it in song_status if it["id"] == song_id), None)
    if song_item:
        song_item.update({"status": "processing", "callbackType": "processing", "progress": 0.0})

    headers = {
        "Authorization": f"Bearer {SUNO_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    try:
        log_event(f"[Generator] Enviando a Suno: {payload}")
        resp = requests.post(SUNO_ENDPOINT, headers=headers, json=payload)
        log_event(f"[Generator] Respuesta Suno: {resp.status_code} - {resp.text}")

        if resp.status_code != 200:
            if song_item:
                song_item.update({"status": "failed", "callbackType": "failed", "audio_url": resp.text})
            return

        task_id = resp.json().get("data", {}).get("taskId")
        if song_item and task_id:
            song_item.update({"taskId": task_id})
            log_event(f"[Generator] Task iniciado ID: {task_id}")
    except Exception as e:
        log_event(f"[Generator] Error interno: {e}")
        if song_item:
            song_item.update({"status": "failed", "callbackType": "failed", "audio_url": str(e)})

