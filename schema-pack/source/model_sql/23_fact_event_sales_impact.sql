-- Query Table: FACT_Event_Sales_Impact
-- Purpose: Join manual event windows to sales and calculate directional event lift.
-- Sources: DIM_Event, FACT_Sales
-- Join keys: sales_date between event dates, plus outlet/category/item text scope.
-- Needs Zoho syntax validation: LIKE with CONCAT and DATEADD may need local adjustment.
-- Parser note: baseline calculation is built with derived tables, not correlated subqueries.

SELECT
    es."event_id" AS "event_id",
    es."event_name" AS "event_name",
    es."event_type" AS "event_type",
    es."start_date" AS "start_date",
    es."end_date" AS "end_date",
    es."outlet_scope" AS "outlet_scope",
    es."affected_outlets" AS "affected_outlets",
    es."affected_category" AS "affected_category",
    es."affected_items" AS "affected_items",
    es."confidence_level" AS "confidence_level",
    es."expected_impact_pct" AS "expected_impact_pct",
    es."sales_date" AS "sales_date",
    es."outlet_code" AS "outlet_code",
    es."outlet_name" AS "outlet_name",
    es."market_area" AS "market_area",
    es."item_number" AS "item_number",
    es."item_name" AS "item_name",
    es."super_category" AS "super_category",
    es."category" AS "category",
    es."event_day_qty" AS "event_day_qty",
    es."event_day_sales" AS "event_day_sales",
    AVG(bd."daily_sales") AS "baseline_sales",
    CASE
        WHEN AVG(bd."daily_sales") > 0
        THEN ((es."event_day_sales" - AVG(bd."daily_sales")) / AVG(bd."daily_sales")) * 100
        ELSE NULL
    END AS "sales_lift_pct"
FROM (
    SELECT
        ev."event_id" AS "event_id",
        ev."event_name" AS "event_name",
        ev."event_type" AS "event_type",
        ev."start_date" AS "start_date",
        ev."end_date" AS "end_date",
        ev."outlet_scope" AS "outlet_scope",
        ev."affected_outlets" AS "affected_outlets",
        ev."affected_category" AS "affected_category",
        ev."affected_items" AS "affected_items",
        ev."confidence_level" AS "confidence_level",
        ev."expected_impact_pct" AS "expected_impact_pct",
        fs."sales_date" AS "sales_date",
        fs."outlet_code" AS "outlet_code",
        fs."outlet_name" AS "outlet_name",
        fs."market_area" AS "market_area",
        fs."item_number" AS "item_number",
        fs."item_name" AS "item_name",
        fs."super_category" AS "super_category",
        fs."category" AS "category",
        SUM(fs."qty") AS "event_day_qty",
        SUM(fs."net_sale") AS "event_day_sales"
    FROM "DIM_Event" ev
    INNER JOIN "FACT_Sales" fs
        ON fs."sales_date" BETWEEN ev."start_date" AND ev."end_date"
       AND (
            ev."outlet_scope" = 'All outlets'
            OR ev."affected_outlets" LIKE CONCAT('%', fs."outlet_name", '%')
       )
       AND (
            ev."affected_category" IS NULL
            OR ev."affected_category" = ''
            OR ev."affected_category" LIKE CONCAT('%', fs."category", '%')
            OR ev."affected_category" LIKE CONCAT('%', fs."super_category", '%')
       )
       AND (
            ev."affected_items" IS NULL
            OR ev."affected_items" = ''
            OR ev."affected_items" LIKE CONCAT('%', fs."item_name", '%')
       )
    GROUP BY
        ev."event_id",
        ev."event_name",
        ev."event_type",
        ev."start_date",
        ev."end_date",
        ev."outlet_scope",
        ev."affected_outlets",
        ev."affected_category",
        ev."affected_items",
        ev."confidence_level",
        ev."expected_impact_pct",
        fs."sales_date",
        fs."outlet_code",
        fs."outlet_name",
        fs."market_area",
        fs."item_number",
        fs."item_name",
        fs."super_category",
        fs."category"
) es
LEFT JOIN (
    SELECT
        evb."event_id" AS "event_id",
        fb."outlet_code" AS "outlet_code",
        fb."outlet_name" AS "outlet_name",
        fb."item_number" AS "item_number",
        fb."sales_date" AS "baseline_date",
        SUM(fb."net_sale") AS "daily_sales"
    FROM "DIM_Event" evb
    INNER JOIN "FACT_Sales" fb
        ON fb."sales_date" >= DATEADD(day, -7, evb."start_date")
       AND fb."sales_date" < evb."start_date"
       AND (
            evb."outlet_scope" = 'All outlets'
            OR evb."affected_outlets" LIKE CONCAT('%', fb."outlet_name", '%')
       )
       AND (
            evb."affected_category" IS NULL
            OR evb."affected_category" = ''
            OR evb."affected_category" LIKE CONCAT('%', fb."category", '%')
            OR evb."affected_category" LIKE CONCAT('%', fb."super_category", '%')
       )
       AND (
            evb."affected_items" IS NULL
            OR evb."affected_items" = ''
            OR evb."affected_items" LIKE CONCAT('%', fb."item_name", '%')
       )
    GROUP BY
        evb."event_id",
        fb."outlet_code",
        fb."outlet_name",
        fb."item_number",
        fb."sales_date"
) bd
    ON bd."event_id" = es."event_id"
   AND bd."outlet_code" = es."outlet_code"
   AND bd."outlet_name" = es."outlet_name"
   AND bd."item_number" = es."item_number"
GROUP BY
    es."event_id",
    es."event_name",
    es."event_type",
    es."start_date",
    es."end_date",
    es."outlet_scope",
    es."affected_outlets",
    es."affected_category",
    es."affected_items",
    es."confidence_level",
    es."expected_impact_pct",
    es."sales_date",
    es."outlet_code",
    es."outlet_name",
    es."market_area",
    es."item_number",
    es."item_name",
    es."super_category",
    es."category",
    es."event_day_qty",
    es."event_day_sales";
