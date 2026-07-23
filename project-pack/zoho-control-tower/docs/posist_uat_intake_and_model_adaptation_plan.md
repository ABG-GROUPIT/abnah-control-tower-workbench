# POSist UAT Intake And Model Adaptation Plan

This document defines how Codex should process the upcoming ABNAH POSist UAT access, POSist report screenshots, and POSist API documentation before changing the current data model.

The screenshot layer is a Codex working layer only. It is not an end-product feature, not a client-facing dashboard, and not a production ingestion method. Its purpose is to help Codex understand POSist's available screens, report structure, API fields, schema grain, and missing data points when the source evidence may arrive as 100 to 200 screenshots.

Final implementation should use POSist APIs, report exports, or governed database/feed connectors wherever possible. Screenshots are temporary discovery evidence used to design those connectors and adapt the model.

The current project is a synthetic Zoho Analytics proof-of-value. It uses synthetic POSIST-like raw reports, Neon raw/control schemas, FastAPI CSV feeds, and Zoho Query Tables organized as:

```text
RAW -> STD -> DIM -> FACT -> SUM -> Dashboards and Ask Zia
```

That structure should remain the adaptation backbone. POSist/UAT discoveries should be mapped into this layered model instead of directly changing dashboard charts one by one.

## 1. Current Model Baseline

Current raw/source families:

| Source family | Current role |
|---|---|
| `sales_report` | Daily outlet-item sales aggregate. |
| `purchase_report` | PO-style procurement lines. |
| `entry_report` | Receipt/GRN-style entries without direct PO number. |
| `inventory_closing_report` | Daily closing inventory by outlet/material. |
| `menu_master` | Sellable menu item master. |
| `vendor_report` | Vendor master. |
| `brand_recipe_consumption` | Recipe/BOM export for theoretical consumption. |
| `manual_calendar_events` | Manual event context. |
| `indian_calendar_holidays` | Holiday/calendar context. |
| `competitor_pricing` | Synthetic competitor price context. |

Current priority dashboard areas:

| Priority | Dashboard area | Current model objects |
|---|---|---|
| P0 | Inventory and Consumption Intelligence | `FACT_Inventory_Closing`, `FACT_Theoretical_Consumption`, `SUM_Inventory_Risk`, `DIM_Ingredient`, `STD_Recipe_BOM` |
| P0 | Vendor and Procurement Analytics | `FACT_Purchase_Order`, `FACT_Entry_Receipt`, `FACT_PO_Receipt_Comparison`, `FACT_Vendor_Spend`, `SUM_Vendor_Share`, `DIM_Vendor` |
| P1 | Sales and Revenue Intelligence | `FACT_Sales`, `SUM_Sales_Category_Mix`, `SUM_Menu_Item_Performance`, Ask Zia sales tables |
| P2 | Events, competitor context, and executive rollups | `FACT_Event_Sales_Impact`, `FACT_Competitor_Price_Position`, `FACT_Outlet_Daily_Health`, `SUM_Executive_KPIs` |

## 2. Intake Folder Structure

When the POSist material arrives, dump all files into one incoming folder:

```text
source_intake/
  posist_uat/
    _incoming_drop/
```

Subfolders are allowed inside `_incoming_drop/`. For example, use `inventory/`, `procurement/`, `api_docs/`, or any quick structure that is convenient during the UAT session.

For the POSist report screenshot flow, use the structured scaffold instead of a loose folder:

```powershell
python scripts\setup_posist_screenshot_structure.py
```

This creates:

```text
source_intake/
  posist_uat/
    _incoming_drop/
      posist_ss/
        p1_main/
        p2_reports/
        p3_examples/
        p4_stock_admin/
```

The structure is:

```text
POSist page -> report section -> individual report -> screenshot slot
```

See `source_intake/posist_uat/structured_screenshot_capture_guide.md` for capture rules, scroll handling, naming, and local OCR/LLM workflow.

Then run:

```powershell
scripts\prepare_posist_screenshot_intake.bat
```

The script creates a dated Codex analysis batch:

