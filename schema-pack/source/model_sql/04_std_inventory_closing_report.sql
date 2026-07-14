-- Query Table: STD_Inventory_Closing_Report
-- Purpose: Union outlet-specific RAW inventory feeds into standardized daily outlet-item closing inventory rows.
-- Sources: RAW_Inventory_Closing_Report_OUT001, RAW_Inventory_Closing_Report_OUT002, RAW_Inventory_Closing_Report_OUT003
-- Caveat: Low stock logic in later tables is heuristic, not prediction.

SELECT DISTINCT
    src."row_id" AS "inventory_row_id",
    src."deployment" AS "outlet_name",
    CASE
        WHEN src."deployment" = 'ABNAH Cafe Connaught Place' THEN 'OUT001'
        WHEN src."deployment" = 'ABNAH Cafe Hauz Khas' THEN 'OUT002'
        WHEN src."deployment" = 'ABNAH Cafe Saket Premium' THEN 'OUT003'
        ELSE NULL
    END AS "outlet_code",
    CASE
        WHEN src."deployment" = 'ABNAH Cafe Connaught Place' THEN 'Connaught Place'
        WHEN src."deployment" = 'ABNAH Cafe Hauz Khas' THEN 'Hauz Khas'
        WHEN src."deployment" = 'ABNAH Cafe Saket Premium' THEN 'Saket'
        ELSE NULL
    END AS "market_area",
    CAST(src."date" AS DATE) AS "inventory_date",
    CAST(src."generation_date" AS DATE) AS "generation_date",
    src."generation_time" AS "generation_time",
    src."item_code" AS "item_code",
    src."item_name" AS "item_name",
    src."super_category_code" AS "super_category_code",
    src."super_category_name" AS "super_category_name",
    src."category_code" AS "category_code",
    src."category_name" AS "category_name",
    src."unit_name" AS "unit_name",
    CAST(src."average_price" AS DECIMAL(14,2)) AS "average_price",
    CAST(src."store_stock_qty" AS DECIMAL(14,4)) AS "store_stock_qty",
    CAST(src."total_qty" AS DECIMAL(14,4)) AS "total_qty",
    CAST(src."total_amt" AS DECIMAL(14,2)) AS "total_amt"
FROM (
    SELECT
        r1."row_id" AS "row_id",
        r1."deployment" AS "deployment",
        r1."date" AS "date",
        r1."generation_date" AS "generation_date",
        r1."generation_time" AS "generation_time",
        r1."item_code" AS "item_code",
        r1."item_name" AS "item_name",
        r1."super_category_code" AS "super_category_code",
        r1."super_category_name" AS "super_category_name",
        r1."category_code" AS "category_code",
        r1."category_name" AS "category_name",
        r1."unit_name" AS "unit_name",
        r1."average_price" AS "average_price",
        r1."store_stock_qty" AS "store_stock_qty",
        r1."total_qty" AS "total_qty",
        r1."total_amt" AS "total_amt"
    FROM "RAW_Inventory_Closing_Report_OUT001" r1
    UNION ALL
    SELECT
        r2."row_id" AS "row_id",
        r2."deployment" AS "deployment",
        r2."date" AS "date",
        r2."generation_date" AS "generation_date",
        r2."generation_time" AS "generation_time",
        r2."item_code" AS "item_code",
        r2."item_name" AS "item_name",
        r2."super_category_code" AS "super_category_code",
        r2."super_category_name" AS "super_category_name",
        r2."category_code" AS "category_code",
        r2."category_name" AS "category_name",
        r2."unit_name" AS "unit_name",
        r2."average_price" AS "average_price",
        r2."store_stock_qty" AS "store_stock_qty",
        r2."total_qty" AS "total_qty",
        r2."total_amt" AS "total_amt"
    FROM "RAW_Inventory_Closing_Report_OUT002" r2
    UNION ALL
    SELECT
        r3."row_id" AS "row_id",
        r3."deployment" AS "deployment",
        r3."date" AS "date",
        r3."generation_date" AS "generation_date",
        r3."generation_time" AS "generation_time",
        r3."item_code" AS "item_code",
        r3."item_name" AS "item_name",
        r3."super_category_code" AS "super_category_code",
        r3."super_category_name" AS "super_category_name",
        r3."category_code" AS "category_code",
        r3."category_name" AS "category_name",
        r3."unit_name" AS "unit_name",
        r3."average_price" AS "average_price",
        r3."store_stock_qty" AS "store_stock_qty",
        r3."total_qty" AS "total_qty",
        r3."total_amt" AS "total_amt"
    FROM "RAW_Inventory_Closing_Report_OUT003" r3
) src;
