@echo off
title AICyberAuditBox Demo Launcher
echo ==========================================
echo    AICyberAuditBox
echo ==========================================

echo.
echo [1/3] Checking Ollama (AI Engine)...
python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:11434/', timeout=2)" >nul 2>&1
if %errorlevel% neq 0 (
    echo [i] NOTE: Ollama is not running. Starting it automatically...
    start "" "%localappdata%\Programs\Ollama\ollama app.exe"
    echo Waiting for Ollama to initialize...
    timeout /t 6 >nul
) else (
    echo [v] OK: Ollama is active.
)

echo.
echo [2/3] Checking Database (ShaktiDB)...
docker ps > nul 2>&1
if %errorlevel% equ 0 (
    echo [v] OK: Docker is running. Starting ShaktiDB container...
    docker rm -f shakthidb_service > nul 2>&1
    docker-compose up -d
) else (
    echo [i] NOTE: Docker Desktop not detected. 
    echo     The system will automatically use 'shakthidb_local.db' ^(SQLite^).
)

echo.
echo [3/3] Launching Dashboard...
echo Installing/Updating dependencies...
pip install -r requirements.txt --quiet
python -m streamlit run app.py --server.port 8501
