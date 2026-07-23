# Zoho Analytics Data Model Plan

This document is the modeling specification for the ABNAH Cafe Intelligence Synthetic Demo in Zoho Analytics.

The project README is the master architecture source. Neon/PostgreSQL is the simulated POSIST-like backend. FastAPI exposes CSV feeds. Zoho Analytics imports those feeds into RAW tables, then performs standardization, dimensional modeling, query-table analysis, and dashboarding.

## Architecture Rule

The Zoho workspace should import fixed RAW tables from FastAPI CSV feed endpoints. Operational reports are imported per outlet:

- `RAW_Sales_Report_OUT001`
- `RAW_Sales_Report_OUT002`
- `RAW_Sales_Report_OUT003`
- `RAW_Purchase_Report_OUT001`
- `RAW_Purchase_Report_OUT002`
- `RAW_Purchase_Report_OUT003`
- `RAW_Entry_Report_OUT001`
- `RAW_Entry_Report_OUT002`
- `RAW_Entry_Report_OUT003`
- `RAW_Inventory_Closing_Report_OUT001`
- `RAW_Inventory_Closing_Report_OUT002`
- `RAW_Inventory_Closing_Report_OUT003`

Static/master reports are imported once and shared:

- `RAW_Menu_Master`
- `RAW_Vendor_Report`
- `RAW_Brand_Recipe_Consumption`
- `RAW_Indian_Calendar_Holidays`
- `RAW_Manual_Calendar_Events`
- `RAW_Competitor_Pricing`

Do not create separate Month 1, Month 2, or Month 3 RAW tables. Each FastAPI endpoint returns the full current report for that outlet or static table. Zoho refresh/re-fetch should update the same imported RAW table.

## Outlet-Aware Modeling Rule

The model must support one cross-outlet executive dashboard and outlet-specific module dashboards.

Operational `STD_*`, `FACT_*`, and non-executive `SUM_*` tables must preserve outlet grain through:

- `outlet_code`
- `outlet_name`
- `market_area`

The synthetic outlet mapping is derived from existing report fields:

| Outlet code | Outlet name | Market area |
|---|---|---|
| `OUT001` | `ABNAH Cafe Connaught Place` | `Connaught Place` |
| `OUT002` | `ABNAH Cafe Hauz Khas` | `Hauz Khas` |
| `OUT003` | `ABNAH Cafe Saket Premium` | `Saket` |

Non-operational static tables such as menu master, vendor master, recipe BOM, and holiday calendar do not contain outlet rows in the raw data. Do not invent duplicated outlet rows for those tables. Instead, join them to outlet-aware facts where outlet context exists.

Competitor pricing contains `market_area`; competitor facts and summaries should map competitor context to outlet market area.

## Modeling Rules

1. Do not manually edit RAW tables except for import and refresh settings.
2. Use `row_id` as the unique source identifier.
3. Preserve ABNAH-style raw report integrity.
4. Put all cleaning, type alignment, and naming standardization in `STD_*` query tables.
5. Put reusable business entities in `DIM_*` query tables.
6. Use `FACT_*` and `SUM_*` tables for dashboards.
7. Do not claim full forecasting, true stockout prediction, or full actual-vs-theoretical variance.
8. Use competitor pricing as context, not proof of sales causation.
9. Treat event impact as explanatory and directional unless validated with stronger statistical controls.
10. For non-executive dashboards, do not aggregate across all outlets unless outlet is included in the grouping.

## Layer 1: Standardized Query Tables

These tables clean names, coerce dates/numbers where possible, and rename fields to stable analysis names.

