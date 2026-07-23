-- Query Table: 11_std_ct_menu_forecast.sql
-- Logical model name: STD_CT_Menu_Forecast
-- Layer: standardized
-- Purpose: Standardize seven-day menu demand forecasts.
-- Sources: AUX_Menu_Demand_Forecast-Copy
-- Validate CAST/date function behavior once in the target Zoho workspace.
SELECT
    f."forecast_as_of_month" AS "source_period_code",
    CAST(f."forecast_date" AS DATE) AS "forecast_date",
    f."outlet_code" AS "outlet_code",
    f."outlet_name" AS "outlet_name",
    f."menu_item_code" AS "menu_item_code",
    f."menu_item_name" AS "menu_item_name",
    f."super_category_name" AS "super_category_name",
    f."category_name" AS "category_name",
    CAST(f."forecast_qty" AS DECIMAL(18,6)) AS "forecast_menu_qty",
    CAST(f."forecast_net_sales" AS DECIMAL(18,2)) AS "forecast_net_sales",
    f."model_name" AS "model_name",
    f."confidence_band" AS "confidence_band"
FROM "AUX_Menu_Demand_Forecast-Copy" f;
