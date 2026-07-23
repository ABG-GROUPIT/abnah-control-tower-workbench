$ErrorActionPreference = "Stop"

$atlasRoot = Split-Path -Parent $PSScriptRoot
$parentRoot = Split-Path -Parent $atlasRoot
$referenceRoot = Join-Path $parentRoot "POSist Schema Reference"
$bundledProjectRoot = Join-Path $atlasRoot "project-pack\zoho-control-tower"
$siblingProjectRoot = Join-Path $parentRoot "abnah-zoho-synthetic-demo"
$projectRoot = if (Test-Path -LiteralPath $bundledProjectRoot) {
    $bundledProjectRoot
}
else {
    $siblingProjectRoot
}
$presentationBuilder = Join-Path $projectRoot "scripts\build_control_tower_presentation.py"
$referenceIndex = Join-Path $referenceRoot "indexes\report_master_index.csv"

if (Get-Command py -ErrorAction SilentlyContinue) {
    if (Test-Path -LiteralPath $presentationBuilder) {
        & py -3 $presentationBuilder --site-root $atlasRoot
    }
    if (Test-Path -LiteralPath $referenceIndex) {
        & py -3 "$PSScriptRoot\build_atlas_data.py" --reference-root $referenceRoot --project-root $projectRoot
    }
    else {
        Write-Host "POSist source indexes are local-only; retaining the committed portable discovery baseline."
    }
    & py -3 "$PSScriptRoot\build_workspace_data.py" --root $atlasRoot
    & py -3 "$PSScriptRoot\validate_atlas_data.py"
    & py -3 "$PSScriptRoot\validate_workspace_data.py"
    & py -3 "$PSScriptRoot\validate_control_tower.py"
    & py -3 "$PSScriptRoot\validate_schema_privacy.py"
    & py -3 "$PSScriptRoot\validate_project_pack.py"
}
elseif (Get-Command python -ErrorAction SilentlyContinue) {
    if (Test-Path -LiteralPath $presentationBuilder) {
        & python $presentationBuilder --site-root $atlasRoot
    }
    if (Test-Path -LiteralPath $referenceIndex) {
        & python "$PSScriptRoot\build_atlas_data.py" --reference-root $referenceRoot --project-root $projectRoot
    }
    else {
        Write-Host "POSist source indexes are local-only; retaining the committed portable discovery baseline."
    }
    & python "$PSScriptRoot\build_workspace_data.py" --root $atlasRoot
    & python "$PSScriptRoot\validate_atlas_data.py"
    & python "$PSScriptRoot\validate_workspace_data.py"
    & python "$PSScriptRoot\validate_control_tower.py"
    & python "$PSScriptRoot\validate_schema_privacy.py"
    & python "$PSScriptRoot\validate_project_pack.py"
}
else {
    throw "Python 3 is required to refresh the atlas."
}
