from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from app.services import transcriber, translator, generator
from app.models.schemas import SongRequest
import os
from app.utils.logger import log_event
from app.core.config import UPLOAD_FOLDER

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
    print(f"Request data: {req_data}")

    filename = title.replace(" ", "_").replace("/", "-") + ".mp3"
    path = os.path.join(UPLOAD_FOLDER, filename)
    # Validar si ya existe la canción antes de generar
    if os.path.exists(path):
        log_event(f"Canción ya existe: {path}, no se vuelve a generar.")
        download_url = f"{os.environ.get('CALLBACK_BASE_URL', 'http://localhost')}/magic/download/{title}"
        log_event(f"Archivo descargable en : {download_url}")

        return JSONResponse({
            "success": True,
            "song_id": None,
            "download_url": download_url,
            "lyrics": texto_en,
            "message": "La canción ya existe y no se volvió a generar."
        })

    song_id, callback_url = generator.iniciar_generacion(req_data, background_tasks)

    # Log para depuración
    log_event(f"Generación en background lanzada para archivo: {filename} con song_id: {song_id}")

    # Responder de inmediato, sin esperar el archivo
    download_url = f"{os.environ.get('CALLBACK_BASE_URL', 'http://localhost')}/magic/download/{title}"
    return JSONResponse({
        "success": True,
        "song_id": song_id,
        "download_url": download_url,
        "lyrics": texto_en,
        "message": "La generación de la canción ha sido iniciada. Consulta el estado o descarga más tarde."
    })

@router.get("/download/{title}", summary="Descargar canción generada por título", tags=["Magic"])
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

