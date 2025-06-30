# 🤖 Chatbot Leyes Ecuador - OpenAI Version

Un chatbot especializado en legislación ecuatoriana que utiliza OpenAI GPT para análisis jurídico inteligente con detección automática de tipos de documentos legales.

## 🆕 Migración a OpenAI

Este proyecto ha sido migrado de Google Gemini a OpenAI para obtener mejores resultados y mayor flexibilidad.

### ⚡ Migración Rápida

1. **Ejecuta el script de migración:**
   ```bash
   python migrate_to_openai.py
   ```

2. **Obtén tu API key de OpenAI:**
   - Ve a: https://platform.openai.com/api-keys
   - Crea una nueva API key

3. **Configura tu .env:**
   ```
   OPENAI_API_KEY=sk-tu-api-key-aqui
   OPENAI_MODEL=gpt-3.5-turbo
   QDRANT_URL=tu-url-qdrant
   QDRANT_API_KEY=tu-api-key-qdrant
   ```

4. **Inicia el servidor:**
   ```bash
   python app.py
   ```

## 🧠 Modelos Disponibles

| Modelo | Costo (1M tokens) | Recomendado para |
|--------|-------------------|------------------|
| `gpt-3.5-turbo` | ~$2 | Uso general, económico |
| `gpt-4o-mini` | ~$0.15 entrada, $0.60 salida | Balance costo/calidad |
| `gpt-4o` | ~$5 entrada, $15 salida | Máxima calidad |
| `gpt-4` | ~$30 entrada, $60 salida | Casos complejos |

## 🔧 Configuración Dinámica

### Cambiar Modelo en Tiempo Real

```bash
# Ver modelo actual
curl GET http://localhost:8000/configuracion/modelo

# Cambiar a GPT-4
curl -X POST http://localhost:8000/configuracion/modelo \
  -H "Content-Type: application/json" \
  -d '{"modelo": "gpt-4o-mini"}'
```

## 📚 Tipos de Documentos Soportados

El sistema detecta automáticamente:

- **COIP** (Código Orgánico Integral Penal) → Experto en Derecho Penal
- **Código de Comercio** → Experto en Derecho Mercantil  
- **Código de la Niñez** → Experto en Derecho de Familia
- **Código Civil** → Experto en Derecho Civil
- **Constitución** → Experto en Derecho Constitucional

## 🚀 Endpoints Principales

### Subir Documento
```bash
POST /documento/subir
# Respuesta incluye detección automática del tipo de documento
```

### Consultar Chatbot
```bash
POST /chat
{
  "pregunta": "¿Cuáles son las penas por homicidio en el COIP?"
}

# Respuesta incluye:
# - Análisis jurídico especializado
# - Tipo de documento consultado
# - Modelo de IA utilizado
# - Fragmentos relevantes consultados
```

### Configuración
```bash
GET /configuracion/modelo          # Ver modelo actual
POST /configuracion/modelo         # Cambiar modelo
GET /documento/info                # Info del documento cargado
GET /documento/estadisticas        # Estadísticas detalladas
```

## 💡 Ventajas de OpenAI

✅ **Mejor calidad** - Respuestas más precisas y coherentes  
✅ **Flexibilidad** - Múltiples modelos según necesidades  
✅ **Costos transparentes** - Control total del gasto  
✅ **Prompts optimizados** - Mejor para análisis jurídico  
✅ **Actualizaciones frecuentes** - Modelos siempre actualizados  

## 🔧 Instalación Completa

1. **Clona el repositorio:**
   ```bash
   git clone <repo-url>
   cd Chatbot-Leyes-Jesica_pdf
   ```

2. **Instala dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecuta migración:**
   ```bash
   python migrate_to_openai.py
   ```

4. **Configura variables de entorno** en `.env`

5. **Inicia el servidor:**
   ```bash
   uvicorn app:app --reload --port 8000
   ```

## 🧪 Pruebas

```bash
# Ejecutar suite completa de pruebas
python test_upload.py

# Verificar estado del sistema
curl GET http://localhost:8000/status
```

## 💰 Optimización de Costos

- **Desarrollo/Pruebas:** `gpt-3.5-turbo` 
- **Producción balance:** `gpt-4o-mini`
- **Máxima calidad:** `gpt-4o`

## 🔒 Seguridad

- API keys almacenadas en `.env` (nunca en código)
- Validación de entrada y límites de tamaño
- Manejo robusto de errores
- Timeouts configurables

## 📞 Soporte

Si encuentras problemas durante la migración:

1. Verifica tu API key de OpenAI
2. Revisa los logs del servidor
3. Ejecuta `python test_upload.py` para diagnósticos
4. Consulta la documentación de OpenAI

---

**¡Tu chatbot jurídico ahora es más potente con OpenAI! 🎉**
