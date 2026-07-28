# Zoho Click-by-Click: Concise P1 and P2 Demo

Use this runbook only for the new sample dashboards. Do not edit the existing
38 Query Tables or existing dashboards.

## 1. Build the Six Query Tables

For each row below:

1. In the ABNAH workspace, click **Create**.
2. Click **New Query Table**.
3. Open the listed SQL file and paste its complete contents.
4. Click **Execute Query**.
5. Confirm the preview returns rows.
6. Click **Save**.
7. Enter the exact Query Table name shown below, including `.sql`.

| Order | Save as | SQL file |
|---:|---|---|
| 1 | `D03_demo_p1_expiry_watch.sql` | `queries/D03_demo_p1_expiry_watch.sql` |
| 2 | `D04_demo_p2_po_control.sql` | `queries/D04_demo_p2_po_control.sql` |
| 3 | `D01_demo_p1_action_queue.sql` | `queries/D01_demo_p1_action_queue.sql` |
| 4 | `D02_demo_p1_menu_impact.sql` | `queries/D02_demo_p1_menu_impact.sql` |
| 5 | `D05_demo_p2_vendor_control.sql` | `queries/D05_demo_p2_vendor_control.sql` |
| 6 | `D06_demo_p2_price_watch.sql` | `queries/D06_demo_p2_price_watch.sql` |

Do not create lookups for these six tables. Their shared filter fields are
mapped inside the dashboard, not through lookup relationships.

## 2. Verify Data Types

Open each new Query Table in **Data** and verify:

| Column | Required type |
|---|---|
| `filter_date` | Date |
| `filter_outlet` | Plain Text |
| `filter_category` | Plain Text |
| `filter_severity` | Plain Text |
| `filter_vendor` | Plain Text |

If `filter_date` is not Date:

1. Right-click the column header.
2. Click **Change Data Type**.
3. Choose **Date**.
4. Save.

Do not change the type of any physical date column in the existing 38 tables.

## 3. Create the P1 Reports

### 3.1 `DEMO_P1_Action_Queue`

1. Open `D01_demo_p1_action_queue.sql`.
2. Click **Create** > **New Report** > **Tabular View**.
3. Add these columns in this order:

| Position | Column | Display label |
|---:|---|---|
| 1 | `risk_severity` | Severity |
| 2 | `item_name` | Item |
| 3 | `current_stock_qty` | Current Stock |
| 4 | `valid_open_po_qty` | Inbound PO |
| 5 | `shortage_qty` | Shortage |
| 6 | `days_cover` | Days Cover |
| 7 | `total_risk_value` | Risk Value |
| 8 | `recommended_action` | Action |

4. Sort `risk_severity_rank` **Descending**.
5. Add a fixed design filter:
   `filter_severity` > **Individual Values** > include `PURPLE`, `RED`, `AMBER`.
6. Save as `DEMO_P1_Action_Queue`.

This fixed design filter is not a user filter. It prevents healthy rows from
crowding the action queue.

### 3.2 `DEMO_P1_Menu_Impact`

1. Open `D02_demo_p1_menu_impact.sql`.
2. Click **Create** > **New Report** > **Tabular View**.
3. Add:

| Position | Column | Display label |
|---:|---|---|
| 1 | `risk_severity` | Severity |
| 2 | `ingredient_name` | Risk Ingredient |
| 3 | `menu_item_name` | Menu Item |
| 4 | `shortage_qty` | Ingredient Shortage |
| 5 | `forecast_menu_qty` | Forecast Menu Qty |
| 6 | `allocated_forecast_net_sales_at_risk` | Sales At Risk |

4. Sort `allocated_forecast_net_sales_at_risk` **Descending**.
5. Save as `DEMO_P1_Menu_Impact`.

### 3.3 `DEMO_P1_Expiry_Watch`

1. Open `D03_demo_p1_expiry_watch.sql`.
2. Click **Create** > **New Report** > **Tabular View**.
3. Add:

| Position | Column | Display label |
|---:|---|---|
| 1 | `filter_severity` | Severity |
| 2 | `item_name` | Item |
| 3 | `vendor_name` | Vendor |
| 4 | `batch_number` | Estimated Batch |
| 5 | `expiry_qty_at_risk` | Qty At Risk |
| 6 | `estimated_expiry_date` | Estimated Expiry |
| 7 | `days_to_expiry` | Days Left |
| 8 | `expiry_risk_value` | Value At Risk |

4. Sort `days_to_expiry` **Ascending**.
5. Save as `DEMO_P1_Expiry_Watch`.
6. Add subtitle text in the dashboard: `Synthetic estimate - not POSIST expiry truth`.

### 3.4 P1 KPI Widgets

Create these widgets inside the new sample P1 dashboard:

