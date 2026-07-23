# Additional Dashboard Charts Deep-Dive README

This README proposes extra dashboard charts that can be built using only the raw data points already available in the project.

No new raw data points are allowed.

Allowed:

```text
Aggregate formulas
Query-table transformations
Existing dimensions
Existing FACT and SUM tables
Existing RAW-derived fields
```

Not allowed:

```text
Bill-level basket analysis
Customer-level analysis
True profit margin
True COGS
Labor cost
Rent/utilities
Wastage
Expiry
Exact PO-to-GRN matching
Vendor SLA scoring
Campaign ROI
```

Those need raw fields that we do not currently have.

## 1. Selection Criteria

Only add a visual if it passes all checks:

| Check | Requirement |
|---|---|
| Business relevance | A department leader can act on or question it |
| Data support | Existing raw fields can support the metric |
| Filter behavior | Required filters exist in the source table |
| Non-duplication | It does not repeat the exact same story as another chart |
| Caveat clarity | If partial, the limitation is understandable |

## 2. Dashboard 1: Executive Outlet Health

Current dashboard already has revenue, average daily revenue, procurement spend, purchase-to-sales ratio, inventory productivity, and low-stock count.

Add charts that explain why the outlet score differs.

### 2.1 Outlet Operating Balance Matrix

Business question:

```text
Which outlet has high sales but also high procurement/inventory pressure?
```

Source:

```text
FACT_Outlet_Daily_Health
```

Chart:

```text
Type: Scatter / bubble
X-axis: net_sales
X aggregation: Sum
Y-axis: po_value
Y aggregation: Sum
Bubble size: inventory_value
Bubble size aggregation: Average
Color: outlet_name
Tooltip: receipt_value, low_stock_item_count, event_count
```

Filters:

```text
Date Range -> activity_date
Outlet -> outlet_name
```

Why useful:

```text
Shows sales scale and purchase pressure together instead of as isolated cards.
```

Caveat:

```text
This is not profit. Procurement value is not COGS.
```

### 2.2 Outlet Sales vs Receipt Realization

Business question:

```text
Are receipts/booked vendor movements aligned with outlet sales scale?
```

Source:

```text
FACT_Outlet_Daily_Health
```

Chart:

```text
Type: Combo bar + line
X-axis: outlet_name
Bar Y-axis: net_sales
Bar aggregation: Sum
Line Y-axis: receipt_value
Line aggregation: Sum
Optional second line: po_value
Sort: SUM(net_sales) descending
```

Filters:

```text
Date Range -> activity_date
Outlet -> outlet_name
```

Why useful:

```text
Makes it obvious if a lower-sales outlet has unusually heavy receipt movement.
```

Caveat:

```text
Receipts are not exact item-level COGS for the same sales period.
```

### 2.3 Inventory Pressure Item-Days By Outlet

Business question:

```text
Which outlet had repeated low-stock pressure during the selected period?
```

Source:

```text
FACT_Outlet_Daily_Health
```

Chart:

```text
Type: Horizontal bar
X-axis: outlet_name
Y-axis: low_stock_item_count
Y aggregation: Sum
Color: market_area
Sort: SUM(low_stock_item_count) descending
```

Filters:

```text
Date Range -> activity_date
Outlet -> outlet_name
```

Why useful:

```text
It separates repeated historical pressure from latest low-stock snapshot.
```

Caveat:

```text
This is item-days, not current item count. One item low for five days counts as five pressure item-days.
```

### 2.4 Event Exposure vs Sales Lift Panel

Business question:

```text
Which outlet had sales during event-marked days and did those days look different?
```

Source:

```text
SUM_Event_Markers
```

Chart:

```text
Type: Table
Rows:
  event_date
  outlet_name
  event_name
  event_type
Values:
  event_day_sales
  baseline_sales
  sales_lift_percentage
  confidence_level
Sort:
  event_date ascending
```

Filters:

```text
Outlet -> outlet_name
Date Range -> event_date
Event Type -> event_type
```

Why useful:

```text
Gives leadership an explanation panel for spikes without overloading the main chart.
```

Caveat:

```text
Event lift is directional. It is not causal proof.
```

## 3. Dashboard 2: Sales And Menu Intelligence

Current dashboard covers category mix, top items, and item detail. Add visuals that separate volume, price realization, and category momentum.

### 3.1 Revenue vs Quantity Menu Quadrant

Business question:

```text
Which items are high-revenue because of volume, price, or both?
```

