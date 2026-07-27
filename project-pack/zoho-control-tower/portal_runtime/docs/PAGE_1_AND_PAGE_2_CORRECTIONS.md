# Page 1 And Page 2 - Do This Next

This guide starts from the current Zoho workspace state:

- all 38 Query Tables are saved;
- corrected Queries 28, 29, 30 and 31 are saved;
- the three Query 30 Aggregate Formulas are saved;
- Page 1 exists and Page 2 is being corrected.

Do not replace another Query Table. Do not delete any Aggregate Formula.

## What The Live Page 1 Test Proved

The public Page 1 dashboard was tested with no date selected and then with
`01 Mar 2026 - 31 Mar 2026`.

| Visible KPI | No date selected | March selected | March truth | Result |
| --- | ---: | ---: | ---: | --- |
| Restaurants at Risk | 3 | 3 | 3 | Correct |
| Menu Items Impacted | 110 | 110 | 110 | Cannot prove mapping because both scopes equal 110 |
| Stockout Risk (Net Sales) | INR 976,271.72 | INR 976,271.72 | INR 411,695.55 | **Date filter is not reaching this Query 28 widget** |
| Expiry Risk (Value) | INR 628,131.99 | about INR 271,399 | INR 271,399.12 | Correct |
| Open Actions | 16 | 6 | 6 | Correct |

The stockout value is not duplicated by Query 28. `INR 976,271.72` is the
correct three-month total. The widget is still summing January, February and
March because its Timeline Filter mapping is missing.

## Part 1 - Fix Page 1 Without Changing SQL

### 1A - Keep The Existing Date Range Control

1. Open `CT_PAGE_1_Risk_Action_Center`.
2. Click **Edit Design**.
3. In **User Filters**, find `Date Range`.
4. Click its **Edit** or pencil icon.
5. Keep **Single Select Box** as the component.
6. Expand **Timeline Filter Column Mapping**.
7. Select the following values from the available lists:

| Table shown by Zoho | Select this date column |
| --- | --- |
| `27_fact_ct_inventory_risk.sql` | `snapshot_date` |
| `28_fact_ct_menu_impact.sql` | `snapshot_date` |
| `38_fact_ct_expiry_risk.sql` | `as_of_date` |
| `36_fact_ct_risky_po.sql` | `as_of_date` |

Do not type a query name or column name. Zoho's Timeline Filter mapping is a
selection list, not a text box.

### 1B - Force The Correct Date On Every Page 1 Object

For each row below:

1. Hover over the named KPI/report in the dashboard.
2. Click the **More** or three-dot icon.
3. Click **Options**.
4. Confirm **Apply Dashboard Filters** is checked.
5. Open **Mapping Timeline Filter**. In some Zoho layouts this appears as
   **Customize** beside `Date Range`.
6. Select the exact date column in the last column below.
7. Click **Apply**.

| Visible KPI or report name | Source Table | Select in Mapping Timeline Filter |
| --- | --- | --- |
| Restaurants at Risk | `27_fact_ct_inventory_risk.sql` | `snapshot_date` |
| Menu Items Impacted | `28_fact_ct_menu_impact.sql` | `snapshot_date` |
| Stockout Risk (Net Sales) | `28_fact_ct_menu_impact.sql` | `snapshot_date` |
| Expiry Risk (Value) | `38_fact_ct_expiry_risk.sql` | `as_of_date` |
| Open Actions | `27_fact_ct_inventory_risk.sql` | `snapshot_date` |
| `CT_P1_Outlet_Risk_Map` | `27_fact_ct_inventory_risk.sql` | `snapshot_date` |
| `CT_P1_Action_Center` | `27_fact_ct_inventory_risk.sql` | `snapshot_date` |
| `CT_P1_Stockout_Risk_Detail` | `27_fact_ct_inventory_risk.sql` | `snapshot_date` |
| `CT_P1_Menu_Impact_Detail` | `28_fact_ct_menu_impact.sql` | `snapshot_date` |
| `CT_P1_Expiry_Risk_Detail_Demo` | `38_fact_ct_expiry_risk.sql` | `as_of_date` |
| `CT_P1_Vendor_PO_Risk` | `36_fact_ct_risky_po.sql` | `as_of_date` |

