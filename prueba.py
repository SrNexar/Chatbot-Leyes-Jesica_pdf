import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime

# Conexión a MongoDB
MONGO_URI = "mongodb+srv://Karina1014:Junio30k.2023@cluster0.zetck.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "UPC"

async def main():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]

    # Pipeline con $lookup
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
        print("📝 Resultado:")
        print(f"- denunciante_id: {doc.get('denunciante_id')}")
        print(f"- device_id: {doc.get('device_id')}")
        print(f"- fecha_hora: {doc.get('fecha_hora')}")
        print(f"- razon_sentencia: {doc.get('razon_sentencia')}")
        print(f"- veredicto: {doc.get('veredicto')}")
        print(f"- lugar_reclusion: {doc.get('lugar_reclusion')}")
        print(f"- conclusion: {doc.get('conclusion')}")

        # Convertir fecha_creacion si existe
        fecha_creacion = doc.get("fecha_creacion")
        if fecha_creacion:
            if isinstance(fecha_creacion, dict) and "$date" in fecha_creacion:
                fecha_ms = int(fecha_creacion["$date"]["$numberLong"])
                fecha_creacion = datetime.fromtimestamp(fecha_ms / 1000)
            print(f"- fecha_creacion: {fecha_creacion}")
        print("=" * 100)

if __name__ == "__main__":
    asyncio.run(main())
