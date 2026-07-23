-- Query Table: ZIA_Procurement_Daily_Vendor_Material
-- Purpose: Ask Zia-safe procurement movement table.
-- Source: FACT_Vendor_Spend.
-- Grain: one row per outlet, date, vendor, material, PO status.
-- Use for: PO raised value, receipt booked value, vendor/material/date questions.

SELECT
    v."activity_date" AS "business_date",
    YEAR(v."activity_date") AS "year_number",
    MONTH(v."activity_date") AS "month_number",
    CONCAT(YEAR(v."activity_date"), '-', LPAD(MONTH(v."activity_date"), 2, '0')) AS "month_key",
    v."outlet_code" AS "outlet_code",
    v."outlet_name" AS "outlet_name",
    v."market_area" AS "market_area",
    v."vendor_name" AS "vendor_name",
    v."item_code" AS "material_code",
    v."item_name" AS "material_name",
    v."category_name" AS "material_category",
    v."super_category_name" AS "material_super_category",
    v."po_status" AS "po_status",
    v."ordered_value" AS "po_raised_value",
    v."received_value" AS "receipt_booked_value",
    v."ordered_value" - v."received_value" AS "po_receipt_gap_value",
    v."po_line_count" AS "po_line_count",
    v."receipt_line_count" AS "receipt_line_count",
    v."open_or_partial_po_count" AS "open_or_partial_po_count"
FROM "FACT_Vendor_Spend" v;
