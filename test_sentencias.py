#!/usr/bin/env python3
"""
Script de prueba para el formato de sentencia judicial
"""

import requests
import json

# Configuración
BASE_URL = "http://localhost:8000"

def test_sentencia_ejemplo():
    """Probar endpoint de sentencia de ejemplo"""
    try:
        response = requests.post(f"{BASE_URL}/sentencia/ejemplo")
        print(f"🧪 Test sentencia ejemplo: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Sentencia generada exitosamente")
            print("\n" + "="*80)
            print("EJEMPLO DE SENTENCIA JUDICIAL:")
            print("="*80)
            print(data["sentencia_ejemplo"])
            print("="*80)
            print(f"📊 Características: {data.get('caracteristicas')}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en test de sentencia: {e}")
        return False

def test_chat_con_caso_penal():
    """Probar chat con un caso penal real"""
    casos_prueba = [
        {
            "nombre": "Caso de Homicidio",
            "pregunta": "Juan mató a Pedro con un cuchillo en la madrugada del 15 de enero. Juan tenía premeditación y lo esperó en su casa."
        },
        {
            "nombre": "Caso de Robo",
            "pregunta": "María robó $2000 de una tienda usando un arma de fuego para intimidar al cajero."
        },
        {
            "nombre": "Caso de Hurto Simple",
            "pregunta": "Carlos tomó una billetera que estaba sobre una mesa en un café, cuando el dueño fue al baño."
        }
    ]
    
    for i, caso in enumerate(casos_prueba, 1):
        print(f"\n🏛️ CASO {i}: {caso['nombre']}")
        print("="*60)
        
        try:
            query = {"pregunta": caso["pregunta"]}
            response = requests.post(f"{BASE_URL}/chat", json=query, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Sentencia generada")
                print(f"📋 Fuente: {data.get('fuente')}")
                print(f"🤖 Modelo: {data.get('modelo_usado')}")
                print(f"📄 Tipo documento: {data.get('documento_tipo')}")
                print("\n📝 SENTENCIA:")
                print("-" * 40)
                # Mostrar solo los primeros 500 caracteres para no saturar
                respuesta = data.get('respuesta', '')
                if len(respuesta) > 500:
                    print(respuesta[:500] + "...")
                    print(f"\n[...sentencia completa de {len(respuesta)} caracteres]")
                else:
                    print(respuesta)
                print("-" * 40)
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Error en caso {i}: {e}")

def test_formato_elementos():
    """Verificar que las respuestas tengan todos los elementos de sentencia"""
    print("\n🔍 VERIFICANDO ELEMENTOS DE FORMATO...")
    
    elementos_requeridos = [
        "📅 **FECHA Y HORA:**",
        "⚖️ **RAZÓN DE LA SENTENCIA:**", 
        "🏛️ **VEREDICTO:**",
        "🏢 **LUGAR DE RECLUSIÓN:**",
        "📋 **CONCLUSIÓN:**"
    ]
    
    # Probar con una pregunta simple
    query = {"pregunta": "¿Qué pena tiene el homicidio?"}
    
    try:
        response = requests.post(f"{BASE_URL}/chat", json=query, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            respuesta = data.get('respuesta', '')
            
            elementos_presentes = []
            elementos_faltantes = []
            
            for elemento in elementos_requeridos:
                if elemento in respuesta:
                    elementos_presentes.append(elemento)
                else:
                    elementos_faltantes.append(elemento)
            
            print(f"✅ Elementos presentes ({len(elementos_presentes)}):")
            for elemento in elementos_presentes:
                print(f"   - {elemento}")
            
            if elementos_faltantes:
                print(f"❌ Elementos faltantes ({len(elementos_faltantes)}):")
                for elemento in elementos_faltantes:
                    print(f"   - {elemento}")
            else:
                print("🎉 ¡Todos los elementos de sentencia están presentes!")
                
        else:
            print(f"❌ Error en verificación: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error en verificación de formato: {e}")

def main():
    print("⚖️ PRUEBAS DEL SISTEMA DE SENTENCIAS JUDICIALES")
    print("=" * 60)
    
    # Verificar que el servidor esté activo
    try:
        response = requests.get(f"{BASE_URL}/status", timeout=5)
        if response.status_code != 200:
            print("❌ El servidor no está disponible")
            return
    except:
        print("❌ No se puede conectar al servidor. ¿Está ejecutándose?")
        print("💡 Ejecuta: python app.py")
        return
    
    print("✅ Servidor conectado\n")
    
    # Ejecutar pruebas
    print("1️⃣ PROBANDO SENTENCIA DE EJEMPLO...")
    test_sentencia_ejemplo()
    
    print("\n2️⃣ PROBANDO CASOS PENALES...")
    test_chat_con_caso_penal()
    
    print("\n3️⃣ VERIFICANDO FORMATO...")
    test_formato_elementos()
    
    print("\n🎯 PRUEBAS COMPLETADAS")
    print("\n💡 COMANDOS ÚTILES:")
    print("- Ver sentencia ejemplo: POST /sentencia/ejemplo")
    print("- Consultar caso: POST /chat")
    print("- Ver estado: GET /status")

if __name__ == "__main__":
    main()
