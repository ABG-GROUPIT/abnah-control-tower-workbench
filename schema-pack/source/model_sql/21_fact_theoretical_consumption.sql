-- Query Table: FACT_Theoretical_Consumption
-- Purpose: Estimate ingredient consumption from sales quantity multiplied by recipe BOM quantity.
-- Sources: FACT_Sales, STD_Recipe_BOM
-- Join key: FACT_Sales.item_name = STD_Recipe_BOM.recipe_name_filled
-- Caveat: This is theoretical consumption only, not full actual-vs-theoretical variance.

SELECT
    s."sales_row_id" AS "sales_row_id",
    s."sales_date" AS "sales_date",
    s."outlet_code" AS "outlet_code",
    s."outlet_name" AS "outlet_name",
    s."market_area" AS "market_area",
    s."item_number" AS "item_number",
    s."item_name" AS "menu_item_name",
    s."super_category" AS "super_category",
    s."category" AS "category",
    s."qty" AS "sold_qty",
    s."net_sale" AS "net_sale",
    b."bom_row_id" AS "bom_row_id",
    b."recipe_name_filled" AS "recipe_name_filled",
    b."recipe_qty_filled" AS "recipe_qty_filled",
    b."recipe_unit_filled" AS "recipe_unit_filled",
    b."ingredient_name" AS "ingredient_name",
    b."ingredient_qty" AS "ingredient_qty",
    b."ingredient_unit" AS "ingredient_unit",
    b."item_tab_type" AS "item_tab_type",
    CASE
        WHEN b."ingredient_name" IN (
            'Napkin',
            'Lid',
            'Straw',
            'Cold Cup',
            'Hot Cup',
            'Dessert Box',
            'Sandwich Box',
            'Wrap Packaging'
        ) THEN 'Packaging Consumable'
        ELSE 'Recipe Ingredient'
    END AS "demand_component_type",
    CASE
        WHEN b."recipe_qty_filled" IS NOT NULL
             AND b."recipe_qty_filled" <> 0
        THEN s."qty" * b."ingredient_qty" / b."recipe_qty_filled"
        ELSE s."qty" * b."ingredient_qty"
    END AS "theoretical_ingredient_qty"
FROM "FACT_Sales" s
INNER JOIN "STD_Recipe_BOM" b
    ON b."recipe_name_filled" = s."item_name";
