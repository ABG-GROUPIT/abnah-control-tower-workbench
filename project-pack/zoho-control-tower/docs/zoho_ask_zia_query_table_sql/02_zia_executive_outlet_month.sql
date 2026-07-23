-- Query Table: ZIA_Executive_Outlet_Month
-- Purpose: Ask Zia-safe monthly outlet scorecard.
-- Source: FACT_Outlet_Daily_Health.
-- Grain: one row per outlet per month.
-- Use for: "show net sales by outlet for January 2026" and executive monthly totals.

SELECT
    YEAR(h."activity_date") AS "year_number",
    MONTH(h."activity_date") AS "month_number",
    CONCAT(YEAR(h."activity_date"), '-', LPAD(MONTH(h."activity_date"), 2, '0')) AS "month_key",
    MIN(h."activity_date") AS "month_start_date",
    MAX(h."activity_date") AS "month_end_date",
    h."outlet_code" AS "outlet_code",
    h."outlet_name" AS "outlet_name",
    h."market_area" AS "market_area",
    COUNT(DISTINCT h."activity_date") AS "active_business_days",
    SUM(h."net_sales") AS "net_sales",
    SUM(h."sold_qty") AS "menu_units_sold",
    SUM(h."po_value") AS "po_raised_value",
    SUM(h."receipt_value") AS "receipt_booked_value",
    SUM(h."po_value") - SUM(h."receipt_value") AS "po_receipt_gap_value",
    SUM(h."open_or_partial_po_count") AS "open_or_partial_po_count",
    SUM(h."low_stock_item_count") AS "inventory_pressure_item_days",
    AVG(h."inventory_value") AS "average_daily_inventory_value",
    CASE
        WHEN COUNT(DISTINCT h."activity_date") <> 0
        THEN SUM(h."net_sales") / COUNT(DISTINCT h."activity_date")
        ELSE NULL
    END AS "average_daily_net_sales",
    CASE
        WHEN SUM(h."net_sales") <> 0 THEN SUM(h."po_value") * 100 / SUM(h."net_sales")
        ELSE NULL
    END AS "purchase_to_sales_pct",
    CASE
        WHEN SUM(h."inventory_value") <> 0
        THEN SUM(h."net_sales") * COUNT(DISTINCT h."activity_date") / SUM(h."inventory_value")
        ELSE NULL
    END AS "revenue_per_average_inventory_rupee"
FROM "FACT_Outlet_Daily_Health" h
GROUP BY
    YEAR(h."activity_date"),
    MONTH(h."activity_date"),
    CONCAT(YEAR(h."activity_date"), '-', LPAD(MONTH(h."activity_date"), 2, '0')),
    h."outlet_code",
    h."outlet_name",
    h."market_area";
