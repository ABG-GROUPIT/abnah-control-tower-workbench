# Zoho Modelling Approach And Dashboard Coverage README

This README explains the complete modelling approach used for the ABNAH Zoho Analytics demo.

It covers:

1. How Web URL imports fit into the architecture.
2. Why the model has RAW, STD, DIM, FACT, and SUM layers.
3. One complete table journey from raw feed to dashboard-ready insight.
4. What each dashboard KPI/chart answers.
5. What each KPI/chart does not fully answer because the current raw data does not contain enough fields.

## 1. Architecture We Chose

Final demo flow:

```text
Synthetic CSV files
-> Neon PostgreSQL raw tables
-> FastAPI hosted on Render
-> Zoho Analytics Web URL / feed import
-> Zoho RAW tables
-> Zoho Query Tables: STD -> DIM -> FACT -> SUM
-> Zoho dashboards and Ask Zia
```

This is intentionally not direct Zoho-to-Neon modelling.

Direct Neon import works as a fallback, but the final demo approach uses FastAPI CSV feeds because it is closer to a controlled reporting API layer.

## 2. Web URL Import Approach

### 2.1 Why Web URLs

Zoho Analytics can import CSV-like data from public HTTPS URLs. Our FastAPI service returns CSV responses at stable feed URLs. This allows the demo to behave like a lightweight data connector.

Hosted base URL:

```text
https://abnah-zoho-synthetic-demo-api.onrender.com
```

Feed pattern:

```text
/zoho/<report_name>.csv?token=<FEED_TOKEN>
/zoho/<report_name>_<OUTLET_CODE>.csv?token=<FEED_TOKEN>
```

Examples:

```text
/zoho/sales_report_OUT001.csv?token=<FEED_TOKEN>
/zoho/purchase_report_OUT002.csv?token=<FEED_TOKEN>
/zoho/menu_master.csv?token=<FEED_TOKEN>
```

### 2.2 Why Outlet-Specific Operational Feeds

Operational reports are imported separately by outlet:

```text
RAW_Sales_Report_OUT001
RAW_Sales_Report_OUT002
RAW_Sales_Report_OUT003
RAW_Purchase_Report_OUT001
...
```

This was chosen because:

- outlet-level testing becomes simple,
- Zoho refresh behavior can be tested outlet by outlet,
- each raw table stays small,
- the STD layer can union the three outlet feeds back into one analytics table,
- dashboard filters can work across all outlets after modelling.

Static/master reports are imported once:

```text
RAW_Menu_Master
RAW_Vendor_Report
RAW_Brand_Recipe_Consumption
RAW_Indian_Calendar_Holidays
RAW_Manual_Calendar_Events
RAW_Competitor_Pricing
```

### 2.3 Refresh Rule

Zoho should refresh the same Web URL source. It should not create new tables per month.

Correct behavior:

```text
Month 1 loaded -> Zoho imports feed rows.
Month 2 loaded -> same feed URL returns Month 1 + Month 2 rows.
Zoho refreshes same RAW table.
Month 3 loaded -> same feed URL returns Month 1 + Month 2 + Month 3 rows.
```

Important check:

```text
row_id must not duplicate after refresh.
```

If Zoho appends the full feed every refresh without key handling, downstream dashboards will double-count.

## 3. Layered Zoho Model

The Zoho model has five layers.

### 3.1 RAW Layer

Purpose:

```text
Imported feed tables exactly as Zoho receives them from FastAPI.
```

RAW tables should not be used directly for dashboards.

Why:

- three outlet feeds need to be unioned,
- raw column names are report-style,
- some values need type casting,
- recipe BOM has blank continuation rows,
- raw tables do not have a unified outlet code / market area field in every report,
- raw tables are not enriched with dimensions or facts.

### 3.2 STD Layer

Purpose:

```text
Standardize raw reports into consistent, typed, outlet-aware tables.
```

Examples:

```text
RAW_Sales_Report_OUT001 + OUT002 + OUT003 -> STD_Sales_Report
RAW_Purchase_Report_OUT001 + OUT002 + OUT003 -> STD_Purchase_Report
RAW_Inventory_Closing_Report_OUT001 + OUT002 + OUT003 -> STD_Inventory_Closing_Report
```

STD tables should:

- preserve row IDs,
- add `outlet_code`,
- add `market_area`,
- standardize dates,
- standardize numeric fields,
- create reusable join keys.

### 3.3 DIM Layer

Purpose:

```text
Create reusable lookup/filter dimensions.
```

