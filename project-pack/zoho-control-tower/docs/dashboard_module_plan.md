# Dashboard Module Plan

The dashboards should use `FACT_*` and `SUM_*` query tables wherever possible. Use RAW tables only for audit/demo drill-through.

For exact Zoho build instructions, lookup relationships, chart types, x-axis/y-axis fields, and dashboard validation steps, use `docs/zoho_actual_data_model_build_readme.md`. This file explains the dashboard design; the build README is the end-to-end implementation checklist.

The model is outlet-aware. RAW imports stay as shared report tables, but every operational standardized table, fact table, and non-executive summary must preserve outlet grain through:

- `outlet_code`
- `outlet_name`
- `market_area`

The three synthetic outlets are:

| Outlet code | Outlet name | Market area |
|---|---|---|
| `OUT001` | `ABNAH Cafe Connaught Place` | `Connaught Place` |
| `OUT002` | `ABNAH Cafe Hauz Khas` | `Hauz Khas` |
| `OUT003` | `ABNAH Cafe Saket Premium` | `Saket` |

## Dashboard Scope Rule

Dashboard 1 is the only cross-outlet dashboard.

Dashboards 2 through 5 are outlet-specific modules. Build them as reusable templates with a mandatory outlet filter, or duplicate dashboard pages with locked filters:

- `Sales_Menu_OUT001`
- `Sales_Menu_OUT002`
- `Sales_Menu_OUT003`
- same pattern for procurement, inventory, and calendar/competitor modules

Do not create separate RAW tables or separate SQL facts per outlet. The enterprise-friendly design is one shared outlet-aware model and outlet-filtered dashboards.

## ABNAH Phase Priority

For the upcoming POSist UAT review, prioritize dashboard adaptation in this order:

1. `Dashboard 4: Inventory and Consumption Intelligence`
2. `Dashboard 3: Vendor and Procurement Analytics`
3. `Dashboard 2: Sales and Menu Intelligence`

Sales and revenue remain important, but the first model-extension pass should focus on source fields that improve inventory pressure, theoretical versus actual consumption, stock movement, reorder logic, vendor performance, PO-to-GRN matching, and procurement value reconciliation.

Use `docs/posist_uat_intake_and_model_adaptation_plan.md` when POSist screenshots, report exports, or API documentation arrive. That screenshot layer is for Codex to understand POSist schema/report structure and adapt the model; it is not an end-user dashboard or production ingestion layer.

Use `docs/external_data_signals_pre_uat_plan.md` before schema design to plan India/NCR context signals with free PoC sources and commercial production candidates kept separate. Candidate signals include IMD/Open-Meteo and commercial weather providers, Google or Mappls vendor route feasibility, manually governed or licensed Delhi/NCR local events, Indian holidays, AQI providers, and commodity data. These should support Inventory/Consumption and Vendor/Procurement first, then Sales/Menu once phase 1 is stable.

## Dashboard 1: Executive / Outlet Comparison / Outlet Health

Scope: cross-outlet comparison across Connaught Place, Hauz Khas, and Saket.

Business questions answered:

- Which outlet had highest sales last month?
- Which outlet is growing after Month 2 or Month 3 refresh?
- Which outlet shows inventory pressure after events?
- Which outlet has the highest event exposure?
- How do the three outlets compare on sales, procurement, receipt value, inventory value, and low-stock pressure?

Primary query tables:

- `SUM_Executive_KPIs`
- `SUM_Outlet_Health`
- `FACT_Outlet_Daily_Health`
- `FACT_Sales`
- `SUM_Event_Markers`

Recommended charts/KPIs:

- All-outlet total net sales KPI
- All-outlet total quantity sold KPI
- Active outlets KPI
- Outlet sales ranking bar chart
- Outlet daily sales trend with one line per outlet
- Outlet health comparison table
- Outlet inventory pressure comparison
- Outlet event exposure comparison
- Event marker/spike explanation table grouped by outlet

Filters:

- Date range/month
- Outlet, optional for drilldown only
- Category
- Event type

Caveats:

- This is the only dashboard where all-outlet totals are encouraged.
- Outlet health score is a demo indicator, not an audited operational score.
- Inventory pressure uses available closing stock and heuristic thresholds, not stockout prediction.

## Dashboard 2: Sales and Menu Intelligence

Scope: outlet-specific template. The dashboard must be filtered to one outlet at a time.

Use for:

- Connaught Place individually
- Hauz Khas individually
- Saket individually

Business questions answered:

- Which menu items sold the most in the selected outlet?
- Which categories contribute most revenue in the selected outlet?
- Which premium items overperform in the selected outlet?
- Which items spike during holidays/events for the selected outlet?

Primary query tables:

- `FACT_Sales`
- `SUM_Sales_Category_Mix`
- `SUM_Menu_Item_Performance`
- `FACT_Event_Sales_Impact`
- `SUM_Event_Impact`

Recommended charts/KPIs:

