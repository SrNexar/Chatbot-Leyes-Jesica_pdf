#!/usr/bin/env python3
"""
Script de prueba para verificar la funcionalidad de carga de documentos
"""

import requests
import json
import os
from pathlib import Path

# Configuración
BASE_URL = "http://localhost:8000"
TEST_PDF_PATH = "docs_upload"  # Carpeta donde están los PDFs

def test_server_status():
    """Verificar que el servidor esté funcionando"""
    try:
        response = requests.get(f"{BASE_URL}/status")
        print(f"✅ Estado del servidor: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   - Qdrant conectado: {data.get('qdrant_conectado')}")
            print(f"   - OpenAI conectado: {data.get('openai_conectado')}")
            print(f"   - Colecciones: {data.get('colecciones_disponibles')}")
            print(f"   - Test OpenAI: {data.get('test_openai', 'N/A')}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error al conectar con el servidor: {e}")
        return False

def test_qdrant_connectivity():
    """Verificar conectividad específica con Qdrant"""
    try:
        response = requests.get(f"{BASE_URL}/qdrant/test")
        print(f"✅ Test de Qdrant: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   - Estado: {data.get('estado')}")
            print(f"   - Conectividad: {data.get('conectividad')}")
            print(f"   - Mensaje: {data.get('mensaje')}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error al probar Qdrant: {e}")
        return False

def clean_collection():
    """Limpiar colección existente"""
    try:
        response = requests.delete(f"{BASE_URL}/documento/limpiar")
        print(f"🧹 Limpieza de colección: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   - {data.get('mensaje')}")
    except Exception as e:
        print(f"❌ Error al limpiar colección: {e}")

def upload_test_document():
    """Subir un documento de prueba"""
    pdf_files = list(Path(TEST_PDF_PATH).glob("*.pdf"))
    
    if not pdf_files:
        print(f"❌ No se encontraron archivos PDF en {TEST_PDF_PATH}")
        return False
    
    # Tomar el primer PDF encontrado
    test_file = pdf_files[0]
    print(f"📄 Subiendo: {test_file.name}")
    
    try:
        with open(test_file, 'rb') as f:
            files = {'file': (test_file.name, f, 'application/pdf')}
            response = requests.post(f"{BASE_URL}/documento/subir", files=files, timeout=300)
        
        print(f"📤 Carga de documento: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   - Estado: {data.get('estado')}")
            print(f"   - Fragmentos cargados: {data.get('fragmentos_cargados')}")
            print(f"   - Archivo: {data.get('archivo')}")
            print(f"   - Tamaño: {data.get('tamaño_archivo_mb')} MB")
            
            # Información del documento detectado
            doc_info = data.get('documento_detectado', {})
            print(f"   - Tipo detectado: {doc_info.get('tipo')}")
            print(f"   - Especialidad: {doc_info.get('especialidad')}")
            print(f"   - Confianza: {doc_info.get('confianza')}")
            print(f"   - Método: {doc_info.get('metodo_deteccion')}")
            return True
        else:
            print(f"   - Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error al subir documento: {e}")
        return False

def test_document_stats():
    """Verificar estadísticas del documento"""
    try:
        response = requests.get(f"{BASE_URL}/documento/estadisticas")
        print(f"📊 Estadísticas del documento: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   - Estado: {data.get('estado')}")
            print(f"   - Total fragmentos: {data.get('total_fragmentos')}")
            print(f"   - Longitud promedio: {data.get('longitud_promedio_fragmento')}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error al obtener estadísticas: {e}")
        return False

def test_chat():
    """Probar una consulta simple"""
    try:
        query = {"pregunta": "¿Qué tipos de delitos existen?"}  # Pregunta más genérica
        response = requests.post(f"{BASE_URL}/chat", json=query, timeout=60)
        
        print(f"💬 Test de chat: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   - Fuente: {data.get('fuente')}")
            print(f"   - Modelo usado: {data.get('modelo_usado', 'N/A')}")
            print(f"   - Tipo documento: {data.get('documento_tipo', 'N/A')}")
            print(f"   - Especialidad: {data.get('documento_especialidad', 'N/A')}")
            print(f"   - Fragmentos consultados: {data.get('fragmentos_consultados', 'N/A')}")
            print(f"   - Respuesta (primeros 150 chars): {data.get('respuesta', '')[:150]}...")
            return True
        else:
            print(f"   - Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error en chat: {e}")
        return False

def test_document_info():
    """Verificar información del documento actual"""
    try:
        response = requests.get(f"{BASE_URL}/documento/info")
        print(f"📋 Información del documento: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   - Estado: {data.get('estado')}")
            if data.get('estado') == 'documento_disponible':
                doc = data.get('documento', {})
                print(f"   - Tipo: {doc.get('tipo')}")
                print(f"   - Especialidad: {doc.get('especialidad')}")
                print(f"   - Descripción: {doc.get('descripcion')}")
                print(f"   - Archivo: {doc.get('filename')}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error al obtener información: {e}")
        return False

def main():
    """Ejecutar todas las pruebas"""
    print("🧪 Iniciando pruebas del sistema de carga de documentos\n")
    
    # Paso 1: Verificar servidor
    if not test_server_status():
        print("❌ El servidor no está disponible. Inicia el servidor primero.")
        return
    print()
    
    # Paso 2: Verificar Qdrant
    if not test_qdrant_connectivity():
        print("❌ Problemas de conectividad con Qdrant.")
        return
    print()
    
    # Paso 3: Limpiar colección
    clean_collection()
    print()
    
    # Paso 4: Subir documento
    if not upload_test_document():
        print("❌ Falló la carga del documento.")
        return
    print()
    
    # Paso 5: Verificar información del documento
    test_document_info()
    print()
    
    # Paso 6: Verificar estadísticas
    test_document_stats()
    print()
    
    # Paso 7: Probar chat
    test_chat()
    print()
    
    # Paso 7: Verificar información del documento
    test_document_info()
    print()
    
    print("✅ Todas las pruebas completadas!")

if __name__ == "__main__":
    main()
