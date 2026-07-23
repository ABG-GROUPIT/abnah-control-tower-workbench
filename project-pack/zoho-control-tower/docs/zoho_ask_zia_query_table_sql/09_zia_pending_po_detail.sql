-- Query Table: ZIA_Pending_PO_Detail
-- Purpose: Ask Zia-safe pending/partial PO follow-up list.
-- Source: FACT_PO_Receipt_Comparison.
-- Grain: one row per pending/partial PO material line.
-- Use for: pending PO detail, pending material quantity, follow-up questions.

SELECT
    p."po_number" AS "po_number",
    p."po_date" AS "po_date",
    YEAR(p."po_date") AS "po_year_number",
    MONTH(p."po_date") AS "po_month_number",
    CONCAT(YEAR(p."po_date"), '-', LPAD(MONTH(p."po_date"), 2, '0')) AS "po_month_key",
    p."expected_delivery_date" AS "expected_delivery_date",
    p."outlet_code" AS "outlet_code",
    p."outlet_name" AS "outlet_name",
    p."market_area" AS "market_area",
    p."vendor_name" AS "vendor_name",
    p."item_code" AS "material_code",
    p."item_name" AS "material_name",
    p."po_status" AS "po_status",
    p."ordered_qty" AS "ordered_qty",
    p."processed_qty" AS "processed_qty",
    p."remaining_qty" AS "remaining_qty",
    p."unit" AS "unit",
    p."total_item_cost" AS "po_raised_value",
    p."matched_received_qty" AS "matched_received_qty",
    p."matched_received_value" AS "matched_received_value",
    p."unmatched_order_qty" AS "unmatched_order_qty",
    p."pending_or_partial_flag" AS "pending_or_partial_flag",
    CASE
        WHEN p."ordered_qty" <> 0 THEN p."total_item_cost" * p."remaining_qty" / p."ordered_qty"
        ELSE NULL
    END AS "estimated_remaining_value"
FROM "FACT_PO_Receipt_Comparison" p
WHERE p."pending_or_partial_flag" = 1;