- Selected-outlet net sales KPI
- Selected-outlet quantity sold KPI
- Net sales by category and super-category
- Quantity sold by item
- Top menu items by sales
- Realized unit price by item
- Menu item contribution table
- Event lift table filtered by affected category/item
- Holiday/event date trend overlay where supported

Mandatory filters:

- Outlet
- Date range/month

Suggested filters:

- Category
- Super-category
- Menu item
- Event type

Caveats:

- Do not aggregate Connaught Place, Hauz Khas, and Saket together in this dashboard unless `outlet_code` and `outlet_name` are included in the chart grouping.
- Sales rows are daily outlet-item aggregates, not individual bills.
- Event lift is directional and depends on baseline query compatibility.

## Dashboard 3: Vendor and Procurement Analytics

Scope: outlet-specific template. The dashboard must be filtered to one outlet at a time.

Business questions answered:

- Which vendors supply which materials for the selected outlet?
- What is each vendor's share of business in the selected outlet?
- Which vendor has highest procurement value in the selected outlet?
- How much did the selected outlet order from a vendor last month?
- Which POs are pending or partially received in the selected outlet?

Primary query tables:

- `FACT_Purchase_Order`
- `FACT_Entry_Receipt`
- `FACT_PO_Receipt_Comparison`
- `FACT_Vendor_Spend`
- `SUM_Vendor_Share`
- `DIM_Vendor`
- `DIM_Ingredient`

Recommended charts/KPIs:

- Selected-outlet purchase order value KPI
- Selected-outlet receipt value KPI
- Vendor share bar chart
- Vendor spend trend
- PO status stacked bar
- Pending/partial PO table
- Vendor-material matrix

Mandatory filters:

- Outlet
- Date range/month

Suggested filters:

- Vendor
- Ingredient/material
- PO status
- Category

Caveats:

- Do not show vendor share as all-outlet vendor share on this dashboard.
- Entry report lacks PO number, so PO-to-receipt matching is approximate by outlet/vendor/item/date window.
- Vendor share is demo spend share, not audited accounts payable spend.

## Dashboard 4: Inventory and Consumption Intelligence

Scope: outlet-specific template. The dashboard must be filtered to one outlet at a time.

Business questions answered:

- Which stock items are low in the selected outlet?
- Which outlet-specific event days created inventory pressure?
- What is theoretical consumption of milk, coffee beans, paneer, or other ingredients based on selected-outlet sales?
- Which materials are used by which recipes sold in the selected outlet?

Primary query tables:

- `FACT_Inventory_Closing`
- `FACT_Theoretical_Consumption`
- `SUM_Inventory_Risk`
- `STD_Recipe_BOM`
- `DIM_Ingredient`
- `FACT_Outlet_Daily_Health`

Recommended charts/KPIs:

- Selected-outlet latest low stock item count
- Selected-outlet latest inventory value
- Low stock table by item
- Theoretical ingredient consumption trend
- Ingredient usage by recipe table
- Inventory value by category
- Event-day inventory pressure table

Mandatory filters:

- Outlet
- Date range/month

Suggested filters:

- Ingredient/material
- Category
- Event type

Caveats:

- Do not combine all three outlet inventories in low-stock tables unless grouped by `outlet_code` and `outlet_name`.
- Theoretical consumption is sales multiplied by BOM quantities.
- This is not full actual-vs-theoretical variance because waste, transfers, and actual consumption postings are not present.
- Low stock is heuristic and should be presented as inventory pressure, not prediction.

## Dashboard 5: Calendar, Event, and Competitor Intelligence

Scope: outlet-specific template. The dashboard must be filtered to one outlet or one outlet market area at a time.

Business questions answered:

- How did sales change after a manual local event was added for the selected outlet?
- Which items spike during holidays/events in the selected outlet?
- Are selected-outlet products priced higher/lower than nearby competitors?
- Which premium items overperform despite higher competitor price in the selected market area?
- Which competitor price disadvantage areas may need review?

Primary query tables:

- `DIM_Event`
- `DIM_Holiday`
- `SUM_Event_Impact`
- `SUM_Event_Markers`
- `FACT_Event_Sales_Impact`
- `FACT_Competitor_Price_Position`
- `SUM_Competitor_Positioning`

Recommended charts/KPIs:

- Event sales lift table
- Spike explanation panel with event date, outlet, event name, affected items, event-day sales, baseline sales, lift percentage, confidence level
- Sales trend with event/holiday filters
- Price index by competitor/category
- ABNAH vs competitor price difference table
- Premium overperformance table
- Price disadvantage review table

Mandatory filters:

- Outlet or market area
- Date range/month

Suggested filters:

- Event type
- Holiday type
- Competitor
- Category/menu item
- Price position

Caveats:

- Competitor pricing is mapped by `market_area`; Connaught Place, Hauz Khas, and Saket should not be blended unless grouped by outlet/market area.
- Competitor pricing is contextual and synthetic.
- Do not claim competitor price caused sales changes.
- If Zoho chart annotations are unavailable, use `SUM_Event_Markers` as the spike explanation panel.
