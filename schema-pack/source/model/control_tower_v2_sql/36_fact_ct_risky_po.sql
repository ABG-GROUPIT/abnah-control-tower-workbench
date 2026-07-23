-- Query Table: 36_fact_ct_risky_po.sql
-- Logical model name: FACT_CT_Risky_PO
-- Layer: fact
-- Purpose: Retain exact open PO lines whose ingredients are currently red, purple or amber.
-- Sources: 05_std_ct_inventory_snapshot.sql, 26_fact_ct_forecast_ingredient_demand.sql, 22_fact_ct_purchase_order.sql
-- Validate CAST/date function behavior once in the target Zoho workspace.
WITH forecast_item AS (
    SELECT
        "source_period_code" AS "source_period_code",
        "outlet_code" AS "outlet_code",
        "item_code" AS "item_code",
        SUM("forecast_ingredient_qty") AS "forecast_required_qty"
    FROM "26_fact_ct_forecast_ingredient_demand.sql"
    GROUP BY "source_period_code", "outlet_code", "item_code"
),
open_po AS (
    SELECT
        "source_period_code" AS "source_period_code",
        "outlet_code" AS "outlet_code",
        "item_code" AS "item_code",
        SUM("remaining_qty") AS "valid_open_po_qty"
    FROM "22_fact_ct_purchase_order.sql"
    WHERE "is_open_po" = 1
    GROUP BY "source_period_code", "outlet_code", "item_code"
),
risk_item AS (
    SELECT
        s."source_period_code" AS "source_period_code",
        s."outlet_code" AS "outlet_code",
        s."item_code" AS "item_code",
        CASE
            WHEN s."closing_qty" <= 0
             AND COALESCE(f."forecast_required_qty", 0) > 0
            THEN 'PURPLE'
            WHEN COALESCE(f."forecast_required_qty", 0)
               > s."closing_qty" + COALESCE(o."valid_open_po_qty", 0)
            THEN 'RED'
            WHEN COALESCE(f."forecast_required_qty", 0) * 1.15
               > s."closing_qty" + COALESCE(o."valid_open_po_qty", 0)
            THEN 'AMBER'
            ELSE 'GREEN'
        END AS "risk_severity"
    FROM "05_std_ct_inventory_snapshot.sql" s
    LEFT JOIN forecast_item f
      ON s."source_period_code" = f."source_period_code"
     AND s."outlet_code" = f."outlet_code"
     AND s."item_code" = f."item_code"
    LEFT JOIN open_po o
      ON s."source_period_code" = o."source_period_code"
     AND s."outlet_code" = o."outlet_code"
     AND s."item_code" = o."item_code"
)
SELECT
    p.*,
    r."risk_severity" AS "risk_severity"
FROM "22_fact_ct_purchase_order.sql" p
INNER JOIN risk_item r
  ON p."source_period_code" = r."source_period_code"
 AND p."outlet_code" = r."outlet_code"
 AND p."item_code" = r."item_code"
WHERE p."is_open_po" = 1
  AND r."risk_severity" <> 'GREEN';
