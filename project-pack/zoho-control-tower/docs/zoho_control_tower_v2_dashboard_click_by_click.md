# ABNAH Zoho Dashboard Click-By-Click Build Manual

This is the working manual to keep open while building in Zoho Analytics.
It contains execution steps, not data-model theory.

Build the four dashboards in this order:

1. `CT_PAGE_1_Risk_Action_Center`
2. `CT_PAGE_2_Procurement_Vendor_Capital`
3. `CT_PAGE_3_Consumption_Menu_Profitability`
4. `CT_PAGE_4_SCM_Explorer_Data_Quality`

Use **consumption**, not **yield**, on Page 3.

## Before Clicking Anything

1. Confirm Query Tables `01` through `38` have been saved successfully.
2. Confirm the lookup relationships in
   `03A_LOOKUPS_FORMULAS_AND_PRE_DASHBOARD_SETUP.md` are complete.
3. Keep all Aggregate Formulas already created. Do not delete them.
4. Confirm these four Aggregate Formulas exist:

| Query Table | Aggregate Formula |
| --- | --- |
| `23_fact_ct_purchase_receipt.sql` | `Weighted Unit Price` |
| `24_fact_ct_po_receipt_line.sql` | `PO Fill Rate %` |
| `24_fact_ct_po_receipt_line.sql` | `Vendor OTIF %` |
| `25_fact_ct_menu_profitability.sql` | `Menu Gross Margin %` |

5. Build the saved reports first.
6. Create the dashboard after its saved reports are ready.
7. Create KPI Widgets inside the dashboard.
8. Add Dashboard User Filters last.
9. Validate the default results before changing colors or sharing URLs.

## KPI Click Register

Use this register to check the selections in each KPI editor. The detailed
clicks appear in the page sections below.

| Page | KPI label | Source table | Data Column / value | Calculation | Fixed filter | Expected default |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Restaurants at Risk | `27_fact_ct_inventory_risk.sql` | `outlet_code` | Count Distinct | `risk_type`: Include `STOCKOUT` | `3` |
| 1 | Menu Items Impacted | `28_fact_ct_menu_impact.sql` | `menu_item_code` | Count Distinct | None | `110` |
| 1 | Stockout Risk | `28_fact_ct_menu_impact.sql` | `allocated_forecast_net_sales_at_risk` | Sum | None | `INR 411,695.55` |
| 1 | Expiry Risk | `38_fact_ct_expiry_risk.sql` | `expiry_risk_value` | Sum | None | `INR 271,399.12` |
| 1 | Open Actions | `27_fact_ct_inventory_risk.sql` | `action_id` | Count Distinct | `risk_type`: Include `STOCKOUT` | `6` |
| 2 | Monthly Purchase | `29_sum_ct_procurement_funnel.sql` | `ordered_value` | Sum | None | `INR 1,565,981.32` |
| 2 | Open PO Exposure | `29_sum_ct_procurement_funnel.sql` | `pending_value` | Sum | None | `INR 177,145.39` |
| 2 | Delayed PO Value | `29_sum_ct_procurement_funnel.sql` | `delayed_value` | Sum | None | `INR 156,529.82` |
| 2 | Avg OTIF | `24_fact_ct_po_receipt_line.sql` | Aggregate Formula `Vendor OTIF %` | Saved Summary View | None | `53.70%` |
| 2 | Price Watch | `31_sum_ct_price_movement.sql` | `item_code` | Count Distinct | None | `42` |
| 3 | Net Sales | `25_fact_ct_menu_profitability.sql` | `net_sales` | Sum | None | `INR 2,192,475.48` |
| 3 | Theoretical COGS | `25_fact_ct_menu_profitability.sql` | `theoretical_cogs` | Sum | None | `INR 393,664.46` |
| 3 | Gross Margin | `25_fact_ct_menu_profitability.sql` | Aggregate Formula `Menu Gross Margin %` | Saved Summary View | None | `82.04%` |
| 3 | Menu Items | `25_fact_ct_menu_profitability.sql` | `menu_item_code` | Count Distinct | None | `110` |
| 3 | Consumption Leakage | `21_fact_ct_consumption_variance.sql` | `leakage_value` | Sum | None | `INR 38,632.37` |
| 4 | Closing Stock Value | `33_sum_ct_scm_monthly.sql` | `closing_stock_value` | Sum | None | `INR 3,344,237.44` |
| 4 | Open PO Snapshot | `33_sum_ct_scm_monthly.sql` | `open_po_value` | Sum | None | `INR 177,145.39` |
| 4 | Monthly Sales | `33_sum_ct_scm_monthly.sql` | `net_sales` | Sum | None | `INR 2,192,475.48` |
| 4 | Actual Consumption | `33_sum_ct_scm_monthly.sql` | `actual_consumption_value` | Sum | None | `INR 377,620.25` |
| 4 | Variance Value | `21_fact_ct_consumption_variance.sql` | `signed_consumption_variance_value` | Sum | None | `INR -22,106.87` |

For direct KPI Widgets, select the physical Data Column and Calculation shown
above. For `Vendor OTIF %` and `Menu Gross Margin %`, create the one-value
**Summary View** described below. Do not try to find an Aggregate Formula in
the direct KPI Widget's Data Column selector.

Keep `PO Fill Rate %` for the Page 2 Vendor Scorecard values. It is not one of
the five Page 2 header cards.

## Exact Fixed-Filter Click Sequence

Use these steps whenever this manual says **add a fixed filter**:

1. Open the saved report in **Edit Design**.
2. Find the field named in the instruction.
3. Drag that field to the **Filters** shelf.
4. Choose **Individual Values**.
5. Choose **Include**.
6. Tick only the exact value named in the instruction.
7. Click **Apply**.
8. Click **Save**.

Do not type SQL operators such as `<>`, `IN`, or `=` into the Zoho report
interface.

Use these exact fixed-filter selections:

| Object | Filter shelf selection |
| --- | --- |
| Restaurants at Risk KPI | `risk_type`: Individual Values, Include `STOCKOUT` |
| Open Actions KPI | `risk_type`: Individual Values, Include `STOCKOUT` |
| `CT_P1_Outlet_Risk_Map` | `risk_type`: Individual Values, Include `STOCKOUT` |
| `CT_P1_Action_Center` | `risk_type`: Individual Values, Include `STOCKOUT` |
| `CT_P1_Stockout_Risk_Detail` | `risk_type`: Individual Values, Include `STOCKOUT` |
| `CT_P2_Pending_By_Vendor` | `is_open_po`: Individual Values, Include `1` |
| `CT_P2_Expected_Delivery_Breach` | `delayed_po_flag`: Individual Values, Include `1` |
| Negative Stock Rows tile | `exception_type`: Individual Values, Include `NEGATIVE_STOCK` |
| Zero Stock With Demand tile | `exception_type`: Individual Values, Include `ZERO_STOCK_WITH_DEMAND` |
| Sold Items Missing Recipe tile | `exception_type`: Individual Values, Include `SOLD_ITEM_MISSING_RECIPE` |
| Items Missing Master tile | `exception_type`: Individual Values, Include `OPERATIONAL_ITEM_MISSING_MASTER` |
| UOM Mismatch tile | `exception_type`: Individual Values, Include `UOM_MISMATCH_WITHOUT_CONVERSION` |
| Open PO Missing Expected Delivery tile | `exception_type`: Individual Values, Include `OPEN_PO_MISSING_EXPECTED_DELIVERY` |

## Exact Dashboard-Filter Mapping Click Sequence

Use these steps for every report or KPI named in a mapping table:

1. Open the dashboard in **Edit Design**.
2. Hover over the report or KPI.
3. Click **More** or the three-dot menu.
4. Click **Options**.
5. Open **Apply Dashboard Filters**.
6. Click **Customize** or **Map Columns**.
7. Select the dashboard filter.
8. Select the exact report column written in the mapping table.
9. Click **Apply**.
10. Save the dashboard.

If the mapping table says `Do not map`, leave that dashboard filter unchecked
for that object.

# Page 1 - Risk Action Center

Build these reference-required saved reports:

1. `CT_P1_Outlet_Risk_Map`
2. `CT_P1_Action_Center`
3. `CT_P1_Stockout_Risk_Detail`
4. `CT_P1_Menu_Impact_Detail`
5. `CT_P1_Expiry_Risk_Detail_Demo`
6. `CT_P1_Vendor_PO_Risk`

