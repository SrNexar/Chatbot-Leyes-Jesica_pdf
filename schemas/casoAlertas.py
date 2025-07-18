from pydantic import BaseModel
from typing import List

class Coordenadas(BaseModel):
    latitude: float
    longitude: float

class Dispositivo(BaseModel):
    duracionVideo: int
    fecha: str
    hora: str
    nivelConfianza: float
    nombrePolicia: str
    palabrasClave: List[str]
    pnc: str
    rango: str
    ubicacion: str
    codigoDelito: str
    user: str

class CasoJudicial(BaseModel):
    alerta: str
    coordenadas: Coordenadas
    descripcion: str
    dispositivo: Dispositivo

