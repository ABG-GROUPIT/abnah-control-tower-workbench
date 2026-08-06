/*
Query Table : QT_01A_Menu_Forecast
Level       : 1
Depends on  : RAW_Bill_Item_Detail, CTL_Calendar, CTL_Rule_Parameters
Grain       : as_of_date + outlet_name + forecast_date + menu_item_code

Performance purpose
-------------------
Finish the historical daily-menu aggregation before recipe expansion.  The
previous single-table design joined every history date to every recipe line
before grouping, which multiplied the expensive portion of the query.

Zoho compatibility
------------------
Exactly three non-recursive CTEs are used.  No Query Table input, correlated
subquery, PIVOT, or cartesian join is used.  Fields passed from Forecast_Stats
to the final SELECT keep explicit same-name aliases so Zoho publishes the CTE
columns reliably.
*/

WITH
Daily_Sales AS
(
    SELECT
        date(S."Close Time") AS "business_date",
        S."Deployment" AS "outlet_name",
        S."Item Number" AS "menu_item_code",
        MAX(S."Item Name") AS "menu_item_name",
        SUM(S."Qty") AS "net_sold_menu_qty",
        SUM(S."Amount" - COALESCE(S."Discount", 0)) AS "net_sales_amount"
    FROM "RAW_Bill_Item_Detail" S
    WHERE S."Close Time" IS NOT NULL
      AND S."Deployment" IS NOT NULL
      AND S."Item Number" IS NOT NULL
    GROUP BY
        date(S."Close Time"),
        S."Deployment",
        S."Item Number"
),
params AS
(
    SELECT
        P0."scope" AS "scope",
        P0."effective_from" AS "effective_from",
        P0."effective_to" AS "effective_to",
        MAX(
            CASE WHEN P0."parameter_id" = 'forecast_history_weeks'
                 THEN P0."parameter_value_numeric" ELSE NULL END
        ) AS "forecast_history_weeks",
        MAX(
            CASE WHEN P0."parameter_id" = 'forecast_horizon_days'
                 THEN P0."parameter_value_numeric" ELSE NULL END
        ) AS "forecast_horizon_days",
        MAX(
            CASE WHEN P0."parameter_id" = 'forecast_min_same_weekday_obs'
                 THEN P0."parameter_value_numeric" ELSE NULL END
        ) AS "forecast_min_same_weekday_obs",
        MAX(
            CASE WHEN P0."parameter_id" = 'forecast_fallback_days'
                 THEN P0."parameter_value_numeric" ELSE NULL END
        ) AS "forecast_fallback_days",
        MAX(P0."formula_version") AS "formula_version"
    FROM "CTL_Rule_Parameters" P0
    WHERE P0."active_flag" = 1
      AND P0."parameter_id" IN
          (
              'forecast_history_weeks',
              'forecast_horizon_days',
              'forecast_min_same_weekday_obs',
              'forecast_fallback_days'
          )
    GROUP BY
        P0."scope",
        P0."effective_from",
        P0."effective_to"
),
Forecast_Stats AS
(
    SELECT
        A."calendar_date" AS "as_of_date",
        F."calendar_date" AS "forecast_date",
        M."outlet_name" AS "outlet_name",
        M."menu_item_code" AS "menu_item_code",
        M."menu_item_name" AS "menu_item_name",
        SUM(
            CASE
                WHEN H."day_of_week_number" = F."day_of_week_number"
                 AND H."calendar_date" >= adddate(
                        F."calendar_date",
                        -7 * P."forecast_history_weeks"
                     )
                 AND H."calendar_date" <= adddate(F."calendar_date", -7)
                THEN 1 ELSE 0
            END
        ) AS "same_weekday_observation_count",
        SUM(
            CASE
                WHEN H."day_of_week_number" = F."day_of_week_number"
                 AND H."calendar_date" >= adddate(
                        F."calendar_date",
                        -7 * P."forecast_history_weeks"
                     )
                 AND H."calendar_date" <= adddate(F."calendar_date", -7)
                THEN COALESCE(D."net_sold_menu_qty", 0)
                ELSE 0
            END
        ) AS "same_weekday_qty_sum",
        SUM(
            CASE
                WHEN H."day_of_week_number" = F."day_of_week_number"
                 AND H."calendar_date" >= adddate(
                        F."calendar_date",
                        -7 * P."forecast_history_weeks"
                     )
                 AND H."calendar_date" <= adddate(F."calendar_date", -7)
                THEN COALESCE(D."net_sales_amount", 0)
                ELSE 0
            END
        ) AS "same_weekday_sales_sum",
        SUM(
            CASE
                WHEN H."calendar_date" >= adddate(
                        A."calendar_date",
                        1 - P."forecast_fallback_days"
                     )
                 AND H."calendar_date" <= A."calendar_date"
                THEN 1 ELSE 0
            END
        ) AS "fallback_observed_day_count",
        SUM(
            CASE
                WHEN H."calendar_date" >= adddate(
                        A."calendar_date",
                        1 - P."forecast_fallback_days"
                     )
                 AND H."calendar_date" <= A."calendar_date"
                THEN COALESCE(D."net_sold_menu_qty", 0)
                ELSE 0
            END
        ) AS "fallback_qty_sum",
        SUM(
            CASE
                WHEN H."calendar_date" >= adddate(
                        A."calendar_date",
                        1 - P."forecast_fallback_days"
                     )
                 AND H."calendar_date" <= A."calendar_date"
                THEN COALESCE(D."net_sales_amount", 0)
                ELSE 0
            END
        ) AS "fallback_sales_sum",
        P."forecast_history_weeks" AS "forecast_history_weeks",
        P."forecast_horizon_days" AS "forecast_horizon_days",
        P."forecast_min_same_weekday_obs"
            AS "forecast_min_same_weekday_obs",
        P."forecast_fallback_days" AS "forecast_fallback_days",
        P."formula_version" AS "formula_version"
    FROM Daily_Sales M
    LEFT JOIN Daily_Sales Earlier
      ON Earlier."outlet_name" = M."outlet_name"
     AND Earlier."menu_item_code" = M."menu_item_code"
     AND Earlier."business_date" < M."business_date"
    JOIN params P
      ON P."scope" = 'global'
    JOIN "CTL_Calendar" A
      ON A."calendar_date" >= P."effective_from"
     AND (P."effective_to" IS NULL
          OR A."calendar_date" <= P."effective_to")
     AND A."is_demo_operational_date" = 1
     AND M."business_date" <= A."calendar_date"
    JOIN "CTL_Calendar" F
      ON F."calendar_date" > A."calendar_date"
     AND F."calendar_date" <= adddate(
            A."calendar_date",
            P."forecast_horizon_days"
         )
    LEFT JOIN "CTL_Calendar" H
      ON H."calendar_date" <= A."calendar_date"
     AND H."calendar_date" >= adddate(
            A."calendar_date",
            -1 * (
                7 * P."forecast_history_weeks"
                + P."forecast_fallback_days"
            )
         )
     AND H."is_demo_operational_date" = 1
    LEFT JOIN Daily_Sales D
      ON D."business_date" = H."calendar_date"
     AND D."outlet_name" = M."outlet_name"
     AND D."menu_item_code" = M."menu_item_code"
    WHERE Earlier."menu_item_code" IS NULL
      AND P."forecast_history_weeks" IS NOT NULL
      AND P."forecast_horizon_days" IS NOT NULL
      AND P."forecast_min_same_weekday_obs" IS NOT NULL
      AND P."forecast_fallback_days" IS NOT NULL
    GROUP BY
        A."calendar_date",
        F."calendar_date",
        F."day_of_week_number",
        M."outlet_name",
        M."menu_item_code",
        M."menu_item_name",
        P."forecast_history_weeks",
        P."forecast_horizon_days",
        P."forecast_min_same_weekday_obs",
        P."forecast_fallback_days",
        P."formula_version"
)
SELECT
    S."as_of_date" AS "as_of_date",
    S."forecast_date" AS "forecast_date",
    S."outlet_name" AS "outlet_name",
    S."menu_item_code" AS "menu_item_code",
    S."menu_item_name" AS "menu_item_name",
    CASE
        WHEN S."same_weekday_observation_count"
             >= S."forecast_min_same_weekday_obs"
        THEN
            CASE
                WHEN S."same_weekday_qty_sum"
                     / S."same_weekday_observation_count" < 0
                THEN 0
                ELSE S."same_weekday_qty_sum"
                     / S."same_weekday_observation_count"
            END
        WHEN S."fallback_observed_day_count" > 0
        THEN
            CASE
                WHEN S."fallback_qty_sum"
                     / S."fallback_observed_day_count" < 0
                THEN 0
                ELSE S."fallback_qty_sum"
                     / S."fallback_observed_day_count"
            END
        ELSE NULL
    END AS "forecast_menu_qty_daily",
    CASE
        WHEN S."same_weekday_observation_count"
             >= S."forecast_min_same_weekday_obs"
        THEN
            CASE
                WHEN S."same_weekday_sales_sum"
                     / S."same_weekday_observation_count" < 0
                THEN 0
                ELSE S."same_weekday_sales_sum"
                     / S."same_weekday_observation_count"
            END
        WHEN S."fallback_observed_day_count" > 0
        THEN
            CASE
                WHEN S."fallback_sales_sum"
                     / S."fallback_observed_day_count" < 0
                THEN 0
                ELSE S."fallback_sales_sum"
                     / S."fallback_observed_day_count"
            END
        ELSE NULL
    END AS "forecast_net_sales_daily",
    CASE
        WHEN S."same_weekday_observation_count"
             >= S."forecast_min_same_weekday_obs"
        THEN 'SAME_WEEKDAY_AVG'
        WHEN S."fallback_observed_day_count" > 0
        THEN 'TRAILING_DAILY_FALLBACK'
        ELSE 'NO_OBSERVED_HISTORY'
    END AS "forecast_method_code",
    S."same_weekday_observation_count"
        AS "same_weekday_observation_count",
    S."fallback_observed_day_count" AS "fallback_observed_day_count",
    adddate(
        S."forecast_date",
        -7 * S."forecast_history_weeks"
    ) AS "same_weekday_history_start_date",
    adddate(S."forecast_date", -7) AS "same_weekday_history_end_date",
    adddate(
        S."as_of_date",
        1 - S."forecast_fallback_days"
    ) AS "fallback_history_start_date",
    S."as_of_date" AS "fallback_history_end_date",
    S."forecast_history_weeks" AS "forecast_history_weeks",
    S."forecast_horizon_days" AS "forecast_horizon_days",
    S."forecast_min_same_weekday_obs"
        AS "forecast_min_same_weekday_obs",
    S."forecast_fallback_days" AS "forecast_fallback_days",
    'CT_FND_001' AS "formula_id",
    S."formula_version" AS "formula_version",
    'RAW_Bill_Item_Detail|CTL_Calendar|CTL_Rule_Parameters'
        AS "lineage_code"
FROM Forecast_Stats S;
