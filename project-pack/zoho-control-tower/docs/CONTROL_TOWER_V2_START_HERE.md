# ABNAH Control Tower v2 - Start Here

## Purpose

This package turns the validated Restroworks report schemas into a synthetic,
three-outlet, three-month baseline for the four-page ABNAH Supply Chain Control
Tower.

It is designed to support two separate outcomes:

1. Build and validate the proposed dashboard in Zoho Analytics without using
   ABNAH row data.
2. Replace the synthetic landing files with controlled ABNAH exports later,
   while retaining the same standardized, fact, KPI and dashboard contracts.

The package does not claim that every KPI is production-approved. It makes the
current calculation assumptions, source gaps, and acceptance values explicit.

## Current Status

| Deliverable | Status |
| --- | --- |
| Exact-schema synthetic reports | 21 validated contracts: 20 current UAT plus historical Vendor Report |
| Exact-schema source files | 173 CSV files |
| Zoho normalized landing files | 21 CSV files |
| Approved synthetic model-output/reference tables | 4 CSV files |
| Schema-capture-only candidates | 3 CSV files, not production-authoritative |
| Cross-report generator checks | 35 of 35 passing |
| Source fidelity | 21 exact headers; current-UAT blank/zero states mirrored |
| Header-only source gates | 2 contracts; no synthetic rows fabricated |
| Zoho Query Tables | 38 active, all within dependency levels 1-3 |
| Dashboard truth files | 12 files |
| Control-tower acceptance checks | 9 of 9 passing |
| Workbench KPI route visualization | Maintained in the ABNAH Schema Atlas project |

## Build In This Order

Run from the repository root:

```powershell
python -m generator.generate_all
python scripts/build_control_tower_v2_sql.py
python scripts/build_control_tower_truth_pack.py
python -m unittest discover -s tests -v
```

Expected generator counts:

```text
control_tower_validated_reports: 21
control_tower_source_rows: 40775
control_tower_reconciliation_checks: 35
```

Expected test result: all repository tests pass after the truth and SQL packs
are built.

## Deliverable Map

| Path | Use |
| --- | --- |
| `data/control_tower/` | Exact-schema report files split by month and outlet |
| `exports/control_tower_zoho/RAW_CT_*.csv` | Consolidated exact Restroworks headers; fidelity evidence |
| `exports/control_tower_zoho/normalized/RAWN_CT_*.csv` | Stable landing headers for Zoho |
| `exports/control_tower_zoho/_CONTROL_TOWER_ACTIVE_IMPORT_MANIFEST.csv` | Exact 14-file v2 import set and row-count gate |
| `exports/control_tower_zoho/AUX_*.csv` | Four synthetic model/reference outputs: demand forecast, theoretical consumption, outlet geography and expiry scenario |
| `exports/control_tower_zoho/truth/` | Expected page and row-level results |
| `docs/zoho_control_tower_v2_sql/` | Query Tables in exact build order |
| `docs/control_tower_v2_source_kpi_matrix.csv` | Source authority, role, fields, fallback and gate |
| `docs/control_tower_synthetic_fidelity.md` | Exact schema boundary and blank/zero/header-only decisions |
| `docs/zoho_control_tower_v2_import.md` | File-import procedure |
| `docs/zoho_control_tower_v2_query_build.md` | Query Table procedure |
| `docs/zoho_control_tower_v2_dashboard_click_by_click.md` | Four-page dashboard procedure |
| `docs/zoho_control_tower_v2_validation.md` | Reconciliation and publication gates |
| `docs/control_tower_v2_truth_reference.md` | Overall synthetic acceptance values |

## Model Shape

```text
Restroworks-shaped CSV landing tables
  -> standardized Query Tables (level 1)
  -> reusable dimensions and facts (levels 1-2)
  -> only necessary KPI summaries (level 3)
  -> Zoho reports, aggregate formulas and dashboard tabs
```

Zoho currently permits a maximum of three Query Table levels. The builder
validates that limit before writing SQL. Presentation-only views therefore use
reports or aggregate formulas rather than creating an illegal fourth layer.

Official reference:
https://www.zoho.com/analytics/help/query-tables.html

## Lean Production Source Set

The current active model needs these ten populated report or master
contracts:

