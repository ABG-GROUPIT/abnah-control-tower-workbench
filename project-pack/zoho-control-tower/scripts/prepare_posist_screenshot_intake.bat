@echo off
setlocal
cd /d "%~dp0\.."
python scripts\prepare_posist_screenshot_intake.py %*
