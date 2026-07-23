@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "INPUT_DIR=%~1"
set "OUTPUT_DIR=%~2"

if not defined INPUT_DIR set "INPUT_DIR=%SCRIPT_DIR%input"

where py >nul 2>&1
if %errorlevel% equ 0 (
  if defined OUTPUT_DIR (
    py -3 "%SCRIPT_DIR%audit.py" --input "%INPUT_DIR%" --output "%OUTPUT_DIR%"
  ) else (
    py -3 "%SCRIPT_DIR%audit.py" --input "%INPUT_DIR%"
  )
) else (
  if defined OUTPUT_DIR (
    python "%SCRIPT_DIR%audit.py" --input "%INPUT_DIR%" --output "%OUTPUT_DIR%"
  ) else (
    python "%SCRIPT_DIR%audit.py" --input "%INPUT_DIR%"
  )
)

exit /b %errorlevel%
