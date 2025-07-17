from fastapi import APIRouter, HTTPException
from schemas.caso import Caso
import config.mongo as mongo
import logging
from pydantic import BaseModel
import requests

router = APIRouter(prefix="/caso", tags=["caso"])

# Clase para la consulta al chatbot
class ConsultaChat(BaseModel):
    pregunta: str

# Función para consultar al chatbot con los datos de MongoDB
async def consultar_chat_con_transcripcion(transcripcion_audio: str, transcripcion_video: str) -> dict:
    # Enviar al endpoint de consulta del chatbot
    try:
        url_chatbot = "http://localhost:8000/chat"  # URL del endpoint del chatbot
        pregunta = f"Audio: {transcripcion_audio} \n Video: {transcripcion_video}"
        
        # Realizamos la consulta POST con la pregunta combinada
        response = requests.post(url_chatbot, json={"pregunta": pregunta})
        
        # Retornar la respuesta del chatbot
        return response.json()
    except Exception as e:
        logging.error(f"Error al consultar el chatbot: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al consultar el chatbot")

@router.post("/", status_code=201)
async def crear_caso(caso: Caso):
    try:
        if mongo.db is None:
            raise HTTPException(status_code=500, detail="DB no conectada")
        
        caso_dict = caso.dict()
        caso_dict["enlace_fuente"] = str(caso_dict["enlace_fuente"])

        # Guardamos el caso en la base de datos
        result = await mongo.db.caso.insert_one(caso_dict)

        # Almacenamos las transcripciones de audio y video
        transcripcion_audio = caso_dict.get("transcripción_de_audio", "")
        transcripcion_video = caso_dict.get("transcripción_de_video", "")

        # Llamamos a la función para consultar el chatbot con las transcripciones
        chatbot_respuesta = await consultar_chat_con_transcripcion(transcripcion_audio, transcripcion_video)

        # Respondemos con el ID del caso y la respuesta del chatbot
        return {"id": str(result.inserted_id), "chatbot_respuesta": chatbot_respuesta}

    except Exception as e:
        logging.error(f"Error creando caso: {e}")
        raise HTTPException(status_code=500, detail="Error creando caso")

@router.get("/")
async def listar_casos():
    try:
        if mongo.db is None:
            raise HTTPException(status_code=500, detail="DB no conectada")
        
        casos = []
        cursor = mongo.db.caso.find()
        
        async for c in cursor:
            c["id"] = str(c["_id"])
            del c["_id"]
            casos.append(c)
        
        return casos
    except Exception as e:
        logging.error(f"Error listando casos: {e}")
        raise HTTPException(status_code=500, detail="Error listando casos")
