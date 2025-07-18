from pydantic import BaseModel, HttpUrl
from typing import Optional, List

class CasoJudicial(BaseModel):
    denunciante_id: str  
    device_id: str
    device_type: str
    location: str
    alert_information: str
    latitude: float
    longitude: float
    date: str
    time: str
    stream_url: HttpUrl
    transcription_video: str
    transcription_audio: Optional[str]
    media_duration: int
    key_words: List[str]
    confidence_level: float
