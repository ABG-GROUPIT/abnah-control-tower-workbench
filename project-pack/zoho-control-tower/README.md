# ABNAH Cafe Intelligence Zoho Analytics Synthetic Demo

## 1. Project Overview

This project is a Zoho Analytics-first proof-of-value demo for ABNAH Cafe Intelligence.

It generates synthetic ABNAH-style operational cafe reports, loads them into a Neon PostgreSQL database that simulates a POSIST-like backend, exposes those reports through FastAPI CSV endpoints, and lets Zoho Analytics import those endpoints as Web URL/feed tables.

The intended architecture is:

```text
Synthetic data generator
-> local CSV files
-> Neon PostgreSQL raw report tables
-> FastAPI CSV feed endpoints
-> Zoho Analytics Web URL/feed import
-> Zoho modeling, joins, dashboards, and Ask Zia-style analysis
```

The project uses synthetic data only. It does not use real or confidential ABNAH operational data.

Important architecture note: the direct Neon PostgreSQL connector to Zoho was tested and works, but it is a fallback/testing path. The desired final demo flow is FastAPI CSV feeds into Zoho Web URL/feed import.

## Work Laptop Quick Start

The repository includes generated synthetic CSVs, Zoho Query Table SQL, the
local audit engine, schema contracts, Control Tower documentation, and the
step-by-step implementation runbooks.

```powershell
git clone https://github.com/ABG-GROUPIT/abnah-control-tower-workbench.git
cd abnah-control-tower-workbench\project-pack\zoho-control-tower
powershell -ExecutionPolicy Bypass -File .\setup_work_laptop.ps1
```

Use `-Regenerate` to rebuild the synthetic package and `-WithOcr` to install
the optional screenshot OCR dependencies. Read `WORK_LAPTOP_SETUP.md` for the
complete one-repository handoff and local-data safety rules.

## Control Tower v2

The current ABNAH Supply Chain Control Tower work uses the validated
Restroworks-shaped package, not the older generic 37-table demo model.

For implementation on another laptop, use the self-contained final package:

- [`FINAL_ZOHO_CONTROL_TOWER_IMPLEMENTATION/START_HERE.md`](FINAL_ZOHO_CONTROL_TOWER_IMPLEMENTATION/START_HERE.md)

Start here:

- `docs/CONTROL_TOWER_V2_START_HERE.md`
- `docs/control_tower_v2_source_kpi_matrix.csv`
- `docs/zoho_control_tower_v2_import.md`
- `docs/zoho_control_tower_v2_query_build.md`
- `docs/ZOHO_LOOKUPS_AGGREGATE_FORMULAS_AND_PRE_DASHBOARD_SETUP.md`: exact
  lookup matrices, row formulas, aggregate formulas, grain restrictions and
  pre-dashboard reconciliation checklist.
- `docs/ZOHO_CURRENT_WORKSPACE_MIGRATION.md`: exact continuation from a
  workspace where all 38 Query Tables, lookups and earlier formulas are already
  complete.
- `docs/ABNAH_REFERENCE_TO_ZOHO_CAPABILITY_MATRIX.md`: mapping from ABNAH's
  supplied visual reference to Zoho native, enhanced and custom-finish
  visuals.
- `docs/zoho_control_tower_v2_dashboard_click_by_click.md`
- `docs/ZOHO_EMBEDDED_PORTAL_SETUP.md`: secured-login embedding,
  browser-local URL configuration, hosting boundaries and custom-chart
  fallbacks.
- `docs/ZOHO_REPORT_BUILD_EMBED_AND_FILTER_SEQUENCE.md`: current-stage,
  four-dashboard build order, sign-in, secured handoff and filter contract.
- `docs/ZOHO_DASHBOARD_FILTER_MAPPING_MATRIX.md`: exact page-by-page Query
  Table, physical field, fixed-filter and dashboard User Filter mappings.
- `docs/ZOHO_PORTAL_HOSTING_AUTH_HANDOFF.md`: final GitHub Pages versus
  SharePoint decision, Pro-plan gate, login behavior, one-file handoff,
  work-laptop checks and backend boundary.
- `docs/zoho_control_tower_v2_validation.md`
- `docs/control_tower_v2_truth_reference.md`
- `docs/ZOHO_CONTROL_TOWER_V2_EXECUTION_RUNBOOK.md`: the authoritative
  parallel migration, 14-table active import, 38-Query-Table dependency, dashboard,
  Ask Zia and cutover sequence.
- `docs/control_tower_synthetic_fidelity.md`: report-by-report POSIST contract,
  blank/zero-only handling, and the exact boundary between raw and modeled data.
- `docs/CONTROL_TOWER_KPI_AND_CHART_LINEAGE_HANDBOOK.md`: searchable lineage
  and exact Zoho configuration for all 76 final KPI/chart/detail objects.
- `docs/PRESENTATION_SAFE_ACTUAL_DATA_ISSUES.md`: the three defensible
  fit-for-use findings to present, plus claims that must not be overstated.

Build and validate:

```powershell
python -m generator.generate_all
python scripts/build_control_tower_v2_sql.py
python scripts/build_control_tower_truth_pack.py
python scripts/build_control_tower_presentation.py --site-root "..\ABNAH Schema Atlas"
python -m unittest discover -s tests -v
```

The presentation generator is the synchronization boundary. After a Query
Table or final dashboard object changes, run it once to regenerate both
handbooks, the 76-story contract, the 38-table model catalog, and the Schema
Atlas website snapshot.

Current v2 baseline:

- 21 validated report contracts: 20 current UAT exports plus the historical ABNAH `Vendor Report`
- 173 exact-schema CSV files
- 35 cross-report reconciliations passing
- 14-table active import manifest, including two visibly synthetic demo references
- 38 active Zoho Query Tables, with no dependency above level 3
- 206 synthetic near-expiry batch tranches for the demo only; 79 carry synthetic
  receipt/GRN lineage and 127 are labelled opening-stock fallbacks
- 69 confirmed no-signal POSIST fields retained in raw shape and excluded downstream
- 2 header-only report contracts mirrored and gated
- 13 synthetic truth/acceptance files
- 9 control-tower acceptance checks passing

## 2. Current Build Status

| Area | Status | Evidence in repo | Notes |
|---|---|---|---|
| Synthetic data generator | Complete | `generator/generate_all.py`, `generator/*.py` | Generates static reports and three months of operational reports. |
| Static report generation | Complete | `data/static/*.csv`, `generator/generate_all.py` | Six static/global CSV reports exist. |
| Outlet-wise monthly report generation | Complete | `data/month_01`, `data/month_02`, `data/month_03` | 36 outlet-wise operational CSV files exist. |
| Neon database schema | Complete | `sql/001_create_raw_tables.sql`, `sql/002_create_control_tables.sql`, `sql/003_indexes.sql` | Creates only `raw` and `control`; no analytics schema. |
| Neon data loading | Complete | `loaders/load_static.py`, `loaders/load_month.py`, `manage_demo.py` | Loads static reports and operational reports into cumulative raw tables. |
| Month 1 reset/load | Complete | `python manage_demo.py reset-month-1` | Drops/recreates raw/control, generates files, loads static + Month 1. |
| Month 2 append/load | Complete | `python manage_demo.py load-month 2` | Appends Month 2 rows into the same raw operational tables. |
| Month 3 append/load | Complete | `python manage_demo.py load-month 3` | Appends Month 3 rows into the same raw operational tables. |
| Month 2 delete | Complete | `loaders/delete_month.py`, `manage_demo.py delete-month 2` | Uses `control.loaded_row_registry`; does not delete static reports. |
| Month 3 delete | Complete | `loaders/delete_month.py`, `manage_demo.py delete-month 3` | Uses `control.loaded_row_registry`; does not delete static reports. |
| Reset to Month 1 | Complete | `manage_demo.py reset-to-month 1` | Deletes Month 2 and Month 3 if loaded. |
| Reset to Month 2 | Complete | `manage_demo.py reset-to-month 2` | Ensures Month 1 + Month 2 and removes Month 3. |
| FastAPI health endpoint | Complete | `app/main.py` | `GET /health`. |
| FastAPI CSV feed endpoints | Complete | `app/csv_feeds.py` | Static/master feeds, outlet-specific operational feeds, and combined debug endpoints. |
| FastAPI admin endpoints | Complete | `app/admin_routes.py` | Reset/load/delete/status endpoints exist. |
| Feed token protection | Complete, needs manual setup | `app/auth.py`, `.env.example` | If `FEED_TOKEN` is blank, feeds are open; if set, token is required. |
| Admin token protection | Complete, needs manual setup | `app/auth.py`, `.env.example` | Admin routes require `ADMIN_TOKEN`; blank token disables admin use by returning 503. |
| ngrok/cloud tunnel setup | Needs manual setup | No ngrok/cloudflared config in repo | Must be installed/run manually or replaced with hosted deployment. |
| Hosted deployment setup | Ready for Render, needs account setup | `render.yaml` | User must connect a Git repo/service and enter `DATABASE_URL`, `FEED_TOKEN`, and `ADMIN_TOKEN` as hosted environment variables. |
| Zoho import steps | Complete documentation, not verified in Zoho | `README.md`, `docs/zoho_fastapi_feed_test.md`, `docs/zoho_import_notes.md` | FastAPI endpoints are documented; actual Zoho workspace import still needs manual test. |
| Main-data ngrok/FastAPI/Zoho test runbook | Complete documentation, not executed in Zoho | `docs/ngrok_fastapi_zoho_main_data_test_runbook.md` | Uses the existing synthetic dataset; does not create dummy test data. |
| Outlet-aware Zoho model specification | Complete documentation and starter SQL, not tested in Zoho | `docs/zoho_data_model_plan.md`, `docs/zoho_query_table_sql/` | Query tables must be manually created and syntax-tested inside Zoho. |
| Validation report | Complete | `docs/validation_report.md` | Includes live Neon and FastAPI feed checks from previous validation run. |
| CSV fallback exports | Complete | `exports/current/*.csv`, `loaders/export_csv.py` | Exports current loaded raw tables as CSV backup. |

