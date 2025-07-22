from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv
from groq import Groq
from datetime import datetime
from bson import ObjectId
import config.mongo as mongo
import openai
import re
import logging

# === Cargar variables de entorno ===
load_dotenv()
# === ************************************************************************** ===
# === OPENAI ===
def cargar_config():
    load_dotenv()
    config = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "QDRANT_URL": os.getenv("QDRANT_URL"),
        "QDRANT_API_KEY": os.getenv("QDRANT_API_KEY")
    }

    if not all(config.values()):
        raise EnvironmentError("Faltan variables de entorno requeridas.")
    
    return config

config = cargar_config()

# === Inicializar servicios ===
openai.api_key = config["OPENAI_API_KEY"]
model_embeddings = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

qdrant_client = QdrantClient(
    url=config["QDRANT_URL"],
    api_key=config["QDRANT_API_KEY"],
    timeout=120  # Aumentar timeout a 120 segundos
)

# === ************************************************************************** ===
# === GROQ ===
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

# === Validación de variables necesarias ===
if not GROQ_API_KEY:
    raise RuntimeError("Falta la variable de entorno GROQ_API_KEY")

if not QDRANT_URL or not QDRANT_API_KEY:
    raise RuntimeError("Faltan variables de entorno QDRANT_URL o QDRANT_API_KEY")

# === Inicializar FastAPI ===
router = APIRouter(prefix="/chatbot", tags=["chatbot"])

# === Endpoint para listar casos disponibles ===
@router.get("/casos", summary="Listar todos los casos disponibles con sus IDs")
async def listar_casos_disponibles():
    """Obtiene todos los casos de la colección alertas2 con sus IDs para usar en el chatbot"""
    try:
        if mongo.db is None:
            raise HTTPException(status_code=500, detail="DB no conectada")

        casos = []
        cursor = mongo.db.alertas2.find({}, {"_id": 1, "alerta": 1, "descripcion": 1})
        async for caso in cursor:
            casos.append({
                "id": str(caso["_id"]),
                "alerta": caso.get("alerta", "Sin alerta"),
                "descripcion": caso.get("descripcion", "Sin descripción")[:100] + "..." if len(caso.get("descripcion", "")) > 100 else caso.get("descripcion", "Sin descripción")
            })
        
        return {
            "total_casos": len(casos),
            "casos": casos
        }
    
    except Exception as e:
        logging.error(f"Error listando casos: {e}")
        raise HTTPException(status_code=500, detail=f"Error al listar casos: {str(e)}")

# === Inicializar modelo de embeddings y cliente Qdrant ===
model_embeddings = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)

# === Diccionario de patrones para identificar documentos legales ===
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

# === Modelo para recibir preguntas ===
class ConsultaChat(BaseModel):
    pregunta: str

# === Detección de colección y tipo de documento (colección fija documentos_legales) ===
def detectar_coleccion_y_datos(pregunta: str):
    pregunta_lower = pregunta.lower()
    for clave, datos in PATRONES.items():
        if any(keyword in pregunta_lower for keyword in datos["keywords"]):
            return "documentos_legales", {
                "tipo": clave,
                "especialidad": datos["especialidad"],
                "descripcion": datos["descripcion"]
            }
    return None, {
        "tipo": "Desconocido",
        "especialidad": "Derecho General",
        "descripcion": "documento legal no identificado"
    }
# === ************************************************************************** ===
# === Endpoint para consultar al chatbot groq-client===
"""
@router.post("/caso/{id}", summary="Consultar al chatbot usando las transcripciones de un caso guardado")
async def consultar_chat_con_caso(id: str):
    try:
        if mongo.db is None:
            raise HTTPException(status_code=500, detail="DB no conectada")

        # Buscar el caso en Mongo
        caso = await mongo.db.caso.find_one({"_id": ObjectId(id)})
        if not caso:
            raise HTTPException(status_code=404, detail="Caso no encontrado")

        # Obtener transcripciones
        transcripcion_video = caso.get("transcripción_de_video", "")
        transcripcion_audio = caso.get("transcripción_de_audio", "")

        if not transcripcion_video and not transcripcion_audio:
            raise HTTPException(status_code=400, detail="El caso no tiene transcripciones para analizar")

        # Concatenar para formar la 'pregunta'
        pregunta = f"{transcripcion_video}\n\n{transcripcion_audio}"

        # Aquí sigue EXACTAMENTE la misma lógica de tu /chat
        coleccion, tipo_documento = detectar_coleccion_y_datos(pregunta)

        if coleccion is None:
            prompt = construir_prompt("", pregunta, tipo_documento, tiene_contexto_relevante=False)
        else:
            vector_pregunta = model_embeddings.encode([pregunta])[0]

            resultados = qdrant_client.search(
                collection_name=coleccion,
                query_vector=vector_pregunta,
                limit=4
            )

            if not resultados:
                prompt = construir_prompt("", pregunta, tipo_documento, tiene_contexto_relevante=False)
            else:
                contexto = "\n\n".join([r.payload["text"] for r in resultados if "text" in r.payload])
                prompt = construir_prompt(contexto, pregunta, tipo_documento)

        # Llamada al modelo Groq
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "Eres un asistente legal que responde con base en el contexto legal proporcionado."},
                {"role": "user", "content": prompt}
            ]
        )
        texto_respuesta = response.choices[0].message.content.strip()

        return {"respuesta": texto_respuesta}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar la respuesta: {str(e)}")
"""

# === ************************************************************************** ===
# === Endpoint para consultar al chatbot OPENAI===