| Widget | Base table | Measure | Aggregation | Fixed filter |
|---|---|---|---|---|
| Open Actions | D01 | `action_id` | Count Distinct | `filter_severity` is PURPLE, RED, or AMBER |
| Menu Sales At Risk | D02 | `allocated_forecast_net_sales_at_risk` | Sum | None |
| Estimated Expiry Value | D03 | `expiry_risk_value` | Sum | None |

Use INR formatting with zero decimals for the two value widgets.

## 4. Create the P2 Reports

### 4.1 `DEMO_P2_PO_Control`

1. Open `D04_demo_p2_po_control.sql`.
2. Click **Create** > **New Report** > **Tabular View**.
3. Add:

| Position | Column | Display label |
|---:|---|---|
| 1 | `control_severity` | Severity |
| 2 | `po_number` | PO Number |
| 3 | `filter_vendor` | Vendor |
| 4 | `item_name` | Item |
| 5 | `po_status` | PO Status |
| 6 | `expected_delivery_date` | Expected Date |
| 7 | `remaining_qty` | Open Qty |
| 8 | `open_po_value` | Open Value |

4. Sort `control_severity` **Descending**, then `open_po_value`
   **Descending**.
5. Save as `DEMO_P2_PO_Control`.

### 4.2 `DEMO_P2_Vendor_Control`

1. Open `D05_demo_p2_vendor_control.sql`.
2. Click **Create** > **New Report** > **Tabular View**.
3. Add:

| Position | Column | Display label |
|---:|---|---|
| 1 | `vendor_control_status` | Status |
| 2 | `vendor_name` | Vendor |
| 3 | `category_name` | Category |
| 4 | `po_count` | POs |
| 5 | `open_po_value` | Open Value |
| 6 | `otif_percent` | OTIF % |
| 7 | `fill_rate_percent` | Fill Rate % |
| 8 | `delayed_po_line_count` | Delayed Lines |

4. Sort `delayed_po_line_count` **Descending**, then `open_po_value`
   **Descending**.
5. Save as `DEMO_P2_Vendor_Control`.

### 4.3 `DEMO_P2_Price_Watch`

1. Open `D06_demo_p2_price_watch.sql`.
2. Click **Create** > **New Report** > **Tabular View**.
3. Add:

| Position | Column | Display label |
|---:|---|---|
| 1 | `price_control_status` | Status |
| 2 | `item_name` | Item |
| 3 | `filter_vendor` | Vendor |
| 4 | `current_unit_price` | Current Price |
| 5 | `previous_unit_price` | Previous Price |
| 6 | `price_change_percent` | Change % |
| 7 | `price_change_value_impact` | Value Impact |

4. Sort `price_change_value_impact` **Descending**.
5. Save as `DEMO_P2_Price_Watch`.

### 4.4 P2 KPI Widgets

| Widget | Base table | Measure | Aggregation | Fixed filter |
|---|---|---|---|---|
| Open PO Value | D04 | `open_po_value` | Sum | None |
| Vendors Requiring Review | D05 | `filter_vendor` | Count Distinct | `vendor_control_status` is RED or AMBER |
| Price Change Impact | D06 | `price_change_value_impact` | Sum | None |

Use INR formatting with zero decimals for value widgets.

## 5. Create the P1 Dashboard Filters

Create a new dashboard named `ABNAH DEMO - P1 Concise`.

1. Add the three P1 widgets.
2. Add `DEMO_P1_Action_Queue`, `DEMO_P1_Menu_Impact`, and
   `DEMO_P1_Expiry_Watch`.
3. In the **User Filters** area, clear **Auto Add User Filters**.
4. Do not enable **Show Report Specific User Filter** on any report.

Create exactly four dashboard controls:

| Display name | Primary column | Merge into the same control |
|---|---|---|
| Date Range | D01.`filter_date` | D02.`filter_date`, D03.`filter_date` |
| Outlet | D01.`filter_outlet` | D02.`filter_outlet`, D03.`filter_outlet` |
| Category | D01.`filter_category` | D02.`filter_category`, D03.`filter_category` |
| Severity | D01.`filter_severity` | D02.`filter_severity`, D03.`filter_severity` |

For each control:

1. Click **Add User Filters**.
2. Drag the primary column into the filter shelf.
3. For Date Range, choose the **Date Range** component.
4. Drag the corresponding D02 column onto the primary control.
5. Drag the corresponding D03 column onto the same control.
6. Click the control's **Edit** icon.
7. Click **Edit Column Mapping**.
8. Verify all three mapped columns appear once.
9. Click **OK**.

For each P1 report and widget:

1. Click its **More** icon.
2. Click **Options**.
3. Select **Apply Dashboard Filters**.
4. Clear **Show Report Specific User Filter**.
5. Click **Customize** beside Apply Dashboard Filters.
6. Map the four controls using the matrix below.
7. Click **Apply**.