Current live Neon status from `python manage_demo.py status` at inspection time:

- Loaded months: `month_01`, `month_02`, `month_03`
- `raw.sales_report`: 14,576 rows
- `raw.purchase_report`: 638 rows
- `raw.entry_report`: 585 rows
- `raw.inventory_closing_report`: 9,720 rows
- `control.loaded_row_registry`: 25,519 rows

Schema check at inspection time:

```text
schemas=['control', 'raw']
analytics_tables=[]
analytics_views=[]
```

## 3. Architecture Explanation

### Neon PostgreSQL

Neon PostgreSQL acts as the simulated POSIST-like backend database. It stores raw ABNAH-style report tables in the `raw` schema and loader tracking tables in the `control` schema.

Neon is not the analytics layer. It intentionally does not create `analytics` schema objects, `dim_*` tables, `fact_*` tables, or Zoho-ready SQL views.

### FastAPI

FastAPI acts as the controlled reporting/API layer.

It reads current raw tables from Neon and returns CSV files from `/zoho/*.csv` endpoints. Zoho Analytics should import those CSV endpoints as Web URL/feed data sources.

FastAPI also exposes protected admin endpoints for resetting, loading, deleting, and checking demo status. These are operational conveniences for testing; the CLI is the safer default for local work.

### Zoho Analytics

Zoho Analytics should import the FastAPI CSV endpoints and perform modeling inside Zoho:

- lookup columns
- formulas
- aggregate formulas
- query tables
- dashboards
- Ask Zia-style analysis

Direct Zoho-to-Neon PostgreSQL import is only a fallback/testing path, not the final demo flow.

## 4. Data Flow

### Month 1

`python manage_demo.py reset-month-1`:

1. Regenerates deterministic synthetic CSVs.
2. Drops old demo objects.
3. Recreates `raw` and `control`.
4. Loads static reports.
5. Loads Month 1 operational rows.
6. Registers Month 1 operational row IDs in `control.loaded_row_registry`.

After this, FastAPI CSV endpoints return static reports and Month 1 operational data.

### Month 2

`python manage_demo.py load-month 2`:

1. Checks `control.etl_load_batch`.
2. Skips safely if Month 2 is already loaded.
3. Appends Month 2 operational rows into the same raw operational tables.
4. Registers inserted Month 2 row IDs.

After this, FastAPI endpoints return Month 1 + Month 2 for operational reports. Zoho must manually refresh/re-fetch the same feed URLs.

### Month 3

`python manage_demo.py load-month 3`:

1. Checks `control.etl_load_batch`.
2. Skips safely if Month 3 is already loaded.
3. Appends Month 3 operational rows into the same raw operational tables.
4. Registers inserted Month 3 row IDs.

After this, FastAPI endpoints return Month 1 + Month 2 + Month 3. Month 3 is designed to support the holiday/event/competitor/inventory-pressure story.

### Deletion And Reset

`python manage_demo.py delete-month 2` removes only Month 2 rows from operational raw tables using `control.loaded_row_registry`.

`python manage_demo.py delete-month 3` removes only Month 3 rows.

`python manage_demo.py reset-to-month 1` removes Month 2 and Month 3 if loaded.

`python manage_demo.py reset-to-month 2` ensures Month 1 + Month 2 are loaded and removes Month 3 if loaded.

Static reports are not deleted by month delete/reset commands.

## 5. Important Import Behavior

Zoho should not create separate tables for Month 1, Month 2, and Month 3.

Operational reports should be imported as outlet-specific RAW tables, because the original synthetic source files are outlet-wise and the dashboard modules are outlet-specific. Static/master reports remain shared global RAW tables.

Operational outlet-specific feeds:

- `sales_report_OUT001`, `sales_report_OUT002`, `sales_report_OUT003`
- `purchase_report_OUT001`, `purchase_report_OUT002`, `purchase_report_OUT003`
- `entry_report_OUT001`, `entry_report_OUT002`, `entry_report_OUT003`
- `inventory_closing_report_OUT001`, `inventory_closing_report_OUT002`, `inventory_closing_report_OUT003`

Month 2 and Month 3 rows are still appended into the same Neon backend raw operational tables. FastAPI filters those Neon raw tables by outlet when serving outlet-specific feed URLs. The Zoho `STD_*` operational Query Tables then union the three outlet-specific RAW imports back into one outlet-aware model for cross-outlet and outlet-filtered dashboards.

Current implementation behavior:

| Behavior | Current state |
|---|---|
| FastAPI endpoint output | Outlet-specific operational feeds plus combined debug feeds |
| Backend Month 2/3 load | Append into existing raw tables |
| Backend duplicate prevention | `row_id` primary keys + `ON CONFLICT DO NOTHING` |
| Backend delete/reset | Registry-based exact row deletion |
| Zoho refresh mode | To be tested in Zoho |
| Recommended Zoho import behavior | Re-fetch/full refresh of the same outlet-specific feed URL |

Risk: if Zoho is configured to append refreshed feed rows without using `row_id` as a key, duplicate rows can appear inside Zoho even though the backend does not duplicate rows. For the first test, verify how Zoho treats Web URL/feed refresh. If Zoho offers update/add by key, use `row_id` as the key. Otherwise, configure refresh/re-import carefully so the table reflects the full feed.

## 6. Repository Structure

Actual major structure:

```text
abnah-zoho-synthetic-demo/
  app/
  generator/
  loaders/
  sql/
  data/
    static/
    month_01/
    month_02/
    month_03/
  exports/
    current/
  scripts/
  docs/
  manage_demo.py
  README.md
  requirements.txt
  .env.example
```

Folder roles:

- `app/`: FastAPI app, CSV feed routes, admin routes, token checks.
- `generator/`: deterministic synthetic data generation.
- `loaders/`: Neon database connection, schema reset, static/month loading, delete/reset helpers, status, export.
- `sql/`: raw/control table DDL and indexes.
- `data/static/`: global/static raw report CSVs.
- `data/month_01/`, `data/month_02/`, `data/month_03/`: outlet-wise operational CSV source files.
- `exports/current/`: current loaded raw tables exported as CSV backup.
- `scripts/`: Windows batch wrappers for common CLI/API commands.
- `docs/`: supporting documentation and validation evidence.

New Zoho build reference docs:

- `docs/inventory_dashboard_step_by_step_readme.md`: exact Inventory and Consumption dashboard filters, KPIs, charts, and filter mappings.
- `docs/zoho_modelling_approach_and_dashboard_coverage_readme.md`: Web URL import architecture, RAW-to-STD-to-FACT/SUM modelling story, and dashboard coverage/gap analysis.
- `docs/additional_dashboard_charts_deep_dive_readme.md`: additional business-relevant dashboard charts possible with the current raw schemas only.
- `docs/posist_uat_intake_and_model_adaptation_plan.md`: Codex working workflow for future POSist UAT screenshots, API docs, report exports, field mapping, and model adaptation. The screenshot layer is for schema discovery, not the end product.
- `docs/external_data_signals_pre_uat_plan.md`: India/NCR-aware pre-UAT plan that separates free PoC sources from commercially available production candidates for weather, Google/Mappls routes, geocodes, curated local events, Indian holidays, AQI, and commodity signals that could later enrich Zoho dashboards, AutoML, and Code Studio workflows.
- `source_intake/posist_uat/restroworks_api_docs_packet/`: first Restroworks public API docs packet with endpoint inventory and mapping seeds for ABNAH model adaptation.
- `source_intake/posist_uat/structured_screenshot_capture_guide.md`: capture and folder-structure guide for POSist report-menu/report-schema screenshots.
- `docs/free_ocr_setup_readme.md`: free OCR setup/check guide for POSist screenshot extraction.
- `docs/run_screenshot_extraction_on_ocr_pc.md`: simple transfer/setup/run workflow for processing POSist screenshots on the 5070 Ti PC.
- `local_data_auditor/README.md`: portable, contract-driven local CSV auditor with exact first-batch report order, grouped-header semantics, report-specific validation rules, and one-command execution.