The three Query 28 objects are the critical correction:

1. `Menu Items Impacted`
2. `Stockout Risk (Net Sales)`
3. `CT_P1_Menu_Impact_Detail`

If `snapshot_date` is visible but disabled, do not type it elsewhere. Open
`28_fact_ct_menu_impact.sql` in **Data** and confirm `snapshot_date` has a Date
calendar icon. If Zoho shows it as Text, stop there and report the metadata
problem; do not create another dashboard filter.

### 1C - Verify The Stockout KPI Definition

Open the `Stockout Risk (Net Sales)` widget and confirm:

| Setting | Exact value |
| --- | --- |
| Source | `28_fact_ct_menu_impact.sql` |
| Data column | `allocated_forecast_net_sales_at_risk` |
| Aggregation | Sum |
| Group By | Empty |
| Fixed filter | None |

Do not use `forecast_net_sales_at_risk`. That unallocated field repeats when a
menu item depends on multiple risky ingredients.

### 1D - Test Page 1

1. Save the dashboard.
2. Open **View Mode**.
3. Set `Date Range` to `01 Mar 2026 - 31 Mar 2026`.
4. Keep Outlet, Raw Material Category and Action Owner at `All`.
5. Verify:

| KPI | Required March result |
| --- | ---: |
| Restaurants at Risk | 3 |
| Menu Items Impacted | 110 |
| Stockout Risk (Net Sales) | INR 411,695.55 |
| Expiry Risk (Value) | INR 271,399.12 |
| Open Actions | 6 |

Open `CT_P1_Menu_Impact_Detail` and confirm every visible `snapshot_date` is
`31 Mar 2026`. If the KPI still displays `9.76L`, the Query 28 widget mapping
was not saved.

## Part 2 - Clean The Existing Page 2 Filter Bar

The current dashboard visibly contains these ten controls:

1. `As-of Source Period.`
2. `Raw Material`
3. `Vendor`
4. `UOM`
5. `Region`
6. `Raw Material Category`
7. `Vendor Name (Global)`
8. `PO Status`
9. `Raw Material (Global)`
10. `Outlet`

The first four controls are the old period control and price-trend-specific
controls. Remove them from the dashboard-wide row:

1. Delete `As-of Source Period.`
2. Delete the first `Raw Material` control, located immediately after it.
3. Delete the first `Vendor` control.
4. Delete `UOM` from the dashboard-wide row.

Keep and rename the remaining controls:

| Current visible label | Final visible label |
| --- | --- |
| `Region` | `Region` |
| `Raw Material Category` | `Ingredient Category` |
| `Vendor Name (Global)` | `Vendor` |
| `PO Status` | `PO Status` |
| `Raw Material (Global)` | `Raw Material` |
| `Outlet` | `Outlet` |

`UOM` may remain only inside `CT_P2_Ingredient_Price_Trend`.

To stop Zoho from adding the old report controls back:

1. In dashboard **Edit Design**, open the **User Filters** panel.
2. Turn off **Auto Add User Filters from Reports**.
3. Hover `CT_P2_Ingredient_Price_Trend`.
4. Click **More > Options**.
5. Use **Show Report Specific User Filter** only for `UOM`.

The global `Raw Material` and `Vendor` controls will filter the trend after
their column mappings are completed below.

## Part 3 - Add And Map The Page 2 Date Range

### 3A - Create The Control

1. In `CT_PAGE_2_Procurement_Vendor_Capital`, click **Edit Design**.
2. Click **Add User Filters**.
3. Check **Include Timeline Filter**.
4. Click the Timeline Filter's pencil icon.
5. Set **Filter Display Name** to `Date Range`.
6. Set **Choose Component Type** to `Single Select Box`.
7. Expand **Timeline Filter Column Mapping**.
8. Select one date column per table:

