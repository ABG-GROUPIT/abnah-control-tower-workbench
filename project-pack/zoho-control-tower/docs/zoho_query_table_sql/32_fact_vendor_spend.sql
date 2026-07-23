-- Query Table: FACT_Vendor_Spend
-- Purpose: Vendor/date/outlet spend fact combining PO value and receipt value.
-- Sources: FACT_Purchase_Order, FACT_Entry_Receipt
-- Supplemental file: requested layer list includes FACT_Vendor_Spend, but the requested numbered file list omitted it.

SELECT
    x."activity_date" AS "activity_date",
    x."outlet_code" AS "outlet_code",
    x."outlet_name" AS "outlet_name",
    x."market_area" AS "market_area",
    x."vendor_name" AS "vendor_name",
    x."item_code" AS "item_code",
    x."item_name" AS "item_name",
    x."category_name" AS "category_name",
    x."super_category_name" AS "super_category_name",
    x."po_status" AS "po_status",
    SUM(x."ordered_value") AS "ordered_value",
    SUM(x."received_value") AS "received_value",
    SUM(x."po_line_count") AS "po_line_count",
    SUM(x."receipt_line_count") AS "receipt_line_count",
    SUM(x."open_or_partial_po_count") AS "open_or_partial_po_count"
FROM (
    SELECT
        po."po_date" AS "activity_date",
        po."outlet_code" AS "outlet_code",
        po."outlet_name" AS "outlet_name",
        po."market_area" AS "market_area",
        po."vendor_name" AS "vendor_name",
        po."item_code" AS "item_code",
        po."item_name" AS "item_name",
        po."category_name" AS "category_name",
        po."super_category_name" AS "super_category_name",
        po."po_status" AS "po_status",
        SUM(po."total_item_cost") AS "ordered_value",
        0 AS "received_value",
        COUNT(*) AS "po_line_count",
        0 AS "receipt_line_count",
        SUM(po."is_open_or_partial") AS "open_or_partial_po_count"
    FROM "FACT_Purchase_Order" po
    GROUP BY
        po."po_date",
        po."outlet_code",
        po."outlet_name",
        po."market_area",
        po."vendor_name",
        po."item_code",
        po."item_name",
        po."category_name",
        po."super_category_name",
        po."po_status"

    UNION ALL

    SELECT
        er."receipt_date" AS "activity_date",
        er."outlet_code" AS "outlet_code",
        er."outlet_name" AS "outlet_name",
        er."market_area" AS "market_area",
        er."vendor_name" AS "vendor_name",
        er."item_code" AS "item_code",
        er."item_name" AS "item_name",
        er."category_name" AS "category_name",
        er."super_category_name" AS "super_category_name",
        NULL AS "po_status",
        0 AS "ordered_value",
        SUM(er."grand_total") AS "received_value",
        0 AS "po_line_count",
        COUNT(*) AS "receipt_line_count",
        0 AS "open_or_partial_po_count"
    FROM "FACT_Entry_Receipt" er
    GROUP BY
        er."receipt_date",
        er."outlet_code",
        er."outlet_name",
        er."market_area",
        er."vendor_name",
        er."item_code",
        er."item_name",
        er."category_name",
        er."super_category_name"
) x
GROUP BY
    x."activity_date",
    x."outlet_code",
    x."outlet_name",
    x."market_area",
    x."vendor_name",
    x."item_code",
    x."item_name",
    x."category_name",
    x."super_category_name",
    x."po_status";
