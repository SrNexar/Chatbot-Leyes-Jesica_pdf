from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
import fitz  # PyMuPDF
from dotenv import load_dotenv
import openai
from datetime import datetime
import os

# === Configuración ===
load_dotenv()

# Validar variables de entorno
required_vars = ["OPENAI_API_KEY", "QDRANT_URL", "QDRANT_API_KEY"]
for var in required_vars:
    if not os.getenv(var):
        raise EnvironmentError(f"Falta la variable de entorno: {var}")

# Inicializar servicios
openai.api_key = os.getenv("OPENAI_API_KEY")
model_embeddings = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
    timeout=120
)

# Constantes
UPLOAD_FOLDER = "docs_upload"
COLLECTION_NAME = "documentos_legales"
CHUNK_SIZE = 800
OVERLAP_SIZE = 200
MODEL_DIM = 384
MIN_SIMILARITY_THRESHOLD = 0.3
BATCH_SIZE = 50

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Variable global para documento actual
documento_actual = {"tipo": None, "especialidad": None, "filename": None}

# === FastAPI App ===
app = FastAPI(title="Chatbot Leyes - Versión Limpia")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Funciones Core ===
def inicializar_qdrant():
    """Inicializa la colección en Qdrant"""
    qdrant_client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=MODEL_DIM, distance=Distance.COSINE)
    )

def procesar_pdf(file_path: str):
    """Extrae texto del PDF y lo convierte en chunks vectorizados"""
    texto = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            texto += page.get_text() + "\n"
    
    if not texto.strip():
        raise ValueError("No se pudo extraer texto del PDF")
    
    tipo_doc = detectar_tipo_documento(texto, os.path.basename(file_path))
    
    chunks = []
    start = 0
    while start < len(texto):
        end = start + CHUNK_SIZE
        chunk = texto[start:end]
        if end < len(texto):
            last_period = chunk.rfind('.')
            if last_period > len(chunk) - 100:
                chunk = chunk[:last_period + 1]
                end = start + len(chunk)
        chunks.append(chunk.strip())
        if end >= len(texto):
            break
        start = end - OVERLAP_SIZE
    
    chunks = [chunk for chunk in chunks if len(chunk) > 50]
    
    vectores = model_embeddings.encode(chunks)
    
    return chunks, vectores, tipo_doc

def detectar_tipo_documento(texto: str, filename: str = ""):
    texto_lower = texto.lower()
    filename_lower = filename.lower()
    
    tipos = {
        "COIP": {
            "keywords": ["código orgánico integral penal", "coip", "delitos"],
            "especialidad": "Derecho Penal"
        },
        "Código Civil": {
            "keywords": ["código civil", "derecho civil", "personas"],
            "especialidad": "Derecho Civil"
        },
        "Constitución": {
            "keywords": ["constitución", "derechos fundamentales"],
            "especialidad": "Derecho Constitucional"
        }
    }
    
    for tipo, info in tipos.items():
        if any(keyword in texto_lower for keyword in info["keywords"]):
            return {"tipo": tipo, "especialidad": info["especialidad"]}
    
    return {"tipo": "Documento Legal", "especialidad": "Derecho General"}

def insertar_en_qdrant(chunks, vectores, tipo_documento):
    total_insertados = 0
    
    for i in range(0, len(chunks), BATCH_SIZE):
        batch_chunks = chunks[i:i + BATCH_SIZE]
        batch_vectores = vectores[i:i + BATCH_SIZE]
        
        puntos = [
            PointStruct(
                id=i + j,
                vector=batch_vectores[j].tolist(),
                payload={"text": batch_chunks[j], "tipo": tipo_documento["tipo"]}
            )
            for j in range(len(batch_chunks))
        ]
        
        qdrant_client.upsert(collection_name=COLLECTION_NAME, points=puntos)
        total_insertados += len(puntos)
    
    return total_insertados

