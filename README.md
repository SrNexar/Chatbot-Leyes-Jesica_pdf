# 📘 Chatbot Legal con OpenAI y Qdrant

Un chatbot especializado en leyes ecuatorianas que procesa documentos PDF legales y responde consultas en formato de sentencia judicial usando **FastAPI**, **Qdrant** como base vectorial, y **OpenAI** como modelo generativo.

---

## 🚀 Características Principales

- **Procesamiento de PDFs**: Carga y procesa documentos legales (COIP, Código de Comercio, etc.)
- **Detección automática**: Identifica el tipo de documento legal subido
- **Respuestas estructuradas**: Todas las respuestas siguen el formato de sentencia judicial ecuatoriana
- **OpenAI API**: Utiliza GPT para generar respuestas inteligentes y contextualizadas
- **Base vectorial**: Almacenamiento en Qdrant para búsqueda semántica eficiente
- **Procesamiento por lotes**: Manejo eficiente de documentos grandes con chunks superpuestos
- **Zona horaria Ecuador**: Fechas y horas correctas para el contexto legal ecuatoriano

## 📋 Formato de Sentencia Judicial

Todas las respuestas del chatbot siguen este formato oficial:

```
📅 FECHA Y HORA: [Fecha y hora actual de Ecuador]
⚖️ RAZÓN DE LA SENTENCIA: [Análisis jurídico detallado]
🏛️ VEREDICTO: [CULPABLE/INOCENTE con justificación legal]
🏢 LUGAR DE RECLUSIÓN: [Centro penitenciario según gravedad del delito]
📋 CONCLUSIÓN: [Resumen y disposiciones finales]
```

---

## 🛠️ Tecnologías utilizadas

- **Python 3.12+**
- **FastAPI** - Framework web moderno
- **Qdrant** - Base de datos vectorial
- **OpenAI API** - Modelo de lenguaje (GPT-3.5/GPT-4)
- **Sentence Transformers** - Embeddings semánticos
- **PyMuPDF** - Procesamiento de PDFs
- **pytz** - Manejo de zonas horarias
- **Openpyxl** - Exportación a Excel

---

## ⚙️ Configuración del entorno

### 1. Clona el repositorio

```bash
git clone https://github.com/Karina1014/Chatbot-Leyes.git
```

### Crear entorno virtual
```
python -m venv venv
```
### Crear entorno virtual
```
venv\Scripts\activate
```

### Instalar fichero Requirements
```
pip install -r requirements.txt
```