| Table shown by Zoho | Select |
| --- | --- |
| `29_sum_ct_procurement_funnel.sql` | `po_date` |
| `30_sum_ct_vendor_scorecard.sql` | `po_date` |
| `31_sum_ct_price_movement.sql` | `price_as_of_date` |
| `22_fact_ct_purchase_order.sql` | `po_date` |
| `24_fact_ct_po_receipt_line.sql` | `po_date` |
| `23_fact_ct_purchase_receipt.sql` | `receipt_date` |

There is nothing to type and no lookup relationship to create in this dialog.

### 3B - Map Every Visible Page 2 Object

For each row:

1. Hover the named object.
2. Click **More > Options**.
3. Check **Apply Dashboard Filters**.
4. Open **Mapping Timeline Filter** or **Customize** beside `Date Range`.
5. Select the exact date field below.
6. Click **Apply**.

| Visible KPI or report | Source Table | Date field to select |
| --- | --- | --- |
| Ordered Value | `29_sum_ct_procurement_funnel.sql` | `po_date` |
| Open PO | `29_sum_ct_procurement_funnel.sql` | `po_date` |
| Delayed PO | `29_sum_ct_procurement_funnel.sql` | `po_date` |
| Avg Vendor OTIF | `24_fact_ct_po_receipt_line.sql` | `po_date` |
| Items to Price Watch | `31_sum_ct_price_movement.sql` | `price_as_of_date` |
| `CT_P2_Ingredient_Price_Trend` | `23_fact_ct_purchase_receipt.sql` | `receipt_date` |
| `CT_P2_Procurement_Funnel` | `29_sum_ct_procurement_funnel.sql` | `po_date` |
| `CT_P2_Vendor_Scorecard` | `30_sum_ct_vendor_scorecard.sql` | `po_date` |
| `CT_P2_Expected_Delivery_Breach` | `22_fact_ct_purchase_order.sql` | `po_date` |
| `CT_P2_Pending_By_Vendor` | `29_sum_ct_procurement_funnel.sql` | `po_date` |
| `CT_P2_Top_Price_Movement` | `31_sum_ct_price_movement.sql` | `price_as_of_date` |

## Part 4 - Map The Five Page 2 Dimension Filters

Zoho calls this a merged User Filter. You do not type expressions.

For each existing filter:

1. Hover the filter and click its pencil icon.
2. Click **Edit Column Mapping**.
3. Select the columns listed for that filter.
4. If **Edit Column Mapping** is not shown, add the same field from the other
   table as a temporary User Filter, then drag it onto the primary filter to
   merge it.
5. Click **OK** and then **Apply**.

### Outlet

Merge `outlet_code` from:

- `29_sum_ct_procurement_funnel.sql`
- `30_sum_ct_vendor_scorecard.sql`
- `31_sum_ct_price_movement.sql`
- `22_fact_ct_purchase_order.sql`
- `24_fact_ct_po_receipt_line.sql`
- `23_fact_ct_purchase_receipt.sql`

### Ingredient Category

Merge `category_name` from the same six tables.

### Vendor

Merge `vendor_name` from the same six tables.

### Raw Material

Merge `item_code` from the same six tables. Use `item_name` only as the
display label if Zoho offers that option.

### PO Status

Merge `po_status` only from:

- `29_sum_ct_procurement_funnel.sql`
- `30_sum_ct_vendor_scorecard.sql`
- `22_fact_ct_purchase_order.sql`
- `24_fact_ct_po_receipt_line.sql`

Do not map PO Status to:

- `31_sum_ct_price_movement.sql`;
- `23_fact_ct_purchase_receipt.sql`.

### Region

Keep `Region` from the canonical outlet lookup, Query 37. It should flow
through the existing `outlet_code` lookups. The synthetic demo contains only
`North`, so Region cannot be functionally tested until another region exists.

