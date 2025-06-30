#!/usr/bin/env python3
"""
Script de prueba para verificar el funcionamiento del chatbot legal
"""

import requests
import json
import time
import os

# Configuración
BASE_URL = "http://localhost:8000"

def test_status():
    """Probar el endpoint de estado"""
    print("🔍 Probando estado del servicio...")
    try:
        response = requests.get(f"{BASE_URL}/status")
        if response.status_code == 200:
            print("✅ Servicio activo")
            return True
        else:
            print(f"❌ Error en servicio: {response.status_code}")
            return False
    except requests.ConnectionError:
        print("❌ No se pudo conectar al servicio. ¿Está corriendo el servidor?")
        return False

def test_qdrant():
    """Probar conexión con Qdrant"""
    print("🔍 Probando conexión con Qdrant...")
    try:
        response = requests.get(f"{BASE_URL}/qdrant/test")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Qdrant conectado: {result.get('message', 'OK')}")
            return True
        else:
            print(f"❌ Error en Qdrant: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error al conectar con Qdrant: {e}")
        return False

def test_modelo_openai():
    """Probar configuración de modelo OpenAI"""
    print("🔍 Probando configuración de OpenAI...")
    try:
        response = requests.get(f"{BASE_URL}/configuracion/modelo")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Modelo OpenAI configurado: {result.get('modelo_actual', 'N/A')}")
            return True
        else:
            print(f"❌ Error al obtener modelo: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error al verificar modelo: {e}")
        return False

def test_subir_documento():
    """Probar subida de documento PDF"""
    print("🔍 Probando subida de documento...")
    
    # Buscar un PDF en la carpeta docs_upload
    docs_folder = "docs_upload"
    pdf_files = [f for f in os.listdir(docs_folder) if f.endswith('.pdf')]
    
    if not pdf_files:
        print("❌ No se encontraron archivos PDF en docs_upload/")
        return False
    
    pdf_file = pdf_files[0]
    file_path = os.path.join(docs_folder, pdf_file)
    
    try:
        with open(file_path, 'rb') as file:
            files = {'file': (pdf_file, file, 'application/pdf')}
            response = requests.post(f"{BASE_URL}/documento/subir", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Documento subido: {result.get('filename', 'N/A')}")
            print(f"   Tipo detectado: {result.get('tipo_documento', {}).get('tipo', 'N/A')}")
            print(f"   Chunks procesados: {result.get('chunks_procesados', 'N/A')}")
            return True
        else:
            print(f"❌ Error al subir documento: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error al subir documento: {e}")
        return False

def test_chat():
    """Probar consulta al chatbot"""
    print("🔍 Probando consulta al chatbot...")
    
    pregunta = "¿Cuál es la pena por robo agravado según el código penal ecuatoriano?"
    
    try:
        data = {"pregunta": pregunta}
        response = requests.post(f"{BASE_URL}/chat", json=data)
        
        if response.status_code == 200:
            result = response.json()
            respuesta = result.get('respuesta', '')
            
            print("✅ Consulta exitosa")
            print(f"   Pregunta: {pregunta}")
            print(f"   Contexto encontrado: {result.get('contexto_encontrado', False)}")
            
            # Verificar formato de sentencia
            elementos_sentencia = [
                "📅 **FECHA Y HORA:**",
                "⚖️ **RAZÓN DE LA SENTENCIA:**",
                "🏛️ **VEREDICTO:**",
                "🏢 **LUGAR DE RECLUSIÓN:**",
                "📋 **CONCLUSIÓN:**"
            ]
            
            formato_correcto = all(elemento in respuesta for elemento in elementos_sentencia)
            
            if formato_correcto:
                print("✅ Formato de sentencia judicial correcto")
            else:
                print("⚠️ Formato de sentencia incompleto")
            
            # Mostrar extracto de la respuesta
            print("\n--- EXTRACTO DE RESPUESTA ---")
            print(respuesta[:500] + "..." if len(respuesta) > 500 else respuesta)
            print("--- FIN EXTRACTO ---\n")
            
            return True
        else:
            print(f"❌ Error en consulta: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error en consulta: {e}")
        return False

def test_sentencia_ejemplo():
    """Probar endpoint de sentencia de ejemplo"""
    print("🔍 Probando sentencia de ejemplo...")
    
    try:
        response = requests.post(f"{BASE_URL}/sentencia/ejemplo")
        
        if response.status_code == 200:
            result = response.json()
            sentencia = result.get('sentencia', '')
            
            print("✅ Sentencia de ejemplo generada")
            print("\n--- SENTENCIA DE EJEMPLO ---")
            print(sentencia)
            print("--- FIN SENTENCIA ---\n")
            
            return True
        else:
            print(f"❌ Error al generar sentencia: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error en sentencia de ejemplo: {e}")
        return False

def test_estadisticas():
    """Probar endpoint de estadísticas"""
    print("🔍 Probando estadísticas del documento...")
    
    try:
        response = requests.get(f"{BASE_URL}/documento/estadisticas")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Estadísticas obtenidas")
            print(f"   Total chunks: {result.get('total_chunks', 'N/A')}")
            print(f"   Tamaño promedio: {result.get('tamaño_promedio_chunk', 'N/A')}")
            return True
        else:
            print(f"❌ Error al obtener estadísticas: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error en estadísticas: {e}")
        return False

def main():
    """Ejecutar todas las pruebas"""
    print("🚀 Iniciando pruebas del Chatbot Legal")
    print("=" * 50)
    
    tests = [
        ("Estado del servicio", test_status),
        ("Conexión Qdrant", test_qdrant),
        ("Modelo OpenAI", test_modelo_openai),
        ("Subida de documento", test_subir_documento),
        ("Consulta chatbot", test_chat),
        ("Sentencia ejemplo", test_sentencia_ejemplo),
        ("Estadísticas", test_estadisticas)
    ]
    
    resultados = []
    
    for nombre, test_func in tests:
        print(f"\n📝 {nombre}")
        print("-" * 30)
        try:
            resultado = test_func()
            resultados.append((nombre, resultado))
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            resultados.append((nombre, False))
        
        time.sleep(1)  # Pausa entre pruebas
    
    # Resumen final
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 50)
    
    exitosas = 0
    for nombre, resultado in resultados:
        estado = "✅ PASÓ" if resultado else "❌ FALLÓ"
        print(f"{estado:<12} {nombre}")
        if resultado:
            exitosas += 1
    
    print(f"\nPruebas exitosas: {exitosas}/{len(resultados)}")
    
    if exitosas == len(resultados):
        print("🎉 ¡Todas las pruebas pasaron! El chatbot está funcionando correctamente.")
    else:
        print("⚠️ Algunas pruebas fallaron. Revisa la configuración.")
    
    return exitosas == len(resultados)

if __name__ == "__main__":
    # Verificar que el directorio de documentos existe
    if not os.path.exists("docs_upload"):
        print("❌ La carpeta 'docs_upload' no existe")
        exit(1)
    
    # Ejecutar pruebas
    success = main()
    exit(0 if success else 1)