Source:

```text
FACT_Sales
```

Chart:

```text
Type: Scatter
X-axis: qty
X aggregation: Sum
Y-axis: net_sale
Y aggregation: Sum
Color: category
Tooltip: item_name, net_sale_per_qty
```

Filters:

```text
Outlet -> outlet_name
Sales Date Range -> sales_date
Menu Category -> category
Menu Item -> item_name
```

Why useful:

```text
Separates high-volume items from high-value items.
```

Caveat:

```text
Not a profit quadrant because cost/margin is unavailable.
```

### 3.2 Realized Price vs Menu Rate

Business question:

```text
Which items realize below/above listed menu rate?
```

Source:

```text
FACT_Sales
```

Required aggregate formulas:

```text
AF_Realized_Unit_Price = SUM(net_sale) / SUM(qty)
AF_Realization_Variance = (SUM(net_sale) / SUM(qty)) - AVG(menu_rate)
AF_Realization_Index = (SUM(net_sale) / SUM(qty)) / AVG(menu_rate)
```

Chart:

```text
Type: Horizontal bar
X-axis: item_name
Y-axis: AF_Realization_Variance
Color: category
Sort: AF_Realization_Variance ascending
Top/Bottom: show bottom 10 or use filter for variance below 0
```

Filters:

```text
Outlet -> outlet_name
Sales Date Range -> sales_date
Menu Category -> category
Menu Item -> item_name
```

Why useful:

```text
Highlights discounting, mix, or data issues where realized sale per unit differs from listed rate.
```

Caveat:

```text
We do not have discount reason or channel commission, so variance is only a signal.
```

### 3.3 Category Trend Stacked Area

Business question:

```text
How does category contribution change over time?
```

Source:

```text
FACT_Sales
```

Chart:

```text
Type: Stacked area or stacked bar
X-axis: sales_date
Y-axis: net_sale
Y aggregation: Sum
Color: category
```

Filters:

```text
Outlet -> outlet_name
Sales Date Range -> sales_date
Menu Category -> category
```

Why useful:

```text
Shows whether a day was driven by coffee, dessert, food, shakes, etc.
```

Caveat:

```text
Too many categories can clutter the chart. Use Top N categories if needed.
```

### 3.4 Day-Of-Week Sales Heatmap

Business question:

```text
Which weekdays are strongest by category or outlet?
```

Source:

```text
FACT_Sales
```

Chart:

```text
Type: Pivot heatmap
Rows: category
Columns: day_of_week_name
Values: SUM(net_sale)
Sort columns by: day_of_week_sort ascending
```

Filters:

```text
Outlet -> outlet_name
Sales Date Range -> sales_date
Menu Category -> category
Super Category -> super_category
Item Name -> item_name
```

Why useful:

```text
Useful for weekly demand patterns. If the selected date range contains multiple Mondays, those Mondays are summed into the Monday column.
```

Caveat:

```text
No hourly sales or labor data, so this cannot directly prescribe staffing levels.
```

Important behavior:

```text
This heatmap always has seven weekday columns because it groups dates into weekday buckets.
It is self-adjusting because Sales Date Range filters FACT_Sales.sales_date.
If Month 2 or Month 3 data is loaded, new dates automatically map to day_of_week_name.
```

### 3.5 Top 5 Category-Item Winners List

Business question:

```text
For the selected filters, which categories and items should be discussed first?
```

Source:

```text
FACT_Sales
```

Build:

```text
Type: Summary View
Rows:
  category
  item_name
Values:
  SUM(net_sale)
  SUM(qty)
  SUM(net_sale) / SUM(qty)
Sort:
  SUM(net_sale) descending
Limit:
  Top 5 or Top 10
```

Filters:

```text
Outlet -> outlet_name
Sales Date Range -> sales_date
Menu Category -> category
Menu Item -> item_name
```

Why useful:

```text
This fills dashboard space with a compact list that updates correctly with filters.
```

Caveat:

```text
It is revenue/volume only, not margin.
```

## 4. Dashboard 3: Vendor And Procurement Analytics

Current dashboard has value KPIs and vendor share. Add visuals that separate PO status, value gap, and vendor-material concentration.

### 4.1 PO Status Value Pipeline

Business question:

```text
How much PO value sits in Closed, Partially Received, Pending, or Cancelled?
```

Source:

```text
FACT_Purchase_Order
```

Chart:

