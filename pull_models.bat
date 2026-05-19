@echo off
title Pulling Offline AI Models (7B/8B Class)
echo ==========================================
echo    AICyberAuditBox - High Performance Models
echo ==========================================
echo.
echo Downloading high-performance models (7B/8B parameters).
echo These are excellent for reasoning, document auditing, and run on CPU with 16GB RAM.
echo.

echo [1/2] Downloading Llama 3.1 (8B) [~4.7 GB]...
ollama pull llama3.1

echo.
echo [2/2] Downloading Qwen 2.5 (7B) [~4.7 GB]...
ollama pull qwen2.5:7b

echo.
echo ==========================================
echo All selected models have been pulled!
pause