## 7. Environment Setup

Python: use Python 3.11 or newer.

Install dependencies:

```powershell
cd abnah-zoho-synthetic-demo
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

Required packages are listed in `requirements.txt`:

- `pandas`
- `numpy`
- `faker`
- `python-dotenv`
- `sqlalchemy`
- `psycopg2-binary`
- `fastapi`
- `uvicorn`

`.env.example`:

```env
DATABASE_URL=
FEED_TOKEN=
ADMIN_TOKEN=
APP_ENV=local
```

Local `.env` should contain:

```env
DATABASE_URL=postgresql+psycopg2://USER:PASSWORD@HOST.neon.tech/DBNAME?sslmode=require
FEED_TOKEN=optional-feed-token
ADMIN_TOKEN=required-for-admin-routes
APP_ENV=local
```

Warnings:

- Never commit real `.env`.
- Never hardcode Neon credentials.
- Never hardcode Zoho credentials.
- Keep feed/admin tokens out of screenshots and public docs.

Verify database connection:

```powershell
python -B manage_demo.py status
```

If the connection string is wrong or missing, the command will fail while creating the SQLAlchemy engine or querying Neon.

## 8. Command Reference

### `python manage_demo.py reset-month-1`

Purpose: reset the demo to Month 1 baseline.

Changes:

- Drops old `raw`, `control`, `analytics`, and `staging` demo schemas if present.
- Recreates `raw` and `control`.
- Generates CSV data.
- Loads static reports.
- Loads Month 1 operational rows.
- Registers Month 1 row IDs.

Safe to run multiple times: yes, but destructive. It wipes and rebuilds the demo schemas.

Expected output: static row counts, Month 1 report load counts, final raw/control row counts.

Verify:

```powershell
python manage_demo.py status
```

### `python manage_demo.py load-month 2`

Purpose: append Month 2 operational rows.

Changes:

- Loads `data/month_02/*/OUT*_*.csv`.
- Inserts into `raw.sales_report`, `raw.purchase_report`, `raw.entry_report`, and `raw.inventory_closing_report`.
- Registers Month 2 rows.

Safe to run multiple times: yes. If Month 2 is already loaded, it skips.

Verify: `raw.sales_report` should increase from 4,855 to 9,416 rows.

### `python manage_demo.py load-month 3`

Purpose: append Month 3 operational rows.

Safe to run multiple times: yes. If Month 3 is already loaded, it skips.

Verify: `raw.sales_report` should increase to 14,576 rows when all three months are loaded.

### `python manage_demo.py delete-month 2`

Purpose: delete only Month 2 operational rows.

Changes:

- Uses `control.loaded_row_registry`.
- Deletes registered Month 2 rows from operational raw tables.
- Removes Month 2 registry and batch records.
- Does not delete static reports.

Safe to run multiple times: mostly safe; if Month 2 is not loaded, it deletes zero rows.

### `python manage_demo.py delete-month 3`

Purpose: delete only Month 3 operational rows.

Same behavior as Month 2 delete, scoped to Month 3.

### `python manage_demo.py reset-to-month 1`

Purpose: return to baseline Month 1 state.

Changes:

- Deletes Month 3 if loaded.
- Deletes Month 2 if loaded.
- Keeps Month 1 and static reports.

### `python manage_demo.py reset-to-month 2`

Purpose: return to Month 1 + Month 2 state.

Changes:

- Ensures Month 1 exists.
- Loads Month 2 if missing.
- Deletes Month 3 if loaded.

### `python manage_demo.py status`

Purpose: print loaded months, raw row counts, registry counts, Zoho import feed URLs, and combined debug feed URLs.

Changes: none.

### `python manage_demo.py export-current-csv`

Purpose: export currently loaded raw tables to `exports/current/`.

Changes:

- Writes CSV backup files under `exports/current/`.
- Does not change Neon data.

## 9. FastAPI Run Guide

Run locally:

```powershell
uvicorn app.main:app --reload --port 8000
```

or:

```powershell
.\scripts\run_api.bat
```

Public feed endpoints:

| Endpoint | What it returns | Token |
|---|---|---|
| `GET /health` | Health check | none |
| `GET /zoho/vendor_report.csv` | Current `raw.vendor_report` | `FEED_TOKEN` if set |
| `GET /zoho/menu_master.csv` | Current `raw.menu_master` | `FEED_TOKEN` if set |
| `GET /zoho/brand_recipe_consumption.csv` | Current `raw.brand_recipe_consumption` | `FEED_TOKEN` if set |
| `GET /zoho/sales_report_OUT001.csv` | Current sales feed filtered to `OUT001` | `FEED_TOKEN` if set |
| `GET /zoho/sales_report_OUT002.csv` | Current sales feed filtered to `OUT002` | `FEED_TOKEN` if set |
| `GET /zoho/sales_report_OUT003.csv` | Current sales feed filtered to `OUT003` | `FEED_TOKEN` if set |
| `GET /zoho/purchase_report_OUT001.csv` | Current purchase feed filtered to `OUT001` | `FEED_TOKEN` if set |
| `GET /zoho/entry_report_OUT001.csv` | Current entry feed filtered to `OUT001` | `FEED_TOKEN` if set |
| `GET /zoho/inventory_closing_report_OUT001.csv` | Current inventory feed filtered to `OUT001` | `FEED_TOKEN` if set |
| `GET /zoho/sales_report.csv` | Combined current `raw.sales_report`, for debug/backward-compatible checks | `FEED_TOKEN` if set |
| `GET /zoho/indian_calendar_holidays.csv` | Current `raw.indian_calendar_holidays` | `FEED_TOKEN` if set |
| `GET /zoho/manual_calendar_events.csv` | Current `raw.manual_calendar_events` | `FEED_TOKEN` if set |
| `GET /zoho/competitor_pricing.csv` | Current `raw.competitor_pricing` | `FEED_TOKEN` if set |

Example feed URL:

```text
http://127.0.0.1:8000/zoho/sales_report_OUT001.csv
```

With token:

```text
http://127.0.0.1:8000/zoho/sales_report_OUT001.csv?token=YOUR_FEED_TOKEN
```

Admin endpoints:

| Endpoint | What it does | Token |
|---|---|---|
| `POST /admin/reset-month-1` | Runs Month 1 reset/load | `X-Admin-Token` required |
| `POST /admin/load-month/2` | Loads Month 2 | `X-Admin-Token` required |
| `POST /admin/load-month/3` | Loads Month 3 | `X-Admin-Token` required |
| `POST /admin/delete-month/2` | Deletes Month 2 | `X-Admin-Token` required |
| `POST /admin/delete-month/3` | Deletes Month 3 | `X-Admin-Token` required |
| `POST /admin/reset-to-month/1` | Resets to Month 1 | `X-Admin-Token` required |
| `POST /admin/reset-to-month/2` | Resets to Month 2 | `X-Admin-Token` required |
| `GET /admin/status` | Returns JSON status | `X-Admin-Token` required |

Example admin curl:

```powershell
curl.exe -X POST "http://127.0.0.1:8000/admin/load-month/2" -H "X-Admin-Token: YOUR_ADMIN_TOKEN"
```

If `ADMIN_TOKEN` is blank, admin endpoints return 503 by design.

## 10. Public URL / ngrok / Hosting Explanation

Zoho cloud cannot import from `localhost` or `127.0.0.1`.

FastAPI must be exposed through a public HTTPS URL using one of:

- ngrok
- cloudflared
- Render
- Railway
- Koyeb
- another approved hosting environment

ngrok is not part of this codebase. It must be installed and run manually.

ngrok test steps:

1. Run FastAPI locally:
   ```powershell
   .\scripts\run_api.bat
   ```
2. Run ngrok:
   ```powershell
   ngrok http 8000
   ```
3. Copy the HTTPS forwarding URL.
4. Test:
   ```text
   https://<ngrok-url>/health
   ```
5. Test a feed:
   ```text
   https://<ngrok-url>/zoho/sales_report_OUT001.csv?token=<FEED_TOKEN>
   ```
6. Use that URL in Zoho Web URL/feed import.

Free ngrok URLs are temporary. For stable leadership demos, host FastAPI on a persistent service.

### Hosted FastAPI Option: Render

The repo includes `render.yaml` so the FastAPI app can be deployed as a Render web service. This gives Zoho Analytics a public HTTPS URL such as:

```text
https://abnah-zoho-synthetic-demo-api.onrender.com
```

This hosted URL is the URL family Zoho should import from:

```text
https://<hosted-api-domain>/zoho/sales_report_OUT001.csv?token=<FEED_TOKEN>
```

Render deployment settings represented in `render.yaml`:

| Setting | Value |
|---|---|
| Runtime | Python |
| Build command | `pip install -r requirements.txt` |
| Start command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Health check | `/health` |
| Region | `singapore` |
| Required hosted secrets | `DATABASE_URL`, `FEED_TOKEN`, `ADMIN_TOKEN` |

Manual setup needed from the user:

1. Put this project in a GitHub/GitLab/Bitbucket repository that Render can access.
2. Create a Render Blueprint or Web Service from that repository.
3. Enter these environment variables in the Render dashboard:
   - `DATABASE_URL`: the Neon SQLAlchemy connection string, including `sslmode=require`.
   - `FEED_TOKEN`: token used by Zoho feed URLs. Use a strong random value.
   - `ADMIN_TOKEN`: token used only for admin reset/load/delete endpoints.
4. Deploy the service.
5. Open `https://<hosted-api-domain>/health` and confirm it returns `{"status":"ok"}`.
6. Open `https://<hosted-api-domain>/zoho/sales_report_OUT001.csv?token=<FEED_TOKEN>` and confirm the CSV downloads.
7. Use the hosted feed URLs in Zoho Analytics `Files/Feeds` or `Web URL` import.

Important hosting notes:

- Do not put real secret values in `render.yaml`, README files, screenshots, or commits.
- If `FEED_TOKEN` is blank in the hosted environment, feed URLs are public. For a leadership demo, set it.
- If `ADMIN_TOKEN` is blank, admin endpoints return 503 by design.
- Zoho cloud pulls from the hosted URL directly. It does not matter which laptop opens Zoho, as long as the hosted FastAPI URL is public HTTPS and reachable from Zoho.
- If the hosted service goes to sleep on a free/low-tier host, the first Zoho refresh may be slow or may time out. For a live demo, warm up `/health` and one feed URL before presenting.

Main-data Zoho connection test:

Use `docs/ngrok_fastapi_zoho_main_data_test_runbook.md` before building the full Zoho model. That runbook tests the real synthetic dataset through:

```text
Neon raw tables
-> FastAPI CSV feed
-> ngrok public URL
-> Zoho Web URL/feed import
-> Month 2 load
-> Zoho refresh
-> duplicate check
-> reset/delete and retest
```

Expected outlet-specific sales row counts during the test:

| Backend state | OUT001 | OUT002 | OUT003 | Total after `STD_Sales_Report` union |
|---|---:|---:|---:|---:|
| Month 1 | 1,529 | 1,595 | 1,731 | 4,855 |
| Month 1 + Month 2 | 3,003 | 3,088 | 3,325 | 9,416 |
| Month 1 + Month 2 + Month 3 | 4,623 | 4,747 | 5,206 | 14,576 |

Do not start full Zoho modeling until this refresh behavior is understood. If Zoho blindly appends the full CSV feed every time, duplicate rows will occur.

## 11. Zoho Analytics Import Steps

1. Create or open a Zoho Analytics workspace.
2. Choose data import.
3. Choose the Web URL/feed option. Exact wording may be `Files/Feeds`, `Web URL`, `URL feed`, or similar.
4. Paste the public FastAPI CSV endpoint URL.
5. If `FEED_TOKEN` is set, include `?token=<FEED_TOKEN>`.
6. Ensure the first row is treated as column headers.
7. Choose create new table.
8. Name the table according to the report.
9. Set column types if needed.
10. Complete import.
11. Repeat for all report endpoints.

Table mapping:

| Zoho table | FastAPI endpoint |
|---|---|
| `RAW_Sales_Report_OUT001` | `/zoho/sales_report_OUT001.csv` |
| `RAW_Sales_Report_OUT002` | `/zoho/sales_report_OUT002.csv` |
| `RAW_Sales_Report_OUT003` | `/zoho/sales_report_OUT003.csv` |
| `RAW_Purchase_Report_OUT001` | `/zoho/purchase_report_OUT001.csv` |
| `RAW_Purchase_Report_OUT002` | `/zoho/purchase_report_OUT002.csv` |
| `RAW_Purchase_Report_OUT003` | `/zoho/purchase_report_OUT003.csv` |
| `RAW_Entry_Report_OUT001` | `/zoho/entry_report_OUT001.csv` |
| `RAW_Entry_Report_OUT002` | `/zoho/entry_report_OUT002.csv` |
| `RAW_Entry_Report_OUT003` | `/zoho/entry_report_OUT003.csv` |
| `RAW_Inventory_Closing_Report_OUT001` | `/zoho/inventory_closing_report_OUT001.csv` |
| `RAW_Inventory_Closing_Report_OUT002` | `/zoho/inventory_closing_report_OUT002.csv` |
| `RAW_Inventory_Closing_Report_OUT003` | `/zoho/inventory_closing_report_OUT003.csv` |
| `RAW_Menu_Master` | `/zoho/menu_master.csv` |
| `RAW_Vendor_Report` | `/zoho/vendor_report.csv` |
| `RAW_Brand_Recipe_Consumption` | `/zoho/brand_recipe_consumption.csv` |
| `RAW_Indian_Calendar_Holidays` | `/zoho/indian_calendar_holidays.csv` |
| `RAW_Manual_Calendar_Events` | `/zoho/manual_calendar_events.csv` |
| `RAW_Competitor_Pricing` | `/zoho/competitor_pricing.csv` |

Refresh test:

1. Run `python manage_demo.py reset-to-month 1`.
2. Import `RAW_Sales_Report_OUT001` while only Month 1 is loaded.
3. Note the row count.
4. Run `python manage_demo.py load-month 2`.
5. Open the same FastAPI `sales_report_OUT001.csv` endpoint and confirm row count increased.
6. In Zoho, manually refresh/re-fetch the imported feed/table.
7. Confirm Zoho row count increased.
8. Check charts update.
9. Repeat for Month 3.

If exact Zoho buttons differ, look for likely labels such as `Data Sources`, `Sync`, `Refresh`, `Re-fetch`, `Import Settings`, or `Sync Now`.

## 12. Complete End-To-End Zoho Build Plan

This is the full build path for Zoho Analytics. Neon remains the raw backend. FastAPI remains the public CSV feed layer. Zoho imports RAW feed tables, then creates the `STD_*`, `DIM_*`, `FACT_*`, and `SUM_*` model inside Zoho.

Zoho supports importing tabular data such as CSV from Web URL feeds through the Files/Feeds option. It also supports secured feed URLs and request parameters/headers. This project uses simple CSV GET endpoints, with `?token=<FEED_TOKEN>` as the recommended feed token pattern.

### 12.1 Build Sequence

Use this sequence exactly:

1. Host FastAPI publicly and validate `/health`.
2. Set backend to Month 1:
   ```powershell
   python manage_demo.py reset-to-month 1
   ```
3. Import only `RAW_Sales_Report_OUT001` first.
4. Load Month 2, refresh the same Zoho table, and prove `row_id` does not duplicate.
5. Load Month 3, refresh the same Zoho table, and prove `row_id` does not duplicate.
6. Reset to Month 1, refresh the same Zoho table, and prove the row count returns to `1,529`.
7. Import all remaining RAW tables.
8. Create Query Tables in this order: `STD_*`, `DIM_*`, `FACT_*`, `SUM_*`.
9. Create lookup relationships.
10. Build dashboards from `FACT_*` and `SUM_*` tables.
11. Test Month 2, Month 3, and reset behavior again after dashboards exist.

Do not build the full model until Zoho refresh behavior is proven. If Zoho appends the full CSV feed on each refresh, every dashboard will inherit duplicate rows.

### 12.2 RAW Tables To Import

Create each RAW table once. Future month changes should refresh/re-fetch the same table, not create new Month 2 or Month 3 tables. Operational RAW tables are outlet-specific. Static/master RAW tables are shared.

| Build order | Zoho RAW table | FastAPI endpoint |
|---:|---|---|
| 1 | `RAW_Sales_Report_OUT001` | `/zoho/sales_report_OUT001.csv` |
| 2 | `RAW_Sales_Report_OUT002` | `/zoho/sales_report_OUT002.csv` |
| 3 | `RAW_Sales_Report_OUT003` | `/zoho/sales_report_OUT003.csv` |
| 4 | `RAW_Purchase_Report_OUT001` | `/zoho/purchase_report_OUT001.csv` |
| 5 | `RAW_Purchase_Report_OUT002` | `/zoho/purchase_report_OUT002.csv` |
| 6 | `RAW_Purchase_Report_OUT003` | `/zoho/purchase_report_OUT003.csv` |
| 7 | `RAW_Entry_Report_OUT001` | `/zoho/entry_report_OUT001.csv` |
| 8 | `RAW_Entry_Report_OUT002` | `/zoho/entry_report_OUT002.csv` |
| 9 | `RAW_Entry_Report_OUT003` | `/zoho/entry_report_OUT003.csv` |
| 10 | `RAW_Inventory_Closing_Report_OUT001` | `/zoho/inventory_closing_report_OUT001.csv` |
| 11 | `RAW_Inventory_Closing_Report_OUT002` | `/zoho/inventory_closing_report_OUT002.csv` |
| 12 | `RAW_Inventory_Closing_Report_OUT003` | `/zoho/inventory_closing_report_OUT003.csv` |
| 13 | `RAW_Menu_Master` | `/zoho/menu_master.csv` |
| 14 | `RAW_Vendor_Report` | `/zoho/vendor_report.csv` |
| 15 | `RAW_Brand_Recipe_Consumption` | `/zoho/brand_recipe_consumption.csv` |
| 16 | `RAW_Indian_Calendar_Holidays` | `/zoho/indian_calendar_holidays.csv` |
| 17 | `RAW_Manual_Calendar_Events` | `/zoho/manual_calendar_events.csv` |
| 18 | `RAW_Competitor_Pricing` | `/zoho/competitor_pricing.csv` |

Recommended import settings:

| Setting | Required behavior |
|---|---|
| First row | Treat as column headers. |
| `row_id` | Keep as text. |
| Date columns | Convert to date where Zoho detects them correctly. |
| Feed token | Use `?token=<FEED_TOKEN>` in the URL, or pass `X-Feed-Token` as a header if Zoho import parameters are preferred. |
| Refresh mode | Prefer replace/re-fetch. If update/add is available, use `row_id` as the key. Avoid blind append. |

Month test row counts for sales:

| Backend state | OUT001 | OUT002 | OUT003 | Total after `STD_Sales_Report` union |
|---|---:|---:|---:|---:|
| Month 1 | 1,529 | 1,595 | 1,731 | 4,855 |
| Month 1 + Month 2 | 3,003 | 3,088 | 3,325 | 9,416 |
| Month 1 + Month 2 + Month 3 | 4,623 | 4,747 | 5,206 | 14,576 |
| Reset to Month 1 | 1,529 | 1,595 | 1,731 | 4,855 |

Duplicate check in Zoho:

```sql
SELECT "row_id", COUNT(*) AS "row_count"
FROM "RAW_Sales_Report_OUT001"
GROUP BY "row_id"
HAVING COUNT(*) > 1
```

Expected result: no rows. Repeat for `RAW_Sales_Report_OUT002` and `RAW_Sales_Report_OUT003`.

### 12.3 Query Table Build Order

The SQL files are in `docs/zoho_query_table_sql/`.

Standardized tables:

| Query table | SQL file | Purpose |
|---|---|---|
| `STD_Sales_Report` | `01_std_sales_report.sql` | Union outlet-specific RAW sales feeds, standardize outlet-item daily sales, and derive outlet fields. |
| `STD_Purchase_Report` | `02_std_purchase_report.sql` | Union outlet-specific RAW purchase feeds, standardize PO line rows, and derive outlet fields. |
| `STD_Entry_Report` | `03_std_entry_report.sql` | Union outlet-specific RAW entry feeds, standardize receipt/GRN rows, and derive outlet fields. |
| `STD_Inventory_Closing_Report` | `04_std_inventory_closing_report.sql` | Union outlet-specific RAW inventory feeds and standardize daily outlet inventory. |
| `STD_Menu_Master` | `05_std_menu_master.sql` | Standardize menu item master. |
| `STD_Vendor_Report` | `06_std_vendor_report.sql` | Standardize vendor master. |
| `STD_Recipe_BOM` | `07_std_recipe_bom.sql` | Fill down recipe block export into recipe-ingredient rows. |
| `STD_Holiday_Calendar` | `08_std_holiday_calendar.sql` | Standardize holiday/calendar markers. |
| `STD_Manual_Events` | `09_std_manual_events.sql` | Standardize manual events and affected scope text. |
| `STD_Competitor_Pricing` | `10_std_competitor_pricing.sql` | Standardize competitor price context and map market areas to outlets. |

Dimensions:

| Query table | SQL file |
|---|---|
| `DIM_Date` | `11_dim_date.sql` |
| `DIM_Outlet` | `12_dim_outlet.sql` |
| `DIM_Menu_Item` | `13_dim_menu_item.sql` |
| `DIM_Vendor` | `14_dim_vendor.sql` |
| `DIM_Ingredient` | `15_dim_ingredient.sql` |
| `DIM_Event` | `16_dim_event.sql` |
| `DIM_Holiday` | `30_dim_holiday.sql` |
| `DIM_Competitor` | `31_dim_competitor.sql` |

Facts:

| Query table | SQL file |
|---|---|
| `FACT_Sales` | `17_fact_sales.sql` |
| `FACT_Purchase_Order` | `18_fact_purchase_order.sql` |
| `FACT_Entry_Receipt` | `19_fact_entry_receipt.sql` |
| `FACT_Inventory_Closing` | `20_fact_inventory_closing.sql` |
| `FACT_Theoretical_Consumption` | `21_fact_theoretical_consumption.sql` |
| `FACT_PO_Receipt_Comparison` | `22_fact_po_receipt_comparison.sql` |
| `FACT_Event_Sales_Impact` | `23_fact_event_sales_impact.sql` |
| `FACT_Competitor_Price_Position` | `24_fact_competitor_price_position.sql` |
| `FACT_Outlet_Daily_Health` | `25_fact_outlet_daily_health.sql` |
| `FACT_Vendor_Spend` | `32_fact_vendor_spend.sql` |

Summaries:

| Query table | SQL file |
|---|---|
| `SUM_Executive_KPIs` | `33_sum_executive_kpis.sql` |
| `SUM_Outlet_Health` | `34_sum_outlet_health.sql` |
| `SUM_Sales_Category_Mix` | `35_sum_sales_category_mix.sql` |
| `SUM_Menu_Item_Performance` | `36_sum_menu_item_performance.sql` |
| `SUM_Vendor_Share` | `26_sum_vendor_share.sql` |
| `SUM_Inventory_Risk` | `27_sum_inventory_risk.sql` |
| `SUM_Event_Impact` | `28_sum_event_impact.sql` |
| `SUM_Competitor_Positioning` | `29_sum_competitor_positioning.sql` |
| `SUM_Event_Markers` | `37_sum_event_markers.sql` |

Zoho syntax risk:

- `07_std_recipe_bom.sql` uses correlated fill-down logic. If Zoho rejects it, add a normalized FastAPI feed later and import it as the recipe BOM source.
- `11_dim_date.sql` uses date functions such as `YEAR`, `MONTH`, `QUARTER`, `DAYOFWEEK`, `CONCAT`, and `LPAD`. If Zoho rejects them, keep only the date and create formulas in Zoho.
- `23_fact_event_sales_impact.sql` and `25_fact_outlet_daily_health.sql` use `LIKE`, `CONCAT`, and date-window logic that may need local Zoho SQL adjustment.

### 12.4 Outlet-Aware Modeling Rules

The model supports one cross-outlet dashboard and multiple outlet-specific dashboards.

Synthetic outlet mapping:

| Outlet code | Outlet name | Market area |
|---|---|---|
| `OUT001` | `ABNAH Cafe Connaught Place` | `Connaught Place` |
| `OUT002` | `ABNAH Cafe Hauz Khas` | `Hauz Khas` |
| `OUT003` | `ABNAH Cafe Saket Premium` | `Saket` |

Rules:

- Do not create separate RAW tables per outlet.
- Do not create separate SQL models per outlet unless Zoho locked dashboard filters are impossible.
- `STD_Sales_Report`, `STD_Purchase_Report`, `STD_Entry_Report`, and `STD_Inventory_Closing_Report` must include `outlet_code`, `outlet_name`, and `market_area`.
- Every `FACT_*` table that has outlet activity must preserve `outlet_code`, `outlet_name`, and `market_area`.
- Every non-executive `SUM_*` table must preserve outlet context.
- Only `SUM_Executive_KPIs` may intentionally show all-outlet totals without outlet grouping.

### 12.5 Required Lookup Relationships

Create lookups after the relevant `DIM_*`, `FACT_*`, and `SUM_*` tables exist. If Zoho does not allow lookup columns on Query Tables in your workspace, continue using the denormalized fields already present in the facts and summaries, and document which lookup could not be created.

| Source table | Source column | Lookup target table | Target column | Purpose |
|---|---|---|---|---|
| `FACT_Sales` | `sales_date` | `DIM_Date` | `date_value` | Date/month filters for sales. |
| `FACT_Sales` | `outlet_code` | `DIM_Outlet` | `outlet_code` | Outlet filters and outlet drilldown. |
| `FACT_Sales` | `item_number` | `DIM_Menu_Item` | `item_number` | Menu item/category drilldown. |
| `FACT_Purchase_Order` | `po_date` | `DIM_Date` | `date_value` | PO date filtering. |
| `FACT_Purchase_Order` | `outlet_code` | `DIM_Outlet` | `outlet_code` | Outlet-specific procurement. |
| `FACT_Purchase_Order` | `vendor_name` | `DIM_Vendor` | `vendor_name` | Vendor filtering and details. |
| `FACT_Purchase_Order` | `item_code` | `DIM_Ingredient` | `ingredient_code` | Material/ingredient filtering. |
| `FACT_Entry_Receipt` | `receipt_date` | `DIM_Date` | `date_value` | Receipt date filtering. |
| `FACT_Entry_Receipt` | `outlet_code` | `DIM_Outlet` | `outlet_code` | Outlet-specific receipts. |
| `FACT_Entry_Receipt` | `vendor_name` | `DIM_Vendor` | `vendor_name` | Receipt vendor filtering. |
| `FACT_Entry_Receipt` | `item_code` | `DIM_Ingredient` | `ingredient_code` | Receipt material filtering. |
| `FACT_Inventory_Closing` | `inventory_date` | `DIM_Date` | `date_value` | Inventory date filtering. |
| `FACT_Inventory_Closing` | `outlet_code` | `DIM_Outlet` | `outlet_code` | Outlet-specific inventory. |
| `FACT_Inventory_Closing` | `item_code` | `DIM_Ingredient` | `ingredient_code` | Inventory material filtering. |
| `FACT_Theoretical_Consumption` | `sales_date` | `DIM_Date` | `date_value` | Consumption date filtering. |
| `FACT_Theoretical_Consumption` | `outlet_code` | `DIM_Outlet` | `outlet_code` | Outlet-specific theoretical consumption. |
| `FACT_Theoretical_Consumption` | `item_number` | `DIM_Menu_Item` | `item_number` | Sold menu item drilldown. |
| `FACT_Theoretical_Consumption` | `ingredient_name` | `DIM_Ingredient` | `ingredient_name` | BOM material drilldown when item code is unavailable. |
| `FACT_Event_Sales_Impact` | `event_id` | `DIM_Event` | `event_id` | Event drilldown. |
| `FACT_Event_Sales_Impact` | `sales_date` | `DIM_Date` | `date_value` | Event date filtering. |
| `FACT_Event_Sales_Impact` | `outlet_code` | `DIM_Outlet` | `outlet_code` | Outlet-specific event analysis. |
| `FACT_Event_Sales_Impact` | `item_number` | `DIM_Menu_Item` | `item_number` | Event item/category drilldown. |
| `FACT_Competitor_Price_Position` | `competitor_id` | `DIM_Competitor` | `competitor_id` | Competitor drilldown. |
| `FACT_Competitor_Price_Position` | `outlet_code` | `DIM_Outlet` | `outlet_code` | Outlet/market competitor filtering. |
| `FACT_Competitor_Price_Position` | `abnah_item_number` | `DIM_Menu_Item` | `item_number` | ABNAH item drilldown. |
| `FACT_Outlet_Daily_Health` | `activity_date` | `DIM_Date` | `date_value` | Daily health date filtering. |
| `FACT_Outlet_Daily_Health` | `outlet_code` | `DIM_Outlet` | `outlet_code` | Outlet comparison and drilldown. |
| `FACT_Vendor_Spend` | `activity_date` | `DIM_Date` | `date_value` | Vendor spend date filtering. |
| `FACT_Vendor_Spend` | `outlet_code` | `DIM_Outlet` | `outlet_code` | Outlet-specific vendor spend. |
| `FACT_Vendor_Spend` | `vendor_name` | `DIM_Vendor` | `vendor_name` | Vendor spend drilldown. |

Optional but useful summary lookups:

| Source table | Source column | Lookup target table | Target column | Purpose |
|---|---|---|---|---|
| `SUM_Outlet_Health` | `outlet_code` | `DIM_Outlet` | `outlet_code` | Dimension-driven outlet filters on executive summaries. |
| `SUM_Sales_Category_Mix` | `outlet_code` | `DIM_Outlet` | `outlet_code` | Outlet-specific category dashboards. |
| `SUM_Menu_Item_Performance` | `item_number` | `DIM_Menu_Item` | `item_number` | Menu item drilldown from ranking charts. |
| `SUM_Menu_Item_Performance` | `outlet_code` | `DIM_Outlet` | `outlet_code` | Outlet-specific menu dashboards. |
| `SUM_Vendor_Share` | `vendor_name` | `DIM_Vendor` | `vendor_name` | Vendor detail drilldown. |
| `SUM_Vendor_Share` | `outlet_code` | `DIM_Outlet` | `outlet_code` | Outlet-specific procurement dashboards. |
| `SUM_Inventory_Risk` | `item_code` | `DIM_Ingredient` | `ingredient_code` | Inventory material drilldown. |
| `SUM_Inventory_Risk` | `outlet_code` | `DIM_Outlet` | `outlet_code` | Outlet-specific inventory dashboards. |
| `SUM_Event_Impact` | `event_id` | `DIM_Event` | `event_id` | Event detail drilldown. |
| `SUM_Event_Markers` | `event_id` | `DIM_Event` | `event_id` | Spike explanation panel filters. |
| `SUM_Competitor_Positioning` | `outlet_code` | `DIM_Outlet` | `outlet_code` | Outlet/market competitor filters. |

Typical Zoho lookup setup:

1. Open the source table, for example `FACT_Sales`.
2. Open table design or edit design.
3. Select the source column, for example `outlet_code`.
4. Change the column type or relationship to Lookup Column.
5. Select the target table, for example `DIM_Outlet`.
6. Select the target column, for example `outlet_code`.
7. Save.
8. Test a chart or pivot to confirm target dimension fields are available.

### 12.6 Dashboard Build Overview

Build dashboards only after RAW refresh, Query Tables, and lookup relationships are working.

Dashboard pages:

| Dashboard | Scope | Mandatory filter |
|---|---|---|
| Executive / Outlet Comparison / Outlet Health | Cross-outlet | Date/month. Outlet optional for drilldown. |
| Sales and Menu Intelligence | One outlet at a time | Outlet and date/month. |
| Vendor and Procurement Analytics | One outlet at a time | Outlet and date/month. |
| Inventory and Consumption Intelligence | One outlet at a time | Outlet and date/month. |
| Calendar, Event, and Competitor Intelligence | One outlet or market area at a time | Outlet or market area, plus date/month. |

Recommended page duplication pattern:

```text
Sales_Menu_OUT001
Sales_Menu_OUT002
Sales_Menu_OUT003
Procurement_OUT001
Procurement_OUT002
Procurement_OUT003
Inventory_OUT001
Inventory_OUT002
Inventory_OUT003
Calendar_Competitor_OUT001
Calendar_Competitor_OUT002
Calendar_Competitor_OUT003
```

If Zoho supports locked dashboard filters, one reusable page per module is acceptable. If filter locking is weak, duplicate pages per outlet.

### 12.7 Dashboard 1: Executive / Outlet Comparison / Outlet Health

Scope: cross-outlet comparison across Connaught Place, Hauz Khas, and Saket.

| Tile/chart | Chart type | Source table | X-axis / dimension | Y-axis / measure | Filters | Purpose |
|---|---|---|---|---|---|---|
| Total Net Sales | KPI tile | `SUM_Executive_KPIs` or `FACT_Sales` | None | `SUM(net_sale)` or metric `Total Net Sales` | Date/month | All-outlet sales headline. |
| Total Quantity Sold | KPI tile | `SUM_Executive_KPIs` or `FACT_Sales` | None | `SUM(qty)` or metric `Total Quantity Sold` | Date/month | All-outlet volume headline. |
| Active Outlets | KPI tile | `DIM_Outlet` | None | `COUNT(outlet_code)` | None | Confirms three outlets. |
| Outlet Sales Ranking | Bar chart | `SUM_Outlet_Health` | `outlet_name` | `total_net_sales` | Date/month | Answers which outlet had highest sales. |
| Outlet Sales Trend | Line chart | `FACT_Outlet_Daily_Health` | `activity_date` | `SUM(net_sales)` | Series: `outlet_name`; date/month | Shows cross-outlet trend. |
| Outlet Health Table | Table/pivot | `SUM_Outlet_Health` | `outlet_name`, `market_area` | `total_net_sales`, `avg_daily_net_sales`, `total_po_value`, `avg_inventory_value`, `low_stock_item_days`, `event_day_markers` | Date/month | Outlet health comparison. |
| Inventory Pressure By Outlet | Bar chart | `SUM_Outlet_Health` | `outlet_name` | `low_stock_item_days` | Date/month | Compares inventory pressure. |
| Event Exposure By Outlet | Bar chart | `SUM_Outlet_Health` | `outlet_name` | `event_day_markers` | Date/month, event type if available | Compares event exposure. |
| Spike Explanation Panel | Table | `SUM_Event_Markers` | `event_date`, `outlet_name`, `event_name`, `event_type` | `event_day_sales`, `baseline_sales`, `sales_lift_percentage` | Date/month | Explains event spikes. |

### 12.8 Dashboard 2: Sales And Menu Intelligence

Scope: outlet-specific. Add a mandatory outlet filter or build one page per outlet.

| Tile/chart | Chart type | Source table | X-axis / dimension | Y-axis / measure | Filters | Purpose |
|---|---|---|---|---|---|---|
| Selected Outlet Net Sales | KPI tile | `FACT_Sales` | None | `SUM(net_sale)` | Mandatory outlet, date/month | Sales headline for one outlet. |
| Selected Outlet Quantity Sold | KPI tile | `FACT_Sales` | None | `SUM(qty)` | Mandatory outlet, date/month | Volume headline for one outlet. |
| Sales Trend | Line chart | `FACT_Sales` | `sales_date` | `SUM(net_sale)` | Mandatory outlet, date/month | Shows daily sales movement. |
| Category Mix | Bar chart | `FACT_Sales` | `category` | `SUM(net_sale)` | Mandatory outlet, date/month | Shows revenue by category. |
| Super Category Mix | Stacked bar or donut | `FACT_Sales` | `super_category` | `SUM(net_sale)` | Mandatory outlet, date/month | Shows beverage/food/dessert contribution. |
| Top Menu Items | Horizontal bar | `SUM_Menu_Item_Performance` | `item_name` | `total_net_sale` | Mandatory outlet, date/month, category | Identifies best-selling items. |
| Menu Quantity Ranking | Horizontal bar | `SUM_Menu_Item_Performance` | `item_name` | `total_qty` | Mandatory outlet, date/month, category | Identifies highest-volume items. |
| Realized Unit Price | Bar/scatter | `SUM_Menu_Item_Performance` | `item_name` | `avg_realized_unit_price` | Mandatory outlet, category | Reviews item price realization. |
| Event Item Lift | Table | `SUM_Event_Impact` | `event_name`, `item_name`, `category` | `event_day_sales`, `baseline_sales`, `sales_lift_pct` | Mandatory outlet, event type, date/month | Shows event-sensitive items. |

### 12.9 Dashboard 3: Vendor And Procurement Analytics

Scope: outlet-specific. Add a mandatory outlet filter.

| Tile/chart | Chart type | Source table | X-axis / dimension | Y-axis / measure | Filters | Purpose |
|---|---|---|---|---|---|---|
| PO Raised Value | KPI tile | `FACT_Vendor_Spend` | None | `SUM(ordered_value)` | Mandatory outlet, procurement date, vendor/material optional | PO value raised in selected scope. |
| Receipt Booked Value | KPI tile | `FACT_Vendor_Spend` | None | `SUM(received_value)` | Mandatory outlet, procurement date, vendor/material optional | Receipt value booked in selected scope. |
| PO vs Receipt Value Gap | KPI tile | `FACT_Vendor_Spend` | None | `SUM(ordered_value) - SUM(received_value)` | Mandatory outlet, procurement date, vendor/material optional; do not map PO status | Shows value gap between PO movement and receipt movement. |
| Open / Partial PO Status Count | KPI tile | `FACT_Vendor_Spend` | None | `SUM(open_or_partial_po_count)` | Mandatory outlet, procurement date, vendor/material optional; PO status allowed | Counts PO lines that are pending, partially received, or have remaining quantity. |
| Vendor PO Raised Share | Bar chart | `FACT_Vendor_Spend` | `vendor_name` | `SUM(ordered_value)` | Mandatory outlet, procurement date | Answers vendor share by PO raised value. |
| Vendor Receipt Booked Share | Bar chart | `FACT_Vendor_Spend` | `vendor_name` | `SUM(received_value)` | Mandatory outlet, procurement date | Compares receipt value by vendor. |
| Vendor Spend Trend | Line chart | `FACT_Vendor_Spend` | `activity_date` | `SUM(ordered_value)`, `SUM(received_value)` | Mandatory outlet, vendor, date/month | Shows procurement trend. |
| PO Status | Stacked bar | `FACT_Purchase_Order` | `po_status` | `COUNT(po_number)` or `SUM(total_item_cost)` | Mandatory outlet, date/month | Shows closed, pending, partial, cancelled. |
| Pending PO Table | Table | `FACT_PO_Receipt_Comparison` | `po_number`, `vendor_name`, `item_name`, `po_status` | `ordered_qty`, `matched_received_qty`, `unmatched_order_qty`, `remaining_qty` | Mandatory outlet, vendor, PO status | Finds pending/partial POs. |
| Vendor Material Matrix | Pivot table | `FACT_Purchase_Order` | Rows: `vendor_name`; columns: `item_name` or `category_name` | `SUM(total_item_cost)` | Mandatory outlet, date/month | Shows which vendors supply which materials. |

### 12.10 Dashboard 4: Inventory And Consumption Intelligence

Scope: outlet-specific. Add a mandatory outlet filter.

| Tile/chart | Chart type | Source table | X-axis / dimension | Y-axis / measure | Filters | Purpose |
|---|---|---|---|---|---|---|
| Latest Inventory Value | KPI tile | `SUM_Inventory_Risk` | None | `SUM(total_amt)` | Mandatory outlet, latest date/month | Inventory value headline. |
| Low Stock Item Count | KPI tile | `SUM_Inventory_Risk` | None | `SUM(low_stock_flag)` | Mandatory outlet, latest date/month | Inventory pressure headline. |
| Inventory Value By Category | Bar chart | `SUM_Inventory_Risk` | `category_name` | `SUM(total_amt)` | Mandatory outlet; latest snapshot only | Shows current stock value mix. |
| Low Stock Table | Table | `SUM_Inventory_Risk` | `item_name`, `category_name`, `inventory_pressure_band` | `total_qty`, `total_amt`, `total_theoretical_qty` | Mandatory outlet, latest date/month | Identifies low stock items. |
| Theoretical Consumption Trend | Line chart | `FACT_Theoretical_Consumption` | `sales_date` | `SUM(theoretical_ingredient_qty)` | Mandatory outlet, ingredient/material, date/month | Shows ingredient demand from sales. |
| Recipe To Material Demand | Pivot/table | `FACT_Theoretical_Consumption` | Rows: `menu_item_name`; columns: `ingredient_name` | `SUM(theoretical_ingredient_qty)` | Mandatory outlet, category, date/month | Shows which materials are used by recipes sold. |
| Event Day Inventory Pressure | Table | `FACT_Outlet_Daily_Health` and `SUM_Event_Markers` | `activity_date`, `outlet_name`, `health_note` | `low_stock_item_count`, `event_count`, `net_sales` | Mandatory outlet, event type/date | Connects events and inventory pressure. |

### 12.11 Dashboard 5: Calendar, Event, And Competitor Intelligence

Scope: outlet-specific or market-area-specific. Add a mandatory outlet or market-area filter.

| Tile/chart | Chart type | Source table | X-axis / dimension | Y-axis / measure | Filters | Purpose |
|---|---|---|---|---|---|---|
| Event Day Sales | Bar chart | `SUM_Event_Impact` | `event_name` | `event_day_sales` | Mandatory outlet, event type, date/month | Shows event sales by event. |
| Event Lift % | Bar chart | `SUM_Event_Impact` | `event_name` | `sales_lift_pct` | Mandatory outlet, event type | Shows directional lift. |
| Spike Explanation Panel | Table | `SUM_Event_Markers` | `event_date`, `event_name`, `event_type`, `affected_items` | `event_day_sales`, `baseline_sales`, `sales_lift_percentage`, `confidence_level` | Mandatory outlet, date/month | Replaces chart annotations if needed. |
| Holiday/Event Sales Trend | Line chart | `FACT_Sales` with holiday/event filter panel | `sales_date` | `SUM(net_sale)` | Mandatory outlet, date/month, event/holiday | Shows sales around calendar markers. |
| Competitor Price Index | Bar chart | `SUM_Competitor_Positioning` | `competitor_name` or `competitor_category` | `avg_price_index` | Mandatory market area/outlet, category | Shows higher/lower pricing context. |
| ABNAH Vs Competitor Difference | Bar chart | `SUM_Competitor_Positioning` | `competitor_category` | `avg_price_difference` | Mandatory market area/outlet | Shows price disadvantage/advantage areas. |
| Premium Overperformance Table | Table | `FACT_Competitor_Price_Position` | `abnah_item_name`, `competitor_name`, `price_position` | `price_index`, `price_difference`, `SUM(net_sale)`, `SUM(qty)` | Mandatory outlet/market area, category | Reviews premium items still selling. |

### 12.12 Dashboard Caveats To Keep Visible

- Sales rows are daily outlet-item aggregates, not individual bills.
- Vendor share is demo spend share, not audited accounts payable spend.
- Entry rows do not include PO number, so PO-to-receipt matching is approximate.
- Theoretical consumption is sales multiplied by recipe BOM quantities. It is not full actual-vs-theoretical variance.
- Low stock and inventory risk are heuristic pressure indicators, not production stockout prediction.
- Competitor pricing is contextual and synthetic. Do not claim competitor prices caused sales changes.
- Event lift is directional and explanatory unless validated with stronger statistical controls.

Detailed supporting documents remain available in:

- `docs/zoho_data_model_plan.md`
- `docs/zoho_raw_import_copy_paste_readme.md`
- `docs/zoho_query_table_build_order.md`
- `docs/zoho_actual_data_model_build_readme.md`
- `docs/zoho_dashboard_build_readme.md`
- `docs/zoho_zia_training_readme.md`
- `docs/zoho_query_table_sql/`
- `docs/dashboard_module_plan.md`
- `docs/zoho_manual_build_steps.md`
- `docs/model_validation_checklist.md`
- `docs/ngrok_fastapi_zoho_main_data_test_runbook.md`

## 13. Validation Checklist

Validate Neon schemas:

```sql
SELECT schema_name
FROM information_schema.schemata
WHERE schema_name IN ('raw', 'control', 'analytics', 'staging')
ORDER BY schema_name;
```

Validate raw table counts:

```sql
SELECT 'sales_report' AS table_name, COUNT(*) FROM raw.sales_report
UNION ALL SELECT 'purchase_report', COUNT(*) FROM raw.purchase_report
UNION ALL SELECT 'entry_report', COUNT(*) FROM raw.entry_report
UNION ALL SELECT 'inventory_closing_report', COUNT(*) FROM raw.inventory_closing_report;
```

Validate loaded months:

```sql
SELECT month_code, status, sales_rows, purchase_rows, entry_rows, inventory_rows, loaded_at
FROM control.etl_load_batch
ORDER BY month_code;
```

Validate registry counts:

```sql
SELECT month_code, table_name, COUNT(*) AS row_count
FROM control.loaded_row_registry
GROUP BY month_code, table_name
ORDER BY month_code, table_name;
```

Validate duplicate row IDs:

```sql
SELECT row_id, COUNT(*)
FROM raw.sales_report
GROUP BY row_id
HAVING COUNT(*) > 1;
```

Repeat for other raw tables if needed.

Validate sales rule:

```sql
SELECT COUNT(*)
FROM raw.sales_report
WHERE qty > 0 AND net_sale <= 0;
```

Validate inventory rule:

```sql
SELECT COUNT(*)
FROM raw.inventory_closing_report
WHERE total_qty < 0 OR store_stock_qty < 0;
```

Validate no internal generated files:

```powershell
Test-Path data\static\ingredients_internal.csv
Test-Path data\static\outlets_internal.csv
```

Validate FastAPI feed:

```powershell
Invoke-WebRequest -UseBasicParsing "http://127.0.0.1:8000/zoho/sales_report_OUT001.csv"
```

Validate Zoho imported row count matches the FastAPI feed row count after each refresh.

## 14. Troubleshooting

Problem: FastAPI works locally but Zoho cannot import.

Cause: Zoho cloud cannot access localhost.

Fix: expose FastAPI using ngrok/cloudflared or deploy it to a public HTTPS host.

Problem: Zoho import gives unauthorized.

Cause: missing or wrong `FEED_TOKEN`.

Fix: use `?token=<FEED_TOKEN>` or `X-Feed-Token`.

Problem: admin endpoint returns 503.

Cause: `ADMIN_TOKEN` is not configured.

Fix: add `ADMIN_TOKEN` to `.env`, restart FastAPI, and send `X-Admin-Token`.

Problem: Zoho table does not update after Month 2.

Cause: Zoho has not re-fetched the Web URL source or the import mode is wrong.

Fix: verify the FastAPI endpoint row count first, then manually refresh/re-fetch the Zoho data source.

Problem: duplicate rows appear in Zoho.

Cause: Zoho may be appending refreshed feed rows instead of replacing/updating by `row_id`.

Fix: configure update/add by `row_id` if available, or use a refresh/re-import mode that reflects the full current feed.

Problem: Month delete does not reflect in Zoho.

Cause: backend endpoint changed but Zoho has not refreshed.

Fix: refresh/re-fetch the Zoho table.

Problem: ngrok URL changed.

Cause: free ngrok URLs are temporary.

Fix: update the Zoho source URL or deploy FastAPI to a stable host.

## 15. Stability And Enterprise Readiness

Demo-ready:

- synthetic data generation
- Neon backend simulation
- raw/control schemas
- month-wise append/delete/reset
- FastAPI CSV feeds
- feed token support
- admin token support
- manual Zoho refresh flow documentation
- CSV fallback exports

Not production-ready:

- no hosted deployment config
- no API gateway
- simple token authentication only
- no OAuth/service account flow
- no IP allowlisting
- manual Zoho refresh
- limited logging
- no enterprise secrets manager
- no automated observability or alerting
- no production POSIST API integration

Enterprise upgrade path:

- company-approved cloud database or direct POSIST/source API
- POSist UAT source-intake workflow for Codex to interpret screenshots, report exports, and API documentation before model changes
- India-aware governed external-signal ETL for IMD/Open-Meteo PoC weather plus commercial weather providers, Google or Mappls vendor routes, geocodes, curated/licensed local events, Indian holidays, AQI providers, commodity data, and other context features
- hosted FastAPI behind API gateway
- OAuth/service account authentication
- IP allowlisting
- centralized logs and metrics
- schema versioning
- automated data quality checks
- scheduled Zoho imports or Zoho Analytics API push
- MDM/admin approval layer for vendor/item/outlet changes

## 16. What Is Still Pending

Must do before Zoho test:

- Set `FEED_TOKEN` in `.env` if the feed should not be public.
- Start FastAPI.
- Expose FastAPI through ngrok/cloudflared or deploy it publicly.
- Use `docs/ngrok_fastapi_zoho_main_data_test_runbook.md` to import `RAW_Sales_Report_OUT001` first.
- Verify Zoho refresh mode and duplicate behavior with Month 1, Month 2, Month 3, and reset-to-Month-1.
- Import remaining feed endpoints only after the sales refresh test works.

Must do before leadership demo:

- Use a stable public URL, preferably hosted rather than free ngrok.
- Confirm all Zoho table row counts after Month 1, Month 2, and Month 3.
- Manually create and syntax-test Zoho `STD_*`, `DIM_*`, `FACT_*`, and `SUM_*` query tables.
- Build outlet-aware Zoho dashboards with one cross-outlet executive dashboard and outlet-filtered module dashboards.
- Prepare event/holiday/competitor/inventory-pressure talking points.
- Practice reset/load/refresh timing.

Optional future scope:

- POSist UAT screenshot/API intake for Codex schema discovery using `docs/posist_uat_intake_and_model_adaptation_plan.md`
- India/NCR external data signal planning using `docs/external_data_signals_pre_uat_plan.md`, with free PoC sources and commercial production candidates tracked separately
- phase 1 model adaptation for Inventory and Consumption Intelligence plus Vendor and Procurement Analytics
- phase 2 model adaptation for sales/revenue once the phase 1 source mapping is stable
- hosted deployment config
- richer API logging
- automated feed health checks
- Zoho Analytics API push path
- MDM/admin data quality workflow
- official holiday source integration
- richer competitor data collection process

## 17. Demo Script

1. Run `python manage_demo.py reset-to-month 1`.
2. Show FastAPI Month 1 sales row count: 4,855.
3. Show Dashboard 1 as cross-outlet executive comparison.
4. Show one outlet-specific module, for example `Sales_Menu_OUT001`.
5. Run `python manage_demo.py load-month 2`.
6. Show FastAPI sales row count increased to 9,416.
7. Refresh/re-fetch Zoho feed tables.
8. Show executive comparison updated and one outlet-specific module updated.
9. Run `python manage_demo.py load-month 3`.
10. Show FastAPI sales row count increased to 14,576.
11. Refresh/re-fetch Zoho feed tables.
12. Show selected-outlet holiday/event/competitor/inventory-pressure story.
13. Run `python manage_demo.py reset-to-month 1` for retest, then refresh/re-fetch Zoho and confirm sales row count returns to 4,855.
14. Explain caveats and future MDM layer.

Do not claim Zoho is already connected unless the runbook test has been completed manually. Do not claim the full Zoho model is complete until query tables and dashboards are manually created and tested inside Zoho.
