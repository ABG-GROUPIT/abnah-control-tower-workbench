# Zoho Dashboard Filter Mapping Matrix

## Product Boundary

Zoho dashboards are the governed build and validation surfaces. The GitHub
Pages control tower does not embed a complete Zoho dashboard UI. Supabase
verifies Zoho access, exports allowlisted Query Table rows, and stores secured
individual-view URLs for selected native visuals and governed drilldowns. The
custom frontend applies the same field-level filter contract to API-backed
surfaces.

A dashboard user filter affects a KPI or report only after that object has been
mapped to a compatible physical field. A report-specific filter affects only
that report. A fixed report filter is part of the business definition and is
not user-toggleable.

## Page 1 - Risk Action Center

Create these dashboard user filters:

1. Date Range
2. Outlet
3. Ingredient Category
4. Action Owner

### Exact Timeline mapping

Do not type these names into a text field. Edit the Timeline Filter, expand
**Timeline Filter Column Mapping**, and select one column per table. Then open
**More > Options > Mapping Timeline Filter** on every object and select the
field shown here:

| Visible object | Source Table | Timeline date |
| --- | --- | --- |
| Restaurants at Risk | Query 27 | `snapshot_date` |
| Menu Items Impacted | Query 28 | `snapshot_date` |
| Stockout Risk (Net Sales) | Query 28 | `snapshot_date` |
| Expiry Risk (Value) | Query 38 | `as_of_date` |
| Open Actions | Query 27 | `snapshot_date` |
| `CT_P1_Outlet_Risk_Map` | Query 27 | `snapshot_date` |
| `CT_P1_Action_Center` | Query 27 | `snapshot_date` |
| `CT_P1_Stockout_Risk_Detail` | Query 27 | `snapshot_date` |
| `CT_P1_Menu_Impact_Detail` | Query 28 | `snapshot_date` |
| `CT_P1_Expiry_Risk_Detail_Demo` | Query 38 | `as_of_date` |
| `CT_P1_Vendor_PO_Risk` | Query 36 | `as_of_date` |

The live dashboard currently maps Query 27 and Query 38 correctly but leaves
the Query 28 stockout widget at the all-period value. The three Query 28
objects must be mapped explicitly.

### Dimension mapping

| Source Table | Outlet | Category | Owner |
| --- | --- | --- | --- |
| Query 27 | `outlet_code` | `category_name` | `action_owner` |
| Query 28 | `outlet_code` | `category_name` | leave unmapped |
| Query 38 | `outlet_code` | `category_name` | `action_owner` |
| Query 36 | `outlet_code` | `category_name` | leave unmapped |

Fixed report conditions:

| Object | Field | Individual Values to include |
| --- | --- | --- |
| Stockout KPIs, map, queue and detail | `risk_type` | `STOCKOUT` |

Query 28 already contains only menu-impact risk rows. Query 36 already contains
open risky PO lines. Query 38 remains explicitly labelled as a synthetic expiry
estimate.

## Page 2 - Procurement, Vendor & Capital Control

Create these dashboard user filters in this order:

1. Date Range
2. Region
3. Outlet
4. Ingredient Category
5. Vendor
6. Raw Material
7. PO Status

Do not add `As-of Source Period` to Page 2. Do not place the Query 23
Raw Material, Vendor or UOM controls in the global filter bar. UOM remains
inside the Ingredient Price Trend report.

### Remove The Exact Existing Duplicate Controls

The reviewed Page 2 filter row currently starts with:

1. `As-of Source Period.`
2. `Raw Material`
3. `Vendor`
4. `UOM`

Delete those four dashboard-wide controls. Keep the later controls and rename:

| Current label | Final label |
| --- | --- |
| `Raw Material Category` | `Ingredient Category` |
| `Vendor Name (Global)` | `Vendor` |
| `Raw Material (Global)` | `Raw Material` |

Turn off **Auto Add User Filters from Reports** so the old Query 23 controls do
not return. Keep `UOM` only as a report-specific control inside
`CT_P2_Ingredient_Price_Trend`.

### Exact Timeline mapping

| Visible object | Source Table | Timeline date |
| --- | --- | --- |
| Ordered Value | Query 29 | `po_date` |
| Open PO | Query 29 | `po_date` |
| Delayed PO | Query 29 | `po_date` |
| Avg Vendor OTIF | Query 24 | `po_date` |
| Items to Price Watch | Query 31 | `price_as_of_date` |
| `CT_P2_Ingredient_Price_Trend` | Query 23 | `receipt_date` |
| `CT_P2_Procurement_Funnel` | Query 29 | `po_date` |
| `CT_P2_Vendor_Scorecard` | Query 30 | `po_date` |
| `CT_P2_Expected_Delivery_Breach` | Query 22 | `po_date` |
| `CT_P2_Pending_By_Vendor` | Query 29 | `po_date` |
| `CT_P2_Top_Price_Movement` | Query 31 | `price_as_of_date` |

### Dimension mapping

