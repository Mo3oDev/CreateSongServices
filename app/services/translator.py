from transformers import pipeline
from app.utils.logger import log_event

# Carga el pipeline una vez
translator = pipeline("translation_en_to_es", model="Helsinki-NLP/opus-mt-en-es")

async def traducir_texto(texto: str) -> str:
    """
    Traduce texto de inglés a español usando transformers.
    """
    log_event(f"[Translator] Traduciendo texto: {texto[:20]}...")
    try:
        result = translator(texto, max_length=512)
        trad = result[0]["translation_text"]
        log_event(f"[Translator] Traducción completada: {trad[:50]}...")
        return trad
    except Exception as e:
        log_event(f"[Translator] Error: {e}")
        raise