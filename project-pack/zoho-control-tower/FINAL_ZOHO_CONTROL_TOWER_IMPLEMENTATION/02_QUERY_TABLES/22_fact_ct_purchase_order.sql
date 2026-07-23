-- Query Table: 22_fact_ct_purchase_order.sql
-- Logical model name: FACT_CT_Purchase_Order
-- Layer: fact
-- Purpose: Calculate ordered, pending and open PO values.
-- Sources: 07_std_ct_purchase_order.sql
-- Validate CAST/date function behavior once in the target Zoho workspace.
SELECT
    p.*,
    p."remaining_qty" * p."unit_price" AS "open_po_value",
    p."processed_qty" * p."unit_price" AS "processed_po_value",
    CASE
        WHEN p."is_open_po" = 1 AND p."expected_delivery_date" IS NULL THEN 1
        ELSE 0
    END AS "missing_expected_delivery_flag",
    CASE
        WHEN p."is_open_po" = 1
         AND p."expected_delivery_date" < p."as_of_date"
        THEN 1 ELSE 0
    END AS "delayed_po_flag"
FROM "07_std_ct_purchase_order.sql" p;
