-- Query Table: ZIA_Procurement_Monthly_Vendor
-- Purpose: Ask Zia-safe monthly vendor scorecard.
-- Source: FACT_Vendor_Spend.
-- Grain: one row per outlet, vendor, month.
-- Use for: top vendors, receipt coverage, PO vs receipt gap.

SELECT
    YEAR(v."activity_date") AS "year_number",
    MONTH(v."activity_date") AS "month_number",
    CONCAT(YEAR(v."activity_date"), '-', LPAD(MONTH(v."activity_date"), 2, '0')) AS "month_key",
    MIN(v."activity_date") AS "month_start_date",
    MAX(v."activity_date") AS "month_end_date",
    v."outlet_code" AS "outlet_code",
    v."outlet_name" AS "outlet_name",
    v."market_area" AS "market_area",
    v."vendor_name" AS "vendor_name",
    COUNT(DISTINCT v."item_name") AS "material_count",
    SUM(v."ordered_value") AS "po_raised_value",
    SUM(v."received_value") AS "receipt_booked_value",
    SUM(v."ordered_value") - SUM(v."received_value") AS "po_receipt_gap_value",
    SUM(v."open_or_partial_po_count") AS "open_or_partial_po_count",
    SUM(v."po_line_count") AS "po_line_count",
    SUM(v."receipt_line_count") AS "receipt_line_count",
    CASE
        WHEN SUM(v."ordered_value") <> 0 THEN SUM(v."received_value") * 100 / SUM(v."ordered_value")
        ELSE NULL
    END AS "receipt_coverage_pct"
FROM "FACT_Vendor_Spend" v
GROUP BY
    YEAR(v."activity_date"),
    MONTH(v."activity_date"),
    CONCAT(YEAR(v."activity_date"), '-', LPAD(MONTH(v."activity_date"), 2, '0')),
    v."outlet_code",
    v."outlet_name",
    v."market_area",
    v."vendor_name";
