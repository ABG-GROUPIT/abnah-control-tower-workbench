-- Query Table: SUM_Outlet_Health
-- Purpose: Outlet-level health summary.
-- Source: FACT_Outlet_Daily_Health
-- Supplemental file: requested dashboard layer includes SUM_Outlet_Health, but the requested numbered file list omitted it.

SELECT
    h."outlet_code" AS "outlet_code",
    h."outlet_name" AS "outlet_name",
    h."market_area" AS "market_area",
    SUM(h."net_sales") AS "total_net_sales",
    AVG(h."net_sales") AS "avg_daily_net_sales",
    SUM(h."sold_qty") AS "total_sold_qty",
    SUM(h."po_value") AS "total_po_value",
    SUM(h."receipt_value") AS "total_receipt_value",
    AVG(h."inventory_value") AS "avg_inventory_value",
    SUM(h."low_stock_item_count") AS "low_stock_item_days",
    SUM(h."event_count") AS "event_day_markers",
    CASE
        WHEN SUM(h."low_stock_item_count") >= 20 THEN 'Pressure'
        WHEN SUM(h."event_count") >= 5 THEN 'Event-sensitive'
        ELSE 'Stable'
    END AS "outlet_health_band"
FROM "FACT_Outlet_Daily_Health" h
GROUP BY
    h."outlet_code",
    h."market_area",
    h."outlet_name";