## P1-R01 - Outlet Risk Map

1. Click **+ New**.
2. Click **New Report**.
3. Choose **Chart View**.
4. Select source table `27_fact_ct_inventory_risk.sql`.
5. Choose the **Map** chart type.
6. For the outlet/location field, select `outlet_name`.
7. For latitude, select the lookup field
   `37_dim_ct_outlet_enriched.sql.latitude`.
8. For longitude, select the lookup field
   `37_dim_ct_outlet_enriched.sql.longitude`.
9. For color, select `risk_severity_rank`.
10. Set the aggregation of `risk_severity_rank` to **Max**.
11. Add these tooltip fields:
    - `outlet_name`
    - `item_code` with **Count Distinct**
    - `shortage_cost_value` with **Sum**
    - `days_cover` with **Min**
    - `risk_severity` with **Actual**
12. Add the fixed filter:
    - field `risk_type`
    - Include `STOCKOUT`
13. Open chart **Settings**.
14. Enable **View Underlying Data**.
15. Enable **Use as Filter**.
16. Set severity colors:
    - `PURPLE` -> `#6C3B8C`
    - `RED` -> `#C63D3D`
    - `AMBER` -> `#D49A22`
    - `GREEN` -> `#2E7D5B`
17. Click **Save As**.
18. Save as `CT_P1_Outlet_Risk_Map`.

If Zoho does not expose the lookup latitude and longitude fields, stop and
repair the `outlet_code` lookup to `37_dim_ct_outlet_enriched.sql`. Do not
manually type coordinates into the chart.

## P1-R02 - Priority Action Queue

1. Click **+ New**.
2. Click **New Report**.
3. Choose **Tabular View**.
4. Select source table `27_fact_ct_inventory_risk.sql`.
5. Add columns in this exact order:
    - `action_id`
    - `outlet_name`
    - `item_name`
    - `risk_severity`
    - `shortage_qty`
    - `shortage_cost_value`
    - `recommended_action`
    - `action_owner`
    - `due_band`
6. Add `risk_severity_rank` as a hidden sort column.
7. Sort `risk_severity_rank` **Descending**.
8. Add secondary sort `shortage_cost_value` **Descending**.
9. Add the fixed filter:
    - field `risk_type`
    - Include `STOCKOUT`
10. Set `shortage_cost_value` to **Currency / INR / 2 decimals**.
11. Set `shortage_qty` to **Number / 2 decimals**.
12. Apply conditional formatting to `risk_severity`:
    - `PURPLE` -> background `#6C3B8C`, white text
    - `RED` -> background `#C63D3D`, white text
    - `AMBER` -> background `#D49A22`, dark text
    - `GREEN` -> background `#2E7D5B`, white text
13. Enable **View Underlying Data**.
14. Click **Save As**.
15. Save as `CT_P1_Action_Center`.

## P1-R03 - Stockout Risk

1. Click **+ New**.
2. Click **New Report**.
3. Choose **Tabular View**.
4. Select source table `27_fact_ct_inventory_risk.sql`.
5. Add columns in this exact order:
    - `outlet_name`
    - `item_code`
    - `item_name`
    - `category_name`
    - `canonical_uom`
    - `current_stock_qty`
    - `forecast_required_qty`
    - `required_qty_with_safety`
    - `valid_open_po_qty`
    - `shortage_qty`
    - `days_cover`
    - `shortage_cost_value`
    - `risk_severity`
6. Sort `risk_severity_rank` **Descending**.
7. Add secondary sort `shortage_cost_value` **Descending**.
8. Add the fixed filter:
    - field `risk_type`
    - Include `STOCKOUT`
9. Set `shortage_cost_value` to **Currency / INR / 2 decimals**.
10. Set quantity fields to **Number / 2 decimals**.
11. Set `days_cover` to **Number / 1 decimal**.
12. Apply the Page 1 severity colors to `risk_severity`.
13. Enable **View Underlying Data**.
14. Click **Save As**.
15. Save as `CT_P1_Stockout_Risk_Detail`.

## P1-R04 - Menu Impact

1. Click **+ New**.
2. Click **New Report**.
3. Choose **Tabular View**.
4. Select source table `28_fact_ct_menu_impact.sql`.
5. Add columns in this exact order:
    - `outlet_name`
    - `ingredient_code`
    - `ingredient_name`
    - `risk_severity`
    - `shortage_qty`
    - `menu_item_code`
    - `menu_item_name`
    - `forecast_menu_qty`
    - `risk_ingredient_count`
    - `allocated_forecast_net_sales_at_risk`
6. Sort `risk_severity` in the order `PURPLE`, `RED`, `AMBER`, `GREEN`.
7. Add secondary sort `allocated_forecast_net_sales_at_risk`
   **Descending**.
8. Do not add a fixed risk filter. Query 28 already contains impact rows.
9. Set `allocated_forecast_net_sales_at_risk` to
   **Currency / INR / 2 decimals**.
10. Apply the Page 1 severity colors to `risk_severity`.
11. Enable **View Underlying Data**.
12. Click **Save As**.
13. Save as `CT_P1_Menu_Impact_Detail`.

## P1-R05 - Expiry Risk Demo

1. Click **+ New**.
2. Click **New Report**.
3. Choose **Tabular View**.
4. Select source table `38_fact_ct_expiry_risk.sql`.
5. Add columns in this exact order:
    - `outlet_name`
    - `item_code`
    - `item_name`
    - `category_name`
    - `batch_number`
    - `receipt_date`
    - `grn_number`
    - `po_number`
    - `vendor_name`
    - `receipt_source_status`
    - `canonical_uom`
    - `item_closing_qty`
    - `estimated_fifo_tranche_qty`
    - `expected_consumption_before_expiry`
    - `expiry_qty_at_risk`
    - `expiry_risk_value`
    - `estimated_expiry_date`
    - `days_to_expiry`
    - `expiry_batch_risk_status`
    - `risk_severity`
    - `estimation_method`
    - `production_use_status`
6. Sort `risk_severity_rank` **Descending**.
7. Add secondary sort `expiry_risk_value` **Descending**.
8. Set `expiry_risk_value` to **Currency / INR / 2 decimals**.
9. Apply the Page 1 severity colors to `risk_severity`.
10. Open report description or subtitle settings.
11. Enter:

```text
Synthetic demo estimate - no enabled POSIST batch/expiry source
```

12. Enable **View Underlying Data**.
13. Click **Save As**.
14. Save as `CT_P1_Expiry_Risk_Detail_Demo`.

## P1-R06 - Vendor / PO Mitigation

1. Click **+ New**.
2. Click **New Report**.
3. Choose **Tabular View**.
4. Select source table `36_fact_ct_risky_po.sql`.
5. Add columns in this exact order:
    - `po_number`
    - `outlet_name`
    - `vendor_name`
    - `item_code`
    - `item_name`
    - `category_name`
    - `po_status`
    - `expected_delivery_date`
    - `remaining_qty`
    - `canonical_uom`
    - `open_po_value`
    - `risk_severity`
6. Sort `risk_severity` in the order `PURPLE`, `RED`, `AMBER`.
7. Add secondary sort `open_po_value` **Descending**.
8. Do not add an open-PO filter. Query 36 already contains only open,
   non-green risk-linked PO rows.
9. Set `open_po_value` to **Currency / INR / 2 decimals**.
10. Apply the Page 1 severity colors.
11. Enable **View Underlying Data**.
12. Click **Save As**.
13. Save as `CT_P1_Vendor_PO_Risk`.

An empty default result is valid for this synthetic checkpoint. Do not replace
an empty result with invented rows.

## P1-D01 - Create the Dashboard

1. Click **+ New**.
2. Choose **Dashboard**.
3. Name it `CT_PAGE_1_Risk_Action_Center`.
4. Click **Create**.
5. Click **Edit Design**.
6. Add a heading text widget:

```text
Risk Action Center
Outlet risk, stockout, expiry demonstration and owned mitigation
```

