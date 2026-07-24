-- Query Table: 24_fact_ct_po_receipt_line.sql
-- Logical model name: FACT_CT_PO_Receipt_Line
-- Layer: fact
-- Purpose: Join exact PO number, outlet and item to receipt lines for fill-rate and OTIF logic.
-- Sources: 07_std_ct_purchase_order.sql, 08_std_ct_purchase_receipt.sql
-- Validate CAST/date function behavior once in the target Zoho workspace.
SELECT
    p."source_period_code" AS "source_period_code",
    p."as_of_date" AS "as_of_date",
    p."outlet_code" AS "outlet_code",
    p."outlet_name" AS "outlet_name",
    p."vendor_name" AS "vendor_name",
    p."po_number" AS "po_number",
    p."po_date" AS "po_date",
    p."expected_delivery_date" AS "expected_delivery_date",
    p."po_status" AS "po_status",
    p."item_code" AS "item_code",
    p."item_name" AS "item_name",
    p."category_name" AS "category_name",
    p."canonical_uom" AS "canonical_uom",
    p."ordered_qty" AS "ordered_qty",
    p."processed_qty" AS "processed_qty",
    p."remaining_qty" AS "remaining_qty",
    p."unit_price" AS "unit_price",
    p."gross_order_value" AS "gross_order_value",
    p."is_open_po" AS "is_open_po",
    p."remaining_qty" * p."unit_price" AS "open_po_value",
    r."receipt_date" AS "receipt_date",
    COALESCE(r."received_qty", 0) AS "received_qty",
    COALESCE(r."receipt_total", 0) AS "receipt_total",
    CASE
        WHEN r."receipt_date" IS NOT NULL
         AND p."expected_delivery_date" IS NOT NULL
         AND r."receipt_date" <= p."expected_delivery_date"
        THEN 1 ELSE 0
    END AS "on_time_flag",
    CASE
        WHEN COALESCE(r."received_qty", 0) >= p."ordered_qty" THEN 1 ELSE 0
    END AS "in_full_flag",
    CASE
        WHEN p."is_open_po" = 0
         AND r."receipt_date" IS NOT NULL
         AND p."expected_delivery_date" IS NOT NULL
        THEN 1 ELSE 0
    END AS "eligible_closed_line_flag",
    CASE
        WHEN p."is_open_po" = 0
         AND r."receipt_date" IS NOT NULL
         AND p."expected_delivery_date" IS NOT NULL
         AND r."receipt_date" <= p."expected_delivery_date"
         AND COALESCE(r."received_qty", 0) >= p."ordered_qty"
        THEN 1 ELSE 0
    END AS "otif_success_flag",
    CASE
        WHEN r."receipt_date" IS NOT NULL
         AND p."expected_delivery_date" IS NOT NULL
        THEN DATEDIFF(r."receipt_date", p."expected_delivery_date")
        ELSE NULL
    END AS "lead_time_deviation_days",
    CASE
        WHEN p."is_open_po" = 0
         AND r."receipt_date" IS NOT NULL
         AND p."expected_delivery_date" IS NOT NULL
        THEN DATEDIFF(r."receipt_date", p."expected_delivery_date")
        ELSE NULL
    END AS "eligible_lead_time_deviation_days",
    CASE
        WHEN p."is_open_po" = 1
         AND p."expected_delivery_date" IS NULL
        THEN 1 ELSE 0
    END AS "missing_expected_delivery_flag",
    CASE
        WHEN p."is_open_po" = 1
         AND p."expected_delivery_date" < p."as_of_date"
        THEN 1 ELSE 0
    END AS "delayed_po_flag"
FROM "07_std_ct_purchase_order.sql" p
LEFT JOIN (
    SELECT
        e."source_period_code" AS "source_period_code",
        e."outlet_code" AS "outlet_code",
        e."po_number" AS "po_number",
        e."item_code" AS "item_code",
        MAX(e."receipt_date") AS "receipt_date",
        SUM(e."received_qty") AS "received_qty",
        SUM(e."receipt_total") AS "receipt_total"
    FROM "08_std_ct_purchase_receipt.sql" e
    GROUP BY
        e."source_period_code",
        e."outlet_code",
        e."po_number",
        e."item_code"
) r
  ON p."outlet_code" = r."outlet_code"
 AND p."po_number" = r."po_number"
 AND p."item_code" = r."item_code"
 AND p."source_period_code" = r."source_period_code";