Use **Edit Column Mapping** on each merged dashboard filter. Select; do not
type. For Outlet, Category, Vendor and Raw Material, merge the corresponding
columns from Queries 22, 23, 24, 29, 30 and 31. For PO Status, merge only
Queries 22, 24, 29 and 30.

| Visible object | Outlet | Category | Vendor | Raw Material | PO Status |
| --- | --- | --- | --- | --- | --- |
| Ordered Value | Query 29 `outlet_code` | Query 29 `category_name` | Query 29 `vendor_name` | Query 29 `item_code` | Query 29 `po_status` |
| Open PO | Query 29 `outlet_code` | Query 29 `category_name` | Query 29 `vendor_name` | Query 29 `item_code` | Query 29 `po_status` |
| Delayed PO | Query 29 `outlet_code` | Query 29 `category_name` | Query 29 `vendor_name` | Query 29 `item_code` | Query 29 `po_status` |
| Avg Vendor OTIF | Query 24 `outlet_code` | Query 24 `category_name` | Query 24 `vendor_name` | Query 24 `item_code` | Query 24 `po_status` |
| Items to Price Watch | Query 31 `outlet_code` | Query 31 `category_name` | Query 31 `vendor_name` | Query 31 `item_code` | Unmapped |
| Ingredient Price Trend | Query 23 `outlet_code` | Query 23 `category_name` | Query 23 `vendor_name` | Query 23 `item_code` | Unmapped |
| Procurement Funnel | Query 29 `outlet_code` | Query 29 `category_name` | Query 29 `vendor_name` | Query 29 `item_code` | Query 29 `po_status` |
| Vendor Scorecard | Query 30 `outlet_code` | Query 30 `category_name` | Query 30 `vendor_name` | Query 30 `item_code` | Query 30 `po_status` |
| Expected Delivery Breach | Query 22 `outlet_code` | Query 22 `category_name` | Query 22 `vendor_name` | Query 22 `item_code` | Query 22 `po_status` |
| Pending By Vendor | Query 29 `outlet_code` | Query 29 `category_name` | Query 29 `vendor_name` | Query 29 `item_code` | Query 29 `po_status` |
| Top Price Movement | Query 31 `outlet_code` | Query 31 `category_name` | Query 31 `vendor_name` | Query 31 `item_code` | Unmapped |

Fixed/report-only conditions:

| Object | Setting |
| --- | --- |
| Expected Delivery Breach | `delayed_po_flag`: Individual Values, include `1` |
| Ingredient Price Trend | exactly one Raw Material and one UOM |
| Top Price Movement | include `INCREASE`, `DECREASE`, `NO_CHANGE`; exclude `NO_BASELINE` |
| Price Watch KPI | Count Distinct `item_code`; keep `NO_BASELINE` |

The corrected Query 29 and Query 30 retain category, item and status. Therefore
the three PO-value KPI widgets and vendor scorecard must now respond to those
compatible controls.

## Page 3 - Consumption & Menu Profitability

Page 3 still uses the synthetic lineage field `source_period_code`, with
default `month_03`, plus Outlet and Region. Menu filters map only to Queries 18,
25 and 32. Ingredient and UOM filters map only to Queries 19, 20 and 21.

Do not map UOM to currency KPIs. Do not map menu filters to ingredient facts.
Do not map ingredient filters to menu sales facts.

## Page 4 - Explorer & Data Quality

Page 4 current-state objects may use `source_period_code` and Outlet. Historical
trends remain unmapped from the current-period control.

Query 34 includes model-wide exception rows with
`source_period_code = ALL` and `outlet_code = ALL`. Do not map Page 4 period or
outlet controls to Query 34 quality tiles or detail.

## Click Sequence

1. Open the dashboard in **Edit Design**.
2. For Date Range, click **Add User Filters > Include Timeline Filter**.
3. Edit the Timeline Filter and expand **Timeline Filter Column Mapping**.
4. Select one physical date per table; do not type a column name.
5. For every KPI/report, click **More > Options**.
6. Check **Apply Dashboard Filters**.
7. Open **Mapping Timeline Filter** or **Customize** and select the exact
   object-level date from this matrix.
8. For Outlet, Category, Vendor, Raw Material and PO Status, edit the merged
   User Filter and click **Edit Column Mapping**.
9. Leave incompatible reports unmapped.
10. Apply fixed definitions in each report's **Filters** shelf using
   **Individual Values > Include**.
11. Save.
12. Test one filter at a time, then test combinations.

## Acceptance

For Page 1 and Page 2:

- no row may remain visible outside the selected physical Date Range;
- Outlet must affect every applicable KPI and report;
- Category, Vendor and Raw Material must affect every source carrying the
  corresponding field;
- PO Status must affect only PO-aware Queries 22, 24, 29, 30 and 36;
- Price Watch must retain new observations without a prior baseline;
- Top Price Movement must exclude those no-baseline observations;
- no report-specific filter may be visually presented as a global control.

The live Page 2 evidence and exact March values are in
`LIVE_P2_DASHBOARD_AUDIT_2026-07-27.md` and
`PAGE_1_AND_PAGE_2_CORRECTIONS.md`.
