-- Query Table: ZIA_Theoretical_Demand_Daily
-- Purpose: Ask Zia-safe theoretical ingredient/material demand table.
-- Source: FACT_Theoretical_Consumption.
-- Grain: one row per outlet, date, menu item, ingredient/material.
-- Use for: recipe demand, packaging demand, ingredient demand trend.

SELECT
    t."sales_date" AS "business_date",
    YEAR(t."sales_date") AS "year_number",
    MONTH(t."sales_date") AS "month_number",
    CONCAT(YEAR(t."sales_date"), '-', LPAD(MONTH(t."sales_date"), 2, '0')) AS "month_key",
    t."outlet_code" AS "outlet_code",
    t."outlet_name" AS "outlet_name",
    t."market_area" AS "market_area",
    t."item_number" AS "menu_item_code",
    t."menu_item_name" AS "menu_item_name",
    t."super_category" AS "menu_super_category",
    t."category" AS "menu_category",
    t."ingredient_name" AS "material_name",
    t."ingredient_unit" AS "material_unit",
    t."item_tab_type" AS "bom_type",
    t."demand_component_type" AS "demand_component_type",
    t."sold_qty" AS "menu_units_sold",
    t."net_sale" AS "menu_net_sales",
    t."theoretical_ingredient_qty" AS "theoretical_demand_qty"
FROM "FACT_Theoretical_Consumption" t;