| Query table | Purpose | Source tables | Required grain | SQL file | Expected outlet fields | Dashboard usage | Caveats |
|---|---|---|---|---|---|---|---|
| `STD_Sales_Report` | Union outlet-specific RAW sales feeds and standardize outlet-item daily sales. | `RAW_Sales_Report_OUT001/OUT002/OUT003` | Outlet + date + item | `01_std_sales_report.sql` | `outlet_code`, `outlet_name`, `market_area` | Sales, menu mix, outlet health, event impact. | Date casts may need Zoho syntax validation. |
| `STD_Purchase_Report` | Union outlet-specific RAW purchase feeds and standardize purchase order lines. | `RAW_Purchase_Report_OUT001/OUT002/OUT003` | Outlet + PO line + vendor + item | `02_std_purchase_report.sql` | `outlet_code`, `outlet_name`, `market_area` | Vendor analytics, PO receipt comparison. | PO lines are synthetic and line-level, not accounting-approved purchase facts. |
| `STD_Entry_Report` | Union outlet-specific RAW entry feeds and standardize receipt/GRN lines. | `RAW_Entry_Report_OUT001/OUT002/OUT003` | Outlet + receipt line + vendor + item | `03_std_entry_report.sql` | `outlet_code`, `outlet_name`, `market_area` | Receipt analytics, PO comparison, vendor spend. | Entry rows do not carry direct PO number; matching to PO is approximate. |
| `STD_Inventory_Closing_Report` | Union outlet-specific RAW inventory feeds and standardize daily closing inventory. | `RAW_Inventory_Closing_Report_OUT001/OUT002/OUT003` | Outlet + date + inventory item | `04_std_inventory_closing_report.sql` | `outlet_code`, `outlet_name`, `market_area` | Inventory risk, outlet health. | Low stock flags are heuristic, not true stockout prediction. |
| `STD_Menu_Master` | Standardize menu item master. | `RAW_Menu_Master` | Menu item | `05_std_menu_master.sql` | Not present in raw; outlet added through sales facts. | Sales mix, competitor mapping. | Do not duplicate menu rows per outlet. |
| `STD_Vendor_Report` | Standardize vendor master. | `RAW_Vendor_Report` | Vendor | `06_std_vendor_report.sql` | Not present in raw; outlet added through purchase/receipt facts. | Vendor dimension, vendor share. | Vendor compliance fields are synthetic demo fields. |
| `STD_Recipe_BOM` | Normalize ABNAH-style recipe block export. | `RAW_Brand_Recipe_Consumption` | Recipe + ingredient | `07_std_recipe_bom.sql` | Not present in raw; outlet added through sales/theoretical consumption facts. | Theoretical consumption and recipe-to-material drilldown. | Fill-down correlated subquery needs Zoho syntax validation. |
| `STD_Holiday_Calendar` | Standardize configured holiday/calendar markers. | `RAW_Indian_Calendar_Holidays` | Calendar date + holiday | `08_std_holiday_calendar.sql` | Not outlet-specific. | Holiday overlays and event intelligence. | Synthetic calendar rows must be verified for production use. |
| `STD_Manual_Events` | Standardize admin/manual business events. | `RAW_Manual_Calendar_Events` | Event + date range + affected scope | `09_std_manual_events.sql` | Affected outlets stored as text scope, not exploded rows. | Event impact and dashboard annotations. | Affected outlets/items are semicolon-delimited text lists. |
| `STD_Competitor_Pricing` | Standardize competitor price mapping. | `RAW_Competitor_Pricing` | Market area + competitor + ABNAH item | `10_std_competitor_pricing.sql` | `outlet_code`, `outlet_name`, `market_area` derived from market area. | Competitor positioning. | Context only; not causal proof. |

## Layer 2: Dimension Query Tables

| Query table | Purpose | Source tables | Required grain | SQL file | Expected columns | Caveats |
|---|---|---|---|---|---|---|
| `DIM_Date` | Reusable calendar dimension from all date-bearing reports. | `STD_*` date tables | Date | `11_dim_date.sql` | Date, year, month, month key, quarter, weekday. | Date functions may need Zoho syntax validation. |
| `DIM_Outlet` | Reusable outlet list. | Sales, purchase, entry, inventory | Outlet | `12_dim_outlet.sql` | `outlet_code`, `outlet_name`, `market_area` | No separate outlet master feed exists. |
| `DIM_Menu_Item` | Reusable menu item list. | Menu master, sales, competitor pricing | Menu item | `13_dim_menu_item.sql` | Menu item id/name/category/rate. | Sales items should match menu master by `item_number`. |
| `DIM_Vendor` | Reusable vendor list. | Vendor master, purchase, entry | Vendor | `14_dim_vendor.sql` | Vendor name/code/contact/state/compliance. | Purchase/entry vendor names are the practical join key. |
| `DIM_Ingredient` | Reusable material/ingredient list. | Inventory, purchase, entry, recipe BOM | Ingredient/material | `15_dim_ingredient.sql` | Ingredient name/code/category/unit. | Some BOM ingredients do not carry item codes. |
| `DIM_Event` | Reusable manual event dimension. | Manual events | Event | `16_dim_event.sql` | Event id, name, type, dates, scope, confidence. | Semicolon scope fields stay text unless manually split in Zoho. |
| `DIM_Holiday` | Reusable holiday dimension. | Holiday calendar | Holiday/date | `30_dim_holiday.sql` | Holiday date/name/type/impact. | Supplemental file because the original output list omitted this object. |
| `DIM_Competitor` | Reusable competitor dimension. | Competitor pricing | Competitor/market | `31_dim_competitor.sql` | Competitor id/name/market/category. | Supplemental file because the original output list omitted this object. |

