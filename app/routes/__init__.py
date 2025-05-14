from fastapi import APIRouter
from fastapi.responses import JSONResponse
from .generator import router as generator_router
from .transcriber import router as transcriber_router
from .translate import router as translate_router
from .callback import router as callback_router
from .magic import router as magic_router

api_router = APIRouter()

@api_router.get("/", summary="API Documentation", tags=["Documentation"])
def api_documentation():
    return JSONResponse({
        "message": "Bienvenido a la API de Servicios de Canción.",
        "endpoints": [
            {
                "path": "generator/generator",
                "description": "Generador de canciones",
                "input": {
                    "body": {
                    "prompt": "Texto de la canción (string, requerido)",
                    "style": "estilo de la canción (string, requerido)",
                    "title": "titulo de la canción (string, requerido)",
                    }
                }
            },
            {
                "path": "/transcriber/transcribe",
                "description": "Transcriptor de audio a texto",
                "input": {
                    "form-data": {
                        "file": "Archivo MP3 (audio/mpeg), requerido"
                    }
                }
            },
            {
                "path": "/translate/translate",
                "description": "Traducción de texto",
                "input": {
                    "body": {
                        "texto": "string (requerido)",
                    }
                }
            },
            {"path": "/songs", "description": "Estado de todas las canciones generadas"},
            {
                "path": "/magic/magic",
                "description": "Sube un archivo MP3, transcribe, traduce y genera una canción. Devuelve el archivo MP3 generado.",
                "input": {
                    "form-data": {
                        "file": "Archivo MP3 (audio/mpeg), requerido",
                        "style": "Estilo de la canción (string, opcional, default: Pop)",
                        "title": "Título de la canción (string, opcional, default: CancionGenerada)"
                    }
                },
                "output": {
                    "file": "Archivo MP3 de la canción generada"
                }
            },
        ]
    })

api_router.include_router(generator_router, prefix="/generator", tags=["Generator"])
api_router.include_router(transcriber_router, prefix="/transcriber", tags=["Transcriber"])
api_router.include_router(translate_router, prefix="/translate", tags=["Translate"])
api_router.include_router(callback_router, tags=["Callback"])
api_router.include_router(magic_router, prefix="/magic", tags=["Magic"])