| Object source | Date Range | Outlet | Category | Severity |
|---|---|---|---|---|
| D01 | `filter_date` | `filter_outlet` | `filter_category` | `filter_severity` |
| D02 | `filter_date` | `filter_outlet` | `filter_category` | `filter_severity` |
| D03 | `filter_date` | `filter_outlet` | `filter_category` | `filter_severity` |

## 6. Create the P2 Dashboard Filters

Create a new dashboard named `ABNAH DEMO - P2 Concise`.

1. Add the three P2 widgets.
2. Add `DEMO_P2_PO_Control`, `DEMO_P2_Vendor_Control`, and
   `DEMO_P2_Price_Watch`.
3. Clear **Auto Add User Filters**.
4. Do not enable **Show Report Specific User Filter**.

Create exactly four controls:

| Display name | Primary column | Merge into the same control |
|---|---|---|
| Date Range | D04.`filter_date` | D05.`filter_date`, D06.`filter_date` |
| Outlet | D04.`filter_outlet` | D05.`filter_outlet`, D06.`filter_outlet` |
| Vendor | D04.`filter_vendor` | D05.`filter_vendor`, D06.`filter_vendor` |
| Category | D04.`filter_category` | D05.`filter_category`, D06.`filter_category` |

For each control, repeat the nine merge-and-mapping clicks from Section 5.

For each P2 report and widget:

1. Click **More** > **Options**.
2. Select **Apply Dashboard Filters**.
3. Clear **Show Report Specific User Filter**.
4. Click **Customize**.
5. Map:

| Object source | Date Range | Outlet | Vendor | Category |
|---|---|---|---|---|
| D04 | `filter_date` | `filter_outlet` | `filter_vendor` | `filter_category` |
| D05 | `filter_date` | `filter_outlet` | `filter_vendor` | `filter_category` |
| D06 | `filter_date` | `filter_outlet` | `filter_vendor` | `filter_category` |

## 7. Conditional Formatting

Open each saved Tabular View in **View Mode**. Right-click a value in the
status column and click **Conditional Formatting**.

Use these exact colors:

| Status | Background | Font |
|---|---|---|
| PURPLE | `#6D28D9` | `#FFFFFF` |
| RED | `#DC2626` | `#FFFFFF` |
| AMBER | `#F59E0B` | `#111827` |
| GREEN | `#15803D` | `#FFFFFF` |
| GREY | `#64748B` | `#FFFFFF` |
| DELAYED / MISSING DATE | `#DC2626` | `#FFFFFF` |
| OPEN | `#F59E0B` | `#111827` |
| CLOSED | `#15803D` | `#FFFFFF` |

Format the following visible status fields:

- P1 Action Queue: `risk_severity`
- P1 Menu Impact: `risk_severity`
- P1 Expiry Watch: `filter_severity`
- P2 PO Control: `control_severity`
- P2 Vendor Control: `vendor_control_status`
- P2 Price Watch: `price_control_status`

## 8. Compact Layout

For each page:

1. Put the three KPI widgets in one top row.
2. Put the highest-priority table full width beneath the widgets.
3. Put the other two tables side by side beneath it.
4. Set each table to show 10 rows initially.
5. Do not add unused columns merely for hover detail.
6. Keep helper columns hidden from the visible table.

P1 priority table: `DEMO_P1_Action_Queue`.

P2 priority table: `DEMO_P2_PO_Control`.

## 9. Five-Minute Validation

1. Set Date Range to one visible source period.
2. Confirm all six objects on that page change.
3. Select one Outlet and confirm no duplicate Outlet filter appears.
4. Select one Category and confirm all page objects update.
5. On P1, select `RED` Severity and confirm expiry/menu/action tables respond.
6. On P2, select one Vendor and confirm all three tables respond.
7. Clear all filters and save.

If a report does not respond, open **More** > **Options** > **Customize** and
correct that report's mapping. Do not add a second user filter.

## 10. Evidence and Limits

- D01 and D02 repeat the validated Query 27/28 business logic without depending
  on those level-3 tables.
- D03 is explicitly estimated synthetic expiry evidence.
- D04-D06 use the same PO and receipt facts as the current procurement model.
- The 80% vendor threshold and 10% price threshold are visual-demo rules, not
  ABNAH-approved production policy.
- No lookup is required for this isolated sample.

Zoho references:

- Dashboard filter mapping:
  <https://www.zoho.com/analytics/help/dashboard/filter.html>
- Tabular conditional formatting:
  <https://help.zoho.com/portal/en/kb/analytics/user-guide/creating-reports/tabular-view/articles/customizing-a-tabular-view>
