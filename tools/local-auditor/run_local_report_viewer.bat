@echo off
setlocal
set "AUDIT_RUN=%~1"
if "%AUDIT_RUN%"=="" set "AUDIT_RUN=%~dp0output\real_dump_corrected_20260723"
py -3 "%~dp0local_report_viewer.py" --audit-run "%AUDIT_RUN%" --open
endlocal
