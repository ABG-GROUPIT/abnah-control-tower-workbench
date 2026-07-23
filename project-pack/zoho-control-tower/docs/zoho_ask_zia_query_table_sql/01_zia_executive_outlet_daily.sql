-- Query Table: ZIA_Executive_Outlet_Daily
-- Purpose: Ask Zia-safe daily outlet scorecard.
-- Source: FACT_Outlet_Daily_Health.
-- Grain: one row per outlet per business_date.
-- Use for: daily outlet sales, PO value, receipt value, inventory pressure, executive health.

SELECT
    h."activity_date" AS "business_date",
    YEAR(h."activity_date") AS "year_number",
    MONTH(h."activity_date") AS "month_number",
    CONCAT(YEAR(h."activity_date"), '-', LPAD(MONTH(h."activity_date"), 2, '0')) AS "month_key",
    DAYOFWEEK(h."activity_date") AS "day_of_week_number",
    CASE DAYOFWEEK(h."activity_date")
        WHEN 2 THEN 1
        WHEN 3 THEN 2
        WHEN 4 THEN 3
        WHEN 5 THEN 4
        WHEN 6 THEN 5
        WHEN 7 THEN 6
        WHEN 1 THEN 7
    END AS "day_of_week_sort",
    CASE DAYOFWEEK(h."activity_date")
        WHEN 1 THEN 'Sunday'
        WHEN 2 THEN 'Monday'
        WHEN 3 THEN 'Tuesday'
        WHEN 4 THEN 'Wednesday'
        WHEN 5 THEN 'Thursday'
        WHEN 6 THEN 'Friday'
        WHEN 7 THEN 'Saturday'
    END AS "day_of_week_name",
    h."outlet_code" AS "outlet_code",
    h."outlet_name" AS "outlet_name",
    h."market_area" AS "market_area",
    h."net_sales" AS "net_sales",
    h."sold_qty" AS "menu_units_sold",
    h."sales_line_count" AS "sales_line_count",
    h."po_value" AS "po_raised_value",
    h."receipt_value" AS "receipt_booked_value",
    h."po_value" - h."receipt_value" AS "po_receipt_gap_value",
    h."open_or_partial_po_count" AS "open_or_partial_po_count",
    h."inventory_value" AS "daily_inventory_value",
    h."low_stock_item_count" AS "low_stock_item_day_count",
    h."event_count" AS "event_marker_count",
    CASE
        WHEN h."net_sales" <> 0 THEN h."po_value" * 100 / h."net_sales"
        ELSE NULL
    END AS "daily_purchase_to_sales_pct",
    CASE
        WHEN h."inventory_value" <> 0 THEN h."net_sales" / h."inventory_value"
        ELSE NULL
    END AS "daily_revenue_per_inventory_rupee",
    h."health_note" AS "outlet_health_note"
FROM "FACT_Outlet_Daily_Health" h;
