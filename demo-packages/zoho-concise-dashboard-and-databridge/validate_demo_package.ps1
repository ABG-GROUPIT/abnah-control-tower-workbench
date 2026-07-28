$ErrorActionPreference = "Stop"

$packageRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$queryRoot = Join-Path $packageRoot "dashboard-demo\queries"
$manifestPath = Join-Path $packageRoot "dashboard-demo\QUERY_MANIFEST.csv"

$expectedQueries = @(
    "D01_demo_p1_action_queue.sql",
    "D02_demo_p1_menu_impact.sql",
    "D03_demo_p1_expiry_watch.sql",
    "D04_demo_p2_po_control.sql",
    "D05_demo_p2_vendor_control.sql",
    "D06_demo_p2_price_watch.sql"
)

$requiredP1Filters = @(
    '"filter_date"',
    '"filter_outlet"',
    '"filter_category"',
    '"filter_severity"'
)

$requiredP2Filters = @(
    '"filter_date"',
    '"filter_outlet"',
    '"filter_vendor"',
    '"filter_category"'
)

$forbiddenLevelThreeSources = @(
    '"27_fact_ct_inventory_risk.sql"',
    '"28_fact_ct_menu_impact.sql"',
    '"30_sum_ct_vendor_scorecard.sql"',
    '"31_sum_ct_price_movement.sql"',
    '"38_fact_ct_expiry_risk.sql"'
)

foreach ($queryName in $expectedQueries) {
    $queryPath = Join-Path $queryRoot $queryName
    if (-not (Test-Path -LiteralPath $queryPath)) {
        throw "Missing query: $queryName"
    }

    $sql = Get-Content -LiteralPath $queryPath -Raw
    if (-not $sql.TrimEnd().EndsWith(";")) {
        throw "Query does not end with a semicolon: $queryName"
    }

    $openParentheses = ([regex]::Matches($sql, "\(")).Count
    $closeParentheses = ([regex]::Matches($sql, "\)")).Count
    if ($openParentheses -ne $closeParentheses) {
        throw "Unbalanced parentheses in $queryName"
    }

    foreach ($source in $forbiddenLevelThreeSources) {
        if ($sql.Contains($source)) {
            throw "$queryName creates an unsafe dependency on $source"
        }
    }

    $requiredFilters = if ($queryName.StartsWith("D0") -and
        [int]$queryName.Substring(2, 1) -le 3) {
        $requiredP1Filters
    }
    else {
        $requiredP2Filters
    }

    foreach ($filterColumn in $requiredFilters) {
        if (-not $sql.Contains($filterColumn)) {
            throw "$queryName is missing $filterColumn"
        }
    }
}

$manifest = Import-Csv -LiteralPath $manifestPath
if ($manifest.Count -ne 6) {
    throw "Manifest must contain exactly six Query Tables."
}

foreach ($row in $manifest) {
    if ([int]$row.dependency_level -gt 3) {
        throw "Dependency level exceeds 3 for $($row.query_table_name)."
    }
    if ($row.query_table_name -notin $expectedQueries) {
        throw "Unexpected Query Table in manifest: $($row.query_table_name)"
    }
}

$workbooks = Get-ChildItem -LiteralPath (
    Join-Path $packageRoot "data-bridge-demo"
) -Recurse -Filter "*.xlsx"

if ($workbooks.Count -ne 7) {
    throw "Expected seven DataBridge workbooks; found $($workbooks.Count)."
}

Write-Output "PASS: 6 isolated Query Tables, dependency ceiling 3, filter contracts present."
Write-Output "PASS: 7 DataBridge workbooks present."
