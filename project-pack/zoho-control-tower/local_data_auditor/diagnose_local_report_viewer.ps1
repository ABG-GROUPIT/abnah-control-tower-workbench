param(
    [int]$Port = 8765
)

$ErrorActionPreference = "Stop"
$healthUrl = "http://127.0.0.1:$Port/health"

Write-Host "ABNAH local reviewer diagnostics"
Write-Host "Laptop: $env:COMPUTERNAME"
Write-Host "Expected address: $healthUrl"

$python = Get-Command py -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Error 'Python launcher "py" is unavailable. Install or request Python 3.'
}

Write-Host "Python:"
& py -3 --version

try {
    $health = Invoke-RestMethod -Uri $healthUrl -TimeoutSec 3
    Write-Host "Reviewer status: RUNNING"
    $health | ConvertTo-Json -Depth 3
    exit 0
}
catch {
    Write-Host "Reviewer status: NOT REACHABLE"
}

$listener = Get-NetTCPConnection -LocalAddress 127.0.0.1 -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if ($listener) {
    Write-Host "Port $Port is occupied by process $($listener.OwningProcess), but it is not the ABNAH reviewer."
}
else {
    Write-Host "Nothing is listening on port $Port."
}

Write-Host ""
Write-Host "Run run_local_report_viewer.bat on this same laptop and leave its window open."
Write-Host "A localhost URL on another PC cannot reach the reviewer running here."
exit 1