1. Gross/Net Margin Report
2. Item Recipe Report
3. Enterprise Variance Report - normal
4. Closing Stock Report
5. Enterprise Purchase Order Report - item detail
6. Enterprise Entry Report - Stock Entry
7. Enterprise Transfer Report - Transfer From
8. Enterprise Transfer Report - Transfer To
9. Enterprise Wastage Report - normal
10. Vendor Report

`Vendor Report` is the exact historical ABNAH vendor-master export. Run its
local structural repair and validation before import because multiple phone
numbers and long addresses were documented to shift cells or continue onto
another physical row. It supports identity, validity, compliance context,
state and address; it does not supply lead time, SLA, or approved vendor-item
mapping.

Enterprise Stock Return is the eleventh candidate contract, but its audited UAT
export is header-only. Keep its schema as a production gate; do not import it as
an active source or publish return KPIs until populated evidence is available.

`AUX_Menu_Demand_Forecast` and `AUX_Theoretical_Consumption` are active model
outputs. `AUX_Outlet_Master` is a synthetic demonstrator reference.
`AUX_Expiry_Estimate` is a synthetic batch-tranche scenario: each row is one
near-expiry FIFO tranche, not a complete POSIST batch ledger. Receipt-linked
rows carry synthetic GRN/PO/vendor lineage; opening-stock fallbacks are labelled
separately. Neither source is ABNAH production truth. Item identity is derived
from captured operational reports; vendor identity is mastered from the
quality-gated historical `Vendor Report` with transaction-only names retained
as exceptions. Scenario item and vendor masters are not active dependencies.

The remaining validated reports are retained as reconciliation, fallback, or
publication-gate sources. They do not all need to be imported for the first
dashboard build.

## Critical Production Gate: Purchase Orders

The latest UAT Enterprise Purchase Order item-detail export is populated: 113
rows match the validated 27-column contract. Expected delivery is present on 111
rows, while close or partial-receipt date is present on only 8 rows. Processed
quantity is positive on 8 rows and remaining quantity is positive on 105 rows.

This resolves the earlier header-only source gap, but not the production logic
gate:

- Link each PO line to the exact Enterprise Entry/GRN line.
- Approve normalized open, partial and closed status semantics.
- Define eligible closed lines and delivery tolerance for OTIF.
- Keep overdue PO and OTIF draft until those checks pass.
- Purchase Detail remains a weak fallback because only 2 of 288 rows carry PO
  identifiers and PO measures in the captured export.

Do not silently synthesize these fields in the production model.

## Calculation Guardrails

- Use **consumption**, never yield, on Page 3.
- Theoretical COGS comes from sold quantity x effective recipe x normalized
  ingredient cost.
- Actual consumption is opening + receipt + transfer in - transfer out - return
  - closing.
- Positive actual-minus-theoretical variance is potential consumption leakage.
- OTIF uses eligible closed PO lines only.
- Stockout risk value is forecast menu net sales, de-duplicated when one menu
  item has several risky ingredients.
- Exact expiry exposure is unavailable while the module is not enabled. The
  demo may show the packaged FIFO/shelf-life scenario only with a visible
  `Demo estimate - no POSIST batch/expiry source` label.
- Do not sum kg, litre and pieces into one quantity KPI.
- High inventory value is descriptive; it is not automatically a risk.

## JavaScript Decision

The four-page control tower can be built with native Zoho charts, KPI widgets,
dashboard tabs, user filters, report-as-filter behavior and conditional
formatting. No JavaScript is required for the core dashboard.

Zoho's JavaScript API is for controlling reports embedded in a separate web
application. Use it only if ABNAH later needs a custom portal shell or behavior
that native dashboards cannot provide:
https://www.zoho.com/analytics/js-api/

## Next Production Step

Replace each synthetic landing table independently with a controlled ABNAH
export, rerun the local structural/value auditor, compare the output packet to
the relevant contract, and reconcile the resulting Zoho report to the matching
truth-table grain before approving the KPI.

Read `CONTROL_TOWER_SOURCE_FEASIBILITY_GATE.md` before importing tables. It is
the authority for unavailable sources, exact surrounding report names and
which requested KPIs must remain hidden or provisional.
