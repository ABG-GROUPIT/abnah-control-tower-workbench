@echo off
setlocal

where ollama >nul 2>&1
if %errorlevel% neq 0 (
  echo Ollama is not installed or not available on PATH.
  echo Install Ollama, then rerun this command.
  exit /b 1
)

echo Pulling the recommended local analyst/verifier model...
ollama pull qwen3:14b
if %errorlevel% neq 0 exit /b %errorlevel%

echo.
echo Ready. Run run_full_pipeline.bat with the CSV drop folder.