```text
source_intake/
  posist_uat/
    batches/
      YYYY-MM-DD/
        00_manifest.csv
        05_codex_analysis_outputs/
```

Do not mix POSist screenshots with the existing Zoho dashboard screenshot folder. The current `Dashboard Screenshots` folder is useful as Zoho build evidence, but POSist/UAT screenshots need a separate source-intake trail for Codex analysis.

The `05_codex_analysis_outputs/` folder is for intermediate extraction and mapping artifacts. These files exist so Codex can reason over a large screenshot/API batch systematically; they are not part of the end-user product.

## 3. Screenshot Manifest

Every generated batch includes `00_manifest.csv`. Minimum columns:

```text
artifact_id,capture_order,file_name,relative_path,artifact_kind,posist_module,screen_or_report_name,menu_path_or_url,outlet_filter,date_filter,other_filters,visible_columns_or_metrics,priority_domain,analysis_status,notes
```

Recommended `priority_domain` values:

```text
inventory_consumption
vendor_procurement
sales_revenue
master_data
settings_admin
api_documentation
unknown
```

The manifest is important because 100 to 200 screenshots cannot be reliably interpreted from image content alone. The manifest preserves navigation path, filter context, and intended business meaning so Codex can group related screenshots, detect duplicates, and map fields to the current model.

## 4. Screenshot Capture Rules

Use direct screen screenshots when possible. Phone photos are acceptable only if direct screenshots are blocked.

For POSist report screens:

1. Capture the report title, selected filters, date range, outlet/store filter, visible columns, totals, and pagination controls.
2. If a table scrolls horizontally, take overlapping screenshots from left to right.
3. If a table scrolls vertically, take top, middle, and bottom screenshots with overlapping rows.
4. If the report supports export to CSV/XLS/PDF, save the export under `_incoming_drop/` near the related screenshot set.
5. Use readable filenames:

```text
inventory_closing__outlet_all__2026-07-10__part01.png
purchase_order_detail__outlet_cp__2026-07-10__part02.png
api_docs__purchase_orders__response_schema__part01.png
```

For API documentation screenshots:

1. Capture endpoint title, method, path, authentication notes, request parameters, response schema, sample response, pagination, and rate-limit/error rules.
2. If docs are available as PDF, HTML, Postman collection, Swagger/OpenAPI, or plain text, save the original file under `_incoming_drop/`. Screenshots should be a backup, not the only source.
3. If sample API responses are available, save redacted JSON/CSV samples under `_incoming_drop/`.

## 4A. Current Restroworks API Packet

Codex has started a structured packet from the public Restroworks API reference at `https://api.restroworks.com/#intro`:

```text
source_intake/posist_uat/restroworks_api_docs_packet/
```

Initial usefulness finding:

| Priority | API area | Why it matters |
|---|---|---|
| P0 | Stock `fetch_Inventory_data` | Candidate source for inventory transactions, purchase/PO mode, stock entry, physical stock, vendor returns, wastage, opening stock, and stock sale. |
| P0 | Stock `get_indents` | Candidate source for internal indent/requisition movement between supplier and receiver stores. |
| P1 | Data Integration `bills` | Candidate source for bill/KOT item lines, item quantities, sales categories, taxes, discounts, payments, and theoretical consumption drivers. |
| P1 | Online Order menu/out-of-stock | Candidate source for menu dimensions and online item availability context. |

Before any SQL model changes, confirm in ABNAH UAT whether these endpoints are enabled for ABNAH, what base URL/authentication is used, and whether sample responses match the public documentation.

## 4B. Current Stock Administration Screenshot Finding

The separate POSist Stock Administration area appears to contain the BOH/raw-report families that were not visible in the earlier FOH-style report screenshots.

Manually reviewed sample screenshots from:

```text
C:\Users\ARNAV\Downloads\Stock Administration
```

Observed Stock Administration sections:

