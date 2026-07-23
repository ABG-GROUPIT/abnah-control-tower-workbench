-- Query Table: SUM_Executive_KPIs
-- Purpose: Metric-name/value table for executive KPI widgets.
-- Sources: FACT_Sales, FACT_Vendor_Spend, FACT_Inventory_Closing, DIM_Outlet, DIM_Event
-- Supplemental file: requested dashboard layer includes SUM_Executive_KPIs, but the requested numbered file list omitted it.

SELECT 'Sales' AS "metric_group", 'Total Net Sales' AS "metric_name", SUM(s."net_sale") AS "metric_value"
FROM "FACT_Sales" s

UNION ALL

SELECT 'Sales' AS "metric_group", 'Total Quantity Sold' AS "metric_name", SUM(s2."qty") AS "metric_value"
FROM "FACT_Sales" s2

UNION ALL

SELECT 'Outlets' AS "metric_group", 'Active Outlets' AS "metric_name", COUNT(*) AS "metric_value"
FROM "DIM_Outlet" o

UNION ALL

SELECT 'Procurement' AS "metric_group", 'Total Ordered Value' AS "metric_name", SUM(vs."ordered_value") AS "metric_value"
FROM "FACT_Vendor_Spend" vs

UNION ALL

SELECT 'Procurement' AS "metric_group", 'Total Received Value' AS "metric_name", SUM(vs2."received_value") AS "metric_value"
FROM "FACT_Vendor_Spend" vs2

UNION ALL

SELECT 'Inventory' AS "metric_group", 'Low Stock Item Days' AS "metric_name", SUM(inv."low_stock_flag") AS "metric_value"
FROM "FACT_Inventory_Closing" inv

UNION ALL

SELECT 'Calendar' AS "metric_group", 'Manual Events' AS "metric_name", COUNT(*) AS "metric_value"
FROM "DIM_Event" e;
