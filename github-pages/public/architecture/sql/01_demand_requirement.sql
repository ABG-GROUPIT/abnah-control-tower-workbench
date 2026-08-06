/*
Query Table : QT_01_Demand_Requirement
Level       : 2
Depends on  : QT_01A_Menu_Forecast, REF_Item_Recipe,
              CTL_UOM_Conversions
Grain       : as_of_date + outlet_name + forecast_date
              + menu_item_code + ingredient_code

Purpose
-------
Expand the materialized menu forecast through the governed recipe and UOM
conversion. The expensive sales-history aggregation finishes in
QT_01A_Menu_Forecast before any recipe fan-out occurs.

Zoho compatibility
------------------
Exactly one non-recursive CTE aggregates duplicate recipe lines. The final
SELECT joins only the 68,649-row menu forecast, the 723-row recipe result and
the governed UOM conversion table. Every carried field is explicitly
republished at the final SELECT boundary for downstream Query Tables.
*/

WITH
Recipe_Lines AS
(
    SELECT
        R."Item Number" AS "menu_item_code",
        MAX(R."Item Name") AS "recipe_menu_item_name",
        R."Ingredient Code" AS "ingredient_code",
        MAX(R."Ingredient Name") AS "ingredient_name",
        R."Recipe Unit" AS "recipe_source_unit",
        SUM(R."Qty") AS "recipe_source_qty_per_menu_unit",
        MAX(R."Recipe Item Type") AS "recipe_item_type"
    FROM "REF_Item_Recipe" R
    WHERE R."Item Number" IS NOT NULL
      AND R."Ingredient Code" IS NOT NULL
    GROUP BY
        R."Item Number",
        R."Ingredient Code",
        R."Recipe Unit"
)
SELECT
    F."as_of_date" AS "as_of_date",
    F."forecast_date" AS "forecast_date",
    F."outlet_name" AS "outlet_name",
    F."menu_item_code" AS "menu_item_code",
    F."menu_item_name" AS "menu_item_name",
    R."ingredient_code" AS "ingredient_code",
    R."ingredient_name" AS "ingredient_name",
    R."recipe_item_type" AS "recipe_item_type",
    R."recipe_source_unit" AS "recipe_source_unit",
    CASE
        WHEN U."multiplier" IS NULL THEN NULL
        WHEN U."to_unit" IS NULL THEN NULL
        WHEN COALESCE(U."offset", 0) <> 0 THEN NULL
        WHEN U."conversion_status" IS NULL
          OR LOWER(U."conversion_status") NOT LIKE 'approved%'
        THEN NULL
        ELSE U."to_unit"
    END AS "canonical_uom",
    R."recipe_source_qty_per_menu_unit"
        AS "recipe_source_qty_per_menu_unit",
    CASE
        WHEN U."multiplier" IS NULL THEN NULL
        WHEN U."to_unit" IS NULL THEN NULL
        WHEN COALESCE(U."offset", 0) <> 0 THEN NULL
        WHEN U."conversion_status" IS NULL
          OR LOWER(U."conversion_status") NOT LIKE 'approved%'
        THEN NULL
        ELSE
            R."recipe_source_qty_per_menu_unit"
            * U."multiplier"
    END AS "recipe_qty_canonical_per_menu_unit",
    F."forecast_menu_qty_daily" AS "forecast_menu_qty_daily",
    CASE
        WHEN U."multiplier" IS NULL THEN NULL
        WHEN U."to_unit" IS NULL THEN NULL
        WHEN COALESCE(U."offset", 0) <> 0 THEN NULL
        WHEN U."conversion_status" IS NULL
          OR LOWER(U."conversion_status") NOT LIKE 'approved%'
        THEN NULL
        ELSE
            F."forecast_menu_qty_daily"
            * R."recipe_source_qty_per_menu_unit"
            * U."multiplier"
    END AS "forecast_ingredient_qty_daily",
    F."forecast_net_sales_daily" AS "forecast_net_sales_daily",
    F."forecast_method_code" AS "forecast_method_code",
    F."same_weekday_observation_count"
        AS "same_weekday_observation_count",
    F."fallback_observed_day_count" AS "fallback_observed_day_count",
    F."same_weekday_history_start_date"
        AS "same_weekday_history_start_date",
    F."same_weekday_history_end_date"
        AS "same_weekday_history_end_date",
    F."fallback_history_start_date" AS "fallback_history_start_date",
    F."fallback_history_end_date" AS "fallback_history_end_date",
    CASE
        WHEN U."multiplier" IS NULL THEN 'MISSING'
        WHEN U."to_unit" IS NULL THEN 'MISSING_TARGET_UOM'
        WHEN COALESCE(U."offset", 0) <> 0 THEN 'NONZERO_OFFSET_BLOCKED'
        WHEN U."conversion_status" IS NULL
          OR LOWER(U."conversion_status") NOT LIKE 'approved%'
        THEN 'UNAPPROVED'
        ELSE 'MAPPED'
    END AS "uom_mapping_status",
    F."forecast_history_weeks" AS "forecast_history_weeks",
    F."forecast_horizon_days" AS "forecast_horizon_days",
    F."forecast_min_same_weekday_obs"
        AS "forecast_min_same_weekday_obs",
    F."forecast_fallback_days" AS "forecast_fallback_days",
    'CT_FND_001|CT_FND_003' AS "formula_id",
    F."formula_version" AS "formula_version",
    'RAW_Bill_Item_Detail|REF_Item_Recipe|CTL_Calendar|CTL_UOM_Conversions|CTL_Rule_Parameters'
        AS "lineage_code"
FROM "QT_01A_Menu_Forecast" F
JOIN Recipe_Lines R
  ON R."menu_item_code" = F."menu_item_code"
JOIN "CTL_UOM_Conversions" U
  ON LOWER(TRIM(U."from_unit")) = LOWER(TRIM(R."recipe_source_unit"))
 AND U."effective_from" <= F."as_of_date"
 AND (
        U."effective_to" IS NULL
        OR U."effective_to" >= F."as_of_date"
     );
