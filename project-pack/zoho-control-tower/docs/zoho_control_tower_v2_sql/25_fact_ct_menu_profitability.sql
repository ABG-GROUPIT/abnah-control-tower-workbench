-- Query Table: 25_fact_ct_menu_profitability.sql
-- Logical model name: FACT_CT_Menu_Profitability
-- Layer: fact
-- Purpose: Aggregate menu sales, theoretical COGS and recipe gross margin.
-- Sources: 01_std_ct_sales_item.sql, 17_dim_ct_recipe_effective.sql
-- Validate CAST/date function behavior once in the target Zoho workspace.
SELECT
    s.*,
    COALESCE(c."theoretical_cost_per_menu_unit", 0)
      * s."sold_qty" AS "theoretical_cogs",
    s."net_sales"
      - COALESCE(c."theoretical_cost_per_menu_unit", 0)
      * s."sold_qty" AS "gross_margin_value",
    CASE
        WHEN s."net_sales" <> 0
        THEN (
          s."net_sales"
          - COALESCE(c."theoretical_cost_per_menu_unit", 0) * s."sold_qty"
        ) / s."net_sales" * 100
        ELSE NULL
    END AS "gross_margin_percent"
FROM (
    SELECT
        "source_period_code" AS "source_period_code",
        "outlet_code" AS "outlet_code",
        "outlet_name" AS "outlet_name",
        "item_code" AS "menu_item_code",
        "item_name" AS "menu_item_name",
        "super_category_name" AS "super_category_name",
        "category_name" AS "category_name",
        SUM("sold_qty") AS "sold_qty",
        SUM("net_sales") AS "net_sales",
        SUM("source_purchase_value") AS "source_reported_purchase_value"
    FROM "01_std_ct_sales_item.sql"
    GROUP BY
        "source_period_code",
        "outlet_code",
        "outlet_name",
        "item_code",
        "item_name",
        "super_category_name",
        "category_name"
) s
LEFT JOIN (
    SELECT
        "menu_item_code" AS "menu_item_code",
        SUM("ingredient_cost_per_menu_unit") AS "theoretical_cost_per_menu_unit"
    FROM "17_dim_ct_recipe_effective.sql"
    GROUP BY "menu_item_code"
) c
  ON s."menu_item_code" = c."menu_item_code";
