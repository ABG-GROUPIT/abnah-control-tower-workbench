-- Query Table: 27_fact_ct_inventory_risk.sql
-- Logical model name: FACT_CT_Inventory_Risk
-- Layer: fact
-- Purpose: Calculate source-supported stockout and days-cover risk at ingredient checkpoint grain.
-- Sources: 05_std_ct_inventory_snapshot.sql, 26_fact_ct_forecast_ingredient_demand.sql, 22_fact_ct_purchase_order.sql
-- Validate CAST/date function behavior once in the target Zoho workspace.
SELECT
    s."source_period_code" AS "source_period_code",
    s."snapshot_date" AS "snapshot_date",
    s."outlet_code" AS "outlet_code",
    s."outlet_name" AS "outlet_name",
    s."item_code" AS "item_code",
    s."item_name" AS "item_name",
    s."category_name" AS "category_name",
    s."super_category_name" AS "super_category_name",
    s."canonical_uom" AS "canonical_uom",
    s."average_unit_cost" AS "average_unit_cost",
    s."closing_qty" AS "current_stock_qty",
    s."closing_value" AS "closing_value",
    COALESCE(f."forecast_required_qty", 0) AS "forecast_required_qty",
    COALESCE(f."forecast_required_qty", 0) * 1.15
      AS "required_qty_with_safety",
    COALESCE(p."valid_open_po_qty", 0) AS "valid_open_po_qty",
    COALESCE(p."valid_open_po_count", 0) AS "valid_open_po_count",
    COALESCE(p."open_po_value", 0) AS "open_po_value",
    CASE
        WHEN COALESCE(f."forecast_required_qty", 0) * 1.15
           > s."closing_qty" + COALESCE(p."valid_open_po_qty", 0)
        THEN COALESCE(f."forecast_required_qty", 0) * 1.15
           - s."closing_qty" - COALESCE(p."valid_open_po_qty", 0)
        ELSE 0
    END AS "shortage_qty",
    CASE
        WHEN COALESCE(f."forecast_required_qty", 0) > 0
        THEN (s."closing_qty" + COALESCE(p."valid_open_po_qty", 0))
           / (COALESCE(f."forecast_required_qty", 0) / 7)
        ELSE NULL
    END AS "days_cover",
    CASE
        WHEN s."closing_qty" <= 0
         AND COALESCE(f."forecast_required_qty", 0) > 0
        THEN 'PURPLE'
        WHEN COALESCE(f."forecast_required_qty", 0)
           > s."closing_qty" + COALESCE(p."valid_open_po_qty", 0)
        THEN 'RED'
        WHEN COALESCE(f."forecast_required_qty", 0) * 1.15
           > s."closing_qty" + COALESCE(p."valid_open_po_qty", 0)
        THEN 'AMBER'
        ELSE 'GREEN'
    END AS "stockout_risk_severity",
    CASE
        WHEN s."closing_qty" <= 0
         AND COALESCE(f."forecast_required_qty", 0) > 0
        THEN 'PURPLE'
        WHEN COALESCE(f."forecast_required_qty", 0)
           > s."closing_qty" + COALESCE(p."valid_open_po_qty", 0)
        THEN 'RED'
        WHEN COALESCE(f."forecast_required_qty", 0) * 1.15
           > s."closing_qty" + COALESCE(p."valid_open_po_qty", 0)
        THEN 'AMBER'
        ELSE 'GREEN'
    END AS "risk_severity",
    CASE
        WHEN s."closing_qty" <= 0
         AND COALESCE(f."forecast_required_qty", 0) > 0
        THEN 4
        WHEN COALESCE(f."forecast_required_qty", 0)
           > s."closing_qty" + COALESCE(p."valid_open_po_qty", 0)
        THEN 3
        WHEN COALESCE(f."forecast_required_qty", 0) * 1.15
           > s."closing_qty" + COALESCE(p."valid_open_po_qty", 0)
        THEN 2
        ELSE 1
    END AS "risk_severity_rank",
    CASE
        WHEN s."closing_qty" <= 0
         AND COALESCE(f."forecast_required_qty", 0) > 0
        THEN 'STOCKOUT'
        WHEN COALESCE(f."forecast_required_qty", 0) * 1.15
           > s."closing_qty" + COALESCE(p."valid_open_po_qty", 0)
        THEN 'STOCKOUT'
        ELSE 'HEALTHY'
    END AS "risk_type",
    CASE
        WHEN COALESCE(f."forecast_required_qty", 0) * 1.15
           > s."closing_qty" + COALESCE(p."valid_open_po_qty", 0)
        THEN (
            COALESCE(f."forecast_required_qty", 0) * 1.15
            - s."closing_qty" - COALESCE(p."valid_open_po_qty", 0)
        ) * s."average_unit_cost"
        ELSE 0
    END AS "shortage_cost_value",
    CASE
        WHEN COALESCE(f."forecast_required_qty", 0) * 1.15
           > s."closing_qty" + COALESCE(p."valid_open_po_qty", 0)
        THEN (
            COALESCE(f."forecast_required_qty", 0) * 1.15
            - s."closing_qty" - COALESCE(p."valid_open_po_qty", 0)
        ) * s."average_unit_cost"
        ELSE 0
    END AS "total_risk_value",
    NULL AS "criticality",
    NULL AS "primary_vendor",
    NULL AS "alternate_vendor",
    'vendor_item_approval_mapping_unavailable' AS "vendor_mapping_status",
    CONCAT(
        s."source_period_code", ':', s."outlet_code", ':', s."item_code"
    ) AS "action_id",
    CASE
        WHEN s."closing_qty" <= 0
         AND COALESCE(f."forecast_required_qty", 0) > 0
         AND COALESCE(p."valid_open_po_qty", 0) = 0
        THEN 'Raise purchase order'
        WHEN COALESCE(f."forecast_required_qty", 0) * 1.15
           > s."closing_qty" + COALESCE(p."valid_open_po_qty", 0)
         AND COALESCE(p."valid_open_po_qty", 0) > 0
        THEN 'Expedite existing PO'
        ELSE 'Monitor'
    END AS "recommended_action",
    CASE
        WHEN COALESCE(f."forecast_required_qty", 0) * 1.15
           > s."closing_qty" + COALESCE(p."valid_open_po_qty", 0)
        THEN 'Procurement'
        ELSE 'Supply Chain'
    END AS "action_owner",
    CASE
        WHEN s."closing_qty" <= 0
         AND COALESCE(f."forecast_required_qty", 0) > 0
        THEN 'Due today'
        WHEN COALESCE(f."forecast_required_qty", 0)
           > s."closing_qty" + COALESCE(p."valid_open_po_qty", 0)
        THEN 'Due today'
        WHEN COALESCE(f."forecast_required_qty", 0) * 1.15
           > s."closing_qty" + COALESCE(p."valid_open_po_qty", 0)
        THEN 'Due in 3 days'
        ELSE 'Monitor'
    END AS "due_band"
FROM "05_std_ct_inventory_snapshot.sql" s
LEFT JOIN (
    SELECT
        "source_period_code" AS "source_period_code",
        "outlet_code" AS "outlet_code",
        "item_code" AS "item_code",
        SUM("forecast_ingredient_qty") AS "forecast_required_qty"
    FROM "26_fact_ct_forecast_ingredient_demand.sql"
    GROUP BY "source_period_code", "outlet_code", "item_code"
) f
  ON s."source_period_code" = f."source_period_code"
 AND s."outlet_code" = f."outlet_code"
 AND s."item_code" = f."item_code"
LEFT JOIN (
    SELECT
        "source_period_code" AS "source_period_code",
        "outlet_code" AS "outlet_code",
        "item_code" AS "item_code",
        SUM("remaining_qty") AS "valid_open_po_qty",
        SUM("open_po_value") AS "open_po_value",
        COUNT(DISTINCT "po_number") AS "valid_open_po_count"
    FROM "22_fact_ct_purchase_order.sql"
    WHERE "is_open_po" = 1
    GROUP BY "source_period_code", "outlet_code", "item_code"
) p
  ON s."source_period_code" = p."source_period_code"
 AND s."outlet_code" = p."outlet_code"
 AND s."item_code" = p."item_code";
