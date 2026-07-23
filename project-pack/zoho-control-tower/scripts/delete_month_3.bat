@echo off
setlocal
cd /d "%~dp0\.."
python manage_demo.py delete-month 3

