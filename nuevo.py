from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv
import openai

# === Cargar variables de entorno ===
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise RuntimeError("Falta la variable de entorno OPENAI_API_KEY")

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

if not QDRANT_URL or not QDRANT_API_KEY:
    raise RuntimeError("Faltan variables de entorno QDRANT_URL o QDRANT_API_KEY")

# === Inicializar FastAPI ===
app = FastAPI(title="Chatbot Legal")

# === Inicializar servicios ===
model_embeddings = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

# === Patrones para identificar colecciones ===
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

# === Modelo de entrada ===
class ConsultaChat(BaseModel):
    pregunta: str

# === Función para detectar colección y datos ===
def detectar_coleccion_y_datos(pregunta: str):
    pregunta_lower = pregunta.lower()
    for coleccion, datos in PATRONES.items():
        if any(keyword in pregunta_lower for keyword in datos["keywords"]):
            return coleccion, {
                "tipo": coleccion,
                "especialidad": datos["especialidad"],
                "descripcion": datos["descripcion"]
            }
    return None, {
        "tipo": "Desconocido",
        "especialidad": "Derecho General",
        "descripcion": "documento legal no identificado"
    }

# === Construcción del prompt ===
def construir_prompt(contexto: str, pregunta: str, tipo_documento: dict, tiene_contexto_relevante: bool = True) -> str:
    from datetime import datetime
    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if tiene_contexto_relevante:
        especialidad = tipo_documento.get('especialidad', 'Derecho General')
        descripcion = tipo_documento.get('descripcion', 'documento legal')
        tipo = tipo_documento.get('tipo', 'Documento Legal')
        
        return f"""Actúas como un JUEZ especializado en {especialidad} ecuatoriano.

INSTRUCCIONES OBLIGATORIAS:
Debes estructurar tu respuesta como una SENTENCIA JUDICIAL con el siguiente formato:

📅 FECHA Y HORA:
{fecha_hora}

⚖️ RAZÓN DE LA SENTENCIA:
[Análisis jurídico detallado basado en el {tipo} proporcionado. Cita artículos específicos y fundamentos legales aplicables al caso presentado]

🏛️ VEREDICTO:
[CULPABLE/INOCENTE - con justificación legal específica basada en los artículos del {tipo}]

🏢 LUGAR DE RECLUSIÓN:
[Si es culpable: especificar centro penitenciario según gravedad del delito]
[Si es inocente: "Libertad inmediata del procesado"]

📋 CONCLUSIÓN:
[Resumen de la sentencia, penas aplicables, derechos del procesado y disposiciones finales]

NOTIFÍQUESE Y CÚMPLASE.

CONTEXTO LEGAL ({tipo}):
{contexto}

CASO A JUZGAR:
{pregunta}

IMPORTANTE: Basa tu sentencia ÚNICAMENTE en el {tipo} proporcionado. Cita artículos específicos."""
    else:
        return f"""Actúas como un JUEZ especializado en legislación ecuatoriana.

⚠️ IMPORTANTE: La información específica sobre este caso NO se encuentra en el documento legal proporcionado.

Estructura tu respuesta como sentencia, pero indicando la limitación:

📅 FECHA Y HORA:
{fecha_hora}

⚖️ RAZÓN DE LA SENTENCIA:
No se cuenta con el marco legal específico en el documento proporcionado para este caso. Sin embargo, basándome en principios generales del derecho ecuatoriano:

🏛️ VEREDICTO:
SUSPENDIDO - Falta de marco legal específico en el documento proporcionado

🏢 LUGAR DE RECLUSIÓN:
No aplicable hasta contar con legislación específica

📋 CONCLUSIÓN:
Esta sentencia provisional se basa en conocimiento general jurídico y NO en el documento específico proporcionado.
Se requiere consultar la legislación correspondiente y asesoramiento legal especializado.

CASO PRESENTADO:
{pregunta}

⚠️ ADVERTENCIA JUDICIAL: Sentencia no definitiva por falta de marco legal específico."""

# === Endpoint principal ===
@app.post("/chat", summary="Consulta al chatbot con contexto jurídico")
async def consultar_chat(req: ConsultaChat):
    try:
        coleccion, tipo_documento = detectar_coleccion_y_datos(req.pregunta)

        if coleccion is None:
            prompt = construir_prompt("", req.pregunta, tipo_documento, tiene_contexto_relevante=False)
        else:
            vector_pregunta = model_embeddings.encode([req.pregunta])[0]

            resultados = qdrant_client.search(
                collection_name=coleccion,
                query_vector=vector_pregunta,
                limit=4
            )

            if not resultados:
                prompt = construir_prompt("", req.pregunta, tipo_documento, tiene_contexto_relevante=False)
            else:
                contexto = "\n\n".join([r.payload.get("text", "") for r in resultados])
                prompt = construir_prompt(contexto, req.pregunta, tipo_documento)

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Puedes cambiar a "gpt-4o" si tienes acceso
            messages=[
                {"role": "system", "content": "Eres un asistente legal que responde con base en el contexto legal proporcionado."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        texto_respuesta = response.choices[0].message.content.strip()

        return {"respuesta": texto_respuesta}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar la respuesta: {str(e)}")
