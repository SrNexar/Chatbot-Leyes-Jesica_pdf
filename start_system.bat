@echo off
title Chatbot Legal - Iniciador del Sistema
color 0A

echo.
echo             CHATBOT LEGAL CON IA - SISTEMA COMPLETO 
echo                   Backend: FastAPI + MongoDB + Qdrant
echo                   Frontend: React Native + Expo
echo.
echo ==================================================================

:MENU
echo.
echo Selecciona una opción:
echo.
echo 1.  Iniciar solo el BACKEND (FastAPI)
echo 2.  Iniciar solo el FRONTEND (React Native)
echo 3.  Iniciar BACKEND y FRONTEND juntos
echo 4.  Ver estado de los servicios
echo 5.  Ver documentación de la API
echo 6.  Salir
echo.
set /p choice="Ingresa tu opción (1-6): "

if "%choice%"=="1" goto START_BACKEND
if "%choice%"=="2" goto START_FRONTEND
if "%choice%"=="3" goto START_BOTH
if "%choice%"=="4" goto STATUS
if "%choice%"=="5" goto DOCS
if "%choice%"=="6" goto EXIT

echo  Opción inválida. Por favor selecciona 1-6.
goto MENU

:START_BACKEND
echo.
echo  INICIANDO BACKEND (FastAPI)...
echo ==================================
echo.

REM Activar entorno virtual y ejecutar FastAPI
start "Backend - FastAPI" cmd /k "title Backend FastAPI && .\venv\Scripts\activate && echo Backend iniciado en http://localhost:8000 && echo Documentación en http://localhost:8000/docs && C:/Users/nexar/Desktop/finalll/Chatbot-Leyes-Jesica_pdf/venv/Scripts/python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

echo  Backend iniciado en una nueva ventana
echo  URL: http://localhost:8000
echo  Docs: http://localhost:8000/docs
echo.
pause
goto MENU

:START_FRONTEND
echo.
echo  INICIANDO FRONTEND (React Native)...
echo =====================================
echo.

REM Cambiar al directorio del frontend e iniciar
start "Frontend - React Native" cmd /k "title Frontend React Native && cd justicIA-Front-main && echo Frontend iniciando... && echo Web: http://localhost:8081 && npx expo start --web --port 8081"

echo  Frontend iniciado en una nueva ventana
echo  Web: http://localhost:8081
echo  Expo Go: Escanea el código QR
echo.
pause
goto MENU

:START_BOTH
echo.
echo  INICIANDO BACKEND Y FRONTEND...
echo =================================
echo.

echo  Iniciando Backend (FastAPI)...
start "Backend - FastAPI" cmd /k "title Backend FastAPI && .\venv\Scripts\activate && echo ✅ Backend FastAPI iniciado && echo 📍 http://localhost:8000 && echo 📚 http://localhost:8000/docs && C:/Users/nexar/Desktop/finalll/Chatbot-Leyes-Jesica_pdf/venv/Scripts/python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak >nul

echo  Iniciando Frontend (React Native)...
start "Frontend - React Native" cmd /k "title Frontend React Native && cd justicIA-Front-main && echo ✅ Frontend React Native iniciado && echo 📍 Web: http://localhost:8081 && echo 📱 Expo Go: Escanea QR && npx expo start --web --port 8081"

echo.
echo  SISTEMA COMPLETO INICIADO
echo =============================
echo  Backend:  http://localhost:8000
echo  Frontend: http://localhost:8081
echo  API Docs: http://localhost:8000/docs
echo.
echo  Ambos servicios están ejecutándose en ventanas separadas
echo  Para detener los servicios, cierra las ventanas o presiona Ctrl+C
echo.
pause
goto MENU

:STATUS
echo.
echo  VERIFICANDO ESTADO DE LOS SERVICIOS...
echo =========================================
echo.

REM Verificar si el puerto 8000 está ocupado (Backend)
netstat -an | find "8000" | find "LISTENING" >nul
if %ERRORLEVEL%==0 (
    echo  Backend: EJECUTÁNDOSE (Puerto 8000)
) else (
    echo  Backend: NO EJECUTÁNDOSE
)

REM Verificar si el puerto 8081 está ocupado (Frontend)
netstat -an | find "8081" | find "LISTENING" >nul
if %ERRORLEVEL%==0 (
    echo  Frontend: EJECUTÁNDOSE (Puerto 8081)
) else (
    echo  Frontend: NO EJECUTÁNDOSE
)

echo.
echo  URLs disponibles:
echo - Backend API: http://localhost:8000
echo - Frontend Web: http://localhost:8081
echo - Documentación: http://localhost:8000/docs
echo.
pause
goto MENU

:DOCS
echo.
echo  ABRIENDO DOCUMENTACIÓN DE LA API...
echo ======================================
echo.

REM Verificar si el backend está ejecutándose
netstat -an | find "8000" | find "LISTENING" >nul
if %ERRORLEVEL%==0 (
    echo  Abriendo http://localhost:8000/docs en el navegador...
    start http://localhost:8000/docs
) else (
    echo  El backend no está ejecutándose
    echo  Inicia primero el backend (opción 1 o 3)
)

echo.
pause
goto MENU

:EXIT
echo.
echo  ¡Gracias por usar el Chatbot Legal!
echo =====================================
echo.
echo Para detener los servicios completamente:
echo 1. Cierra las ventanas del Backend y Frontend
echo 2. O presiona Ctrl+C en cada una
echo.
echo Desarrollado con ❤️ usando FastAPI y React Native
echo.
pause
exit