## Layer 3: Fact / Analysis Query Tables

| Query table | Purpose | Required grain | Source tables | SQL file | Required outlet fields | Dashboard usage | Caveats |
|---|---|---|---|---|---|---|---|
| `FACT_Sales` | Sales fact enriched with menu and holiday metadata. | Outlet + date + item | `STD_Sales_Report`, `DIM_Menu_Item`, `STD_Holiday_Calendar` | `17_fact_sales.sql` | `outlet_code`, `outlet_name`, `market_area` | Executive, outlet sales/menu, event, competitor. | Daily outlet-item aggregate, not individual bills. |
| `FACT_Purchase_Order` | Purchase order line fact. | Outlet + PO line + item + vendor | `STD_Purchase_Report`, `DIM_Vendor`, `DIM_Ingredient` | `18_fact_purchase_order.sql` | `outlet_code`, `outlet_name`, `market_area` | Procurement and vendor analytics. | PO status is synthetic but internally consistent. |
| `FACT_Entry_Receipt` | Receipt/GRN line fact. | Outlet + receipt line + item + vendor | `STD_Entry_Report`, `DIM_Vendor`, `DIM_Ingredient` | `19_fact_entry_receipt.sql` | `outlet_code`, `outlet_name`, `market_area` | Receipt analytics and PO comparison. | No direct PO number in entry feed. |
| `FACT_Inventory_Closing` | Daily inventory closing fact. | Outlet + date + inventory item | `STD_Inventory_Closing_Report`, `DIM_Ingredient` | `20_fact_inventory_closing.sql` | `outlet_code`, `outlet_name`, `market_area` | Inventory risk, outlet health. | Inventory pressure is heuristic. |
| `FACT_Theoretical_Consumption` | Estimate ingredient consumption from sales and recipe BOM. | Outlet + date + sold menu item + ingredient | `FACT_Sales`, `STD_Recipe_BOM` | `21_fact_theoretical_consumption.sql` | `outlet_code`, `outlet_name`, `market_area` | Recipe/material analysis and inventory pressure explanation. | Not full variance because actual consumption/wastage is not available. |
| `FACT_PO_Receipt_Comparison` | Compare ordered/processed PO lines with receipts. | Outlet + PO line + vendor + item | `FACT_Purchase_Order`, `FACT_Entry_Receipt` | `22_fact_po_receipt_comparison.sql` | `outlet_code`, `outlet_name`, `market_area` | Pending/partial PO analysis. | Approximate match due to missing PO number in entries. |
| `FACT_Event_Sales_Impact` | Connect event windows to sales and compute directional lift. | Outlet + event + date + category/item where possible | `DIM_Event`, `FACT_Sales` | `23_fact_event_sales_impact.sql` | `outlet_code`, `outlet_name`, `market_area` | Event intelligence and spike explanation. | Baseline date arithmetic/string matching may need Zoho syntax validation. |
| `FACT_Competitor_Price_Position` | Connect competitor price context to ABNAH item sales. | Outlet/market_area + competitor + ABNAH item | `STD_Competitor_Pricing`, `FACT_Sales` | `24_fact_competitor_price_position.sql` | `outlet_code`, `outlet_name`, `outlet_market_area`, `market_area` | Competitor dashboard. | Context only; no causation claim. |
| `FACT_Outlet_Daily_Health` | Daily outlet-level operational summary. | Outlet + date | Sales, purchase, entry, inventory, events | `25_fact_outlet_daily_health.sql` | `outlet_code`, `outlet_name`, `market_area` | Executive and outlet health. | Aggregates are directional demo KPIs. |
| `FACT_Vendor_Spend` | Vendor spend summary from purchase and receipt data. | Outlet + vendor + date/month | Purchase order and entry receipt facts | `32_fact_vendor_spend.sql` | `outlet_code`, `outlet_name`, `market_area` | Vendor share and spend questions. | Supplemental file because the original output list omitted this object. |

## Layer 4: Dashboard Summary Query Tables

