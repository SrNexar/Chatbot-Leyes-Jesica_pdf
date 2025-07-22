from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import CasoMongoAlerta, caso, SubirDocumento, CasoNotificacion 
from config.mongo import connect_db
import logging

app = FastAPI(title="Chatbot Legal - API")

# Configurar CORS para permitir conexiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await connect_db()
    logging.info("Servidor iniciado y DB conectada")

# Ruta para CRUD MongoDB (casos)
app.include_router(CasoMongoAlerta.router)

# Ruta para el chatbot (caso)
app.include_router(caso.router)

# Ruta para subir la documentación 
app.include_router(SubirDocumento.router)

# Ruta para notificaciones de casos
app.include_router(CasoNotificacion.router)
