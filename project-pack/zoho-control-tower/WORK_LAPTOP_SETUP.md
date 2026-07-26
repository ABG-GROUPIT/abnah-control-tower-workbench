# ABNAH Work-Laptop Handoff

## Canonical Source

Use the ABG repository:

```text
https://github.com/ABG-GROUPIT/abnah-control-tower-workbench
```

The hosted Atlas and complete downloadable project pack are:

```text
https://abg-groupit.github.io/abnah-control-tower-workbench/
https://abg-groupit.github.io/abnah-control-tower-workbench/ABNAH_COMPLETE_PROJECT_PACK.zip
```

This one pack contains the synthetic data, 38 Zoho Query Tables, dashboard
instructions, acceptance references, report contracts, local auditor and portal
handoff documents.

Actual ABNAH CSV exports, screenshots, audit outputs, credentials and private
machine paths are intentionally excluded.

## Prerequisites

- Python 3.11 or newer for the local auditor.
- Git and Node.js 22 or newer only when editing/rebuilding the website.
- Optional Ollama for local LLM review.
- Optional OCR packages only for future screenshot extraction.

## 1. Obtain The Complete Pack

Preferred non-development handoff:

1. Open the hosted Atlas.
2. Download `ABNAH_COMPLETE_PROJECT_PACK.zip`.
3. Extract it to a company-approved local folder.
4. Work inside `project-pack/zoho-control-tower`.

Developer handoff:

```powershell
git clone https://github.com/ABG-GROUPIT/abnah-control-tower-workbench.git
cd abnah-control-tower-workbench
npm ci
npm run data:validate
```

## 2. Zoho Implementation

Start with:

```text
FINAL_ZOHO_CONTROL_TOWER_IMPLEMENTATION/START_HERE.md
```

Important folders:

- `01_IMPORT_FILES/`: the final Zoho landing-table CSVs;
- `02_QUERY_TABLES/`: the 38 Query Tables in dependency order;
- `03_ZOHO_INSTRUCTIONS/`: lookups, formulas, filters, dashboards, Ask Zia,
  portal embedding and hosting;
- `04_VALIDATION_AND_LIMITATIONS/TRUTH_PACK/`: expected KPI/chart values.

Do not delete or overwrite an older accepted workspace until the replacement
tables, Query Tables, dashboards and truth checks pass.

## 3. Run A Local Actual-CSV Audit

Copy actual exports only into:

```text
local_data_auditor/input/
```

Run:

```powershell
cd local_data_auditor
.\run_laptop_pipeline.bat
```

Outputs remain under `local_data_auditor/output/`. They must not be uploaded or
committed.

To review complete local rows:

```powershell
.\run_local_report_viewer.bat
```

The terminal must remain open. The expected health endpoint is:

```text
http://127.0.0.1:8765/health
```

If the browser says connection refused:

```powershell
powershell -ExecutionPolicy Bypass -File .\diagnose_local_report_viewer.ps1
```

The viewer must run on the same company laptop as the browser. `127.0.0.1`
never reaches a different laptop.

## 4. Open The Separate Delivery Portal

The Atlas **Live portal** link opens:

```text
/portal/
```

Follow:

```text
docs/ZOHO_PORTAL_HOSTING_AUTH_HANDOFF.md
```

No key is required for the secured-login MVP. Import the four secured Zoho
iframe `src` URLs using one JSON file based on:

```text
config/zoho-secured-embed-handoff.example.json
```

The file must not contain a password, OAuth token, client secret or report row.

## 5. Rebuild The Website Only When Needed

Zoho data refreshes and Zoho report changes appear through the iframe and do
not require a website rebuild.

Rebuild only when changing Atlas content, portal code, labels, layouts,
lineage, documentation or the committed blueprint:

```powershell
npm run data:validate
npm run typecheck
npm run lint
npm test
npm run build:pages
```

## 6. Data Safety

Never commit:

- `local_data_auditor/input/`;
- `local_data_auditor/output/`;
- POSIST/UAT screenshot dumps;
- full actual report exports;
- OAuth tokens, refresh tokens or client secrets;
- browser-local handoff files unless ABG explicitly accepts exposing the view
  identifiers.

Screenshots remain local. GitHub contains only derived schemas, field
definitions, mapping decisions, sanitized evidence, synthetic data,
implementation code and instructions.

Before every project-pack push:

```powershell
python scripts\check_repository_safety.py
```
