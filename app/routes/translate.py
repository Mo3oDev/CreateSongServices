from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services import translator
from app.models.schemas import TranslationRequest

router = APIRouter()

@router.post("/translate", summary="Traducir texto", tags=["Traducción"])
async def translate_text(request: TranslationRequest):
    if not request.texto.strip():
        raise HTTPException(status_code=400, detail="Texto vacío")

    traduccion = await translator.traducir_texto(request.texto)
    return {"traduccion": traduccion}
