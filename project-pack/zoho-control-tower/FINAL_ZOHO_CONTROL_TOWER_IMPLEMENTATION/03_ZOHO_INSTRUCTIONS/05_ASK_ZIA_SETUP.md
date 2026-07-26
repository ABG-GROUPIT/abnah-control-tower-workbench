# Zoho Control Tower v2 - Ask Zia Setup

## Deployment Gate

Ask Zia is an optional presentation layer. Configure it only after:

1. all 14 landing tables are imported;
2. all 38 Query Tables are built in manifest order;
3. all saved reports and the five KPI objects inside each of the four page
   dashboards reconcile to the truth pack; and
4. every unresolved production limitation is visible to the reviewer.

Do not create a second semantic SQL layer for the first implementation. The
current fact and summary tables already provide controlled grains for Ask Zia.

The uppercase table names in this guide are logical model labels. In Zoho,
select the numbered `.sql` Query Table mapped by `logical_model_name` in
`zoho_control_tower_v2_sql/QUERY_TABLE_MANIFEST.csv`. For example,
`FACT_CT_Inventory_Risk` is `27_fact_ct_inventory_risk.sql`.

Zoho supports table and column synonyms, table and column priority, default
functions, and excluding a table from Ask Zia. Use these controls to prevent
the assistant from selecting raw or intermediate tables:
https://www.zoho.com/analytics/help/train-ask-zia.html

## Governed Table Set

Give these tables high priority:

| Table | Business purpose | Suggested table synonyms |
| --- | --- | --- |
| `FACT_CT_Inventory_Risk` | Ingredient stockout and days-cover action list | inventory risk, stock risk, shortage action |
| `FACT_CT_Expiry_Risk` | Explicitly synthetic expiry scenario for the demonstrator | demo expiry estimate, synthetic near-expiry risk |
| `FACT_CT_Menu_Impact` | Menu items and forecast revenue affected by ingredient risk | menu impact, revenue at risk |
| `FACT_CT_Risky_PO` | Open PO lines connected to current inventory risk | risky purchase orders, urgent POs |
| `FACT_CT_Purchase_Order` | Detailed order, pending value and delay state | purchase orders, POs |
| `FACT_CT_Purchase_Receipt` | Detailed accepted receipt lines and paid prices | receipts, GRNs, goods received |
| `SUM_CT_Procurement_Funnel` | Ordered, processed, pending and delayed values | procurement funnel, PO pipeline |
| `SUM_CT_Vendor_Scorecard` | Synthetic linked-line vendor service measures | vendor scorecard, supplier performance |
| `SUM_CT_Price_Movement` | Same-item and same-UOM receipt price changes | price movement, purchase price trend |
| `FACT_CT_Consumption_Variance` | Actual versus theoretical ingredient consumption | consumption variance, usage variance |
| `FACT_CT_Menu_Profitability` | Detailed menu revenue, theoretical COGS and margin | menu profitability, item margin |
| `SUM_CT_Menu_Profitability` | Menu profitability and BCG classification | menu engineering, menu matrix |
| `SUM_CT_SCM_Monthly` | Monthly SCM executive measures | SCM monthly, control tower summary |
| `FACT_CT_Data_Quality_Exception` | Drillable model and source exceptions | data quality, data exceptions |
| `SUM_CT_Financial_Leakage` | Observed wastage value only | wastage leakage, observed leakage |

Give dimension tables low or medium priority for filtering context. Exclude all
`RAWN_CT_*`, `STD_CT_*`, and `AUX_*` tables from Ask Zia. Also exclude every
legacy table from the older 37-query model.

## Column Settings

Apply these synonyms where the corresponding column exists:

| Column | Suggested synonyms |
| --- | --- |
| `source_period_code` | period, month |
| `outlet_name` | outlet, store, location |
| `item_name` or `ingredient_name` | ingredient, raw material, inventory item |
| `menu_item_name` | menu item, product |
| `vendor_name` | vendor, supplier |
| `risk_severity` | risk level, severity |
| `shortage_qty` | shortage, shortfall quantity |
| `days_cover` | stock cover, days of inventory |
| `open_po_value` | open PO value, pending PO value, committed capital |
| `pending_value` | pending procurement value, outstanding PO value |
| `delayed_value` | delayed PO value, overdue value |
| `unit_price_change_percent` | price change percent, purchase inflation |
| `variance_qty` | consumption variance quantity, usage variance |
| `variance_value` | consumption variance value, leakage value |
| `gross_margin_percent` | gross margin percent, margin rate |
| `exception_type` | data issue, exception category |

Set additive currency and quantity fields to `Sum` only at their declared
grain. Set percentage, rate, unit-price, days-cover and deviation fields to
`Average` or no default aggregate as appropriate. Never sum:

- `otif_percent`
- `fill_rate_percent`
- `unit_price_change_percent`
- `gross_margin_percent`
- `days_cover`
- `average_lead_time_deviation_days`

When a weighted rate is required, use the governed summary table or a saved
report whose numerator and denominator are explicit.

## Controlled Question Bank

Run each question, inspect the generated report information, and confirm the
selected table, aggregation, grouping and filters before saving it.

| Test question | Expected primary table |
| --- | --- |
| Show red and purple inventory risks by outlet | `FACT_CT_Inventory_Risk` |
| Show the synthetic expiry estimate by outlet and item | `FACT_CT_Expiry_Risk` |
| Which ingredients have the largest shortage quantity? | `FACT_CT_Inventory_Risk` |
| Show forecast revenue at risk by menu item | `FACT_CT_Menu_Impact` |
| Show open PO value by vendor and month | `FACT_CT_Purchase_Order` |
| Show ordered, processed and pending procurement value by month | `SUM_CT_Procurement_Funnel` |
| Show vendor fill rate by month | `SUM_CT_Vendor_Scorecard` |
| Show purchase price change percent by item and vendor | `SUM_CT_Price_Movement` |
| Show actual versus theoretical consumption variance by ingredient | `FACT_CT_Consumption_Variance` |
| Show menu items by gross margin percent and sold quantity | `SUM_CT_Menu_Profitability` |
| Show monthly sales, closing stock and open PO value | `SUM_CT_SCM_Monthly` |
| Show data-quality exceptions by type | `FACT_CT_Data_Quality_Exception` |
| Show observed wastage value by outlet | `SUM_CT_Financial_Leakage` |

Reject and retrain any answer that selects a raw, standardized, AUX or legacy
table, sums a rate, or silently removes null/negative operational exceptions.

## Questions Zia Must Not Answer As Production Truth

Do not publish Ask Zia answers for:

- exact or actual expiry quantity/value; Zia may answer only when the question
  explicitly asks for the **synthetic demo estimate**;
- actual ABNAH OTIF or lead-time deviation;
- vendor return rate or vendor-return leakage;
- approved primary or alternate vendors;
- source reorder level or minimum-order quantity;
- multi-outlet geography from current ABNAH actual data.

The synthetic model may demonstrate some formulas, but the current actual
source evidence does not authorize these as production facts.

## Acceptance

Ask Zia is ready only when:

- every controlled question selects an approved table;
- every measure uses the expected aggregation;
- saved answers match the dashboard or truth-pack total under the same filters;
- unavailable KPIs remain unavailable; and
- the workspace administrator signs off the synonym and exclusion settings.

Use the generated report description and Report Information panel to verify the
metric, aggregation, grouping and filters before saving an answer:
https://help.zoho.com/portal/en/kb/analytics/user-guide/ask-zia/articles/using-ask-zia
