-- Query Table: ZIA_Current_Inventory_Snapshot
-- Purpose: Ask Zia-safe current inventory table.
-- Sources: RAW_Inventory_Closing_Report_OUT001, RAW_Inventory_Closing_Report_OUT002, RAW_Inventory_Closing_Report_OUT003.
-- Grain: one row per outlet and inventory material at latest stock date in each outlet feed.
-- Use for: current inventory value, current low stock, watch material questions.
-- Why raw source: avoids Zoho's query-over-query depth limit from SUM_Inventory_Risk.

SELECT DISTINCT
    CAST(r1."date" AS DATE) AS "stock_snapshot_date",
    YEAR(CAST(r1."date" AS DATE)) AS "year_number",
    MONTH(CAST(r1."date" AS DATE)) AS "month_number",
    CONCAT(YEAR(CAST(r1."date" AS DATE)), '-', LPAD(MONTH(CAST(r1."date" AS DATE)), 2, '0')) AS "month_key",
    'OUT001' AS "outlet_code",
    r1."deployment" AS "outlet_name",
    'Connaught Place' AS "market_area",
    r1."item_code" AS "material_code",
    r1."item_name" AS "material_name",
    r1."category_name" AS "material_category",
    r1."super_category_name" AS "material_super_category",
    r1."unit_name" AS "unit_name",
    CAST(r1."total_qty" AS DECIMAL(14,4)) AS "current_stock_qty",
    CAST(r1."total_amt" AS DECIMAL(14,2)) AS "current_inventory_value",
    CASE
        WHEN CAST(r1."total_qty" AS DECIMAL(14,4)) <= 10 THEN 1
        ELSE 0
    END AS "low_stock_flag",
    CASE
        WHEN CAST(r1."total_qty" AS DECIMAL(14,4)) <= 25 THEN 1
        ELSE 0
    END AS "watch_material_flag",
    CASE
        WHEN CAST(r1."total_qty" AS DECIMAL(14,4)) <= 10 THEN 'Low'
        WHEN CAST(r1."total_qty" AS DECIMAL(14,4)) <= 25 THEN 'Watch'
        ELSE 'OK'
    END AS "inventory_pressure_band",
    CASE
        WHEN CAST(r1."total_qty" AS DECIMAL(14,4)) <= 10 THEN 'Review stock'
        ELSE 'OK'
    END AS "inventory_risk_note"
FROM "RAW_Inventory_Closing_Report_OUT001" r1
WHERE CAST(r1."date" AS DATE) = (
    SELECT MAX(CAST(r1_latest."date" AS DATE))
    FROM "RAW_Inventory_Closing_Report_OUT001" r1_latest
)

UNION ALL

SELECT DISTINCT
    CAST(r2."date" AS DATE) AS "stock_snapshot_date",
    YEAR(CAST(r2."date" AS DATE)) AS "year_number",
    MONTH(CAST(r2."date" AS DATE)) AS "month_number",
    CONCAT(YEAR(CAST(r2."date" AS DATE)), '-', LPAD(MONTH(CAST(r2."date" AS DATE)), 2, '0')) AS "month_key",
    'OUT002' AS "outlet_code",
    r2."deployment" AS "outlet_name",
    'Hauz Khas' AS "market_area",
    r2."item_code" AS "material_code",
    r2."item_name" AS "material_name",
    r2."category_name" AS "material_category",
    r2."super_category_name" AS "material_super_category",
    r2."unit_name" AS "unit_name",
    CAST(r2."total_qty" AS DECIMAL(14,4)) AS "current_stock_qty",
    CAST(r2."total_amt" AS DECIMAL(14,2)) AS "current_inventory_value",
    CASE
        WHEN CAST(r2."total_qty" AS DECIMAL(14,4)) <= 10 THEN 1
        ELSE 0
    END AS "low_stock_flag",
    CASE
        WHEN CAST(r2."total_qty" AS DECIMAL(14,4)) <= 25 THEN 1
        ELSE 0
    END AS "watch_material_flag",
    CASE
        WHEN CAST(r2."total_qty" AS DECIMAL(14,4)) <= 10 THEN 'Low'
        WHEN CAST(r2."total_qty" AS DECIMAL(14,4)) <= 25 THEN 'Watch'
        ELSE 'OK'
    END AS "inventory_pressure_band",
    CASE
        WHEN CAST(r2."total_qty" AS DECIMAL(14,4)) <= 10 THEN 'Review stock'
        ELSE 'OK'
    END AS "inventory_risk_note"
FROM "RAW_Inventory_Closing_Report_OUT002" r2
WHERE CAST(r2."date" AS DATE) = (
    SELECT MAX(CAST(r2_latest."date" AS DATE))
    FROM "RAW_Inventory_Closing_Report_OUT002" r2_latest
)

UNION ALL

SELECT DISTINCT
    CAST(r3."date" AS DATE) AS "stock_snapshot_date",
    YEAR(CAST(r3."date" AS DATE)) AS "year_number",
    MONTH(CAST(r3."date" AS DATE)) AS "month_number",
    CONCAT(YEAR(CAST(r3."date" AS DATE)), '-', LPAD(MONTH(CAST(r3."date" AS DATE)), 2, '0')) AS "month_key",
    'OUT003' AS "outlet_code",
    r3."deployment" AS "outlet_name",
    'Saket' AS "market_area",
    r3."item_code" AS "material_code",
    r3."item_name" AS "material_name",
    r3."category_name" AS "material_category",
    r3."super_category_name" AS "material_super_category",
    r3."unit_name" AS "unit_name",
    CAST(r3."total_qty" AS DECIMAL(14,4)) AS "current_stock_qty",
    CAST(r3."total_amt" AS DECIMAL(14,2)) AS "current_inventory_value",
    CASE
        WHEN CAST(r3."total_qty" AS DECIMAL(14,4)) <= 10 THEN 1
        ELSE 0
    END AS "low_stock_flag",
    CASE
        WHEN CAST(r3."total_qty" AS DECIMAL(14,4)) <= 25 THEN 1
        ELSE 0
    END AS "watch_material_flag",
    CASE
        WHEN CAST(r3."total_qty" AS DECIMAL(14,4)) <= 10 THEN 'Low'
        WHEN CAST(r3."total_qty" AS DECIMAL(14,4)) <= 25 THEN 'Watch'
        ELSE 'OK'
    END AS "inventory_pressure_band",
    CASE
        WHEN CAST(r3."total_qty" AS DECIMAL(14,4)) <= 10 THEN 'Review stock'
        ELSE 'OK'
    END AS "inventory_risk_note"
FROM "RAW_Inventory_Closing_Report_OUT003" r3
WHERE CAST(r3."date" AS DATE) = (
    SELECT MAX(CAST(r3_latest."date" AS DATE))
    FROM "RAW_Inventory_Closing_Report_OUT003" r3_latest
);
