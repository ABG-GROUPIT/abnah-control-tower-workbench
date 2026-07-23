-- Query Table: 08_std_ct_purchase_receipt.sql
-- Logical model name: STD_CT_Purchase_Receipt
-- Layer: standardized
-- Purpose: Standardize PO-linked GRN/entry lines.
-- Sources: RAWN_CT_enterprise_entry-Copy
-- Validate CAST/date function behavior once in the target Zoho workspace.
SELECT
    e."source_period_code" AS "source_period_code",
    e."source_outlet_code" AS "outlet_code",
    e."deployment_name" AS "outlet_name",
    e."store_kitchen_name" AS "store_kitchen_name",
    e."vendor_name" AS "vendor_name",
    e."po_number" AS "po_number",
    e."transaction_number" AS "grn_number",
    e."invoice_number" AS "invoice_number",
    CAST(e."entry_date" AS DATE) AS "receipt_date",
    CAST(e."invoice_date" AS DATE) AS "invoice_date",
    e."item_code" AS "item_code",
    e."item_name" AS "item_name",
    e."category_name" AS "category_name",
    e."super_category_name" AS "super_category_name",
    CAST(e."entry_qty" AS DECIMAL(18,6)) AS "received_qty",
    e."unit" AS "canonical_uom",
    CAST(e."unit_price" AS DECIMAL(18,4)) AS "unit_price",
    CAST(e."base_amt" AS DECIMAL(18,2)) AS "receipt_subtotal",
    CAST(e."discount_amt" AS DECIMAL(18,2)) AS "discount_value",
    CAST(e."total_tax_amt" AS DECIMAL(18,2)) AS "tax_value",
    CAST(e."total_amt" AS DECIMAL(18,2)) AS "receipt_total"
FROM "RAWN_CT_enterprise_entry-Copy" e;
