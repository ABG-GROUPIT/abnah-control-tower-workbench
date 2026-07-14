-- Query Table: SUM_Event_Impact
-- Purpose: Event lift summary by event, outlet, category, and item.
-- Source: FACT_Event_Sales_Impact
-- Caveat: Lift is directional and depends on baseline query compatibility.

SELECT
    fe."event_id" AS "event_id",
    fe."event_name" AS "event_name",
    fe."event_type" AS "event_type",
    fe."start_date" AS "start_date",
    fe."end_date" AS "end_date",
    fe."outlet_code" AS "outlet_code",
    fe."outlet_name" AS "outlet_name",
    fe."market_area" AS "market_area",
    fe."super_category" AS "super_category",
    fe."category" AS "category",
    fe."item_number" AS "item_number",
    fe."item_name" AS "item_name",
    fe."confidence_level" AS "confidence_level",
    SUM(fe."event_day_qty") AS "event_day_qty",
    SUM(fe."event_day_sales") AS "event_day_sales",
    AVG(fe."baseline_sales") AS "baseline_sales",
    SUM(fe."event_day_sales") - AVG(fe."baseline_sales") AS "sales_lift_value",
    CASE
        WHEN AVG(fe."baseline_sales") > 0
        THEN (SUM(fe."event_day_sales") - AVG(fe."baseline_sales")) / AVG(fe."baseline_sales") * 100
        ELSE NULL
    END AS "sales_lift_pct"
FROM "FACT_Event_Sales_Impact" fe
GROUP BY
    fe."event_id",
    fe."event_name",
    fe."event_type",
    fe."start_date",
    fe."end_date",
    fe."outlet_code",
    fe."outlet_name",
    fe."market_area",
    fe."super_category",
    fe."category",
    fe."item_number",
    fe."item_name",
    fe."confidence_level";