| Section | Why it matters for ABNAH phase 1 |
|---|---|
| Enterprise Reports | Entry, Vendor Price, Stock Return, Consumption, Re-order, Purchase Order, Consolidated Indent, Variance, Bill Passing, Wastage, Purchase Summary, Internal Indent, Food Cost. |
| Transactional Reports | Entry, Stock Return, Purchase Detail, Purchase Requisition, Bill Passing, Stock In Stock Out. |
| PO/SO Reports | Purchase Order, Standing Purchase Order, Sales Order, ERP Vendor Invoice. |
| Indent Reports | Indent, Consolidated Indent, Consolidated Indent Items, Issue, outlet-wise consolidated indent, returns. |
| Aggregation Reports | Consumption, Variance, Movement, Finished Food, Recipe Consumption. |
| Analytical Reports | Food Cost, Re-order Level, Closing Stock, Cost Margin, Pricing Ledger, Purchase Summary, Stock Recipe. |
| Other Reports | Expiry, Default Cost, Kitchen Wise Item, Vendor Pricing, Late Delivery, Vendor Last 5 Purchase Price, Yield, Production Plan, Gate Pass, Bin Packaging. |

Working conclusion: the missing inventory/procurement report gap is likely a navigation/module-access gap, not proof that POSist lacks those datasets. Treat `p4_stock_admin` as the first capture priority for phase 1.

Remaining gate: this is conclusive for UI navigation, but not sufficient for final schema or SQL changes until exports, API sample responses, or field-level screenshots confirm columns, keys, grain, refresh behavior, and reconciliation totals.

## 5. Extraction Workflow

After the intake folder is ready, process it in this order.

### 5.1 Inventory The Material

Create `05_codex_analysis_outputs/intake_inventory.csv` with:

```text
file_name,file_type,folder,byte_size,image_width,image_height,manifest_status,notes
```

Confirm every screenshot has a manifest row. Flag unknowns before model design starts.

### 5.2 Extract Screen And Report Structure

Create or fill `05_codex_analysis_outputs/screen_catalog_seed.csv` with:

```text
source_file,posist_module,screen_or_report_name,chart_or_table_name,visible_fields,visible_filters,visible_metrics,grain_hint,business_question,priority_domain,confidence,notes
```

For each screen, capture:

- report names and module names,
- visible columns and measures,
- filters and date controls,
- totals/subtotals,
- likely data grain,
- whether the screen supports export,
- whether the screen maps to an existing dashboard need.

### 5.3 Extract API Documentation

Create or fill `05_codex_analysis_outputs/api_endpoint_catalog_seed.csv` with:

```text
endpoint_name,method,path,auth_type,request_params,response_fields,response_grain,pagination,incremental_key,rate_limit,priority_domain,notes
```

Create or fill `05_codex_analysis_outputs/api_field_catalog_seed.csv` with:

```text
endpoint_name,field_name,field_type,description,nullable,sample_value,semantic_role,possible_current_mapping,notes
```

### 5.4 Build The Mapping Matrix

Create or fill `05_codex_analysis_outputs/posist_to_current_model_mapping_seed.csv` with:

```text
priority_domain,posist_source,posist_field,current_layer,current_table,current_field,mapping_type,grain_match,action_required,validation_rule,notes
```

Use these `mapping_type` values:

| Mapping type | Meaning |
|---|---|
| `direct_existing` | POSist field maps cleanly to a current field. |
| `rename_or_cast` | Field exists conceptually but needs naming/type conversion. |
| `new_raw_column` | Existing raw source table needs another field. |
| `new_raw_table` | New POSist source family is required. |
| `new_dimension` | New reusable entity is required. |
| `new_fact` | New activity grain is required. |
| `dashboard_only_context` | Useful label/context but not a core model field yet. |
| `ignore_or_backlog` | Not needed for phase 1. |

## 6. Phase 1 Field Discovery Priorities

ABNAH's first focus is inventory/consumption intelligence and vendor/procurement. During POSist review, prioritize these data points.

### 6.1 Inventory And Consumption

Look for:

