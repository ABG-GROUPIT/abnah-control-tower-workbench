# Zoho Dashboard Filter Click Checklist

Build every report and KPI from `04_DASHBOARD_BUILD.md` first. Use this file
only while adding and mapping filters.

## Create a Dashboard User Filter

1. Open the required `CT_PAGE_...` dashboard.
2. Click **Edit Design**.
3. Click **+ Add User Filters**.
4. Select the table and column written below.
5. Select the written display type.
6. Type the exact label.
7. Select the written default.
8. Click **Apply**.
9. Save the dashboard.

## Map a Dashboard User Filter to an Object

1. Stay in dashboard **Edit Design**.
2. Hover over the KPI, chart, table or Summary View.
3. Click **More**.
4. Click **Options**.
5. Open **Apply Dashboard Filters**.
6. Click **Customize** or **Map Columns**.
7. Tick the dashboard filter.
8. Select the exact destination column.
9. Click **Apply**.
10. Save.

When this checklist says `OFF`, leave that filter unchecked for the object.

# Page 1

Dashboard:

```text
CT_PAGE_1_Risk_Action_Center
```

## Create These Filters

| Order | Label | Source table/column | Display | Default |
| ---: | --- | --- | --- | --- |
| 1 | As-of Source Period | `27_fact_ct_inventory_risk.sql.source_period_code` | Dropdown, single select | `month_03` |
| 2 | Region | Lookup `37_dim_ct_outlet_enriched.sql.region` | Dropdown, multi-select | All |
| 3 | Outlet | `27_fact_ct_inventory_risk.sql.outlet_code` | Dropdown, multi-select | All |
| 4 | Raw Material Category | `27_fact_ct_inventory_risk.sql.category_name` | Dropdown, multi-select | All |
| 5 | Action Owner | `27_fact_ct_inventory_risk.sql.action_owner` | Dropdown, multi-select | All |

Do not create `Risk Type` in Zoho. The custom portal will use it to show or
hide the Stockout, Expiry and Vendor sections after URL handoff.

## Map Page 1 Objects

| Object/source | Period | Region | Outlet | Category | Owner |
| --- | --- | --- | --- | --- | --- |
| Query 27 KPIs and reports | `source_period_code` | lookup `region` | `outlet_code` | `category_name` | `action_owner` |
| Query 28 KPIs and Menu Impact | `source_period_code` | lookup `region` | `outlet_code` | lookup Query 14 `category_name` through `ingredient_code` | OFF |
| Query 38 KPI and Expiry Detail | `source_period_code` | physical `region` | `outlet_code` | `category_name` | `action_owner` |
| Query 36 Vendor/PO Risk | `source_period_code` | lookup `region` | `outlet_code` | `category_name` | OFF |

## Page 1 Fixed Filters

Open each named object in Edit Design, drag the field to **Filters**, choose
**Individual Values > Include**, tick the value, and save.

| Object | Field | Include |
| --- | --- | --- |
| Restaurants at Risk KPI | `risk_type` | `STOCKOUT` |
| Open Actions KPI | `risk_type` | `STOCKOUT` |
| `CT_P1_Outlet_Risk_Map` | `risk_type` | `STOCKOUT` |
| `CT_P1_Action_Center` | `risk_type` | `STOCKOUT` |
| `CT_P1_Stockout_Risk_Detail` | `risk_type` | `STOCKOUT` |

Do not add redundant fixed filters to Queries 28, 36 or 38.

# Page 2

Dashboard:

```text
CT_PAGE_2_Procurement_Vendor_Capital
```

## Create These Filters

| Order | Label | Source table/column | Display | Default |
| ---: | --- | --- | --- | --- |
| 1 | As-of Source Period | `29_sum_ct_procurement_funnel.sql.source_period_code` | Dropdown, single select | `month_03` |
| 2 | Region | Lookup `37_dim_ct_outlet_enriched.sql.region` | Dropdown, multi-select | All |
| 3 | Raw Material Category | `22_fact_ct_purchase_order.sql.category_name` | Dropdown, multi-select | All |
| 4 | Vendor | `24_fact_ct_po_receipt_line.sql.vendor_name` | Dropdown, multi-select | All |
| 5 | PO Status | `22_fact_ct_purchase_order.sql.po_status` | Dropdown, multi-select | All |
| 6 | Raw Material | `22_fact_ct_purchase_order.sql.item_code` | Search dropdown, multi-select | All |
| 7 | Outlet | `22_fact_ct_purchase_order.sql.outlet_code` | Dropdown, multi-select | All |

