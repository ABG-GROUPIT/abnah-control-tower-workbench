$ErrorActionPreference = "Stop"

$atlasRoot = Split-Path -Parent $PSScriptRoot
$referenceRoot = Join-Path (Split-Path -Parent $atlasRoot) "POSist Schema Reference"
$projectRoot = Join-Path (Split-Path -Parent $atlasRoot) "abnah-zoho-synthetic-demo"
$presentationBuilder = Join-Path $projectRoot "scripts\build_control_tower_presentation.py"

if (Get-Command py -ErrorAction SilentlyContinue) {
    if (Test-Path -LiteralPath $presentationBuilder) {
        & py -3 $presentationBuilder --site-root $atlasRoot
    }
    & py -3 "$PSScriptRoot\build_atlas_data.py" --reference-root $referenceRoot --project-root $projectRoot
    & py -3 "$PSScriptRoot\build_workspace_data.py" --root $atlasRoot
    & py -3 "$PSScriptRoot\validate_atlas_data.py"
    & py -3 "$PSScriptRoot\validate_workspace_data.py"
    & py -3 "$PSScriptRoot\validate_control_tower.py"
    & py -3 "$PSScriptRoot\validate_schema_privacy.py"
}
elseif (Get-Command python -ErrorAction SilentlyContinue) {
    if (Test-Path -LiteralPath $presentationBuilder) {
        & python $presentationBuilder --site-root $atlasRoot
    }
    & python "$PSScriptRoot\build_atlas_data.py" --reference-root $referenceRoot --project-root $projectRoot
    & python "$PSScriptRoot\build_workspace_data.py" --root $atlasRoot
    & python "$PSScriptRoot\validate_atlas_data.py"
    & python "$PSScriptRoot\validate_workspace_data.py"
    & python "$PSScriptRoot\validate_control_tower.py"
    & python "$PSScriptRoot\validate_schema_privacy.py"
}
else {
    throw "Python 3 is required to refresh the atlas."
}
