-- Diagnostic Query Table: CHECK_Sales_By_Outlet
-- Purpose: Validate outlet-level sales totals after each Zoho layer is refreshed.
-- Expected Month 1 outlet totals:
-- ABNAH Cafe Connaught Place: net_sale 626349.57, qty 2432
-- ABNAH Cafe Hauz Khas:       net_sale 626542.86, qty 2440
-- ABNAH Cafe Saket Premium:   net_sale 692296.57, qty 2652

SELECT
    'STD_Sales_Report' AS "source_layer",
    s."outlet_name" AS "outlet_name",
    COUNT(s."sales_row_id") AS "row_count",
    SUM(s."net_sale") AS "net_sale",
    SUM(s."qty") AS "qty"
FROM "STD_Sales_Report" s
GROUP BY s."outlet_name"

UNION ALL

SELECT
    'FACT_Sales' AS "source_layer",
    f."outlet_name" AS "outlet_name",
    COUNT(f."sales_row_id") AS "row_count",
    SUM(f."net_sale") AS "net_sale",
    SUM(f."qty") AS "qty"
FROM "FACT_Sales" f
GROUP BY f."outlet_name"

UNION ALL

SELECT
    'SUM_Menu_Item_Performance' AS "source_layer",
    m."outlet_name" AS "outlet_name",
    COUNT(m."item_number") AS "row_count",
    SUM(m."total_net_sale") AS "net_sale",
    SUM(m."total_qty") AS "qty"
FROM "SUM_Menu_Item_Performance" m
GROUP BY m."outlet_name";