## Part 5 - Page 2 Object Contract

Use this table instead of searching another README for source information.

| Visible object | Source | Date | Outlet | Category | Vendor | Raw Material | PO Status | Fixed/report-only rule |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Ordered Value | Query 29 | `po_date` | Yes | Yes | Yes | Yes | Yes | Sum `ordered_value` |
| Open PO | Query 29 | `po_date` | Yes | Yes | Yes | Yes | Yes | Sum `pending_value` |
| Delayed PO | Query 29 | `po_date` | Yes | Yes | Yes | Yes | Yes | Sum `delayed_value` |
| Avg Vendor OTIF | Query 24 | `po_date` | Yes | Yes | Yes | Yes | Yes | Use `Vendor OTIF %` Aggregate Formula |
| Items to Price Watch | Query 31 | `price_as_of_date` | Yes | Yes | Yes | Yes | No | Count Distinct `item_code`; keep `NO_BASELINE` |
| `CT_P2_Ingredient_Price_Trend` | Query 23 | `receipt_date` | Yes | Yes | Yes | Yes | No | `UOM` remains report-specific |
| `CT_P2_Procurement_Funnel` | Query 29 | `po_date` | Yes | Yes | Yes | Yes | Yes | Sum four value fields |
| `CT_P2_Vendor_Scorecard` | Query 30 | `po_date` | Yes | Yes | Yes | Yes | Yes | Use all three Q30 formulas |
| `CT_P2_Expected_Delivery_Breach` | Query 22 | `po_date` | Yes | Yes | Yes | Yes | Yes | `delayed_po_flag`: include `1` |
| `CT_P2_Pending_By_Vendor` | Query 29 | `po_date` | Yes | Yes | Yes | Yes | Yes | Sum `pending_value` |
| `CT_P2_Top_Price_Movement` | Query 31 | `price_as_of_date` | Yes | Yes | Yes | Yes | No | Exclude `NO_BASELINE`; sort absolute change descending |

## Part 6 - Validate Page 2

1. Save the dashboard.
2. Open **View Mode**.
3. Select `01 Mar 2026 - 31 Mar 2026`.
4. Clear every other filter.
5. Verify:

| KPI | Required March result |
| --- | ---: |
| Ordered Value | INR 1,565,981.32 |
| Open PO | INR 177,145.39 |
| Delayed PO | INR 156,529.83 |
| Avg Vendor OTIF | 53.70% |
| Items to Price Watch | 42 |

Then test one control at a time:

1. Outlet must change all five KPIs and all compatible reports.
2. Ingredient Category must change all five KPIs and all compatible reports.
3. Vendor must change all five KPIs and all vendor-aware reports.
4. Raw Material must change all item-aware objects.
5. PO Status must change only Query 22, 24, 29 and 30 objects.
6. Date Range must remove every row outside the selected physical dates.

## Stop Rules

- Do not re-save another Query Table for these two filter issues.
- Do not delete the seven existing Aggregate Formulas.
- Do not reintroduce `As-of Source Period.` on Page 2.
- Do not type SQL such as `<>`, `=` or column names into dashboard controls.
- Do not use Query 23 as a separate dashboard-wide Raw Material or Vendor
  control.
- Do not accept `9.76L` as the March Stockout Risk value.

## Unchanged Evidence Boundaries

Some expiry rows are an `Opening stock estimate` and intentionally have no
GRN, PO or vendor lineage. Do not fill those cells with invented identifiers.

`recommended_action`, `action_owner` and `due_band` are model outputs created by CASE rules.
They are not POSIST source fields and must remain labelled as model
recommendations.

## URL And Authentication Handoff

Use:

```text
portal-handoff/ABNAH_PORTAL_HANDOFF_TEMPLATE.json
```

Copy it to the ignored `.local.json` file and fill the URL/key placeholders
after Page 1 and Page 2 pass the checks above. The folder README contains the
exact validation command.
