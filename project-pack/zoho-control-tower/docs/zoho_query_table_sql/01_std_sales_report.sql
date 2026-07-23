-- Query Table: STD_Sales_Report
-- Purpose: Union outlet-specific RAW sales feeds into a stable daily outlet-item sales grain.
-- Sources: RAW_Sales_Report_OUT001, RAW_Sales_Report_OUT002, RAW_Sales_Report_OUT003
-- Needs Zoho syntax validation: CAST behavior may vary if Zoho already imports dates/numbers correctly.

SELECT DISTINCT
    src."row_id" AS "sales_row_id",
    src."outlet_name" AS "outlet_name",
    CASE
        WHEN src."outlet_name" = 'ABNAH Cafe Connaught Place' THEN 'OUT001'
        WHEN src."outlet_name" = 'ABNAH Cafe Hauz Khas' THEN 'OUT002'
        WHEN src."outlet_name" = 'ABNAH Cafe Saket Premium' THEN 'OUT003'
        ELSE NULL
    END AS "outlet_code",
    CASE
        WHEN src."outlet_name" = 'ABNAH Cafe Connaught Place' THEN 'Connaught Place'
        WHEN src."outlet_name" = 'ABNAH Cafe Hauz Khas' THEN 'Hauz Khas'
        WHEN src."outlet_name" = 'ABNAH Cafe Saket Premium' THEN 'Saket'
        ELSE NULL
    END AS "market_area",
    CAST(src."date" AS DATE) AS "sales_date",
    src."super_category" AS "super_category",
    src."category" AS "category",
    src."item_number" AS "item_number",
    src."item_name" AS "item_name",
    CAST(src."qty" AS DECIMAL(12,4)) AS "qty",
    CAST(src."net_sale" AS DECIMAL(14,2)) AS "net_sale",
    CASE
        WHEN CAST(src."qty" AS DECIMAL(12,4)) <> 0
        THEN CAST(src."net_sale" AS DECIMAL(14,2)) / CAST(src."qty" AS DECIMAL(12,4))
        ELSE NULL
    END AS "net_sale_per_qty"
FROM (
    SELECT
        r1."row_id" AS "row_id",
        r1."outlet_name" AS "outlet_name",
        r1."date" AS "date",
        r1."super_category" AS "super_category",
        r1."category" AS "category",
        r1."item_number" AS "item_number",
        r1."item_name" AS "item_name",
        r1."qty" AS "qty",
        r1."net_sale" AS "net_sale"
    FROM "RAW_Sales_Report_OUT001" r1
    UNION ALL
    SELECT
        r2."row_id" AS "row_id",
        r2."outlet_name" AS "outlet_name",
        r2."date" AS "date",
        r2."super_category" AS "super_category",
        r2."category" AS "category",
        r2."item_number" AS "item_number",
        r2."item_name" AS "item_name",
        r2."qty" AS "qty",
        r2."net_sale" AS "net_sale"
    FROM "RAW_Sales_Report_OUT002" r2
    UNION ALL
    SELECT
        r3."row_id" AS "row_id",
        r3."outlet_name" AS "outlet_name",
        r3."date" AS "date",
        r3."super_category" AS "super_category",
        r3."category" AS "category",
        r3."item_number" AS "item_number",
        r3."item_name" AS "item_name",
        r3."qty" AS "qty",
        r3."net_sale" AS "net_sale"
    FROM "RAW_Sales_Report_OUT003" r3
) src;