7. Add the six saved reports from the Page 1 list.
8. Arrange:
    - Row 1: five KPI Widgets
    - Row 2: `CT_P1_Outlet_Risk_Map` on the left and
      `CT_P1_Action_Center` on the right
    - Row 3: `CT_P1_Stockout_Risk_Detail` and
      `CT_P1_Menu_Impact_Detail`
    - Row 4: `CT_P1_Expiry_Risk_Detail_Demo` and
      `CT_P1_Vendor_PO_Risk`
9. Save the dashboard.

## P1-K01 - Restaurants at Risk

1. Open `CT_PAGE_1_Risk_Action_Center` in **Edit Design**.
2. Click **Widget**.
3. Choose **KPI Widget**.
4. Choose **Single Label**.
5. Open the **Data** tab.
6. Select table `27_fact_ct_inventory_risk.sql`.
7. Select Data Column `outlet_code`.
8. Select Calculation **Count Distinct**.
9. Leave **Group By** blank.
10. Open the widget **Filters** tab.
11. Add field `risk_type`.
12. Choose **Individual Values > Include > STOCKOUT**.
13. Open **Settings > Primary Value**.
14. Set label to `Restaurants at Risk`.
15. Set format to **Whole Number**.
16. Leave secondary value and target blank.
17. Click **Apply**.
18. Expected result at `month_03`, all outlets: `3`.

## P1-K02 - Menu Items Impacted

1. Add another **KPI Widget > Single Label**.
2. Select table `28_fact_ct_menu_impact.sql`.
3. Select Data Column `menu_item_code`.
4. Select Calculation **Count Distinct**.
5. Leave **Group By** blank.
6. Add no fixed filter.
7. Set label to `Menu Items Impacted`.
8. Set format to **Whole Number**.
9. Click **Apply**.
10. Expected result: `110`.

## P1-K03 - Stockout Risk

1. Add another **KPI Widget > Single Label**.
2. Select table `28_fact_ct_menu_impact.sql`.
3. Select Data Column `allocated_forecast_net_sales_at_risk`.
4. Select Calculation **Sum**.
5. Leave **Group By** blank.
6. Add no fixed filter.
7. Set label to `Stockout Risk`.
8. Set subtitle to `Forecast sales at risk - next 7 days`.
9. Set format to **Currency / INR / 2 decimals**.
10. Click **Apply**.
11. Expected result: `INR 411,695.55`.

## P1-K04 - Expiry Risk

1. Add another **KPI Widget > Single Label**.
2. Select table `38_fact_ct_expiry_risk.sql`.
3. Select Data Column `expiry_risk_value`.
4. Select Calculation **Sum**.
5. Leave **Group By** blank.
6. Set label to `Expiry Risk`.
7. Set subtitle to:

```text
Synthetic demo estimate - no enabled POSIST batch/expiry source
```

8. Set format to **Currency / INR / 2 decimals**.
9. Click **Apply**.
10. Expected result: `INR 271,399.12`.

## P1-K05 - Open Actions

1. Add another **KPI Widget > Single Label**.
2. Select table `27_fact_ct_inventory_risk.sql`.
3. Select Data Column `action_id`.
4. Select Calculation **Count Distinct**.
5. Leave **Group By** blank.
6. Add widget fixed filter:
    - `risk_type`
    - **Individual Values > Include > STOCKOUT**
7. Set label to `Open Actions`.
8. Set format to **Whole Number**.
9. Click **Apply**.
10. Expected result: `6`.

## P1-F01 - Create Dashboard User Filters

Create these filters in this exact order.

### As-of Source Period

1. Open the dashboard in **Edit Design**.
2. Click **+ Add User Filters**.
3. Select table `27_fact_ct_inventory_risk.sql`.
4. Select column `source_period_code`.
5. Choose **Dropdown**.
6. Choose **Single Select**.
7. Set label to `As-of Source Period`.
8. Set default to `month_03`.
9. Click **Apply**.

### Region

1. Click **+ Add User Filters**.
2. Select the lookup column
   `37_dim_ct_outlet_enriched.sql.region`.
3. Choose **Dropdown**.
4. Choose **Multi Select**.
5. Set label to `Region`.
6. Set default to **All**.
7. Click **Apply**.

### Outlet

1. Click **+ Add User Filters**.
2. Select table `27_fact_ct_inventory_risk.sql`.
3. Select column `outlet_code`.
4. Choose **Dropdown**.
5. Choose **Multi Select**.
6. Set label to `Outlet`.
7. Set default to **All**.
8. Click **Apply**.

### Raw Material Category

1. Click **+ Add User Filters**.
2. Select table `27_fact_ct_inventory_risk.sql`.
3. Select column `category_name`.
4. Choose **Dropdown**.
5. Choose **Multi Select**.
6. Set label to `Raw Material Category`.
7. Set default to **All**.
8. Click **Apply**.

### Action Owner

1. Click **+ Add User Filters**.
2. Select table `27_fact_ct_inventory_risk.sql`.
3. Select column `action_owner`.
4. Choose **Dropdown**.
5. Choose **Multi Select**.
6. Set label to `Action Owner`.
7. Set default to **All**.
8. Click **Apply**.

Do not create the ABNAH `Risk Type` control in the native Zoho dashboard.
Stockout, expiry and vendor/PO panels come from different source tables. The
custom portal will implement this control as a section toggle after the URLs
are handed over.

## P1-F02 - Map the Dashboard Filters

Repeat the dashboard-filter mapping click sequence for each row.

| Object | Period | Outlet | Region | Raw Material Category | Action Owner |
| --- | --- | --- | --- | --- | --- |
| Both Query 27 KPI Widgets | `source_period_code` | `outlet_code` | lookup `region` | `category_name` | `action_owner` |
| `CT_P1_Outlet_Risk_Map` | `source_period_code` | `outlet_code` | lookup `region` | `category_name` | `action_owner` |
| `CT_P1_Action_Center` | `source_period_code` | `outlet_code` | lookup `region` | `category_name` | `action_owner` |
| `CT_P1_Stockout_Risk_Detail` | `source_period_code` | `outlet_code` | lookup `region` | `category_name` | `action_owner` |
| Menu Items Impacted KPI | `source_period_code` | `outlet_code` | lookup `region` | lookup `14_dim_ct_item.sql.category_name` through `ingredient_code` | Do not map |
| Stockout Risk KPI | `source_period_code` | `outlet_code` | lookup `region` | lookup `14_dim_ct_item.sql.category_name` through `ingredient_code` | Do not map |
| `CT_P1_Menu_Impact_Detail` | `source_period_code` | `outlet_code` | lookup `region` | lookup `14_dim_ct_item.sql.category_name` through `ingredient_code` | Do not map |
| Expiry Risk KPI | `source_period_code` | `outlet_code` | physical `region` | `category_name` | `action_owner` |
| `CT_P1_Expiry_Risk_Detail_Demo` | `source_period_code` | `outlet_code` | physical `region` | `category_name` | `action_owner` |
| `CT_P1_Vendor_PO_Risk` | `source_period_code` | `outlet_code` | lookup `region` | `category_name` | Do not map |

## P1 Validation

1. Set `As-of Source Period` to `month_03`.
2. Set Outlet to **All**.
3. Confirm KPI values: `3`, `110`, `INR 411,695.55`,
   `INR 271,399.12`, `6`.
4. Confirm `CT_P1_Action_Center` has `6` rows.
5. Confirm `CT_P1_Menu_Impact_Detail` has `302` rows.
6. Confirm the expiry detail has `68` demo rows.
7. Select `OUT001`, `OUT002`, and `OUT003` separately.
8. Confirm every compatible KPI and report changes.
9. Reset Outlet to **All**.
10. Save the dashboard.

# Page 2 - Procurement, Vendor & Capital Control

Build these reference-required saved reports:

1. `CT_P2_Procurement_Funnel`
2. `CT_P2_Vendor_Scorecard`
3. `CT_P2_Ingredient_Price_Trend`
4. `CT_P2_Top_Price_Movement`
5. `CT_P2_Pending_By_Vendor`
6. `CT_P2_Expected_Delivery_Breach`

## P2-R01 - Procurement Funnel

1. Click **+ New**.
2. Click **New Report**.
3. Choose **Chart View**.
4. Select source table `29_sum_ct_procurement_funnel.sql`.
5. Choose **Horizontal Bar > Clustered**. Do not choose the native Funnel
   chart because it accepts one value field and this object requires four.
