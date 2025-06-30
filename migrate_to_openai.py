#!/usr/bin/env python3
"""
Script para migrar de Google Gemini a OpenAI
"""

import subprocess
import sys
import os
from pathlib import Path

def install_openai():
    """Instalar OpenAI package"""
    try:
        print("📦 Instalando OpenAI...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "openai"])
        print("✅ OpenAI instalado exitosamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al instalar OpenAI: {e}")
        return False

def check_env_file():
    """Verificar archivo .env"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        if env_example.exists():
            print("📋 Copiando .env.example a .env...")
            import shutil
            shutil.copy(env_example, env_file)
            print("✅ Archivo .env creado")
            print("⚠️  IMPORTANTE: Edita el archivo .env y agrega tu OPENAI_API_KEY")
        else:
            print("❌ No se encontró .env.example")
            return False
    else:
        print("✅ Archivo .env encontrado")
        
        # Verificar si tiene OPENAI_API_KEY
        with open(env_file, 'r') as f:
            content = f.read()
            
        if "OPENAI_API_KEY" not in content:
            print("⚠️  Agregando configuración de OpenAI al .env...")
            with open(env_file, 'a') as f:
                f.write("\n# Configuración de OpenAI\n")
                f.write("OPENAI_API_KEY=tu_api_key_de_openai_aqui\n")
                f.write("OPENAI_MODEL=gpt-3.5-turbo\n")
            print("✅ Configuración agregada al .env")
            print("⚠️  IMPORTANTE: Edita el archivo .env y agrega tu OPENAI_API_KEY real")
    
    return True

def test_migration():
    """Probar que la migración funciona"""
    try:
        print("🧪 Probando importación de OpenAI...")
        import openai
        print("✅ OpenAI se importa correctamente")
        return True
    except ImportError as e:
        print(f"❌ Error al importar OpenAI: {e}")
        return False

def show_next_steps():
    """Mostrar próximos pasos"""
    print("\n🎯 PRÓXIMOS PASOS:")
    print("1. Obtén tu API key de OpenAI en: https://platform.openai.com/api-keys")
    print("2. Edita el archivo .env y reemplaza 'tu_api_key_de_openai_aqui' con tu API key real")
    print("3. (Opcional) Cambia OPENAI_MODEL si quieres usar GPT-4 o otro modelo")
    print("4. Reinicia el servidor: python app.py")
    print("5. Prueba el endpoint: GET /status para verificar la conexión")
    
    print("\n💰 INFORMACIÓN DE COSTOS:")
    print("- GPT-3.5-turbo: ~$0.002 por 1K tokens (más económico)")
    print("- GPT-4o-mini: ~$0.15 por 1M tokens de entrada, $0.60 por 1M tokens de salida")
    print("- GPT-4: ~$30 por 1M tokens de entrada, $60 por 1M tokens de salida")
    
    print("\n🔧 COMANDOS ÚTILES:")
    print("- Cambiar modelo: POST /configuracion/modelo")
    print("- Ver modelo actual: GET /configuracion/modelo")
    print("- Probar sistema: python test_upload.py")

def main():
    print("🚀 Iniciando migración de Google Gemini a OpenAI\n")
    
    # Paso 1: Instalar OpenAI
    if not install_openai():
        return
    
    # Paso 2: Configurar .env
    if not check_env_file():
        return
        
    # Paso 3: Probar migración
    if not test_migration():
        return
    
    # Paso 4: Mostrar próximos pasos
    show_next_steps()
    
    print("\n✅ ¡Migración completada exitosamente!")

if __name__ == "__main__":
    main()