- opening stock,
- closing stock,
- stock in,
- stock out,
- material issue,
- recipe consumption,
- production consumption,
- actual consumption posting,
- stock adjustment,
- wastage/spoilage,
- transfer in and transfer out,
- physical count,
- min/max level,
- reorder level,
- safety stock,
- lead time,
- batch number,
- expiry date,
- UOM conversion,
- stock valuation method,
- item-to-vendor mapping,
- item category and storage location.

Model impact if available:

| POSist data point | Current limitation removed | Likely model change |
|---|---|---|
| Actual consumption or material issue | Current model has theoretical consumption only. | Add `FACT_Actual_Consumption` and actual-vs-theoretical variance summaries. |
| Wastage/spoilage | Cannot explain inventory leakage. | Add wastage fact and variance reasons. |
| Transfers | Cannot separate consumption from inter-outlet movement. | Add transfer fact and outlet-to-outlet flow dashboard. |
| Reorder levels and lead time | Low stock is only heuristic. | Replace simple low-stock bands with reorder/stockout-risk logic. |
| Batch and expiry | Cannot track freshness risk. | Add batch/expiry inventory aging summary. |
| UOM conversion | Ingredient comparisons may be inconsistent. | Add canonical unit conversion dimension. |

### 6.2 Vendor And Procurement

Look for:

- purchase order header,
- purchase order line,
- PO status history,
- approval status,
- expected delivery date,
- actual delivery timestamp,
- GRN/receipt rows with PO number,
- invoice number and invoice value,
- vendor item rate history,
- vendor contracts or preferred vendor flags,
- returns to vendor,
- rejected quantity and rejection reason,
- payment status,
- tax and charges breakdown,
- vendor master status,
- vendor lead time,
- vendor quality/QC fields.

Model impact if available:

| POSist data point | Current limitation removed | Likely model change |
|---|---|---|
| PO number on GRN/receipt | Current PO-to-receipt match is approximate. | Update `FACT_PO_Receipt_Comparison` to exact matching. |
| Actual delivery timestamp | Cannot measure vendor lateness. | Add delivery SLA metrics. |
| Rejection/QC fields | Cannot score vendor quality. | Add vendor quality fact and scorecard. |
| Rate history | Cannot analyze vendor price movement. | Add price trend and variance summaries. |
| Payment status | Cannot connect procurement to payable status. | Add payable/procurement lifecycle fields. |

### 6.3 Sales And Revenue

Sales remains important but phase 2. Still capture sales fields while reviewing POSist because sales drives consumption and demand.

Look for:

- bill/order ID,
- line item ID,
- order timestamp,
- channel,
- payment mode,
- discount reason,
- void/refund,
- taxes and service charge,
- customer count,
- modifier/add-on detail,
- combo detail,
- cashier/user,
- table/session,
- delivery aggregator,
- item-level price before and after discount.

Model impact if available:

| POSist data point | Current limitation removed | Likely model change |
|---|---|---|
| Bill/order ID | Current sales is daily item aggregate. | Add bill-line fact for basket and attach-rate analysis. |
| Order timestamp | No daypart analysis. | Add hourly/daypart sales tables. |
| Discounts and voids | Cannot explain realized price. | Add discount/void analysis. |
| Channel/payment | Cannot split dine-in/delivery/payment behavior. | Add channel and payment dimensions. |

## 7. Adaptation Design Rules

Use these rules before modifying code or SQL:

1. Keep RAW source data untouched and auditable.
2. Add POSist-specific raw tables or adapters before changing canonical `STD_*` outputs.
3. Preserve current synthetic feeds until the POSist connector is proven.
4. Keep outlet, vendor, item, ingredient, date, and document-number keys explicit.
5. Do not downgrade current dashboard fields. Add compatibility columns where needed.
6. Promote a POSist field to `DIM_*`, `FACT_*`, or `SUM_*` only after its grain and refresh behavior are understood.
7. Prefer exact document keys over fuzzy matching whenever POSist provides them.
8. Separate current-state inventory snapshots from movement facts.
9. Separate theoretical consumption, actual consumption, wastage, and transfer movement.
10. Document every caveat that remains after POSist mapping.

