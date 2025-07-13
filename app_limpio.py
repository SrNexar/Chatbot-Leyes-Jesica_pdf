from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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
    # Extraer texto
    texto = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            texto += page.get_text() + "\n"
    
    if not texto.strip():
        raise ValueError("No se pudo extraer texto del PDF")
    
    # Detectar tipo de documento
    tipo_doc = detectar_tipo_documento(texto, os.path.basename(file_path))
    
    # Crear chunks
    chunks = []
    start = 0
    while start < len(texto):
        end = start + CHUNK_SIZE
        chunk = texto[start:end]
        
        # Cortar en punto natural si no es el final
        if end < len(texto):
            last_period = chunk.rfind('.')
            if last_period > len(chunk) - 100:
                chunk = chunk[:last_period + 1]
                end = start + len(chunk)
        
        chunks.append(chunk.strip())
        if end >= len(texto):
            break
        start = end - OVERLAP_SIZE
    
    # Filtrar chunks muy pequeños
    chunks = [chunk for chunk in chunks if len(chunk) > 50]
    
    # Vectorizar
    vectores = model_embeddings.encode(chunks)
    
    return chunks, vectores, tipo_doc

def detectar_tipo_documento(texto: str, filename: str = ""):
    """Detecta el tipo de documento legal"""
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
    
    # Detectar por contenido
    for tipo, info in tipos.items():
        if any(keyword in texto_lower for keyword in info["keywords"]):
            return {"tipo": tipo, "especialidad": info["especialidad"]}
    
    return {"tipo": "Documento Legal", "especialidad": "Derecho General"}

def insertar_en_qdrant(chunks, vectores, tipo_documento):
    """Inserta los chunks en Qdrant por lotes"""
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

def generar_respuesta_openai(contexto: str, pregunta: str, tiene_contexto: bool = True):
    """Genera respuesta usando OpenAI"""
    if tiene_contexto:
        prompt = f"""Actúas como un JUEZ ecuatoriano especializado en {documento_actual.get('especialidad', 'Derecho General')}.

Estructura tu respuesta como SENTENCIA JUDICIAL:

📅 **FECHA Y HORA:** {datetime.now().strftime('%d de %B de %Y, %H:%M horas')}

⚖️ **RAZÓN DE LA SENTENCIA:**
[Análisis jurídico basado en el contexto proporcionado]

🏛️ **VEREDICTO:**
[CULPABLE/INOCENTE con justificación legal]

🏢 **LUGAR DE RECLUSIÓN:**
[Centro penitenciario correspondiente o "Libertad inmediata"]

📋 **CONCLUSIÓN:**
[Resumen de la sentencia]

CONTEXTO LEGAL:
{contexto}

CASO A JUZGAR:
{pregunta}"""
    else:
        prompt = f"""Actúas como un JUEZ ecuatoriano.

IMPORTANTE: No hay información específica en el documento para este caso.

📅 **FECHA Y HORA:** {datetime.now().strftime('%d de %B de %Y, %H:%M horas')}

⚖️ **RAZÓN DE LA SENTENCIA:**
No se cuenta con el marco legal específico para este caso.

🏛️ **VEREDICTO:**
SUSPENDIDO - Falta de marco legal específico

🏢 **LUGAR DE RECLUSIÓN:**
No aplicable

📋 **CONCLUSIÓN:**
Se requiere consultar la legislación correspondiente.

CASO: {pregunta}"""
    
    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
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
    """Sube y procesa un documento PDF"""
    try:
        # Validaciones básicas
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Solo archivos PDF")
        
        # Guardar archivo
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Procesar PDF
        chunks, vectores, tipo_doc = procesar_pdf(file_path)
        
        # Actualizar documento actual
        global documento_actual
        documento_actual.update({
            "tipo": tipo_doc["tipo"],
            "especialidad": tipo_doc["especialidad"],
            "filename": file.filename
        })
        
        # Inicializar Qdrant y cargar datos
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

class Consulta(BaseModel):
    pregunta: str

@app.post("/consultar")
async def consultar(consulta: Consulta):
    """Consulta al chatbot"""
    try:
        # Verificar si hay documento cargado
        if not documento_actual.get("tipo"):
            raise HTTPException(status_code=400, detail="No hay documento cargado")
        
        # Buscar contexto relevante
        vector_pregunta = model_embeddings.encode([consulta.pregunta])[0]
        
        resultados = qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=vector_pregunta,
            limit=5,
            score_threshold=MIN_SIMILARITY_THRESHOLD
        )
        
        # Generar respuesta
        if not resultados:
            respuesta = generar_respuesta_openai("", consulta.pregunta, False)
            fuente = "conocimiento_general"
        else:
            contexto = "\n".join([r.payload["text"] for r in resultados])
            respuesta = generar_respuesta_openai(contexto, consulta.pregunta, True)
            fuente = "documento"
        
        return {
            "respuesta": respuesta,
            "fuente": fuente,
            "documento": documento_actual.get("filename", "No disponible")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/estado")
async def verificar_estado():
    """Verifica el estado del sistema"""
    try:
        # Verificar Qdrant
        collections = qdrant_client.get_collections()
        
        # Verificar OpenAI
        client = openai.OpenAI()
        test_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Di OK"}],
            max_tokens=10
        )
        
        return {
            "estado": "operativo",
            "qdrant": "conectado",
            "openai": "conectado",
            "documento_actual": documento_actual.get("filename", "Ninguno")
        }
    except Exception as e:
        return {"estado": "error", "mensaje": str(e)}

@app.delete("/limpiar")
async def limpiar_datos():
    """Limpia la colección de documentos"""
    try:
        collections = qdrant_client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if COLLECTION_NAME in collection_names:
            qdrant_client.delete_collection(COLLECTION_NAME)
        
        global documento_actual
        documento_actual = {"tipo": None, "especialidad": None, "filename": None}
        
        return {"estado": "limpiado", "mensaje": "Datos eliminados correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
