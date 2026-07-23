@echo off
setlocal

if "%~1"=="" (
  echo Usage: run_laptop_pipeline.bat "D:\path\to\CSV_DROP"
  exit /b 2
)

call "%~dp0run_full_pipeline.bat" "%~1" qwen2.5:7b-instruct 8192 5m
exit /b %errorlevel%
