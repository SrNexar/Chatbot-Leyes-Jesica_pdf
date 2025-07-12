from fastapi import APIRouter, HTTPException
from schemas.consulta import ConsultaChat
from services.chatbot_service import procesar_chat

router = APIRouter(prefix="/chatbot", tags=["chatbot"])

@router.post("/")
async def consultar_chat(req: ConsultaChat):
    try:
        respuesta = await procesar_chat(req)
        return {"respuesta": respuesta}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando respuesta: {e}")