Core dimensions:

```text
DIM_Date
DIM_Outlet
DIM_Menu_Item
DIM_Vendor
DIM_Ingredient
DIM_Event
DIM_Holiday
DIM_Competitor
```

DIM tables help with:

- user filters,
- consistent labels,
- reusable joins,
- Ask Zia context,
- reduced duplicated business logic.

### 3.4 FACT Layer

Purpose:

```text
Create analytic transaction/activity tables at a usable grain.
```

FACT tables are where dashboards should usually start.

Examples:

```text
FACT_Sales
FACT_Purchase_Order
FACT_Entry_Receipt
FACT_Inventory_Closing
FACT_Theoretical_Consumption
FACT_PO_Receipt_Comparison
FACT_Event_Sales_Impact
FACT_Competitor_Price_Position
FACT_Outlet_Daily_Health
FACT_Vendor_Spend
```

FACT tables keep dates and filters usable. If a dashboard must respond to a date range, prefer a FACT table over a full-period SUM table.

### 3.5 SUM Layer

Purpose:

```text
Create focused dashboard-ready aggregates.
```

SUM tables are useful when the grain is intentionally fixed, such as latest inventory snapshot or full-month item performance.

Examples:

```text
SUM_Inventory_Risk
SUM_Event_Impact
SUM_Competitor_Positioning
SUM_Menu_Item_Performance
SUM_Outlet_Health
```

Do not use a SUM table when the dashboard needs a filter that the SUM table does not contain.

Example:

```text
SUM_Inventory_Risk is latest inventory only.
It should not be expected to respond to Sales Date Range.
```

## 4. Complete Example: Sales Report Journey

This is the clearest example of why the layered model matters.

### 4.1 Raw Source: FastAPI Feed

Zoho imports outlet-specific sales URLs:

```text
RAW_Sales_Report_OUT001 <- /zoho/sales_report_OUT001.csv
RAW_Sales_Report_OUT002 <- /zoho/sales_report_OUT002.csv
RAW_Sales_Report_OUT003 <- /zoho/sales_report_OUT003.csv
```

RAW schema:

| Column | Meaning |
|---|---|
| `row_id` | Source row key |
| `outlet_name` | Outlet label from synthetic source |
| `date` | Sales date |
| `super_category` | Menu super category |
| `category` | Menu category |
| `item_number` | Menu item code |
| `item_name` | Menu item name |
| `qty` | Units sold |
| `net_sale` | Net sales value |

Month 1 row counts:

| RAW table | Month 1 rows |
|---|---:|
| `RAW_Sales_Report_OUT001` | 1,529 |
| `RAW_Sales_Report_OUT002` | 1,595 |
| `RAW_Sales_Report_OUT003` | 1,731 |

### 4.2 Standardized Layer: `STD_Sales_Report`

Query file:

```text
docs/zoho_query_table_sql/01_std_sales_report.sql
```

Purpose:

```text
Union three outlet sales feeds and create a stable daily outlet-item sales grain.
```

STD schema:

| Column | Source / transformation |
|---|---|
| `sales_row_id` | RAW `row_id` |
| `outlet_name` | RAW `outlet_name` |
| `outlet_code` | Derived from outlet name |
| `market_area` | Derived from outlet name |
| `sales_date` | RAW `date` converted to date |
| `super_category` | RAW `super_category` |
| `category` | RAW `category` |
| `item_number` | RAW `item_number` |
| `item_name` | RAW `item_name` |
| `qty` | RAW `qty` as decimal/number |
| `net_sale` | RAW `net_sale` as decimal/currency |
| `net_sale_per_qty` | `net_sale / qty` |

Why this matters:

- all outlets become one table,
- every sales row has `outlet_code`,
- date filters use `sales_date`,
- item filters use `item_number` and `item_name`,
- unit price realization becomes reusable.

### 4.3 Dimension Layer: `DIM_Menu_Item`

Query file:

```text
docs/zoho_query_table_sql/13_dim_menu_item.sql
```

Purpose:

```text
Create one reusable menu item dimension from menu master and sold items.
```

Relevant schema:

| Column | Meaning |
|---|---|
| `menu_item_key` | Stable key |
| `item_number` | Menu item code |
| `item_name` | Menu item label |
| `menu_rate` | Listed menu price |
| `category_name` | Master category |
| `super_category_name` | Master super category |
| `non_veg` | Menu flag |
| `has_variant` | Variant flag |
| `source_type` | Master or sales-derived fallback |

Why this matters:

