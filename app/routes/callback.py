from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from app.services.generator import song_status
from app.utils.logger import log_event
from app.core.config import UPLOAD_FOLDER
import os
import json
import requests

router = APIRouter()

@router.get("/songs", summary="Obtener estado de todas las canciones", tags=["Callback"])
def get_all_songs():
    """Devuelve el estado de todas las canciones generadas."""
    return {"songs": song_status}

@router.post("/callback", summary="Callback de SunoAPI", tags=["Callback"])
async def suno_callback(request: Request):
    """Procesa el callback recibido desde Suno con los resultados de la canción"""
    try:
        data = await request.json()
        log_event(f"Callback recibido: {json.dumps(data)}")

        # Buscar task_id en la estructura principal o anidada
        task_id = (
            data.get("taskId") or
            data.get("task_id") or
            data.get("data", {}).get("taskId") or
            data.get("data", {}).get("task_id") or
            data.get("callback", {}).get("data", {}).get("task_id")
        )
        # Buscar status y audio_url
        callback_type = (
            data.get("callbackType") or
            data.get("data", {}).get("callbackType") or
            data.get("callback", {}).get("data", {}).get("callbackType")
        )
        audio_url = None
        title = None
        # Buscar en items si existen (ajustado para data['data']['data'] también)
        canciones = data.get("callback", {}).get("data", {}).get("items")
        if not canciones and isinstance(data.get("data", {}).get("data"), list):
            canciones = data["data"]["data"]
        if canciones:
            # Buscar la canción cuyo id coincida con el task_id, si no, usar la primera
            primera = next((c for c in canciones if c.get("id") == task_id), None) or canciones[0]
            audio_url = primera.get("audio_url") or primera.get("stream_audio_url")
            title = primera.get("title", "sin_nombre")
        # Fallback
        if not audio_url:
            audio_url = data.get("audio_url")
        if not title:
            title = data.get("title", "sin_nombre")

        # Actualizar estado interno si existe
        song = next((s for s in song_status if s.get("taskId") == task_id), None)
        if song:
            song.update({
                "status": callback_type or song.get("status"),
                "audio_url": audio_url or song.get("audio_url"),
                "callbackType": callback_type or song.get("callbackType")
            })
            log_event(f"[Callback] Actualizado id={song['id']} status={callback_type} audio_url={audio_url}")
        else:
            log_event(f"[Callback] taskId no encontrado para update: {task_id}")

        # Descargar audio si hay url válida
        if audio_url:
            safe_title = title.replace(" ", "_").replace("/", "-")
            # Crear carpeta si no existe
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            filename = os.path.join(UPLOAD_FOLDER, f"{safe_title}.mp3")
            if not os.path.exists(filename):
                audio_response = requests.get(audio_url)
                if audio_response.status_code == 200:
                    with open(filename, "wb") as f:
                        f.write(audio_response.content)
                    log_event(f"Canción guardada: {filename}")
                else:
                    log_event(f"Error al descargar audio: {audio_response.status_code}")
        else:
            log_event("No se encontró stream_audio_url ni audio_url")

        return {"success": True}
    except Exception as e:
        log_event(f"Error en callback: {e}")
        raise HTTPException(status_code=500, detail=str(e))
