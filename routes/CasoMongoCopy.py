from fastapi import APIRouter, HTTPException
from schemas.casoCopy import CasoJudicial
import config.mongo as mongo
import logging

router = APIRouter(prefix="/caso", tags=["caso"])

@router.post("/", status_code=201)
async def crear_caso(caso: CasoJudicial):
    try:
        if mongo.db is None:
            raise HTTPException(status_code=500, detail="DB no conectada")

        caso_dict = caso.dict()
        # Convertir stream_url (HttpUrl) a str antes de guardar en Mongo
        caso_dict["stream_url"] = str(caso_dict["stream_url"])

        result = await mongo.db.resolucion.insert_one(caso_dict)
        return {"id": str(result.inserted_id)}
    except Exception as e:
        logging.error(f"Error creando caso: {e}")
        raise HTTPException(status_code=500, detail="Error creando caso")

@router.get("/")
async def listar_casos():
    try:
        if mongo.db is None:
            raise HTTPException(status_code=500, detail="DB no conectada")

        casos = []
        cursor = mongo.db.resolucion.find()
        async for c in cursor:
            c["id"] = str(c["_id"])
            del c["_id"]
            casos.append(c)
        return casos
    except Exception as e:
        logging.error(f"Error listando casos: {e}")
        raise HTTPException(status_code=500, detail="Error listando casos")