```text
Type: Stacked bar
X-axis: po_status
Y-axis: total_item_cost
Y aggregation: Sum
Color: po_status
```

Filters:

```text
Outlet -> outlet_name
Procurement Date -> po_date
Vendor -> vendor_name
Material -> item_name
PO Status -> po_status
```

Why useful:

```text
Shows operational follow-up value, not just count.
```

Caveat:

```text
Cancelled POs are shown as PO history. They should not be treated as active obligation unless the business wants that.
```

### 4.2 PO vs Receipt Gap By Vendor

Business question:

```text
Which vendors have the largest value gap between PO raised and receipt booked?
```

Source:

```text
FACT_Vendor_Spend
```

Aggregate formula:

```text
AF_PO_Receipt_Gap = SUM(ordered_value) - SUM(received_value)
```

Chart:

```text
Type: Horizontal bar
X-axis: vendor_name
Y-axis: AF_PO_Receipt_Gap
Sort: AF_PO_Receipt_Gap descending
Color: vendor_name or category_name
```

Filters:

```text
Outlet -> outlet_name
Procurement Date -> activity_date
Vendor -> vendor_name
Material -> item_name
```

Do not map PO Status to this chart unless you specifically want a status-scoped gap.

Why useful:

```text
Prevents confusion between value gap and open/partial count.
```

Caveat:

```text
Entry rows do not carry PO number, so receipt booking is approximate by vendor/item/date movement.
```

### 4.3 Vendor Material Concentration Matrix

Business question:

```text
Which vendors supply which material categories and where is spend concentrated?
```

Source:

```text
FACT_Purchase_Order
```

Chart:

```text
Type: Pivot / matrix heatmap
Rows: vendor_name
Columns: category_name
Values: SUM(total_item_cost)
```

Filters:

```text
Outlet -> outlet_name
Procurement Date -> po_date
Vendor -> vendor_name
Material -> item_name
PO Status -> po_status
```

Why useful:

```text
Shows dependency concentration by vendor and category.
```

Caveat:

```text
It does not evaluate vendor quality or SLA.
```

### 4.4 Pending Quantity By Material

Business question:

```text
Which materials have the highest pending/unmatched quantity?
```

Source:

```text
FACT_PO_Receipt_Comparison
```

Chart:

```text
Type: Horizontal bar
X-axis: item_name
Y-axis: unmatched_order_qty or remaining_qty
Y aggregation: Sum
Color: vendor_name
Criteria: pending_or_partial_flag = 1
Sort: SUM(unmatched_order_qty) descending
```

Filters:

```text
Outlet -> outlet_name
Procurement Date -> po_date
Vendor -> vendor_name
Material -> item_name
PO Status -> po_status
```

Why useful:

```text
Turns open/partial PO status into a material-level action list.
```

Caveat:

```text
PO-to-receipt matching is approximate because receipt rows lack PO number.
```

### 4.5 Receipt Booking Trend

Business question:

```text
When did receipt value actually get booked?
```

Source:

```text
FACT_Entry_Receipt
```

Chart:

```text
Type: Line
X-axis: receipt_date
Y-axis: grand_total or entry_total
Y aggregation: Sum
Color: vendor_name or category_name
```

Filters:

```text
Outlet -> outlet_name
Receipt Date -> receipt_date
Vendor -> vendor_name
Material -> item_name
```

Why useful:

```text
Separates receipt timing from PO creation timing.
```

Caveat:

```text
Receipt date may not exactly match expected delivery or PO close status.
```

## 5. Dashboard 4: Inventory And Consumption Intelligence

Current dashboard should show current stock and theoretical demand separately. Add visuals that make the separation useful.

### 5.1 Current Value vs Theoretical Demand Quadrant

Business question:

```text
Which materials have high current value and high theoretical demand?
```

Source:

```text
SUM_Inventory_Risk
```

Chart:

```text
Type: Scatter
X-axis: total_theoretical_qty
X aggregation: Sum
Y-axis: total_amt
Y aggregation: Sum
Color: inventory_pressure_band
Tooltip: item_name, category_name, total_qty, risk_note
```

Filters:

```text
Outlet -> outlet_name
Inventory Category -> category_name
Inventory Item -> item_name
Stock Pressure Band -> inventory_pressure_band
```

Why useful:

```text
Highlights materials that are expensive and demanded, or demanded but low.
```

Caveat:

```text
The theoretical demand in SUM_Inventory_Risk is not date-filtered. For date-filtered demand, use FACT_Theoretical_Consumption.
```

