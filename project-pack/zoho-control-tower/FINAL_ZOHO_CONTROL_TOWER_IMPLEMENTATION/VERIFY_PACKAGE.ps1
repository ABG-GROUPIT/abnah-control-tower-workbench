$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$manifestPath = Join-Path $root 'PACKAGE_MANIFEST.csv'
if (-not (Test-Path -LiteralPath $manifestPath)) {
    throw "Missing PACKAGE_MANIFEST.csv"
}

$manifest = @(Import-Csv -LiteralPath $manifestPath)
foreach ($row in $manifest) {
    $relative = $row.path.Replace('/', [IO.Path]::DirectorySeparatorChar)
    $path = Join-Path $root $relative
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "Missing packaged file: $($row.path)"
    }
    $file = Get-Item -LiteralPath $path
    if ($file.Length -ne [int64]$row.size_bytes) {
        throw "Size mismatch: $($row.path)"
    }
    $hash = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($hash -ne $row.sha256.ToLowerInvariant()) {
        throw "SHA-256 mismatch: $($row.path)"
    }
}

$importDir = Join-Path $root '01_IMPORT_FILES'
$imports = @(
    Get-ChildItem -LiteralPath $importDir -Filter '*.csv' -File |
        Where-Object { $_.Name -ne 'IMPORT_CHECKLIST.csv' }
)
if ($imports.Count -ne 14) {
    throw "Expected 14 import files, found $($imports.Count)"
}

$queryDir = Join-Path $root '02_QUERY_TABLES'
$queries = @(Get-ChildItem -LiteralPath $queryDir -Filter '*.sql' -File)
if ($queries.Count -ne 38) {
    throw "Expected 38 SQL files, found $($queries.Count)"
}
$queryManifest = @(Import-Csv -LiteralPath (Join-Path $queryDir 'QUERY_TABLE_MANIFEST.csv'))
if ($queryManifest.Count -ne 38) {
    throw "Expected 38 Query Table manifest rows, found $($queryManifest.Count)"
}
if (($queryManifest | Measure-Object -Property dependency_level -Maximum).Maximum -gt 3) {
    throw 'A Query Table dependency exceeds level 3'
}

$truthDir = Join-Path $root '04_VALIDATION_AND_LIMITATIONS\TRUTH_PACK'
$truthFiles = @(Get-ChildItem -LiteralPath $truthDir -Filter '*.csv' -File)
if ($truthFiles.Count -ne 12) {
    throw "Expected 12 truth files, found $($truthFiles.Count)"
}

$reconciliation = @(
    Import-Csv -LiteralPath (
        Join-Path $root '04_VALIDATION_AND_LIMITATIONS\_RECONCILIATION_RESULTS.csv'
    )
)
$failedReconciliation = @($reconciliation | Where-Object { $_.status -ne 'PASS' })
if ($failedReconciliation.Count -ne 0) {
    throw "Generator reconciliation contains $($failedReconciliation.Count) failures"
}

$acceptance = @(
    Import-Csv -LiteralPath (
        Join-Path $truthDir 'CONTROL_TOWER_ACCEPTANCE_CHECKS.csv'
    )
)
$failedAcceptance = @($acceptance | Where-Object { $_.status -ne 'PASS' })
if ($failedAcceptance.Count -ne 0) {
    throw "Truth-pack acceptance contains $($failedAcceptance.Count) failures"
}

$required = @(
    '01_IMPORT_FILES\RAWN_CT_vendor_report.csv',
    '02_QUERY_TABLES\10_std_ct_vendor_report.sql',
    '03_ZOHO_INSTRUCTIONS\03A_LOOKUPS_FORMULAS_AND_PRE_DASHBOARD_SETUP.md',
    '03_ZOHO_INSTRUCTIONS\04_DASHBOARD_BUILD.md',
    '03_ZOHO_INSTRUCTIONS\05_ASK_ZIA_SETUP.md'
)
foreach ($relative in $required) {
    if (-not (Test-Path -LiteralPath (Join-Path $root $relative) -PathType Leaf)) {
        throw "Missing required implementation asset: $relative"
    }
}

Write-Host ''
Write-Host 'FINAL ZOHO PACKAGE: PASS' -ForegroundColor Green
Write-Host "Payload files verified: $($manifest.Count)"
Write-Host 'Active imports: 14'
Write-Host 'Query Tables: 38'
Write-Host 'Truth files: 12'
