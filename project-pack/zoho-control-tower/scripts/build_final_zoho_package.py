from __future__ import annotations

import csv
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_NAME = "FINAL_ZOHO_CONTROL_TOWER_IMPLEMENTATION"
PACKAGE = ROOT / PACKAGE_NAME
EXPORTS = ROOT / "exports" / "control_tower_zoho"
ACTIVE_MANIFEST = EXPORTS / "_CONTROL_TOWER_ACTIVE_IMPORT_MANIFEST.csv"
SQL_SOURCE = ROOT / "docs" / "zoho_control_tower_v2_sql"
TRUTH_SOURCE = EXPORTS / "truth"
CONTRACT_SOURCE = ROOT / "local_data_auditor" / "contracts"
ZOHO_IMPORT_TABLE_SUFFIX = "-Copy"
EXPECTED_ACTIVE_IMPORTS = 14
EXPECTED_QUERY_TABLES = 38
EXPECTED_TRUTH_FILES = 13

INSTRUCTION_FILES = (
    (
        ROOT / "docs" / "ZOHO_CONTROL_TOWER_V2_EXECUTION_RUNBOOK.md",
        "01_EXECUTION_RUNBOOK.md",
    ),
    (
        ROOT / "docs" / "zoho_control_tower_v2_import.md",
        "02_IMPORT_PROCEDURE.md",
    ),
    (
        ROOT / "docs" / "zoho_control_tower_v2_query_build.md",
        "03_QUERY_TABLE_BUILD.md",
    ),
    (
        ROOT
        / "docs"
        / "ZOHO_LOOKUPS_AGGREGATE_FORMULAS_AND_PRE_DASHBOARD_SETUP.md",
        "03A_LOOKUPS_FORMULAS_AND_PRE_DASHBOARD_SETUP.md",
    ),
    (
        ROOT / "docs" / "zoho_control_tower_v2_dashboard_click_by_click.md",
        "04_DASHBOARD_BUILD.md",
    ),
    (
        ROOT / "docs" / "ZOHO_DASHBOARD_EXPECTED_RESULTS.md",
        "04A_DASHBOARD_EXPECTED_RESULTS.md",
    ),
    (
        ROOT / "docs" / "zoho_control_tower_v2_ask_zia.md",
        "05_ASK_ZIA_SETUP.md",
    ),
    (
        ROOT / "docs" / "zoho_control_tower_v2_validation.md",
        "06_VALIDATION_AND_PUBLICATION.md",
    ),
)

VALIDATION_FILES = (
    (
        ACTIVE_MANIFEST,
        "_CONTROL_TOWER_ACTIVE_IMPORT_MANIFEST.csv",
    ),
    (
        EXPORTS / "_RECONCILIATION_RESULTS.csv",
        "_RECONCILIATION_RESULTS.csv",
    ),
    (
        EXPORTS / "_SYNTHETIC_FIDELITY_REGISTER.csv",
        "_SYNTHETIC_FIDELITY_REGISTER.csv",
    ),
    (
        ROOT / "docs" / "control_tower_v2_source_kpi_matrix.csv",
        "SOURCE_KPI_MATRIX.csv",
    ),
    (
        ROOT / "docs" / "control_tower_synthetic_fidelity.md",
        "SYNTHETIC_FIDELITY.md",
    ),
    (
        ROOT / "docs" / "control_tower_synthetic_validation.md",
        "SYNTHETIC_VALIDATION.md",
    ),
    (
        ROOT / "docs" / "CONTROL_TOWER_SOURCE_FEASIBILITY_GATE.md",
        "SOURCE_FEASIBILITY_AND_LIMITATIONS.md",
    ),
    (
        ROOT / "docs" / "ACTUAL_CSV_SEMANTIC_REASSESSMENT.md",
        "ACTUAL_CSV_SEMANTIC_REASSESSMENT.md",
    ),
    (
        ROOT / "docs" / "CONTROL_TOWER_PRESENTATION_ISSUES.md",
        "PRESENTATION_ISSUES.md",
    ),
    (
        ROOT / "docs" / "VENDOR_LAST_5_PURCHASE_PRICE_ASSESSMENT.md",
        "VENDOR_LAST_5_PURCHASE_PRICE_ASSESSMENT.md",
    ),
    (
        ROOT / "docs" / "control_tower_v2_truth_reference.md",
        "TRUTH_REFERENCE.md",
    ),
)


