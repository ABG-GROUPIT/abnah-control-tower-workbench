-- Query Table: STD_Entry_Report
-- Purpose: Union outlet-specific RAW entry feeds into standardized receipt/GRN-style rows.
-- Sources: RAW_Entry_Report_OUT001, RAW_Entry_Report_OUT002, RAW_Entry_Report_OUT003
-- Join keys downstream: outlet_name, vendor_name, item_code, receipt_date.
-- Caveat: Entry rows do not carry po_number, so PO matching is approximate.

SELECT DISTINCT
    src."row_id" AS "entry_row_id",
    src."deployment_name" AS "outlet_name",
    CASE
        WHEN src."deployment_name" = 'ABNAH Cafe Connaught Place' THEN 'OUT001'
        WHEN src."deployment_name" = 'ABNAH Cafe Hauz Khas' THEN 'OUT002'
        WHEN src."deployment_name" = 'ABNAH Cafe Saket Premium' THEN 'OUT003'
        ELSE NULL
    END AS "outlet_code",
    CASE
        WHEN src."deployment_name" = 'ABNAH Cafe Connaught Place' THEN 'Connaught Place'
        WHEN src."deployment_name" = 'ABNAH Cafe Hauz Khas' THEN 'Hauz Khas'
        WHEN src."deployment_name" = 'ABNAH Cafe Saket Premium' THEN 'Saket'
        ELSE NULL
    END AS "market_area",
    src."store_kitchen_name" AS "store_kitchen_name",
    src."user_name" AS "user_name",
    src."vendor_name" AS "vendor_name",
    CAST(src."date" AS DATE) AS "receipt_date",
    src."transaction_number" AS "transaction_number",
    src."invoice_number" AS "invoice_number",
    CAST(src."invoice_date" AS DATE) AS "invoice_date",
    src."item_code" AS "item_code",
    src."item_name" AS "item_name",
    src."category_name" AS "category_name",
    src."super_category_name" AS "super_category_name",
    CAST(src."quantity" AS DECIMAL(14,4)) AS "received_qty",
    src."unit" AS "unit",
    CAST(src."mrp" AS DECIMAL(14,2)) AS "mrp",
    CAST(src."unit_price" AS DECIMAL(14,2)) AS "unit_price",
    CAST(src."amount" AS DECIMAL(14,2)) AS "amount",
    CAST(src."discount" AS DECIMAL(14,2)) AS "discount",
    CAST(src."gst_igst_rate" AS DECIMAL(8,2)) AS "gst_igst_rate",
    CAST(src."gst_igst_value" AS DECIMAL(14,2)) AS "gst_igst_value",
    CAST(src."total_tax" AS DECIMAL(14,2)) AS "total_tax",
    CAST(src."item_charges_amount" AS DECIMAL(14,2)) AS "item_charges_amount",
    CAST(src."entry_total" AS DECIMAL(14,2)) AS "entry_total",
    CAST(src."return_quantity" AS DECIMAL(14,4)) AS "return_qty",
    CAST(src."return_amount" AS DECIMAL(14,2)) AS "return_amount",
    CAST(src."grand_total" AS DECIMAL(14,2)) AS "grand_total"
FROM (
    SELECT
        r1."row_id" AS "row_id",
        r1."deployment_name" AS "deployment_name",
        r1."store_kitchen_name" AS "store_kitchen_name",
        r1."user_name" AS "user_name",
        r1."vendor_name" AS "vendor_name",
        r1."date" AS "date",
        r1."transaction_number" AS "transaction_number",
        r1."invoice_number" AS "invoice_number",
        r1."invoice_date" AS "invoice_date",
        r1."item_code" AS "item_code",
        r1."item_name" AS "item_name",
        r1."category_name" AS "category_name",
        r1."super_category_name" AS "super_category_name",
        r1."quantity" AS "quantity",
        r1."unit" AS "unit",
        r1."mrp" AS "mrp",
        r1."unit_price" AS "unit_price",
        r1."amount" AS "amount",
        r1."discount" AS "discount",
        r1."gst_igst_rate" AS "gst_igst_rate",
        r1."gst_igst_value" AS "gst_igst_value",
        r1."total_tax" AS "total_tax",
        r1."item_charges_amount" AS "item_charges_amount",
        r1."entry_total" AS "entry_total",
        r1."return_quantity" AS "return_quantity",
        r1."return_amount" AS "return_amount",
        r1."grand_total" AS "grand_total"
    FROM "RAW_Entry_Report_OUT001" r1
    UNION ALL
    SELECT
        r2."row_id" AS "row_id",
        r2."deployment_name" AS "deployment_name",
        r2."store_kitchen_name" AS "store_kitchen_name",
        r2."user_name" AS "user_name",
        r2."vendor_name" AS "vendor_name",
        r2."date" AS "date",
        r2."transaction_number" AS "transaction_number",
        r2."invoice_number" AS "invoice_number",
        r2."invoice_date" AS "invoice_date",
        r2."item_code" AS "item_code",
        r2."item_name" AS "item_name",
        r2."category_name" AS "category_name",
        r2."super_category_name" AS "super_category_name",
        r2."quantity" AS "quantity",
        r2."unit" AS "unit",
        r2."mrp" AS "mrp",
        r2."unit_price" AS "unit_price",
        r2."amount" AS "amount",
        r2."discount" AS "discount",
        r2."gst_igst_rate" AS "gst_igst_rate",
        r2."gst_igst_value" AS "gst_igst_value",
        r2."total_tax" AS "total_tax",
        r2."item_charges_amount" AS "item_charges_amount",
        r2."entry_total" AS "entry_total",
        r2."return_quantity" AS "return_quantity",
        r2."return_amount" AS "return_amount",
        r2."grand_total" AS "grand_total"
    FROM "RAW_Entry_Report_OUT002" r2
    UNION ALL
    SELECT
        r3."row_id" AS "row_id",
        r3."deployment_name" AS "deployment_name",
        r3."store_kitchen_name" AS "store_kitchen_name",
        r3."user_name" AS "user_name",
        r3."vendor_name" AS "vendor_name",
        r3."date" AS "date",
        r3."transaction_number" AS "transaction_number",
        r3."invoice_number" AS "invoice_number",
        r3."invoice_date" AS "invoice_date",
        r3."item_code" AS "item_code",
        r3."item_name" AS "item_name",
        r3."category_name" AS "category_name",
        r3."super_category_name" AS "super_category_name",
        r3."quantity" AS "quantity",
        r3."unit" AS "unit",
        r3."mrp" AS "mrp",
        r3."unit_price" AS "unit_price",
        r3."amount" AS "amount",
        r3."discount" AS "discount",
        r3."gst_igst_rate" AS "gst_igst_rate",
        r3."gst_igst_value" AS "gst_igst_value",
        r3."total_tax" AS "total_tax",
        r3."item_charges_amount" AS "item_charges_amount",
        r3."entry_total" AS "entry_total",
        r3."return_quantity" AS "return_quantity",
        r3."return_amount" AS "return_amount",
        r3."grand_total" AS "grand_total"
    FROM "RAW_Entry_Report_OUT003" r3
) src;
