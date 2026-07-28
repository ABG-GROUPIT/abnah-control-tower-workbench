-- Query Table: D04_demo_p2_po_control.sql
-- Purpose: Concise Page 2 purchase-order control table for the visual demo.
-- Source: 07_std_ct_purchase_order.sql
-- Dependency level: 2
-- Isolation rule: Do not replace or edit Query 22.
SELECT
    p."source_period_code" AS "source_period_code",
    p."po_date" AS "filter_date",
    p."outlet_name" AS "filter_outlet",
    p."vendor_name" AS "filter_vendor",
    p."category_name" AS "filter_category",
    p."outlet_code" AS "outlet_code",
    p."po_number" AS "po_number",
    p."po_status" AS "po_status",
    p."item_code" AS "item_code",
    p."item_name" AS "item_name",
    p."canonical_uom" AS "canonical_uom",
    p."expected_delivery_date" AS "expected_delivery_date",
    p."ordered_qty" AS "ordered_qty",
    p."processed_qty" AS "processed_qty",
    p."remaining_qty" AS "remaining_qty",
    p."unit_price" AS "unit_price",
    p."gross_order_value" AS "gross_order_value",
    p."remaining_qty" * p."unit_price" AS "open_po_value",
    CASE
        WHEN p."is_open_po" = 1
         AND p."expected_delivery_date" IS NULL
        THEN 'MISSING DATE'
        WHEN p."is_open_po" = 1
         AND p."expected_delivery_date" < p."as_of_date"
        THEN 'DELAYED'
        WHEN p."is_open_po" = 1 THEN 'OPEN'
        ELSE 'CLOSED'
    END AS "delivery_control_status",
    CASE
        WHEN p."is_open_po" = 1
         AND p."expected_delivery_date" IS NULL
        THEN 'RED'
        WHEN p."is_open_po" = 1
         AND p."expected_delivery_date" < p."as_of_date"
        THEN 'RED'
        WHEN p."is_open_po" = 1 THEN 'AMBER'
        ELSE 'GREEN'
    END AS "control_severity"
FROM "07_std_ct_purchase_order.sql" p;
