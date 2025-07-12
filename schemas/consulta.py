from pydantic import BaseModel

class ConsultaChat(BaseModel):
    pregunta: str