- all menu charts can use consistent item/category naming,
- Ask Zia can understand menu item context,
- item ranking and category mix avoid raw naming drift.

### 4.4 Fact Layer: `FACT_Sales`

Query file:

```text
docs/zoho_query_table_sql/17_fact_sales.sql
```

Purpose:

```text
Create date-safe sales fact enriched with menu metadata and holiday context.
```

FACT schema:

| Column | Meaning |
|---|---|
| `sales_row_id` | Sales row key |
| `sales_date` | Date used for sales filters |
| `outlet_code` | Outlet code |
| `outlet_name` | Outlet name |
| `market_area` | Market area |
| `item_number` | Menu item code |
| `item_name` | Menu item name |
| `super_category` | Sales super category |
| `category` | Sales category |
| `menu_rate` | Menu master rate if matched |
| `qty` | Units sold |
| `net_sale` | Net sales value |
| `net_sale_per_qty` | Realized average unit value |
| `holiday_name` | Holiday context if date matched |
| `holiday_type` | Holiday type |
| `holiday_impact_direction` | Expected holiday direction |

Why this matters:

- Date Range filters work.
- Outlet filters work.
- Category and item charts work.
- Holiday context can be shown without changing raw sales.
- Chart values are not fixed full-month summaries.

### 4.5 Summary Layer: Sales Summaries

`SUM_Sales_Category_Mix`:

| Column | Meaning |
|---|---|
| `outlet_code` | Outlet code |
| `outlet_name` | Outlet name |
| `market_area` | Market area |
| `super_category` | Sales super category |
| `category` | Sales category |
| `total_qty` | Full-period quantity |
| `total_net_sale` | Full-period revenue |
| `net_sale_share_pct` | Share within outlet |
| `outlet_net_sale` | Outlet total used for share |

`SUM_Menu_Item_Performance`:

| Column | Meaning |
|---|---|
| `outlet_code` | Outlet code |
| `outlet_name` | Outlet name |
| `market_area` | Market area |
| `item_number` | Menu item code |
| `item_name` | Menu item name |
| `super_category` | Super category |
| `category` | Category |
| `total_qty` | Full-period units sold |
| `total_net_sale` | Full-period net sales |
| `avg_realized_unit_price` | Sales realization |
| `avg_price_index` | Competitor context if mapped |
| `price_position` | Premium/discount/parity context |
| `performance_note` | Interpretation label |

Use `FACT_Sales` for date-filtered sales charts. Use `SUM_Menu_Item_Performance` only when a full-period item ranking is acceptable.

## 5. Dashboard Coverage And Data Sufficiency

This section explains what each dashboard element answers and what it cannot fully answer with current raw data.

### 5.1 Dashboard 1: Executive Outlet Health

Purpose:

```text
Give leadership a cross-outlet view of sales, procurement pressure, inventory pressure, and event exposure.
```

| KPI / chart | Business question answered | Source and data points | Answer quality | Missing data for a production-grade answer |
|---|---|---|---|---|
| Net Sales Revenue | What did the outlet/chain sell in the selected date range? | `FACT_Outlet_Daily_Health.net_sales`, from `FACT_Sales.net_sale` | Complete for synthetic sales revenue | Discounts by reason, channel mix, tax treatment, returns/refunds |
| Average Daily Revenue | What is the revenue run-rate per active sales day? | `SUM(net_sales) / DISTINCTCOUNT(activity_date)` | Complete for active-day run-rate | Store operating hours and closed-day reason |
| PO Raised Value | How much procurement value was ordered? | `FACT_Outlet_Daily_Health.po_value`, from `FACT_Purchase_Order.total_item_cost` | Partial | Actual approvals, cancelled value treatment, PO revisions |
| Receipt Booked Value | How much value was received/booked? | `FACT_Outlet_Daily_Health.receipt_value`, from `FACT_Entry_Receipt.grand_total` / receipt values | Partial | PO number on receipt rows, actual GRN-to-PO matching |
| Purchase-To-Sales Ratio | How heavy is procurement spend versus sales? | `SUM(po_value) / SUM(net_sales)` | Directional | Opening inventory, wastage, actual COGS, transfers, vendor credit notes |
| Revenue Per Avg Inventory Rupee | How much revenue is generated per rupee of average inventory value? | `SUM(net_sales) * DISTINCTCOUNT(activity_date) / SUM(inventory_value)` | Directional | True average inventory by opening/closing, COGS, actual consumption |
| Daily Sales Trend | Which days spike or dip by outlet? | `FACT_Outlet_Daily_Health.activity_date`, `net_sales`, event notes | Good for synthetic trend | Hourly sales, footfall, channel, weather |
| Outlet Sales Ranking | Which outlet leads revenue? | `SUM(net_sales)` by `outlet_name` | Complete for sales ranking | Profit, rent, labor, capacity |
| Sales vs Purchase vs Receipt Comparison | Is procurement pressure aligned with sales? | `net_sales`, `po_value`, `receipt_value` by outlet/date | Partial | Actual consumption, inventory movement, PO-to-GRN matching |

