from fastapi import APIRouter, HTTPException
from schemas.caso import Caso
import config.mongo as mongo
import logging

router = APIRouter(prefix="/caso", tags=["caso"])

@router.post("/", status_code=201)
async def crear_caso(caso: Caso):
    try:
        if mongo.db is None:
            raise HTTPException(status_code=500, detail="DB no conectada")
        caso_dict = caso.dict()
        # Convertir HttpUrl a str antes de guardar en Mongo
        caso_dict["enlace_fuente"] = str(caso_dict["enlace_fuente"])
        result = await mongo.db.caso.insert_one(caso_dict)
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
        cursor = mongo.db.caso.find()
        async for c in cursor:
            c["id"] = str(c["_id"])
            casos.append(c)
        return casos
    except Exception as e:
        logging.error(f"Error listando casos: {e}")
        raise HTTPException(status_code=500, detail="Error listando casos")
