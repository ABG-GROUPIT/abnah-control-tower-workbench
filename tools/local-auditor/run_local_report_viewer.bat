@echo off
setlocal
set "AUDIT_RUN=%~1"
if "%AUDIT_RUN%"=="" set "AUDIT_RUN=%~dp0output\real_dump_corrected_20260723"
set "VIEWER_PORT=%ABNAH_VIEWER_PORT%"
if "%VIEWER_PORT%"=="" set "VIEWER_PORT=8765"

where py >nul 2>nul
if errorlevel 1 (
  echo [ABNAH reviewer] Python launcher "py" is not available on this laptop.
  echo Install or request Python 3, then run this file again.
  pause
  exit /b 1
)

if not exist "%AUDIT_RUN%\LOCAL_EVIDENCE_DO_NOT_UPLOAD\full_profiles_with_local_samples.json" (
  echo [ABNAH reviewer] Completed audit evidence was not found:
  echo %AUDIT_RUN%
  echo Run run_laptop_pipeline.bat first, or pass a completed audit-run folder.
  pause
  exit /b 1
)

echo [ABNAH reviewer] Starting on this laptop at http://127.0.0.1:%VIEWER_PORT%/
echo [ABNAH reviewer] Leave this window open while reviewing.
py -3 "%~dp0local_report_viewer.py" --audit-run "%AUDIT_RUN%" --port "%VIEWER_PORT%" --open
if errorlevel 1 (
  echo.
  echo [ABNAH reviewer] Startup failed. Run diagnose_local_report_viewer.ps1 for details.
  pause
)
endlocal
