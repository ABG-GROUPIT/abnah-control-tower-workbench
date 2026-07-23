-- Query Table: FACT_PO_Receipt_Comparison
-- Purpose: Compare purchase order lines with receipt/entry rows.
-- Sources: FACT_Purchase_Order, FACT_Entry_Receipt
-- Join keys: outlet_name, vendor_name, item_code, receipt_date between po_date and expected_delivery_date.
-- Caveat: Approximate because entry rows do not include po_number.

SELECT
    p."purchase_row_id" AS "purchase_row_id",
    p."po_number" AS "po_number",
    p."po_date" AS "po_date",
    p."expected_delivery_date" AS "expected_delivery_date",
    p."outlet_code" AS "outlet_code",
    p."outlet_name" AS "outlet_name",
    p."market_area" AS "market_area",
    p."vendor_name" AS "vendor_name",
    p."vendor_code" AS "vendor_code",
    p."po_status" AS "po_status",
    p."item_code" AS "item_code",
    p."item_name" AS "item_name",
    p."ordered_qty" AS "ordered_qty",
    p."processed_qty" AS "processed_qty",
    p."remaining_qty" AS "remaining_qty",
    p."unit" AS "unit",
    p."total_item_cost" AS "total_item_cost",
    COALESCE(SUM(e."received_qty"), 0) AS "matched_received_qty",
    COALESCE(SUM(e."grand_total"), 0) AS "matched_received_value",
    p."ordered_qty" - COALESCE(SUM(e."received_qty"), 0) AS "unmatched_order_qty",
    CASE
        WHEN p."po_status" IN ('Pending', 'Partially Received') THEN 1
        WHEN p."remaining_qty" > 0 THEN 1
        ELSE 0
    END AS "pending_or_partial_flag"
FROM "FACT_Purchase_Order" p
LEFT JOIN "FACT_Entry_Receipt" e
    ON e."outlet_name" = p."outlet_name"
   AND e."outlet_code" = p."outlet_code"
   AND e."vendor_name" = p."vendor_name"
   AND e."item_code" = p."item_code"
   AND e."receipt_date" BETWEEN p."po_date" AND p."expected_delivery_date"
GROUP BY
    p."purchase_row_id",
    p."po_number",
    p."po_date",
    p."expected_delivery_date",
    p."outlet_code",
    p."outlet_name",
    p."market_area",
    p."vendor_name",
    p."vendor_code",
    p."po_status",
    p."item_code",
    p."item_name",
    p."ordered_qty",
    p."processed_qty",
    p."remaining_qty",
    p."unit",
    p."total_item_cost";