6. Drag `source_period_code` to the Y-axis/category shelf.
7. Add these X-axis value fields:
    - `ordered_value` with **Sum**
    - `processed_value` with **Sum**
    - `pending_value` with **Sum**
    - `delayed_value` with **Sum**
8. Rename the displayed measures:
    - Ordered
    - Processed
    - Pending
    - Delayed
9. Set all four measures to **Currency / INR / 2 decimals**.
10. Use colors:
    - Ordered `#4164D9`
    - Processed `#2E7D5B`
    - Pending `#D49A22`
    - Delayed `#C63D3D`
11. Click **Save As**.
12. Save as `CT_P2_Procurement_Funnel`.

Do not create another Query Table just to force a funnel shape.

## P2-R02 - Vendor Risk Scorecard

1. Click **+ New**.
2. Click **New Report**.
3. Choose **Pivot View**.
4. Select source table `24_fact_ct_po_receipt_line.sql`.
5. Drag `vendor_name` to **Rows**.
6. Add these values:
    - `gross_order_value` with **Sum**
    - `open_po_value` with **Sum**
    - Aggregate Formula `Vendor OTIF %`
    - Aggregate Formula `PO Fill Rate %`
    - `eligible_lead_time_deviation_days` with **Average**
    - `delayed_po_flag` with **Sum**
7. Rename displayed values:
    - Monthly Purchase
    - Open PO Exposure
    - OTIF %
    - Fill Rate %
    - Avg Lead Deviation Days
    - Delayed Lines
8. Set purchase and exposure to **Currency / INR / 2 decimals**.
9. Set OTIF and Fill Rate to **Percentage / 2 decimals**.
10. Set lead deviation to **Number / 1 decimal**.
11. Sort `open_po_value` **Descending**.
12. Apply conditional formatting:
    - OTIF below `60` -> red
    - OTIF from `60` to below `80` -> amber
    - OTIF `80` or above -> green
13. Add report subtitle:

```text
Formula demonstration until deterministic PO-to-GRN linkage is approved
```

14. Enable **View Underlying Data**.
15. Click **Save As**.
16. Save as `CT_P2_Vendor_Scorecard`.

## P2-R03 - Raw Material Price Trend

1. Click **+ New**.
2. Click **New Report**.
3. Choose **Chart View**.
4. Select source table `23_fact_ct_purchase_receipt.sql`.
5. Choose **Line Chart**.
6. Drag `source_period_code` to the X-axis.
7. Drag Aggregate Formula `Weighted Unit Price` to the Y-axis.
8. Drag `vendor_name` to **Color/Series**.
9. Sort `source_period_code` **Ascending**.
10. Set the Y-axis format to **Currency / INR / 2 decimals**.
11. Add a report User Filter:
    - field `item_code`
    - dropdown
    - single select
    - label `Raw Material`
12. Add a second report User Filter:
    - field `vendor_name`
    - dropdown
    - multi-select
    - label `Vendor`
13. Add a third report User Filter:
    - field `canonical_uom`
    - dropdown
    - single select
    - label `UOM`
14. Click **Save As**.
15. Save as `CT_P2_Ingredient_Price_Trend`.

The dashboard As-of Source Period filter must not be mapped to this chart. The
chart must keep all three periods.

## P2-R04 - Top Price Movement

1. Click **+ New**.
2. Click **New Report**.
3. Choose **Chart View**.
4. Select source table `31_sum_ct_price_movement.sql`.
5. Choose **Horizontal Bar**.
6. Drag `price_comparison_key` to the Y-axis.
7. Drag `unit_price_change_percent` to the X-axis.
8. Set aggregation to **Max**.
9. Drag `price_movement_direction` to **Color/Series**.
10. Sort by `absolute_unit_price_change_percent` **Descending**.
11. Set **Top/Bottom N** to **Top 10**.
12. Set number format to **Percentage / 2 decimals**.
13. Set colors:
    - `INCREASE` -> `#C63D3D`
    - `DECREASE` -> `#2E7D5B`
    - `NO_CHANGE` -> `#7C8793`
14. Enable **Use as Filter**.
15. Click **Save As**.
16. Save as `CT_P2_Top_Price_Movement`.

## P2-R05 - Pending by Vendor

1. Click **+ New**.
2. Click **New Report**.
3. Choose **Tabular View**.
4. Select source table `22_fact_ct_purchase_order.sql`.
5. Add columns in this exact order:
    - `vendor_name`
    - `item_code`
    - `item_name`
    - `category_name`
    - `remaining_qty`
    - `canonical_uom`
    - `open_po_value`
    - `expected_delivery_date`
    - `po_number`
    - `po_status`
6. Add the fixed filter:
    - field `is_open_po`
    - Include `1`
7. Sort `open_po_value` **Descending**.
8. Set `open_po_value` to **Currency / INR / 2 decimals**.
9. Set `remaining_qty` to **Number / 2 decimals**.
10. Enable **View Underlying Data**.
11. Click **Save As**.
12. Save as `CT_P2_Pending_By_Vendor`.

## P2-R06 - Expected Delivery Breach

1. Click **+ New**.
2. Click **New Report**.
3. Choose **Tabular View**.
4. Select source table `22_fact_ct_purchase_order.sql`.
5. Add columns in this exact order:
    - `po_number`
    - `vendor_name`
    - `outlet_name`
    - `item_code`
    - `item_name`
    - `remaining_qty`
    - `canonical_uom`
    - `open_po_value`
    - `expected_delivery_date`
    - `as_of_date`
    - `po_status`
6. Add the fixed filter:
    - field `delayed_po_flag`
    - Include `1`
7. Sort `expected_delivery_date` **Ascending**.
8. Add secondary sort `open_po_value` **Descending**.
9. Set `open_po_value` to **Currency / INR / 2 decimals**.
10. Apply red conditional formatting to overdue rows.
11. Enable **View Underlying Data**.
12. Click **Save As**.
13. Save as `CT_P2_Expected_Delivery_Breach`.

## P2-D01 - Create the Dashboard

1. Click **+ New**.
2. Choose **Dashboard**.
3. Name it `CT_PAGE_2_Procurement_Vendor_Capital`.
4. Click **Create**.
5. Click **Edit Design**.
6. Add heading:

```text
Procurement, Vendor & Capital Control
Purchase commitments, vendor reliability, delivery exposure and price movement
```

7. Add the six Page 2 saved reports.
8. Arrange:
    - Row 1: five KPI Widgets
    - Row 2: Procurement Funnel and Vendor Scorecard
    - Row 3: Raw Material Price Trend and Top Price Movement
    - Row 4: Pending by Vendor and Expected Delivery Breach
9. Save.

## P2-K01 - Monthly Purchase

1. Open the dashboard in **Edit Design**.
2. Click **Widget > KPI Widget > Single Label**.
3. Select table `29_sum_ct_procurement_funnel.sql`.
4. Select Data Column `ordered_value`.
5. Select Calculation **Sum**.
6. Leave **Group By** blank.
7. Set label to `Monthly Purchase`.
8. Set subtitle to `Ordered gross value`.
9. Set format to **Currency / INR / 2 decimals**.
10. Click **Apply**.
11. Expected result: `INR 1,565,981.32`.

## P2-K02 - Open PO Exposure

1. Add **KPI Widget > Single Label**.
2. Select table `29_sum_ct_procurement_funnel.sql`.
3. Select Data Column `pending_value`.
4. Select Calculation **Sum**.
5. Leave **Group By** blank.
6. Set label to `Open PO Exposure`.
7. Set format to **Currency / INR / 2 decimals**.
8. Click **Apply**.
9. Expected result: `INR 177,145.39`.

## P2-K03 - Delayed PO Value

1. Add **KPI Widget > Single Label**.
2. Select table `29_sum_ct_procurement_funnel.sql`.
3. Select Data Column `delayed_value`.
4. Select Calculation **Sum**.
5. Leave **Group By** blank.
6. Set label to `Delayed PO Value`.
7. Set format to **Currency / INR / 2 decimals**.
8. Click **Apply**.
9. Expected result: `INR 156,529.82`.

## P2-K04 - Average OTIF

This ratio must be a saved Summary View because it is an Aggregate Formula.

