-- Query Table: 07_std_ct_purchase_order.sql
-- Logical model name: STD_CT_Purchase_Order
-- Layer: standardized
-- Purpose: Standardize purchase-order lines and normalized open/closed status.
-- Sources: RAWN_CT_enterprise_purchase_order-Copy
-- Validate CAST/date function behavior once in the target Zoho workspace.
SELECT
    p."source_period_code" AS "source_period_code",
    CAST(p."source_period_end" AS DATE) AS "as_of_date",
    p."source_outlet_code" AS "outlet_code",
    p."deployment_name" AS "outlet_name",
    p."store_name" AS "store_name",
    p."vendor_name" AS "vendor_name",
    p."po_number" AS "po_number",
    CAST(p."po_date" AS DATE) AS "po_date",
    CAST(p."expected_delivery_date" AS DATE) AS "expected_delivery_date",
    CAST(p."po_close_or_partial_receive_date" AS DATE) AS "close_or_partial_receive_date",
    p."po_status" AS "po_status",
    p."item_code" AS "item_code",
    p."item_name" AS "item_name",
    p."category_name" AS "category_name",
    p."super_category_name" AS "super_category_name",
    CAST(p."processed_qty" AS DECIMAL(18,6)) AS "processed_qty",
    CAST(p."remaining_balance_qty" AS DECIMAL(18,6)) AS "remaining_qty",
    CAST(p."ordered_qty" AS DECIMAL(18,6)) AS "ordered_qty",
    p."unit" AS "canonical_uom",
    CAST(p."unit_price" AS DECIMAL(18,4)) AS "unit_price",
    CAST(p."new_subtotal" AS DECIMAL(18,2)) AS "net_order_value",
    CAST(p."tax_amt" AS DECIMAL(18,2)) AS "tax_value",
    CAST(p."total_item_cost" AS DECIMAL(18,2)) AS "gross_order_value",
    CASE
        WHEN p."po_status" IN ('Pending', 'Partially Received') THEN 1
        WHEN CAST(p."remaining_balance_qty" AS DECIMAL(18,6)) > 0 THEN 1
        ELSE 0
    END AS "is_open_po"
FROM "RAWN_CT_enterprise_purchase_order-Copy" p;
