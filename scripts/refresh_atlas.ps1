$ErrorActionPreference = "Stop"

$atlasRoot = Split-Path -Parent $PSScriptRoot
$referenceRoot = Join-Path (Split-Path -Parent $atlasRoot) "POSist Schema Reference"
$projectRoot = Join-Path (Split-Path -Parent $atlasRoot) "abnah-zoho-synthetic-demo"

if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 "$PSScriptRoot\build_atlas_data.py" --reference-root $referenceRoot --project-root $projectRoot
    & py -3 "$PSScriptRoot\build_workspace_data.py" --root $atlasRoot
    & py -3 "$PSScriptRoot\validate_atlas_data.py"
    & py -3 "$PSScriptRoot\validate_workspace_data.py"
    & py -3 "$PSScriptRoot\validate_schema_privacy.py"
}
elseif (Get-Command python -ErrorAction SilentlyContinue) {
    & python "$PSScriptRoot\build_atlas_data.py" --reference-root $referenceRoot --project-root $projectRoot
    & python "$PSScriptRoot\build_workspace_data.py" --root $atlasRoot
    & python "$PSScriptRoot\validate_atlas_data.py"
    & python "$PSScriptRoot\validate_workspace_data.py"
    & python "$PSScriptRoot\validate_schema_privacy.py"
}
else {
    throw "Python 3 is required to refresh the atlas."
}