## 8. Target Future Architecture

The current synthetic flow stays available for demo continuity:

```text
Synthetic CSV -> Neon raw -> FastAPI CSV feeds -> Zoho RAW -> STD/DIM/FACT/SUM
```

The POSist-aware flow should add a source adapter path:

```text
POSist API or report export
-> POSist raw landing tables/files
-> source-to-canonical adapters
-> canonical STD tables
-> DIM/FACT/SUM model
-> Zoho dashboards and Ask Zia
```

Possible implementation options:

| Option | When to use |
|---|---|
| FastAPI pulls POSist API and serves canonical CSV feeds | Use when POSist API access is reliable and Zoho should keep Web URL import. |
| Scheduled ETL writes POSist data into Neon raw tables | Use when we need history, auditability, and repeatable validation. |
| POSist report exports loaded manually during discovery | Use during UAT before stable API credentials and refresh rules are known. |
| Direct Zoho import from POSist/exported files | Use only as temporary exploration, not the preferred governed model. |

## 9. Model Change Gates

Do not implement model changes until these gates are satisfied.

| Gate | Requirement |
|---|---|
| Source catalog complete | Every screenshot/API artifact has a manifest entry and extracted catalog row. |
| Priority tagged | Each source is tagged P0 inventory/procurement, P1 sales, or backlog. |
| Grain identified | Each source has a known grain such as outlet-date-item, PO-line, GRN-line, stock movement, bill-line. |
| Keys identified | Primary keys and join keys are documented. |
| Refresh behavior known | API pagination, incremental fields, and update/delete behavior are known or explicitly unknown. |
| Validation rule defined | UI totals or exported samples can be reconciled to raw/STD/fact totals. |

## 10. Expected Outputs After POSist Material Arrives

After processing the screenshots and API docs, Codex should produce these working outputs:

1. `intake_inventory.csv`
2. `screen_catalog_seed.csv`
3. `api_endpoint_catalog_seed.csv`
4. `api_field_catalog_seed.csv`
5. `posist_to_current_model_mapping_seed.csv`
6. a prioritized gap report for P0 inventory/procurement
7. an updated data model plan
8. a SQL/model change list
9. a dashboard change list
10. a validation checklist comparing POSist UI/report totals against modeled outputs

These outputs are analysis artifacts. They are useful because they let Codex adapt the raw landing layer, canonical `STD_*` tables, dimensions, facts, summaries, and dashboards with traceability back to the POSist evidence. They should not be presented as the final product experience.

## 11. First Adaptation Backlog

Start with these workstreams once POSist data is understood:

| Order | Workstream | Outcome |
|---:|---|---|
| 1 | POSist inventory/procurement source catalog | Know exactly which POSist reports/API endpoints support phase 1. |
| 2 | POSist field-to-current-model mapping | Decide direct maps, new fields, and new facts. |
| 3 | Raw landing/adapters | Add raw/API ingestion without breaking synthetic demo feeds. |
| 4 | Inventory model extension | Add actual consumption, wastage, transfers, reorder levels, expiry/batch if available. |
| 5 | Procurement model extension | Add exact PO-GRN matching, vendor SLA, rate history, QC/returns if available. |
| 6 | Dashboard refresh | Update Dashboard 4 first, Dashboard 3 second, then Sales/Revenue. |
| 7 | Ask Zia refresh | Add Zia-safe P0 tables for new inventory/procurement facts. |

## 12. Caveats

- Screenshots are Codex discovery evidence for UI/report structure, not proof of data type, completeness, or refresh behavior.
- The screenshot layer is not a production connector, not a dashboard feature, and not the end product.
- API docs may describe fields that are not enabled in ABNAH's UAT tenant.
- UI totals must be reconciled against exported data or API responses before they are used as validation truth.
- Do not label inventory pressure as stockout prediction unless POSist provides reorder levels, lead time, and movement history.
- Do not label consumption variance as actual-vs-theoretical unless actual consumption, wastage, adjustments, and transfers are separated.
