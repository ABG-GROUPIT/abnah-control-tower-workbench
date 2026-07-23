-- Query Table: 26_fact_ct_forecast_ingredient_demand.sql
-- Logical model name: FACT_CT_Forecast_Ingredient_Demand
-- Layer: fact
-- Purpose: Convert menu demand forecast into ingredient requirements through the effective recipe.
-- Sources: 11_std_ct_menu_forecast.sql, 17_dim_ct_recipe_effective.sql
-- Validate CAST/date function behavior once in the target Zoho workspace.
SELECT
    f."source_period_code" AS "source_period_code",
    f."forecast_date" AS "forecast_date",
    f."outlet_code" AS "outlet_code",
    f."outlet_name" AS "outlet_name",
    f."menu_item_code" AS "menu_item_code",
    f."menu_item_name" AS "menu_item_name",
    r."ingredient_code" AS "item_code",
    r."ingredient_name" AS "item_name",
    r."canonical_uom" AS "canonical_uom",
    f."forecast_menu_qty" AS "forecast_menu_qty",
    r."canonical_recipe_qty" AS "canonical_recipe_qty",
    f."forecast_menu_qty" * r."canonical_recipe_qty" AS "forecast_ingredient_qty",
    f."forecast_net_sales" AS "forecast_net_sales"
FROM "11_std_ct_menu_forecast.sql" f
INNER JOIN "17_dim_ct_recipe_effective.sql" r
  ON f."menu_item_code" = r."menu_item_code";