Keep Outlet in the Zoho validation dashboard. The custom ABNAH Page 2 can hide
it to match the supplied visual.

## Map Page 2 Objects

| Object | Period | Region | Outlet | Category | Vendor | PO Status | Raw Material |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Monthly Purchase KPI | `source_period_code` | lookup `region` | `outlet_code` | OFF | `vendor_name` | OFF | OFF |
| Open PO Exposure KPI | `source_period_code` | lookup `region` | `outlet_code` | OFF | `vendor_name` | OFF | OFF |
| Delayed PO Value KPI | `source_period_code` | lookup `region` | `outlet_code` | OFF | `vendor_name` | OFF | OFF |
| Avg OTIF Summary | `source_period_code` | lookup `region` | `outlet_code` | `category_name` | `vendor_name` | `po_status` | `item_code` |
| Price Watch KPI | `source_period_code` | lookup `region` | `outlet_code` | lookup `category_name` | `vendor_name` | OFF | `item_code` |
| Procurement Funnel | `source_period_code` | lookup `region` | `outlet_code` | OFF | `vendor_name` | OFF | OFF |
| Vendor Scorecard | `source_period_code` | lookup `region` | `outlet_code` | `category_name` | `vendor_name` | `po_status` | `item_code` |
| Raw Material Price Trend | OFF | lookup `region` | `outlet_code` | `category_name` | `vendor_name` | OFF | `item_code` |
| Top Price Movement | `source_period_code` | lookup `region` | `outlet_code` | lookup `category_name` | `vendor_name` | OFF | `item_code` |
| Pending by Vendor | `source_period_code` | lookup `region` | `outlet_code` | `category_name` | `vendor_name` | `po_status` | `item_code` |
| Expected Delivery Breach | `source_period_code` | lookup `region` | `outlet_code` | `category_name` | `vendor_name` | `po_status` | `item_code` |

The Query 29 KPI Widgets cannot respond to Category, PO Status or Raw
Material. Leave those mappings off.

## Page 2 Fixed Filters

| Object | Field | Include |
| --- | --- | --- |
| Pending by Vendor | `is_open_po` | `1` |
| Expected Delivery Breach | `delayed_po_flag` | `1` |

Do not use `Open` or `Delayed` as `po_status` values. The actual current status
values are:

```text
Pending
Partially Received
Closed
Cancelled
```

# Page 3

Dashboard:

```text
CT_PAGE_3_Consumption_Menu_Profitability
```

## Create These Filters

| Order | Label | Source table/column | Display | Default |
| ---: | --- | --- | --- | --- |
| 1 | As-of Source Period | `25_fact_ct_menu_profitability.sql.source_period_code` | Dropdown, single select | `month_03` |
| 2 | Region | Lookup `37_dim_ct_outlet_enriched.sql.region` | Dropdown, multi-select | All |
| 3 | Outlet | `25_fact_ct_menu_profitability.sql.outlet_code` | Dropdown, multi-select | All |
| 4 | Menu Super Category | `25_fact_ct_menu_profitability.sql.super_category_name` | Dropdown, multi-select | All |
| 5 | Menu Category | `25_fact_ct_menu_profitability.sql.category_name` | Dropdown, multi-select | All |
| 6 | Menu Item | `25_fact_ct_menu_profitability.sql.menu_item_code` | Search dropdown, multi-select | All |
| 7 | Raw Material | `21_fact_ct_consumption_variance.sql.item_code` | Search dropdown, multi-select | All |
| 8 | UOM | `21_fact_ct_consumption_variance.sql.canonical_uom` | Dropdown, single select | Select one for quantity views |

## Map Page 3 Menu Objects

Map these five filters:

- As-of Source Period -> `source_period_code`
- Region -> lookup `region`
- Outlet -> `outlet_code`
- Menu Super Category -> `super_category_name`
- Menu Category -> `category_name`
- Menu Item -> `menu_item_code`

Apply them to:

