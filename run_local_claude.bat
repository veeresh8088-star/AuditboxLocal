:: title Local Claude Agent (Ollama Mode)
echo ==========================================
echo    DEBUG: Launching Local Claude
echo ==========================================

:: Set the API endpoint to point to local Ollama
set ANTHROPIC_BASE_URL=http://localhost:11434/v1
:: Set a mock key to bypass login checks
set ANTHROPIC_API_KEY=sk-ant-local-1234567890abcdef

echo Checking for claude.exe...
if exist "C:\Users\HP\.local\bin\claude.exe" (
    echo [OK] Found at C:\Users\HP\.local\bin\claude.exe
    "C:\Users\HP\.local\bin\claude.exe" --model llama3.1
) else (
    echo [ERROR] Could not find C:\Users\HP\.local\bin\claude.exe
    echo Attempting to run via NPX instead...
    npx -y @anthropic-ai/claude-code --model llama3.1
)

pause
