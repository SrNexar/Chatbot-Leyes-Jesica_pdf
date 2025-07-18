from fastapi import APIRouter, HTTPException
from schemas.casoAlertas import CasoJudicial
import config.mongo as mongo
import logging

router = APIRouter(prefix="/caso", tags=["caso"])

@router.post("/", status_code=201)
async def crear_caso(caso: CasoJudicial):
    try:
        if mongo.db is None:
            raise HTTPException(status_code=500, detail="DB no conectada")

        caso_dict = caso.dict()
       
        result = await mongo.db.alertas2.insert_one(caso_dict)
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
        cursor = mongo.db.alertas2.find()
        async for c in cursor:
            c["id"] = str(c["_id"])
            del c["_id"]
            casos.append(c)
        return casos
    except Exception as e:
        logging.error(f"Error listando casos: {e}")
        raise HTTPException(status_code=500, detail="Error listando casos")