@router.post("/chatcaso/{id_alerta}", summary="Consultar chatbot OpenAI con transcripciones de dos colecciones distintas")
async def consultar_chat_openai_con_caso(id_alerta: str):
    try:
        if mongo.db is None:
            raise HTTPException(status_code=500, detail="DB no conectada")

        # Limpiar y validar el ID
        id_alerta_limpio = id_alerta.strip().replace('\n', '').replace('\r', '')
        
        # Validar que el ID tenga el formato correcto (24 caracteres hexadecimales)
        if len(id_alerta_limpio) != 24:
            raise HTTPException(status_code=400, detail=f"ID inválido: debe tener 24 caracteres, recibido {len(id_alerta_limpio)} caracteres")
        
        # Validar que sean caracteres hexadecimales
        try:
            int(id_alerta_limpio, 16)
        except ValueError:
            raise HTTPException(status_code=400, detail="ID inválido: debe contener solo caracteres hexadecimales (0-9, a-f)")

        caso = await mongo.db.alertas2.find_one({"_id": ObjectId(id_alerta_limpio)})
        if not caso:
            raise HTTPException(status_code=404, detail="Alerta no encontrada")

        transcripcion = caso.get("descripcion", "")

        if not transcripcion and not transcripcion:
            raise HTTPException(status_code=400, detail="El caso no tiene transcripciones para analizar")
        prompt_ampliacion = f"""
Eres un asistente de seguridad de Ecuador encargado de generar un reporte detallado y coherente basado en la siguiente información:

- Transcripción de video: "{transcripcion}"


A partir de esta información, crea una descripción ampliada y realista del incidente captado en el video, imaginando un contexto plausible que ayude a comprender la situación con mayor profundidad. Describe el entorno, el comportamiento y las emociones de las personas involucradas, así como las acciones específicas (por ejemplo, agresiones físicas como golpes, uso de objetos, o amenazas) y las posibles consecuencias visibles.

No inventes hechos imposibles ni exageres sin fundamento, pero sí agrega detalles que enriquezcan el análisis, como el escenario donde ocurre el hecho, movimientos, objetos usados y reacciones.

La descripción debe servir para un análisis de seguridad efectivo y debe reflejar un escenario creíble basado en la información dada.
"""


        ampliacion_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente que amplía transcripciones breves para crear un contexto útil."},
                {"role": "user", "content": prompt_ampliacion}
            ],
            temperature=0.7,
            max_tokens=500
        )

        texto_ampliado = ampliacion_response.choices[0].message.content.strip()

        # Usar el texto ampliado como la pregunta para el análisis posterior
        pregunta = texto_ampliado


        # Detectar colección y tipo documento basado en la pregunta ampliada
        coleccion, tipo_documento = detectar_coleccion_y_datos(pregunta)

        if coleccion is None:
            prompt = construir_prompt("", pregunta, tipo_documento, tiene_contexto_relevante=False)
        else:
            vector_pregunta = model_embeddings.encode([pregunta])[0]
            resultados = qdrant_client.search(
                collection_name=coleccion,
                query_vector=vector_pregunta,
                limit=4
            )
            if not resultados:
                prompt = construir_prompt("", pregunta, tipo_documento, tiene_contexto_relevante=False)
            else:
                contexto = "\n\n".join([r.payload.get("text", "") for r in resultados])
                prompt = construir_prompt(contexto, pregunta, tipo_documento)

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente legal que responde con base en el contexto legal proporcionado."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=1500
        )
        texto_respuesta = response.choices[0].message.content.strip()
        try:
            logging.info(texto_ampliado)
        except Exception as e:
            logging.error(f"Error: {e}")
        campos = extraer_campos_respuesta(texto_respuesta, texto_ampliado)


        notificacion = {
            "caso_id": ObjectId(id_alerta_limpio),
            **campos,
            "fecha_creacion": datetime.now()
        }

        await mongo.db.notificacion.insert_one(notificacion)

        return {
    "respuesta": texto_respuesta,
    "texto_ampliado": texto_ampliado
}


    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar la respuesta: {str(e)}")



# === Construcción del prompt ===
def construir_prompt(contexto: str, pregunta: str, tipo_documento: dict, tiene_contexto_relevante: bool = True) -> str:
    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if tiene_contexto_relevante:
        especialidad = tipo_documento.get('especialidad', 'Derecho General')
        descripcion = tipo_documento.get('descripcion', 'documento legal')
        tipo = tipo_documento.get('tipo', 'Documento Legal')

        return f"""Actúas como un JUEZ especializado en {especialidad} ecuatoriano.

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


def extraer_campos_respuesta(respuesta: str, texto_ampliado: str) -> dict:
    import re  # Asegúrate de importar re si no lo has hecho
    
    iconos_campos = {
        "📅 FECHA Y HORA:": "fecha_hora",
        "⚖️ RAZÓN DE LA SENTENCIA:": "razon_sentencia",
        "🏛️ VEREDICTO:": "veredicto",
        "🏢 LUGAR DE RECLUSIÓN:": "lugar_reclusion",
        "📋 CONCLUSIÓN:": "conclusion"
    }

    partes = re.split(r'(📅 FECHA Y HORA:|⚖️ RAZÓN DE LA SENTENCIA:|🏛️ VEREDICTO:|🏢 LUGAR DE RECLUSIÓN:|📋 CONCLUSIÓN:)', respuesta)
    
    resultado = {"texto_ampliado": texto_ampliado.strip()}
    clave_actual = None

    for parte in partes:
        parte = parte.strip()
        if parte in iconos_campos:
            clave_actual = iconos_campos[parte]
            resultado[clave_actual] = ""
        elif clave_actual:
            resultado[clave_actual] += parte.strip() + " "

    return {k: v.strip() for k, v in resultado.items()}