$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$demoRoot = Split-Path -Parent $scriptRoot
$builder = Join-Path $scriptRoot "build_databridge_demo_workbooks.mjs"
$node = "C:\Users\ARNAV\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe"
$bundledModules = "C:\Users\ARNAV\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\node_modules"
$tempRoot = Join-Path $env:TEMP ("abnah-databridge-builder-" + [guid]::NewGuid().ToString("N"))

New-Item -ItemType Directory -Path $tempRoot -Force | Out-Null
Copy-Item -LiteralPath $builder -Destination (Join-Path $tempRoot "builder.mjs")
New-Item -ItemType Junction -Path (Join-Path $tempRoot "node_modules") -Target $bundledModules | Out-Null

try {
    & $node (Join-Path $tempRoot "builder.mjs") $demoRoot
    if ($LASTEXITCODE -ne 0) {
        throw "Workbook build failed with exit code $LASTEXITCODE."
    }
}
finally {
    $resolvedTemp = [System.IO.Path]::GetFullPath($tempRoot)
    $resolvedBase = [System.IO.Path]::GetFullPath($env:TEMP)
    if ($resolvedTemp.StartsWith($resolvedBase, [System.StringComparison]::OrdinalIgnoreCase)) {
        Remove-Item -LiteralPath $resolvedTemp -Recurse -Force
    }
}
