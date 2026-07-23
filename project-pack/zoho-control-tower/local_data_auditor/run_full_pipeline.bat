@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "INPUT_DIR=%~1"
set "MODEL=%~2"
set "NUM_CTX=%~3"
set "KEEP_ALIVE=%~4"

if not defined INPUT_DIR set "INPUT_DIR=%SCRIPT_DIR%input"
if not defined MODEL set "MODEL=qwen3:14b"
if not defined NUM_CTX set "NUM_CTX=32768"
if not defined KEEP_ALIVE set "KEEP_ALIVE=0"

where py >nul 2>&1
if %errorlevel% equ 0 (
  py -3 "%SCRIPT_DIR%run_pipeline.py" --input "%INPUT_DIR%" --model "%MODEL%" --num-ctx "%NUM_CTX%" --keep-alive "%KEEP_ALIVE%"
) else (
  python "%SCRIPT_DIR%run_pipeline.py" --input "%INPUT_DIR%" --model "%MODEL%" --num-ctx "%NUM_CTX%" --keep-alive "%KEEP_ALIVE%"
)

exit /b %errorlevel%