### 5.2 Stock Pressure By Category

Business question:

```text
Which inventory categories have the most Low or Watch items?
```

Source:

```text
SUM_Inventory_Risk
```

Chart:

```text
Type: Stacked bar
X-axis: category_name
Y-axis: item_code
Y aggregation: Count Distinct
Color: inventory_pressure_band
Sort: Low count descending if Zoho allows
```

Filters:

```text
Outlet -> outlet_name
Inventory Category -> category_name
Inventory Item -> item_name
Stock Pressure Band -> inventory_pressure_band
```

Why useful:

```text
Gives a category-level replenishment view.
```

Caveat:

```text
Pressure is based on generic thresholds, not item-specific reorder points.
```

### 5.3 Low-Stock Value Exposure

Business question:

```text
Among low-stock items, which ones still carry meaningful stock value?
```

Source:

```text
SUM_Inventory_Risk
```

Chart:

```text
Type: Horizontal bar
X-axis: item_name
Y-axis: total_amt
Y aggregation: Sum
Criteria: low_stock_flag = 1
Color: category_name
Sort: SUM(total_amt) descending
```

Filters:

```text
Outlet -> outlet_name
Inventory Category -> category_name
Inventory Item -> item_name
Stock Pressure Band -> inventory_pressure_band
```

Why useful:

```text
Some low-stock items may be low quantity but high value. This helps prioritize review.
```

Caveat:

```text
Does not show expiry or lead time.
```

### 5.4 Inventory Value Trend By Category

Business question:

```text
How does inventory value move over time by category?
```

Source:

```text
FACT_Inventory_Closing
```

Chart:

```text
Type: Line or stacked area
X-axis: inventory_date
Y-axis: total_amt
Y aggregation: Sum
Color: category_name
```

Filters:

```text
Outlet -> outlet_name
Inventory Date Range -> inventory_date
Inventory Category -> category_name
Inventory Item -> item_name
```

Why useful:

```text
This is the correct use of FACT_Inventory_Closing because the X-axis is date.
```

Caveat:

```text
Do not use this source to create a category-only current inventory value chart.
```

### 5.5 Theoretical Ingredient Demand By Menu Category

Business question:

```text
Which menu categories are driving ingredient demand?
```

Source:

```text
FACT_Theoretical_Consumption
```

Chart:

```text
Type: Stacked bar
X-axis: category
Y-axis: theoretical_ingredient_qty
Y aggregation: Sum
Color: ingredient_name or ingredient_unit
Criteria: demand_component_type = 'Recipe Ingredient'
```

Filters:

```text
Outlet -> outlet_name
Sales Date Range -> sales_date
Demand Component Type -> demand_component_type
Demand Ingredient -> ingredient_name
Menu Category -> category
Menu Item -> menu_item_name
```

Why useful:

```text
Connects menu demand to material demand without claiming actual consumption.
```

Caveat:

```text
Ingredient units differ, so avoid summing across incompatible units unless the chart is filtered to one ingredient/unit family.
```

## 6. Dashboard 5: Calendar, Event, And Competitor Intelligence

Current dashboard explains event lift and competitor context. Add visuals that show confidence, category scope, and premium sales context.

### 6.1 Event Lift Ranking

Business question:

```text
Which configured events had the highest directional sales lift?
```

Source:

```text
SUM_Event_Impact
```

Chart:

```text
Type: Horizontal bar
X-axis: event_name
Y-axis: sales_lift_pct
Y aggregation: Average
Color: confidence_level
Sort: AVG(sales_lift_pct) descending
```

Filters:

```text
Outlet -> outlet_name
Event Type -> event_type
Event Date Range -> start_date or event date table if available
Menu Category -> category
Menu Item -> item_name
```

Why useful:

```text
Quickly identifies the event story worth discussing.
```

Caveat:

```text
Lift is directional baseline math, not causal proof.
```

### 6.2 Event Sales vs Baseline

Business question:

```text
Was event-day sales above or below baseline in rupees?
```

Source:

```text
SUM_Event_Impact
```

Chart:

```text
Type: Combo or grouped bar
X-axis: event_name
Y-axis 1: event_day_sales
Y-axis 2: baseline_sales
Aggregation: Sum or Average depending on grain
Color/group: outlet_name
```

Filters:

```text
Outlet -> outlet_name
Event Type -> event_type
Menu Category -> category
Menu Item -> item_name
```

Why useful:

```text
Shows the actual value behind a lift percentage.
```

