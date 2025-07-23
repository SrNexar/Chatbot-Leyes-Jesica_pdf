from fastapi import APIRouter, HTTPException
from database import db
from datetime import datetime

router = APIRouter()

@router.get("/notificacionCaso")
async def notificacion_caso():
    try:
        pipeline = [
            {
                "$lookup": {
                    "from": "resolucion",
                    "localField": "caso_id",
                    "foreignField": "_id",
                    "as": "resolucion_info"
                }
            },
            {
                "$unwind": "$resolucion_info"
            },
            {
                "$project": {
                    "_id": 0,
                    "denunciante_id": "$resolucion_info.denunciante_id",
                    "device_id": "$resolucion_info.device_id",
                    "fecha_hora": 1,
                    "razon_sentencia": 1,
                    "veredicto": 1,
                    "lugar_reclusion": 1,
                    "conclusion": 1,
                    "fecha_creacion": 1
                }
            }
        ]

        resultados = await db.sentenciaCopy.aggregate(pipeline).to_list(length=10)

        for doc in resultados:
            fecha_creacion = doc.get("fecha_creacion")
            if fecha_creacion and isinstance(fecha_creacion, dict) and "$date" in fecha_creacion:
                fecha_ms = int(fecha_creacion["$date"]["$numberLong"])
                doc["fecha_creacion"] = datetime.fromtimestamp(fecha_ms / 1000).isoformat()

        return resultados

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener la notificación del caso: {str(e)}")
