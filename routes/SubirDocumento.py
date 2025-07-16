import os
from typing import List, Tuple
from fastapi import FastAPI, UploadFile, File, HTTPException, APIRouter
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from docx import Document
import fitz  # PyMuPDF

# === Configuración ===
UPLOAD_FOLDER = "docs_upload"
COLLECTION_NAME = "COIP_Documentos"
CHUNK_SIZE = 800
OVERLAP_SIZE = 200
BATCH_SIZE = 50
MODEL_DIM = 384


QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

if not QDRANT_URL or not QDRANT_API_KEY:
    raise RuntimeError("Faltan variables de entorno QDRANT_URL o QDRANT_API_KEY")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

router = APIRouter(prefix="/documento", tags=["documento"])

# === Inicialización de servicios ===
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

# === Utilidades ===

def init_collection():
    qdrant.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE)
    )

def detectar_tipo_documento(texto: str, nombre: str) -> str:
    if "ley" in texto.lower():
        return "ley"
    elif "contrato" in texto.lower():
        return "contrato"
    return "desconocido"

def extract_text(path: str, ext: str) -> str:
    if ext == "pdf":
        with fitz.open(path) as doc:
            return "\n\n".join(page.get_text().strip() for page in doc if page.get_text().strip())
    elif ext == "docx":
        doc = Document(path)
        return "\n".join(p.text.strip() for p in doc.paragraphs if p.text.strip())
    else:
        raise ValueError("Extensión no soportada")

def chunk_text(text: str, chunk_size: int, overlap_size: int) -> List[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        if end < len(text):
            natural_break = max(
                chunk.rfind('.', max(0, len(chunk) - 100)),
                chunk.rfind('\n', max(0, len(chunk) - 100))
            )
            if natural_break > 0:
                chunk = chunk[:natural_break + 1]
                end = start + len(chunk)

        if len(chunk.strip()) > 50:
            chunks.append(chunk.strip())

        if end >= len(text):
            break
        start = end - overlap_size
    return chunks

def embed_and_store(chunks: List[str]):
    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i:i+BATCH_SIZE]
        vectors = model.encode(batch)
        points = [
            PointStruct(id=i+j, vector=vectors[j].tolist(), payload={"text": batch[j]})
            for j in range(len(batch))
        ]
        qdrant.upsert(collection_name=COLLECTION_NAME, points=points)

# === Endpoint ===

@router.post("/subir", summary="Sube un documento .pdf o .docx y lo indexa en Qdrant")
async def subir_documento(file: UploadFile = File(...)):
    ext = file.filename.lower().split(".")[-1]
    if ext not in ("pdf", "docx"):
        raise HTTPException(400, detail="Solo se permiten archivos .pdf o .docx")

    save_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(save_path, "wb") as f:
        f.write(await file.read())

    try:
        text = extract_text(save_path, ext)
    except Exception as e:
        raise HTTPException(400, detail=f"No se pudo extraer texto: {str(e)}")

    if not text.strip():
        raise HTTPException(400, detail="El archivo no contiene texto extraíble")

    chunks = chunk_text(text, CHUNK_SIZE, OVERLAP_SIZE)
    if not chunks:
        raise HTTPException(400, detail="No se generaron fragmentos útiles del texto")

    init_collection()
    embed_and_store(chunks)

    tipo_doc = detectar_tipo_documento(text, file.filename)

    return {
        "estado": "ok",
        "archivo": file.filename,
        "tipo_documento": tipo_doc,
        "fragmentos_cargados": len(chunks)
    }