Important questions not fully answerable yet:

| Question | Why not fully answerable | Required future data |
|---|---|---|
| Which outlet is most profitable? | No labor, rent, utilities, discounts, COGS, waste | P&L data, recipe-level actual COGS, payroll, rental overhead |
| Which outlet is operationally underperforming? | No service speed, complaints, footfall, uptime | POS bills, service metrics, feedback, staffing, store hours |
| Which outlet needs replenishment fastest? | Low-stock thresholds are heuristic | Reorder levels, lead times, actual consumption, current open POs |

### 5.2 Dashboard 2: Sales And Menu Intelligence

Purpose:

```text
Explain revenue mix, item winners, category trends, and menu performance.
```

| KPI / chart | Business question answered | Source and data points | Answer quality | Missing data for a production-grade answer |
|---|---|---|---|---|
| Selected Outlet Net Sales | How much did this outlet sell? | `FACT_Sales.net_sale` | Complete for synthetic net sales | Channel, order count, discount reason |
| Sales Trend | Which days changed sales? | `FACT_Sales.sales_date`, `net_sale` | Good | Hourly split, weather, traffic |
| Category Revenue Mix | Which menu categories drive revenue? | `FACT_Sales.category`, `net_sale` | Complete for category sales | Gross margin by category |
| Super Category Mix | What is beverage/food/dessert contribution? | `FACT_Sales.super_category`, `net_sale` | Complete for revenue contribution | Item profitability |
| Top Menu Items By Net Sales | Which items are biggest revenue drivers? | `FACT_Sales.item_name`, `SUM(net_sale)` | Complete for revenue | Contribution margin, waste, prep complexity |
| Top Menu Items By Quantity | Which items move most units? | `FACT_Sales.item_name`, `SUM(qty)` | Complete for units | Ticket count, order attach rate |
| Realized Unit Price | Are items selling at expected value? | `net_sale_per_qty`, menu rate | Directional | Discount rule, delivery commission, tax inclusion |
| Menu Item Detail Table | What exact items/categories explain the view? | `FACT_Sales` or date-safe summary | Complete if built from `FACT_Sales` | Margin and ingredient cost |

Important questions not fully answerable yet:

| Question | Why not fully answerable | Required future data |
|---|---|---|
| Which menu items are most profitable? | No recipe cost valuation or actual ingredient depletion | Ingredient purchase cost by batch, recipe cost, wastage |
| Which items are usually bought together? | Sales data is daily outlet-item aggregate, not bill-level | Bill/order ID, line-level ticket data |
| What caused a category dip? | No footfall, channel, staff, weather, campaign spend | Footfall, channel, campaign calendar, operations logs |

### 5.3 Dashboard 3: Vendor And Procurement Analytics

Purpose:

```text
Explain PO value, receipt value, vendor concentration, and PO follow-up risk.
```

| KPI / chart | Business question answered | Source and data points | Answer quality | Missing data for a production-grade answer |
|---|---|---|---|---|
| PO Raised Value | What value of POs was raised? | `FACT_Vendor_Spend.ordered_value`, from purchase report | Complete for PO raised value | Approval history, PO revisions |
| Receipt Booked Value | What value was received/booked? | `FACT_Vendor_Spend.received_value`, from entry report | Partial | Receipt rows do not carry PO number |
| PO vs Receipt Value Gap | Is ordered value larger than booked value? | `SUM(ordered_value) - SUM(received_value)` | Directional | Exact PO-GRN matching |
| Open / Partial PO Status Count | How many PO lines need operational follow-up? | `SUM(open_or_partial_po_count)` | Good for status/remaining quantity | True delivery status updates |
| Vendor PO Raised Share | Which vendors dominate PO value? | `vendor_name`, `SUM(ordered_value)` | Complete for PO share | Contract pricing, vendor SLA |
| Vendor Receipt Booked Share | Which vendors dominate receipt value? | `vendor_name`, `SUM(received_value)` | Partial | Exact PO-to-receipt match |
| PO Status Chart | How many lines are Closed/Pending/Partial/Cancelled? | `FACT_Purchase_Order.po_status`, `COUNT` or `SUM(total_item_cost)` | Complete for synthetic PO statuses | Real approval/cancellation reasons |
| Pending PO Detail Table | Which PO lines need follow-up? | `FACT_PO_Receipt_Comparison`, `pending_or_partial_flag`, `remaining_qty` | Directional | PO number on GRN rows |
| Vendor Material Matrix | Which vendor supplies which materials? | `FACT_Purchase_Order.vendor_name`, `item_name`, `total_item_cost` | Good | Preferred vendor contracts and price history |

