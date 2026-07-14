-- Query Table: SUM_Event_Markers
-- Purpose: Spike explanation panel and dashboard annotation replacement.
-- Source: FACT_Event_Sales_Impact
-- Supplemental file: requested special handling includes SUM_Event_Markers.

SELECT
    fe."sales_date" AS "event_date",
    fe."outlet_code" AS "outlet_code",
    fe."outlet_name" AS "outlet_name",
    fe."market_area" AS "market_area",
    fe."event_id" AS "event_id",
    fe."event_name" AS "event_name",
    fe."event_type" AS "event_type",
    fe."affected_category" AS "affected_category",
    fe."affected_items" AS "affected_items",
    SUM(fe."event_day_sales") AS "event_day_sales",
    AVG(fe."baseline_sales") AS "baseline_sales",
    CASE
        WHEN AVG(fe."baseline_sales") > 0
        THEN (SUM(fe."event_day_sales") - AVG(fe."baseline_sales")) / AVG(fe."baseline_sales") * 100
        ELSE NULL
    END AS "sales_lift_percentage",
    fe."confidence_level" AS "confidence_level"
FROM "FACT_Event_Sales_Impact" fe
GROUP BY
    fe."sales_date",
    fe."outlet_code",
    fe."outlet_name",
    fe."market_area",
    fe."event_id",
    fe."event_name",
    fe."event_type",
    fe."affected_category",
    fe."affected_items",
    fe."confidence_level";
