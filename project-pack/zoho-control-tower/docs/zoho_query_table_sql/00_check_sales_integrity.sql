-- Diagnostic Query Table: CHECK_Sales_Integrity
-- Purpose: Confirm where sales totals change in Zoho after RAW import.
-- Expected Month 1 totals when only Month 1 is loaded:
-- RAW OUT001: rows 1529, net_sale 626349.57, qty 2432
-- RAW OUT002: rows 1595, net_sale 626542.86, qty 2440
-- RAW OUT003: rows 1731, net_sale 692296.57, qty 2652
-- RAW total / STD total / FACT total: rows 4855, net_sale 1945189.00, qty 7524

SELECT
    '01_RAW_OUT001' AS "check_name",
    COUNT(r1."row_id") AS "row_count",
    SUM(CAST(r1."net_sale" AS DECIMAL(14,2))) AS "net_sale",
    SUM(CAST(r1."qty" AS DECIMAL(14,4))) AS "qty"
FROM "RAW_Sales_Report_OUT001" r1

UNION ALL

SELECT
    '02_RAW_OUT002' AS "check_name",
    COUNT(r2."row_id") AS "row_count",
    SUM(CAST(r2."net_sale" AS DECIMAL(14,2))) AS "net_sale",
    SUM(CAST(r2."qty" AS DECIMAL(14,4))) AS "qty"
FROM "RAW_Sales_Report_OUT002" r2

UNION ALL

SELECT
    '03_RAW_OUT003' AS "check_name",
    COUNT(r3."row_id") AS "row_count",
    SUM(CAST(r3."net_sale" AS DECIMAL(14,2))) AS "net_sale",
    SUM(CAST(r3."qty" AS DECIMAL(14,4))) AS "qty"
FROM "RAW_Sales_Report_OUT003" r3

UNION ALL

SELECT
    '04_STD_Sales_Report' AS "check_name",
    COUNT(s."sales_row_id") AS "row_count",
    SUM(s."net_sale") AS "net_sale",
    SUM(s."qty") AS "qty"
FROM "STD_Sales_Report" s

UNION ALL

SELECT
    '05_FACT_Sales' AS "check_name",
    COUNT(f."sales_row_id") AS "row_count",
    SUM(f."net_sale") AS "net_sale",
    SUM(f."qty") AS "qty"
FROM "FACT_Sales" f

UNION ALL

SELECT
    '06_SUM_Menu_Item_Performance' AS "check_name",
    COUNT(m."item_number") AS "row_count",
    SUM(m."total_net_sale") AS "net_sale",
    SUM(m."total_qty") AS "qty"
FROM "SUM_Menu_Item_Performance" m;
