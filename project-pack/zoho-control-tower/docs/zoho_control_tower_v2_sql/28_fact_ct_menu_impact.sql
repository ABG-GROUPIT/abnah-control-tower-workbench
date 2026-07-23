-- Query Table: 28_fact_ct_menu_impact.sql
-- Logical model name: FACT_CT_Menu_Impact
-- Layer: fact
-- Purpose: Connect risky ingredients back to forecast menu items and revenue at risk.
-- Sources: 05_std_ct_inventory_snapshot.sql, 26_fact_ct_forecast_ingredient_demand.sql, 22_fact_ct_purchase_order.sql
-- Validate CAST/date function behavior once in the target Zoho workspace.
WITH forecast_menu AS (
    SELECT
        "source_period_code" AS "source_period_code",
        "outlet_code" AS "outlet_code",
        "outlet_name" AS "outlet_name",
        "menu_item_code" AS "menu_item_code",
        "menu_item_name" AS "menu_item_name",
        "item_code" AS "item_code",
        "item_name" AS "item_name",
        SUM("forecast_menu_qty") AS "forecast_menu_qty",
        SUM("forecast_ingredient_qty") AS "forecast_ingredient_qty",
        SUM("forecast_net_sales") AS "forecast_net_sales"
    FROM "26_fact_ct_forecast_ingredient_demand.sql"
    GROUP BY
        "source_period_code",
        "outlet_code",
        "outlet_name",
        "menu_item_code",
        "menu_item_name",
        "item_code",
        "item_name"
),
po_open AS (
    SELECT
        "source_period_code" AS "source_period_code",
        "outlet_code" AS "outlet_code",
        "item_code" AS "item_code",
        SUM("remaining_qty") AS "valid_open_po_qty"
    FROM "22_fact_ct_purchase_order.sql"
    WHERE "is_open_po" = 1
    GROUP BY "source_period_code", "outlet_code", "item_code"
),
risk_count AS (
    SELECT
        f."source_period_code" AS "source_period_code",
        f."outlet_code" AS "outlet_code",
        f."menu_item_code" AS "menu_item_code",
        COUNT(DISTINCT f."item_code") AS "risk_ingredient_count"
    FROM forecast_menu f
    INNER JOIN "05_std_ct_inventory_snapshot.sql" s
      ON f."source_period_code" = s."source_period_code"
     AND f."outlet_code" = s."outlet_code"
     AND f."item_code" = s."item_code"
    LEFT JOIN po_open p
      ON f."source_period_code" = p."source_period_code"
     AND f."outlet_code" = p."outlet_code"
     AND f."item_code" = p."item_code"
    WHERE (
        s."closing_qty" <= 0
        AND f."forecast_ingredient_qty" > 0
    )
       OR f."forecast_ingredient_qty" * 1.15
          > s."closing_qty" + COALESCE(p."valid_open_po_qty", 0)
    GROUP BY f."source_period_code", f."outlet_code", f."menu_item_code"
)
SELECT
    f."source_period_code" AS "source_period_code",
    f."outlet_code" AS "outlet_code",
    f."outlet_name" AS "outlet_name",
    f."item_code" AS "ingredient_code",
    f."item_name" AS "ingredient_name",
    CASE
        WHEN s."closing_qty" <= 0 AND f."forecast_ingredient_qty" > 0
        THEN 'PURPLE'
        WHEN f."forecast_ingredient_qty"
           > s."closing_qty" + COALESCE(p."valid_open_po_qty", 0)
        THEN 'RED'
        WHEN f."forecast_ingredient_qty" * 1.15
           > s."closing_qty" + COALESCE(p."valid_open_po_qty", 0)
        THEN 'AMBER'
        ELSE 'GREEN'
    END AS "risk_severity",
    CASE
        WHEN f."forecast_ingredient_qty" * 1.15
           > s."closing_qty" + COALESCE(p."valid_open_po_qty", 0)
        THEN f."forecast_ingredient_qty" * 1.15
           - s."closing_qty" - COALESCE(p."valid_open_po_qty", 0)
        ELSE 0
    END AS "shortage_qty",
    f."menu_item_code" AS "menu_item_code",
    f."menu_item_name" AS "menu_item_name",
    f."forecast_menu_qty" AS "forecast_menu_qty",
    f."forecast_net_sales" AS "forecast_net_sales_at_risk",
    c."risk_ingredient_count" AS "risk_ingredient_count",
    f."forecast_net_sales" / c."risk_ingredient_count"
      AS "allocated_forecast_net_sales_at_risk"
FROM forecast_menu f
INNER JOIN "05_std_ct_inventory_snapshot.sql" s
  ON f."source_period_code" = s."source_period_code"
 AND f."outlet_code" = s."outlet_code"
 AND f."item_code" = s."item_code"
LEFT JOIN po_open p
  ON f."source_period_code" = p."source_period_code"
 AND f."outlet_code" = p."outlet_code"
 AND f."item_code" = p."item_code"
INNER JOIN risk_count c
  ON f."source_period_code" = c."source_period_code"
 AND f."outlet_code" = c."outlet_code"
 AND f."menu_item_code" = c."menu_item_code"
WHERE (
    s."closing_qty" <= 0
    AND f."forecast_ingredient_qty" > 0
)
   OR f."forecast_ingredient_qty" * 1.15
      > s."closing_qty" + COALESCE(p."valid_open_po_qty", 0);
