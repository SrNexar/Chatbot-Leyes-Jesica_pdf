from fastapi import FastAPI
from routes import caso
from config.mongo import connect_db
import logging

app = FastAPI(title="Chatbot Legal - API")

@app.on_event("startup")
async def startup():
    await connect_db()
    logging.info("Servidor iniciado y DB conectada")

# Ruta para CRUD MongoDB (casos)
app.include_router(caso.router)