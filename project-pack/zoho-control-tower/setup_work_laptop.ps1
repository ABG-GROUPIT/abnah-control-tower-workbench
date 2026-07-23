[CmdletBinding()]
param(
    [switch]$WithOcr,
    [switch]$Regenerate,
    [switch]$SkipTests
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $root

if (Get-Command py.exe -ErrorAction SilentlyContinue) {
    & py -3 -m venv .venv
} elseif (Get-Command python.exe -ErrorAction SilentlyContinue) {
    & python -m venv .venv
} else {
    throw "Python 3.11 or newer is required."
}

$python = Join-Path $root ".venv\Scripts\python.exe"
& $python -m pip install --upgrade pip
& $python -m pip install -r requirements.txt

if ($WithOcr) {
    & $python -m pip install -r requirements-ocr.txt
}

if (-not (Test-Path -LiteralPath ".env")) {
    Copy-Item -LiteralPath ".env.example" -Destination ".env"
}

if ($Regenerate) {
    & $python -m generator.generate_all
    & $python scripts\build_control_tower_v2_sql.py
    & $python scripts\build_control_tower_truth_pack.py
}

& $python scripts\check_repository_safety.py

if (-not $SkipTests) {
    & $python -m unittest discover -s tests -v
    & $python -m unittest discover -s local_data_auditor\tests -v
}

Write-Host ""
Write-Host "ABNAH project setup is complete." -ForegroundColor Green
Write-Host "Zoho package: exports\control_tower_zoho"
Write-Host "Execution runbook: docs\ZOHO_CONTROL_TOWER_V2_EXECUTION_RUNBOOK.md"
Write-Host "Local CSV drop: local_data_auditor\input"
