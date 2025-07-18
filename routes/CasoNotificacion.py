from fastapi import APIRouter, HTTPException
import config.mongo as mongo
from datetime import datetime
from bson import ObjectId

router = APIRouter()

@router.get("/notificacionCaso")
async def notificacion_caso():
    try:
        pipeline = [
            {
                "$lookup": {
                    "from": "alertas2",
                    "localField": "caso_id_alerta",  # campo en notificacion
                    "foreignField": "_id",           # campo en alertas2
                    "as": "alerta_info"
                }
            },
            {
                "$unwind": "$alerta_info"  
            },
            {
                "$project": {
                    "_id": 0,
                    # Campos de alerta (alertas2)
                    "alerta": "$alerta_info.alerta",
                    "descripcion": "$alerta_info.descripcion",
                     "user": "$alerta_info.dispositivo.user",
                    # Campos de notificacion
                    "fecha_hora": 1,
                    "razon_sentencia": 1,
                    "veredicto": 1,
                    "lugar_reclusion": 1,
                    "conclusion": 1,
                    "fecha_creacion": 1
                }
            }
        ]

        resultados = await mongo.db.notificacion.aggregate(pipeline).to_list(length=10)

        # Convertir fecha_creacion si viene en formato BSON
        for doc in resultados:
            fecha_creacion = doc.get("fecha_creacion")
            if fecha_creacion and isinstance(fecha_creacion, dict) and "$date" in fecha_creacion:
                fecha_ms = int(fecha_creacion["$date"]["$numberLong"])
                doc["fecha_creacion"] = datetime.fromtimestamp(fecha_ms / 1000).isoformat()

        return resultados

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener la notificación del caso: {str(e)}")
