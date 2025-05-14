from pydantic import BaseModel
from typing import List, Optional


class SongRequest(BaseModel):
    prompt: str
    style: Optional[str] = None
    title: Optional[str] = None
    customMode: Optional[bool] = True
    instrumental: Optional[bool] = False
    model: Optional[str] = "V3_5"
    duration: Optional[int] = 45
    tempo: Optional[int] = None
    key: Optional[str] = None
    voice_presets: Optional[List[str]] = None
    negativeTags: Optional[str] = None


class SongStatus(BaseModel):
    id: str
    prompt: str
    title: Optional[str]
    style: Optional[str]
    status: str
    progress: float
    timestamp: str
    audio_url: Optional[str] = None
    taskId: Optional[str] = None
    callbackType: Optional[str] = None

class TranslationRequest(BaseModel):
    texto: str