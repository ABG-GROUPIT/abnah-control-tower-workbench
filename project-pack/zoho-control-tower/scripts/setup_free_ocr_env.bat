@echo off
setlocal
cd /d "%~dp0.."
where py >nul 2>nul
if %errorlevel%==0 (
  py -3.9 -m venv .venv-ocr39
  call .venv-ocr39\Scripts\activate.bat
) else (
  python -m venv .venv-ocr
  call .venv-ocr\Scripts\activate.bat
)
python -m pip install --upgrade pip
python -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements-ocr.txt
python scripts\check_free_ocr_tools.py
endlocal
