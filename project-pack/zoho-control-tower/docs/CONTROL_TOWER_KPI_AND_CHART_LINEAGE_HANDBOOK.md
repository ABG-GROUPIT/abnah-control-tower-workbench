# ABNAH Control Tower KPI And Chart Lineage Handbook

## Purpose

Use this document when somebody asks where a KPI or chart came from, which POSIST fields support it, how the model joins them, and exactly how the final Zoho object is configured.

This is generated from `docs/control_tower_presentation_contract.json`. Update the contract through `scripts/build_control_tower_presentation.py`; do not hand-edit this generated handbook.

## Non-Negotiable Rules

- The dashboard runs on a three-month synthetic baseline, but its source field names and transformation pattern follow the captured POSIST report contracts.
- Expiry is always labelled as a synthetic demonstration because no enabled POSIST batch/expiry source exists.
- OTIF and lead-time deviation remain formula demonstrations until actual PO-to-GRN linkage improves.
- Current stock, risk, and working-capital widgets use exactly one source period.
- Quantities across kg, litre, and pieces are never added without one canonical UOM.
- Percentages are ratios of summed numerators and denominators, never averages of row percentages.

## Search Index

| Page | Object | Kind | Zoho visual | Final Query Table |
| ---: | --- | --- | --- | --- |
| 1 | [Risk Action Center](#ct-p1-action-center) | table | Tabular | `27_fact_ct_inventory_risk.sql` |
| 1 | [Expiry Risk Detail - Demo](#ct-p1-expiry-risk-detail-demo) | table | Tabular | `38_fact_ct_expiry_risk.sql` |
| 1 | [Expiry Risk Value - Demo Estimate](#ct-p1-kpi-expiry-risk-value-demo) | kpi | KPI widget | `38_fact_ct_expiry_risk.sql` |
| 1 | [Menu Items At Risk](#ct-p1-kpi-menu-items-at-risk) | kpi | KPI widget | `28_fact_ct_menu_impact.sql` |
| 1 | [Open Risky PO Count](#ct-p1-kpi-open-risky-po) | kpi | KPI widget | `36_fact_ct_risky_po.sql` |
| 1 | [Outlets At Stockout Risk](#ct-p1-kpi-outlets-at-stockout-risk) | kpi | KPI widget | `27_fact_ct_inventory_risk.sql` |
| 1 | [Stockout Sales At Risk](#ct-p1-kpi-stockout-risk-value) | kpi | KPI widget | `28_fact_ct_menu_impact.sql` |
| 1 | [Menu Impact Detail](#ct-p1-menu-impact-detail) | table | Tabular | `28_fact_ct_menu_impact.sql` |
| 1 | [Outlet Risk Map](#ct-p1-outlet-risk-map) | chart | Map | `27_fact_ct_inventory_risk.sql` |
| 1 | [Stockout Priority Stack](#ct-p1-stockout-priority-stack) | chart | Horizontal stacked bar | `27_fact_ct_inventory_risk.sql` |
| 1 | [Stockout Risk Detail](#ct-p1-stockout-risk-detail) | table | Tabular | `27_fact_ct_inventory_risk.sql` |
| 1 | [Vendor PO Risk](#ct-p1-vendor-po-risk) | table | Tabular | `36_fact_ct_risky_po.sql` |
| 2 | [Expected Delivery Breach](#ct-p2-expected-delivery-breach) | table | Tabular | `22_fact_ct_purchase_order.sql` |
| 2 | [Expiry Exposure - Demo](#ct-p2-expiry-exposure-demo) | chart | Column | `38_fact_ct_expiry_risk.sql` |
| 2 | [High Value / Slow Stock](#ct-p2-high-value-slow-stock) | table | Tabular | `27_fact_ct_inventory_risk.sql` |
| 2 | [Ingredient Price Trend](#ct-p2-ingredient-price-trend) | chart | Line | `23_fact_ct_purchase_receipt.sql` |
| 2 | [Inventory Value](#ct-p2-inventory-value) | chart | Stacked bar | `05_std_ct_inventory_snapshot.sql` |
| 2 | [Closing Inventory Value](#ct-p2-kpi-closing-inventory) | kpi | KPI widget | `33_sum_ct_scm_monthly.sql` |
| 2 | [PO Fill Rate](#ct-p2-kpi-fill-rate) | kpi | Saved Summary View | `24_fact_ct_po_receipt_line.sql` |
| 2 | [Ordered Gross Value](#ct-p2-kpi-monthly-purchase) | kpi | KPI widget | `29_sum_ct_procurement_funnel.sql` |
| 2 | [Vendor OTIF - Formula Demo](#ct-p2-kpi-otif) | kpi | Saved Summary View | `24_fact_ct_po_receipt_line.sql` |
| 2 | [Open PO Count](#ct-p2-kpi-open-po-count) | kpi | KPI widget | `29_sum_ct_procurement_funnel.sql` |
| 2 | [Open PO Liability](#ct-p2-kpi-open-po-liability) | kpi | KPI widget | `29_sum_ct_procurement_funnel.sql` |
| 2 | [Working Capital Locked](#ct-p2-kpi-working-capital) | kpi | KPI widget | `33_sum_ct_scm_monthly.sql` |
| 2 | [Observed Wastage](#ct-p2-observed-wastage) | chart | Column | `35_sum_ct_financial_leakage.sql` |
| 2 | [PO Status Distribution](#ct-p2-po-status-distribution) | chart | Stacked bar | `22_fact_ct_purchase_order.sql` |
| 2 | [Pending Value By Vendor](#ct-p2-pending-by-vendor) | chart | Horizontal bar | `29_sum_ct_procurement_funnel.sql` |
| 2 | [Pending Ingredient Risk](#ct-p2-pending-ingredient-risk) | table | Tabular | `36_fact_ct_risky_po.sql` |
| 2 | [Procurement Funnel](#ct-p2-procurement-funnel) | chart | Funnel or grouped horizontal bar | `29_sum_ct_procurement_funnel.sql` |
| 2 | [Top Price Movement](#ct-p2-top-price-movement) | chart | Divergent or horizontal bar | `31_sum_ct_price_movement.sql` |
| 2 | [Vendor Performance Matrix](#ct-p2-vendor-performance-matrix) | chart | Bubble | `24_fact_ct_po_receipt_line.sql` |
| 2 | [Vendor Price Comparison](#ct-p2-vendor-price-comparison) | chart | Grouped bar | `23_fact_ct_purchase_receipt.sql` |
| 2 | [Vendor Scorecard](#ct-p2-vendor-scorecard) | table | Summary or pivot | `24_fact_ct_po_receipt_line.sql` |
| 3 | [Actual vs Theoretical Consumption](#ct-p3-actual-vs-theoretical) | chart | Grouped bar | `21_fact_ct_consumption_variance.sql` |
| 3 | [Category Contribution](#ct-p3-category-contribution) | chart | Stacked bar or ring | `25_fact_ct_menu_profitability.sql` |
| 3 | [Consumption Bridge](#ct-p3-consumption-bridge) | chart | Combination | `20_fact_ct_actual_consumption.sql` |
| 3 | [Consumption Leakage Rank](#ct-p3-consumption-leakage-rank) | chart | Horizontal bar | `21_fact_ct_consumption_variance.sql` |
| 3 | [Consumption Leakage Value](#ct-p3-kpi-consumption-leakage) | kpi | KPI widget | `21_fact_ct_consumption_variance.sql` |
| 3 | [Menu Gross Margin %](#ct-p3-kpi-menu-gross-margin) | kpi | Saved Summary View | `25_fact_ct_menu_profitability.sql` |
| 3 | [Net Sales](#ct-p3-kpi-net-sales) | kpi | KPI widget | `25_fact_ct_menu_profitability.sql` |
| 3 | [Quantity Sold](#ct-p3-kpi-quantity-sold) | kpi | KPI widget | `25_fact_ct_menu_profitability.sql` |
| 3 | [Theoretical COGS](#ct-p3-kpi-theoretical-cogs) | kpi | KPI widget | `25_fact_ct_menu_profitability.sql` |
| 3 | [Low Consumption Check](#ct-p3-low-consumption-check) | table | Tabular | `21_fact_ct_consumption_variance.sql` |
| 3 | [Menu BCG](#ct-p3-menu-bcg) | chart | Bubble | `32_sum_ct_menu_profitability.sql` |
| 3 | [Menu COGS Detail](#ct-p3-menu-cogs-detail) | table | Tabular | `25_fact_ct_menu_profitability.sql` |
| 3 | [Menu Margin Rank](#ct-p3-menu-margin-rank) | chart | Horizontal bar | `32_sum_ct_menu_profitability.sql` |
| 3 | [Outlet Item Heatmap](#ct-p3-outlet-item-heatmap) | chart | Heat map | `25_fact_ct_menu_profitability.sql` |
| 3 | [Sales Trend](#ct-p3-sales-trend) | chart | Line | `18_fact_ct_sales.sql` |
| 3 | [Theoretical Consumption Detail](#ct-p3-theoretical-consumption-detail) | table | Tabular | `19_fact_ct_theoretical_consumption.sql` |
| 3 | [Top / Slow Menu Ranking](#ct-p3-top-slow-menu-ranking) | chart | Horizontal bar | `32_sum_ct_menu_profitability.sql` |
| 4 | [Consumption Variance Trend](#ct-p4-consumption-variance-trend) | chart | Bar / line | `21_fact_ct_consumption_variance.sql` |
| 4 | [Negative Stock Count](#ct-p4-dq-negative-stock) | kpi | KPI widget | `34_fact_ct_data_quality_exception.sql` |
| 4 | [Open PO Missing Expected Delivery Count](#ct-p4-dq-open-po-missing-expected-delivery) | kpi | KPI widget | `34_fact_ct_data_quality_exception.sql` |
| 4 | [Operational Items Missing Master Count](#ct-p4-dq-operational-item-missing-master) | kpi | KPI widget | `34_fact_ct_data_quality_exception.sql` |
| 4 | [Sold Items Missing Recipe Count](#ct-p4-dq-sold-item-missing-recipe) | kpi | KPI widget | `34_fact_ct_data_quality_exception.sql` |
| 4 | [UOM Mismatch Without Conversion Count](#ct-p4-dq-uom-mismatch-without-conversion) | kpi | KPI widget | `34_fact_ct_data_quality_exception.sql` |
| 4 | [Zero Stock With Demand Count](#ct-p4-dq-zero-stock-with-demand) | kpi | KPI widget | `34_fact_ct_data_quality_exception.sql` |
| 4 | [Data Quality Detail](#ct-p4-data-quality-detail) | table | Tabular | `34_fact_ct_data_quality_exception.sql` |
| 4 | [SCM Descriptive Explorer](#ct-p4-descriptive-explorer) | table | Pivot or tabular | `33_sum_ct_scm_monthly.sql` |
| 4 | [Expiry Explorer - Demo](#ct-p4-expiry-explorer-demo) | table | Tabular | `38_fact_ct_expiry_risk.sql` |
| 4 | [GRN Explorer](#ct-p4-grn-explorer) | table | Tabular | `23_fact_ct_purchase_receipt.sql` |
| 4 | [Item Explorer](#ct-p4-item-explorer) | table | Tabular | `27_fact_ct_inventory_risk.sql` |
| 4 | [Active Menu Items](#ct-p4-kpi-active-menu-items) | kpi | KPI widget | `18_fact_ct_sales.sql` |
| 4 | [Active Vendors](#ct-p4-kpi-active-vendors) | kpi | KPI widget | `22_fact_ct_purchase_order.sql` |
| 4 | [Actual Consumption Value](#ct-p4-kpi-actual-consumption) | kpi | KPI widget | `33_sum_ct_scm_monthly.sql` |
| 4 | [Closing Stock Value](#ct-p4-kpi-closing-stock) | kpi | KPI widget | `33_sum_ct_scm_monthly.sql` |
| 4 | [Signed Consumption Variance Value](#ct-p4-kpi-consumption-variance) | kpi | KPI widget | `21_fact_ct_consumption_variance.sql` |
| 4 | [GRN Value](#ct-p4-kpi-grn-value) | kpi | KPI widget | `23_fact_ct_purchase_receipt.sql` |
| 4 | [Net Sales](#ct-p4-kpi-net-sales) | kpi | KPI widget | `33_sum_ct_scm_monthly.sql` |
| 4 | [Open PO Value](#ct-p4-kpi-open-po) | kpi | KPI widget | `33_sum_ct_scm_monthly.sql` |
| 4 | [Open PO Line Count](#ct-p4-kpi-open-po-lines) | kpi | KPI widget | `22_fact_ct_purchase_order.sql` |
| 4 | [Quantity Sold](#ct-p4-kpi-quantity-sold) | kpi | KPI widget | `18_fact_ct_sales.sql` |
| 4 | [PO Explorer](#ct-p4-po-explorer) | table | Tabular | `24_fact_ct_po_receipt_line.sql` |
| 4 | [SCM Monthly Trend](#ct-p4-scm-monthly-trend) | chart | Combination | `33_sum_ct_scm_monthly.sql` |
| 4 | [Sales Explorer](#ct-p4-sales-explorer) | table | Tabular | `18_fact_ct_sales.sql` |
| 4 | [Vendor Explorer](#ct-p4-vendor-explorer) | table | Tabular | `30_sum_ct_vendor_scorecard.sql` |

# Page 1 - Risk Action Center

Show what needs action now across stockout, menu impact, expiry demonstration, and linked open purchase orders.

<a id="ct-p1-action-center"></a>
## CT_P1_Action_Center - Risk Action Center

**Business question:** What exact stockout action, owner, and due band should operations see?

**Final object:** table / Tabular from `27_fact_ct_inventory_risk.sql`

**Final grain:** Source period, outlet, and inventory ingredient checkpoint

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Closing Stock Report | captured_posist_report | Current quantity, average cost, and closing valuation evidence | `Deployment`, `Date`, `Generation Date`, `Item Code`, `Item Name`, `Category Name`, `Unit Name`, `Average Price`, `Total Qty`, `Total Amt` |
| Item Recipe Report | captured_posist_report | Menu-to-ingredient conversion | `Item Number`, `Qty`, `Recipe Unit`, `Ingredient Code`, `Ingredient Name` |
| AUX Menu Demand Forecast | synthetic_model_input | Synthetic seven-day menu demand and net-sales forecast | `source_period_code`, `outlet_code`, `menu_item_code`, `forecast_menu_qty`, `forecast_net_sales` |
| Enterprise Purchase Order Report | captured_posist_report | Ordered, processed, remaining, expected-date, status, and commitment-value evidence | `Deployment`, `Store Name`, `Vendor Name`, `PO Number`, `PO Date`, `Expected Delivery`, `PO Close Date/Partial Recieve Date`, `PO Status`, `Item Code`, `Item Name`, `Total Processed Qty`, `Remaining Balance Qty`, `Quantity`, `Unit`, `Unit Price`, `Total Item Cost` |

### Model Route And Relationship

`05_std_ct_inventory_snapshot.sql -> 26_fact_ct_forecast_ingredient_demand.sql -> 22_fact_ct_purchase_order.sql -> 27_fact_ct_inventory_risk.sql`

**Join/relationship logic:** Join stock, seven-day forecast ingredient demand, and valid open PO quantity on source period + outlet + item.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `item_code -> 14_dim_ct_item.sql.item_code`

### Calculation

**Final fields:** `action_id`, `outlet_code`, `item_code`, `risk_severity`, `shortage_qty`, `recommended_action`, `action_owner`, `due_band`, `total_risk_value`

**Formula:** `Direct fact fields; no dashboard-only calculation.`

**Aggregation:** One row per risk action

### Exact Zoho Configuration

**Visual:** Tabular

**Shelves/columns:**

- Columns: action ID, outlet, item, severity, shortage, recommended action, owner, due band

**Fixed report filters:**

- Filter shelf: risk_type / Individual Values / Include STOCKOUT

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- New/matured
- Risk severity
- Action owner
- Ingredient category

**Sort:** risk_severity_rank descending, total_risk_value descending, due_band ascending

**Tooltips:**

- None

**Formatting:**

- Conditional format severity with approved RAG palette
- Enable View Underlying Data

### Guardrails

- The 15% safety factor is a demo rule pending ABNAH approval.
- Query 27 covers stockout exposure only; expiry is separate.

### How To Explain It

Risk Action Center starts from Closing Stock Report, Item Recipe Report, AUX Menu Demand Forecast, Enterprise Purchase Order Report. The model follows 05_std_ct_inventory_snapshot.sql -> 26_fact_ct_forecast_ingredient_demand.sql -> 22_fact_ct_purchase_order.sql -> 27_fact_ct_inventory_risk.sql at source period, outlet, and inventory ingredient checkpoint. The relationship rule is: Join stock, seven-day forecast ingredient demand, and valid open PO quantity on source period + outlet + item. In Zoho, use one row per risk action and render it as tabular to answer: What exact stockout action, owner, and due band should operations see?

<a id="ct-p1-expiry-risk-detail-demo"></a>
## CT_P1_Expiry_Risk_Detail_Demo - Expiry Risk Detail - Demo

**Business question:** How does the synthetic expiry scenario trace each at-risk FIFO tranche?

**Final object:** table / Tabular from `38_fact_ct_expiry_risk.sql`

**Final grain:** Source period, outlet, synthetic batch allocation, and item

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Enterprise Entry Report - Stock Entry | captured_posist_report | Receipt date, GRN, PO, vendor, quantity, and cost pattern used for traceable demo tranches | `Date`, `Transaction Number`, `PO Number`, `Vendor Name`, `Item Code`, `Item Name`, `Quantity`, `Unit`, `Unit Price` |
| Closing Stock Report | captured_posist_report | Current item quantity and average-cost boundary | `Date`, `Item Code`, `Item Name`, `Unit Name`, `Average Price`, `Total Qty` |
| AUX Expiry Estimate | synthetic_model_input | Synthetic FIFO tranche and shelf-life scenario; not a POSIST batch or expiry source | `batch_allocation_id`, `receipt_date`, `estimated_expiry_date`, `expiry_qty_at_risk`, `expiry_risk_value`, `production_use_status` |

### Model Route And Relationship

`AUX_Expiry_Estimate-Copy -> 38_fact_ct_expiry_risk.sql`

**Join/relationship logic:** Expose the prebuilt synthetic FIFO/shelf-life scenario with permanent evidence and production-use labels.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `item_code -> 14_dim_ct_item.sql.item_code`

### Calculation

**Final fields:** `batch_allocation_id`, `receipt_date`, `grn_number`, `po_number`, `vendor_name`, `item_closing_qty`, `estimated_fifo_tranche_qty`, `expected_consumption_before_expiry`, `expiry_qty_at_risk`, `expiry_risk_value`, `estimated_expiry_date`, `risk_severity`, `estimation_method`

**Formula:** `Scenario output is already calculated in AUX_Expiry_Estimate-Copy.`

**Aggregation:** One row per synthetic batch allocation

### Exact Zoho Configuration

**Visual:** Tabular

**Shelves/columns:**

- Columns: traceability, scenario inputs, at-risk quantity/value, estimated date, severity, method

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- New/matured
- Risk severity
- Action owner
- Ingredient category

**Sort:** risk_severity_rank descending, expiry_risk_value descending

**Tooltips:**

- None

**Formatting:**

- Permanent synthetic-source qualifier

### Guardrails

- Every title or subtitle must say Synthetic demo estimate - no POSIST batch/expiry source.
- Do not present the scenario as actual batch ageing or expiry truth.

### How To Explain It

Expiry Risk Detail - Demo starts from Enterprise Entry Report - Stock Entry, Closing Stock Report, AUX Expiry Estimate. The model follows AUX_Expiry_Estimate-Copy -> 38_fact_ct_expiry_risk.sql at source period, outlet, synthetic batch allocation, and item. The relationship rule is: Expose the prebuilt synthetic FIFO/shelf-life scenario with permanent evidence and production-use labels. In Zoho, use one row per synthetic batch allocation and render it as tabular to answer: How does the synthetic expiry scenario trace each at-risk FIFO tranche?

<a id="ct-p1-kpi-expiry-risk-value-demo"></a>
## CT_P1_KPI_Expiry_Risk_Value_Demo - Expiry Risk Value - Demo Estimate

**Business question:** What value is exposed in the synthetic FIFO and shelf-life scenario?

**Final object:** kpi / KPI widget from `38_fact_ct_expiry_risk.sql`

**Final grain:** Source period, outlet, synthetic batch allocation, and item

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Enterprise Entry Report - Stock Entry | captured_posist_report | Receipt date, GRN, PO, vendor, quantity, and cost pattern used for traceable demo tranches | `Date`, `Transaction Number`, `PO Number`, `Vendor Name`, `Item Code`, `Item Name`, `Quantity`, `Unit`, `Unit Price` |
| Closing Stock Report | captured_posist_report | Current item quantity and average-cost boundary | `Date`, `Item Code`, `Item Name`, `Unit Name`, `Average Price`, `Total Qty` |
| AUX Expiry Estimate | synthetic_model_input | Synthetic FIFO tranche and shelf-life scenario; not a POSIST batch or expiry source | `batch_allocation_id`, `receipt_date`, `estimated_expiry_date`, `expiry_qty_at_risk`, `expiry_risk_value`, `production_use_status` |

### Model Route And Relationship

`AUX_Expiry_Estimate-Copy -> 38_fact_ct_expiry_risk.sql`

**Join/relationship logic:** Expose the prebuilt synthetic FIFO/shelf-life scenario with permanent evidence and production-use labels.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `item_code -> 14_dim_ct_item.sql.item_code`

### Calculation

**Final fields:** `expiry_risk_value`, `production_use_status`, `is_estimated`

**Formula:** `sum("expiry_risk_value")`

**Aggregation:** Sum expiry risk value

### Exact Zoho Configuration

**Visual:** KPI widget

**Shelves/columns:**

- Data Column: expiry_risk_value
- Show Value As: Sum
- Group By: blank

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- New/matured
- Risk severity
- Action owner
- Ingredient category

**Sort:** Business-relevant default order

**Tooltips:**

- None

**Formatting:**

- INR currency
- Subtitle: Synthetic estimate - no POSIST batch/expiry source

### Guardrails

- Every title or subtitle must say Synthetic demo estimate - no POSIST batch/expiry source.
- Do not present the scenario as actual batch ageing or expiry truth.

### How To Explain It

Expiry Risk Value - Demo Estimate starts from Enterprise Entry Report - Stock Entry, Closing Stock Report, AUX Expiry Estimate. The model follows AUX_Expiry_Estimate-Copy -> 38_fact_ct_expiry_risk.sql at source period, outlet, synthetic batch allocation, and item. The relationship rule is: Expose the prebuilt synthetic FIFO/shelf-life scenario with permanent evidence and production-use labels. In Zoho, use sum expiry risk value and render it as kpi widget to answer: What value is exposed in the synthetic FIFO and shelf-life scenario?

<a id="ct-p1-kpi-menu-items-at-risk"></a>
## CT_P1_KPI_Menu_Items_At_Risk - Menu Items At Risk

**Business question:** How many menu items depend on ingredients that cannot meet the forecast requirement?

**Final object:** kpi / KPI widget from `28_fact_ct_menu_impact.sql`

**Final grain:** Source period, outlet, risky ingredient, and impacted menu item

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Closing Stock Report | captured_posist_report | Current quantity, average cost, and closing valuation evidence | `Deployment`, `Date`, `Generation Date`, `Item Code`, `Item Name`, `Category Name`, `Unit Name`, `Average Price`, `Total Qty`, `Total Amt` |
| Item Recipe Report | captured_posist_report | Menu-to-ingredient conversion | `Item Number`, `Qty`, `Recipe Unit`, `Ingredient Code`, `Ingredient Name` |
| AUX Menu Demand Forecast | synthetic_model_input | Synthetic seven-day menu demand and net-sales forecast | `source_period_code`, `outlet_code`, `menu_item_code`, `forecast_menu_qty`, `forecast_net_sales` |
| Enterprise Purchase Order Report | captured_posist_report | Ordered, processed, remaining, expected-date, status, and commitment-value evidence | `Deployment`, `Store Name`, `Vendor Name`, `PO Number`, `PO Date`, `Expected Delivery`, `PO Close Date/Partial Recieve Date`, `PO Status`, `Item Code`, `Item Name`, `Total Processed Qty`, `Remaining Balance Qty`, `Quantity`, `Unit`, `Unit Price`, `Total Item Cost` |

### Model Route And Relationship

`05_std_ct_inventory_snapshot.sql -> 26_fact_ct_forecast_ingredient_demand.sql -> 22_fact_ct_purchase_order.sql -> 28_fact_ct_menu_impact.sql`

**Join/relationship logic:** Identify shortage ingredients, connect them to forecast menu items, and allocate each menu item's forecast sales across its risky ingredients.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `ingredient_code -> 14_dim_ct_item.sql.item_code`
- `menu_item_code -> 15_dim_ct_menu_item.sql.menu_item_code`

### Calculation

**Final fields:** `menu_item_code`, `shortage_qty`, `risk_severity`

**Formula:** `distinctcount("menu_item_code")`

**Aggregation:** Distinct count of menu_item_code

### Exact Zoho Configuration

**Visual:** KPI widget

**Shelves/columns:**

- Data Column: menu_item_code
- Show Value As: Count Distinct
- Group By: blank

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- New/matured
- Risk severity
- Action owner
- Ingredient category

**Sort:** Business-relevant default order

**Tooltips:**

- None

**Formatting:**

- Whole number

### Guardrails

- Sum allocated_forecast_net_sales_at_risk, not the repeating unallocated forecast value.
- Only risk rows are retained.

### How To Explain It

Menu Items At Risk starts from Closing Stock Report, Item Recipe Report, AUX Menu Demand Forecast, Enterprise Purchase Order Report. The model follows 05_std_ct_inventory_snapshot.sql -> 26_fact_ct_forecast_ingredient_demand.sql -> 22_fact_ct_purchase_order.sql -> 28_fact_ct_menu_impact.sql at source period, outlet, risky ingredient, and impacted menu item. The relationship rule is: Identify shortage ingredients, connect them to forecast menu items, and allocate each menu item's forecast sales across its risky ingredients. In Zoho, use distinct count of menu_item_code and render it as kpi widget to answer: How many menu items depend on ingredients that cannot meet the forecast requirement?

<a id="ct-p1-kpi-open-risky-po"></a>
## CT_P1_KPI_Open_Risky_PO - Open Risky PO Count

**Business question:** How many distinct open POs relate to ingredients already in a stockout-risk state?

**Final object:** kpi / KPI widget from `36_fact_ct_risky_po.sql`

**Final grain:** Source period, outlet, open PO, and risky item line

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Closing Stock Report | captured_posist_report | Current quantity, average cost, and closing valuation evidence | `Deployment`, `Date`, `Generation Date`, `Item Code`, `Item Name`, `Category Name`, `Unit Name`, `Average Price`, `Total Qty`, `Total Amt` |
| Item Recipe Report | captured_posist_report | Menu-to-ingredient conversion | `Item Number`, `Qty`, `Recipe Unit`, `Ingredient Code`, `Ingredient Name` |
| AUX Menu Demand Forecast | synthetic_model_input | Synthetic seven-day menu demand and net-sales forecast | `source_period_code`, `outlet_code`, `menu_item_code`, `forecast_menu_qty`, `forecast_net_sales` |
| Enterprise Purchase Order Report | captured_posist_report | Ordered, processed, remaining, expected-date, status, and commitment-value evidence | `Deployment`, `Store Name`, `Vendor Name`, `PO Number`, `PO Date`, `Expected Delivery`, `PO Close Date/Partial Recieve Date`, `PO Status`, `Item Code`, `Item Name`, `Total Processed Qty`, `Remaining Balance Qty`, `Quantity`, `Unit`, `Unit Price`, `Total Item Cost` |

### Model Route And Relationship

`05_std_ct_inventory_snapshot.sql -> 26_fact_ct_forecast_ingredient_demand.sql -> 22_fact_ct_purchase_order.sql -> 36_fact_ct_risky_po.sql`

**Join/relationship logic:** Retain open PO lines only where the matching item checkpoint is purple, red, or amber.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `item_code -> 14_dim_ct_item.sql.item_code`
- `vendor_name -> 16_dim_ct_vendor.sql.vendor_name`

### Calculation

**Final fields:** `po_number`, `risk_severity`, `open_po_value`

**Formula:** `distinctcount("po_number")`

**Aggregation:** Distinct count of PO number

### Exact Zoho Configuration

**Visual:** KPI widget

**Shelves/columns:**

- Data Column: po_number
- Show Value As: Count Distinct
- Group By: blank

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- New/matured
- Risk severity
- Action owner
- Ingredient category

**Sort:** Business-relevant default order

**Tooltips:**

- None

**Formatting:**

- Whole number

### Guardrails

- Count distinct PO number, not rows.
- Open PO quantity may reduce shortage risk but does not guarantee on-time receipt.

### How To Explain It

Open Risky PO Count starts from Closing Stock Report, Item Recipe Report, AUX Menu Demand Forecast, Enterprise Purchase Order Report. The model follows 05_std_ct_inventory_snapshot.sql -> 26_fact_ct_forecast_ingredient_demand.sql -> 22_fact_ct_purchase_order.sql -> 36_fact_ct_risky_po.sql at source period, outlet, open po, and risky item line. The relationship rule is: Retain open PO lines only where the matching item checkpoint is purple, red, or amber. In Zoho, use distinct count of po number and render it as kpi widget to answer: How many distinct open POs relate to ingredients already in a stockout-risk state?

<a id="ct-p1-kpi-outlets-at-stockout-risk"></a>
## CT_P1_KPI_Outlets_At_Stockout_Risk - Outlets At Stockout Risk

**Business question:** How many outlets require stockout action in the selected checkpoint?

**Final object:** kpi / KPI widget from `27_fact_ct_inventory_risk.sql`

**Final grain:** Source period, outlet, and inventory ingredient checkpoint

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Closing Stock Report | captured_posist_report | Current quantity, average cost, and closing valuation evidence | `Deployment`, `Date`, `Generation Date`, `Item Code`, `Item Name`, `Category Name`, `Unit Name`, `Average Price`, `Total Qty`, `Total Amt` |
| Item Recipe Report | captured_posist_report | Menu-to-ingredient conversion | `Item Number`, `Qty`, `Recipe Unit`, `Ingredient Code`, `Ingredient Name` |
| AUX Menu Demand Forecast | synthetic_model_input | Synthetic seven-day menu demand and net-sales forecast | `source_period_code`, `outlet_code`, `menu_item_code`, `forecast_menu_qty`, `forecast_net_sales` |
| Enterprise Purchase Order Report | captured_posist_report | Ordered, processed, remaining, expected-date, status, and commitment-value evidence | `Deployment`, `Store Name`, `Vendor Name`, `PO Number`, `PO Date`, `Expected Delivery`, `PO Close Date/Partial Recieve Date`, `PO Status`, `Item Code`, `Item Name`, `Total Processed Qty`, `Remaining Balance Qty`, `Quantity`, `Unit`, `Unit Price`, `Total Item Cost` |

### Model Route And Relationship

`05_std_ct_inventory_snapshot.sql -> 26_fact_ct_forecast_ingredient_demand.sql -> 22_fact_ct_purchase_order.sql -> 27_fact_ct_inventory_risk.sql`

**Join/relationship logic:** Join stock, seven-day forecast ingredient demand, and valid open PO quantity on source period + outlet + item.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `item_code -> 14_dim_ct_item.sql.item_code`

### Calculation

**Final fields:** `outlet_code`, `risk_type`

**Formula:** `Direct KPI Data Column "outlet_code"; Show Value As Count Distinct.`

**Aggregation:** Distinct count of physical outlet_code

### Exact Zoho Configuration

**Visual:** KPI widget

**Shelves/columns:**

- Data Column: outlet_code
- Show Value As: Count Distinct
- Group By: blank

**Fixed report filters:**

- Filter shelf: risk_type / Individual Values / Include STOCKOUT

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- New/matured
- Risk severity
- Action owner
- Ingredient category

**Sort:** Business-relevant default order

**Tooltips:**

- None

**Formatting:**

- Whole number

### Guardrails

- The 15% safety factor is a demo rule pending ABNAH approval.
- Query 27 covers stockout exposure only; expiry is separate.

### How To Explain It

Outlets At Stockout Risk starts from Closing Stock Report, Item Recipe Report, AUX Menu Demand Forecast, Enterprise Purchase Order Report. The model follows 05_std_ct_inventory_snapshot.sql -> 26_fact_ct_forecast_ingredient_demand.sql -> 22_fact_ct_purchase_order.sql -> 27_fact_ct_inventory_risk.sql at source period, outlet, and inventory ingredient checkpoint. The relationship rule is: Join stock, seven-day forecast ingredient demand, and valid open PO quantity on source period + outlet + item. In Zoho, use distinct count of physical outlet_code and render it as kpi widget to answer: How many outlets require stockout action in the selected checkpoint?

<a id="ct-p1-kpi-stockout-risk-value"></a>
## CT_P1_KPI_Stockout_Risk_Value - Stockout Sales At Risk

**Business question:** How much forecast menu revenue is allocated to current ingredient shortages?

**Final object:** kpi / KPI widget from `28_fact_ct_menu_impact.sql`

**Final grain:** Source period, outlet, risky ingredient, and impacted menu item

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Closing Stock Report | captured_posist_report | Current quantity, average cost, and closing valuation evidence | `Deployment`, `Date`, `Generation Date`, `Item Code`, `Item Name`, `Category Name`, `Unit Name`, `Average Price`, `Total Qty`, `Total Amt` |
| Item Recipe Report | captured_posist_report | Menu-to-ingredient conversion | `Item Number`, `Qty`, `Recipe Unit`, `Ingredient Code`, `Ingredient Name` |
| AUX Menu Demand Forecast | synthetic_model_input | Synthetic seven-day menu demand and net-sales forecast | `source_period_code`, `outlet_code`, `menu_item_code`, `forecast_menu_qty`, `forecast_net_sales` |
| Enterprise Purchase Order Report | captured_posist_report | Ordered, processed, remaining, expected-date, status, and commitment-value evidence | `Deployment`, `Store Name`, `Vendor Name`, `PO Number`, `PO Date`, `Expected Delivery`, `PO Close Date/Partial Recieve Date`, `PO Status`, `Item Code`, `Item Name`, `Total Processed Qty`, `Remaining Balance Qty`, `Quantity`, `Unit`, `Unit Price`, `Total Item Cost` |

### Model Route And Relationship

`05_std_ct_inventory_snapshot.sql -> 26_fact_ct_forecast_ingredient_demand.sql -> 22_fact_ct_purchase_order.sql -> 28_fact_ct_menu_impact.sql`

**Join/relationship logic:** Identify shortage ingredients, connect them to forecast menu items, and allocate each menu item's forecast sales across its risky ingredients.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `ingredient_code -> 14_dim_ct_item.sql.item_code`
- `menu_item_code -> 15_dim_ct_menu_item.sql.menu_item_code`

### Calculation

**Final fields:** `shortage_qty`, `allocated_forecast_net_sales_at_risk`

**Formula:** `sum("allocated_forecast_net_sales_at_risk")`

**Aggregation:** Sum allocated forecast net sales at risk

### Exact Zoho Configuration

**Visual:** KPI widget

**Shelves/columns:**

- Data Column: allocated_forecast_net_sales_at_risk
- Show Value As: Sum
- Group By: blank

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- New/matured
- Risk severity
- Action owner
- Ingredient category

**Sort:** Business-relevant default order

**Tooltips:**

- None

**Formatting:**

- INR currency
- Compact notation

### Guardrails

- Sum allocated_forecast_net_sales_at_risk, not the repeating unallocated forecast value.
- Only risk rows are retained.
- Never sum forecast_net_sales_at_risk because it repeats for multi-ingredient menu items.

### How To Explain It

Stockout Sales At Risk starts from Closing Stock Report, Item Recipe Report, AUX Menu Demand Forecast, Enterprise Purchase Order Report. The model follows 05_std_ct_inventory_snapshot.sql -> 26_fact_ct_forecast_ingredient_demand.sql -> 22_fact_ct_purchase_order.sql -> 28_fact_ct_menu_impact.sql at source period, outlet, risky ingredient, and impacted menu item. The relationship rule is: Identify shortage ingredients, connect them to forecast menu items, and allocate each menu item's forecast sales across its risky ingredients. In Zoho, use sum allocated forecast net sales at risk and render it as kpi widget to answer: How much forecast menu revenue is allocated to current ingredient shortages?

<a id="ct-p1-menu-impact-detail"></a>
## CT_P1_Menu_Impact_Detail - Menu Impact Detail

**Business question:** Which menu items and forecast sales are exposed by each risky ingredient?

**Final object:** table / Tabular from `28_fact_ct_menu_impact.sql`

**Final grain:** Source period, outlet, risky ingredient, and impacted menu item

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Closing Stock Report | captured_posist_report | Current quantity, average cost, and closing valuation evidence | `Deployment`, `Date`, `Generation Date`, `Item Code`, `Item Name`, `Category Name`, `Unit Name`, `Average Price`, `Total Qty`, `Total Amt` |
| Item Recipe Report | captured_posist_report | Menu-to-ingredient conversion | `Item Number`, `Qty`, `Recipe Unit`, `Ingredient Code`, `Ingredient Name` |
| AUX Menu Demand Forecast | synthetic_model_input | Synthetic seven-day menu demand and net-sales forecast | `source_period_code`, `outlet_code`, `menu_item_code`, `forecast_menu_qty`, `forecast_net_sales` |
| Enterprise Purchase Order Report | captured_posist_report | Ordered, processed, remaining, expected-date, status, and commitment-value evidence | `Deployment`, `Store Name`, `Vendor Name`, `PO Number`, `PO Date`, `Expected Delivery`, `PO Close Date/Partial Recieve Date`, `PO Status`, `Item Code`, `Item Name`, `Total Processed Qty`, `Remaining Balance Qty`, `Quantity`, `Unit`, `Unit Price`, `Total Item Cost` |

### Model Route And Relationship

`05_std_ct_inventory_snapshot.sql -> 26_fact_ct_forecast_ingredient_demand.sql -> 22_fact_ct_purchase_order.sql -> 28_fact_ct_menu_impact.sql`

**Join/relationship logic:** Identify shortage ingredients, connect them to forecast menu items, and allocate each menu item's forecast sales across its risky ingredients.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `ingredient_code -> 14_dim_ct_item.sql.item_code`
- `menu_item_code -> 15_dim_ct_menu_item.sql.menu_item_code`

### Calculation

**Final fields:** `ingredient_code`, `menu_item_code`, `risk_severity`, `forecast_menu_qty`, `allocated_forecast_net_sales_at_risk`

**Formula:** `Allocated sales at risk = forecast menu sales / count of risky ingredients for that menu item.`

**Aggregation:** Direct rows; sum only the allocated value

### Exact Zoho Configuration

**Visual:** Tabular

**Shelves/columns:**

- Columns: ingredient, menu item, severity, forecast menu quantity, allocated sales at risk

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- New/matured
- Risk severity
- Action owner
- Ingredient category

**Sort:** Allocated sales at risk descending

**Tooltips:**

- None

**Formatting:**

- None

### Guardrails

- Sum allocated_forecast_net_sales_at_risk, not the repeating unallocated forecast value.
- Only risk rows are retained.

### How To Explain It

Menu Impact Detail starts from Closing Stock Report, Item Recipe Report, AUX Menu Demand Forecast, Enterprise Purchase Order Report. The model follows 05_std_ct_inventory_snapshot.sql -> 26_fact_ct_forecast_ingredient_demand.sql -> 22_fact_ct_purchase_order.sql -> 28_fact_ct_menu_impact.sql at source period, outlet, risky ingredient, and impacted menu item. The relationship rule is: Identify shortage ingredients, connect them to forecast menu items, and allocate each menu item's forecast sales across its risky ingredients. In Zoho, use direct rows; sum only the allocated value and render it as tabular to answer: Which menu items and forecast sales are exposed by each risky ingredient?

<a id="ct-p1-outlet-risk-map"></a>
## CT_P1_Outlet_Risk_Map - Outlet Risk Map

**Business question:** Where are stockout-risk outlets located and how severe is their highest current risk?

**Final object:** chart / Map from `27_fact_ct_inventory_risk.sql`

**Final grain:** Source period, outlet, and inventory ingredient checkpoint

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Closing Stock Report | captured_posist_report | Current quantity, average cost, and closing valuation evidence | `Deployment`, `Date`, `Generation Date`, `Item Code`, `Item Name`, `Category Name`, `Unit Name`, `Average Price`, `Total Qty`, `Total Amt` |
| Item Recipe Report | captured_posist_report | Menu-to-ingredient conversion | `Item Number`, `Qty`, `Recipe Unit`, `Ingredient Code`, `Ingredient Name` |
| AUX Menu Demand Forecast | synthetic_model_input | Synthetic seven-day menu demand and net-sales forecast | `source_period_code`, `outlet_code`, `menu_item_code`, `forecast_menu_qty`, `forecast_net_sales` |
| Enterprise Purchase Order Report | captured_posist_report | Ordered, processed, remaining, expected-date, status, and commitment-value evidence | `Deployment`, `Store Name`, `Vendor Name`, `PO Number`, `PO Date`, `Expected Delivery`, `PO Close Date/Partial Recieve Date`, `PO Status`, `Item Code`, `Item Name`, `Total Processed Qty`, `Remaining Balance Qty`, `Quantity`, `Unit`, `Unit Price`, `Total Item Cost` |

### Model Route And Relationship

`05_std_ct_inventory_snapshot.sql -> 26_fact_ct_forecast_ingredient_demand.sql -> 22_fact_ct_purchase_order.sql -> 27_fact_ct_inventory_risk.sql`

**Join/relationship logic:** Join stock, seven-day forecast ingredient demand, and valid open PO quantity on source period + outlet + item.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `item_code -> 14_dim_ct_item.sql.item_code`

### Calculation

**Final fields:** `outlet_code`, `risk_severity_rank`, `shortage_cost_value`, `days_cover`

**Formula:** `Maximum risk severity rank by outlet; supporting values remain additive or distinct at outlet scope.`

**Aggregation:** Max severity rank, distinct risk items, sum shortage cost

### Exact Zoho Configuration

**Visual:** Map

**Shelves/columns:**

- Location: outlet via 37_dim_ct_outlet_enriched.sql
- Latitude/longitude: enriched outlet fields
- Color: max risk_severity_rank

**Fixed report filters:**

- Filter shelf: risk_type / Individual Values / Include STOCKOUT

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- New/matured
- Risk severity
- Action owner
- Ingredient category

**Sort:** Business-relevant default order

**Tooltips:**

- Outlet
- Distinct risk item count
- Shortage cost
- Days cover
- Maximum severity

**Formatting:**

- None

### Guardrails

- The 15% safety factor is a demo rule pending ABNAH approval.
- Query 27 covers stockout exposure only; expiry is separate.
- Synthetic geography must be replaced by an approved ABNAH outlet reference for production.

### How To Explain It

Outlet Risk Map starts from Closing Stock Report, Item Recipe Report, AUX Menu Demand Forecast, Enterprise Purchase Order Report. The model follows 05_std_ct_inventory_snapshot.sql -> 26_fact_ct_forecast_ingredient_demand.sql -> 22_fact_ct_purchase_order.sql -> 27_fact_ct_inventory_risk.sql at source period, outlet, and inventory ingredient checkpoint. The relationship rule is: Join stock, seven-day forecast ingredient demand, and valid open PO quantity on source period + outlet + item. In Zoho, use max severity rank, distinct risk items, sum shortage cost and render it as map to answer: Where are stockout-risk outlets located and how severe is their highest current risk?

<a id="ct-p1-stockout-priority-stack"></a>
## CT_P1_Stockout_Priority_Stack - Stockout Priority Stack

**Business question:** Which outlets carry the largest shortage-cost exposure by severity?

**Final object:** chart / Horizontal stacked bar from `27_fact_ct_inventory_risk.sql`

**Final grain:** Source period, outlet, and inventory ingredient checkpoint

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Closing Stock Report | captured_posist_report | Current quantity, average cost, and closing valuation evidence | `Deployment`, `Date`, `Generation Date`, `Item Code`, `Item Name`, `Category Name`, `Unit Name`, `Average Price`, `Total Qty`, `Total Amt` |
| Item Recipe Report | captured_posist_report | Menu-to-ingredient conversion | `Item Number`, `Qty`, `Recipe Unit`, `Ingredient Code`, `Ingredient Name` |
| AUX Menu Demand Forecast | synthetic_model_input | Synthetic seven-day menu demand and net-sales forecast | `source_period_code`, `outlet_code`, `menu_item_code`, `forecast_menu_qty`, `forecast_net_sales` |
| Enterprise Purchase Order Report | captured_posist_report | Ordered, processed, remaining, expected-date, status, and commitment-value evidence | `Deployment`, `Store Name`, `Vendor Name`, `PO Number`, `PO Date`, `Expected Delivery`, `PO Close Date/Partial Recieve Date`, `PO Status`, `Item Code`, `Item Name`, `Total Processed Qty`, `Remaining Balance Qty`, `Quantity`, `Unit`, `Unit Price`, `Total Item Cost` |

### Model Route And Relationship

`05_std_ct_inventory_snapshot.sql -> 26_fact_ct_forecast_ingredient_demand.sql -> 22_fact_ct_purchase_order.sql -> 27_fact_ct_inventory_risk.sql`

**Join/relationship logic:** Join stock, seven-day forecast ingredient demand, and valid open PO quantity on source period + outlet + item.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `item_code -> 14_dim_ct_item.sql.item_code`

### Calculation

**Final fields:** `outlet_code`, `shortage_cost_value`, `risk_severity`, `risk_severity_rank`

**Formula:** `sum("shortage_cost_value")`

**Aggregation:** Sum shortage cost value

### Exact Zoho Configuration

**Visual:** Horizontal stacked bar

**Shelves/columns:**

- Y: outlet
- X: shortage cost value
- Color: risk severity

**Fixed report filters:**

- Filter shelf: risk_type / Individual Values / Include STOCKOUT

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- New/matured
- Risk severity
- Action owner
- Ingredient category

**Sort:** Risk severity rank descending, then shortage cost descending

**Tooltips:**

- Item count
- Shortage quantity
- Days cover

**Formatting:**

- RAG palette only for severity

### Guardrails

- The 15% safety factor is a demo rule pending ABNAH approval.
- Query 27 covers stockout exposure only; expiry is separate.

### How To Explain It

Stockout Priority Stack starts from Closing Stock Report, Item Recipe Report, AUX Menu Demand Forecast, Enterprise Purchase Order Report. The model follows 05_std_ct_inventory_snapshot.sql -> 26_fact_ct_forecast_ingredient_demand.sql -> 22_fact_ct_purchase_order.sql -> 27_fact_ct_inventory_risk.sql at source period, outlet, and inventory ingredient checkpoint. The relationship rule is: Join stock, seven-day forecast ingredient demand, and valid open PO quantity on source period + outlet + item. In Zoho, use sum shortage cost value and render it as horizontal stacked bar to answer: Which outlets carry the largest shortage-cost exposure by severity?

<a id="ct-p1-stockout-risk-detail"></a>
## CT_P1_Stockout_Risk_Detail - Stockout Risk Detail

**Business question:** Which stock, forecast, safety, inbound, and cost inputs created each shortage?

**Final object:** table / Tabular from `27_fact_ct_inventory_risk.sql`

**Final grain:** Source period, outlet, and inventory ingredient checkpoint

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Closing Stock Report | captured_posist_report | Current quantity, average cost, and closing valuation evidence | `Deployment`, `Date`, `Generation Date`, `Item Code`, `Item Name`, `Category Name`, `Unit Name`, `Average Price`, `Total Qty`, `Total Amt` |
| Item Recipe Report | captured_posist_report | Menu-to-ingredient conversion | `Item Number`, `Qty`, `Recipe Unit`, `Ingredient Code`, `Ingredient Name` |
| AUX Menu Demand Forecast | synthetic_model_input | Synthetic seven-day menu demand and net-sales forecast | `source_period_code`, `outlet_code`, `menu_item_code`, `forecast_menu_qty`, `forecast_net_sales` |
| Enterprise Purchase Order Report | captured_posist_report | Ordered, processed, remaining, expected-date, status, and commitment-value evidence | `Deployment`, `Store Name`, `Vendor Name`, `PO Number`, `PO Date`, `Expected Delivery`, `PO Close Date/Partial Recieve Date`, `PO Status`, `Item Code`, `Item Name`, `Total Processed Qty`, `Remaining Balance Qty`, `Quantity`, `Unit`, `Unit Price`, `Total Item Cost` |

### Model Route And Relationship

`05_std_ct_inventory_snapshot.sql -> 26_fact_ct_forecast_ingredient_demand.sql -> 22_fact_ct_purchase_order.sql -> 27_fact_ct_inventory_risk.sql`

**Join/relationship logic:** Join stock, seven-day forecast ingredient demand, and valid open PO quantity on source period + outlet + item.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `item_code -> 14_dim_ct_item.sql.item_code`

### Calculation

**Final fields:** `item_code`, `current_stock_qty`, `forecast_required_qty`, `required_qty_with_safety`, `valid_open_po_qty`, `shortage_qty`, `days_cover`, `shortage_cost_value`, `risk_severity`

**Formula:** `shortage_qty = max(0, forecast_required_qty * 1.15 - current_stock_qty - valid_open_po_qty)`

**Aggregation:** Direct detail rows

### Exact Zoho Configuration

**Visual:** Tabular

**Shelves/columns:**

- Columns: item, stock, forecast, safety requirement, inbound, shortage, days cover, cost, severity

**Fixed report filters:**

- Filter shelf: risk_type / Individual Values / Include STOCKOUT

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- New/matured
- Risk severity
- Action owner
- Ingredient category

**Sort:** risk_severity_rank descending, shortage_cost_value descending

**Tooltips:**

- None

**Formatting:**

- None

### Guardrails

- The 15% safety factor is a demo rule pending ABNAH approval.
- Query 27 covers stockout exposure only; expiry is separate.

### How To Explain It

Stockout Risk Detail starts from Closing Stock Report, Item Recipe Report, AUX Menu Demand Forecast, Enterprise Purchase Order Report. The model follows 05_std_ct_inventory_snapshot.sql -> 26_fact_ct_forecast_ingredient_demand.sql -> 22_fact_ct_purchase_order.sql -> 27_fact_ct_inventory_risk.sql at source period, outlet, and inventory ingredient checkpoint. The relationship rule is: Join stock, seven-day forecast ingredient demand, and valid open PO quantity on source period + outlet + item. In Zoho, use direct detail rows and render it as tabular to answer: Which stock, forecast, safety, inbound, and cost inputs created each shortage?

<a id="ct-p1-vendor-po-risk"></a>
## CT_P1_Vendor_PO_Risk - Vendor PO Risk

**Business question:** Which open vendor POs are linked to current shortage-risk ingredients?

**Final object:** table / Tabular from `36_fact_ct_risky_po.sql`

**Final grain:** Source period, outlet, open PO, and risky item line

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Closing Stock Report | captured_posist_report | Current quantity, average cost, and closing valuation evidence | `Deployment`, `Date`, `Generation Date`, `Item Code`, `Item Name`, `Category Name`, `Unit Name`, `Average Price`, `Total Qty`, `Total Amt` |
| Item Recipe Report | captured_posist_report | Menu-to-ingredient conversion | `Item Number`, `Qty`, `Recipe Unit`, `Ingredient Code`, `Ingredient Name` |
| AUX Menu Demand Forecast | synthetic_model_input | Synthetic seven-day menu demand and net-sales forecast | `source_period_code`, `outlet_code`, `menu_item_code`, `forecast_menu_qty`, `forecast_net_sales` |
| Enterprise Purchase Order Report | captured_posist_report | Ordered, processed, remaining, expected-date, status, and commitment-value evidence | `Deployment`, `Store Name`, `Vendor Name`, `PO Number`, `PO Date`, `Expected Delivery`, `PO Close Date/Partial Recieve Date`, `PO Status`, `Item Code`, `Item Name`, `Total Processed Qty`, `Remaining Balance Qty`, `Quantity`, `Unit`, `Unit Price`, `Total Item Cost` |

### Model Route And Relationship

`05_std_ct_inventory_snapshot.sql -> 26_fact_ct_forecast_ingredient_demand.sql -> 22_fact_ct_purchase_order.sql -> 36_fact_ct_risky_po.sql`

**Join/relationship logic:** Retain open PO lines only where the matching item checkpoint is purple, red, or amber.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `item_code -> 14_dim_ct_item.sql.item_code`
- `vendor_name -> 16_dim_ct_vendor.sql.vendor_name`

### Calculation

**Final fields:** `po_number`, `vendor_name`, `expected_delivery_date`, `remaining_qty`, `open_po_value`, `risk_severity`

**Formula:** `Direct filtered risky-PO fact rows.`

**Aggregation:** One row per open risky PO item line

### Exact Zoho Configuration

**Visual:** Tabular

**Shelves/columns:**

- Columns: PO, vendor, expected date, remaining quantity, liability, severity

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- New/matured
- Risk severity
- Action owner
- Ingredient category

**Sort:** risk_severity_rank descending, open_po_value descending

**Tooltips:**

- None

**Formatting:**

- None

### Guardrails

- Count distinct PO number, not rows.
- Open PO quantity may reduce shortage risk but does not guarantee on-time receipt.

### How To Explain It

Vendor PO Risk starts from Closing Stock Report, Item Recipe Report, AUX Menu Demand Forecast, Enterprise Purchase Order Report. The model follows 05_std_ct_inventory_snapshot.sql -> 26_fact_ct_forecast_ingredient_demand.sql -> 22_fact_ct_purchase_order.sql -> 36_fact_ct_risky_po.sql at source period, outlet, open po, and risky item line. The relationship rule is: Retain open PO lines only where the matching item checkpoint is purple, red, or amber. In Zoho, use one row per open risky po item line and render it as tabular to answer: Which open vendor POs are linked to current shortage-risk ingredients?

# Page 2 - Procurement, Vendor & Capital Control

Explain purchase commitments, receipts, vendor performance, price movement, and capital exposure.

<a id="ct-p2-expected-delivery-breach"></a>
## CT_P2_Expected_Delivery_Breach - Expected Delivery Breach

**Business question:** Which open PO lines have passed their expected delivery date in the model?

**Final object:** table / Tabular from `22_fact_ct_purchase_order.sql`

**Final grain:** Source period, outlet, purchase order, and item line

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Enterprise Purchase Order Report | captured_posist_report | Ordered, processed, remaining, expected-date, status, and commitment-value evidence | `Deployment`, `Store Name`, `Vendor Name`, `PO Number`, `PO Date`, `Expected Delivery`, `PO Close Date/Partial Recieve Date`, `PO Status`, `Item Code`, `Item Name`, `Total Processed Qty`, `Remaining Balance Qty`, `Quantity`, `Unit`, `Unit Price`, `Total Item Cost` |

### Model Route And Relationship

`RAWN_CT_enterprise_purchase_order-Copy -> 07_std_ct_purchase_order.sql -> 22_fact_ct_purchase_order.sql`

**Join/relationship logic:** Normalize line status and derive ordered value, open quantity/value, open flag, and delayed flag at PO-line grain.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `item_code -> 14_dim_ct_item.sql.item_code`
- `vendor_name -> 16_dim_ct_vendor.sql.vendor_name`

### Calculation

**Final fields:** `po_number`, `vendor_name`, `item_code`, `expected_delivery_date`, `remaining_qty`, `open_po_value`, `delayed_po_flag`

**Formula:** `Select the physical delayed flag through the report Filter shelf.`

**Aggregation:** Direct detail rows

### Exact Zoho Configuration

**Visual:** Tabular

**Shelves/columns:**

- Columns: PO, vendor, item, expected date, remaining quantity/value

**Fixed report filters:**

- Filter shelf: delayed_po_flag / Individual Values / Include 1

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Vendor
- Ingredient category
- Item
- PO status

**Sort:** Expected delivery ascending

**Tooltips:**

- None

**Formatting:**

- None

### Guardrails

- Use distinct PO number for PO counts; row count is a PO-line count.
- Expected-date exceptions are operational states, not automatically source defects.
- Treat as an action queue; a revised date may exist outside the captured report.

### How To Explain It

Expected Delivery Breach starts from Enterprise Purchase Order Report. The model follows RAWN_CT_enterprise_purchase_order-Copy -> 07_std_ct_purchase_order.sql -> 22_fact_ct_purchase_order.sql at source period, outlet, purchase order, and item line. The relationship rule is: Normalize line status and derive ordered value, open quantity/value, open flag, and delayed flag at PO-line grain. In Zoho, use direct detail rows and render it as tabular to answer: Which open PO lines have passed their expected delivery date in the model?

<a id="ct-p2-expiry-exposure-demo"></a>
## CT_P2_Expiry_Exposure_Demo - Expiry Exposure - Demo

**Business question:** How does the synthetic expiry-risk value vary by period?

**Final object:** chart / Column from `38_fact_ct_expiry_risk.sql`

**Final grain:** Source period, outlet, synthetic batch allocation, and item

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Enterprise Entry Report - Stock Entry | captured_posist_report | Receipt date, GRN, PO, vendor, quantity, and cost pattern used for traceable demo tranches | `Date`, `Transaction Number`, `PO Number`, `Vendor Name`, `Item Code`, `Item Name`, `Quantity`, `Unit`, `Unit Price` |
| Closing Stock Report | captured_posist_report | Current item quantity and average-cost boundary | `Date`, `Item Code`, `Item Name`, `Unit Name`, `Average Price`, `Total Qty` |
| AUX Expiry Estimate | synthetic_model_input | Synthetic FIFO tranche and shelf-life scenario; not a POSIST batch or expiry source | `batch_allocation_id`, `receipt_date`, `estimated_expiry_date`, `expiry_qty_at_risk`, `expiry_risk_value`, `production_use_status` |

### Model Route And Relationship

`AUX_Expiry_Estimate-Copy -> 38_fact_ct_expiry_risk.sql`

**Join/relationship logic:** Expose the prebuilt synthetic FIFO/shelf-life scenario with permanent evidence and production-use labels.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `item_code -> 14_dim_ct_item.sql.item_code`

### Calculation

**Final fields:** `source_period_code`, `expiry_risk_value`, `production_use_status`

**Formula:** `sum("expiry_risk_value")`

**Aggregation:** Sum expiry risk value

### Exact Zoho Configuration

**Visual:** Column

**Shelves/columns:**

- X: source period
- Y: expiry risk value

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Vendor
- Ingredient category
- Item
- PO status

**Sort:** Business-relevant default order

**Tooltips:**

- None

**Formatting:**

- INR currency
- Subtitle: Synthetic estimate - no POSIST batch/expiry source

### Guardrails

- Every title or subtitle must say Synthetic demo estimate - no POSIST batch/expiry source.
- Do not present the scenario as actual batch ageing or expiry truth.

### How To Explain It

Expiry Exposure - Demo starts from Enterprise Entry Report - Stock Entry, Closing Stock Report, AUX Expiry Estimate. The model follows AUX_Expiry_Estimate-Copy -> 38_fact_ct_expiry_risk.sql at source period, outlet, synthetic batch allocation, and item. The relationship rule is: Expose the prebuilt synthetic FIFO/shelf-life scenario with permanent evidence and production-use labels. In Zoho, use sum expiry risk value and render it as column to answer: How does the synthetic expiry-risk value vary by period?

<a id="ct-p2-high-value-slow-stock"></a>
## CT_P2_High_Value_Slow_Stock - High Value / Slow Stock

**Business question:** Which items combine high closing value with high days cover or weak demand?

**Final object:** table / Tabular from `27_fact_ct_inventory_risk.sql`

**Final grain:** Source period, outlet, and inventory ingredient checkpoint

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Closing Stock Report | captured_posist_report | Current quantity, average cost, and closing valuation evidence | `Deployment`, `Date`, `Generation Date`, `Item Code`, `Item Name`, `Category Name`, `Unit Name`, `Average Price`, `Total Qty`, `Total Amt` |
| Item Recipe Report | captured_posist_report | Menu-to-ingredient conversion | `Item Number`, `Qty`, `Recipe Unit`, `Ingredient Code`, `Ingredient Name` |
| AUX Menu Demand Forecast | synthetic_model_input | Synthetic seven-day menu demand and net-sales forecast | `source_period_code`, `outlet_code`, `menu_item_code`, `forecast_menu_qty`, `forecast_net_sales` |
| Enterprise Purchase Order Report | captured_posist_report | Ordered, processed, remaining, expected-date, status, and commitment-value evidence | `Deployment`, `Store Name`, `Vendor Name`, `PO Number`, `PO Date`, `Expected Delivery`, `PO Close Date/Partial Recieve Date`, `PO Status`, `Item Code`, `Item Name`, `Total Processed Qty`, `Remaining Balance Qty`, `Quantity`, `Unit`, `Unit Price`, `Total Item Cost` |

### Model Route And Relationship

`05_std_ct_inventory_snapshot.sql -> 26_fact_ct_forecast_ingredient_demand.sql -> 22_fact_ct_purchase_order.sql -> 27_fact_ct_inventory_risk.sql`

**Join/relationship logic:** Join stock, seven-day forecast ingredient demand, and valid open PO quantity on source period + outlet + item.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `item_code -> 14_dim_ct_item.sql.item_code`

### Calculation

**Final fields:** `item_code`, `closing_value`, `days_cover`, `forecast_required_qty`, `risk_severity`

**Formula:** `Direct inventory-risk rows; ranking uses closing value and days cover.`

**Aggregation:** One row per item checkpoint

### Exact Zoho Configuration

**Visual:** Tabular

**Shelves/columns:**

- Columns: item, closing value, days cover, forecast demand, severity

**Fixed report filters:**

- Exactly one source period

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Vendor
- Ingredient category
- Item
- PO status

**Sort:** Closing value descending, days cover descending

**Tooltips:**

- None

**Formatting:**

- None

### Guardrails

- The 15% safety factor is a demo rule pending ABNAH approval.
- Query 27 covers stockout exposure only; expiry is separate.

### How To Explain It

High Value / Slow Stock starts from Closing Stock Report, Item Recipe Report, AUX Menu Demand Forecast, Enterprise Purchase Order Report. The model follows 05_std_ct_inventory_snapshot.sql -> 26_fact_ct_forecast_ingredient_demand.sql -> 22_fact_ct_purchase_order.sql -> 27_fact_ct_inventory_risk.sql at source period, outlet, and inventory ingredient checkpoint. The relationship rule is: Join stock, seven-day forecast ingredient demand, and valid open PO quantity on source period + outlet + item. In Zoho, use one row per item checkpoint and render it as tabular to answer: Which items combine high closing value with high days cover or weak demand?

<a id="ct-p2-ingredient-price-trend"></a>
## CT_P2_Ingredient_Price_Trend - Ingredient Price Trend

**Business question:** How has weighted received unit price changed by ingredient over time?

**Final object:** chart / Line from `23_fact_ct_purchase_receipt.sql`

**Final grain:** Source period, outlet, stock-entry transaction, and item line

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Enterprise Entry Report - Stock Entry | captured_posist_report | GRN/stock-entry receipt quantity, price, tax, total, vendor, and PO reference | `Deployment Name`, `Store/Kitchen Name`, `Vendor Name`, `Date`, `Transaction Number`, `Invoice Number`, `PO Number`, `Item Code`, `Item Name`, `Quantity`, `Unit`, `Unit Price`, `Amount`, `Total Tax`, `Total` |

### Model Route And Relationship

`RAWN_CT_enterprise_entry-Copy -> 08_std_ct_purchase_receipt.sql -> 23_fact_ct_purchase_receipt.sql`

**Join/relationship logic:** Normalize receipt identity, PO reference, quantity, subtotal, tax, and total without dropping the raw identifier.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `item_code -> 14_dim_ct_item.sql.item_code`
- `vendor_name -> 16_dim_ct_vendor.sql.vendor_name`

### Calculation

**Final fields:** `source_period_code`, `item_code`, `received_qty`, `receipt_subtotal`, `vendor_name`

**Formula:** `Aggregate Formula "Weighted Unit Price".`

**Aggregation:** Weighted unit price

### Exact Zoho Configuration

**Visual:** Line

**Shelves/columns:**

- X: source period
- Y: Weighted Unit Price
- Color: item

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Vendor
- Ingredient category
- Item
- PO status

**Sort:** Business-relevant default order

**Tooltips:**

- Vendor
- Received quantity
- Receipt subtotal

**Formatting:**

- INR per selected UOM

### Guardrails

- Weighted price is receipt subtotal divided by received quantity.
- PO linkage remains sparse in the audited actual extract.

### How To Explain It

Ingredient Price Trend starts from Enterprise Entry Report - Stock Entry. The model follows RAWN_CT_enterprise_entry-Copy -> 08_std_ct_purchase_receipt.sql -> 23_fact_ct_purchase_receipt.sql at source period, outlet, stock-entry transaction, and item line. The relationship rule is: Normalize receipt identity, PO reference, quantity, subtotal, tax, and total without dropping the raw identifier. In Zoho, use weighted unit price and render it as line to answer: How has weighted received unit price changed by ingredient over time?

<a id="ct-p2-inventory-value"></a>
## CT_P2_Inventory_Value - Inventory Value

**Business question:** Where is closing inventory value concentrated by outlet and category?

**Final object:** chart / Stacked bar from `05_std_ct_inventory_snapshot.sql`

**Final grain:** Source period, outlet, and inventory item checkpoint

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Closing Stock Report | captured_posist_report | Current quantity, average cost, and closing valuation evidence | `Deployment`, `Date`, `Generation Date`, `Item Code`, `Item Name`, `Category Name`, `Unit Name`, `Average Price`, `Total Qty`, `Total Amt` |

### Model Route And Relationship

`RAWN_CT_closing_stock-Copy -> 05_std_ct_inventory_snapshot.sql`

**Join/relationship logic:** No cross-report join in the final table; normalize outlet, item, period, UOM, quantity, and value.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `item_code -> 14_dim_ct_item.sql.item_code`

### Calculation

**Final fields:** `outlet_code`, `category_name`, `closing_value`

**Formula:** `sum("closing_value")`

**Aggregation:** Sum closing value

### Exact Zoho Configuration

**Visual:** Stacked bar

**Shelves/columns:**

- X: outlet
- Y: closing value
- Color: category

**Fixed report filters:**

- Exactly one source period

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Vendor
- Ingredient category
- Item
- PO status

**Sort:** Business-relevant default order

**Tooltips:**

- None

**Formatting:**

- INR currency

### Guardrails

- Use one source period for a current-state stock value.
- Do not add quantities across unlike UOMs.

### How To Explain It

Inventory Value starts from Closing Stock Report. The model follows RAWN_CT_closing_stock-Copy -> 05_std_ct_inventory_snapshot.sql at source period, outlet, and inventory item checkpoint. The relationship rule is: No cross-report join in the final table; normalize outlet, item, period, UOM, quantity, and value. In Zoho, use sum closing value and render it as stacked bar to answer: Where is closing inventory value concentrated by outlet and category?

<a id="ct-p2-kpi-closing-inventory"></a>
## CT_P2_KPI_Closing_Inventory - Closing Inventory Value

**Business question:** What is the selected checkpoint's closing inventory value?

**Final object:** kpi / KPI widget from `33_sum_ct_scm_monthly.sql`

**Final grain:** Source period and outlet

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Gross/Net Margin Report | captured_posist_report | Bill-item sales, quantity, realized revenue, and source cost evidence | `Store Name`, `Date`, `Bill No.`, `Super Category`, `Category`, `SKU Code / Item No`, `SKU / Item Name`, `Item Qty`, `Net Sale Value`, `Purchase Value` |
| Closing Stock Report | captured_posist_report | Current quantity, average cost, and closing valuation evidence | `Deployment`, `Date`, `Generation Date`, `Item Code`, `Item Name`, `Category Name`, `Unit Name`, `Average Price`, `Total Qty`, `Total Amt` |
| Enterprise Purchase Order Report | captured_posist_report | Ordered, processed, remaining, expected-date, status, and commitment-value evidence | `Deployment`, `Store Name`, `Vendor Name`, `PO Number`, `PO Date`, `Expected Delivery`, `PO Close Date/Partial Recieve Date`, `PO Status`, `Item Code`, `Item Name`, `Total Processed Qty`, `Remaining Balance Qty`, `Quantity`, `Unit`, `Unit Price`, `Total Item Cost` |
| Enterprise Variance Report | captured_posist_report | Opening, purchase, transfer, return, closing, and actual-consumption movement bridge | `Deployment Name`, `StoreKitchen Name`, `Item Code`, `Item Name`, `Average Price`, `Opening Qty`, `Purchase Qty`, `Stock In Qty`, `Stock Out Qty`, `Return Qty`, `Closing Qty`, `Actual Consumption`, `Unit` |

### Model Route And Relationship

`18_fact_ct_sales.sql -> 05_std_ct_inventory_snapshot.sql -> 22_fact_ct_purchase_order.sql -> 20_fact_ct_actual_consumption.sql -> 33_sum_ct_scm_monthly.sql`

**Join/relationship logic:** Aggregate each fact to source period + outlet before joining sales, stock value, open PO value, and actual consumption value.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`

### Calculation

**Final fields:** `closing_stock_value`

**Formula:** `sum("closing_stock_value")`

**Aggregation:** Sum closing stock value

### Exact Zoho Configuration

**Visual:** KPI widget

**Shelves/columns:**

- Data Column: closing_stock_value
- Show Value As: Sum
- Group By: blank

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Vendor
- Ingredient category
- Item
- PO status

**Sort:** Business-relevant default order

**Tooltips:**

- None

**Formatting:**

- INR currency

### Guardrails

- Current-state stock and working-capital widgets require one source period.
- This is a descriptive monthly summary, not a transaction table.
- Require exactly one source period.

### How To Explain It

Closing Inventory Value starts from Gross/Net Margin Report, Closing Stock Report, Enterprise Purchase Order Report, Enterprise Variance Report. The model follows 18_fact_ct_sales.sql -> 05_std_ct_inventory_snapshot.sql -> 22_fact_ct_purchase_order.sql -> 20_fact_ct_actual_consumption.sql -> 33_sum_ct_scm_monthly.sql at source period and outlet. The relationship rule is: Aggregate each fact to source period + outlet before joining sales, stock value, open PO value, and actual consumption value. In Zoho, use sum closing stock value and render it as kpi widget to answer: What is the selected checkpoint's closing inventory value?

<a id="ct-p2-kpi-fill-rate"></a>
## CT_P2_KPI_Fill_Rate - PO Fill Rate

**Business question:** What proportion of ordered quantity was linked to accepted receipt quantity?

**Final object:** kpi / Saved Summary View from `24_fact_ct_po_receipt_line.sql`

**Final grain:** Source period, outlet, purchase order, and item line

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Enterprise Purchase Order Report | captured_posist_report | Ordered, processed, remaining, expected-date, status, and commitment-value evidence | `Deployment`, `Store Name`, `Vendor Name`, `PO Number`, `PO Date`, `Expected Delivery`, `PO Close Date/Partial Recieve Date`, `PO Status`, `Item Code`, `Item Name`, `Total Processed Qty`, `Remaining Balance Qty`, `Quantity`, `Unit`, `Unit Price`, `Total Item Cost` |
| Enterprise Entry Report - Stock Entry | captured_posist_report | GRN/stock-entry receipt quantity, price, tax, total, vendor, and PO reference | `Deployment Name`, `Store/Kitchen Name`, `Vendor Name`, `Date`, `Transaction Number`, `Invoice Number`, `PO Number`, `Item Code`, `Item Name`, `Quantity`, `Unit`, `Unit Price`, `Amount`, `Total Tax`, `Total` |

### Model Route And Relationship

`07_std_ct_purchase_order.sql -> 08_std_ct_purchase_receipt.sql -> 24_fact_ct_po_receipt_line.sql`

**Join/relationship logic:** Left join PO and receipt lines on source period + outlet + canonical PO number + item code; aggregate receipts before the join.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `item_code -> 14_dim_ct_item.sql.item_code`
- `vendor_name -> 16_dim_ct_vendor.sql.vendor_name`

### Calculation

**Final fields:** `ordered_qty`, `received_qty`

**Formula:** `Aggregate Formula "PO Fill Rate %" in a saved Summary View.`

**Aggregation:** Ratio of summed quantities

### Exact Zoho Configuration

**Visual:** Saved Summary View

**Shelves/columns:**

- Summary value: PO Fill Rate %
- Grouping: none

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Vendor
- Ingredient category
- Item
- PO status

**Sort:** Business-relevant default order

**Tooltips:**

- None

**Formatting:**

- Percentage; expected display near 83.25% in all-period synthetic truth

### Guardrails

- Actual PO-to-GRN linkage was sparse, so OTIF remains a formula demonstration.
- Fill rate uses sums of quantities, never an average of row percentages.
- The Aggregate Formula is not selected from a direct KPI Widget Data Column list.

### How To Explain It

PO Fill Rate starts from Enterprise Purchase Order Report, Enterprise Entry Report - Stock Entry. The model follows 07_std_ct_purchase_order.sql -> 08_std_ct_purchase_receipt.sql -> 24_fact_ct_po_receipt_line.sql at source period, outlet, purchase order, and item line. The relationship rule is: Left join PO and receipt lines on source period + outlet + canonical PO number + item code; aggregate receipts before the join. In Zoho, use ratio of summed quantities and render it as saved summary view to answer: What proportion of ordered quantity was linked to accepted receipt quantity?

<a id="ct-p2-kpi-monthly-purchase"></a>
## CT_P2_KPI_Monthly_Purchase - Ordered Gross Value

**Business question:** What was the selected-period ordered gross commitment?

**Final object:** kpi / KPI widget from `29_sum_ct_procurement_funnel.sql`

**Final grain:** Source period, outlet, and vendor

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Enterprise Purchase Order Report | captured_posist_report | Ordered, processed, remaining, expected-date, status, and commitment-value evidence | `Deployment`, `Store Name`, `Vendor Name`, `PO Number`, `PO Date`, `Expected Delivery`, `PO Close Date/Partial Recieve Date`, `PO Status`, `Item Code`, `Item Name`, `Total Processed Qty`, `Remaining Balance Qty`, `Quantity`, `Unit`, `Unit Price`, `Total Item Cost` |

### Model Route And Relationship

`22_fact_ct_purchase_order.sql -> 29_sum_ct_procurement_funnel.sql`

**Join/relationship logic:** Group PO lines by source period + outlet + vendor and aggregate ordered, processed, pending, delayed value, and distinct PO counts.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `vendor_name -> 16_dim_ct_vendor.sql.vendor_name`

### Calculation

**Final fields:** `ordered_value`

**Formula:** `sum("ordered_value")`

**Aggregation:** Sum ordered value

### Exact Zoho Configuration

**Visual:** KPI widget

**Shelves/columns:**

- Data Column: ordered_value
- Show Value As: Sum
- Group By: blank

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Vendor
- Ingredient category
- Item
- PO status

**Sort:** Business-relevant default order

**Tooltips:**

- None

**Formatting:**

- INR currency
- Label Ordered Gross Value until basis is approved

### Guardrails

- Monthly purchase is labelled Ordered Gross Value until the production basis is approved.
- Do not use row count as PO count.

### How To Explain It

Ordered Gross Value starts from Enterprise Purchase Order Report. The model follows 22_fact_ct_purchase_order.sql -> 29_sum_ct_procurement_funnel.sql at source period, outlet, and vendor. The relationship rule is: Group PO lines by source period + outlet + vendor and aggregate ordered, processed, pending, delayed value, and distinct PO counts. In Zoho, use sum ordered value and render it as kpi widget to answer: What was the selected-period ordered gross commitment?

<a id="ct-p2-kpi-otif"></a>
## CT_P2_KPI_OTIF - Vendor OTIF - Formula Demo

**Business question:** What share of eligible closed PO lines met both quantity and date conditions in the demonstration?

**Final object:** kpi / Saved Summary View from `24_fact_ct_po_receipt_line.sql`

**Final grain:** Source period, outlet, purchase order, and item line

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Enterprise Purchase Order Report | captured_posist_report | Ordered, processed, remaining, expected-date, status, and commitment-value evidence | `Deployment`, `Store Name`, `Vendor Name`, `PO Number`, `PO Date`, `Expected Delivery`, `PO Close Date/Partial Recieve Date`, `PO Status`, `Item Code`, `Item Name`, `Total Processed Qty`, `Remaining Balance Qty`, `Quantity`, `Unit`, `Unit Price`, `Total Item Cost` |
| Enterprise Entry Report - Stock Entry | captured_posist_report | GRN/stock-entry receipt quantity, price, tax, total, vendor, and PO reference | `Deployment Name`, `Store/Kitchen Name`, `Vendor Name`, `Date`, `Transaction Number`, `Invoice Number`, `PO Number`, `Item Code`, `Item Name`, `Quantity`, `Unit`, `Unit Price`, `Amount`, `Total Tax`, `Total` |

### Model Route And Relationship

`07_std_ct_purchase_order.sql -> 08_std_ct_purchase_receipt.sql -> 24_fact_ct_po_receipt_line.sql`

**Join/relationship logic:** Left join PO and receipt lines on source period + outlet + canonical PO number + item code; aggregate receipts before the join.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `item_code -> 14_dim_ct_item.sql.item_code`
- `vendor_name -> 16_dim_ct_vendor.sql.vendor_name`

### Calculation

**Final fields:** `eligible_closed_line_flag`, `otif_success_flag`

**Formula:** `Aggregate Formula "Vendor OTIF %" in a saved Summary View.`

**Aggregation:** Ratio of summed flags

### Exact Zoho Configuration

**Visual:** Saved Summary View

**Shelves/columns:**

- Summary value: Vendor OTIF %
- Grouping: none

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Vendor
- Ingredient category
- Item
- PO status

**Sort:** Business-relevant default order

**Tooltips:**

- None

**Formatting:**

- Percentage
- Visible Formula demo label

### Guardrails

- Actual PO-to-GRN linkage was sparse, so OTIF remains a formula demonstration.
- Fill rate uses sums of quantities, never an average of row percentages.
- Production is blocked by sparse actual PO-to-GRN linkage.
- The Aggregate Formula is not selected from a direct KPI Widget Data Column list.

### How To Explain It

Vendor OTIF - Formula Demo starts from Enterprise Purchase Order Report, Enterprise Entry Report - Stock Entry. The model follows 07_std_ct_purchase_order.sql -> 08_std_ct_purchase_receipt.sql -> 24_fact_ct_po_receipt_line.sql at source period, outlet, purchase order, and item line. The relationship rule is: Left join PO and receipt lines on source period + outlet + canonical PO number + item code; aggregate receipts before the join. In Zoho, use ratio of summed flags and render it as saved summary view to answer: What share of eligible closed PO lines met both quantity and date conditions in the demonstration?

<a id="ct-p2-kpi-open-po-count"></a>
## CT_P2_KPI_Open_PO_Count - Open PO Count

**Business question:** How many distinct purchase orders remain open?

**Final object:** kpi / KPI widget from `29_sum_ct_procurement_funnel.sql`

**Final grain:** Source period, outlet, and vendor

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Enterprise Purchase Order Report | captured_posist_report | Ordered, processed, remaining, expected-date, status, and commitment-value evidence | `Deployment`, `Store Name`, `Vendor Name`, `PO Number`, `PO Date`, `Expected Delivery`, `PO Close Date/Partial Recieve Date`, `PO Status`, `Item Code`, `Item Name`, `Total Processed Qty`, `Remaining Balance Qty`, `Quantity`, `Unit`, `Unit Price`, `Total Item Cost` |

### Model Route And Relationship

`22_fact_ct_purchase_order.sql -> 29_sum_ct_procurement_funnel.sql`

**Join/relationship logic:** Group PO lines by source period + outlet + vendor and aggregate ordered, processed, pending, delayed value, and distinct PO counts.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `vendor_name -> 16_dim_ct_vendor.sql.vendor_name`

### Calculation

**Final fields:** `open_po_count`

**Formula:** `sum("open_po_count")`

**Aggregation:** Sum vendor-level distinct PO counts within the selected outlet scope

### Exact Zoho Configuration

**Visual:** KPI widget

**Shelves/columns:**

- Data Column: open_po_count
- Show Value As: Sum
- Group By: blank

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Vendor
- Ingredient category
- Item
- PO status

**Sort:** Business-relevant default order

**Tooltips:**

- None

**Formatting:**

- Whole number

### Guardrails

- Monthly purchase is labelled Ordered Gross Value until the production basis is approved.
- Do not use row count as PO count.

### How To Explain It

Open PO Count starts from Enterprise Purchase Order Report. The model follows 22_fact_ct_purchase_order.sql -> 29_sum_ct_procurement_funnel.sql at source period, outlet, and vendor. The relationship rule is: Group PO lines by source period + outlet + vendor and aggregate ordered, processed, pending, delayed value, and distinct PO counts. In Zoho, use sum vendor-level distinct po counts within the selected outlet scope and render it as kpi widget to answer: How many distinct purchase orders remain open?

<a id="ct-p2-kpi-open-po-liability"></a>
## CT_P2_KPI_Open_PO_Liability - Open PO Liability

**Business question:** How much value remains committed on open PO lines?

**Final object:** kpi / KPI widget from `29_sum_ct_procurement_funnel.sql`

**Final grain:** Source period, outlet, and vendor

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Enterprise Purchase Order Report | captured_posist_report | Ordered, processed, remaining, expected-date, status, and commitment-value evidence | `Deployment`, `Store Name`, `Vendor Name`, `PO Number`, `PO Date`, `Expected Delivery`, `PO Close Date/Partial Recieve Date`, `PO Status`, `Item Code`, `Item Name`, `Total Processed Qty`, `Remaining Balance Qty`, `Quantity`, `Unit`, `Unit Price`, `Total Item Cost` |

### Model Route And Relationship

`22_fact_ct_purchase_order.sql -> 29_sum_ct_procurement_funnel.sql`

**Join/relationship logic:** Group PO lines by source period + outlet + vendor and aggregate ordered, processed, pending, delayed value, and distinct PO counts.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `vendor_name -> 16_dim_ct_vendor.sql.vendor_name`

### Calculation

**Final fields:** `pending_value`

**Formula:** `sum("pending_value")`

**Aggregation:** Sum pending value

### Exact Zoho Configuration

**Visual:** KPI widget

**Shelves/columns:**

- Data Column: pending_value
- Show Value As: Sum
- Group By: blank

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Vendor
- Ingredient category
- Item
- PO status

**Sort:** Business-relevant default order

**Tooltips:**

- None

**Formatting:**

- INR currency

### Guardrails

- Monthly purchase is labelled Ordered Gross Value until the production basis is approved.
- Do not use row count as PO count.

### How To Explain It

Open PO Liability starts from Enterprise Purchase Order Report. The model follows 22_fact_ct_purchase_order.sql -> 29_sum_ct_procurement_funnel.sql at source period, outlet, and vendor. The relationship rule is: Group PO lines by source period + outlet + vendor and aggregate ordered, processed, pending, delayed value, and distinct PO counts. In Zoho, use sum pending value and render it as kpi widget to answer: How much value remains committed on open PO lines?

<a id="ct-p2-kpi-working-capital"></a>
## CT_P2_KPI_Working_Capital - Working Capital Locked

**Business question:** How much capital is represented by closing inventory plus open PO liability?

**Final object:** kpi / KPI widget from `33_sum_ct_scm_monthly.sql`

**Final grain:** Source period and outlet

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Gross/Net Margin Report | captured_posist_report | Bill-item sales, quantity, realized revenue, and source cost evidence | `Store Name`, `Date`, `Bill No.`, `Super Category`, `Category`, `SKU Code / Item No`, `SKU / Item Name`, `Item Qty`, `Net Sale Value`, `Purchase Value` |
| Closing Stock Report | captured_posist_report | Current quantity, average cost, and closing valuation evidence | `Deployment`, `Date`, `Generation Date`, `Item Code`, `Item Name`, `Category Name`, `Unit Name`, `Average Price`, `Total Qty`, `Total Amt` |
| Enterprise Purchase Order Report | captured_posist_report | Ordered, processed, remaining, expected-date, status, and commitment-value evidence | `Deployment`, `Store Name`, `Vendor Name`, `PO Number`, `PO Date`, `Expected Delivery`, `PO Close Date/Partial Recieve Date`, `PO Status`, `Item Code`, `Item Name`, `Total Processed Qty`, `Remaining Balance Qty`, `Quantity`, `Unit`, `Unit Price`, `Total Item Cost` |
| Enterprise Variance Report | captured_posist_report | Opening, purchase, transfer, return, closing, and actual-consumption movement bridge | `Deployment Name`, `StoreKitchen Name`, `Item Code`, `Item Name`, `Average Price`, `Opening Qty`, `Purchase Qty`, `Stock In Qty`, `Stock Out Qty`, `Return Qty`, `Closing Qty`, `Actual Consumption`, `Unit` |

### Model Route And Relationship

`18_fact_ct_sales.sql -> 05_std_ct_inventory_snapshot.sql -> 22_fact_ct_purchase_order.sql -> 20_fact_ct_actual_consumption.sql -> 33_sum_ct_scm_monthly.sql`

**Join/relationship logic:** Aggregate each fact to source period + outlet before joining sales, stock value, open PO value, and actual consumption value.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`

### Calculation

**Final fields:** `working_capital_value`

**Formula:** `sum("working_capital_value")`

**Aggregation:** Sum the physical working-capital field

### Exact Zoho Configuration

**Visual:** KPI widget

**Shelves/columns:**

- Data Column: working_capital_value
- Show Value As: Sum
- Group By: blank

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Vendor
- Ingredient category
- Item
- PO status

**Sort:** Business-relevant default order

**Tooltips:**

- None

**Formatting:**

- INR currency

### Guardrails

- Current-state stock and working-capital widgets require one source period.
- This is a descriptive monthly summary, not a transaction table.
- Show closing inventory and open PO liability separately beside this combined KPI.
- Require one source period.

### How To Explain It

Working Capital Locked starts from Gross/Net Margin Report, Closing Stock Report, Enterprise Purchase Order Report, Enterprise Variance Report. The model follows 18_fact_ct_sales.sql -> 05_std_ct_inventory_snapshot.sql -> 22_fact_ct_purchase_order.sql -> 20_fact_ct_actual_consumption.sql -> 33_sum_ct_scm_monthly.sql at source period and outlet. The relationship rule is: Aggregate each fact to source period + outlet before joining sales, stock value, open PO value, and actual consumption value. In Zoho, use sum the physical working-capital field and render it as kpi widget to answer: How much capital is represented by closing inventory plus open PO liability?

<a id="ct-p2-observed-wastage"></a>
## CT_P2_Observed_Wastage - Observed Wastage

**Business question:** How much source-observed wastage value occurred by period?

**Final object:** chart / Column from `35_sum_ct_financial_leakage.sql`

**Final grain:** Source period and outlet

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Enterprise Wastage Report | captured_posist_report | Observed wastage quantity and value | `Deployment Name`, `Store/Kitchen Name`, `Date`, `Transaction Number`, `Item Code`, `Item Name`, `Quantity`, `Unit`, `Unit Price`, `Amount` |

### Model Route And Relationship

`RAWN_CT_enterprise_wastage_normal-Copy -> 09_std_ct_wastage.sql -> 35_sum_ct_financial_leakage.sql`

**Join/relationship logic:** Aggregate observed wastage value by period and outlet.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`

### Calculation

**Final fields:** `source_period_code`, `leakage_value`

**Formula:** `sum("leakage_value")`

**Aggregation:** Sum observed wastage value

### Exact Zoho Configuration

**Visual:** Column

**Shelves/columns:**

- X: source period
- Y: observed wastage value

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Vendor
- Ingredient category
- Item
- PO status

**Sort:** Business-relevant default order

**Tooltips:**

- None

**Formatting:**

- INR currency

### Guardrails

- Label as Observed Wastage, not total financial leakage.
- Vendor returns and production expiry are unavailable.
- This is observed wastage only, not returns plus expiry plus wastage.

### How To Explain It

Observed Wastage starts from Enterprise Wastage Report. The model follows RAWN_CT_enterprise_wastage_normal-Copy -> 09_std_ct_wastage.sql -> 35_sum_ct_financial_leakage.sql at source period and outlet. The relationship rule is: Aggregate observed wastage value by period and outlet. In Zoho, use sum observed wastage value and render it as column to answer: How much source-observed wastage value occurred by period?

<a id="ct-p2-po-status-distribution"></a>
## CT_P2_PO_Status_Distribution - PO Status Distribution

**Business question:** How are purchase orders distributed by normalized status and liability?

**Final object:** chart / Stacked bar from `22_fact_ct_purchase_order.sql`

**Final grain:** Source period, outlet, purchase order, and item line

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Enterprise Purchase Order Report | captured_posist_report | Ordered, processed, remaining, expected-date, status, and commitment-value evidence | `Deployment`, `Store Name`, `Vendor Name`, `PO Number`, `PO Date`, `Expected Delivery`, `PO Close Date/Partial Recieve Date`, `PO Status`, `Item Code`, `Item Name`, `Total Processed Qty`, `Remaining Balance Qty`, `Quantity`, `Unit`, `Unit Price`, `Total Item Cost` |

### Model Route And Relationship

`RAWN_CT_enterprise_purchase_order-Copy -> 07_std_ct_purchase_order.sql -> 22_fact_ct_purchase_order.sql`

**Join/relationship logic:** Normalize line status and derive ordered value, open quantity/value, open flag, and delayed flag at PO-line grain.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `item_code -> 14_dim_ct_item.sql.item_code`
- `vendor_name -> 16_dim_ct_vendor.sql.vendor_name`

### Calculation

**Final fields:** `po_status`, `po_number`, `open_po_value`

**Formula:** `distinctcount("po_number") and sum("open_po_value")`

**Aggregation:** Distinct PO count plus sum open liability

### Exact Zoho Configuration

**Visual:** Stacked bar

**Shelves/columns:**

- X: PO status
- Y: distinct PO count and open liability

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Vendor
- Ingredient category
- Item
- PO status

**Sort:** Business-relevant default order

**Tooltips:**

- Ordered value
- Remaining quantity

**Formatting:**

- None

### Guardrails

- Use distinct PO number for PO counts; row count is a PO-line count.
- Expected-date exceptions are operational states, not automatically source defects.

### How To Explain It

PO Status Distribution starts from Enterprise Purchase Order Report. The model follows RAWN_CT_enterprise_purchase_order-Copy -> 07_std_ct_purchase_order.sql -> 22_fact_ct_purchase_order.sql at source period, outlet, purchase order, and item line. The relationship rule is: Normalize line status and derive ordered value, open quantity/value, open flag, and delayed flag at PO-line grain. In Zoho, use distinct po count plus sum open liability and render it as stacked bar to answer: How are purchase orders distributed by normalized status and liability?

<a id="ct-p2-pending-by-vendor"></a>
## CT_P2_Pending_By_Vendor - Pending Value By Vendor

**Business question:** Which vendors hold the most open PO liability?

**Final object:** chart / Horizontal bar from `29_sum_ct_procurement_funnel.sql`

**Final grain:** Source period, outlet, and vendor

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Enterprise Purchase Order Report | captured_posist_report | Ordered, processed, remaining, expected-date, status, and commitment-value evidence | `Deployment`, `Store Name`, `Vendor Name`, `PO Number`, `PO Date`, `Expected Delivery`, `PO Close Date/Partial Recieve Date`, `PO Status`, `Item Code`, `Item Name`, `Total Processed Qty`, `Remaining Balance Qty`, `Quantity`, `Unit`, `Unit Price`, `Total Item Cost` |

### Model Route And Relationship

`22_fact_ct_purchase_order.sql -> 29_sum_ct_procurement_funnel.sql`

**Join/relationship logic:** Group PO lines by source period + outlet + vendor and aggregate ordered, processed, pending, delayed value, and distinct PO counts.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `vendor_name -> 16_dim_ct_vendor.sql.vendor_name`

### Calculation

**Final fields:** `vendor_name`, `pending_value`

**Formula:** `sum("pending_value")`

**Aggregation:** Sum pending value

### Exact Zoho Configuration

**Visual:** Horizontal bar

**Shelves/columns:**

- Y: vendor
- X: pending value

**Fixed report filters:**

- Open PO summary only

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Vendor
- Ingredient category
- Item
- PO status

**Sort:** Pending value descending

**Tooltips:**

- None

**Formatting:**

- INR currency

### Guardrails

- Monthly purchase is labelled Ordered Gross Value until the production basis is approved.
- Do not use row count as PO count.

### How To Explain It

Pending Value By Vendor starts from Enterprise Purchase Order Report. The model follows 22_fact_ct_purchase_order.sql -> 29_sum_ct_procurement_funnel.sql at source period, outlet, and vendor. The relationship rule is: Group PO lines by source period + outlet + vendor and aggregate ordered, processed, pending, delayed value, and distinct PO counts. In Zoho, use sum pending value and render it as horizontal bar to answer: Which vendors hold the most open PO liability?

<a id="ct-p2-pending-ingredient-risk"></a>
## CT_P2_Pending_Ingredient_Risk - Pending Ingredient Risk

**Business question:** Which pending PO ingredients are already tied to operational stockout risk?

**Final object:** table / Tabular from `36_fact_ct_risky_po.sql`

**Final grain:** Source period, outlet, open PO, and risky item line

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Closing Stock Report | captured_posist_report | Current quantity, average cost, and closing valuation evidence | `Deployment`, `Date`, `Generation Date`, `Item Code`, `Item Name`, `Category Name`, `Unit Name`, `Average Price`, `Total Qty`, `Total Amt` |
| Item Recipe Report | captured_posist_report | Menu-to-ingredient conversion | `Item Number`, `Qty`, `Recipe Unit`, `Ingredient Code`, `Ingredient Name` |
| AUX Menu Demand Forecast | synthetic_model_input | Synthetic seven-day menu demand and net-sales forecast | `source_period_code`, `outlet_code`, `menu_item_code`, `forecast_menu_qty`, `forecast_net_sales` |
| Enterprise Purchase Order Report | captured_posist_report | Ordered, processed, remaining, expected-date, status, and commitment-value evidence | `Deployment`, `Store Name`, `Vendor Name`, `PO Number`, `PO Date`, `Expected Delivery`, `PO Close Date/Partial Recieve Date`, `PO Status`, `Item Code`, `Item Name`, `Total Processed Qty`, `Remaining Balance Qty`, `Quantity`, `Unit`, `Unit Price`, `Total Item Cost` |

### Model Route And Relationship

`05_std_ct_inventory_snapshot.sql -> 26_fact_ct_forecast_ingredient_demand.sql -> 22_fact_ct_purchase_order.sql -> 36_fact_ct_risky_po.sql`

**Join/relationship logic:** Retain open PO lines only where the matching item checkpoint is purple, red, or amber.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `item_code -> 14_dim_ct_item.sql.item_code`
- `vendor_name -> 16_dim_ct_vendor.sql.vendor_name`

### Calculation

**Final fields:** `po_number`, `vendor_name`, `item_code`, `remaining_qty`, `open_po_value`, `expected_delivery_date`, `risk_severity`

**Formula:** `Direct risky-PO fact rows.`

**Aggregation:** One row per open risky PO item line

### Exact Zoho Configuration

**Visual:** Tabular

**Shelves/columns:**

- Columns: PO, vendor, ingredient, remaining quantity/value, expected date, severity

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Vendor
- Ingredient category
- Item
- PO status

**Sort:** risk_severity_rank descending, open_po_value descending

**Tooltips:**

- None

**Formatting:**

- None

### Guardrails

- Count distinct PO number, not rows.
- Open PO quantity may reduce shortage risk but does not guarantee on-time receipt.

### How To Explain It

Pending Ingredient Risk starts from Closing Stock Report, Item Recipe Report, AUX Menu Demand Forecast, Enterprise Purchase Order Report. The model follows 05_std_ct_inventory_snapshot.sql -> 26_fact_ct_forecast_ingredient_demand.sql -> 22_fact_ct_purchase_order.sql -> 36_fact_ct_risky_po.sql at source period, outlet, open po, and risky item line. The relationship rule is: Retain open PO lines only where the matching item checkpoint is purple, red, or amber. In Zoho, use one row per open risky po item line and render it as tabular to answer: Which pending PO ingredients are already tied to operational stockout risk?

<a id="ct-p2-procurement-funnel"></a>
## CT_P2_Procurement_Funnel - Procurement Funnel

**Business question:** How does ordered value move through processed, pending, and delayed stages?

**Final object:** chart / Funnel or grouped horizontal bar from `29_sum_ct_procurement_funnel.sql`

**Final grain:** Source period, outlet, and vendor

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Enterprise Purchase Order Report | captured_posist_report | Ordered, processed, remaining, expected-date, status, and commitment-value evidence | `Deployment`, `Store Name`, `Vendor Name`, `PO Number`, `PO Date`, `Expected Delivery`, `PO Close Date/Partial Recieve Date`, `PO Status`, `Item Code`, `Item Name`, `Total Processed Qty`, `Remaining Balance Qty`, `Quantity`, `Unit`, `Unit Price`, `Total Item Cost` |

### Model Route And Relationship

`22_fact_ct_purchase_order.sql -> 29_sum_ct_procurement_funnel.sql`

**Join/relationship logic:** Group PO lines by source period + outlet + vendor and aggregate ordered, processed, pending, delayed value, and distinct PO counts.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `vendor_name -> 16_dim_ct_vendor.sql.vendor_name`

### Calculation

**Final fields:** `ordered_value`, `processed_value`, `pending_value`, `delayed_value`, `po_count`, `open_po_count`

**Formula:** `Four direct stage measures from the procurement summary.`

**Aggregation:** Sum each value measure

### Exact Zoho Configuration

**Visual:** Funnel or grouped horizontal bar

**Shelves/columns:**

- Stages: ordered, processed, pending, delayed

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Vendor
- Ingredient category
- Item
- PO status

**Sort:** Business-relevant default order

**Tooltips:**

- PO count
- Open PO count

**Formatting:**

- None

### Guardrails

- Monthly purchase is labelled Ordered Gross Value until the production basis is approved.
- Do not use row count as PO count.
- Use a grouped horizontal bar if Zoho cannot use measure names as funnel stages.

### How To Explain It

Procurement Funnel starts from Enterprise Purchase Order Report. The model follows 22_fact_ct_purchase_order.sql -> 29_sum_ct_procurement_funnel.sql at source period, outlet, and vendor. The relationship rule is: Group PO lines by source period + outlet + vendor and aggregate ordered, processed, pending, delayed value, and distinct PO counts. In Zoho, use sum each value measure and render it as funnel or grouped horizontal bar to answer: How does ordered value move through processed, pending, and delayed stages?

<a id="ct-p2-top-price-movement"></a>
## CT_P2_Top_Price_Movement - Top Price Movement

**Business question:** Which item/vendor prices changed most from the prior synthetic month?

**Final object:** chart / Divergent or horizontal bar from `31_sum_ct_price_movement.sql`

**Final grain:** Source period, outlet, vendor, item, and canonical UOM

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Enterprise Entry Report - Stock Entry | captured_posist_report | GRN/stock-entry receipt quantity, price, tax, total, vendor, and PO reference | `Deployment Name`, `Store/Kitchen Name`, `Vendor Name`, `Date`, `Transaction Number`, `Invoice Number`, `PO Number`, `Item Code`, `Item Name`, `Quantity`, `Unit`, `Unit Price`, `Amount`, `Total Tax`, `Total` |

### Model Route And Relationship

`23_fact_ct_purchase_receipt.sql -> 31_sum_ct_price_movement.sql`

**Join/relationship logic:** Calculate weighted receipt price per period and compare it with the immediately prior synthetic month at the same outlet/vendor/item/UOM grain.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `item_code -> 14_dim_ct_item.sql.item_code`
- `vendor_name -> 16_dim_ct_vendor.sql.vendor_name`

### Calculation

**Final fields:** `price_comparison_key`, `unit_price_change_percent`, `absolute_unit_price_change_percent`, `price_movement_direction`

**Formula:** `Signed physical change is displayed; absolute physical change is used only for sorting.`

**Aggregation:** Direct period-item-vendor-UOM result

### Exact Zoho Configuration

**Visual:** Divergent or horizontal bar

**Shelves/columns:**

- Y: price_comparison_key
- X: unit_price_change_percent
- Color: price_movement_direction

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Vendor
- Ingredient category
- Item
- PO status

**Sort:** absolute_unit_price_change_percent descending; Top 10

**Tooltips:**

- Vendor
- Previous weighted price
- Current weighted price

**Formatting:**

- Signed percentage

### Guardrails

- Do not aggregate price-change percentages across items or UOMs.
- Use absolute change only for sorting; display the signed change.

### How To Explain It

Top Price Movement starts from Enterprise Entry Report - Stock Entry. The model follows 23_fact_ct_purchase_receipt.sql -> 31_sum_ct_price_movement.sql at source period, outlet, vendor, item, and canonical uom. The relationship rule is: Calculate weighted receipt price per period and compare it with the immediately prior synthetic month at the same outlet/vendor/item/UOM grain. In Zoho, use direct period-item-vendor-uom result and render it as divergent or horizontal bar to answer: Which item/vendor prices changed most from the prior synthetic month?

<a id="ct-p2-vendor-performance-matrix"></a>
## CT_P2_Vendor_Performance_Matrix - Vendor Performance Matrix

**Business question:** Which vendors combine low OTIF, lead-time deviation, and high open exposure?

**Final object:** chart / Bubble from `24_fact_ct_po_receipt_line.sql`

**Final grain:** Source period, outlet, purchase order, and item line

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Enterprise Purchase Order Report | captured_posist_report | Ordered, processed, remaining, expected-date, status, and commitment-value evidence | `Deployment`, `Store Name`, `Vendor Name`, `PO Number`, `PO Date`, `Expected Delivery`, `PO Close Date/Partial Recieve Date`, `PO Status`, `Item Code`, `Item Name`, `Total Processed Qty`, `Remaining Balance Qty`, `Quantity`, `Unit`, `Unit Price`, `Total Item Cost` |
| Enterprise Entry Report - Stock Entry | captured_posist_report | GRN/stock-entry receipt quantity, price, tax, total, vendor, and PO reference | `Deployment Name`, `Store/Kitchen Name`, `Vendor Name`, `Date`, `Transaction Number`, `Invoice Number`, `PO Number`, `Item Code`, `Item Name`, `Quantity`, `Unit`, `Unit Price`, `Amount`, `Total Tax`, `Total` |

### Model Route And Relationship

`07_std_ct_purchase_order.sql -> 08_std_ct_purchase_receipt.sql -> 24_fact_ct_po_receipt_line.sql`

**Join/relationship logic:** Left join PO and receipt lines on source period + outlet + canonical PO number + item code; aggregate receipts before the join.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `item_code -> 14_dim_ct_item.sql.item_code`
- `vendor_name -> 16_dim_ct_vendor.sql.vendor_name`

### Calculation

**Final fields:** `vendor_name`, `eligible_closed_line_flag`, `otif_success_flag`, `eligible_lead_time_deviation_days`, `open_po_value`

**Formula:** `Use Vendor OTIF % Aggregate Formula and physical eligible lead-time deviation.`

**Aggregation:** Group by vendor over Query 24

### Exact Zoho Configuration

**Visual:** Bubble

**Shelves/columns:**

- X: Vendor OTIF %
- Y: average eligible_lead_time_deviation_days
- Size: sum open_po_value
- Text: vendor

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Vendor
- Ingredient category
- Item
- PO status

**Sort:** Business-relevant default order

**Tooltips:**

- PO Fill Rate %
- Open PO value
- Delayed line count

**Formatting:**

- None

### Guardrails

- Actual PO-to-GRN linkage was sparse, so OTIF remains a formula demonstration.
- Fill rate uses sums of quantities, never an average of row percentages.
- Formula demonstration until actual PO-to-GRN linkage improves.

### How To Explain It

Vendor Performance Matrix starts from Enterprise Purchase Order Report, Enterprise Entry Report - Stock Entry. The model follows 07_std_ct_purchase_order.sql -> 08_std_ct_purchase_receipt.sql -> 24_fact_ct_po_receipt_line.sql at source period, outlet, purchase order, and item line. The relationship rule is: Left join PO and receipt lines on source period + outlet + canonical PO number + item code; aggregate receipts before the join. In Zoho, use group by vendor over query 24 and render it as bubble to answer: Which vendors combine low OTIF, lead-time deviation, and high open exposure?

<a id="ct-p2-vendor-price-comparison"></a>
## CT_P2_Vendor_Price_Comparison - Vendor Price Comparison

**Business question:** For one ingredient and UOM, which vendor supplied at what weighted price?

**Final object:** chart / Grouped bar from `23_fact_ct_purchase_receipt.sql`

**Final grain:** Source period, outlet, stock-entry transaction, and item line

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Enterprise Entry Report - Stock Entry | captured_posist_report | GRN/stock-entry receipt quantity, price, tax, total, vendor, and PO reference | `Deployment Name`, `Store/Kitchen Name`, `Vendor Name`, `Date`, `Transaction Number`, `Invoice Number`, `PO Number`, `Item Code`, `Item Name`, `Quantity`, `Unit`, `Unit Price`, `Amount`, `Total Tax`, `Total` |

### Model Route And Relationship

`RAWN_CT_enterprise_entry-Copy -> 08_std_ct_purchase_receipt.sql -> 23_fact_ct_purchase_receipt.sql`

**Join/relationship logic:** Normalize receipt identity, PO reference, quantity, subtotal, tax, and total without dropping the raw identifier.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `item_code -> 14_dim_ct_item.sql.item_code`
- `vendor_name -> 16_dim_ct_vendor.sql.vendor_name`

### Calculation

**Final fields:** `vendor_name`, `item_code`, `canonical_uom`, `received_qty`, `receipt_subtotal`

**Formula:** `Aggregate Formula "Weighted Unit Price".`

**Aggregation:** Weighted unit price

### Exact Zoho Configuration

**Visual:** Grouped bar

**Shelves/columns:**

- X: vendor
- Y: Weighted Unit Price

**Fixed report filters:**

- Item user filter: select exactly one value
- Canonical UOM user filter: select exactly one value

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Vendor
- Ingredient category
- Item
- PO status

**Sort:** Weighted unit price ascending

**Tooltips:**

- None

**Formatting:**

- INR per selected UOM

### Guardrails

- Weighted price is receipt subtotal divided by received quantity.
- PO linkage remains sparse in the audited actual extract.

### How To Explain It

Vendor Price Comparison starts from Enterprise Entry Report - Stock Entry. The model follows RAWN_CT_enterprise_entry-Copy -> 08_std_ct_purchase_receipt.sql -> 23_fact_ct_purchase_receipt.sql at source period, outlet, stock-entry transaction, and item line. The relationship rule is: Normalize receipt identity, PO reference, quantity, subtotal, tax, and total without dropping the raw identifier. In Zoho, use weighted unit price and render it as grouped bar to answer: For one ingredient and UOM, which vendor supplied at what weighted price?

<a id="ct-p2-vendor-scorecard"></a>
## CT_P2_Vendor_Scorecard - Vendor Scorecard

**Business question:** What purchase, exposure, fill, OTIF, lead, and delay profile does each vendor have?

**Final object:** table / Summary or pivot from `24_fact_ct_po_receipt_line.sql`

**Final grain:** Source period, outlet, purchase order, and item line

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Enterprise Purchase Order Report | captured_posist_report | Ordered, processed, remaining, expected-date, status, and commitment-value evidence | `Deployment`, `Store Name`, `Vendor Name`, `PO Number`, `PO Date`, `Expected Delivery`, `PO Close Date/Partial Recieve Date`, `PO Status`, `Item Code`, `Item Name`, `Total Processed Qty`, `Remaining Balance Qty`, `Quantity`, `Unit`, `Unit Price`, `Total Item Cost` |
| Enterprise Entry Report - Stock Entry | captured_posist_report | GRN/stock-entry receipt quantity, price, tax, total, vendor, and PO reference | `Deployment Name`, `Store/Kitchen Name`, `Vendor Name`, `Date`, `Transaction Number`, `Invoice Number`, `PO Number`, `Item Code`, `Item Name`, `Quantity`, `Unit`, `Unit Price`, `Amount`, `Total Tax`, `Total` |

### Model Route And Relationship

`07_std_ct_purchase_order.sql -> 08_std_ct_purchase_receipt.sql -> 24_fact_ct_po_receipt_line.sql`

**Join/relationship logic:** Left join PO and receipt lines on source period + outlet + canonical PO number + item code; aggregate receipts before the join.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `item_code -> 14_dim_ct_item.sql.item_code`
- `vendor_name -> 16_dim_ct_vendor.sql.vendor_name`

### Calculation

**Final fields:** `vendor_name`, `gross_order_value`, `open_po_value`, `ordered_qty`, `received_qty`, `eligible_closed_line_flag`, `otif_success_flag`, `eligible_lead_time_deviation_days`, `delayed_po_flag`

**Formula:** `Use PO Fill Rate % and Vendor OTIF % Aggregate Formulas over Query 24.`

**Aggregation:** Group by vendor

### Exact Zoho Configuration

**Visual:** Summary or pivot

**Shelves/columns:**

- Columns: vendor, purchase, open liability, OTIF, fill, eligible lead deviation, delayed lines

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Vendor
- Ingredient category
- Item
- PO status

**Sort:** Open PO value descending

**Tooltips:**

- None

**Formatting:**

- None

### Guardrails

- Actual PO-to-GRN linkage was sparse, so OTIF remains a formula demonstration.
- Fill rate uses sums of quantities, never an average of row percentages.
- Do not average precomputed Query 30 percentages across outlets.

### How To Explain It

Vendor Scorecard starts from Enterprise Purchase Order Report, Enterprise Entry Report - Stock Entry. The model follows 07_std_ct_purchase_order.sql -> 08_std_ct_purchase_receipt.sql -> 24_fact_ct_po_receipt_line.sql at source period, outlet, purchase order, and item line. The relationship rule is: Left join PO and receipt lines on source period + outlet + canonical PO number + item code; aggregate receipts before the join. In Zoho, use group by vendor and render it as summary or pivot to answer: What purchase, exposure, fill, OTIF, lead, and delay profile does each vendor have?

# Page 3 - Consumption Variance & Menu Profitability

Connect actual and theoretical consumption to leakage, menu cost, sales, and margin.

<a id="ct-p3-actual-vs-theoretical"></a>
## CT_P3_Actual_vs_Theoretical - Actual vs Theoretical Consumption

**Business question:** For one UOM, where does actual ingredient consumption differ from theoretical?

**Final object:** chart / Grouped bar from `21_fact_ct_consumption_variance.sql`

**Final grain:** Source period, outlet, inventory item, and canonical UOM

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Enterprise Variance Report | captured_posist_report | Opening, purchase, transfer, return, closing, and actual-consumption movement bridge | `Deployment Name`, `StoreKitchen Name`, `Item Code`, `Item Name`, `Average Price`, `Opening Qty`, `Purchase Qty`, `Stock In Qty`, `Stock Out Qty`, `Return Qty`, `Closing Qty`, `Actual Consumption`, `Unit` |
| Gross/Net Margin Report | captured_posist_report | Sold menu-item quantities used by the theoretical model | `Store Name`, `Date`, `SKU Code / Item No`, `SKU / Item Name`, `Item Qty` |
| Item Recipe Report | captured_posist_report | Menu-item to ingredient quantity and UOM bridge | `Item Number`, `Item Name`, `Qty`, `Recipe Unit`, `Ingredient Code`, `Ingredient Name` |
| Closing Stock Report | captured_posist_report | Ingredient UOM and average-cost reference | `Item Code`, `Item Name`, `Unit Name`, `Average Price` |
| AUX Theoretical Consumption | synthetic_model_input | Synthetic three-month baseline derived from sales, recipe, UOM, and cost inputs | `source_period_code`, `outlet_code`, `item_code`, `canonical_uom`, `theoretical_consumption_qty`, `theoretical_consumption_value` |

### Model Route And Relationship

`20_fact_ct_actual_consumption.sql -> 19_fact_ct_theoretical_consumption.sql -> 21_fact_ct_consumption_variance.sql`

**Join/relationship logic:** Join actual and theoretical consumption on source period + outlet + item; calculate signed variance, positive leakage, and low-consumption check.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `item_code -> 14_dim_ct_item.sql.item_code`

### Calculation

**Final fields:** `item_code`, `actual_consumption_qty`, `theoretical_consumption_qty`, `canonical_uom`

**Formula:** `Display both fact measures at the same joined grain.`

**Aggregation:** Sum quantities only within one canonical UOM

### Exact Zoho Configuration

**Visual:** Grouped bar

**Shelves/columns:**

- X: ingredient
- Y: actual quantity and theoretical quantity

**Fixed report filters:**

- Exactly one canonical UOM

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Menu category
- Menu item
- Ingredient category
- Ingredient
- Canonical UOM

**Sort:** Absolute variance descending

**Tooltips:**

- None

**Formatting:**

- None

### Guardrails

- Positive leakage is not the same as signed variance.
- Low consumption is a data/process check, not a favorable saving.

### How To Explain It

Actual vs Theoretical Consumption starts from Enterprise Variance Report, Gross/Net Margin Report, Item Recipe Report, Closing Stock Report, AUX Theoretical Consumption. The model follows 20_fact_ct_actual_consumption.sql -> 19_fact_ct_theoretical_consumption.sql -> 21_fact_ct_consumption_variance.sql at source period, outlet, inventory item, and canonical uom. The relationship rule is: Join actual and theoretical consumption on source period + outlet + item; calculate signed variance, positive leakage, and low-consumption check. In Zoho, use sum quantities only within one canonical uom and render it as grouped bar to answer: For one UOM, where does actual ingredient consumption differ from theoretical?

<a id="ct-p3-category-contribution"></a>
## CT_P3_Category_Contribution - Category Contribution

**Business question:** What share of net sales comes from each menu category?

**Final object:** chart / Stacked bar or ring from `25_fact_ct_menu_profitability.sql`

**Final grain:** Source period, outlet, and menu item

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Gross/Net Margin Report | captured_posist_report | Bill-item sales, quantity, realized revenue, and source cost evidence | `Store Name`, `Date`, `Bill No.`, `Super Category`, `Category`, `SKU Code / Item No`, `SKU / Item Name`, `Item Qty`, `Net Sale Value`, `Purchase Value` |
| Item Recipe Report | captured_posist_report | Menu-item to ingredient quantity and UOM bridge | `Item Number`, `Item Name`, `Qty`, `Recipe Unit`, `Ingredient Code`, `Ingredient Name` |
| Closing Stock Report | captured_posist_report | Ingredient UOM and average-cost reference | `Item Code`, `Item Name`, `Unit Name`, `Average Price` |
| AUX Theoretical Consumption | synthetic_model_input | Synthetic three-month baseline derived from sales, recipe, UOM, and cost inputs | `source_period_code`, `outlet_code`, `item_code`, `canonical_uom`, `theoretical_consumption_qty`, `theoretical_consumption_value` |

### Model Route And Relationship

`01_std_ct_sales_item.sql -> 17_dim_ct_recipe_effective.sql -> 25_fact_ct_menu_profitability.sql`

**Join/relationship logic:** Aggregate menu sales and join effective recipe cost to calculate theoretical cost per unit, COGS, and gross margin.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `menu_item_code -> 15_dim_ct_menu_item.sql.menu_item_code`

### Calculation

**Final fields:** `category_name`, `net_sales`

**Formula:** `sum("net_sales") shown as percent of report total`

**Aggregation:** Sum net sales; Show Values As > % of Total

### Exact Zoho Configuration

**Visual:** Stacked bar or ring

**Shelves/columns:**

- Category: category name
- Measure: net sales

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Menu category
- Menu item
- Ingredient category
- Ingredient
- Canonical UOM

**Sort:** Net sales descending

**Tooltips:**

- None

**Formatting:**

- Percent of total

### Guardrails

- Menu gross margin percent is ratio of summed margin to summed sales.
- Do not average row-level margin percentages.
- Do not create a separate table aggregate formula for percent-of-total.

### How To Explain It

Category Contribution starts from Gross/Net Margin Report, Item Recipe Report, Closing Stock Report, AUX Theoretical Consumption. The model follows 01_std_ct_sales_item.sql -> 17_dim_ct_recipe_effective.sql -> 25_fact_ct_menu_profitability.sql at source period, outlet, and menu item. The relationship rule is: Aggregate menu sales and join effective recipe cost to calculate theoretical cost per unit, COGS, and gross margin. In Zoho, use sum net sales; show values as > % of total and render it as stacked bar or ring to answer: What share of net sales comes from each menu category?

<a id="ct-p3-consumption-bridge"></a>
## CT_P3_Consumption_Bridge - Consumption Bridge

**Business question:** How do opening, receipts, transfers, returns, and closing stock reconcile to actual consumption?

**Final object:** chart / Combination from `20_fact_ct_actual_consumption.sql`

**Final grain:** Source period, outlet, inventory item, and canonical UOM

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Enterprise Variance Report | captured_posist_report | Opening, purchase, transfer, return, closing, and actual-consumption movement bridge | `Deployment Name`, `StoreKitchen Name`, `Item Code`, `Item Name`, `Average Price`, `Opening Qty`, `Purchase Qty`, `Stock In Qty`, `Stock Out Qty`, `Return Qty`, `Closing Qty`, `Actual Consumption`, `Unit` |

### Model Route And Relationship

`RAWN_CT_enterprise_variance_normal-Copy -> 04_std_ct_inventory_period.sql -> 20_fact_ct_actual_consumption.sql`

**Join/relationship logic:** Actual consumption = opening + receipts + transfer in - transfer out - returns - closing.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `item_code -> 14_dim_ct_item.sql.item_code`

### Calculation

**Final fields:** `source_period_code`, `opening_qty`, `purchase_qty`, `transfer_in_qty`, `bridge_transfer_out_qty`, `bridge_return_qty`, `bridge_closing_qty`, `calculated_actual_consumption_qty`

**Formula:** `Physical bridge fields are already signed in Query 20.`

**Aggregation:** Sum each bridge component within one canonical UOM

### Exact Zoho Configuration

**Visual:** Combination

**Shelves/columns:**

- X: source period
- Bars: opening, purchase, transfer in, bridge transfer out, bridge return, bridge closing
- Line: calculated actual consumption

**Fixed report filters:**

- Canonical UOM user filter: select exactly one value for this quantity view

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Menu category
- Menu item
- Ingredient category
- Ingredient
- Canonical UOM

**Sort:** Business-relevant default order

**Tooltips:**

- Outlet
- Item
- Actual consumption value

**Formatting:**

- None

### Guardrails

- Signed bridge columns are report formula columns for presentation, not new source facts.
- Quantity totals require one canonical UOM.

### How To Explain It

Consumption Bridge starts from Enterprise Variance Report. The model follows RAWN_CT_enterprise_variance_normal-Copy -> 04_std_ct_inventory_period.sql -> 20_fact_ct_actual_consumption.sql at source period, outlet, inventory item, and canonical uom. The relationship rule is: Actual consumption = opening + receipts + transfer in - transfer out - returns - closing. In Zoho, use sum each bridge component within one canonical uom and render it as combination to answer: How do opening, receipts, transfers, returns, and closing stock reconcile to actual consumption?

<a id="ct-p3-consumption-leakage-rank"></a>
## CT_P3_Consumption_Leakage_Rank - Consumption Leakage Rank

**Business question:** Which ingredients create the highest positive consumption leakage value?

**Final object:** chart / Horizontal bar from `21_fact_ct_consumption_variance.sql`

**Final grain:** Source period, outlet, inventory item, and canonical UOM

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Enterprise Variance Report | captured_posist_report | Opening, purchase, transfer, return, closing, and actual-consumption movement bridge | `Deployment Name`, `StoreKitchen Name`, `Item Code`, `Item Name`, `Average Price`, `Opening Qty`, `Purchase Qty`, `Stock In Qty`, `Stock Out Qty`, `Return Qty`, `Closing Qty`, `Actual Consumption`, `Unit` |
| Gross/Net Margin Report | captured_posist_report | Sold menu-item quantities used by the theoretical model | `Store Name`, `Date`, `SKU Code / Item No`, `SKU / Item Name`, `Item Qty` |
| Item Recipe Report | captured_posist_report | Menu-item to ingredient quantity and UOM bridge | `Item Number`, `Item Name`, `Qty`, `Recipe Unit`, `Ingredient Code`, `Ingredient Name` |
| Closing Stock Report | captured_posist_report | Ingredient UOM and average-cost reference | `Item Code`, `Item Name`, `Unit Name`, `Average Price` |
| AUX Theoretical Consumption | synthetic_model_input | Synthetic three-month baseline derived from sales, recipe, UOM, and cost inputs | `source_period_code`, `outlet_code`, `item_code`, `canonical_uom`, `theoretical_consumption_qty`, `theoretical_consumption_value` |

### Model Route And Relationship

`20_fact_ct_actual_consumption.sql -> 19_fact_ct_theoretical_consumption.sql -> 21_fact_ct_consumption_variance.sql`

**Join/relationship logic:** Join actual and theoretical consumption on source period + outlet + item; calculate signed variance, positive leakage, and low-consumption check.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `item_code -> 14_dim_ct_item.sql.item_code`

### Calculation

**Final fields:** `item_code`, `leakage_value`, `consumption_variance_direction`

**Formula:** `sum("leakage_value")`

**Aggregation:** Sum leakage value

### Exact Zoho Configuration

**Visual:** Horizontal bar

**Shelves/columns:**

- Y: ingredient
- X: leakage value

**Fixed report filters:**

- Filter shelf: consumption_variance_direction / Individual Values / Include OVER_CONSUMPTION

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Menu category
- Menu item
- Ingredient category
- Ingredient
- Canonical UOM

**Sort:** Leakage value descending

**Tooltips:**

- None

**Formatting:**

- INR currency

### Guardrails

- Positive leakage is not the same as signed variance.
- Low consumption is a data/process check, not a favorable saving.

### How To Explain It

Consumption Leakage Rank starts from Enterprise Variance Report, Gross/Net Margin Report, Item Recipe Report, Closing Stock Report, AUX Theoretical Consumption. The model follows 20_fact_ct_actual_consumption.sql -> 19_fact_ct_theoretical_consumption.sql -> 21_fact_ct_consumption_variance.sql at source period, outlet, inventory item, and canonical uom. The relationship rule is: Join actual and theoretical consumption on source period + outlet + item; calculate signed variance, positive leakage, and low-consumption check. In Zoho, use sum leakage value and render it as horizontal bar to answer: Which ingredients create the highest positive consumption leakage value?

<a id="ct-p3-kpi-consumption-leakage"></a>
## CT_P3_KPI_Consumption_Leakage - Consumption Leakage Value

**Business question:** What positive actual-over-theoretical consumption variance is valued as leakage?

**Final object:** kpi / KPI widget from `21_fact_ct_consumption_variance.sql`

**Final grain:** Source period, outlet, inventory item, and canonical UOM

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Enterprise Variance Report | captured_posist_report | Opening, purchase, transfer, return, closing, and actual-consumption movement bridge | `Deployment Name`, `StoreKitchen Name`, `Item Code`, `Item Name`, `Average Price`, `Opening Qty`, `Purchase Qty`, `Stock In Qty`, `Stock Out Qty`, `Return Qty`, `Closing Qty`, `Actual Consumption`, `Unit` |
| Gross/Net Margin Report | captured_posist_report | Sold menu-item quantities used by the theoretical model | `Store Name`, `Date`, `SKU Code / Item No`, `SKU / Item Name`, `Item Qty` |
| Item Recipe Report | captured_posist_report | Menu-item to ingredient quantity and UOM bridge | `Item Number`, `Item Name`, `Qty`, `Recipe Unit`, `Ingredient Code`, `Ingredient Name` |
| Closing Stock Report | captured_posist_report | Ingredient UOM and average-cost reference | `Item Code`, `Item Name`, `Unit Name`, `Average Price` |
| AUX Theoretical Consumption | synthetic_model_input | Synthetic three-month baseline derived from sales, recipe, UOM, and cost inputs | `source_period_code`, `outlet_code`, `item_code`, `canonical_uom`, `theoretical_consumption_qty`, `theoretical_consumption_value` |

### Model Route And Relationship

`20_fact_ct_actual_consumption.sql -> 19_fact_ct_theoretical_consumption.sql -> 21_fact_ct_consumption_variance.sql`

**Join/relationship logic:** Join actual and theoretical consumption on source period + outlet + item; calculate signed variance, positive leakage, and low-consumption check.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `item_code -> 14_dim_ct_item.sql.item_code`

### Calculation

**Final fields:** `leakage_value`

**Formula:** `sum("leakage_value")`

**Aggregation:** Sum leakage value

### Exact Zoho Configuration

**Visual:** KPI widget

**Shelves/columns:**

- Data Column: leakage_value
- Show Value As: Sum
- Group By: blank

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Menu category
- Menu item
- Ingredient category
- Ingredient
- Canonical UOM

**Sort:** Business-relevant default order

**Tooltips:**

- None

**Formatting:**

- INR currency

### Guardrails

- Positive leakage is not the same as signed variance.
- Low consumption is a data/process check, not a favorable saving.
- Use value, not a mixed-UOM all-item quantity.

### How To Explain It

Consumption Leakage Value starts from Enterprise Variance Report, Gross/Net Margin Report, Item Recipe Report, Closing Stock Report, AUX Theoretical Consumption. The model follows 20_fact_ct_actual_consumption.sql -> 19_fact_ct_theoretical_consumption.sql -> 21_fact_ct_consumption_variance.sql at source period, outlet, inventory item, and canonical uom. The relationship rule is: Join actual and theoretical consumption on source period + outlet + item; calculate signed variance, positive leakage, and low-consumption check. In Zoho, use sum leakage value and render it as kpi widget to answer: What positive actual-over-theoretical consumption variance is valued as leakage?

<a id="ct-p3-kpi-menu-gross-margin"></a>
## CT_P3_KPI_Menu_Gross_Margin - Menu Gross Margin %

**Business question:** What share of net sales remains after theoretical menu COGS?

**Final object:** kpi / Saved Summary View from `25_fact_ct_menu_profitability.sql`

**Final grain:** Source period, outlet, and menu item

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Gross/Net Margin Report | captured_posist_report | Bill-item sales, quantity, realized revenue, and source cost evidence | `Store Name`, `Date`, `Bill No.`, `Super Category`, `Category`, `SKU Code / Item No`, `SKU / Item Name`, `Item Qty`, `Net Sale Value`, `Purchase Value` |
| Item Recipe Report | captured_posist_report | Menu-item to ingredient quantity and UOM bridge | `Item Number`, `Item Name`, `Qty`, `Recipe Unit`, `Ingredient Code`, `Ingredient Name` |
| Closing Stock Report | captured_posist_report | Ingredient UOM and average-cost reference | `Item Code`, `Item Name`, `Unit Name`, `Average Price` |
| AUX Theoretical Consumption | synthetic_model_input | Synthetic three-month baseline derived from sales, recipe, UOM, and cost inputs | `source_period_code`, `outlet_code`, `item_code`, `canonical_uom`, `theoretical_consumption_qty`, `theoretical_consumption_value` |

### Model Route And Relationship

`01_std_ct_sales_item.sql -> 17_dim_ct_recipe_effective.sql -> 25_fact_ct_menu_profitability.sql`

**Join/relationship logic:** Aggregate menu sales and join effective recipe cost to calculate theoretical cost per unit, COGS, and gross margin.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `menu_item_code -> 15_dim_ct_menu_item.sql.menu_item_code`

### Calculation

**Final fields:** `gross_margin_value`, `net_sales`

**Formula:** `Aggregate Formula "Menu Gross Margin %" in a saved Summary View.`

**Aggregation:** Ratio of summed gross margin value to summed net sales

### Exact Zoho Configuration

**Visual:** Saved Summary View

**Shelves/columns:**

- Summary value: Menu Gross Margin %
- Grouping: none

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Menu category
- Menu item
- Ingredient category
- Ingredient
- Canonical UOM

**Sort:** Business-relevant default order

**Tooltips:**

- None

**Formatting:**

- Percentage; expected display near 82.02% in all-period synthetic truth

### Guardrails

- Menu gross margin percent is ratio of summed margin to summed sales.
- Do not average row-level margin percentages.
- Never average gross_margin_percent.
- The Aggregate Formula is not selected from a direct KPI Widget Data Column list.

### How To Explain It

Menu Gross Margin % starts from Gross/Net Margin Report, Item Recipe Report, Closing Stock Report, AUX Theoretical Consumption. The model follows 01_std_ct_sales_item.sql -> 17_dim_ct_recipe_effective.sql -> 25_fact_ct_menu_profitability.sql at source period, outlet, and menu item. The relationship rule is: Aggregate menu sales and join effective recipe cost to calculate theoretical cost per unit, COGS, and gross margin. In Zoho, use ratio of summed gross margin value to summed net sales and render it as saved summary view to answer: What share of net sales remains after theoretical menu COGS?

<a id="ct-p3-kpi-net-sales"></a>
## CT_P3_KPI_Net_Sales - Net Sales

**Business question:** What net menu sales were realized in the selected scope?

**Final object:** kpi / KPI widget from `25_fact_ct_menu_profitability.sql`

**Final grain:** Source period, outlet, and menu item

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Gross/Net Margin Report | captured_posist_report | Bill-item sales, quantity, realized revenue, and source cost evidence | `Store Name`, `Date`, `Bill No.`, `Super Category`, `Category`, `SKU Code / Item No`, `SKU / Item Name`, `Item Qty`, `Net Sale Value`, `Purchase Value` |
| Item Recipe Report | captured_posist_report | Menu-item to ingredient quantity and UOM bridge | `Item Number`, `Item Name`, `Qty`, `Recipe Unit`, `Ingredient Code`, `Ingredient Name` |
| Closing Stock Report | captured_posist_report | Ingredient UOM and average-cost reference | `Item Code`, `Item Name`, `Unit Name`, `Average Price` |
| AUX Theoretical Consumption | synthetic_model_input | Synthetic three-month baseline derived from sales, recipe, UOM, and cost inputs | `source_period_code`, `outlet_code`, `item_code`, `canonical_uom`, `theoretical_consumption_qty`, `theoretical_consumption_value` |

### Model Route And Relationship

`01_std_ct_sales_item.sql -> 17_dim_ct_recipe_effective.sql -> 25_fact_ct_menu_profitability.sql`

**Join/relationship logic:** Aggregate menu sales and join effective recipe cost to calculate theoretical cost per unit, COGS, and gross margin.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `menu_item_code -> 15_dim_ct_menu_item.sql.menu_item_code`

### Calculation

**Final fields:** `net_sales`

**Formula:** `sum("net_sales")`

**Aggregation:** Sum net sales

### Exact Zoho Configuration

**Visual:** KPI widget

**Shelves/columns:**

- Data Column: net_sales
- Show Value As: Sum
- Group By: blank

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Menu category
- Menu item
- Ingredient category
- Ingredient
- Canonical UOM

**Sort:** Business-relevant default order

**Tooltips:**

- None

**Formatting:**

- INR currency

### Guardrails

- Menu gross margin percent is ratio of summed margin to summed sales.
- Do not average row-level margin percentages.

### How To Explain It

Net Sales starts from Gross/Net Margin Report, Item Recipe Report, Closing Stock Report, AUX Theoretical Consumption. The model follows 01_std_ct_sales_item.sql -> 17_dim_ct_recipe_effective.sql -> 25_fact_ct_menu_profitability.sql at source period, outlet, and menu item. The relationship rule is: Aggregate menu sales and join effective recipe cost to calculate theoretical cost per unit, COGS, and gross margin. In Zoho, use sum net sales and render it as kpi widget to answer: What net menu sales were realized in the selected scope?

<a id="ct-p3-kpi-quantity-sold"></a>
## CT_P3_KPI_Quantity_Sold - Quantity Sold

**Business question:** How many menu-item units were sold?

**Final object:** kpi / KPI widget from `25_fact_ct_menu_profitability.sql`

**Final grain:** Source period, outlet, and menu item

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Gross/Net Margin Report | captured_posist_report | Bill-item sales, quantity, realized revenue, and source cost evidence | `Store Name`, `Date`, `Bill No.`, `Super Category`, `Category`, `SKU Code / Item No`, `SKU / Item Name`, `Item Qty`, `Net Sale Value`, `Purchase Value` |
| Item Recipe Report | captured_posist_report | Menu-item to ingredient quantity and UOM bridge | `Item Number`, `Item Name`, `Qty`, `Recipe Unit`, `Ingredient Code`, `Ingredient Name` |
| Closing Stock Report | captured_posist_report | Ingredient UOM and average-cost reference | `Item Code`, `Item Name`, `Unit Name`, `Average Price` |
| AUX Theoretical Consumption | synthetic_model_input | Synthetic three-month baseline derived from sales, recipe, UOM, and cost inputs | `source_period_code`, `outlet_code`, `item_code`, `canonical_uom`, `theoretical_consumption_qty`, `theoretical_consumption_value` |

### Model Route And Relationship

`01_std_ct_sales_item.sql -> 17_dim_ct_recipe_effective.sql -> 25_fact_ct_menu_profitability.sql`

**Join/relationship logic:** Aggregate menu sales and join effective recipe cost to calculate theoretical cost per unit, COGS, and gross margin.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `menu_item_code -> 15_dim_ct_menu_item.sql.menu_item_code`

### Calculation

**Final fields:** `sold_qty`

**Formula:** `sum("sold_qty")`

**Aggregation:** Sum sold quantity

### Exact Zoho Configuration

**Visual:** KPI widget

**Shelves/columns:**

- Data Column: sold_qty
- Show Value As: Sum
- Group By: blank

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Menu category
- Menu item
- Ingredient category
- Ingredient
- Canonical UOM

**Sort:** Business-relevant default order

**Tooltips:**

- None

**Formatting:**

- Whole or decimal quantity as source requires

### Guardrails

- Menu gross margin percent is ratio of summed margin to summed sales.
- Do not average row-level margin percentages.

### How To Explain It

Quantity Sold starts from Gross/Net Margin Report, Item Recipe Report, Closing Stock Report, AUX Theoretical Consumption. The model follows 01_std_ct_sales_item.sql -> 17_dim_ct_recipe_effective.sql -> 25_fact_ct_menu_profitability.sql at source period, outlet, and menu item. The relationship rule is: Aggregate menu sales and join effective recipe cost to calculate theoretical cost per unit, COGS, and gross margin. In Zoho, use sum sold quantity and render it as kpi widget to answer: How many menu-item units were sold?

<a id="ct-p3-kpi-theoretical-cogs"></a>
## CT_P3_KPI_Theoretical_COGS - Theoretical COGS

**Business question:** What should the sold menu mix have cost under the effective recipe and normalized ingredient cost?

**Final object:** kpi / KPI widget from `25_fact_ct_menu_profitability.sql`

**Final grain:** Source period, outlet, and menu item

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Gross/Net Margin Report | captured_posist_report | Bill-item sales, quantity, realized revenue, and source cost evidence | `Store Name`, `Date`, `Bill No.`, `Super Category`, `Category`, `SKU Code / Item No`, `SKU / Item Name`, `Item Qty`, `Net Sale Value`, `Purchase Value` |
| Item Recipe Report | captured_posist_report | Menu-item to ingredient quantity and UOM bridge | `Item Number`, `Item Name`, `Qty`, `Recipe Unit`, `Ingredient Code`, `Ingredient Name` |
| Closing Stock Report | captured_posist_report | Ingredient UOM and average-cost reference | `Item Code`, `Item Name`, `Unit Name`, `Average Price` |
| AUX Theoretical Consumption | synthetic_model_input | Synthetic three-month baseline derived from sales, recipe, UOM, and cost inputs | `source_period_code`, `outlet_code`, `item_code`, `canonical_uom`, `theoretical_consumption_qty`, `theoretical_consumption_value` |

### Model Route And Relationship

`01_std_ct_sales_item.sql -> 17_dim_ct_recipe_effective.sql -> 25_fact_ct_menu_profitability.sql`

**Join/relationship logic:** Aggregate menu sales and join effective recipe cost to calculate theoretical cost per unit, COGS, and gross margin.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `menu_item_code -> 15_dim_ct_menu_item.sql.menu_item_code`

### Calculation

**Final fields:** `sold_qty`, `theoretical_cost_per_unit`, `theoretical_cogs`

**Formula:** `sum("theoretical_cogs")`

**Aggregation:** Sum theoretical COGS

### Exact Zoho Configuration

**Visual:** KPI widget

**Shelves/columns:**

- Data Column: theoretical_cogs
- Show Value As: Sum
- Group By: blank

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Menu category
- Menu item
- Ingredient category
- Ingredient
- Canonical UOM

**Sort:** Business-relevant default order

**Tooltips:**

- None

**Formatting:**

- INR currency

### Guardrails

- Menu gross margin percent is ratio of summed margin to summed sales.
- Do not average row-level margin percentages.

### How To Explain It

Theoretical COGS starts from Gross/Net Margin Report, Item Recipe Report, Closing Stock Report, AUX Theoretical Consumption. The model follows 01_std_ct_sales_item.sql -> 17_dim_ct_recipe_effective.sql -> 25_fact_ct_menu_profitability.sql at source period, outlet, and menu item. The relationship rule is: Aggregate menu sales and join effective recipe cost to calculate theoretical cost per unit, COGS, and gross margin. In Zoho, use sum theoretical cogs and render it as kpi widget to answer: What should the sold menu mix have cost under the effective recipe and normalized ingredient cost?

<a id="ct-p3-low-consumption-check"></a>
## CT_P3_Low_Consumption_Check - Low Consumption Check

**Business question:** Where is theoretical consumption higher than calculated actual consumption?

**Final object:** table / Tabular from `21_fact_ct_consumption_variance.sql`

**Final grain:** Source period, outlet, inventory item, and canonical UOM

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Enterprise Variance Report | captured_posist_report | Opening, purchase, transfer, return, closing, and actual-consumption movement bridge | `Deployment Name`, `StoreKitchen Name`, `Item Code`, `Item Name`, `Average Price`, `Opening Qty`, `Purchase Qty`, `Stock In Qty`, `Stock Out Qty`, `Return Qty`, `Closing Qty`, `Actual Consumption`, `Unit` |
| Gross/Net Margin Report | captured_posist_report | Sold menu-item quantities used by the theoretical model | `Store Name`, `Date`, `SKU Code / Item No`, `SKU / Item Name`, `Item Qty` |
| Item Recipe Report | captured_posist_report | Menu-item to ingredient quantity and UOM bridge | `Item Number`, `Item Name`, `Qty`, `Recipe Unit`, `Ingredient Code`, `Ingredient Name` |
| Closing Stock Report | captured_posist_report | Ingredient UOM and average-cost reference | `Item Code`, `Item Name`, `Unit Name`, `Average Price` |
| AUX Theoretical Consumption | synthetic_model_input | Synthetic three-month baseline derived from sales, recipe, UOM, and cost inputs | `source_period_code`, `outlet_code`, `item_code`, `canonical_uom`, `theoretical_consumption_qty`, `theoretical_consumption_value` |

### Model Route And Relationship

`20_fact_ct_actual_consumption.sql -> 19_fact_ct_theoretical_consumption.sql -> 21_fact_ct_consumption_variance.sql`

**Join/relationship logic:** Join actual and theoretical consumption on source period + outlet + item; calculate signed variance, positive leakage, and low-consumption check.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `item_code -> 14_dim_ct_item.sql.item_code`

### Calculation

**Final fields:** `outlet_code`, `item_code`, `actual_consumption_qty`, `theoretical_consumption_qty`, `low_consumption_qty`, `canonical_uom`, `consumption_variance_direction`

**Formula:** `low_consumption_qty is the positive under-consumption difference.`

**Aggregation:** Direct detail rows

### Exact Zoho Configuration

**Visual:** Tabular

**Shelves/columns:**

- Columns: outlet, ingredient, actual, theoretical, delta, UOM

**Fixed report filters:**

- Filter shelf: consumption_variance_direction / Individual Values / Include UNDER_CONSUMPTION
- Canonical UOM user filter: select exactly one value for quantity comparison

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Menu category
- Menu item
- Ingredient category
- Ingredient
- Canonical UOM

**Sort:** Low consumption quantity descending

**Tooltips:**

- None

**Formatting:**

- None

### Guardrails

- Positive leakage is not the same as signed variance.
- Low consumption is a data/process check, not a favorable saving.
- Title and explanation must frame this as a data/process check, not a saving.

### How To Explain It

Low Consumption Check starts from Enterprise Variance Report, Gross/Net Margin Report, Item Recipe Report, Closing Stock Report, AUX Theoretical Consumption. The model follows 20_fact_ct_actual_consumption.sql -> 19_fact_ct_theoretical_consumption.sql -> 21_fact_ct_consumption_variance.sql at source period, outlet, inventory item, and canonical uom. The relationship rule is: Join actual and theoretical consumption on source period + outlet + item; calculate signed variance, positive leakage, and low-consumption check. In Zoho, use direct detail rows and render it as tabular to answer: Where is theoretical consumption higher than calculated actual consumption?

<a id="ct-p3-menu-bcg"></a>
## CT_P3_Menu_BCG - Menu BCG

**Business question:** Which menu items are high/low volume and high/low margin under the demo thresholds?

**Final object:** chart / Bubble from `32_sum_ct_menu_profitability.sql`

**Final grain:** Source period, outlet, and menu item

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Gross/Net Margin Report | captured_posist_report | Bill-item sales, quantity, realized revenue, and source cost evidence | `Store Name`, `Date`, `Bill No.`, `Super Category`, `Category`, `SKU Code / Item No`, `SKU / Item Name`, `Item Qty`, `Net Sale Value`, `Purchase Value` |
| Item Recipe Report | captured_posist_report | Menu-item to ingredient quantity and UOM bridge | `Item Number`, `Item Name`, `Qty`, `Recipe Unit`, `Ingredient Code`, `Ingredient Name` |
| Closing Stock Report | captured_posist_report | Ingredient UOM and average-cost reference | `Item Code`, `Item Name`, `Unit Name`, `Average Price` |
| AUX Theoretical Consumption | synthetic_model_input | Synthetic three-month baseline derived from sales, recipe, UOM, and cost inputs | `source_period_code`, `outlet_code`, `item_code`, `canonical_uom`, `theoretical_consumption_qty`, `theoretical_consumption_value` |

### Model Route And Relationship

`25_fact_ct_menu_profitability.sql -> 32_sum_ct_menu_profitability.sql`

**Join/relationship logic:** Classify menu items into synthetic BCG quadrants from sold quantity and gross margin percent.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `menu_item_code -> 15_dim_ct_menu_item.sql.menu_item_code`

### Calculation

**Final fields:** `menu_item_code`, `sold_qty`, `gross_margin_percent`, `net_sales`, `bcg_quadrant`

**Formula:** `Quadrant is preclassified from sold quantity and gross margin percent.`

**Aggregation:** Direct summary at one period + one outlet + menu item

### Exact Zoho Configuration

**Visual:** Bubble

**Shelves/columns:**

- X: sold quantity
- Y: gross margin %
- Size: net sales
- Text: menu item
- Color: BCG quadrant

**Fixed report filters:**

- Exactly one source period
- Exactly one outlet or keep outlet visible

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Menu category
- Menu item
- Ingredient category
- Ingredient
- Canonical UOM

**Sort:** Business-relevant default order

**Tooltips:**

- None

**Formatting:**

- None

### Guardrails

- Use one source period and one outlet, or keep outlet visible.
- BCG thresholds are demonstration rules pending business approval.
- Thresholds are synthetic demonstration rules.

### How To Explain It

Menu BCG starts from Gross/Net Margin Report, Item Recipe Report, Closing Stock Report, AUX Theoretical Consumption. The model follows 25_fact_ct_menu_profitability.sql -> 32_sum_ct_menu_profitability.sql at source period, outlet, and menu item. The relationship rule is: Classify menu items into synthetic BCG quadrants from sold quantity and gross margin percent. In Zoho, use direct summary at one period + one outlet + menu item and render it as bubble to answer: Which menu items are high/low volume and high/low margin under the demo thresholds?

<a id="ct-p3-menu-cogs-detail"></a>
## CT_P3_Menu_COGS_Detail - Menu COGS Detail

**Business question:** How do sold quantity, recipe cost, COGS, sales, and margin reconcile for each menu item?

**Final object:** table / Tabular from `25_fact_ct_menu_profitability.sql`

**Final grain:** Source period, outlet, and menu item

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Gross/Net Margin Report | captured_posist_report | Bill-item sales, quantity, realized revenue, and source cost evidence | `Store Name`, `Date`, `Bill No.`, `Super Category`, `Category`, `SKU Code / Item No`, `SKU / Item Name`, `Item Qty`, `Net Sale Value`, `Purchase Value` |
| Item Recipe Report | captured_posist_report | Menu-item to ingredient quantity and UOM bridge | `Item Number`, `Item Name`, `Qty`, `Recipe Unit`, `Ingredient Code`, `Ingredient Name` |
| Closing Stock Report | captured_posist_report | Ingredient UOM and average-cost reference | `Item Code`, `Item Name`, `Unit Name`, `Average Price` |
| AUX Theoretical Consumption | synthetic_model_input | Synthetic three-month baseline derived from sales, recipe, UOM, and cost inputs | `source_period_code`, `outlet_code`, `item_code`, `canonical_uom`, `theoretical_consumption_qty`, `theoretical_consumption_value` |

### Model Route And Relationship

`01_std_ct_sales_item.sql -> 17_dim_ct_recipe_effective.sql -> 25_fact_ct_menu_profitability.sql`

**Join/relationship logic:** Aggregate menu sales and join effective recipe cost to calculate theoretical cost per unit, COGS, and gross margin.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `menu_item_code -> 15_dim_ct_menu_item.sql.menu_item_code`

### Calculation

**Final fields:** `menu_item_code`, `sold_qty`, `theoretical_cost_per_unit`, `theoretical_cogs`, `net_sales`, `gross_margin_value`, `gross_margin_percent`

**Formula:** `gross margin value = net sales - theoretical COGS`

**Aggregation:** Direct menu profitability rows

### Exact Zoho Configuration

**Visual:** Tabular

**Shelves/columns:**

- Columns: menu item, sold quantity, theoretical unit cost, COGS, net sales, margin

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Menu category
- Menu item
- Ingredient category
- Ingredient
- Canonical UOM

**Sort:** Net sales descending

**Tooltips:**

- None

**Formatting:**

- None

### Guardrails

- Menu gross margin percent is ratio of summed margin to summed sales.
- Do not average row-level margin percentages.

### How To Explain It

Menu COGS Detail starts from Gross/Net Margin Report, Item Recipe Report, Closing Stock Report, AUX Theoretical Consumption. The model follows 01_std_ct_sales_item.sql -> 17_dim_ct_recipe_effective.sql -> 25_fact_ct_menu_profitability.sql at source period, outlet, and menu item. The relationship rule is: Aggregate menu sales and join effective recipe cost to calculate theoretical cost per unit, COGS, and gross margin. In Zoho, use direct menu profitability rows and render it as tabular to answer: How do sold quantity, recipe cost, COGS, sales, and margin reconcile for each menu item?

<a id="ct-p3-menu-margin-rank"></a>
## CT_P3_Menu_Margin_Rank - Menu Margin Rank

**Business question:** Which menu items contribute the most gross margin value?

**Final object:** chart / Horizontal bar from `32_sum_ct_menu_profitability.sql`

**Final grain:** Source period, outlet, and menu item

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Gross/Net Margin Report | captured_posist_report | Bill-item sales, quantity, realized revenue, and source cost evidence | `Store Name`, `Date`, `Bill No.`, `Super Category`, `Category`, `SKU Code / Item No`, `SKU / Item Name`, `Item Qty`, `Net Sale Value`, `Purchase Value` |
| Item Recipe Report | captured_posist_report | Menu-item to ingredient quantity and UOM bridge | `Item Number`, `Item Name`, `Qty`, `Recipe Unit`, `Ingredient Code`, `Ingredient Name` |
| Closing Stock Report | captured_posist_report | Ingredient UOM and average-cost reference | `Item Code`, `Item Name`, `Unit Name`, `Average Price` |
| AUX Theoretical Consumption | synthetic_model_input | Synthetic three-month baseline derived from sales, recipe, UOM, and cost inputs | `source_period_code`, `outlet_code`, `item_code`, `canonical_uom`, `theoretical_consumption_qty`, `theoretical_consumption_value` |

### Model Route And Relationship

`25_fact_ct_menu_profitability.sql -> 32_sum_ct_menu_profitability.sql`

**Join/relationship logic:** Classify menu items into synthetic BCG quadrants from sold quantity and gross margin percent.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `menu_item_code -> 15_dim_ct_menu_item.sql.menu_item_code`

### Calculation

**Final fields:** `menu_item_code`, `gross_margin_value`, `theoretical_cogs`, `gross_margin_percent`

**Formula:** `sum("gross_margin_value")`

**Aggregation:** Sum margin value within selected period/outlet

### Exact Zoho Configuration

**Visual:** Horizontal bar

**Shelves/columns:**

- Y: menu item
- X: gross margin value

**Fixed report filters:**

- One source period for like-for-like ranking

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Menu category
- Menu item
- Ingredient category
- Ingredient
- Canonical UOM

**Sort:** Gross margin value descending

**Tooltips:**

- Theoretical COGS
- Gross margin %

**Formatting:**

- INR currency

### Guardrails

- Use one source period and one outlet, or keep outlet visible.
- BCG thresholds are demonstration rules pending business approval.

### How To Explain It

Menu Margin Rank starts from Gross/Net Margin Report, Item Recipe Report, Closing Stock Report, AUX Theoretical Consumption. The model follows 25_fact_ct_menu_profitability.sql -> 32_sum_ct_menu_profitability.sql at source period, outlet, and menu item. The relationship rule is: Classify menu items into synthetic BCG quadrants from sold quantity and gross margin percent. In Zoho, use sum margin value within selected period/outlet and render it as horizontal bar to answer: Which menu items contribute the most gross margin value?

<a id="ct-p3-outlet-item-heatmap"></a>
## CT_P3_Outlet_Item_Heatmap - Outlet Item Heatmap

**Business question:** How does menu/category performance vary across outlets?

**Final object:** chart / Heat map from `25_fact_ct_menu_profitability.sql`

**Final grain:** Source period, outlet, and menu item

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Gross/Net Margin Report | captured_posist_report | Bill-item sales, quantity, realized revenue, and source cost evidence | `Store Name`, `Date`, `Bill No.`, `Super Category`, `Category`, `SKU Code / Item No`, `SKU / Item Name`, `Item Qty`, `Net Sale Value`, `Purchase Value` |
| Item Recipe Report | captured_posist_report | Menu-item to ingredient quantity and UOM bridge | `Item Number`, `Item Name`, `Qty`, `Recipe Unit`, `Ingredient Code`, `Ingredient Name` |
| Closing Stock Report | captured_posist_report | Ingredient UOM and average-cost reference | `Item Code`, `Item Name`, `Unit Name`, `Average Price` |
| AUX Theoretical Consumption | synthetic_model_input | Synthetic three-month baseline derived from sales, recipe, UOM, and cost inputs | `source_period_code`, `outlet_code`, `item_code`, `canonical_uom`, `theoretical_consumption_qty`, `theoretical_consumption_value` |

### Model Route And Relationship

`01_std_ct_sales_item.sql -> 17_dim_ct_recipe_effective.sql -> 25_fact_ct_menu_profitability.sql`

**Join/relationship logic:** Aggregate menu sales and join effective recipe cost to calculate theoretical cost per unit, COGS, and gross margin.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `menu_item_code -> 15_dim_ct_menu_item.sql.menu_item_code`

### Calculation

**Final fields:** `outlet_code`, `menu_item_code`, `category_name`, `net_sales`, `sold_qty`

**Formula:** `sum("net_sales") or sum("sold_qty")`

**Aggregation:** Sum selected additive measure

### Exact Zoho Configuration

**Visual:** Heat map

**Shelves/columns:**

- X: menu item or category
- Y: outlet
- Color: net sales or sold quantity

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Menu category
- Menu item
- Ingredient category
- Ingredient
- Canonical UOM

**Sort:** Business-relevant default order

**Tooltips:**

- Gross margin value
- Theoretical COGS

**Formatting:**

- None

### Guardrails

- Menu gross margin percent is ratio of summed margin to summed sales.
- Do not average row-level margin percentages.

### How To Explain It

Outlet Item Heatmap starts from Gross/Net Margin Report, Item Recipe Report, Closing Stock Report, AUX Theoretical Consumption. The model follows 01_std_ct_sales_item.sql -> 17_dim_ct_recipe_effective.sql -> 25_fact_ct_menu_profitability.sql at source period, outlet, and menu item. The relationship rule is: Aggregate menu sales and join effective recipe cost to calculate theoretical cost per unit, COGS, and gross margin. In Zoho, use sum selected additive measure and render it as heat map to answer: How does menu/category performance vary across outlets?

<a id="ct-p3-sales-trend"></a>
## CT_P3_Sales_Trend - Sales Trend

**Business question:** How do net sales and menu quantity move by sales date?

**Final object:** chart / Line from `18_fact_ct_sales.sql`

**Final grain:** Sales date, outlet, bill, and menu item

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Gross/Net Margin Report | captured_posist_report | Bill-item sales, quantity, realized revenue, and source cost evidence | `Store Name`, `Date`, `Bill No.`, `Super Category`, `Category`, `SKU Code / Item No`, `SKU / Item Name`, `Item Qty`, `Net Sale Value`, `Purchase Value` |

### Model Route And Relationship

`RAWN_CT_gross_net_margin-Copy -> 01_std_ct_sales_item.sql -> 18_fact_ct_sales.sql`

**Join/relationship logic:** No cross-report join in the fact; preserve the validated bill-item grain.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `sales_date -> 12_dim_ct_date.sql.calendar_date`
- `item_code -> 15_dim_ct_menu_item.sql.menu_item_code`

### Calculation

**Final fields:** `sales_date`, `net_sales`, `sold_qty`

**Formula:** `sum("net_sales") and sum("sold_qty")`

**Aggregation:** Sum additive sales measures by date

### Exact Zoho Configuration

**Visual:** Line

**Shelves/columns:**

- X: sales date
- Y: net sales and sold quantity

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Menu category
- Menu item
- Ingredient category
- Ingredient
- Canonical UOM

**Sort:** Business-relevant default order

**Tooltips:**

- Outlet
- Menu item
- Category

**Formatting:**

- None

### Guardrails

- The sales item key is a menu item, not an inventory ingredient.
- Use source purchase value only where cost coverage is approved.

### How To Explain It

Sales Trend starts from Gross/Net Margin Report. The model follows RAWN_CT_gross_net_margin-Copy -> 01_std_ct_sales_item.sql -> 18_fact_ct_sales.sql at sales date, outlet, bill, and menu item. The relationship rule is: No cross-report join in the fact; preserve the validated bill-item grain. In Zoho, use sum additive sales measures by date and render it as line to answer: How do net sales and menu quantity move by sales date?

<a id="ct-p3-theoretical-consumption-detail"></a>
## CT_P3_Theoretical_Consumption_Detail - Theoretical Consumption Detail

**Business question:** What ingredient quantity and value should have been consumed?

**Final object:** table / Tabular from `19_fact_ct_theoretical_consumption.sql`

**Final grain:** Source period, outlet, ingredient, and canonical UOM

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Gross/Net Margin Report | captured_posist_report | Sold menu-item quantities used by the theoretical model | `Store Name`, `Date`, `SKU Code / Item No`, `SKU / Item Name`, `Item Qty` |
| Item Recipe Report | captured_posist_report | Menu-item to ingredient quantity and UOM bridge | `Item Number`, `Item Name`, `Qty`, `Recipe Unit`, `Ingredient Code`, `Ingredient Name` |
| Closing Stock Report | captured_posist_report | Ingredient UOM and average-cost reference | `Item Code`, `Item Name`, `Unit Name`, `Average Price` |
| AUX Theoretical Consumption | synthetic_model_input | Synthetic three-month baseline derived from sales, recipe, UOM, and cost inputs | `source_period_code`, `outlet_code`, `item_code`, `canonical_uom`, `theoretical_consumption_qty`, `theoretical_consumption_value` |

### Model Route And Relationship

`AUX_Theoretical_Consumption-Copy -> 03_std_ct_theoretical_consumption.sql -> 19_fact_ct_theoretical_consumption.sql`

**Join/relationship logic:** Sales quantity x governed recipe quantity x approved UOM conversion; cost value uses the normalized ingredient cost.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `item_code -> 14_dim_ct_item.sql.item_code`

### Calculation

**Final fields:** `outlet_code`, `item_code`, `theoretical_consumption_qty`, `theoretical_consumption_value`, `canonical_uom`, `average_unit_cost`

**Formula:** `Sold menu quantity x normalized recipe ingredient quantity; value x normalized average cost.`

**Aggregation:** Direct detail rows

### Exact Zoho Configuration

**Visual:** Tabular

**Shelves/columns:**

- Columns: outlet, ingredient, theoretical quantity/value, UOM, average cost

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Menu category
- Menu item
- Ingredient category
- Ingredient
- Canonical UOM

**Sort:** Theoretical consumption value descending

**Tooltips:**

- None

**Formatting:**

- None

### Guardrails

- The current three-month values are synthetic, while the POSIST source fields and formula pattern are factual.
- Quantity comparisons require one canonical UOM.

### How To Explain It

Theoretical Consumption Detail starts from Gross/Net Margin Report, Item Recipe Report, Closing Stock Report, AUX Theoretical Consumption. The model follows AUX_Theoretical_Consumption-Copy -> 03_std_ct_theoretical_consumption.sql -> 19_fact_ct_theoretical_consumption.sql at source period, outlet, ingredient, and canonical uom. The relationship rule is: Sales quantity x governed recipe quantity x approved UOM conversion; cost value uses the normalized ingredient cost. In Zoho, use direct detail rows and render it as tabular to answer: What ingredient quantity and value should have been consumed?

<a id="ct-p3-top-slow-menu-ranking"></a>
## CT_P3_Top_Slow_Menu_Ranking - Top / Slow Menu Ranking

**Business question:** Which menu items rank highest or lowest on the selected commercial measure?

**Final object:** chart / Horizontal bar from `32_sum_ct_menu_profitability.sql`

**Final grain:** Source period, outlet, and menu item

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Gross/Net Margin Report | captured_posist_report | Bill-item sales, quantity, realized revenue, and source cost evidence | `Store Name`, `Date`, `Bill No.`, `Super Category`, `Category`, `SKU Code / Item No`, `SKU / Item Name`, `Item Qty`, `Net Sale Value`, `Purchase Value` |
| Item Recipe Report | captured_posist_report | Menu-item to ingredient quantity and UOM bridge | `Item Number`, `Item Name`, `Qty`, `Recipe Unit`, `Ingredient Code`, `Ingredient Name` |
| Closing Stock Report | captured_posist_report | Ingredient UOM and average-cost reference | `Item Code`, `Item Name`, `Unit Name`, `Average Price` |
| AUX Theoretical Consumption | synthetic_model_input | Synthetic three-month baseline derived from sales, recipe, UOM, and cost inputs | `source_period_code`, `outlet_code`, `item_code`, `canonical_uom`, `theoretical_consumption_qty`, `theoretical_consumption_value` |

### Model Route And Relationship

`25_fact_ct_menu_profitability.sql -> 32_sum_ct_menu_profitability.sql`

**Join/relationship logic:** Classify menu items into synthetic BCG quadrants from sold quantity and gross margin percent.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `menu_item_code -> 15_dim_ct_menu_item.sql.menu_item_code`

### Calculation

**Final fields:** `menu_item_code`, `sold_qty`, `net_sales`, `theoretical_cogs`, `gross_margin_value`

**Formula:** `Use one selected ranking measure; all fields are already at menu summary grain.`

**Aggregation:** Sum selected additive measure

### Exact Zoho Configuration

**Visual:** Horizontal bar

**Shelves/columns:**

- Y: menu item
- X: selected sold quantity, net sales, COGS, or margin

**Fixed report filters:**

- One source period for like-for-like ranking

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Menu category
- Menu item
- Ingredient category
- Ingredient
- Canonical UOM

**Sort:** Selected metric ascending for slow or descending for top

**Tooltips:**

- None

**Formatting:**

- None

### Guardrails

- Use one source period and one outlet, or keep outlet visible.
- BCG thresholds are demonstration rules pending business approval.

### How To Explain It

Top / Slow Menu Ranking starts from Gross/Net Margin Report, Item Recipe Report, Closing Stock Report, AUX Theoretical Consumption. The model follows 25_fact_ct_menu_profitability.sql -> 32_sum_ct_menu_profitability.sql at source period, outlet, and menu item. The relationship rule is: Classify menu items into synthetic BCG quadrants from sold quantity and gross margin percent. In Zoho, use sum selected additive measure and render it as horizontal bar to answer: Which menu items rank highest or lowest on the selected commercial measure?

# Page 4 - SCM Descriptive Explorer & Data Quality

Provide governed totals, trends, drilldowns, exports, and explicit data-quality exceptions.

<a id="ct-p4-consumption-variance-trend"></a>
## CT_P4_Consumption_Variance_Trend - Consumption Variance Trend

**Business question:** How do signed consumption variance and positive leakage change by period?

**Final object:** chart / Bar / line from `21_fact_ct_consumption_variance.sql`

**Final grain:** Source period, outlet, inventory item, and canonical UOM

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Enterprise Variance Report | captured_posist_report | Opening, purchase, transfer, return, closing, and actual-consumption movement bridge | `Deployment Name`, `StoreKitchen Name`, `Item Code`, `Item Name`, `Average Price`, `Opening Qty`, `Purchase Qty`, `Stock In Qty`, `Stock Out Qty`, `Return Qty`, `Closing Qty`, `Actual Consumption`, `Unit` |
| Gross/Net Margin Report | captured_posist_report | Sold menu-item quantities used by the theoretical model | `Store Name`, `Date`, `SKU Code / Item No`, `SKU / Item Name`, `Item Qty` |
| Item Recipe Report | captured_posist_report | Menu-item to ingredient quantity and UOM bridge | `Item Number`, `Item Name`, `Qty`, `Recipe Unit`, `Ingredient Code`, `Ingredient Name` |
| Closing Stock Report | captured_posist_report | Ingredient UOM and average-cost reference | `Item Code`, `Item Name`, `Unit Name`, `Average Price` |
| AUX Theoretical Consumption | synthetic_model_input | Synthetic three-month baseline derived from sales, recipe, UOM, and cost inputs | `source_period_code`, `outlet_code`, `item_code`, `canonical_uom`, `theoretical_consumption_qty`, `theoretical_consumption_value` |

### Model Route And Relationship

`20_fact_ct_actual_consumption.sql -> 19_fact_ct_theoretical_consumption.sql -> 21_fact_ct_consumption_variance.sql`

**Join/relationship logic:** Join actual and theoretical consumption on source period + outlet + item; calculate signed variance, positive leakage, and low-consumption check.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `item_code -> 14_dim_ct_item.sql.item_code`

### Calculation

**Final fields:** `source_period_code`, `actual_consumption_value`, `theoretical_consumption_value`, `leakage_value`

**Formula:** `Signed variance = actual value - theoretical value; leakage is positive-only.`

**Aggregation:** Sum both explicitly labelled value measures

### Exact Zoho Configuration

**Visual:** Bar / line

**Shelves/columns:**

- X: source period
- Y: signed variance value and leakage value

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Item
- Vendor
- Exception type

**Sort:** Business-relevant default order

**Tooltips:**

- None

**Formatting:**

- INR currency

### Guardrails

- Positive leakage is not the same as signed variance.
- Low consumption is a data/process check, not a favorable saving.

### How To Explain It

Consumption Variance Trend starts from Enterprise Variance Report, Gross/Net Margin Report, Item Recipe Report, Closing Stock Report, AUX Theoretical Consumption. The model follows 20_fact_ct_actual_consumption.sql -> 19_fact_ct_theoretical_consumption.sql -> 21_fact_ct_consumption_variance.sql at source period, outlet, inventory item, and canonical uom. The relationship rule is: Join actual and theoretical consumption on source period + outlet + item; calculate signed variance, positive leakage, and low-consumption check. In Zoho, use sum both explicitly labelled value measures and render it as bar / line to answer: How do signed consumption variance and positive leakage change by period?

<a id="ct-p4-dq-negative-stock"></a>
## CT_P4_DQ_NEGATIVE_STOCK - Negative Stock Count

**Business question:** Closing quantity below zero

**Final object:** kpi / KPI widget from `34_fact_ct_data_quality_exception.sql`

**Final grain:** One generated exception record

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Closing Stock Report | captured_posist_report | Current quantity, average cost, and closing valuation evidence | `Deployment`, `Date`, `Generation Date`, `Item Code`, `Item Name`, `Category Name`, `Unit Name`, `Average Price`, `Total Qty`, `Total Amt` |
| Item Recipe Report | captured_posist_report | Menu-to-ingredient conversion | `Item Number`, `Qty`, `Recipe Unit`, `Ingredient Code`, `Ingredient Name` |
| AUX Menu Demand Forecast | synthetic_model_input | Synthetic seven-day menu demand and net-sales forecast | `source_period_code`, `outlet_code`, `menu_item_code`, `forecast_menu_qty`, `forecast_net_sales` |
| Gross/Net Margin Report | captured_posist_report | Bill-item sales, quantity, realized revenue, and source cost evidence | `Store Name`, `Date`, `Bill No.`, `Super Category`, `Category`, `SKU Code / Item No`, `SKU / Item Name`, `Item Qty`, `Net Sale Value`, `Purchase Value` |
| Enterprise Purchase Order Report | captured_posist_report | Ordered, processed, remaining, expected-date, status, and commitment-value evidence | `Deployment`, `Store Name`, `Vendor Name`, `PO Number`, `PO Date`, `Expected Delivery`, `PO Close Date/Partial Recieve Date`, `PO Status`, `Item Code`, `Item Name`, `Total Processed Qty`, `Remaining Balance Qty`, `Quantity`, `Unit`, `Unit Price`, `Total Item Cost` |
| Enterprise Entry Report - Stock Entry | captured_posist_report | GRN/stock-entry receipt quantity, price, tax, total, vendor, and PO reference | `Deployment Name`, `Store/Kitchen Name`, `Vendor Name`, `Date`, `Transaction Number`, `Invoice Number`, `PO Number`, `Item Code`, `Item Name`, `Quantity`, `Unit`, `Unit Price`, `Amount`, `Total Tax`, `Total` |

### Model Route And Relationship

`Governed source and model checks -> 34_fact_ct_data_quality_exception.sql`

**Join/relationship logic:** UNION explicit quality controls into a common exception grain with type, period, outlet, record key, item, and reference.

**Zoho lookups:**

- None

### Calculation

**Final fields:** `exception_type`, `exception_count`

**Formula:** `sum("exception_count")`

**Aggregation:** Sum exception count

### Exact Zoho Configuration

**Visual:** KPI widget

**Shelves/columns:**

- Data Column: exception_count
- Show Value As: Sum
- Group By: blank

**Fixed report filters:**

- Filter shelf: exception_type / Individual Values / Include NEGATIVE_STOCK

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Item
- Vendor
- Exception type

**Sort:** Business-relevant default order

**Tooltips:**

- None

**Formatting:**

- Whole number

### Guardrails

- Do not create outlet/item lookups; ALL and blank keys are intentional.
- A zero count means the check ran and found no exception.
- Use the Page 4 Exception Type user filter for the shared detail table; a single-number widget has no category dimension to pass.

### How To Explain It

Negative Stock Count starts from Closing Stock Report, Item Recipe Report, AUX Menu Demand Forecast, Gross/Net Margin Report, Enterprise Purchase Order Report, Enterprise Entry Report - Stock Entry. The model follows Governed source and model checks -> 34_fact_ct_data_quality_exception.sql at one generated exception record. The relationship rule is: UNION explicit quality controls into a common exception grain with type, period, outlet, record key, item, and reference. In Zoho, use sum exception count and render it as kpi widget to answer: Closing quantity below zero

<a id="ct-p4-dq-open-po-missing-expected-delivery"></a>
## CT_P4_DQ_OPEN_PO_MISSING_EXPECTED_DELIVERY - Open PO Missing Expected Delivery Count

**Business question:** Open PO lacks an expected delivery date

**Final object:** kpi / KPI widget from `34_fact_ct_data_quality_exception.sql`

**Final grain:** One generated exception record

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Closing Stock Report | captured_posist_report | Current quantity, average cost, and closing valuation evidence | `Deployment`, `Date`, `Generation Date`, `Item Code`, `Item Name`, `Category Name`, `Unit Name`, `Average Price`, `Total Qty`, `Total Amt` |
| Item Recipe Report | captured_posist_report | Menu-to-ingredient conversion | `Item Number`, `Qty`, `Recipe Unit`, `Ingredient Code`, `Ingredient Name` |
| AUX Menu Demand Forecast | synthetic_model_input | Synthetic seven-day menu demand and net-sales forecast | `source_period_code`, `outlet_code`, `menu_item_code`, `forecast_menu_qty`, `forecast_net_sales` |
| Gross/Net Margin Report | captured_posist_report | Bill-item sales, quantity, realized revenue, and source cost evidence | `Store Name`, `Date`, `Bill No.`, `Super Category`, `Category`, `SKU Code / Item No`, `SKU / Item Name`, `Item Qty`, `Net Sale Value`, `Purchase Value` |
| Enterprise Purchase Order Report | captured_posist_report | Ordered, processed, remaining, expected-date, status, and commitment-value evidence | `Deployment`, `Store Name`, `Vendor Name`, `PO Number`, `PO Date`, `Expected Delivery`, `PO Close Date/Partial Recieve Date`, `PO Status`, `Item Code`, `Item Name`, `Total Processed Qty`, `Remaining Balance Qty`, `Quantity`, `Unit`, `Unit Price`, `Total Item Cost` |
| Enterprise Entry Report - Stock Entry | captured_posist_report | GRN/stock-entry receipt quantity, price, tax, total, vendor, and PO reference | `Deployment Name`, `Store/Kitchen Name`, `Vendor Name`, `Date`, `Transaction Number`, `Invoice Number`, `PO Number`, `Item Code`, `Item Name`, `Quantity`, `Unit`, `Unit Price`, `Amount`, `Total Tax`, `Total` |

### Model Route And Relationship

`Governed source and model checks -> 34_fact_ct_data_quality_exception.sql`

**Join/relationship logic:** UNION explicit quality controls into a common exception grain with type, period, outlet, record key, item, and reference.

**Zoho lookups:**

- None

### Calculation

**Final fields:** `exception_type`, `exception_count`

**Formula:** `sum("exception_count")`

**Aggregation:** Sum exception count

### Exact Zoho Configuration

**Visual:** KPI widget

**Shelves/columns:**

- Data Column: exception_count
- Show Value As: Sum
- Group By: blank

**Fixed report filters:**

- Filter shelf: exception_type / Individual Values / Include OPEN_PO_MISSING_EXPECTED_DELIVERY

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Item
- Vendor
- Exception type

**Sort:** Business-relevant default order

**Tooltips:**

- None

**Formatting:**

- Whole number

### Guardrails

- Do not create outlet/item lookups; ALL and blank keys are intentional.
- A zero count means the check ran and found no exception.
- Use the Page 4 Exception Type user filter for the shared detail table; a single-number widget has no category dimension to pass.

### How To Explain It

Open PO Missing Expected Delivery Count starts from Closing Stock Report, Item Recipe Report, AUX Menu Demand Forecast, Gross/Net Margin Report, Enterprise Purchase Order Report, Enterprise Entry Report - Stock Entry. The model follows Governed source and model checks -> 34_fact_ct_data_quality_exception.sql at one generated exception record. The relationship rule is: UNION explicit quality controls into a common exception grain with type, period, outlet, record key, item, and reference. In Zoho, use sum exception count and render it as kpi widget to answer: Open PO lacks an expected delivery date

<a id="ct-p4-dq-operational-item-missing-master"></a>
## CT_P4_DQ_OPERATIONAL_ITEM_MISSING_MASTER - Operational Items Missing Master Count

**Business question:** Operational item does not resolve to the canonical item reference

**Final object:** kpi / KPI widget from `34_fact_ct_data_quality_exception.sql`

**Final grain:** One generated exception record

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Closing Stock Report | captured_posist_report | Current quantity, average cost, and closing valuation evidence | `Deployment`, `Date`, `Generation Date`, `Item Code`, `Item Name`, `Category Name`, `Unit Name`, `Average Price`, `Total Qty`, `Total Amt` |
| Item Recipe Report | captured_posist_report | Menu-to-ingredient conversion | `Item Number`, `Qty`, `Recipe Unit`, `Ingredient Code`, `Ingredient Name` |
| AUX Menu Demand Forecast | synthetic_model_input | Synthetic seven-day menu demand and net-sales forecast | `source_period_code`, `outlet_code`, `menu_item_code`, `forecast_menu_qty`, `forecast_net_sales` |
| Gross/Net Margin Report | captured_posist_report | Bill-item sales, quantity, realized revenue, and source cost evidence | `Store Name`, `Date`, `Bill No.`, `Super Category`, `Category`, `SKU Code / Item No`, `SKU / Item Name`, `Item Qty`, `Net Sale Value`, `Purchase Value` |
| Enterprise Purchase Order Report | captured_posist_report | Ordered, processed, remaining, expected-date, status, and commitment-value evidence | `Deployment`, `Store Name`, `Vendor Name`, `PO Number`, `PO Date`, `Expected Delivery`, `PO Close Date/Partial Recieve Date`, `PO Status`, `Item Code`, `Item Name`, `Total Processed Qty`, `Remaining Balance Qty`, `Quantity`, `Unit`, `Unit Price`, `Total Item Cost` |
| Enterprise Entry Report - Stock Entry | captured_posist_report | GRN/stock-entry receipt quantity, price, tax, total, vendor, and PO reference | `Deployment Name`, `Store/Kitchen Name`, `Vendor Name`, `Date`, `Transaction Number`, `Invoice Number`, `PO Number`, `Item Code`, `Item Name`, `Quantity`, `Unit`, `Unit Price`, `Amount`, `Total Tax`, `Total` |

### Model Route And Relationship

`Governed source and model checks -> 34_fact_ct_data_quality_exception.sql`

**Join/relationship logic:** UNION explicit quality controls into a common exception grain with type, period, outlet, record key, item, and reference.

**Zoho lookups:**

- None

### Calculation

**Final fields:** `exception_type`, `exception_count`

**Formula:** `sum("exception_count")`

**Aggregation:** Sum exception count

### Exact Zoho Configuration

**Visual:** KPI widget

**Shelves/columns:**

- Data Column: exception_count
- Show Value As: Sum
- Group By: blank

**Fixed report filters:**

- Filter shelf: exception_type / Individual Values / Include OPERATIONAL_ITEM_MISSING_MASTER

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Item
- Vendor
- Exception type

**Sort:** Business-relevant default order

**Tooltips:**

- None

**Formatting:**

- Whole number

### Guardrails

- Do not create outlet/item lookups; ALL and blank keys are intentional.
- A zero count means the check ran and found no exception.
- Use the Page 4 Exception Type user filter for the shared detail table; a single-number widget has no category dimension to pass.

### How To Explain It

Operational Items Missing Master Count starts from Closing Stock Report, Item Recipe Report, AUX Menu Demand Forecast, Gross/Net Margin Report, Enterprise Purchase Order Report, Enterprise Entry Report - Stock Entry. The model follows Governed source and model checks -> 34_fact_ct_data_quality_exception.sql at one generated exception record. The relationship rule is: UNION explicit quality controls into a common exception grain with type, period, outlet, record key, item, and reference. In Zoho, use sum exception count and render it as kpi widget to answer: Operational item does not resolve to the canonical item reference

<a id="ct-p4-dq-sold-item-missing-recipe"></a>
## CT_P4_DQ_SOLD_ITEM_MISSING_RECIPE - Sold Items Missing Recipe Count

**Business question:** Sold menu item has no effective recipe

**Final object:** kpi / KPI widget from `34_fact_ct_data_quality_exception.sql`

**Final grain:** One generated exception record

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Closing Stock Report | captured_posist_report | Current quantity, average cost, and closing valuation evidence | `Deployment`, `Date`, `Generation Date`, `Item Code`, `Item Name`, `Category Name`, `Unit Name`, `Average Price`, `Total Qty`, `Total Amt` |
| Item Recipe Report | captured_posist_report | Menu-to-ingredient conversion | `Item Number`, `Qty`, `Recipe Unit`, `Ingredient Code`, `Ingredient Name` |
| AUX Menu Demand Forecast | synthetic_model_input | Synthetic seven-day menu demand and net-sales forecast | `source_period_code`, `outlet_code`, `menu_item_code`, `forecast_menu_qty`, `forecast_net_sales` |
| Gross/Net Margin Report | captured_posist_report | Bill-item sales, quantity, realized revenue, and source cost evidence | `Store Name`, `Date`, `Bill No.`, `Super Category`, `Category`, `SKU Code / Item No`, `SKU / Item Name`, `Item Qty`, `Net Sale Value`, `Purchase Value` |
| Enterprise Purchase Order Report | captured_posist_report | Ordered, processed, remaining, expected-date, status, and commitment-value evidence | `Deployment`, `Store Name`, `Vendor Name`, `PO Number`, `PO Date`, `Expected Delivery`, `PO Close Date/Partial Recieve Date`, `PO Status`, `Item Code`, `Item Name`, `Total Processed Qty`, `Remaining Balance Qty`, `Quantity`, `Unit`, `Unit Price`, `Total Item Cost` |
| Enterprise Entry Report - Stock Entry | captured_posist_report | GRN/stock-entry receipt quantity, price, tax, total, vendor, and PO reference | `Deployment Name`, `Store/Kitchen Name`, `Vendor Name`, `Date`, `Transaction Number`, `Invoice Number`, `PO Number`, `Item Code`, `Item Name`, `Quantity`, `Unit`, `Unit Price`, `Amount`, `Total Tax`, `Total` |

### Model Route And Relationship

`Governed source and model checks -> 34_fact_ct_data_quality_exception.sql`

**Join/relationship logic:** UNION explicit quality controls into a common exception grain with type, period, outlet, record key, item, and reference.

**Zoho lookups:**

- None

### Calculation

**Final fields:** `exception_type`, `exception_count`

**Formula:** `sum("exception_count")`

**Aggregation:** Sum exception count

### Exact Zoho Configuration

**Visual:** KPI widget

**Shelves/columns:**

- Data Column: exception_count
- Show Value As: Sum
- Group By: blank

**Fixed report filters:**

- Filter shelf: exception_type / Individual Values / Include SOLD_ITEM_MISSING_RECIPE

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Item
- Vendor
- Exception type

**Sort:** Business-relevant default order

**Tooltips:**

- None

**Formatting:**

- Whole number

### Guardrails

- Do not create outlet/item lookups; ALL and blank keys are intentional.
- A zero count means the check ran and found no exception.
- Use the Page 4 Exception Type user filter for the shared detail table; a single-number widget has no category dimension to pass.

### How To Explain It

Sold Items Missing Recipe Count starts from Closing Stock Report, Item Recipe Report, AUX Menu Demand Forecast, Gross/Net Margin Report, Enterprise Purchase Order Report, Enterprise Entry Report - Stock Entry. The model follows Governed source and model checks -> 34_fact_ct_data_quality_exception.sql at one generated exception record. The relationship rule is: UNION explicit quality controls into a common exception grain with type, period, outlet, record key, item, and reference. In Zoho, use sum exception count and render it as kpi widget to answer: Sold menu item has no effective recipe

<a id="ct-p4-dq-uom-mismatch-without-conversion"></a>
## CT_P4_DQ_UOM_MISMATCH_WITHOUT_CONVERSION - UOM Mismatch Without Conversion Count

**Business question:** Observed UOMs cannot be governed by an approved conversion

**Final object:** kpi / KPI widget from `34_fact_ct_data_quality_exception.sql`

**Final grain:** One generated exception record

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Closing Stock Report | captured_posist_report | Current quantity, average cost, and closing valuation evidence | `Deployment`, `Date`, `Generation Date`, `Item Code`, `Item Name`, `Category Name`, `Unit Name`, `Average Price`, `Total Qty`, `Total Amt` |
| Item Recipe Report | captured_posist_report | Menu-to-ingredient conversion | `Item Number`, `Qty`, `Recipe Unit`, `Ingredient Code`, `Ingredient Name` |
| AUX Menu Demand Forecast | synthetic_model_input | Synthetic seven-day menu demand and net-sales forecast | `source_period_code`, `outlet_code`, `menu_item_code`, `forecast_menu_qty`, `forecast_net_sales` |
| Gross/Net Margin Report | captured_posist_report | Bill-item sales, quantity, realized revenue, and source cost evidence | `Store Name`, `Date`, `Bill No.`, `Super Category`, `Category`, `SKU Code / Item No`, `SKU / Item Name`, `Item Qty`, `Net Sale Value`, `Purchase Value` |
| Enterprise Purchase Order Report | captured_posist_report | Ordered, processed, remaining, expected-date, status, and commitment-value evidence | `Deployment`, `Store Name`, `Vendor Name`, `PO Number`, `PO Date`, `Expected Delivery`, `PO Close Date/Partial Recieve Date`, `PO Status`, `Item Code`, `Item Name`, `Total Processed Qty`, `Remaining Balance Qty`, `Quantity`, `Unit`, `Unit Price`, `Total Item Cost` |
| Enterprise Entry Report - Stock Entry | captured_posist_report | GRN/stock-entry receipt quantity, price, tax, total, vendor, and PO reference | `Deployment Name`, `Store/Kitchen Name`, `Vendor Name`, `Date`, `Transaction Number`, `Invoice Number`, `PO Number`, `Item Code`, `Item Name`, `Quantity`, `Unit`, `Unit Price`, `Amount`, `Total Tax`, `Total` |

### Model Route And Relationship

`Governed source and model checks -> 34_fact_ct_data_quality_exception.sql`

**Join/relationship logic:** UNION explicit quality controls into a common exception grain with type, period, outlet, record key, item, and reference.

**Zoho lookups:**

- None

### Calculation

**Final fields:** `exception_type`, `exception_count`

**Formula:** `sum("exception_count")`

**Aggregation:** Sum exception count

### Exact Zoho Configuration

**Visual:** KPI widget

**Shelves/columns:**

- Data Column: exception_count
- Show Value As: Sum
- Group By: blank

**Fixed report filters:**

- Filter shelf: exception_type / Individual Values / Include UOM_MISMATCH_WITHOUT_CONVERSION

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Item
- Vendor
- Exception type

**Sort:** Business-relevant default order

**Tooltips:**

- None

**Formatting:**

- Whole number

### Guardrails

- Do not create outlet/item lookups; ALL and blank keys are intentional.
- A zero count means the check ran and found no exception.
- Use the Page 4 Exception Type user filter for the shared detail table; a single-number widget has no category dimension to pass.

### How To Explain It

UOM Mismatch Without Conversion Count starts from Closing Stock Report, Item Recipe Report, AUX Menu Demand Forecast, Gross/Net Margin Report, Enterprise Purchase Order Report, Enterprise Entry Report - Stock Entry. The model follows Governed source and model checks -> 34_fact_ct_data_quality_exception.sql at one generated exception record. The relationship rule is: UNION explicit quality controls into a common exception grain with type, period, outlet, record key, item, and reference. In Zoho, use sum exception count and render it as kpi widget to answer: Observed UOMs cannot be governed by an approved conversion

<a id="ct-p4-dq-zero-stock-with-demand"></a>
## CT_P4_DQ_ZERO_STOCK_WITH_DEMAND - Zero Stock With Demand Count

**Business question:** Zero closing stock while forecast demand is positive

**Final object:** kpi / KPI widget from `34_fact_ct_data_quality_exception.sql`

**Final grain:** One generated exception record

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Closing Stock Report | captured_posist_report | Current quantity, average cost, and closing valuation evidence | `Deployment`, `Date`, `Generation Date`, `Item Code`, `Item Name`, `Category Name`, `Unit Name`, `Average Price`, `Total Qty`, `Total Amt` |
| Item Recipe Report | captured_posist_report | Menu-to-ingredient conversion | `Item Number`, `Qty`, `Recipe Unit`, `Ingredient Code`, `Ingredient Name` |
| AUX Menu Demand Forecast | synthetic_model_input | Synthetic seven-day menu demand and net-sales forecast | `source_period_code`, `outlet_code`, `menu_item_code`, `forecast_menu_qty`, `forecast_net_sales` |
| Gross/Net Margin Report | captured_posist_report | Bill-item sales, quantity, realized revenue, and source cost evidence | `Store Name`, `Date`, `Bill No.`, `Super Category`, `Category`, `SKU Code / Item No`, `SKU / Item Name`, `Item Qty`, `Net Sale Value`, `Purchase Value` |
| Enterprise Purchase Order Report | captured_posist_report | Ordered, processed, remaining, expected-date, status, and commitment-value evidence | `Deployment`, `Store Name`, `Vendor Name`, `PO Number`, `PO Date`, `Expected Delivery`, `PO Close Date/Partial Recieve Date`, `PO Status`, `Item Code`, `Item Name`, `Total Processed Qty`, `Remaining Balance Qty`, `Quantity`, `Unit`, `Unit Price`, `Total Item Cost` |
| Enterprise Entry Report - Stock Entry | captured_posist_report | GRN/stock-entry receipt quantity, price, tax, total, vendor, and PO reference | `Deployment Name`, `Store/Kitchen Name`, `Vendor Name`, `Date`, `Transaction Number`, `Invoice Number`, `PO Number`, `Item Code`, `Item Name`, `Quantity`, `Unit`, `Unit Price`, `Amount`, `Total Tax`, `Total` |

### Model Route And Relationship

`Governed source and model checks -> 34_fact_ct_data_quality_exception.sql`

**Join/relationship logic:** UNION explicit quality controls into a common exception grain with type, period, outlet, record key, item, and reference.

**Zoho lookups:**

- None

### Calculation

**Final fields:** `exception_type`, `exception_count`

**Formula:** `sum("exception_count")`

**Aggregation:** Sum exception count

### Exact Zoho Configuration

**Visual:** KPI widget

**Shelves/columns:**

- Data Column: exception_count
- Show Value As: Sum
- Group By: blank

**Fixed report filters:**

- Filter shelf: exception_type / Individual Values / Include ZERO_STOCK_WITH_DEMAND

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Item
- Vendor
- Exception type

**Sort:** Business-relevant default order

**Tooltips:**

- None

**Formatting:**

- Whole number

### Guardrails

- Do not create outlet/item lookups; ALL and blank keys are intentional.
- A zero count means the check ran and found no exception.
- Use the Page 4 Exception Type user filter for the shared detail table; a single-number widget has no category dimension to pass.

### How To Explain It

Zero Stock With Demand Count starts from Closing Stock Report, Item Recipe Report, AUX Menu Demand Forecast, Gross/Net Margin Report, Enterprise Purchase Order Report, Enterprise Entry Report - Stock Entry. The model follows Governed source and model checks -> 34_fact_ct_data_quality_exception.sql at one generated exception record. The relationship rule is: UNION explicit quality controls into a common exception grain with type, period, outlet, record key, item, and reference. In Zoho, use sum exception count and render it as kpi widget to answer: Zero closing stock while forecast demand is positive

<a id="ct-p4-data-quality-detail"></a>
## CT_P4_Data_Quality_Detail - Data Quality Detail

**Business question:** Which exact governed exception records sit behind each quality tile?

**Final object:** table / Tabular from `34_fact_ct_data_quality_exception.sql`

**Final grain:** One generated exception record

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Closing Stock Report | captured_posist_report | Current quantity, average cost, and closing valuation evidence | `Deployment`, `Date`, `Generation Date`, `Item Code`, `Item Name`, `Category Name`, `Unit Name`, `Average Price`, `Total Qty`, `Total Amt` |
| Item Recipe Report | captured_posist_report | Menu-to-ingredient conversion | `Item Number`, `Qty`, `Recipe Unit`, `Ingredient Code`, `Ingredient Name` |
| AUX Menu Demand Forecast | synthetic_model_input | Synthetic seven-day menu demand and net-sales forecast | `source_period_code`, `outlet_code`, `menu_item_code`, `forecast_menu_qty`, `forecast_net_sales` |
| Gross/Net Margin Report | captured_posist_report | Bill-item sales, quantity, realized revenue, and source cost evidence | `Store Name`, `Date`, `Bill No.`, `Super Category`, `Category`, `SKU Code / Item No`, `SKU / Item Name`, `Item Qty`, `Net Sale Value`, `Purchase Value` |
| Enterprise Purchase Order Report | captured_posist_report | Ordered, processed, remaining, expected-date, status, and commitment-value evidence | `Deployment`, `Store Name`, `Vendor Name`, `PO Number`, `PO Date`, `Expected Delivery`, `PO Close Date/Partial Recieve Date`, `PO Status`, `Item Code`, `Item Name`, `Total Processed Qty`, `Remaining Balance Qty`, `Quantity`, `Unit`, `Unit Price`, `Total Item Cost` |
| Enterprise Entry Report - Stock Entry | captured_posist_report | GRN/stock-entry receipt quantity, price, tax, total, vendor, and PO reference | `Deployment Name`, `Store/Kitchen Name`, `Vendor Name`, `Date`, `Transaction Number`, `Invoice Number`, `PO Number`, `Item Code`, `Item Name`, `Quantity`, `Unit`, `Unit Price`, `Amount`, `Total Tax`, `Total` |

### Model Route And Relationship

`Governed source and model checks -> 34_fact_ct_data_quality_exception.sql`

**Join/relationship logic:** UNION explicit quality controls into a common exception grain with type, period, outlet, record key, item, and reference.

**Zoho lookups:**

- None

### Calculation

**Final fields:** `exception_type`, `source_period_code`, `outlet_code`, `record_key`, `item_code`, `reference_number`, `definition`, `exception_count`

**Formula:** `Direct generated exception rows.`

**Aggregation:** One row per generated exception record

### Exact Zoho Configuration

**Visual:** Tabular

**Shelves/columns:**

- Columns: exception type, period, outlet, record key, item, PO/reference, definition

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Item
- Vendor
- Exception type

**Sort:** Exception type, period, outlet, record key

**Tooltips:**

- None

**Formatting:**

- Enable underlying data and export

### Guardrails

- Do not create outlet/item lookups; ALL and blank keys are intentional.
- A zero count means the check ran and found no exception.

### How To Explain It

Data Quality Detail starts from Closing Stock Report, Item Recipe Report, AUX Menu Demand Forecast, Gross/Net Margin Report, Enterprise Purchase Order Report, Enterprise Entry Report - Stock Entry. The model follows Governed source and model checks -> 34_fact_ct_data_quality_exception.sql at one generated exception record. The relationship rule is: UNION explicit quality controls into a common exception grain with type, period, outlet, record key, item, and reference. In Zoho, use one row per generated exception record and render it as tabular to answer: Which exact governed exception records sit behind each quality tile?

<a id="ct-p4-descriptive-explorer"></a>
## CT_P4_Descriptive_Explorer - SCM Descriptive Explorer

**Business question:** What governed SCM values can be drilled and exported by period and outlet?

**Final object:** table / Pivot or tabular from `33_sum_ct_scm_monthly.sql`

**Final grain:** Source period and outlet

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Gross/Net Margin Report | captured_posist_report | Bill-item sales, quantity, realized revenue, and source cost evidence | `Store Name`, `Date`, `Bill No.`, `Super Category`, `Category`, `SKU Code / Item No`, `SKU / Item Name`, `Item Qty`, `Net Sale Value`, `Purchase Value` |
| Closing Stock Report | captured_posist_report | Current quantity, average cost, and closing valuation evidence | `Deployment`, `Date`, `Generation Date`, `Item Code`, `Item Name`, `Category Name`, `Unit Name`, `Average Price`, `Total Qty`, `Total Amt` |
| Enterprise Purchase Order Report | captured_posist_report | Ordered, processed, remaining, expected-date, status, and commitment-value evidence | `Deployment`, `Store Name`, `Vendor Name`, `PO Number`, `PO Date`, `Expected Delivery`, `PO Close Date/Partial Recieve Date`, `PO Status`, `Item Code`, `Item Name`, `Total Processed Qty`, `Remaining Balance Qty`, `Quantity`, `Unit`, `Unit Price`, `Total Item Cost` |
| Enterprise Variance Report | captured_posist_report | Opening, purchase, transfer, return, closing, and actual-consumption movement bridge | `Deployment Name`, `StoreKitchen Name`, `Item Code`, `Item Name`, `Average Price`, `Opening Qty`, `Purchase Qty`, `Stock In Qty`, `Stock Out Qty`, `Return Qty`, `Closing Qty`, `Actual Consumption`, `Unit` |

### Model Route And Relationship

`18_fact_ct_sales.sql -> 05_std_ct_inventory_snapshot.sql -> 22_fact_ct_purchase_order.sql -> 20_fact_ct_actual_consumption.sql -> 33_sum_ct_scm_monthly.sql`

**Join/relationship logic:** Aggregate each fact to source period + outlet before joining sales, stock value, open PO value, and actual consumption value.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`

### Calculation

**Final fields:** `source_period_code`, `outlet_code`, `closing_stock_value`, `open_po_value`, `net_sales`, `actual_consumption_value`

**Formula:** `Direct monthly summary values with drill reports for lower grain.`

**Aggregation:** Sum at selected period/outlet scope

### Exact Zoho Configuration

**Visual:** Pivot or tabular

**Shelves/columns:**

- Rows: period and outlet
- Measures: stock, open PO, sales, actual consumption

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Item
- Vendor
- Exception type

**Sort:** Business-relevant default order

**Tooltips:**

- None

**Formatting:**

- Enable export and underlying data

### Guardrails

- Current-state stock and working-capital widgets require one source period.
- This is a descriptive monthly summary, not a transaction table.

### How To Explain It

SCM Descriptive Explorer starts from Gross/Net Margin Report, Closing Stock Report, Enterprise Purchase Order Report, Enterprise Variance Report. The model follows 18_fact_ct_sales.sql -> 05_std_ct_inventory_snapshot.sql -> 22_fact_ct_purchase_order.sql -> 20_fact_ct_actual_consumption.sql -> 33_sum_ct_scm_monthly.sql at source period and outlet. The relationship rule is: Aggregate each fact to source period + outlet before joining sales, stock value, open PO value, and actual consumption value. In Zoho, use sum at selected period/outlet scope and render it as pivot or tabular to answer: What governed SCM values can be drilled and exported by period and outlet?

<a id="ct-p4-expiry-explorer-demo"></a>
## CT_P4_Expiry_Explorer_Demo - Expiry Explorer - Demo

**Business question:** Which scenario inputs and outputs explain the synthetic expiry exposure?

**Final object:** table / Tabular from `38_fact_ct_expiry_risk.sql`

**Final grain:** Source period, outlet, synthetic batch allocation, and item

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Enterprise Entry Report - Stock Entry | captured_posist_report | Receipt date, GRN, PO, vendor, quantity, and cost pattern used for traceable demo tranches | `Date`, `Transaction Number`, `PO Number`, `Vendor Name`, `Item Code`, `Item Name`, `Quantity`, `Unit`, `Unit Price` |
| Closing Stock Report | captured_posist_report | Current item quantity and average-cost boundary | `Date`, `Item Code`, `Item Name`, `Unit Name`, `Average Price`, `Total Qty` |
| AUX Expiry Estimate | synthetic_model_input | Synthetic FIFO tranche and shelf-life scenario; not a POSIST batch or expiry source | `batch_allocation_id`, `receipt_date`, `estimated_expiry_date`, `expiry_qty_at_risk`, `expiry_risk_value`, `production_use_status` |

### Model Route And Relationship

`AUX_Expiry_Estimate-Copy -> 38_fact_ct_expiry_risk.sql`

**Join/relationship logic:** Expose the prebuilt synthetic FIFO/shelf-life scenario with permanent evidence and production-use labels.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `item_code -> 14_dim_ct_item.sql.item_code`

### Calculation

**Final fields:** `outlet_code`, `item_code`, `shelf_life_days_assumption`, `estimated_fifo_tranche_qty`, `estimated_expiry_date`, `expiry_qty_at_risk`, `expiry_risk_value`, `production_use_status`

**Formula:** `Direct synthetic scenario rows.`

**Aggregation:** One row per synthetic batch allocation

### Exact Zoho Configuration

**Visual:** Tabular

**Shelves/columns:**

- Columns: outlet, item, scenario inputs, estimated date, quantity/value, production-use label

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Item
- Vendor
- Exception type

**Sort:** Business-relevant default order

**Tooltips:**

- None

**Formatting:**

- Permanent synthetic-source qualifier

### Guardrails

- Every title or subtitle must say Synthetic demo estimate - no POSIST batch/expiry source.
- Do not present the scenario as actual batch ageing or expiry truth.

### How To Explain It

Expiry Explorer - Demo starts from Enterprise Entry Report - Stock Entry, Closing Stock Report, AUX Expiry Estimate. The model follows AUX_Expiry_Estimate-Copy -> 38_fact_ct_expiry_risk.sql at source period, outlet, synthetic batch allocation, and item. The relationship rule is: Expose the prebuilt synthetic FIFO/shelf-life scenario with permanent evidence and production-use labels. In Zoho, use one row per synthetic batch allocation and render it as tabular to answer: Which scenario inputs and outputs explain the synthetic expiry exposure?

<a id="ct-p4-grn-explorer"></a>
## CT_P4_GRN_Explorer - GRN Explorer

**Business question:** Which receipt lines explain GRN quantity and value?

**Final object:** table / Tabular from `23_fact_ct_purchase_receipt.sql`

**Final grain:** Source period, outlet, stock-entry transaction, and item line

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Enterprise Entry Report - Stock Entry | captured_posist_report | GRN/stock-entry receipt quantity, price, tax, total, vendor, and PO reference | `Deployment Name`, `Store/Kitchen Name`, `Vendor Name`, `Date`, `Transaction Number`, `Invoice Number`, `PO Number`, `Item Code`, `Item Name`, `Quantity`, `Unit`, `Unit Price`, `Amount`, `Total Tax`, `Total` |

### Model Route And Relationship

`RAWN_CT_enterprise_entry-Copy -> 08_std_ct_purchase_receipt.sql -> 23_fact_ct_purchase_receipt.sql`

**Join/relationship logic:** Normalize receipt identity, PO reference, quantity, subtotal, tax, and total without dropping the raw identifier.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `item_code -> 14_dim_ct_item.sql.item_code`
- `vendor_name -> 16_dim_ct_vendor.sql.vendor_name`

### Calculation

**Final fields:** `receipt_date`, `grn_number`, `po_number`, `vendor_name`, `item_code`, `received_qty`, `receipt_subtotal`, `receipt_tax`, `receipt_total`, `return_source_status`

**Formula:** `Direct normalized stock-entry receipt rows.`

**Aggregation:** One row per receipt item line

### Exact Zoho Configuration

**Visual:** Tabular

**Shelves/columns:**

- Columns: receipt date, GRN, PO, vendor, item, quantity, subtotal, tax, total, return-source status

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Item
- Vendor
- Exception type

**Sort:** Receipt date descending

**Tooltips:**

- None

**Formatting:**

- None

### Guardrails

- Weighted price is receipt subtotal divided by received quantity.
- PO linkage remains sparse in the audited actual extract.

### How To Explain It

GRN Explorer starts from Enterprise Entry Report - Stock Entry. The model follows RAWN_CT_enterprise_entry-Copy -> 08_std_ct_purchase_receipt.sql -> 23_fact_ct_purchase_receipt.sql at source period, outlet, stock-entry transaction, and item line. The relationship rule is: Normalize receipt identity, PO reference, quantity, subtotal, tax, and total without dropping the raw identifier. In Zoho, use one row per receipt item line and render it as tabular to answer: Which receipt lines explain GRN quantity and value?

<a id="ct-p4-item-explorer"></a>
## CT_P4_Item_Explorer - Item Explorer

**Business question:** Which item checkpoints explain stock, cost, forecast, PO, and risk totals?

**Final object:** table / Tabular from `27_fact_ct_inventory_risk.sql`

**Final grain:** Source period, outlet, and inventory ingredient checkpoint

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Closing Stock Report | captured_posist_report | Current quantity, average cost, and closing valuation evidence | `Deployment`, `Date`, `Generation Date`, `Item Code`, `Item Name`, `Category Name`, `Unit Name`, `Average Price`, `Total Qty`, `Total Amt` |
| Item Recipe Report | captured_posist_report | Menu-to-ingredient conversion | `Item Number`, `Qty`, `Recipe Unit`, `Ingredient Code`, `Ingredient Name` |
| AUX Menu Demand Forecast | synthetic_model_input | Synthetic seven-day menu demand and net-sales forecast | `source_period_code`, `outlet_code`, `menu_item_code`, `forecast_menu_qty`, `forecast_net_sales` |
| Enterprise Purchase Order Report | captured_posist_report | Ordered, processed, remaining, expected-date, status, and commitment-value evidence | `Deployment`, `Store Name`, `Vendor Name`, `PO Number`, `PO Date`, `Expected Delivery`, `PO Close Date/Partial Recieve Date`, `PO Status`, `Item Code`, `Item Name`, `Total Processed Qty`, `Remaining Balance Qty`, `Quantity`, `Unit`, `Unit Price`, `Total Item Cost` |

### Model Route And Relationship

`05_std_ct_inventory_snapshot.sql -> 26_fact_ct_forecast_ingredient_demand.sql -> 22_fact_ct_purchase_order.sql -> 27_fact_ct_inventory_risk.sql`

**Join/relationship logic:** Join stock, seven-day forecast ingredient demand, and valid open PO quantity on source period + outlet + item.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `item_code -> 14_dim_ct_item.sql.item_code`

### Calculation

**Final fields:** `outlet_code`, `item_code`, `category_name`, `current_stock_qty`, `average_unit_cost`, `forecast_required_qty`, `valid_open_po_qty`, `risk_severity`

**Formula:** `Direct inventory-risk detail.`

**Aggregation:** One row per item checkpoint

### Exact Zoho Configuration

**Visual:** Tabular

**Shelves/columns:**

- Columns: outlet, item, category, stock, cost, forecast, PO, severity

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Item
- Vendor
- Exception type

**Sort:** Outlet, risk rank descending, item

**Tooltips:**

- None

**Formatting:**

- None

### Guardrails

- The 15% safety factor is a demo rule pending ABNAH approval.
- Query 27 covers stockout exposure only; expiry is separate.

### How To Explain It

Item Explorer starts from Closing Stock Report, Item Recipe Report, AUX Menu Demand Forecast, Enterprise Purchase Order Report. The model follows 05_std_ct_inventory_snapshot.sql -> 26_fact_ct_forecast_ingredient_demand.sql -> 22_fact_ct_purchase_order.sql -> 27_fact_ct_inventory_risk.sql at source period, outlet, and inventory ingredient checkpoint. The relationship rule is: Join stock, seven-day forecast ingredient demand, and valid open PO quantity on source period + outlet + item. In Zoho, use one row per item checkpoint and render it as tabular to answer: Which item checkpoints explain stock, cost, forecast, PO, and risk totals?

<a id="ct-p4-kpi-active-menu-items"></a>
## CT_P4_KPI_Active_Menu_Items - Active Menu Items

**Business question:** How many distinct menu items had sales in the selected scope?

**Final object:** kpi / KPI widget from `18_fact_ct_sales.sql`

**Final grain:** Sales date, outlet, bill, and menu item

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Gross/Net Margin Report | captured_posist_report | Bill-item sales, quantity, realized revenue, and source cost evidence | `Store Name`, `Date`, `Bill No.`, `Super Category`, `Category`, `SKU Code / Item No`, `SKU / Item Name`, `Item Qty`, `Net Sale Value`, `Purchase Value` |

### Model Route And Relationship

`RAWN_CT_gross_net_margin-Copy -> 01_std_ct_sales_item.sql -> 18_fact_ct_sales.sql`

**Join/relationship logic:** No cross-report join in the fact; preserve the validated bill-item grain.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `sales_date -> 12_dim_ct_date.sql.calendar_date`
- `item_code -> 15_dim_ct_menu_item.sql.menu_item_code`

### Calculation

**Final fields:** `item_code`

**Formula:** `distinctcount("item_code")`

**Aggregation:** Distinct menu-item count

### Exact Zoho Configuration

**Visual:** KPI widget

**Shelves/columns:**

- Data Column: item_code
- Show Value As: Count Distinct
- Group By: blank

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Item
- Vendor
- Exception type

**Sort:** Business-relevant default order

**Tooltips:**

- None

**Formatting:**

- Whole number

### Guardrails

- The sales item key is a menu item, not an inventory ingredient.
- Use source purchase value only where cost coverage is approved.

### How To Explain It

Active Menu Items starts from Gross/Net Margin Report. The model follows RAWN_CT_gross_net_margin-Copy -> 01_std_ct_sales_item.sql -> 18_fact_ct_sales.sql at sales date, outlet, bill, and menu item. The relationship rule is: No cross-report join in the fact; preserve the validated bill-item grain. In Zoho, use distinct menu-item count and render it as kpi widget to answer: How many distinct menu items had sales in the selected scope?

<a id="ct-p4-kpi-active-vendors"></a>
## CT_P4_KPI_Active_Vendors - Active Vendors

**Business question:** How many distinct vendors appear on purchase orders in the selected scope?

**Final object:** kpi / KPI widget from `22_fact_ct_purchase_order.sql`

**Final grain:** Source period, outlet, purchase order, and item line

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Enterprise Purchase Order Report | captured_posist_report | Ordered, processed, remaining, expected-date, status, and commitment-value evidence | `Deployment`, `Store Name`, `Vendor Name`, `PO Number`, `PO Date`, `Expected Delivery`, `PO Close Date/Partial Recieve Date`, `PO Status`, `Item Code`, `Item Name`, `Total Processed Qty`, `Remaining Balance Qty`, `Quantity`, `Unit`, `Unit Price`, `Total Item Cost` |

### Model Route And Relationship

`RAWN_CT_enterprise_purchase_order-Copy -> 07_std_ct_purchase_order.sql -> 22_fact_ct_purchase_order.sql`

**Join/relationship logic:** Normalize line status and derive ordered value, open quantity/value, open flag, and delayed flag at PO-line grain.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `item_code -> 14_dim_ct_item.sql.item_code`
- `vendor_name -> 16_dim_ct_vendor.sql.vendor_name`

### Calculation

**Final fields:** `vendor_name`

**Formula:** `distinctcount("vendor_name")`

**Aggregation:** Distinct vendor count

### Exact Zoho Configuration

**Visual:** KPI widget

**Shelves/columns:**

- Data Column: vendor_name
- Show Value As: Count Distinct
- Group By: blank

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Item
- Vendor
- Exception type

**Sort:** Business-relevant default order

**Tooltips:**

- None

**Formatting:**

- Whole number

### Guardrails

- Use distinct PO number for PO counts; row count is a PO-line count.
- Expected-date exceptions are operational states, not automatically source defects.

### How To Explain It

Active Vendors starts from Enterprise Purchase Order Report. The model follows RAWN_CT_enterprise_purchase_order-Copy -> 07_std_ct_purchase_order.sql -> 22_fact_ct_purchase_order.sql at source period, outlet, purchase order, and item line. The relationship rule is: Normalize line status and derive ordered value, open quantity/value, open flag, and delayed flag at PO-line grain. In Zoho, use distinct vendor count and render it as kpi widget to answer: How many distinct vendors appear on purchase orders in the selected scope?

<a id="ct-p4-kpi-actual-consumption"></a>
## CT_P4_KPI_Actual_Consumption - Actual Consumption Value

**Business question:** What calculated actual-consumption value is summarized for the selected scope?

**Final object:** kpi / KPI widget from `33_sum_ct_scm_monthly.sql`

**Final grain:** Source period and outlet

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Gross/Net Margin Report | captured_posist_report | Bill-item sales, quantity, realized revenue, and source cost evidence | `Store Name`, `Date`, `Bill No.`, `Super Category`, `Category`, `SKU Code / Item No`, `SKU / Item Name`, `Item Qty`, `Net Sale Value`, `Purchase Value` |
| Closing Stock Report | captured_posist_report | Current quantity, average cost, and closing valuation evidence | `Deployment`, `Date`, `Generation Date`, `Item Code`, `Item Name`, `Category Name`, `Unit Name`, `Average Price`, `Total Qty`, `Total Amt` |
| Enterprise Purchase Order Report | captured_posist_report | Ordered, processed, remaining, expected-date, status, and commitment-value evidence | `Deployment`, `Store Name`, `Vendor Name`, `PO Number`, `PO Date`, `Expected Delivery`, `PO Close Date/Partial Recieve Date`, `PO Status`, `Item Code`, `Item Name`, `Total Processed Qty`, `Remaining Balance Qty`, `Quantity`, `Unit`, `Unit Price`, `Total Item Cost` |
| Enterprise Variance Report | captured_posist_report | Opening, purchase, transfer, return, closing, and actual-consumption movement bridge | `Deployment Name`, `StoreKitchen Name`, `Item Code`, `Item Name`, `Average Price`, `Opening Qty`, `Purchase Qty`, `Stock In Qty`, `Stock Out Qty`, `Return Qty`, `Closing Qty`, `Actual Consumption`, `Unit` |

### Model Route And Relationship

`18_fact_ct_sales.sql -> 05_std_ct_inventory_snapshot.sql -> 22_fact_ct_purchase_order.sql -> 20_fact_ct_actual_consumption.sql -> 33_sum_ct_scm_monthly.sql`

**Join/relationship logic:** Aggregate each fact to source period + outlet before joining sales, stock value, open PO value, and actual consumption value.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`

### Calculation

**Final fields:** `actual_consumption_value`

**Formula:** `sum("actual_consumption_value")`

**Aggregation:** Sum actual consumption value

### Exact Zoho Configuration

**Visual:** KPI widget

**Shelves/columns:**

- Data Column: actual_consumption_value
- Show Value As: Sum
- Group By: blank

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Item
- Vendor
- Exception type

**Sort:** Business-relevant default order

**Tooltips:**

- None

**Formatting:**

- INR currency

### Guardrails

- Current-state stock and working-capital widgets require one source period.
- This is a descriptive monthly summary, not a transaction table.

### How To Explain It

Actual Consumption Value starts from Gross/Net Margin Report, Closing Stock Report, Enterprise Purchase Order Report, Enterprise Variance Report. The model follows 18_fact_ct_sales.sql -> 05_std_ct_inventory_snapshot.sql -> 22_fact_ct_purchase_order.sql -> 20_fact_ct_actual_consumption.sql -> 33_sum_ct_scm_monthly.sql at source period and outlet. The relationship rule is: Aggregate each fact to source period + outlet before joining sales, stock value, open PO value, and actual consumption value. In Zoho, use sum actual consumption value and render it as kpi widget to answer: What calculated actual-consumption value is summarized for the selected scope?

<a id="ct-p4-kpi-closing-stock"></a>
## CT_P4_KPI_Closing_Stock - Closing Stock Value

**Business question:** What is the selected checkpoint's closing stock value?

**Final object:** kpi / KPI widget from `33_sum_ct_scm_monthly.sql`

**Final grain:** Source period and outlet

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Gross/Net Margin Report | captured_posist_report | Bill-item sales, quantity, realized revenue, and source cost evidence | `Store Name`, `Date`, `Bill No.`, `Super Category`, `Category`, `SKU Code / Item No`, `SKU / Item Name`, `Item Qty`, `Net Sale Value`, `Purchase Value` |
| Closing Stock Report | captured_posist_report | Current quantity, average cost, and closing valuation evidence | `Deployment`, `Date`, `Generation Date`, `Item Code`, `Item Name`, `Category Name`, `Unit Name`, `Average Price`, `Total Qty`, `Total Amt` |
| Enterprise Purchase Order Report | captured_posist_report | Ordered, processed, remaining, expected-date, status, and commitment-value evidence | `Deployment`, `Store Name`, `Vendor Name`, `PO Number`, `PO Date`, `Expected Delivery`, `PO Close Date/Partial Recieve Date`, `PO Status`, `Item Code`, `Item Name`, `Total Processed Qty`, `Remaining Balance Qty`, `Quantity`, `Unit`, `Unit Price`, `Total Item Cost` |
| Enterprise Variance Report | captured_posist_report | Opening, purchase, transfer, return, closing, and actual-consumption movement bridge | `Deployment Name`, `StoreKitchen Name`, `Item Code`, `Item Name`, `Average Price`, `Opening Qty`, `Purchase Qty`, `Stock In Qty`, `Stock Out Qty`, `Return Qty`, `Closing Qty`, `Actual Consumption`, `Unit` |

### Model Route And Relationship

`18_fact_ct_sales.sql -> 05_std_ct_inventory_snapshot.sql -> 22_fact_ct_purchase_order.sql -> 20_fact_ct_actual_consumption.sql -> 33_sum_ct_scm_monthly.sql`

**Join/relationship logic:** Aggregate each fact to source period + outlet before joining sales, stock value, open PO value, and actual consumption value.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`

### Calculation

**Final fields:** `closing_stock_value`

**Formula:** `sum("closing_stock_value")`

**Aggregation:** Sum closing stock value

### Exact Zoho Configuration

**Visual:** KPI widget

**Shelves/columns:**

- Data Column: closing_stock_value
- Show Value As: Sum
- Group By: blank

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Item
- Vendor
- Exception type

**Sort:** Business-relevant default order

**Tooltips:**

- None

**Formatting:**

- INR currency

### Guardrails

- Current-state stock and working-capital widgets require one source period.
- This is a descriptive monthly summary, not a transaction table.
- Require one source period.

### How To Explain It

Closing Stock Value starts from Gross/Net Margin Report, Closing Stock Report, Enterprise Purchase Order Report, Enterprise Variance Report. The model follows 18_fact_ct_sales.sql -> 05_std_ct_inventory_snapshot.sql -> 22_fact_ct_purchase_order.sql -> 20_fact_ct_actual_consumption.sql -> 33_sum_ct_scm_monthly.sql at source period and outlet. The relationship rule is: Aggregate each fact to source period + outlet before joining sales, stock value, open PO value, and actual consumption value. In Zoho, use sum closing stock value and render it as kpi widget to answer: What is the selected checkpoint's closing stock value?

<a id="ct-p4-kpi-consumption-variance"></a>
## CT_P4_KPI_Consumption_Variance - Signed Consumption Variance Value

**Business question:** What is the signed actual-versus-theoretical consumption variance value for the checkpoint?

**Final object:** kpi / KPI widget from `21_fact_ct_consumption_variance.sql`

**Final grain:** Source period, outlet, inventory item, and canonical UOM

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Enterprise Variance Report | captured_posist_report | Opening, purchase, transfer, return, closing, and actual-consumption movement bridge | `Deployment Name`, `StoreKitchen Name`, `Item Code`, `Item Name`, `Average Price`, `Opening Qty`, `Purchase Qty`, `Stock In Qty`, `Stock Out Qty`, `Return Qty`, `Closing Qty`, `Actual Consumption`, `Unit` |
| Gross/Net Margin Report | captured_posist_report | Sold menu-item quantities used by the theoretical model | `Store Name`, `Date`, `SKU Code / Item No`, `SKU / Item Name`, `Item Qty` |
| Item Recipe Report | captured_posist_report | Menu-item to ingredient quantity and UOM bridge | `Item Number`, `Item Name`, `Qty`, `Recipe Unit`, `Ingredient Code`, `Ingredient Name` |
| Closing Stock Report | captured_posist_report | Ingredient UOM and average-cost reference | `Item Code`, `Item Name`, `Unit Name`, `Average Price` |
| AUX Theoretical Consumption | synthetic_model_input | Synthetic three-month baseline derived from sales, recipe, UOM, and cost inputs | `source_period_code`, `outlet_code`, `item_code`, `canonical_uom`, `theoretical_consumption_qty`, `theoretical_consumption_value` |

### Model Route And Relationship

`20_fact_ct_actual_consumption.sql -> 19_fact_ct_theoretical_consumption.sql -> 21_fact_ct_consumption_variance.sql`

**Join/relationship logic:** Join actual and theoretical consumption on source period + outlet + item; calculate signed variance, positive leakage, and low-consumption check.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `item_code -> 14_dim_ct_item.sql.item_code`

### Calculation

**Final fields:** `signed_consumption_variance_value`

**Formula:** `sum("signed_consumption_variance_value")`

**Aggregation:** Sum the physical signed variance value

### Exact Zoho Configuration

**Visual:** KPI widget

**Shelves/columns:**

- Data Column: signed_consumption_variance_value
- Show Value As: Sum
- Group By: blank

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Item
- Vendor
- Exception type

**Sort:** Business-relevant default order

**Tooltips:**

- None

**Formatting:**

- INR currency; allow negative values

### Guardrails

- Positive leakage is not the same as signed variance.
- Low consumption is a data/process check, not a favorable saving.
- Keep positive leakage as a separate control.

### How To Explain It

Signed Consumption Variance Value starts from Enterprise Variance Report, Gross/Net Margin Report, Item Recipe Report, Closing Stock Report, AUX Theoretical Consumption. The model follows 20_fact_ct_actual_consumption.sql -> 19_fact_ct_theoretical_consumption.sql -> 21_fact_ct_consumption_variance.sql at source period, outlet, inventory item, and canonical uom. The relationship rule is: Join actual and theoretical consumption on source period + outlet + item; calculate signed variance, positive leakage, and low-consumption check. In Zoho, use sum the physical signed variance value and render it as kpi widget to answer: What is the signed actual-versus-theoretical consumption variance value for the checkpoint?

<a id="ct-p4-kpi-grn-value"></a>
## CT_P4_KPI_GRN_Value - GRN Value

**Business question:** What accepted receipt total was recorded in the selected scope?

**Final object:** kpi / KPI widget from `23_fact_ct_purchase_receipt.sql`

**Final grain:** Source period, outlet, stock-entry transaction, and item line

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Enterprise Entry Report - Stock Entry | captured_posist_report | GRN/stock-entry receipt quantity, price, tax, total, vendor, and PO reference | `Deployment Name`, `Store/Kitchen Name`, `Vendor Name`, `Date`, `Transaction Number`, `Invoice Number`, `PO Number`, `Item Code`, `Item Name`, `Quantity`, `Unit`, `Unit Price`, `Amount`, `Total Tax`, `Total` |

### Model Route And Relationship

`RAWN_CT_enterprise_entry-Copy -> 08_std_ct_purchase_receipt.sql -> 23_fact_ct_purchase_receipt.sql`

**Join/relationship logic:** Normalize receipt identity, PO reference, quantity, subtotal, tax, and total without dropping the raw identifier.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `item_code -> 14_dim_ct_item.sql.item_code`
- `vendor_name -> 16_dim_ct_vendor.sql.vendor_name`

### Calculation

**Final fields:** `receipt_total`

**Formula:** `sum("receipt_total")`

**Aggregation:** Sum receipt total

### Exact Zoho Configuration

**Visual:** KPI widget

**Shelves/columns:**

- Data Column: receipt_total
- Show Value As: Sum
- Group By: blank

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Item
- Vendor
- Exception type

**Sort:** Business-relevant default order

**Tooltips:**

- None

**Formatting:**

- INR currency

### Guardrails

- Weighted price is receipt subtotal divided by received quantity.
- PO linkage remains sparse in the audited actual extract.

### How To Explain It

GRN Value starts from Enterprise Entry Report - Stock Entry. The model follows RAWN_CT_enterprise_entry-Copy -> 08_std_ct_purchase_receipt.sql -> 23_fact_ct_purchase_receipt.sql at source period, outlet, stock-entry transaction, and item line. The relationship rule is: Normalize receipt identity, PO reference, quantity, subtotal, tax, and total without dropping the raw identifier. In Zoho, use sum receipt total and render it as kpi widget to answer: What accepted receipt total was recorded in the selected scope?

<a id="ct-p4-kpi-net-sales"></a>
## CT_P4_KPI_Net_Sales - Net Sales

**Business question:** What net sales are summarized for the selected period and outlet?

**Final object:** kpi / KPI widget from `33_sum_ct_scm_monthly.sql`

**Final grain:** Source period and outlet

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Gross/Net Margin Report | captured_posist_report | Bill-item sales, quantity, realized revenue, and source cost evidence | `Store Name`, `Date`, `Bill No.`, `Super Category`, `Category`, `SKU Code / Item No`, `SKU / Item Name`, `Item Qty`, `Net Sale Value`, `Purchase Value` |
| Closing Stock Report | captured_posist_report | Current quantity, average cost, and closing valuation evidence | `Deployment`, `Date`, `Generation Date`, `Item Code`, `Item Name`, `Category Name`, `Unit Name`, `Average Price`, `Total Qty`, `Total Amt` |
| Enterprise Purchase Order Report | captured_posist_report | Ordered, processed, remaining, expected-date, status, and commitment-value evidence | `Deployment`, `Store Name`, `Vendor Name`, `PO Number`, `PO Date`, `Expected Delivery`, `PO Close Date/Partial Recieve Date`, `PO Status`, `Item Code`, `Item Name`, `Total Processed Qty`, `Remaining Balance Qty`, `Quantity`, `Unit`, `Unit Price`, `Total Item Cost` |
| Enterprise Variance Report | captured_posist_report | Opening, purchase, transfer, return, closing, and actual-consumption movement bridge | `Deployment Name`, `StoreKitchen Name`, `Item Code`, `Item Name`, `Average Price`, `Opening Qty`, `Purchase Qty`, `Stock In Qty`, `Stock Out Qty`, `Return Qty`, `Closing Qty`, `Actual Consumption`, `Unit` |

### Model Route And Relationship

`18_fact_ct_sales.sql -> 05_std_ct_inventory_snapshot.sql -> 22_fact_ct_purchase_order.sql -> 20_fact_ct_actual_consumption.sql -> 33_sum_ct_scm_monthly.sql`

**Join/relationship logic:** Aggregate each fact to source period + outlet before joining sales, stock value, open PO value, and actual consumption value.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`

### Calculation

**Final fields:** `net_sales`

**Formula:** `sum("net_sales")`

**Aggregation:** Sum net sales

### Exact Zoho Configuration

**Visual:** KPI widget

**Shelves/columns:**

- Data Column: net_sales
- Show Value As: Sum
- Group By: blank

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Item
- Vendor
- Exception type

**Sort:** Business-relevant default order

**Tooltips:**

- None

**Formatting:**

- INR currency

### Guardrails

- Current-state stock and working-capital widgets require one source period.
- This is a descriptive monthly summary, not a transaction table.

### How To Explain It

Net Sales starts from Gross/Net Margin Report, Closing Stock Report, Enterprise Purchase Order Report, Enterprise Variance Report. The model follows 18_fact_ct_sales.sql -> 05_std_ct_inventory_snapshot.sql -> 22_fact_ct_purchase_order.sql -> 20_fact_ct_actual_consumption.sql -> 33_sum_ct_scm_monthly.sql at source period and outlet. The relationship rule is: Aggregate each fact to source period + outlet before joining sales, stock value, open PO value, and actual consumption value. In Zoho, use sum net sales and render it as kpi widget to answer: What net sales are summarized for the selected period and outlet?

<a id="ct-p4-kpi-open-po"></a>
## CT_P4_KPI_Open_PO - Open PO Value

**Business question:** What open PO value exists in the selected checkpoint?

**Final object:** kpi / KPI widget from `33_sum_ct_scm_monthly.sql`

**Final grain:** Source period and outlet

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Gross/Net Margin Report | captured_posist_report | Bill-item sales, quantity, realized revenue, and source cost evidence | `Store Name`, `Date`, `Bill No.`, `Super Category`, `Category`, `SKU Code / Item No`, `SKU / Item Name`, `Item Qty`, `Net Sale Value`, `Purchase Value` |
| Closing Stock Report | captured_posist_report | Current quantity, average cost, and closing valuation evidence | `Deployment`, `Date`, `Generation Date`, `Item Code`, `Item Name`, `Category Name`, `Unit Name`, `Average Price`, `Total Qty`, `Total Amt` |
| Enterprise Purchase Order Report | captured_posist_report | Ordered, processed, remaining, expected-date, status, and commitment-value evidence | `Deployment`, `Store Name`, `Vendor Name`, `PO Number`, `PO Date`, `Expected Delivery`, `PO Close Date/Partial Recieve Date`, `PO Status`, `Item Code`, `Item Name`, `Total Processed Qty`, `Remaining Balance Qty`, `Quantity`, `Unit`, `Unit Price`, `Total Item Cost` |
| Enterprise Variance Report | captured_posist_report | Opening, purchase, transfer, return, closing, and actual-consumption movement bridge | `Deployment Name`, `StoreKitchen Name`, `Item Code`, `Item Name`, `Average Price`, `Opening Qty`, `Purchase Qty`, `Stock In Qty`, `Stock Out Qty`, `Return Qty`, `Closing Qty`, `Actual Consumption`, `Unit` |

### Model Route And Relationship

`18_fact_ct_sales.sql -> 05_std_ct_inventory_snapshot.sql -> 22_fact_ct_purchase_order.sql -> 20_fact_ct_actual_consumption.sql -> 33_sum_ct_scm_monthly.sql`

**Join/relationship logic:** Aggregate each fact to source period + outlet before joining sales, stock value, open PO value, and actual consumption value.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`

### Calculation

**Final fields:** `open_po_value`

**Formula:** `sum("open_po_value")`

**Aggregation:** Sum open PO value

### Exact Zoho Configuration

**Visual:** KPI widget

**Shelves/columns:**

- Data Column: open_po_value
- Show Value As: Sum
- Group By: blank

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Item
- Vendor
- Exception type

**Sort:** Business-relevant default order

**Tooltips:**

- None

**Formatting:**

- INR currency

### Guardrails

- Current-state stock and working-capital widgets require one source period.
- This is a descriptive monthly summary, not a transaction table.
- Require one source period for current-state display.

### How To Explain It

Open PO Value starts from Gross/Net Margin Report, Closing Stock Report, Enterprise Purchase Order Report, Enterprise Variance Report. The model follows 18_fact_ct_sales.sql -> 05_std_ct_inventory_snapshot.sql -> 22_fact_ct_purchase_order.sql -> 20_fact_ct_actual_consumption.sql -> 33_sum_ct_scm_monthly.sql at source period and outlet. The relationship rule is: Aggregate each fact to source period + outlet before joining sales, stock value, open PO value, and actual consumption value. In Zoho, use sum open po value and render it as kpi widget to answer: What open PO value exists in the selected checkpoint?

<a id="ct-p4-kpi-open-po-lines"></a>
## CT_P4_KPI_Open_PO_Lines - Open PO Line Count

**Business question:** How many PO item lines remain open?

**Final object:** kpi / KPI widget from `22_fact_ct_purchase_order.sql`

**Final grain:** Source period, outlet, purchase order, and item line

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Enterprise Purchase Order Report | captured_posist_report | Ordered, processed, remaining, expected-date, status, and commitment-value evidence | `Deployment`, `Store Name`, `Vendor Name`, `PO Number`, `PO Date`, `Expected Delivery`, `PO Close Date/Partial Recieve Date`, `PO Status`, `Item Code`, `Item Name`, `Total Processed Qty`, `Remaining Balance Qty`, `Quantity`, `Unit`, `Unit Price`, `Total Item Cost` |

### Model Route And Relationship

`RAWN_CT_enterprise_purchase_order-Copy -> 07_std_ct_purchase_order.sql -> 22_fact_ct_purchase_order.sql`

**Join/relationship logic:** Normalize line status and derive ordered value, open quantity/value, open flag, and delayed flag at PO-line grain.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `item_code -> 14_dim_ct_item.sql.item_code`
- `vendor_name -> 16_dim_ct_vendor.sql.vendor_name`

### Calculation

**Final fields:** `is_open_po`

**Formula:** `sum("is_open_po")`

**Aggregation:** Sum the physical open-line flag

### Exact Zoho Configuration

**Visual:** KPI widget

**Shelves/columns:**

- Data Column: is_open_po
- Show Value As: Sum
- Group By: blank

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Item
- Vendor
- Exception type

**Sort:** Business-relevant default order

**Tooltips:**

- None

**Formatting:**

- Whole number

### Guardrails

- Use distinct PO number for PO counts; row count is a PO-line count.
- Expected-date exceptions are operational states, not automatically source defects.
- This is not a distinct PO count. No fixed filter is required because closed lines contribute zero.

### How To Explain It

Open PO Line Count starts from Enterprise Purchase Order Report. The model follows RAWN_CT_enterprise_purchase_order-Copy -> 07_std_ct_purchase_order.sql -> 22_fact_ct_purchase_order.sql at source period, outlet, purchase order, and item line. The relationship rule is: Normalize line status and derive ordered value, open quantity/value, open flag, and delayed flag at PO-line grain. In Zoho, use sum the physical open-line flag and render it as kpi widget to answer: How many PO item lines remain open?

<a id="ct-p4-kpi-quantity-sold"></a>
## CT_P4_KPI_Quantity_Sold - Quantity Sold

**Business question:** How many menu-item units were sold?

**Final object:** kpi / KPI widget from `18_fact_ct_sales.sql`

**Final grain:** Sales date, outlet, bill, and menu item

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Gross/Net Margin Report | captured_posist_report | Bill-item sales, quantity, realized revenue, and source cost evidence | `Store Name`, `Date`, `Bill No.`, `Super Category`, `Category`, `SKU Code / Item No`, `SKU / Item Name`, `Item Qty`, `Net Sale Value`, `Purchase Value` |

### Model Route And Relationship

`RAWN_CT_gross_net_margin-Copy -> 01_std_ct_sales_item.sql -> 18_fact_ct_sales.sql`

**Join/relationship logic:** No cross-report join in the fact; preserve the validated bill-item grain.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `sales_date -> 12_dim_ct_date.sql.calendar_date`
- `item_code -> 15_dim_ct_menu_item.sql.menu_item_code`

### Calculation

**Final fields:** `sold_qty`

**Formula:** `sum("sold_qty")`

**Aggregation:** Sum sold quantity

### Exact Zoho Configuration

**Visual:** KPI widget

**Shelves/columns:**

- Data Column: sold_qty
- Show Value As: Sum
- Group By: blank

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Item
- Vendor
- Exception type

**Sort:** Business-relevant default order

**Tooltips:**

- None

**Formatting:**

- None

### Guardrails

- The sales item key is a menu item, not an inventory ingredient.
- Use source purchase value only where cost coverage is approved.

### How To Explain It

Quantity Sold starts from Gross/Net Margin Report. The model follows RAWN_CT_gross_net_margin-Copy -> 01_std_ct_sales_item.sql -> 18_fact_ct_sales.sql at sales date, outlet, bill, and menu item. The relationship rule is: No cross-report join in the fact; preserve the validated bill-item grain. In Zoho, use sum sold quantity and render it as kpi widget to answer: How many menu-item units were sold?

<a id="ct-p4-po-explorer"></a>
## CT_P4_PO_Explorer - PO Explorer

**Business question:** How do ordered, received, remaining, expected, actual, and status fields reconcile by PO line?

**Final object:** table / Tabular from `24_fact_ct_po_receipt_line.sql`

**Final grain:** Source period, outlet, purchase order, and item line

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Enterprise Purchase Order Report | captured_posist_report | Ordered, processed, remaining, expected-date, status, and commitment-value evidence | `Deployment`, `Store Name`, `Vendor Name`, `PO Number`, `PO Date`, `Expected Delivery`, `PO Close Date/Partial Recieve Date`, `PO Status`, `Item Code`, `Item Name`, `Total Processed Qty`, `Remaining Balance Qty`, `Quantity`, `Unit`, `Unit Price`, `Total Item Cost` |
| Enterprise Entry Report - Stock Entry | captured_posist_report | GRN/stock-entry receipt quantity, price, tax, total, vendor, and PO reference | `Deployment Name`, `Store/Kitchen Name`, `Vendor Name`, `Date`, `Transaction Number`, `Invoice Number`, `PO Number`, `Item Code`, `Item Name`, `Quantity`, `Unit`, `Unit Price`, `Amount`, `Total Tax`, `Total` |

### Model Route And Relationship

`07_std_ct_purchase_order.sql -> 08_std_ct_purchase_receipt.sql -> 24_fact_ct_po_receipt_line.sql`

**Join/relationship logic:** Left join PO and receipt lines on source period + outlet + canonical PO number + item code; aggregate receipts before the join.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `item_code -> 14_dim_ct_item.sql.item_code`
- `vendor_name -> 16_dim_ct_vendor.sql.vendor_name`

### Calculation

**Final fields:** `po_number`, `vendor_name`, `item_code`, `ordered_qty`, `received_qty`, `remaining_qty`, `expected_delivery_date`, `actual_receipt_date`, `po_status`

**Formula:** `PO lines left joined to aggregated receipt lines on canonical business keys.`

**Aggregation:** One row per PO item line

### Exact Zoho Configuration

**Visual:** Tabular

**Shelves/columns:**

- Columns: PO, vendor, item, ordered, received, remaining, expected, actual, status

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Item
- Vendor
- Exception type

**Sort:** PO number, item

**Tooltips:**

- None

**Formatting:**

- None

### Guardrails

- Actual PO-to-GRN linkage was sparse, so OTIF remains a formula demonstration.
- Fill rate uses sums of quantities, never an average of row percentages.

### How To Explain It

PO Explorer starts from Enterprise Purchase Order Report, Enterprise Entry Report - Stock Entry. The model follows 07_std_ct_purchase_order.sql -> 08_std_ct_purchase_receipt.sql -> 24_fact_ct_po_receipt_line.sql at source period, outlet, purchase order, and item line. The relationship rule is: Left join PO and receipt lines on source period + outlet + canonical PO number + item code; aggregate receipts before the join. In Zoho, use one row per po item line and render it as tabular to answer: How do ordered, received, remaining, expected, actual, and status fields reconcile by PO line?

<a id="ct-p4-scm-monthly-trend"></a>
## CT_P4_SCM_Monthly_Trend - SCM Monthly Trend

**Business question:** How do stock value, open PO value, net sales, and actual consumption move together?

**Final object:** chart / Combination from `33_sum_ct_scm_monthly.sql`

**Final grain:** Source period and outlet

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Gross/Net Margin Report | captured_posist_report | Bill-item sales, quantity, realized revenue, and source cost evidence | `Store Name`, `Date`, `Bill No.`, `Super Category`, `Category`, `SKU Code / Item No`, `SKU / Item Name`, `Item Qty`, `Net Sale Value`, `Purchase Value` |
| Closing Stock Report | captured_posist_report | Current quantity, average cost, and closing valuation evidence | `Deployment`, `Date`, `Generation Date`, `Item Code`, `Item Name`, `Category Name`, `Unit Name`, `Average Price`, `Total Qty`, `Total Amt` |
| Enterprise Purchase Order Report | captured_posist_report | Ordered, processed, remaining, expected-date, status, and commitment-value evidence | `Deployment`, `Store Name`, `Vendor Name`, `PO Number`, `PO Date`, `Expected Delivery`, `PO Close Date/Partial Recieve Date`, `PO Status`, `Item Code`, `Item Name`, `Total Processed Qty`, `Remaining Balance Qty`, `Quantity`, `Unit`, `Unit Price`, `Total Item Cost` |
| Enterprise Variance Report | captured_posist_report | Opening, purchase, transfer, return, closing, and actual-consumption movement bridge | `Deployment Name`, `StoreKitchen Name`, `Item Code`, `Item Name`, `Average Price`, `Opening Qty`, `Purchase Qty`, `Stock In Qty`, `Stock Out Qty`, `Return Qty`, `Closing Qty`, `Actual Consumption`, `Unit` |

### Model Route And Relationship

`18_fact_ct_sales.sql -> 05_std_ct_inventory_snapshot.sql -> 22_fact_ct_purchase_order.sql -> 20_fact_ct_actual_consumption.sql -> 33_sum_ct_scm_monthly.sql`

**Join/relationship logic:** Aggregate each fact to source period + outlet before joining sales, stock value, open PO value, and actual consumption value.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`

### Calculation

**Final fields:** `source_period_code`, `closing_stock_value`, `open_po_value`, `net_sales`, `actual_consumption_value`

**Formula:** `All four values are pre-aggregated to period + outlet before the summary join.`

**Aggregation:** Sum each additive value measure

### Exact Zoho Configuration

**Visual:** Combination

**Shelves/columns:**

- X: source period
- Bars: closing stock and open PO
- Lines: net sales and actual consumption

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Item
- Vendor
- Exception type

**Sort:** Business-relevant default order

**Tooltips:**

- Outlet

**Formatting:**

- None

### Guardrails

- Current-state stock and working-capital widgets require one source period.
- This is a descriptive monthly summary, not a transaction table.

### How To Explain It

SCM Monthly Trend starts from Gross/Net Margin Report, Closing Stock Report, Enterprise Purchase Order Report, Enterprise Variance Report. The model follows 18_fact_ct_sales.sql -> 05_std_ct_inventory_snapshot.sql -> 22_fact_ct_purchase_order.sql -> 20_fact_ct_actual_consumption.sql -> 33_sum_ct_scm_monthly.sql at source period and outlet. The relationship rule is: Aggregate each fact to source period + outlet before joining sales, stock value, open PO value, and actual consumption value. In Zoho, use sum each additive value measure and render it as combination to answer: How do stock value, open PO value, net sales, and actual consumption move together?

<a id="ct-p4-sales-explorer"></a>
## CT_P4_Sales_Explorer - Sales Explorer

**Business question:** Which date/outlet/menu rows explain the descriptive sales totals?

**Final object:** table / Tabular from `18_fact_ct_sales.sql`

**Final grain:** Sales date, outlet, bill, and menu item

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Gross/Net Margin Report | captured_posist_report | Bill-item sales, quantity, realized revenue, and source cost evidence | `Store Name`, `Date`, `Bill No.`, `Super Category`, `Category`, `SKU Code / Item No`, `SKU / Item Name`, `Item Qty`, `Net Sale Value`, `Purchase Value` |

### Model Route And Relationship

`RAWN_CT_gross_net_margin-Copy -> 01_std_ct_sales_item.sql -> 18_fact_ct_sales.sql`

**Join/relationship logic:** No cross-report join in the fact; preserve the validated bill-item grain.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `sales_date -> 12_dim_ct_date.sql.calendar_date`
- `item_code -> 15_dim_ct_menu_item.sql.menu_item_code`

### Calculation

**Final fields:** `sales_date`, `outlet_code`, `item_code`, `category_name`, `sold_qty`, `net_sales`, `realized_unit_price`

**Formula:** `Direct bill-item fact detail.`

**Aggregation:** One row per validated sales item line

### Exact Zoho Configuration

**Visual:** Tabular

**Shelves/columns:**

- Columns: date, outlet, menu item/category, sold quantity, net sales, realized unit price

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Item
- Vendor
- Exception type

**Sort:** Sales date descending

**Tooltips:**

- None

**Formatting:**

- None

### Guardrails

- The sales item key is a menu item, not an inventory ingredient.
- Use source purchase value only where cost coverage is approved.

### How To Explain It

Sales Explorer starts from Gross/Net Margin Report. The model follows RAWN_CT_gross_net_margin-Copy -> 01_std_ct_sales_item.sql -> 18_fact_ct_sales.sql at sales date, outlet, bill, and menu item. The relationship rule is: No cross-report join in the fact; preserve the validated bill-item grain. In Zoho, use one row per validated sales item line and render it as tabular to answer: Which date/outlet/menu rows explain the descriptive sales totals?

<a id="ct-p4-vendor-explorer"></a>
## CT_P4_Vendor_Explorer - Vendor Explorer

**Business question:** Which vendor-level values and formula demonstrations explain procurement performance?

**Final object:** table / Tabular from `30_sum_ct_vendor_scorecard.sql`

**Final grain:** Source period, outlet, and vendor

### Original Evidence

| Original report/input | Evidence level | Role | Exact fields used by this model profile |
| --- | --- | --- | --- |
| Enterprise Purchase Order Report | captured_posist_report | Ordered, processed, remaining, expected-date, status, and commitment-value evidence | `Deployment`, `Store Name`, `Vendor Name`, `PO Number`, `PO Date`, `Expected Delivery`, `PO Close Date/Partial Recieve Date`, `PO Status`, `Item Code`, `Item Name`, `Total Processed Qty`, `Remaining Balance Qty`, `Quantity`, `Unit`, `Unit Price`, `Total Item Cost` |
| Enterprise Entry Report - Stock Entry | captured_posist_report | GRN/stock-entry receipt quantity, price, tax, total, vendor, and PO reference | `Deployment Name`, `Store/Kitchen Name`, `Vendor Name`, `Date`, `Transaction Number`, `Invoice Number`, `PO Number`, `Item Code`, `Item Name`, `Quantity`, `Unit`, `Unit Price`, `Amount`, `Total Tax`, `Total` |

### Model Route And Relationship

`24_fact_ct_po_receipt_line.sql -> 30_sum_ct_vendor_scorecard.sql`

**Join/relationship logic:** Aggregate PO/receipt line results into vendor purchase, open exposure, fill, eligible OTIF, and lead-time deviation.

**Zoho lookups:**

- `outlet_code -> 37_dim_ct_outlet_enriched.sql.outlet_code`
- `vendor_name -> 16_dim_ct_vendor.sql.vendor_name`

### Calculation

**Final fields:** `vendor_name`, `monthly_purchase_value`, `received_value`, `open_po_value`, `fill_rate_percent`, `otif_percent`, `average_lead_time_deviation_days`, `delayed_line_count`

**Formula:** `Direct vendor scorecard summary.`

**Aggregation:** One row per period + outlet + vendor

### Exact Zoho Configuration

**Visual:** Tabular

**Shelves/columns:**

- Columns: vendor, ordered/received value, open liability, fill, eligible OTIF, lead deviation, delayed lines

**Fixed report filters:**

- None

**User filters:**

- Source period (global, single-select; default month_03)
- Outlet (global, multi-select)
- Region
- Item
- Vendor
- Exception type

**Sort:** Open PO value descending

**Tooltips:**

- None

**Formatting:**

- None

### Guardrails

- Do not average vendor percentages across outlets.
- OTIF and lead deviation remain demonstration metrics until receipt linkage improves.
- OTIF and lead deviation remain formula demonstrations.

### How To Explain It

Vendor Explorer starts from Enterprise Purchase Order Report, Enterprise Entry Report - Stock Entry. The model follows 24_fact_ct_po_receipt_line.sql -> 30_sum_ct_vendor_scorecard.sql at source period, outlet, and vendor. The relationship rule is: Aggregate PO/receipt line results into vendor purchase, open exposure, fill, eligible OTIF, and lead-time deviation. In Zoho, use one row per period + outlet + vendor and render it as tabular to answer: Which vendor-level values and formula demonstrations explain procurement performance?
