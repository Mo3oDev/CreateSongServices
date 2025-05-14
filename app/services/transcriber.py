import io
import os
import uuid
import whisper
from pydub import AudioSegment
from app.utils.logger import log_event
import tempfile

# Load Whisper model once
dev_model = whisper.load_model("large-v3")

def preprocess_audio(input_source, duration_ms=35_000, target_sr=16_000, output_path=None):
    """
    Preprocesa un archivo de audio para Whisper:
      - Recorta duración
      - Convierte a mono
      - Cambia tasa de muestreo
      - Ajusta volumen a -20 dBFS

    input_source puede ser:
      - Ruta a archivo (str)
      - Bytes o BytesIO
    """
    # Init AudioSegment
    if isinstance(input_source, (bytes, bytearray)):
        buffer = io.BytesIO(input_source)
        audio = AudioSegment.from_file(buffer, format="mp3")
    elif isinstance(input_source, io.BytesIO):
        audio = AudioSegment.from_file(input_source, format="mp3")
    else:
        audio = AudioSegment.from_file(input_source)

    # Trim, mono, resample, normalize
    audio = audio[:duration_ms]
    audio = audio.set_channels(1).set_frame_rate(target_sr)
    gain = -20.0 - audio.dBFS
    audio = audio.apply_gain(gain)

    # Determine a safe temp directory
    if not output_path:
        temp_dir = tempfile.gettempdir()
        filename = f"{uuid.uuid4().hex}.wav"
        output_path = os.path.join(temp_dir, filename)

    # Export
    audio.export(output_path, format="wav")
    return output_path

async def transcribir_audio(audio_source, language: str = "en") -> str:
    """
    Transcribe un archivo de audio usando Whisper.
    audio_source puede ser bytes or file path.
    """
    log_event("[Transcriber] Preprocesando audio")
    wav_path = preprocess_audio(audio_source, duration_ms=45_000)

    log_event("[Transcriber] Llamando a Whisper")
    
    result = dev_model.transcribe(wav_path, language=language, task="transcribe")
    text = result.get("text", "").strip()

    # Limpieza
    try:
        os.remove(wav_path)
    except OSError:
        pass

    log_event(f"[Transcriber] Resultado (primeros 50 chars): {text[:50]}...")
    return text