- Net Sales KPI
- Theoretical COGS KPI
- Gross Margin Summary
- Menu Items KPI
- `CT_P3_Menu_BCG`
- `CT_P3_Outlet_Item_Heatmap`

For every menu object, leave Raw Material and UOM off.

## Map Page 3 Ingredient Objects

| Object | Period | Region | Outlet | Raw Material | UOM |
| --- | --- | --- | --- | --- | --- |
| Consumption Leakage KPI | `source_period_code` | lookup `region` | `outlet_code` | `item_code` | OFF |
| Consumption Bridge | `source_period_code` | lookup `region` | `outlet_code` | `item_code` | `canonical_uom` |
| Consumption Variance | `source_period_code` | lookup `region` | `outlet_code` | `item_code` | OFF for currency view |

For every ingredient object, leave Menu Super Category, Menu Category and Menu
Item off.

No reference-required Page 3 object needs an additional fixed filter.

# Page 4

Dashboard:

```text
CT_PAGE_4_SCM_Explorer_Data_Quality
```

## Create These Filters

| Order | Label | Source table/column | Display | Default |
| ---: | --- | --- | --- | --- |
| 1 | Current Period | `33_sum_ct_scm_monthly.sql.source_period_code` | Dropdown, single select | `month_03` |
| 2 | Region | Lookup `37_dim_ct_outlet_enriched.sql.region` | Dropdown, multi-select | All |
| 3 | Outlet | `33_sum_ct_scm_monthly.sql.outlet_code` | Dropdown, multi-select | All |
| 4 | Raw Material Category | `21_fact_ct_consumption_variance.sql.category_name` | Dropdown, multi-select | All |
| 5 | Exception Type | `34_fact_ct_data_quality_exception.sql.exception_type` | Dropdown, multi-select | All |

## Map Page 4 Objects

| Object | Period | Region | Outlet | Category | Exception |
| --- | --- | --- | --- | --- | --- |
| Closing Stock KPI | `source_period_code` | lookup `region` | `outlet_code` | OFF | OFF |
| Open PO KPI | `source_period_code` | lookup `region` | `outlet_code` | OFF | OFF |
| Monthly Sales KPI | `source_period_code` | lookup `region` | `outlet_code` | OFF | OFF |
| Actual Consumption KPI | `source_period_code` | lookup `region` | `outlet_code` | OFF | OFF |
| Variance Value KPI | `source_period_code` | lookup `region` | `outlet_code` | `category_name` | OFF |
| Month-End SCM Trend | OFF | lookup `region` | `outlet_code` | OFF | OFF |
| Six Query 34 tiles | OFF | OFF | OFF | OFF | OFF |
| Data Quality Detail | OFF | OFF | OFF | OFF | `exception_type` |
| SCM Descriptive Explorer | `source_period_code` | lookup `region` | `outlet_code` | OFF | OFF |

## Page 4 Fixed Filters

Every tile uses:

- Table: `34_fact_ct_data_quality_exception.sql`
- Data Column: `exception_count`
- Calculation: Sum
- Group By: blank
- Filter field: `exception_type`
- Filter mode: **Individual Values > Include**

| Tile | Include |
| --- | --- |
| Negative Stock Rows | `NEGATIVE_STOCK` |
| Zero Stock With Demand | `ZERO_STOCK_WITH_DEMAND` |
| Sold Items Missing Recipe | `SOLD_ITEM_MISSING_RECIPE` |
| Items Missing Master | `OPERATIONAL_ITEM_MISSING_MASTER` |
| UOM Mismatch | `UOM_MISMATCH_WITHOUT_CONVERSION` |
| Open PO Missing Expected Delivery | `OPEN_PO_MISSING_EXPECTED_DELIVERY` |

# Final Filter Test

For each dashboard:

1. Set the period to `month_03`.
2. Set all other filters to **All**.
3. Record the KPI values.
4. Select `OUT001`.
5. Confirm every object mapped to Outlet changes.
6. Select `OUT002`.
7. Repeat.
8. Select `OUT003`.
9. Repeat.
10. Reset Outlet to **All**.
11. Confirm Price Trend and Page 4 Month-End Trend still show all three
    periods.
12. Confirm Query 34 tiles do not change when Period or Outlet changes.
13. Save.