Important questions not fully answerable yet:

| Question | Why not fully answerable | Required future data |
|---|---|---|
| Which vendors are late? | No actual delivery timestamp tied to PO number | PO number in receipts, delivery timestamp, SLA |
| Which vendors have quality issues? | No rejection/quality inspection data | QC results, return reasons, supplier scorecards |
| Are prices rising? | Current data has limited synthetic period and no contract rates | Longer purchase history, negotiated rates, market index |

### 5.4 Dashboard 4: Inventory And Consumption Intelligence

Purpose:

```text
Explain current stock value, low-stock pressure, and recipe-derived ingredient demand.
```

| KPI / chart | Business question answered | Source and data points | Answer quality | Missing data for a production-grade answer |
|---|---|---|---|---|
| Current Inventory Value | What is current stock value? | `SUM_Inventory_Risk.total_amt`, latest inventory snapshot | Complete for synthetic latest stock | Opening/closing valuation policy, expiry, batch price |
| Current Low-Stock Material Count | How many materials are in low stock? | `SUM(low_stock_flag)` | Directional | Item-specific reorder levels |
| Current Stock Pressure Band | How many materials are Low/Watch/OK? | `inventory_pressure_band` from `total_qty` thresholds | Directional | Reorder threshold by material and outlet |
| Inventory Value By Category | Where is stock capital concentrated? | `SUM_Inventory_Risk.category_name`, `total_amt` | Good current stock view | Category-level carrying cost and spoilage |
| Top Inventory Value Items | Which materials hold most stock value? | `item_name`, `total_amt` | Good | Shelf life and stock age |
| Low Stock Items Table | Which current items need review? | `low_stock_flag`, `total_qty`, `risk_note` | Directional | Lead time and reorder point |
| Theoretical Ingredient Demand | What material demand did sales create? | `FACT_Theoretical_Consumption.theoretical_ingredient_qty`, filtered by `demand_component_type = Recipe Ingredient` when the chart should exclude packaging | Good theoretical model | Actual consumption postings, wastage, substitutions |
| Menu To Material Demand | Which menu items drove ingredient demand? | `menu_item_name`, `ingredient_name`, `demand_component_type`, `theoretical_ingredient_qty` | Good theoretical explanation | Actual kitchen usage and yield loss |

Important questions not fully answerable yet:

| Question | Why not fully answerable | Required future data |
|---|---|---|
| Will this item stock out tomorrow? | No reorder points, lead times, planned demand, actual depletion | Lead time, min/max levels, daily opening/closing stock, forecast |
| What is actual vs theoretical variance? | No actual ingredient consumption posting | Kitchen issue notes, production/wastage, stock adjustments |
| Which stock is expiring? | No batch/expiry dates | Batch-level stock and expiry |

### 5.5 Dashboard 5: Calendar, Event, And Competitor Intelligence

Purpose:

```text
Explain sales lift around known events and competitor price positioning.
```

| KPI / chart | Business question answered | Source and data points | Answer quality | Missing data for a production-grade answer |
|---|---|---|---|---|
| Event Day Sales | What sales occurred during configured events? | `SUM_Event_Impact.event_day_sales` | Directional | Actual campaign spend and footfall |
| Event Lift Percent | Was event-day sales above baseline? | `sales_lift_pct`, event vs baseline comparison | Directional | Control group, longer baseline, external factors |
| Spike Explanation Panel | Which event may explain a sales spike? | `SUM_Event_Markers` | Good for demo explanation | Causal experiment design |
| Holiday/Event Sales Trend | How did sales move around events? | `FACT_Sales.sales_date`, event/holiday context | Good visual story | Weather, channel, operational constraints |
| Competitor Price Index | Is ABNAH priced above/below nearby competitors? | `SUM_Competitor_Positioning.avg_price_index` | Good price context | Competitor live menu, promo prices |
| ABNAH vs Competitor Difference | How large is price gap by category? | `avg_price_difference`, `price_position_band` | Good context | Like-for-like size, item comparability |
| Premium Overperformance Table | Which premium-priced items still sold well? | competitor mapping + `FACT_Sales.qty/net_sale` | Directional | Causal pricing test and promo context |

