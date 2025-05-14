from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.models.schemas import SongRequest
from app.services import generator

router = APIRouter()

@router.post("/generate", summary="Generar canción", tags=["Generador"])
async def generate_song(request_data: SongRequest, background_tasks: BackgroundTasks):
    if not request_data.prompt.strip():
        raise HTTPException(status_code=400, detail="Se requiere un prompt válido")

    song_id, callback_url = generator.iniciar_generacion(request_data, background_tasks)
    
    return {
        "id": song_id,
        "message": "Generación iniciada",
        "callBackUrl": callback_url
    }