def generar_respuesta_openai(contexto: str, tiene_contexto: bool = True):
    # Cambié la función para que no necesite pregunta, sólo contexto
    if tiene_contexto:
        prompt = f"""Actúas como un JUEZ ecuatoriano especializado en {documento_actual.get('especialidad', 'Derecho General')}.
        
Estructura tu respuesta como un RESUMEN LEGAL basado en el contexto del documento cargado:

📅 **FECHA Y HORA:** {datetime.now().strftime('%d de %B de %Y, %H:%M horas')}

RESUMEN DEL DOCUMENTO LEGAL:

{contexto}
"""
    else:
        prompt = f"""Actúas como un JUEZ ecuatoriano.

IMPORTANTE: No hay información específica en el documento para este caso.

📅 **FECHA Y HORA:** {datetime.now().strftime('%d de %B de %Y, %H:%M horas')}

No se dispone de contenido para analizar."""
    
    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.2
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error al generar respuesta: {str(e)}"

# === Endpoints ===
@app.get("/")
async def home():
    return {"mensaje": "Chatbot de Leyes - Versión Limpia", "version": "2.0"}

@app.post("/subir-documento")
async def subir_documento(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Solo archivos PDF")
        
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        chunks, vectores, tipo_doc = procesar_pdf(file_path)
        
        global documento_actual
        documento_actual.update({
            "tipo": tipo_doc["tipo"],
            "especialidad": tipo_doc["especialidad"],
            "filename": file.filename
        })
        
        inicializar_qdrant()
        total_insertados = insertar_en_qdrant(chunks, vectores, tipo_doc)
        
        return {
            "estado": "exitoso",
            "archivo": file.filename,
            "fragmentos": total_insertados,
            "tipo_documento": tipo_doc["tipo"],
            "especialidad": tipo_doc["especialidad"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Modelo de consulta modificado para que no reciba pregunta
class Consulta(BaseModel):
    contexto_adicional: Optional[str] = Field(None, example="Información extra relevante")
    tags: Optional[List[str]] = Field(None, example=["penal", "robo"])
    importancia: Optional[int] = Field(1, ge=1, le=5, example=3)

@app.post("/consultar")
async def consultar(consulta: Consulta):
    try:
        if not documento_actual.get("tipo"):
            raise HTTPException(status_code=400, detail="No hay documento cargado")
        
        # Buscar sin pregunta, pero igual con el vector del contexto adicional o un vector vacío
        # Si no hay contexto adicional, simplemente usamos un vector de ceros para buscar
        if consulta.contexto_adicional:
            vector_contexto = model_embeddings.encode([consulta.contexto_adicional])[0]
        else:
            # Vector neutro, o también podría usar vector para texto vacío
            vector_contexto = model_embeddings.encode([""])[0]
        
        resultados = qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=vector_contexto,
            limit=5,
            score_threshold=MIN_SIMILARITY_THRESHOLD
        )
        
        if not resultados:
            respuesta = generar_respuesta_openai("", False)
            fuente = "conocimiento_general"
        else:
            contexto = "\n".join([r.payload["text"] for r in resultados])
            
            # Añadimos contexto adicional si lo hay
            if consulta.contexto_adicional:
                contexto += "\nContexto adicional: " + consulta.contexto_adicional
            
            respuesta = generar_respuesta_openai(contexto, True)
            fuente = "documento"
        
        return {
            "respuesta": respuesta,
            "fuente": fuente,
            "documento": documento_actual.get("filename", "No disponible"),
            "tags": consulta.tags,
            "importancia": consulta.importancia
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/estado")
async def verificar_estado():
    try:
        collections = qdrant_client.get_collections()
        
        client = openai.OpenAI()
        test_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Di OK"}],
            max_tokens=3,
            temperature=0
        )
        openai_ok = test_response.choices[0].message.content.strip().upper() == "OK"
        
        return {
            "qdrant": {"collections": [c.name for c in collections.collections]},
            "openai": openai_ok,
            "documento_actual": documento_actual
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al verificar estado: {str(e)}")
