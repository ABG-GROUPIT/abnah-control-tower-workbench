@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\refresh_atlas.ps1"
if errorlevel 1 exit /b %errorlevel%
echo.
echo ABNAH Data Discovery Atlas refreshed and validated.