1. Click **+ New**.
2. Click **New Report**.
3. Choose **Summary View**.
4. Select source table `24_fact_ct_po_receipt_line.sql`.
5. Drag Aggregate Formula `Vendor OTIF %` into the summary value area.
6. Do not add a grouping field.
7. Set label to `Avg OTIF`.
8. Set subtitle to `Formula demo - linkage approval pending`.
9. Set format to **Percentage / 2 decimals**.
10. Click **Save As**.
11. Save as `CT_P2_KPI_OTIF`.
12. Add this Summary View to the KPI row of the Page 2 dashboard.
13. Expected result: `53.70%`.

Do not average the row-level `otif_percent` field from Query 30.

## P2-K05 - Price Watch

1. Add **KPI Widget > Single Label**.
2. Select table `31_sum_ct_price_movement.sql`.
3. Select Data Column `item_code`.
4. Select Calculation **Count Distinct**.
5. Leave **Group By** blank.
6. Set label to `Price Watch`.
7. Set subtitle to `Raw materials tracked`.
8. Set format to **Whole Number**.
9. Click **Apply**.
10. Expected result: `42`.

## P2-F01 - Create Dashboard User Filters

Create the following filters in order.

### As-of Source Period

1. Click **+ Add User Filters**.
2. Select table `29_sum_ct_procurement_funnel.sql`.
3. Select `source_period_code`.
4. Choose **Dropdown > Single Select**.
5. Label: `As-of Source Period`.
6. Default: `month_03`.
7. Click **Apply**.

### Region

1. Click **+ Add User Filters**.
2. Select lookup field `37_dim_ct_outlet_enriched.sql.region`.
3. Choose **Dropdown > Multi Select**.
4. Label: `Region`.
5. Default: **All**.
6. Click **Apply**.

### Raw Material Category

1. Click **+ Add User Filters**.
2. Select table `22_fact_ct_purchase_order.sql`.
3. Select `category_name`.
4. Choose **Dropdown > Multi Select**.
5. Label: `Raw Material Category`.
6. Default: **All**.
7. Click **Apply**.

### Vendor

1. Click **+ Add User Filters**.
2. Select table `24_fact_ct_po_receipt_line.sql`.
3. Select `vendor_name`.
4. Choose **Dropdown > Multi Select**.
5. Label: `Vendor`.
6. Default: **All**.
7. Click **Apply**.

### PO Status

1. Click **+ Add User Filters**.
2. Select table `22_fact_ct_purchase_order.sql`.
3. Select `po_status`.
4. Choose **Dropdown > Multi Select**.
5. Label: `PO Status`.
6. Default: **All**.
7. Click **Apply**.

Use only these values if Zoho asks you to preselect values:

```text
Pending
Partially Received
Closed
Cancelled
```

### Raw Material

1. Click **+ Add User Filters**.
2. Select table `22_fact_ct_purchase_order.sql`.
3. Select `item_code`.
4. Choose **Dropdown with Search > Multi Select**.
5. Label: `Raw Material`.
6. Default: **All**.
7. Click **Apply**.

### Outlet

The ABNAH visual does not display this Page 2 control, but keep it in the
native Zoho validation dashboard.

1. Click **+ Add User Filters**.
2. Select `outlet_code`.
3. Choose **Dropdown > Multi Select**.
4. Label: `Outlet`.
5. Default: **All**.
6. Click **Apply**.

The custom portal can hide this control while retaining the mapping.

## P2-F02 - Map the Dashboard Filters

| Object | Period | Outlet | Region | Category | Vendor | PO Status | Raw Material |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Three Query 29 KPI Widgets | `source_period_code` | `outlet_code` | lookup `region` | Do not map | `vendor_name` | Do not map | Do not map |
| `CT_P2_Procurement_Funnel` | `source_period_code` | `outlet_code` | lookup `region` | Do not map | `vendor_name` | Do not map | Do not map |
| `CT_P2_Vendor_Scorecard` | `source_period_code` | `outlet_code` | lookup `region` | `category_name` | `vendor_name` | `po_status` | `item_code` |
| `CT_P2_KPI_OTIF` | `source_period_code` | `outlet_code` | lookup `region` | `category_name` | `vendor_name` | `po_status` | `item_code` |
| `CT_P2_Ingredient_Price_Trend` | Do not map | `outlet_code` | lookup `region` | `category_name` | `vendor_name` | Do not map | `item_code` |
| Price Watch KPI | `source_period_code` | `outlet_code` | lookup `region` | lookup `category_name` | `vendor_name` | Do not map | `item_code` |
| `CT_P2_Top_Price_Movement` | `source_period_code` | `outlet_code` | lookup `region` | lookup `category_name` | `vendor_name` | Do not map | `item_code` |
| `CT_P2_Pending_By_Vendor` | `source_period_code` | `outlet_code` | lookup `region` | `category_name` | `vendor_name` | `po_status` | `item_code` |
| `CT_P2_Expected_Delivery_Breach` | `source_period_code` | `outlet_code` | lookup `region` | `category_name` | `vendor_name` | `po_status` | `item_code` |

## P2 Validation

1. Set period to `month_03`.
2. Set all other filters to **All**.
3. Confirm KPI values:
    - `INR 1,565,981.32`
    - `INR 177,145.39`
    - `INR 156,529.82`
    - `53.70%`
    - `42`
4. Confirm Expected Delivery Breach has `38` rows and `21` distinct POs.
5. Confirm its open exposure totals approximately `INR 156,529.82`.
6. Confirm Price Trend still contains all three periods.
7. Select one vendor and confirm only vendor-compatible objects change.
8. Select one raw material and confirm Query 29 KPI Widgets do not change.
9. Reset all filters.
10. Save.

# Page 3 - Consumption Variance & Menu Profitability

Build these reference-required saved reports:

1. `CT_P3_Consumption_Bridge`
2. `CT_P3_Consumption_Variance`
3. `CT_P3_Menu_BCG`
4. `CT_P3_Outlet_Item_Heatmap`

## P3-R01 - Consumption Bridge

1. Click **+ New**.
2. Click **New Report**.
3. Choose **Chart View**.
4. Select source table `20_fact_ct_actual_consumption.sql`.
5. Choose **Combination Chart**.
6. Drag `source_period_code` to the X-axis.
7. Add these bar values in this order:
    - `opening_qty` with **Sum**
    - `purchase_qty` with **Sum**
    - `transfer_in_qty` with **Sum**
    - `bridge_transfer_out_qty` with **Sum**
    - `bridge_return_qty` with **Sum**
    - `bridge_closing_qty` with **Sum**
8. Add `calculated_actual_consumption_qty` with **Sum** as the line value.
9. Add report User Filter `item_code`:
    - dropdown with search
    - single select
    - label `Raw Material`
10. Add report User Filter `canonical_uom`:
    - dropdown
    - single select
    - label `UOM`
11. Do not display an all-UOM total.
12. Sort `source_period_code` **Ascending**.
13. Set quantity formats to **Number / 2 decimals**.
14. Use colors:
    - opening `#162552`
    - purchase `#9A8559`
    - transfer in `#2E7D5B`
    - transfer out `#C63D3D`
    - return `#D49A22`
    - closing `#7C8793`
    - actual consumption line `#4164D9`
15. Click **Save As**.
16. Save as `CT_P3_Consumption_Bridge`.

## P3-R02 - Consumption Variance

1. Click **+ New**.
2. Click **New Report**.
3. Choose **Chart View**.
4. Select source table `21_fact_ct_consumption_variance.sql`.
5. Choose **Butterfly Chart**.
6. Drag `item_name` to the X-axis/category shelf.
7. Drag `signed_consumption_variance_value` to the Y-axis/value shelf.
8. Select Calculation **Sum**.
9. Drag `consumption_variance_direction` to **Color/Series**.
10. Sort by the absolute visual magnitude, largest first. If Zoho cannot sort
    by absolute value, sort `signed_consumption_variance_value` descending.
11. Set format to **Currency / INR / 2 decimals**.
12. Set colors:
    - `OVER_CONSUMPTION` -> `#C63D3D`
    - `UNDER_CONSUMPTION` -> `#D49A22`
    - `MATCHED` -> `#2E7D5B`
13. Add subtitle:

```text
Actual consumption minus theoretical consumption
```

14. Click **Save As**.
15. Save as `CT_P3_Consumption_Variance`.

## P3-R03 - Menu BCG Matrix

