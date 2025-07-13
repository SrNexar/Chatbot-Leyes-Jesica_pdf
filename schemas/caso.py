from pydantic import BaseModel, HttpUrl

class Caso(BaseModel):
    direccion: str
    interseccion: str
    numero_casa: str
    latitud: str
    longitud: str
    tipo_lugar: str
    sector_punto_referencia: str
    fecha_hecho: str
    hora_aproximada_hecho: str
    enlace_fuente: HttpUrl
    transcripción_de_video: str
    transcripción_de_audio: str