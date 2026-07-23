@echo off
setlocal
cd /d "%~dp0.."
set "INPUT_DIR=%USERPROFILE%\OneDrive\Desktop\ABNAH_POSIST_SCREENSHOTS\p1_main"
if not exist "%INPUT_DIR%" set "INPUT_DIR=%USERPROFILE%\Desktop\ABNAH_POSIST_SCREENSHOTS\p1_main"
if not exist "%INPUT_DIR%" (
  echo Input folder not found: "%INPUT_DIR%"
  exit /b 1
)
if exist ".venv-ocr39\Scripts\python.exe" (
  ".venv-ocr39\Scripts\python.exe" scripts\run_posist_screenshot_extraction.py --input "%INPUT_DIR%"
) else if exist ".venv-ocr\Scripts\python.exe" (
  ".venv-ocr\Scripts\python.exe" scripts\run_posist_screenshot_extraction.py --input "%INPUT_DIR%"
) else (
  python scripts\run_posist_screenshot_extraction.py --input "%INPUT_DIR%"
)
endlocal
