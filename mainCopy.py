from fastapi import FastAPI
from routes import CasoMongoCopy, CasoCopy, SubirDocumento
from config.mongo import connect_db
import logging

app = FastAPI(title="Chatbot Legal - API")

@app.on_event("startup")
async def startup():
    await connect_db()
    logging.info("Servidor iniciado y DB conectada")

# Ruta para CRUD MongoDB (casos)
app.include_router(CasoMongoCopy.router)

# Ruta para el chatbot (caso)
app.include_router(CasoCopy.router)

# Ruta para subir la documentación 
app.include_router(SubirDocumento.router)
