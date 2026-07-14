-- Query Table: FACT_Outlet_Daily_Health
-- Purpose: Daily outlet-level operational summary.
-- Sources: FACT_Sales, FACT_Purchase_Order, FACT_Entry_Receipt, FACT_Inventory_Closing, DIM_Event
-- Parser note: event_count is built with a derived table, not correlated subqueries.

SELECT
    s."activity_date" AS "activity_date",
    s."outlet_code" AS "outlet_code",
    s."outlet_name" AS "outlet_name",
    s."market_area" AS "market_area",
    s."net_sales" AS "net_sales",
    s."sold_qty" AS "sold_qty",
    s."sales_line_count" AS "sales_line_count",
    COALESCE(p."po_value", 0) AS "po_value",
    COALESCE(p."open_or_partial_po_count", 0) AS "open_or_partial_po_count",
    COALESCE(r."receipt_value", 0) AS "receipt_value",
    COALESCE(i."inventory_value", 0) AS "inventory_value",
    COALESCE(i."low_stock_item_count", 0) AS "low_stock_item_count",
    COALESCE(ec."event_count", 0) AS "event_count",
    CASE
        WHEN COALESCE(i."low_stock_item_count", 0) >= 5 THEN 'Inventory Pressure'
        WHEN COALESCE(ec."event_count", 0) > 0 THEN 'Event Day'
        ELSE 'Normal'
    END AS "health_note"
FROM (
    SELECT
        fs."sales_date" AS "activity_date",
        fs."outlet_code" AS "outlet_code",
        fs."outlet_name" AS "outlet_name",
        fs."market_area" AS "market_area",
        SUM(fs."net_sale") AS "net_sales",
        SUM(fs."qty") AS "sold_qty",
        COUNT(*) AS "sales_line_count"
    FROM "FACT_Sales" fs
    GROUP BY
        fs."sales_date",
        fs."outlet_code",
        fs."outlet_name",
        fs."market_area"
) s
LEFT JOIN (
    SELECT
        po."po_date" AS "activity_date",
        po."outlet_code" AS "outlet_code",
        po."outlet_name" AS "outlet_name",
        po."market_area" AS "market_area",
        SUM(po."total_item_cost") AS "po_value",
        SUM(po."is_open_or_partial") AS "open_or_partial_po_count"
    FROM "FACT_Purchase_Order" po
    GROUP BY
        po."po_date",
        po."outlet_code",
        po."outlet_name",
        po."market_area"
) p
    ON p."activity_date" = s."activity_date"
   AND p."outlet_code" = s."outlet_code"
   AND p."outlet_name" = s."outlet_name"
LEFT JOIN (
    SELECT
        er."receipt_date" AS "activity_date",
        er."outlet_code" AS "outlet_code",
        er."outlet_name" AS "outlet_name",
        er."market_area" AS "market_area",
        SUM(er."grand_total") AS "receipt_value"
    FROM "FACT_Entry_Receipt" er
    GROUP BY
        er."receipt_date",
        er."outlet_code",
        er."outlet_name",
        er."market_area"
) r
    ON r."activity_date" = s."activity_date"
   AND r."outlet_code" = s."outlet_code"
   AND r."outlet_name" = s."outlet_name"
LEFT JOIN (
    SELECT
        inv."inventory_date" AS "activity_date",
        inv."outlet_code" AS "outlet_code",
        inv."outlet_name" AS "outlet_name",
        inv."market_area" AS "market_area",
        SUM(inv."total_amt") AS "inventory_value",
        SUM(inv."low_stock_flag") AS "low_stock_item_count"
    FROM "FACT_Inventory_Closing" inv
    GROUP BY
        inv."inventory_date",
        inv."outlet_code",
        inv."outlet_name",
        inv."market_area"
) i
    ON i."activity_date" = s."activity_date"
   AND i."outlet_code" = s."outlet_code"
   AND i."outlet_name" = s."outlet_name"
LEFT JOIN (
    SELECT
        fs."sales_date" AS "activity_date",
        fs."outlet_code" AS "outlet_code",
        fs."outlet_name" AS "outlet_name",
        COUNT(DISTINCT ev."event_id") AS "event_count"
    FROM "FACT_Sales" fs
    INNER JOIN "DIM_Event" ev
        ON fs."sales_date" BETWEEN ev."start_date" AND ev."end_date"
       AND (
            ev."outlet_scope" = 'All outlets'
            OR ev."affected_outlets" LIKE CONCAT('%', fs."outlet_name", '%')
       )
    GROUP BY
        fs."sales_date",
        fs."outlet_code",
        fs."outlet_name"
) ec
    ON ec."activity_date" = s."activity_date"
   AND ec."outlet_code" = s."outlet_code"
   AND ec."outlet_name" = s."outlet_name";
