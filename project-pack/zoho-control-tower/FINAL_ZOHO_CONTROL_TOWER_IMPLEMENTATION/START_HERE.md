# ABNAH Supply Chain Control Tower v2 - Final Zoho Package

## Use This Folder Only

This is the canonical implementation package for the current ABNAH Control
Tower v2 model. It contains the exact synthetic files, Query Table SQL,
Zoho build instructions, validation evidence, limitations and developer
contracts needed to reproduce the demonstrator.

Do not use the repository's older generic 37-query model or its older Ask Zia
SQL layer. They belong to an earlier dashboard architecture.

Package baseline:

- 14 active Zoho import files;
- 25,020 synthetic import rows;
- 38 Query Tables in dependency-safe order;
- maximum Query Table dependency level 3;
- 13 truth and acceptance files;
- 21 captured source-schema contracts;
- no actual ABNAH operational rows.

## Start Now

From this folder, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\VERIFY_PACKAGE.ps1
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
5. Configure and validate all lookup columns and the four active aggregate
   formulas using
   `03_ZOHO_INSTRUCTIONS/03A_LOOKUPS_FORMULAS_AND_PRE_DASHBOARD_SETUP.md`.
   If the 38 tables, lookups and earlier formulas already exist, use
   `03_ZOHO_INSTRUCTIONS/03B_CURRENT_WORKSPACE_MIGRATION.md` instead.
6. Review the reference-to-Zoho decisions in
   `03_ZOHO_INSTRUCTIONS/04B_REFERENCE_TO_ZOHO_CAPABILITY_MATRIX.md`.
7. Run the query and KPI gates in
   `03_ZOHO_INSTRUCTIONS/06_VALIDATION_AND_PUBLICATION.md`.
8. Build every saved report, KPI widget and dashboard filter using
   `03_ZOHO_INSTRUCTIONS/04_DASHBOARD_BUILD.md`.
9. Reconcile every card and chart against
   `03_ZOHO_INSTRUCTIONS/04A_DASHBOARD_EXPECTED_RESULTS.md`.
10. Map each dashboard User Filter to the exact compatible report field using
    `03_ZOHO_INSTRUCTIONS/05_DASHBOARD_FILTER_MAPPING.md`.
11. Build, share and hand off each saved report in the order in
    `03_ZOHO_INSTRUCTIONS/09_REPORT_BUILD_EMBED_AND_FILTER_SEQUENCE.md`.
12. Connect individual secured report URLs to the ABG custom portal using
    `03_ZOHO_INSTRUCTIONS/07_EMBEDDED_PORTAL_SETUP.md`.
    Keep each native page-dashboard URL as a validation and fallback link.
13. Complete company-laptop, authentication and hosting checks using
    `03_ZOHO_INSTRUCTIONS/08_PORTAL_HOSTING_AUTH_HANDOFF.md`.
14. Configure Ask Zia only after reconciliation passes, using
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
python .\scripts\build_final_zoho_package.py
```

from the repository root, then rerun all tests before publishing the revision.
