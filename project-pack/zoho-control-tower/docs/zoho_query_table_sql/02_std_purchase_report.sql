-- Query Table: STD_Purchase_Report
-- Purpose: Union outlet-specific RAW purchase feeds into standardized purchase order line rows.
-- Sources: RAW_Purchase_Report_OUT001, RAW_Purchase_Report_OUT002, RAW_Purchase_Report_OUT003
-- Join keys downstream: po_number, outlet_name, vendor_name, item_code, po_date.
-- Needs Zoho syntax validation: CAST behavior may vary if Zoho already imports dates/numbers correctly.

SELECT DISTINCT
    src."row_id" AS "purchase_row_id",
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
    src."store_name" AS "store_name",
    src."vendor_name" AS "vendor_name",
    src."po_number" AS "po_number",
    CAST(src."po_date" AS DATE) AS "po_date",
    CAST(src."expected_delivery" AS DATE) AS "expected_delivery_date",
    src."po_status" AS "po_status",
    src."item_code" AS "item_code",
    src."item_name" AS "item_name",
    src."category_name" AS "category_name",
    src."super_category_name" AS "super_category_name",
    CAST(src."total_processed_qty" AS DECIMAL(14,4)) AS "processed_qty",
    CAST(src."remaining_balance_qty" AS DECIMAL(14,4)) AS "remaining_qty",
    CAST(src."quantity" AS DECIMAL(14,4)) AS "ordered_qty",
    src."unit" AS "unit",
    CAST(src."unit_price" AS DECIMAL(14,2)) AS "unit_price",
    CAST(src."subtotal" AS DECIMAL(14,2)) AS "subtotal",
    CAST(src."tax" AS DECIMAL(14,2)) AS "tax",
    CAST(src."total_item_cost" AS DECIMAL(14,2)) AS "total_item_cost",
    CASE
        WHEN src."po_status" IN ('Pending', 'Partially Received') THEN 1
        WHEN CAST(src."remaining_balance_qty" AS DECIMAL(14,4)) > 0 THEN 1
        ELSE 0
    END AS "is_open_or_partial"
FROM (
    SELECT
        r1."row_id" AS "row_id",
        r1."deployment" AS "deployment",
        r1."store_name" AS "store_name",
        r1."vendor_name" AS "vendor_name",
        r1."po_number" AS "po_number",
        r1."po_date" AS "po_date",
        r1."expected_delivery" AS "expected_delivery",
        r1."po_status" AS "po_status",
        r1."item_code" AS "item_code",
        r1."item_name" AS "item_name",
        r1."category_name" AS "category_name",
        r1."super_category_name" AS "super_category_name",
        r1."total_processed_qty" AS "total_processed_qty",
        r1."remaining_balance_qty" AS "remaining_balance_qty",
        r1."quantity" AS "quantity",
        r1."unit" AS "unit",
        r1."unit_price" AS "unit_price",
        r1."subtotal" AS "subtotal",
        r1."tax" AS "tax",
        r1."total_item_cost" AS "total_item_cost"
    FROM "RAW_Purchase_Report_OUT001" r1
    UNION ALL
    SELECT
        r2."row_id" AS "row_id",
        r2."deployment" AS "deployment",
        r2."store_name" AS "store_name",
        r2."vendor_name" AS "vendor_name",
        r2."po_number" AS "po_number",
        r2."po_date" AS "po_date",
        r2."expected_delivery" AS "expected_delivery",
        r2."po_status" AS "po_status",
        r2."item_code" AS "item_code",
        r2."item_name" AS "item_name",
        r2."category_name" AS "category_name",
        r2."super_category_name" AS "super_category_name",
        r2."total_processed_qty" AS "total_processed_qty",
        r2."remaining_balance_qty" AS "remaining_balance_qty",
        r2."quantity" AS "quantity",
        r2."unit" AS "unit",
        r2."unit_price" AS "unit_price",
        r2."subtotal" AS "subtotal",
        r2."tax" AS "tax",
        r2."total_item_cost" AS "total_item_cost"
    FROM "RAW_Purchase_Report_OUT002" r2
    UNION ALL
    SELECT
        r3."row_id" AS "row_id",
        r3."deployment" AS "deployment",
        r3."store_name" AS "store_name",
        r3."vendor_name" AS "vendor_name",
        r3."po_number" AS "po_number",
        r3."po_date" AS "po_date",
        r3."expected_delivery" AS "expected_delivery",
        r3."po_status" AS "po_status",
        r3."item_code" AS "item_code",
        r3."item_name" AS "item_name",
        r3."category_name" AS "category_name",
        r3."super_category_name" AS "super_category_name",
        r3."total_processed_qty" AS "total_processed_qty",
        r3."remaining_balance_qty" AS "remaining_balance_qty",
        r3."quantity" AS "quantity",
        r3."unit" AS "unit",
        r3."unit_price" AS "unit_price",
        r3."subtotal" AS "subtotal",
        r3."tax" AS "tax",
        r3."total_item_cost" AS "total_item_cost"
    FROM "RAW_Purchase_Report_OUT003" r3
) src;
