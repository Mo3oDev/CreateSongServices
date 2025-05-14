from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services import transcriber

router = APIRouter()

@router.post("/transcribe", summary="Transcribir audio", tags=["Transcripción"])
async def transcribe_audio(file: UploadFile = File(...)):
    # 1) Validate content-type
    if file.content_type != "audio/mpeg":
        raise HTTPException(status_code=400, detail="El archivo debe ser un MP3")

    # 2) Read raw bytes (this is the crucial 'await')
    audio_bytes = await file.read()

    # 3) Delegate to service; now accepts bytes too
    texto = await transcriber.transcribir_audio(audio_bytes, language="en")
    return {"texto": texto}