1. Click **+ New**.
2. Click **New Report**.
3. Choose **Chart View**.
4. Select source table `32_sum_ct_menu_profitability.sql`.
5. Choose **Bubble Chart**.
6. Drag `sold_qty` to the X-axis and choose **Sum**.
7. Drag `gross_margin_percent` to the Y-axis and choose **Max**.
8. Drag `net_sales` to Bubble Size and choose **Sum**.
9. Drag `bcg_quadrant` to **Color/Series**.
10. Drag `menu_item_name` to **Text**.
11. Drag `outlet_name` to **Tooltip** first. This dimension keeps separate
    outlet/menu bubbles instead of merging the same menu item across outlets.
12. Add the remaining tooltip fields:
    - `menu_item_name`
    - `sold_qty`
    - `net_sales`
    - `gross_margin_value`
    - `gross_margin_percent`
13. Add report User Filter `menu_item_code`:
    - dropdown with search
    - multi-select
    - label `Menu Item`
14. Set quadrant colors:
    - `Stars` -> `#2E7D5B`
    - `Niche gems` -> `#4164D9`
    - `Volume drags` -> `#D49A22`
    - `Review / rationalize` -> `#C63D3D`
15. Enable **Use as Filter**.
16. Click **Save As**.
17. Save as `CT_P3_Menu_BCG`.

For all-outlet analysis, keep `outlet_name` available as a tooltip and test
one outlet separately. Do not average `gross_margin_percent`.

## P3-R04 - Item Sales Heatmap

1. Click **+ New**.
2. Click **New Report**.
3. Choose **Chart View**.
4. Select source table `25_fact_ct_menu_profitability.sql`.
5. Choose **Heat Map**.
6. Drag `menu_item_name` to the X-axis.
7. Drag `outlet_name` to the Y-axis.
8. Drag `net_sales` to Color/Value and choose **Sum**.
9. Sort by `net_sales` **Descending**.
10. Set **Top N** menu items to **Top 20** for the first build.
11. Set tooltip fields:
    - `super_category_name`
    - `category_name`
    - `menu_item_name`
    - `sold_qty` with Sum
    - `net_sales` with Sum
    - `gross_margin_value` with Sum
12. Use a five-step neutral-to-red heat scale.
13. Enable **Use as Filter**.
14. Click **Save As**.
15. Save as `CT_P3_Outlet_Item_Heatmap`.

The ABNAH custom portal will later switch between super category, category and
menu-item levels. Build this first Zoho report at menu-item level.

## P3-D01 - Create the Dashboard

1. Click **+ New**.
2. Choose **Dashboard**.
3. Name it `CT_PAGE_3_Consumption_Menu_Profitability`.
4. Click **Create**.
5. Click **Edit Design**.
6. Add heading:

```text
Consumption Variance & Menu Profitability
Actual versus theoretical consumption, leakage and menu economics
```

7. Add the four saved reports.
8. Arrange:
    - Row 1: five KPI objects
    - Row 2: Consumption Bridge and Consumption Variance
    - Row 3: Menu BCG Matrix full width
    - Row 4: Item Sales Heatmap full width
9. Save.

## P3-K01 - Net Sales

1. Open the dashboard in **Edit Design**.
2. Click **Widget > KPI Widget > Single Label**.
3. Select table `25_fact_ct_menu_profitability.sql`.
4. Select Data Column `net_sales`.
5. Select Calculation **Sum**.
6. Leave **Group By** blank.
7. Set label to `Net Sales`.
8. Set format to **Currency / INR / 2 decimals**.
9. Click **Apply**.
10. Expected result: `INR 2,192,475.48`.

## P3-K02 - Theoretical COGS

1. Add **KPI Widget > Single Label**.
2. Select table `25_fact_ct_menu_profitability.sql`.
3. Select Data Column `theoretical_cogs`.
4. Select Calculation **Sum**.
5. Leave **Group By** blank.
6. Set label to `Theoretical COGS`.
7. Set subtitle to `Recipe-cost based`.
8. Set format to **Currency / INR / 2 decimals**.
9. Click **Apply**.
10. Expected result: `INR 393,664.46`.

## P3-K03 - Gross Margin

1. Click **+ New**.
2. Click **New Report**.
3. Choose **Summary View**.
4. Select table `25_fact_ct_menu_profitability.sql`.
5. Drag Aggregate Formula `Menu Gross Margin %` into the value area.
6. Do not add a grouping field.
7. Set label to `Gross Margin`.
8. Set subtitle to `Recipe-cost based`.
9. Set format to **Percentage / 2 decimals**.
10. Click **Save As**.
11. Save as `CT_P3_KPI_Menu_Gross_Margin`.
12. Add the Summary View to the Page 3 KPI row.
13. Expected result: `82.04%`.

## P3-K04 - Menu Items

1. Add **KPI Widget > Single Label**.
2. Select table `25_fact_ct_menu_profitability.sql`.
3. Select Data Column `menu_item_code`.
4. Select Calculation **Count Distinct**.
5. Leave **Group By** blank.
6. Set label to `Menu Items`.
7. Set format to **Whole Number**.
8. Click **Apply**.
9. Expected result: `110`.

## P3-K05 - Consumption Leakage

1. Add **KPI Widget > Single Label**.
2. Select table `21_fact_ct_consumption_variance.sql`.
3. Select Data Column `leakage_value`.
4. Select Calculation **Sum**.
5. Leave **Group By** blank.
6. Set label to `Consumption Leakage`.
7. Set subtitle to `Positive variance only`.
8. Set format to **Currency / INR / 2 decimals**.
9. Click **Apply**.
10. Expected result: `INR 38,632.37`.

## P3-F01 - Create Dashboard User Filters

### As-of Source Period

1. Click **+ Add User Filters**.
2. Select table `25_fact_ct_menu_profitability.sql`.
3. Select `source_period_code`.
4. Choose **Dropdown > Single Select**.
5. Label: `As-of Source Period`.
6. Default: `month_03`.
7. Click **Apply**.

### Region

1. Click **+ Add User Filters**.
2. Select lookup field `37_dim_ct_outlet_enriched.sql.region`.
3. Choose **Dropdown > Multi Select**.
4. Label: `Region`.
5. Default: **All**.
6. Click **Apply**.

### Outlet

1. Click **+ Add User Filters**.
2. Select `outlet_code`.
3. Choose **Dropdown > Multi Select**.
4. Label: `Outlet`.
5. Default: **All**.
6. Click **Apply**.

### Menu Super Category

1. Click **+ Add User Filters**.
2. Select table `25_fact_ct_menu_profitability.sql`.
3. Select `super_category_name`.
4. Choose **Dropdown > Multi Select**.
5. Label: `Menu Super Category`.
6. Default: **All**.
7. Click **Apply**.

### Menu Category

1. Click **+ Add User Filters**.
2. Select table `25_fact_ct_menu_profitability.sql`.
3. Select `category_name`.
4. Choose **Dropdown > Multi Select**.
5. Label: `Menu Category`.
6. Default: **All**.
7. Click **Apply**.

### Menu Item

1. Click **+ Add User Filters**.
2. Select table `25_fact_ct_menu_profitability.sql`.
3. Select `menu_item_code`.
4. Choose **Dropdown with Search > Multi Select**.
5. Label: `Menu Item`.
6. Default: **All**.
7. Click **Apply**.

### Raw Material

1. Click **+ Add User Filters**.
2. Select table `21_fact_ct_consumption_variance.sql`.
3. Select `item_code`.
4. Choose **Dropdown with Search > Multi Select**.
5. Label: `Raw Material`.
6. Default: **All**.
7. Click **Apply**.

### UOM

1. Click **+ Add User Filters**.
2. Select table `21_fact_ct_consumption_variance.sql`.
3. Select `canonical_uom`.
4. Choose **Dropdown > Single Select**.
5. Label: `UOM`.
6. Select one default UOM when displaying quantities.
7. Click **Apply**.

## P3-F02 - Map the Dashboard Filters