| Query table | Purpose | Required grain | SQL file | Required outlet behavior | Dashboard usage | Caveats |
|---|---|---|---|---|---|---|
| `SUM_Executive_KPIs` | Compact KPI metric list for executive dashboard. | All-outlet metric list | `33_sum_executive_kpis.sql` | May contain all-outlet totals. | Executive headline KPIs. | This is the only summary where all-outlet totals are acceptable by default. |
| `SUM_Outlet_Health` | Outlet health comparison rollup. | Outlet | `34_sum_outlet_health.sql` | Must compare outlets and include `outlet_code`, `outlet_name`, `market_area`. | Executive / outlet comparison. | Health band is a simple weighted indicator. |
| `SUM_Sales_Category_Mix` | Category and super-category sales contribution. | Outlet + category | `35_sum_sales_category_mix.sql` | Must include `outlet_code`, `outlet_name`, `market_area`. | Outlet-specific sales/menu dashboard. | Share should be calculated within outlet. |
| `SUM_Menu_Item_Performance` | Menu item performance ranking. | Outlet + menu item | `36_sum_menu_item_performance.sql` | Must include `outlet_code`, `outlet_name`, `market_area`. | Outlet-specific menu intelligence. | Competitor mapping is partial by design. |
| `SUM_Vendor_Share` | Vendor share of PO and receipt value. | Outlet + vendor | `26_sum_vendor_share.sql` | Must include `outlet_code`, `outlet_name`, `market_area`. | Outlet-specific procurement dashboard. | Share should be calculated within outlet. |
| `SUM_Inventory_Risk` | Latest inventory pressure summary. | Outlet + inventory item | `27_sum_inventory_risk.sql` | Must include `outlet_code`, `outlet_name`, `market_area`. | Outlet-specific inventory dashboard. | Not a stockout forecast. |
| `SUM_Event_Impact` | Event lift summary. | Outlet + event + date/category/item | `28_sum_event_impact.sql` | Must include `outlet_code`, `outlet_name`, `market_area`. | Outlet-specific event dashboard. | Treat lift as directional. |
| `SUM_Competitor_Positioning` | Competitor price and mapped sales summary. | Outlet/market_area + competitor/category | `29_sum_competitor_positioning.sql` | Must include `outlet_code`, `outlet_name`, and/or market-area fields. | Outlet-specific competitor dashboard. | Context only; no causation claim. |
| `SUM_Event_Markers` | Spike explanation panel / chart annotation table. | Outlet + event + date | `37_sum_event_markers.sql` | Must include `outlet_code`, `outlet_name`, `market_area`. | Annotation replacement if Zoho chart annotations are unavailable. | Uses text panels/tables instead of native annotations. |

## Dashboard Scope

Dashboard 1, Executive / Outlet Comparison / Outlet Health, is cross-outlet.

Dashboards 2 through 5 are outlet-specific module templates. Use one shared query-table model, then apply a locked dashboard filter or duplicated dashboard pages per outlet:

- `Sales_Menu_OUT001`
- `Sales_Menu_OUT002`
- `Sales_Menu_OUT003`

Repeat the same approach for procurement, inventory, and calendar/competitor dashboards.

Do not create files such as `FACT_Sales_OUT001` unless Zoho filter locking is not viable. Separate outlet SQL files are an optional fallback, not the preferred design.

## Recipe BOM Fill-Down Strategy

`RAW_Brand_Recipe_Consumption` mimics the real export: `recipe_name`, `recipe_qty`, and `recipe_unit` appear only on the first row of each recipe block. Continuation rows are blank.

The preferred Zoho query-table approach is in `07_std_recipe_bom.sql`:

1. Use the zero-padded `row_id` sequence.
2. For each row, find the latest previous-or-current nonblank recipe row.
3. Copy that recipe name, qty, and unit onto continuation rows.

This needs Zoho SQL syntax validation because correlated subqueries and scalar subselects can vary by workspace/version.

Stable fallback if Zoho cannot run the fill-down query:

1. Keep importing `RAW_Brand_Recipe_Consumption` as the audit/demo visual feed.
2. Add a FastAPI technical feed named `/zoho/brand_recipe_consumption_normalized.csv`.
3. Import it as `STD_Recipe_BOM` or as a new RAW technical table and then create a trivial `STD_Recipe_BOM` query table from it.

## Refresh Behavior

Refresh RAW tables from FastAPI feeds. If Zoho supports replace/re-fetch mode, use it. If Zoho supports update/add with a key, use `row_id`.

Do not use blind append mode unless you have verified deduplication, because the FastAPI endpoint returns the full current report each time. Blind append can duplicate rows inside Zoho.

Test refresh behavior with the three outlet sales RAW tables first before importing all eighteen RAW tables. The first four `STD_*` tables should then union the outlet RAW imports and produce the combined operational totals.