Important questions not fully answerable yet:

| Question | Why not fully answerable | Required future data |
|---|---|---|
| Did the event cause the lift? | Current model is correlation/directional | Control group, experiment design, campaign spend |
| Did competitor pricing cause sales loss? | Competitor data is contextual | Time-varying competitor prices, demand elasticity, promotions |
| Which campaign ROI was best? | No campaign cost | Campaign spend, redemption, channel attribution |

## 6. Modelling Lessons And Rules For The Demo

### 6.1 Use Date-Grain FACT Tables For Date Filters

If a dashboard filter is Date Range, the source chart must include the correct date column.

Examples:

```text
Sales Date Range -> FACT_Sales.sales_date
Procurement Date Range -> FACT_Vendor_Spend.activity_date
Inventory Date Range -> FACT_Inventory_Closing.inventory_date
Event Date Range -> SUM_Event_Markers.event_date or FACT_Event_Sales_Impact.sales_date
```

### 6.2 Use Latest Snapshot SUM Tables Only For Current-State Cards

Example:

```text
SUM_Inventory_Risk = current/latest stock view.
```

It should not be expected to change with a sales date filter.

### 6.3 Do Not Sum Ratios

Bad:

```text
SUM(outlet_ratio)
```

Good:

```text
SUM(numerator) / SUM(denominator)
```

Examples:

```text
Purchase-To-Sales Ratio = SUM(po_value) / SUM(net_sales)
Revenue Per Avg Inventory Rupee = SUM(net_sales) * DISTINCTCOUNT(activity_date) / SUM(inventory_value)
```

### 6.4 Do Not Claim Causality From Context Tables

Competitor and event tables support business context.

They do not prove:

```text
Competitor price caused sales change.
Event caused all sales lift.
Low stock caused sales loss.
```

Use language like:

```text
directional lift
contextual signal
pressure indicator
requires operational validation
```

## 7. Recommended Demo Explanation

Use this summary when explaining the modelling approach to someone:

```text
We imported the same report-style CSVs that an operations team would export from a backend system. Zoho receives them through secured Web URL feeds from FastAPI. Inside Zoho, RAW tables are kept untouched, STD tables clean and union outlet feeds, DIM tables create reusable lookup/filter entities, FACT tables preserve business activity at date-safe grains, and SUM tables create dashboard-ready aggregates. Every dashboard visual is built only from FACT or SUM tables, depending on whether the visual needs filter-safe detail or an intentionally fixed summary.
```

## 8. POSist/UAT Adaptation Extension

The next ABNAH discovery phase should use `docs/posist_uat_intake_and_model_adaptation_plan.md`.

The existing layered model remains the backbone. New POSist screenshots, report exports, and API docs should first be cataloged, mapped, and validated before any `STD_*`, `DIM_*`, `FACT_*`, or `SUM_*` tables are changed.

This screenshot/API catalog is a Codex working layer for schema discovery across a large screenshot batch. It is not the product experience and should not become the production ingestion path.

Before schema changes, use `docs/external_data_signals_pre_uat_plan.md` to shortlist lean India/NCR external context signals while keeping free PoC sources separate from commercially available production candidates. Candidate signals include IMD/Open-Meteo and commercial weather providers, Google or Mappls vendor route time, geocodes, manually governed or licensed Delhi/NCR events, Indian holidays, AQI providers, and commodity data. These signals should be treated as enrichment/context features until POSist UAT confirms the internal grains and keys they can join to.

Phase priority:

| Priority | Domain | Goal |
|---|---|---|
| P0 | Inventory and consumption | Find source fields for actual consumption, stock movement, wastage, transfers, reorder levels, lead times, expiry/batches, and UOM conversion. |
| P0 | Vendor and procurement | Find source fields for exact PO-GRN linkage, delivery status, rate history, rejection/QC, returns, vendor SLA, and payable/procurement lifecycle. |
| P1 | Sales and revenue | Find bill-level, channel, discount, refund, payment, item modifier, and timestamp fields after P0 mapping is stable. |

Do not treat screenshots alone as final schema proof. Screenshots identify report structure and business intent. API docs, exports, or sample responses are needed to confirm field names, data types, grain, refresh behavior, and validation totals.