def read_dict_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_dict_rows(
    path: Path,
    fieldnames: list[str],
    rows: list[dict[str, object]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def csv_shape(path: Path) -> tuple[int, int]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        row_count = sum(1 for _ in reader)
    return row_count, len(header)


def copy_required(source: Path, destination: Path) -> None:
    if not source.is_file():
        raise FileNotFoundError(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def copy_text_required(source: Path, destination: Path) -> None:
    if not source.is_file():
        raise FileNotFoundError(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    text = source.read_text(encoding="utf-8-sig")
    with destination.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def safe_recreate_package() -> None:
    root = ROOT.resolve()
    target = PACKAGE.resolve()
    if target.parent != root or target.name != PACKAGE_NAME:
        raise RuntimeError(f"Refusing to recreate unexpected path: {target}")
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)


def build_import_folder() -> tuple[list[dict[str, str]], list[dict[str, object]]]:
    active_rows = read_dict_rows(ACTIVE_MANIFEST)
    if len(active_rows) != EXPECTED_ACTIVE_IMPORTS:
        raise RuntimeError(
            f"Expected {EXPECTED_ACTIVE_IMPORTS} active imports, "
            f"found {len(active_rows)}"
        )

    destination = PACKAGE / "01_IMPORT_FILES"
    checklist: list[dict[str, object]] = []
    for order, row in enumerate(active_rows, start=1):
        relative_source = Path(row["zoho_import_file"])
        if relative_source.parts[0].lower() == "normalized":
            source = EXPORTS / relative_source
        else:
            source = EXPORTS / relative_source.name
        target = destination / source.name
        copy_required(source, target)

        actual_rows, column_count = csv_shape(target)
        expected_rows = int(row["row_count"])
        if actual_rows != expected_rows:
            raise RuntimeError(
                f"{source.name}: expected {expected_rows} rows, found {actual_rows}"
            )
        checklist.append(
            {
                "build_order": order,
                "zoho_table_name": source.stem + ZOHO_IMPORT_TABLE_SUFFIX,
                "file_name": source.name,
                "expected_rows": expected_rows,
                "expected_columns": column_count,
                "source_role": row["active_v2_role"],
                "status": "NOT_STARTED",
                "actual_rows": "",
                "rejected_rows": "",
                "implemented_by": "",
                "implemented_on": "",
                "notes": "",
            }
        )

    write_dict_rows(
        destination / "IMPORT_CHECKLIST.csv",
        [
            "build_order",
            "zoho_table_name",
            "file_name",
            "expected_rows",
            "expected_columns",
            "source_role",
            "status",
            "actual_rows",
            "rejected_rows",
            "implemented_by",
            "implemented_on",
            "notes",
        ],
        checklist,
    )
    return active_rows, checklist


def build_query_folder() -> list[dict[str, str]]:
    destination = PACKAGE / "02_QUERY_TABLES"
    query_rows = read_dict_rows(SQL_SOURCE / "QUERY_TABLE_MANIFEST.csv")
    if len(query_rows) != EXPECTED_QUERY_TABLES:
        raise RuntimeError(
            f"Expected {EXPECTED_QUERY_TABLES} Query Tables, "
            f"found {len(query_rows)}"
        )

    for row in query_rows:
        copy_text_required(
            SQL_SOURCE / row["sql_file"],
            destination / row["sql_file"],
        )
    copy_text_required(
        SQL_SOURCE / "QUERY_TABLE_MANIFEST.csv",
        destination / "QUERY_TABLE_MANIFEST.csv",
    )
    copy_text_required(SQL_SOURCE / "README.md", destination / "README.md")

    checklist: list[dict[str, object]] = []
    for row in query_rows:
        checklist.append(
            {
                **row,
                "status": "NOT_STARTED",
                "preview_row_count": "",
                "implemented_by": "",
                "implemented_on": "",
                "notes": "",
            }
        )
    write_dict_rows(
        destination / "QUERY_BUILD_CHECKLIST.csv",
        list(query_rows[0].keys())
        + [
            "status",
            "preview_row_count",
            "implemented_by",
            "implemented_on",
            "notes",
        ],
        checklist,
    )
    return query_rows


def build_instruction_folder() -> None:
    destination = PACKAGE / "03_ZOHO_INSTRUCTIONS"
    for source, filename in INSTRUCTION_FILES:
        copy_text_required(source, destination / filename)


def build_validation_folder() -> None:
    destination = PACKAGE / "04_VALIDATION_AND_LIMITATIONS"
    for source, filename in VALIDATION_FILES:
        if source.suffix.lower() in {".md", ".json"} or filename == "SOURCE_KPI_MATRIX.csv":
            copy_text_required(source, destination / filename)
        else:
            copy_required(source, destination / filename)

    truth_destination = destination / "TRUTH_PACK"
    truth_files = sorted(TRUTH_SOURCE.glob("*.csv"))
    if len(truth_files) != EXPECTED_TRUTH_FILES:
        raise RuntimeError(
            f"Expected {EXPECTED_TRUTH_FILES} truth files, "
            f"found {len(truth_files)}"
        )
    for source in truth_files:
        copy_required(source, truth_destination / source.name)


def build_handoff_folder() -> None:
    destination = PACKAGE / "05_DEVELOPER_HANDOFF"
    copy_text_required(
        ROOT / "docs" / "CONTROL_TOWER_V2_START_HERE.md",
        destination / "MODEL_OVERVIEW.md",
    )
    copy_text_required(
        ROOT / "docs" / "control_tower_synthetic_fidelity.json",
        destination / "SYNTHETIC_FIDELITY.json",
    )

    contracts = sorted(CONTRACT_SOURCE.glob("*.json"))
    if len(contracts) != 21:
        raise RuntimeError(f"Expected 21 source contracts, found {len(contracts)}")
    for source in contracts:
        copy_text_required(
            source,
            destination / "SOURCE_CONTRACTS" / source.name,
        )


def write_start_here(import_rows: list[dict[str, str]]) -> None:
    expected_rows = sum(int(row["row_count"]) for row in import_rows)
    content = f"""# ABNAH Supply Chain Control Tower v2 - Final Zoho Package

## Use This Folder Only

This is the canonical implementation package for the current ABNAH Control
Tower v2 model. It contains the exact synthetic files, Query Table SQL,
Zoho build instructions, validation evidence, limitations and developer
contracts needed to reproduce the demonstrator.

Do not use the repository's older generic 37-query model or its older Ask Zia
SQL layer. They belong to an earlier dashboard architecture.

Package baseline:

- 14 active Zoho import files;
- {expected_rows:,} synthetic import rows;
- 38 Query Tables in dependency-safe order;
- maximum Query Table dependency level 3;
- 13 truth and acceptance files;
- 21 captured source-schema contracts;
- no actual ABNAH operational rows.

## Start Now

From this folder, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\\VERIFY_PACKAGE.ps1
```

Continue only when it prints `FINAL ZOHO PACKAGE: PASS`.

Then:

1. Read `03_ZOHO_INSTRUCTIONS/01_EXECUTION_RUNBOOK.md`.
2. Create or use a separate Zoho workspace named
   `ABNAH Control Tower v2 Build`.
3. Import the 14 files in `01_IMPORT_FILES` using
   `IMPORT_CHECKLIST.csv`. This build targets the already-created Zoho tables
   whose names are the filename stem followed by `-Copy`.
4. Build the 38 Query Tables in the exact order in
   `02_QUERY_TABLES/QUERY_BUILD_CHECKLIST.csv`.
5. Configure and validate all lookup columns, formula columns and aggregate
   formulas using
   `03_ZOHO_INSTRUCTIONS/03A_LOOKUPS_FORMULAS_AND_PRE_DASHBOARD_SETUP.md`.
6. Run the query and KPI gates in
   `03_ZOHO_INSTRUCTIONS/06_VALIDATION_AND_PUBLICATION.md`.
7. Build the four dashboard pages using
   `03_ZOHO_INSTRUCTIONS/04_DASHBOARD_BUILD.md`.
8. Reconcile every card and chart against
   `03_ZOHO_INSTRUCTIONS/04A_DASHBOARD_EXPECTED_RESULTS.md`.
9. Configure Ask Zia only after reconciliation passes, using
   `03_ZOHO_INSTRUCTIONS/05_ASK_ZIA_SETUP.md`.

Record progress directly in the two checklist CSVs and
`IMPLEMENTATION_STATUS.md`.

## Folder Map

| Folder | Purpose |
| --- | --- |
| `01_IMPORT_FILES` | The only 14 CSV files to import into Zoho, plus an editable checklist |
| `02_QUERY_TABLES` | All 38 SQL files, authoritative manifest and editable build checklist |
| `03_ZOHO_INSTRUCTIONS` | End-to-end import, model, dashboard, Ask Zia and validation steps |
| `04_VALIDATION_AND_LIMITATIONS` | Truth pack, source/KPI matrix, semantic audit and presentation gates |
| `05_DEVELOPER_HANDOFF` | Machine-readable source contracts and model/fidelity references |

`PACKAGE_MANIFEST.csv` contains a SHA-256 hash for every packaged payload file.

## Stop Gates

Stop and resolve the issue before continuing when:

- an import row count differs from `IMPORT_CHECKLIST.csv`;
- Zoho rejects or shifts a column;
- a Query Table is created out of order or unexpectedly returns zero rows;
- a dependency would exceed level 3;
- any reconciliation or truth-pack check fails;
- a dashboard value cannot be traced to a fact/summary table and landing source;
- Ask Zia selects a raw, standardized, AUX or legacy table; or
- an unavailable KPI is shown as actual ABNAH truth.

## Current Production Limitations

The demonstrator does not make these actual-data claims:

- exact production expiry risk, because the module is not enabled; the packaged
  value is a visibly synthetic demo estimate;
- source reorder levels, because the captured report is header-only;
- vendor return rate, because Stock Return is header-only;
- actual OTIF or lead-time deviation, because PO-to-receipt lineage is sparse;
- approved primary or alternate vendors;
- multi-outlet ABNAH geography.

Synthetic formula prototypes can remain in the demo only when visibly labelled
and traceable to the documented assumption.

## When Actual Exports Arrive

Keep actual CSV rows local. Run them through the repository's local audit
engine, compare schema and value profiles to the source contracts, then produce
approved normalized landing files. Do not commit raw ABNAH operational rows.

Update the source contract, active import manifest, Query Table SQL, truth pack
and limitation register together. Rebuild this folder with:

```powershell
python .\\scripts\\build_final_zoho_package.py
```

from the repository root, then rerun all tests before publishing the revision.
"""
    with (PACKAGE / "START_HERE.md").open(
        "w", encoding="utf-8", newline="\n"
    ) as handle:
        handle.write(content)


def write_implementation_status() -> None:
    content = """# Zoho Implementation Status

Update this file during the build. Do not mark a stage complete until its
validation checkpoint passes.

| Stage | Status | Owner | Date | Evidence / notes |
| --- | --- | --- | --- | --- |
| Package verification | NOT STARTED |  |  |  |
| Workspace backup or isolated v2 workspace | NOT STARTED |  |  |  |
| 14 landing tables imported | NOT STARTED |  |  |  |
| Import row and column checks | NOT STARTED |  |  |  |
| Query orders 1-11: standardized | NOT STARTED |  |  |  |
| Query orders 12-17: dimensions | NOT STARTED |  |  |  |
| Query orders 18-28: facts | NOT STARTED |  |  |  |
| Query orders 29-38: summaries, action facts and demo reference extensions | NOT STARTED |  |  |  |
| Lookup columns and formula columns | NOT STARTED |  |  |  |
| Aggregate formulas and grain checks | NOT STARTED |  |  |  |
| Truth-pack reconciliation | NOT STARTED |  |  |  |
| Page 1: Risk Action Center | NOT STARTED |  |  |  |
| Page 2: Procurement, Vendor and Capital Control | NOT STARTED |  |  |  |
| Page 3: Consumption Variance and Menu Profitability | NOT STARTED |  |  |  |
| Page 4: SCM Explorer and Data Quality | NOT STARTED |  |  |  |
| Ask Zia controlled question bank | NOT STARTED |  |  |  |
| Business owner review | NOT STARTED |  |  |  |
| Publication decision | NOT STARTED |  |  |  |
"""
    with (PACKAGE / "IMPLEMENTATION_STATUS.md").open(
        "w", encoding="utf-8", newline="\n"
    ) as handle:
        handle.write(content)


def write_verifier() -> None:
    content = r"""$ErrorActionPreference = 'Stop'
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
if ($truthFiles.Count -ne 13) {
    throw "Expected 13 truth files, found $($truthFiles.Count)"
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
    '03_ZOHO_INSTRUCTIONS\04A_DASHBOARD_EXPECTED_RESULTS.md',
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
Write-Host 'Truth files: 13'
"""
    with (PACKAGE / "VERIFY_PACKAGE.ps1").open(
        "w", encoding="utf-8", newline="\n"
    ) as handle:
        handle.write(content)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def manifest_metadata(
    relative: Path,
    active_by_file: dict[str, dict[str, str]],
    query_by_file: dict[str, dict[str, str]],
) -> tuple[str, str]:
    path = relative.as_posix()
    name = relative.name
    if path.startswith("01_IMPORT_FILES/") and name in active_by_file:
        row = active_by_file[name]
        return row["report_name"], row["active_v2_role"]
    if path.startswith("02_QUERY_TABLES/") and name in query_by_file:
        row = query_by_file[name]
        return row["query_table_name"], row["purpose"]
    if path.startswith("03_ZOHO_INSTRUCTIONS/"):
        return "Zoho instruction", name
    if "/TRUTH_PACK/" in path:
        return "Synthetic acceptance truth", name
    if path.startswith("04_VALIDATION_AND_LIMITATIONS/"):
        return "Validation and limitation evidence", name
    if path.startswith("05_DEVELOPER_HANDOFF/SOURCE_CONTRACTS/"):
        return "Machine-readable source schema contract", name
    if path.startswith("05_DEVELOPER_HANDOFF/"):
        return "Developer handoff reference", name
    return "Package control", name


def write_package_manifest(
    active_rows: list[dict[str, str]],
    query_rows: list[dict[str, str]],
) -> None:
    active_by_file = {
        Path(row["zoho_import_file"]).name: row for row in active_rows
    }
    query_by_file = {row["sql_file"]: row for row in query_rows}

    rows: list[dict[str, object]] = []
    payload_files = sorted(
        path
        for path in PACKAGE.rglob("*")
        if path.is_file() and path.name != "PACKAGE_MANIFEST.csv"
    )
    for path in payload_files:
        relative = path.relative_to(PACKAGE)
        subject, purpose = manifest_metadata(
            relative,
            active_by_file,
            query_by_file,
        )
        rows.append(
            {
                "stage": relative.parts[0],
                "path": relative.as_posix(),
                "subject": subject,
                "purpose": purpose,
                "size_bytes": path.stat().st_size,
                "sha256": file_sha256(path),
            }
        )
    write_dict_rows(
        PACKAGE / "PACKAGE_MANIFEST.csv",
        ["stage", "path", "subject", "purpose", "size_bytes", "sha256"],
        rows,
    )


def build() -> Path:
    subprocess.run(
        [
            sys.executable,
            str(Path(__file__).with_name("build_dashboard_expected_results.py")),
        ],
        check=True,
    )
    safe_recreate_package()
    active_rows, _ = build_import_folder()
    query_rows = build_query_folder()
    build_instruction_folder()
    build_validation_folder()
    build_handoff_folder()
    write_start_here(active_rows)
    write_implementation_status()
    write_verifier()
    write_package_manifest(active_rows, query_rows)
    return PACKAGE


if __name__ == "__main__":
    output = build()
    print(f"Built final Zoho package: {output}")
