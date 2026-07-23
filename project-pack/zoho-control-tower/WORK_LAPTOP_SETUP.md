# ABNAH Work Laptop Handoff

This handoff uses two private GitHub repositories:

- `arnavkadhe/abnah-zoho-synthetic-demo`: synthetic data, Zoho SQL, local
  auditing, report contracts, validation, and implementation runbooks.
- `arnavkadhe/abnah-schema-workspace`: the editable Schema Workspace and
  Control Tower architecture website.

Actual ABNAH CSV exports, screenshots, audit outputs, credentials, and local
machine paths are intentionally excluded.

## Prerequisites

- Git
- Python 3.11 or newer
- Node.js 22 or newer for the Schema Workspace
- Optional: Ollama for local LLM review
- Optional: Tesseract or RapidOCR dependencies for screenshot extraction

## 1. Clone And Prepare The Synthetic Project

```powershell
git clone https://github.com/arnavkadhe/abnah-zoho-synthetic-demo.git
cd abnah-zoho-synthetic-demo
powershell -ExecutionPolicy Bypass -File .\setup_work_laptop.ps1
```

The default setup creates `.venv`, installs the core packages, runs the
repository safety check, and executes the test suite.

Optional setup:

```powershell
.\setup_work_laptop.ps1 -Regenerate
.\setup_work_laptop.ps1 -WithOcr
.\setup_work_laptop.ps1 -Regenerate -WithOcr
```

Important outputs:

- `exports/control_tower_zoho/`: 16 Zoho landing-table CSVs plus normalized
  variants and acceptance outputs.
- `docs/ZOHO_CONTROL_TOWER_V2_EXECUTION_RUNBOOK.md`: authoritative 16-table,
  37-Query-Table, four-dashboard implementation order.
- `docs/zoho_control_tower_v2_sql/`: Query Table SQL in dependency order.
- `docs/control_tower_v2_truth_reference.md`: synthetic truth and acceptance
  reference.

## 2. Run A Local Actual-CSV Audit

Copy actual CSV exports only into:

```text
local_data_auditor/input/
```

That directory is ignored by Git. Run:

```powershell
cd local_data_auditor
.\run_laptop_pipeline.bat
```

Outputs remain under `local_data_auditor/output/`, which is also ignored.
Review full rows locally with:

```powershell
.\run_local_report_viewer.bat
```

The portable packets produced for Codex contain schema and aggregated issue
evidence, not complete operational rows.

## 3. Clone And Run The Schema Workspace

```powershell
git clone https://github.com/arnavkadhe/abnah-schema-workspace.git
cd abnah-schema-workspace
npm ci
npm run data:validate
npm run dev
```

Before transferring or publishing changes:

```powershell
npm run typecheck
npm run lint
npm test
```

## 4. Zoho Implementation

Follow these files in order:

1. `docs/CONTROL_TOWER_V2_START_HERE.md`
2. `docs/ZOHO_CONTROL_TOWER_V2_EXECUTION_RUNBOOK.md`
3. `docs/zoho_control_tower_v2_import.md`
4. `docs/zoho_control_tower_v2_query_build.md`
5. `docs/zoho_control_tower_v2_dashboard_click_by_click.md`
6. `docs/zoho_control_tower_v2_validation.md`

Build the v2 Zoho workspace in parallel with the existing workspace. Do not
delete the older raw tables before reconciliation, dashboard acceptance, and
rollback approval.

## 5. Data Safety

Never commit files from:

- `local_data_auditor/input/`
- `local_data_auditor/output/`
- `source_intake/posist_uat/_incoming_drop/`
- `source_intake/posist_uat/batches/`
- `source_intake/posist_uat/_working_previews/`
- `source_intake/posist_uat/ocr_runs/`

Screenshots remain local. Store only derived report schemas, field definitions,
mapping decisions, sanitized evidence, synthetic data, and implementation code
in GitHub.

Run this before every push:

```powershell
python scripts\check_repository_safety.py
```
