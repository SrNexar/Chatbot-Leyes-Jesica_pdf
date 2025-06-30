# 🚀 Guía de Inicio Rápido - Chatbot Legal

## Paso 1: Configuración de Credenciales

1. **Copia el archivo de configuración**:
```bash
copy .env.example .env
```

2. **Edita el archivo `.env` con tus credenciales**:
```env
# OpenAI
OPENAI_API_KEY=sk-tu_api_key_aqui

# Qdrant Cloud (obtén tu cluster gratuito en https://cloud.qdrant.io)
QDRANT_URL=https://tu-cluster-id.us-east-1-0.aws.cloud.qdrant.io:6333
QDRANT_API_KEY=tu_api_key_de_qdrant

# Modelo OpenAI (opcional)
OPENAI_MODEL=gpt-3.5-turbo
```

## Paso 2: Instalación de Dependencias

```bash
pip install -r requirements.txt
```

## Paso 3: Ejecutar el Servidor

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

El servidor estará disponible en: http://localhost:8000

## Paso 4: Verificar Funcionamiento

### Opción A: Interfaz Web
- Ve a http://localhost:8000/docs
- Prueba los endpoints desde la interfaz Swagger

### Opción B: Script de Prueba
```bash
python test_completo.py
```

## Paso 5: Subir Documentos PDF

1. **Via API**:
```bash
curl -X POST "http://localhost:8000/documento/subir" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@docs_upload/documento.pdf"
```

2. **Via interfaz web**: 
   - http://localhost:8000/docs
   - Sección "documento/subir"

## Paso 6: Hacer Consultas

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"pregunta": "¿Cuál es la pena por robo agravado?"}'
```

## 📝 Endpoints Principales

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/status` | GET | Estado del servicio |
| `/documento/subir` | POST | Subir PDF legal |
| `/chat` | POST | Consultar chatbot |
| `/documento/estadisticas` | GET | Estadísticas del documento |
| `/configuracion/modelo` | GET/POST | Ver/cambiar modelo OpenAI |
| `/sentencia/ejemplo` | POST | Generar sentencia de ejemplo |

## 🔧 Solución de Problemas

### Error: "Faltan variables de entorno"
- Verifica que el archivo `.env` exista y tenga las credenciales correctas

### Error: "Connection timeout"
- Verifica la URL y API key de Qdrant
- Prueba la conectividad: `curl -X GET "http://localhost:8000/qdrant/test"`

### Error: "OpenAI API key invalid"
- Verifica tu API key de OpenAI en el archivo `.env`
- Asegúrate de tener créditos en tu cuenta OpenAI

### Error: "PDF no procesado"
- Verifica que el PDF tenga contenido de texto (no solo imágenes)
- El archivo debe ser un PDF válido y no estar corrupto

## 🎯 Casos de Uso

### 1. Consulta sobre Penas
```json
{
  "pregunta": "¿Cuál es la pena por homicidio según el COIP?"
}
```

### 2. Consulta sobre Procedimientos
```json
{
  "pregunta": "¿Cuáles son los requisitos para constituir una sociedad anónima?"
}
```

### 3. Consulta sobre Derechos
```json
{
  "pregunta": "¿Cuáles son los derechos de los niños según el código?"
}
```

## 📊 Formatos de Respuesta

Todas las respuestas siguen el formato de **sentencia judicial**:

```
📅 FECHA Y HORA: 29 de junio de 2025, 14:30 horas

⚖️ RAZÓN DE LA SENTENCIA:
[Análisis jurídico detallado basado en los artículos aplicables]

🏛️ VEREDICTO:
[CULPABLE/INOCENTE con justificación específica]

🏢 LUGAR DE RECLUSIÓN:
[Centro penitenciario según gravedad del delito]

📋 CONCLUSIÓN:
[Resumen, penas aplicables y disposiciones finales]

NOTIFÍQUESE Y CÚMPLASE.
```

## 🐳 Docker (Opcional)

Si prefieres usar Docker:

```bash
# Construir imagen
docker build -t chatbot-legal .

# Ejecutar contenedor
docker run -p 8000:8000 --env-file .env chatbot-legal

# O usar docker-compose
docker-compose up -d
```

## 📚 Documentos Soportados

El sistema detecta automáticamente:
- **COIP**: Código Orgánico Integral Penal
- **Código de Comercio**: Legislación comercial
- **Código de la Niñez**: Derechos de menores
- **Código Civil**: Derecho civil general
- **Constitución**: Carta magna

## 💡 Tips

1. **Archivos grandes**: El sistema procesa automáticamente en chunks
2. **Múltiples documentos**: Sube uno a la vez para mejor precisión
3. **Preguntas específicas**: Formula preguntas claras y específicas
4. **Formato judicial**: Todas las respuestas siguen formato de sentencia

## 📞 Soporte

- **Logs**: Revisa `registro_chat.xlsx` para historial
- **Errores**: Verifica logs de la terminal donde ejecutas el servidor
- **Documentación**: http://localhost:8000/docs para detalles de API