| Object | Period | Outlet | Region | Menu Super Category | Menu Category | Menu Item | Raw Material | UOM |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Net Sales KPI | `source_period_code` | `outlet_code` | lookup `region` | `super_category_name` | `category_name` | `menu_item_code` | Do not map | Do not map |
| Theoretical COGS KPI | `source_period_code` | `outlet_code` | lookup `region` | `super_category_name` | `category_name` | `menu_item_code` | Do not map | Do not map |
| Gross Margin Summary | `source_period_code` | `outlet_code` | lookup `region` | `super_category_name` | `category_name` | `menu_item_code` | Do not map | Do not map |
| Menu Items KPI | `source_period_code` | `outlet_code` | lookup `region` | `super_category_name` | `category_name` | `menu_item_code` | Do not map | Do not map |
| Consumption Leakage KPI | `source_period_code` | `outlet_code` | lookup `region` | Do not map | Do not map | Do not map | `item_code` | Do not map |
| `CT_P3_Consumption_Bridge` | `source_period_code` | `outlet_code` | lookup `region` | Do not map | Do not map | Do not map | `item_code` | `canonical_uom` |
| `CT_P3_Consumption_Variance` | `source_period_code` | `outlet_code` | lookup `region` | Do not map | Do not map | Do not map | `item_code` | Do not map for value view |
| `CT_P3_Menu_BCG` | `source_period_code` | `outlet_code` | lookup `region` | `super_category_name` | `category_name` | `menu_item_code` | Do not map | Do not map |
| `CT_P3_Outlet_Item_Heatmap` | `source_period_code` | `outlet_code` | lookup `region` | `super_category_name` | `category_name` | `menu_item_code` | Do not map | Do not map |

## P3 Validation

1. Set period to `month_03`.
2. Set Outlet to **All**.
3. Set menu and ingredient filters to **All**.
4. Confirm KPI values:
    - `INR 2,192,475.48`
    - `INR 393,664.46`
    - `82.04%`
    - `110`
    - `INR 38,632.37`
5. Select one menu category.
6. Confirm only menu KPIs, BCG and Heatmap change.
7. Select one raw material.
8. Confirm only consumption objects change.
9. Confirm the Gross Margin card does not average row percentages.
10. Reset all filters and save.

# Page 4 - SCM Descriptive Explorer & Data Quality

Build these reference-required saved reports:

1. `CT_P4_SCM_Monthly_Trend`
2. `CT_P4_Data_Quality_Detail`
3. `CT_P4_Descriptive_Explorer`

Build six Data Quality KPI tiles inside the dashboard.

## P4-R01 - Month-End SCM Trend

1. Click **+ New**.
2. Click **New Report**.
3. Choose **Chart View**.
4. Select source table `33_sum_ct_scm_monthly.sql`.
5. Choose **Combination Chart**.
6. Drag `source_period_code` to the X-axis.
7. Add bar values:
    - `closing_stock_value` with **Sum**
    - `open_po_value` with **Sum**
8. Add line values:
    - `net_sales` with **Sum**
    - `actual_consumption_value` with **Sum**
9. Sort `source_period_code` **Ascending**.
10. Format every value as **Currency / INR / 2 decimals**.
11. Use colors:
    - Closing Stock `#424B56`
    - Open PO `#E44B51`
    - Net Sales `#4164D9`
    - Actual Consumption `#9A8559`
12. Do not apply the dashboard current-period filter to this trend.
13. Click **Save As**.
14. Save as `CT_P4_SCM_Monthly_Trend`.

## P4-R02 - Data Quality Detail

1. Click **+ New**.
2. Click **New Report**.
3. Choose **Tabular View**.
4. Select source table `34_fact_ct_data_quality_exception.sql`.
5. Add columns in this exact order:
    - `exception_type`
    - `source_period_code`
    - `outlet_code`
    - `outlet_name`
    - `exception_record_key`
    - `item_code`
    - `reference_number`
    - `exception_count`
    - `definition`
6. Sort `exception_type` **Ascending**.
7. Add a report User Filter:
    - field `exception_type`
    - dropdown
    - multi-select
    - label `Exception Type`
8. Enable **View Underlying Data**.
9. Enable export.
10. Click **Save As**.
11. Save as `CT_P4_Data_Quality_Detail`.

Do not map Source Period or Outlet dashboard filters to Query 34. Query 34
contains valid model-wide rows with `ALL` keys.

## P4-R03 - SCM Descriptive Explorer

1. Click **+ New**.
2. Click **New Report**.
3. Choose **Tabular View**.
4. Select source table `33_sum_ct_scm_monthly.sql`.
5. Add columns in this exact order:
    - `source_period_code`
    - `outlet_code`
    - `outlet_name`
    - `closing_stock_value`
    - `open_po_value`
    - `working_capital_value`
    - `net_sales`
    - `actual_consumption_value`
6. Sort `source_period_code` **Descending**.
7. Add secondary sort `outlet_code` **Ascending**.
8. Set all measures to **Currency / INR / 2 decimals**.
9. Enable **View Underlying Data**.
10. Enable export.
11. Click **Save As**.
12. Save as `CT_P4_Descriptive_Explorer`.

## P4-D01 - Create the Dashboard

1. Click **+ New**.
2. Choose **Dashboard**.
3. Name it `CT_PAGE_4_SCM_Explorer_Data_Quality`.
4. Click **Create**.
5. Click **Edit Design**.
6. Add heading:

```text
SCM Descriptive Explorer & Data Quality
Month-end trend, governed drilldown, export and exception control
```

7. Add the three Page 4 saved reports.
8. Arrange:
    - Row 1: five reference KPI Widgets
    - Row 2: Month-End SCM Trend full width
    - Row 3: six Data Quality tiles
    - Row 4: Data Quality Detail full width
    - Row 5: SCM Descriptive Explorer full width
9. Save.

## P4-K01 - Closing Stock Value

1. Open the dashboard in **Edit Design**.
2. Click **Widget > KPI Widget > Single Label**.
3. Select table `33_sum_ct_scm_monthly.sql`.
4. Select Data Column `closing_stock_value`.
5. Select Calculation **Sum**.
6. Leave **Group By** blank.
7. Set label to `Closing Stock Value`.
8. Set format to **Currency / INR / 2 decimals**.
9. Click **Apply**.
10. Expected result: `INR 3,344,237.44`.

## P4-K02 - Open PO Snapshot

1. Add **KPI Widget > Single Label**.
2. Select table `33_sum_ct_scm_monthly.sql`.
3. Select Data Column `open_po_value`.
4. Select Calculation **Sum**.
5. Leave **Group By** blank.
6. Set label to `Open PO Snapshot`.
7. Set format to **Currency / INR / 2 decimals**.
8. Click **Apply**.
9. Expected result: `INR 177,145.39`.

## P4-K03 - Monthly Sales

1. Add **KPI Widget > Single Label**.
2. Select table `33_sum_ct_scm_monthly.sql`.
3. Select Data Column `net_sales`.
4. Select Calculation **Sum**.
5. Leave **Group By** blank.
6. Set label to `Monthly Sales`.
7. Set format to **Currency / INR / 2 decimals**.
8. Click **Apply**.
9. Expected result: `INR 2,192,475.48`.

## P4-K04 - Actual Consumption

1. Add **KPI Widget > Single Label**.
2. Select table `33_sum_ct_scm_monthly.sql`.
3. Select Data Column `actual_consumption_value`.
4. Select Calculation **Sum**.
5. Leave **Group By** blank.
6. Set label to `Actual Consumption`.
7. Set format to **Currency / INR / 2 decimals**.
8. Click **Apply**.
9. Expected result: `INR 377,620.25`.

## P4-K05 - Variance Value

1. Add **KPI Widget > Single Label**.
2. Select table `21_fact_ct_consumption_variance.sql`.
3. Select Data Column `signed_consumption_variance_value`.
4. Select Calculation **Sum**.
5. Leave **Group By** blank.
6. Set label to `Variance Value`.
7. Set subtitle to `Actual consumption minus theoretical consumption`.
8. Set format to **Currency / INR / 2 decimals**.
9. Allow negative values.
10. Click **Apply**.
11. Expected result: `INR -22,106.87`.

Do not color every negative variance red. Under-consumption can also indicate a
recipe, stock-count, UOM or process issue.

## P4-Q01 - Negative Stock Tile

1. Click **Widget > KPI Widget > Single Label**.
2. Select table `34_fact_ct_data_quality_exception.sql`.
3. Select Data Column `exception_count`.
4. Select Calculation **Sum**.
5. Leave **Group By** blank.
6. Add widget fixed filter:
    - `exception_type`
    - Include `NEGATIVE_STOCK`
