@echo off
setlocal
cd /d "%~dp0.."
if exist ".venv-ocr39\Scripts\python.exe" (
  ".venv-ocr39\Scripts\python.exe" scripts\run_posist_screenshot_extraction.py %*
) else if exist ".venv-ocr\Scripts\python.exe" (
  ".venv-ocr\Scripts\python.exe" scripts\run_posist_screenshot_extraction.py %*
) else (
  python scripts\run_posist_screenshot_extraction.py %*
)
endlocal
