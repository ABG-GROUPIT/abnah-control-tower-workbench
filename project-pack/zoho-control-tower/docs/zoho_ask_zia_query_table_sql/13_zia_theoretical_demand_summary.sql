-- Query Table: ZIA_Theoretical_Demand_Summary
-- Purpose: Ask Zia-safe loaded-period theoretical demand summary.
-- Source: FACT_Theoretical_Consumption.
-- Grain: one row per outlet, demand component type, material.
-- Use for: top recipe ingredients, top packaging materials, material demand story.

SELECT
    t."outlet_code" AS "outlet_code",
    t."outlet_name" AS "outlet_name",
    t."market_area" AS "market_area",
    t."demand_component_type" AS "demand_component_type",
    t."ingredient_name" AS "material_name",
    t."ingredient_unit" AS "material_unit",
    COUNT(DISTINCT t."menu_item_name") AS "menu_item_driver_count",
    COUNT(DISTINCT t."sales_date") AS "sales_dates_with_demand",
    SUM(t."sold_qty") AS "source_menu_units_sold",
    SUM(t."net_sale") AS "source_menu_net_sales",
    SUM(t."theoretical_ingredient_qty") AS "theoretical_demand_qty"
FROM "FACT_Theoretical_Consumption" t
GROUP BY
    t."outlet_code",
    t."outlet_name",
    t."market_area",
    t."demand_component_type",
    t."ingredient_name",
    t."ingredient_unit";