7. Set label to `Negative Stock Rows`.
8. Set format to **Whole Number**.
9. Set card color to red.
10. Click **Apply**.
11. Expected result: `1`.

## P4-Q02 - Zero Stock With Demand Tile

1. Add **KPI Widget > Single Label**.
2. Use Data Column `exception_count` with **Sum**.
3. Leave **Group By** blank.
4. Add fixed filter `exception_type` Include
   `ZERO_STOCK_WITH_DEMAND`.
5. Set label to `Zero Stock With Demand`.
6. Set format to **Whole Number**.
7. Set card color to red.
8. Click **Apply**.
9. Expected result: `2`.

## P4-Q03 - Missing Recipe Tile

1. Add **KPI Widget > Single Label**.
2. Use Data Column `exception_count` with **Sum**.
3. Leave **Group By** blank.
4. Add fixed filter `exception_type` Include
   `SOLD_ITEM_MISSING_RECIPE`.
5. Set label to `Sold Items Missing Recipe`.
6. Set format to **Whole Number**.
7. Set card color to amber.
8. Click **Apply**.
9. Expected result: `0`.

If Zoho renders no matching row as blank rather than `0`, leave the tile as
blank and validate Query 34 directly. Do not replace a blank no-row result with
an invented count.

## P4-Q04 - Missing Item Master Tile

1. Add **KPI Widget > Single Label**.
2. Use Data Column `exception_count` with **Sum**.
3. Leave **Group By** blank.
4. Add fixed filter `exception_type` Include
   `OPERATIONAL_ITEM_MISSING_MASTER`.
5. Set label to `Items Missing Master`.
6. Set format to **Whole Number**.
7. Set card color to amber.
8. Click **Apply**.
9. Expected result: `0`.

If Zoho renders no matching row as blank rather than `0`, leave the tile as
blank and validate Query 34 directly. Do not replace a blank no-row result with
an invented count.

## P4-Q05 - UOM Mismatch Tile

1. Add **KPI Widget > Single Label**.
2. Use Data Column `exception_count` with **Sum**.
3. Leave **Group By** blank.
4. Add fixed filter `exception_type` Include
   `UOM_MISMATCH_WITHOUT_CONVERSION`.
5. Set label to `UOM Mismatch`.
6. Set format to **Whole Number**.
7. Set card color to amber.
8. Click **Apply**.
9. Expected result: `0`.

If Zoho renders no matching row as blank rather than `0`, leave the tile as
blank and validate Query 34 directly. Do not replace a blank no-row result with
an invented count.

## P4-Q06 - Missing Expected Delivery Tile

1. Add **KPI Widget > Single Label**.
2. Use Data Column `exception_count` with **Sum**.
3. Leave **Group By** blank.
4. Add fixed filter `exception_type` Include
   `OPEN_PO_MISSING_EXPECTED_DELIVERY`.
5. Set label to `Open PO Missing Expected Delivery`.
6. Set format to **Whole Number**.
7. Set card color to red.
8. Click **Apply**.
9. Expected result: `3`.

## P4-F01 - Create Dashboard User Filters

### Current Period

1. Click **+ Add User Filters**.
2. Select table `33_sum_ct_scm_monthly.sql`.
3. Select `source_period_code`.
4. Choose **Dropdown > Single Select**.
5. Label: `Current Period`.
6. Default: `month_03`.
7. Click **Apply**.

### Region

1. Click **+ Add User Filters**.
2. Select lookup field `37_dim_ct_outlet_enriched.sql.region`.
3. Choose **Dropdown > Multi Select**.
4. Label: `Region`.
5. Default: **All**.
6. Click **Apply**.

### Outlet

1. Click **+ Add User Filters**.
2. Select `outlet_code`.
3. Choose **Dropdown > Multi Select**.
4. Label: `Outlet`.
5. Default: **All**.
6. Click **Apply**.

### Raw Material Category

1. Click **+ Add User Filters**.
2. Select table `21_fact_ct_consumption_variance.sql`.
3. Select `category_name`.
4. Choose **Dropdown > Multi Select**.
5. Label: `Raw Material Category`.
6. Default: **All**.
7. Click **Apply**.

### Exception Type

1. Click **+ Add User Filters**.
2. Select table `34_fact_ct_data_quality_exception.sql`.
3. Select `exception_type`.
4. Choose **Dropdown > Multi Select**.
5. Label: `Exception Type`.
6. Default: **All**.
7. Click **Apply**.

## P4-F02 - Map the Dashboard Filters

| Object | Current Period | Outlet | Region | Raw Material Category | Exception Type |
| --- | --- | --- | --- | --- | --- |
| Closing Stock KPI | `source_period_code` | `outlet_code` | lookup `region` | Do not map | Do not map |
| Open PO KPI | `source_period_code` | `outlet_code` | lookup `region` | Do not map | Do not map |
| Monthly Sales KPI | `source_period_code` | `outlet_code` | lookup `region` | Do not map | Do not map |
| Actual Consumption KPI | `source_period_code` | `outlet_code` | lookup `region` | Do not map | Do not map |
| Variance Value KPI | `source_period_code` | `outlet_code` | lookup `region` | `category_name` | Do not map |
| `CT_P4_SCM_Monthly_Trend` | Do not map | `outlet_code` | lookup `region` | Do not map | Do not map |
| Six Query 34 tiles | Do not map | Do not map | Do not map | Do not map | Do not map |
| `CT_P4_Data_Quality_Detail` | Do not map | Do not map | Do not map | Do not map | `exception_type` |
| `CT_P4_Descriptive_Explorer` | `source_period_code` | `outlet_code` | lookup `region` | Do not map | Do not map |

## P4 Validation

1. Set Current Period to `month_03`.
2. Set Outlet and Region to **All**.
3. Confirm the five KPI values:
    - `INR 3,344,237.44`
    - `INR 177,145.39`
    - `INR 2,192,475.48`
    - `INR 377,620.25`
    - `INR -22,106.87`
4. Confirm the monthly trend still shows `month_01`, `month_02`, and
   `month_03`.
5. Confirm the six Data Quality tiles do not change when Current Period or
   Outlet changes.
6. Select one Exception Type.
7. Confirm only `CT_P4_Data_Quality_Detail` changes.
8. Reset filters and save.

# Required Color and Formatting Settings

## Page Accent Colors

| Page | Primary | Secondary |
| --- | --- | --- |
| Page 1 | `#5B2D82` | `#9A8559` |
| Page 2 | `#4164D9` | `#223B9C` |
| Page 3 | `#9A8559` | `#162552` |
| Page 4 | `#E44B51` | `#424B56` |

## RAG Colors

| State | Color |
| --- | --- |
| Purple / immediate | `#6C3B8C` |
| Red / high | `#C63D3D` |
| Amber / watch | `#D49A22` |
| Green / healthy | `#2E7D5B` |
| Grey / unavailable | `#7C8793` |

Use RAG colors only for a real state or exception. Page 4 descriptive totals
must remain neutral.

# Save and URL Handoff

After each saved report is validated:

1. Open the report in **View Mode**.
2. Click **Share**.
3. Click **Embed** or **URL / Permalink**.
4. Choose secured **Access with Login**.
5. Keep interactive mode enabled.
6. Copy the individual report URL.
7. Record it against the exact `CT_...` report name.

After each page dashboard is validated:

1. Open the dashboard in **View Mode**.
2. Click **Share**.
3. Click **Embed**.
4. Choose secured **Access with Login**.
5. Copy the dashboard URL.
6. Record it against the exact `CT_PAGE_...` name.

Provide both the individual report URLs and four dashboard URLs. The individual
report URLs will populate the custom ABNAH page slots. The dashboard URLs will
remain the native Zoho validation and fallback views.

# Final Build Order

1. Build and validate all Page 1 saved reports.
2. Build Page 1 dashboard and KPI Widgets.
3. Add and map Page 1 dashboard filters.
4. Repeat for Pages 2, 3, and 4.
5. Compare all default values with
   `04A_DASHBOARD_EXPECTED_RESULTS.md`.
6. Collect individual report URLs.
7. Collect four dashboard URLs.
8. Do not publish the custom portal until every URL has been tested while
   signed in with the intended company Zoho account.
