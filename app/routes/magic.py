from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from app.services import transcriber, translator, generator
from app.models.schemas import SongRequest
import os
from app.core.config import UPLOAD_FOLDER, CALLBACK_BASE_URL
from app.utils.logger import log_event

router = APIRouter()

@router.post("/magic", summary="Transcribe, translate, and generate song from audio file", tags=["Magic"])
async def magic_song(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    style: str = File("Pop"),
    title: str = File("CancionGenerada")
):
    """
    1) Recibe un archivo MP3, 2) transcribe el audio, 3) traduce el texto al inglés, 4) encola generación de canción,
    5) retorna el ID de la canción y un endpoint para consulta de estado o descarga futura.
    """
    # Validación de tipo
    if file.content_type != "audio/mpeg":
        raise HTTPException(status_code=400, detail="El archivo debe ser un MP3")

    # 1. Leer bytes
    audio_bytes = await file.read()

    # 2. Transcribir
    texto = await transcriber.transcribir_audio(audio_bytes, language="en")
    if not texto.strip():
        raise HTTPException(status_code=400, detail="No se pudo transcribir el audio")

    # 3. Traducir a inglés
    try:
        texto_en = await translator.traducir_texto(texto)
    except Exception:
        texto_en = texto

    # 4. Preparar solicitud y encolar generación
    req_data = SongRequest(
        prompt=texto_en,
        style=style,
        title=title
    )
    song_id, callback_url = generator.iniciar_generacion(req_data, background_tasks)

    # Esperar a que el archivo esté disponible (máx 60s)
    import time
    filename = title.replace(" ", "_").replace("/", "-") + ".mp3"
    path = os.path.join(UPLOAD_FOLDER, filename)
    timeout = 120
    waited = 0
    while waited < timeout:
        if os.path.exists(path):
            break
        time.sleep(2)
        waited += 2
    if not os.path.exists(path):
        return JSONResponse({
            "success": False,
            "song_id": song_id,
            "message": "La canción aún no está disponible. Intenta descargarla más tarde.",
            "download_url": f"{CALLBACK_BASE_URL}/magic/download/{title}",
            "lyrics": texto_en,
        }, status_code=202)

    # 5. Devolver respuesta con song_id y rutas de consulta
    download_url = f"{CALLBACK_BASE_URL}/magic/download/{title}"
    return JSONResponse({
        "success": True,
        "song_id": song_id,
        "download_url": download_url,
        "lyrics": texto_en,
    })

@router.get("/magic/download/{title}", summary="Descargar canción generada por título", tags=["Magic"])
def magic_download_by_title(title: str):
    """
    Devuelve el archivo MP3 generado si ya existe en disco, buscando por el título.
    """
    log_event(f"Descargando canción por título: {title}")
    filename = title.replace(" ", "_").replace("/", "-") + ".mp3"
    path = os.path.join(UPLOAD_FOLDER, filename)
    log_event(f"Buscando archivo en: {path}")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Archivo no disponible aún")
    return FileResponse(path, media_type="audio/mpeg", filename=filename)