Caveat:

```text
Baseline is synthetic and method-dependent.
```

### 6.3 Competitor Price Position By Category

Business question:

```text
Where is ABNAH premium, discounted, or at parity versus competitors?
```

Source:

```text
SUM_Competitor_Positioning
```

Chart:

```text
Type: Stacked bar
X-axis: competitor_category
Y-axis: mapped_abnah_item_count
Y aggregation: Sum
Color: price_position_band
```

Filters:

```text
Outlet -> outlet_name
Market Area -> market_area or outlet_market_area
Competitor -> competitor_name
Competitor Category -> competitor_category
Price Position -> price_position_band
```

Why useful:

```text
Shows price positioning breadth, not just one average index.
```

Caveat:

```text
Competitor item comparability is synthetic and category-level.
```

### 6.4 Premium Context Sales

Business question:

```text
Do premium-positioned ABNAH items still generate sales?
```

Source:

```text
FACT_Competitor_Price_Position
```

Chart:

```text
Type: Horizontal bar
X-axis: abnah_item_name
Y-axis: net_sale
Y aggregation: Sum
Color: price_position_band
Criteria: price_position_band = Premium if desired
Sort: SUM(net_sale) descending
Top N: 10
```

Filters:

```text
Outlet -> outlet_name
Market Area -> market_area / outlet_market_area
Competitor Category -> competitor_category
Price Position -> price_position_band
Sales Date Range -> sales_date
```

Why useful:

```text
Shows where ABNAH can sustain premium pricing in the demo context.
```

Caveat:

```text
Does not prove price elasticity or customer preference.
```

### 6.5 Competitor Price Index vs Sales Scatter

Business question:

```text
Are higher-index items still selling?
```

Source:

```text
FACT_Competitor_Price_Position
```

Chart:

```text
Type: Scatter
X-axis: price_index
X aggregation: Average
Y-axis: net_sale
Y aggregation: Sum
Color: category
Tooltip: abnah_item_name, competitor_name, price_position_band
```

Filters:

```text
Outlet -> outlet_name
Sales Date Range -> sales_date
Competitor Category -> competitor_category
Price Position -> price_position_band
```

Why useful:

```text
Gives a pricing-context discussion without claiming causation.
```

Caveat:

```text
Do not present as price elasticity. It is context only.
```

## 7. Charts To Avoid For Now

Do not build these unless the raw data model is expanded.

| Avoided chart | Why to avoid | Required future data |
|---|---|---|
| Profit by menu item | No actual COGS/margin | Recipe costing, purchase cost by batch, wastage |
| Basket/attachment analysis | Sales data is daily item aggregate, not bill-line data | Bill ID / order ID |
| Customer repeat behavior | No customer identifier | Customer ID / loyalty ID |
| Vendor delay scorecard | Receipts do not carry PO number and no delivery timestamp | PO-GRN matching, delivery timestamp |
| Stockout forecast | No reorder levels or lead times | Min/max stock, vendor lead time, actual consumption |
| Campaign ROI | No campaign cost | Campaign spend, impressions, redemptions |
| Labor productivity | No staff/labor hours | Staff schedule and labor cost |
| Food waste loss | No wastage/expiry data | Wastage logs, expiry, disposal records |

## 8. Priority Build Order

If time is limited, build in this order.

### High Priority

1. `Revenue vs Quantity Menu Quadrant`
2. `PO vs Receipt Gap By Vendor`
3. `Stock Pressure By Category`
4. `Event Sales vs Baseline`
5. `Competitor Price Position By Category`

### Medium Priority

1. `Outlet Operating Balance Matrix`
2. `Category Trend Stacked Area`
3. `Vendor Material Concentration Matrix`
4. `Inventory Value Trend By Category`
5. `Premium Context Sales`

### Optional

1. `Day-Of-Week Sales Heatmap`
2. `Receipt Booking Trend`
3. `Low-Stock Value Exposure`
4. `Competitor Price Index vs Sales Scatter`

## 9. Final Dashboard Design Rule

Use extra charts only when they improve the story:

```text
Executive dashboard -> explain outlet health.
Sales/Menu dashboard -> explain revenue, volume, and price realization.
Vendor dashboard -> explain PO value, receipt value, and follow-up pressure.
Inventory dashboard -> separate current stock from theoretical demand.
Event/Competitor dashboard -> explain context without claiming causality.
```

If a chart cannot be explained in one business sentence, do not add it.
