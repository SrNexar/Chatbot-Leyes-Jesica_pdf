import os
import openai
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from schemas.consulta import ConsultaChat
from datetime import datetime

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

model_embeddings = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

PATRONES = {
    "COIP": {
        "keywords": ["coip", "código orgánico integral penal", "delitos", "penas", "homicidio", "robo", "estafa"],
        "especialidad": "Derecho Penal",
        "descripcion": "Código Orgánico Integral Penal",
    },
    "Código de Comercio": {
        "keywords": ["código de comercio", "mercantil", "empresa", "comerciante", "sociedad anónima", "contrato mercantil"],
        "especialidad": "Derecho Mercantil",
        "descripcion": "Código de Comercio",
    },
    "Código de la Niñez": {
        "keywords": ["código de la niñez", "niños", "adolescentes", "menores", "patria potestad", "tutela"],
        "especialidad": "Derecho de Familia y Niñez",
        "descripcion": "Código de la Niñez y Adolescencia",
    },
    "Código Civil": {
        "keywords": ["código civil", "derecho civil", "personas", "bienes", "obligaciones", "contratos civiles"],
        "especialidad": "Derecho Civil",
        "descripcion": "Código Civil",
    },
    "Constitución": {
        "keywords": ["constitución", "derechos fundamentales", "garantías constitucionales", "estado", "poderes públicos"],
        "especialidad": "Derecho Constitucional",
        "descripcion": "Constitución",
    }
}

def detectar_coleccion_y_datos(pregunta: str):
    pregunta_lower = pregunta.lower()
    for coleccion, datos in PATRONES.items():
        if any(keyword in pregunta_lower for keyword in datos["keywords"]):
            return coleccion, datos
    return None, {
        "tipo": "Desconocido",
        "especialidad": "Derecho General",
        "descripcion": "documento legal no identificado"
    }

def construir_prompt(contexto: str, pregunta: str, tipo_documento: dict, tiene_contexto_relevante=True) -> str:
    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if tiene_contexto_relevante:
        tipo = tipo_documento.get("tipo", "Documento Legal")
        especialidad = tipo_documento.get("especialidad", "Derecho General")
        descripcion = tipo_documento.get("descripcion", "documento legal")

        return f"""Actúas como un JUEZ especializado en {especialidad} ecuatoriano.

📅 FECHA Y HORA:
{fecha_hora}

⚖️ RAZÓN DE LA SENTENCIA:
[Análisis jurídico basado en el {tipo}. Cita artículos.]

🏛️ VEREDICTO:
[CULPABLE o INOCENTE]

🏢 LUGAR DE RECLUSIÓN:
[Centro penitenciario si aplica]

📋 CONCLUSIÓN:
[Resumen del fallo]

CONTEXTO LEGAL ({tipo}):
{contexto}

CASO A JUZGAR:
{pregunta}"""
    else:
        return f"""Actúas como un JUEZ ecuatoriano. Sin contexto legal específico.

📅 FECHA Y HORA:
{fecha_hora}

⚖️ RAZÓN DE LA SENTENCIA:
Sin contexto legal específico.

🏛️ VEREDICTO:
SUSPENDIDO

📋 CONCLUSIÓN:
La sentencia no puede emitirse por falta de contexto.

CASO:
{pregunta}"""

async def procesar_chat(req: ConsultaChat) -> str:
    coleccion, tipo_documento = detectar_coleccion_y_datos(req.pregunta)

    if coleccion:
        vector = model_embeddings.encode([req.pregunta])[0]
        resultados = qdrant_client.search(collection_name=coleccion, query_vector=vector, limit=3)
        contexto = "\n\n".join([r.payload.get("text", "") for r in resultados]) if resultados else ""
        prompt = construir_prompt(contexto, req.pregunta, tipo_documento, tiene_contexto_relevante=bool(contexto))
    else:
        prompt = construir_prompt("", req.pregunta, tipo_documento, tiene_contexto_relevante=False)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Eres un asistente legal que responde con base en el contexto legal proporcionado."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=500
    )

    return response.choices[0].message.content.strip()
