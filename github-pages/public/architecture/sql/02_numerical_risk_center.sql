/*
Query Table : QT_02_Numerical_Risk_Center
Level       : 3
Depends on  : QT_02A_Risk_Base_Evidence, QT_01A_Menu_Forecast,
              REF_Item_Recipe, CTL_UOM_Conversions, CTL_Snapshot_Status
Output grain: one numerical evidence row per as-of date and evaluation_id

Purpose
-------
Combine the consolidated base-risk helper with derived menu-impact evidence,
then calculate exact subject-level summary fields. The final column names,
grain, and semantics remain unchanged for Aggregate Formulas and reports.

Important
---------
Purple is emitted only by INV_STOCKOUT_PURPLE. Provisional expiry remains
visibly disclosed and cannot become Purple.

Zoho compatibility
------------------
Exactly three non-recursive CTEs are used. The subject summary is calculated by
a self-join in the main SELECT, avoiding a fourth CTE and forbidden CTE nesting.
All CTE and saved-table boundaries explicitly publish the evidence contract;
grouped menu keys use deterministic aggregates. The only V2 presentation
addition is a distinct impacted-ingredient list for the Menu Impact tooltip.
*/

WITH
menu_risk_daily AS
(
    SELECT
        r."as_of_date" AS "as_of_date",
        f."outlet_name" AS "outlet_name",
        f."forecast_date" AS "forecast_date",
        f."menu_item_code" AS "menu_item_code",
        MAX(f."menu_item_name") AS "menu_item_name",
        MIN(r."risk_priority_rank") AS "risk_priority_rank",
        MAX(r."risk_severity_level") AS "risk_severity_level",
        COUNT(DISTINCT r."item_code") AS "impacted_ingredient_count",
        GROUP_CONCAT(
            DISTINCT CONCAT(r."item_code", ' - ', r."item_name")
        ) AS "impacted_ingredient_list",
        MAX(f."forecast_menu_qty_daily") AS "forecast_menu_qty_daily",
        MAX(f."forecast_net_sales_daily") AS "forecast_net_sales_daily",
        MAX(r."breach_ratio") AS "max_breach_ratio",
        SUM(r."monetary_exposure") AS "ingredient_monetary_exposure",
        MAX(r."formula_version") AS "formula_version"
    FROM "QT_02A_Risk_Base_Evidence" r
    JOIN "QT_01A_Menu_Forecast" f
      ON f."as_of_date" = r."as_of_date"
     AND f."outlet_name" = r."outlet_name"
     AND DATEDIFF(f."forecast_date", r."as_of_date")
         BETWEEN 1 AND f."forecast_horizon_days"
    JOIN "REF_Item_Recipe" recipe
      ON recipe."Item Number" = f."menu_item_code"
     AND recipe."Ingredient Code" = r."item_code"
     AND recipe."Item Number" IS NOT NULL
     AND recipe."Ingredient Code" IS NOT NULL
    JOIN "CTL_UOM_Conversions" uom
      ON LOWER(TRIM(uom."from_unit"))
         = LOWER(TRIM(recipe."Recipe Unit"))
     AND uom."effective_from" <= f."as_of_date"
     AND (
            uom."effective_to" IS NULL
            OR uom."effective_to" >= f."as_of_date"
         )
    WHERE r."subject_type" = 'INVENTORY'
      AND r."risk_priority_rank" IN (1, 2, 3)
    GROUP BY
        r."as_of_date",
        f."outlet_name",
        f."forecast_date",
        f."menu_item_code"
),
menu_evidence AS
(
    SELECT
        m."as_of_date" AS "as_of_date",
        MAX(
            CONCAT(
                'MENU|',
                CAST(m."as_of_date" AS CHAR),
                '|',
                m."outlet_name",
                '|',
                m."menu_item_code"
            )
        ) AS "evaluation_id",
        MAX(
            CONCAT(
                'MENU|',
                m."outlet_name",
                '|',
                m."menu_item_code"
            )
        ) AS "subject_group_id",
        'MENU_IMPACT' AS "subject_type",
        m."outlet_name" AS "outlet_name",
        CAST(NULL AS CHAR) AS "store_name",
        m."menu_item_code" AS "item_code",
        MAX(m."menu_item_name") AS "item_name",
        CAST(NULL AS CHAR) AS "category_name",
        CAST(NULL AS CHAR) AS "super_category_name",
        CAST(NULL AS CHAR) AS "vendor_name",
        CAST(NULL AS CHAR) AS "po_number",
        CAST(NULL AS CHAR) AS "batch_number",
        CAST(NULL AS DATE) AS "expiry_date",
        CAST(NULL AS DECIMAL(18,6)) AS "batch_remaining_qty",
        CAST(NULL AS DECIMAL(18,6)) AS "total_item_stock_qty",
        CAST(NULL AS DECIMAL(18,6)) AS "expired_batch_qty",
        CAST(NULL AS DECIMAL(18,6)) AS "usable_nonexpired_qty",
        CAST(NULL AS DATE) AS "next_day_date",
        CAST(NULL AS DATE) AS "forecast_horizon_end_date",
        CAST(NULL AS DECIMAL(18,0)) AS "forecast_horizon_days",
        CAST(NULL AS CHAR) AS "source_unit",
        CAST(NULL AS CHAR) AS "canonical_uom",
        CASE
            WHEN MIN(m."risk_priority_rank") = 1 THEN 'INV_STOCKOUT_PURPLE'
            WHEN MIN(m."risk_priority_rank") = 2 THEN 'INV_SHORTAGE_RED'
            ELSE 'INV_SAFETY_AMBER'
        END AS "rule_id",
        SUM(m."forecast_menu_qty_daily") AS "actual_value",
        CAST(NULL AS DECIMAL(18,6)) AS "threshold_value",
        CAST(NULL AS DECIMAL(18,6)) AS "gap_value",
        MAX(m."max_breach_ratio") AS "breach_ratio",
        CASE
            WHEN MIN(m."risk_priority_rank") = 1 THEN 'Purple'
            WHEN MIN(m."risk_priority_rank") = 2 THEN 'Red'
            ELSE 'Amber'
        END AS "risk_color",
        MIN(m."risk_priority_rank") AS "risk_priority_rank",
        MAX(m."risk_severity_level") AS "risk_severity_level",
        CAST(NULL AS DECIMAL(18,6)) AS "current_stock_qty",
        CAST(NULL AS DECIMAL(18,2)) AS "current_stock_value",
        CAST(NULL AS DECIMAL(18,6)) AS "forecast_required_qty",
        CAST(NULL AS DECIMAL(18,6)) AS "next_day_required_qty",
        CAST(NULL AS DECIMAL(18,6)) AS "required_qty_with_safety",
        CAST(NULL AS DECIMAL(18,6)) AS "valid_open_po_qty",
        CAST(NULL AS DECIMAL(18,6)) AS "available_qty",
        CAST(NULL AS DECIMAL(18,6)) AS "shortage_qty",
        SUM(m."forecast_net_sales_daily") AS "monetary_exposure",
        CAST(NULL AS DECIMAL(18,2)) AS "next_day_requirement_value",
        CAST(NULL AS DECIMAL(18,6)) AS "next_day_shortage_qty",
        CAST(NULL AS DECIMAL(18,2)) AS "next_day_shortage_value",
        CAST(NULL AS DECIMAL(18,2)) AS "seven_day_requirement_value",
        1 AS "impacted_menu_item_count",
        MAX(m."impacted_ingredient_count") AS "impacted_ingredient_count",
        MAX(m."impacted_ingredient_list") AS "impacted_ingredient_list",
        CAST(NULL AS DECIMAL(18,0)) AS "days_to_expiry",
        CAST(NULL AS DECIMAL(18,0)) AS "po_overdue_days",
        m."as_of_date" AS "source_snapshot_date",
        'MODEL_DERIVED' AS "data_status",
        CAST(NULL AS CHAR) AS "source_disclosure",
        MAX(m."formula_version") AS "formula_version",
        CAST(NULL AS CHAR) AS "source_formula_version",
        'QT_01_Demand_Requirement;INVENTORY_RISK_BRANCH' AS "source_table",
        MAX(
            CONCAT(m."outlet_name", '|', m."menu_item_code")
        ) AS "source_row_key"
    FROM menu_risk_daily m
    GROUP BY
        m."as_of_date",
        m."outlet_name",
        m."menu_item_code"
),
evidence_union AS
(
    SELECT
        b."as_of_date" AS "as_of_date",
        b."evaluation_id" AS "evaluation_id",
        b."subject_group_id" AS "subject_group_id",
        b."subject_type" AS "subject_type",
        b."outlet_name" AS "outlet_name",
        b."store_name" AS "store_name",
        b."item_code" AS "item_code",
        b."item_name" AS "item_name",
        b."category_name" AS "category_name",
        b."super_category_name" AS "super_category_name",
        b."vendor_name" AS "vendor_name",
        b."po_number" AS "po_number",
        b."batch_number" AS "batch_number",
        b."expiry_date" AS "expiry_date",
        b."batch_remaining_qty" AS "batch_remaining_qty",
        b."total_item_stock_qty" AS "total_item_stock_qty",
        b."expired_batch_qty" AS "expired_batch_qty",
        b."usable_nonexpired_qty" AS "usable_nonexpired_qty",
        b."next_day_date" AS "next_day_date",
        b."forecast_horizon_end_date" AS "forecast_horizon_end_date",
        b."forecast_horizon_days" AS "forecast_horizon_days",
        b."source_unit" AS "source_unit",
        b."canonical_uom" AS "canonical_uom",
        b."rule_id" AS "rule_id",
        b."actual_value" AS "actual_value",
        b."threshold_value" AS "threshold_value",
        b."gap_value" AS "gap_value",
        b."breach_ratio" AS "breach_ratio",
        b."risk_color" AS "risk_color",
        b."risk_priority_rank" AS "risk_priority_rank",
        b."risk_severity_level" AS "risk_severity_level",
        b."current_stock_qty" AS "current_stock_qty",
        b."current_stock_value" AS "current_stock_value",
        b."forecast_required_qty" AS "forecast_required_qty",
        b."next_day_required_qty" AS "next_day_required_qty",
        b."required_qty_with_safety" AS "required_qty_with_safety",
        b."valid_open_po_qty" AS "valid_open_po_qty",
        b."available_qty" AS "available_qty",
        b."shortage_qty" AS "shortage_qty",
        b."monetary_exposure" AS "monetary_exposure",
        b."next_day_requirement_value" AS "next_day_requirement_value",
        b."next_day_shortage_qty" AS "next_day_shortage_qty",
        b."next_day_shortage_value" AS "next_day_shortage_value",
        b."seven_day_requirement_value" AS "seven_day_requirement_value",
        b."impacted_menu_item_count" AS "impacted_menu_item_count",
        b."impacted_ingredient_count" AS "impacted_ingredient_count",
        CAST(NULL AS CHAR) AS "impacted_ingredient_list",
        b."days_to_expiry" AS "days_to_expiry",
        b."po_overdue_days" AS "po_overdue_days",
        b."source_snapshot_date" AS "source_snapshot_date",
        b."data_status" AS "data_status",
        b."source_disclosure" AS "source_disclosure",
        b."formula_version" AS "formula_version",
        b."source_formula_version" AS "source_formula_version",
        b."source_table" AS "source_table",
        b."source_row_key" AS "source_row_key"
    FROM "QT_02A_Risk_Base_Evidence" b

    UNION ALL

    SELECT
        m."as_of_date" AS "as_of_date",
        m."evaluation_id" AS "evaluation_id",
        m."subject_group_id" AS "subject_group_id",
        m."subject_type" AS "subject_type",
        m."outlet_name" AS "outlet_name",
        m."store_name" AS "store_name",
        m."item_code" AS "item_code",
        m."item_name" AS "item_name",
        m."category_name" AS "category_name",
        m."super_category_name" AS "super_category_name",
        m."vendor_name" AS "vendor_name",
        m."po_number" AS "po_number",
        m."batch_number" AS "batch_number",
        m."expiry_date" AS "expiry_date",
        m."batch_remaining_qty" AS "batch_remaining_qty",
        m."total_item_stock_qty" AS "total_item_stock_qty",
        m."expired_batch_qty" AS "expired_batch_qty",
        m."usable_nonexpired_qty" AS "usable_nonexpired_qty",
        m."next_day_date" AS "next_day_date",
        m."forecast_horizon_end_date" AS "forecast_horizon_end_date",
        m."forecast_horizon_days" AS "forecast_horizon_days",
        m."source_unit" AS "source_unit",
        m."canonical_uom" AS "canonical_uom",
        m."rule_id" AS "rule_id",
        m."actual_value" AS "actual_value",
        m."threshold_value" AS "threshold_value",
        m."gap_value" AS "gap_value",
        m."breach_ratio" AS "breach_ratio",
        m."risk_color" AS "risk_color",
        m."risk_priority_rank" AS "risk_priority_rank",
        m."risk_severity_level" AS "risk_severity_level",
        m."current_stock_qty" AS "current_stock_qty",
        m."current_stock_value" AS "current_stock_value",
        m."forecast_required_qty" AS "forecast_required_qty",
        m."next_day_required_qty" AS "next_day_required_qty",
        m."required_qty_with_safety" AS "required_qty_with_safety",
        m."valid_open_po_qty" AS "valid_open_po_qty",
        m."available_qty" AS "available_qty",
        m."shortage_qty" AS "shortage_qty",
        m."monetary_exposure" AS "monetary_exposure",
        m."next_day_requirement_value" AS "next_day_requirement_value",
        m."next_day_shortage_qty" AS "next_day_shortage_qty",
        m."next_day_shortage_value" AS "next_day_shortage_value",
        m."seven_day_requirement_value" AS "seven_day_requirement_value",
        m."impacted_menu_item_count" AS "impacted_menu_item_count",
        m."impacted_ingredient_count" AS "impacted_ingredient_count",
        m."impacted_ingredient_list" AS "impacted_ingredient_list",
        m."days_to_expiry" AS "days_to_expiry",
        m."po_overdue_days" AS "po_overdue_days",
        m."source_snapshot_date" AS "source_snapshot_date",
        m."data_status" AS "data_status",
        m."source_disclosure" AS "source_disclosure",
        m."formula_version" AS "formula_version",
        m."source_formula_version" AS "source_formula_version",
        m."source_table" AS "source_table",
        m."source_row_key" AS "source_row_key"
    FROM menu_evidence m
)
SELECT
    e."as_of_date" AS "as_of_date",
    e."evaluation_id" AS "evaluation_id",
    e."subject_group_id" AS "subject_group_id",
    e."subject_type" AS "subject_type",
    e."outlet_name" AS "outlet_name",
    e."store_name" AS "store_name",
    e."item_code" AS "item_code",
    e."item_name" AS "item_name",
    e."category_name" AS "category_name",
    e."super_category_name" AS "super_category_name",
    e."vendor_name" AS "vendor_name",
    e."po_number" AS "po_number",
    e."batch_number" AS "batch_number",
    e."expiry_date" AS "expiry_date",
    e."batch_remaining_qty" AS "batch_remaining_qty",
    e."total_item_stock_qty" AS "total_item_stock_qty",
    e."expired_batch_qty" AS "expired_batch_qty",
    e."usable_nonexpired_qty" AS "usable_nonexpired_qty",
    e."next_day_date" AS "next_day_date",
    e."forecast_horizon_end_date" AS "forecast_horizon_end_date",
    e."forecast_horizon_days" AS "forecast_horizon_days",
    e."source_unit" AS "source_unit",
    e."canonical_uom" AS "canonical_uom",
    e."rule_id" AS "rule_id",
    e."actual_value" AS "actual_value",
    e."threshold_value" AS "threshold_value",
    e."gap_value" AS "gap_value",
    e."breach_ratio" AS "breach_ratio",
    e."risk_color" AS "risk_color",
    e."risk_priority_rank" AS "risk_priority_rank",
    e."risk_severity_level" AS "risk_severity_level",
    e."current_stock_qty" AS "current_stock_qty",
    e."current_stock_value" AS "current_stock_value",
    e."forecast_required_qty" AS "forecast_required_qty",
    e."next_day_required_qty" AS "next_day_required_qty",
    e."required_qty_with_safety" AS "required_qty_with_safety",
    e."valid_open_po_qty" AS "valid_open_po_qty",
    e."available_qty" AS "available_qty",
    e."shortage_qty" AS "shortage_qty",
    e."monetary_exposure" AS "monetary_exposure",
    e."next_day_requirement_value" AS "next_day_requirement_value",
    e."next_day_shortage_qty" AS "next_day_shortage_qty",
    e."next_day_shortage_value" AS "next_day_shortage_value",
    e."seven_day_requirement_value" AS "seven_day_requirement_value",
    e."impacted_menu_item_count" AS "impacted_menu_item_count",
    e."impacted_ingredient_count" AS "impacted_ingredient_count",
    e."impacted_ingredient_list" AS "impacted_ingredient_list",
    e."days_to_expiry" AS "days_to_expiry",
    e."po_overdue_days" AS "po_overdue_days",
    e."source_snapshot_date" AS "source_snapshot_date",
    e."data_status" AS "data_status",
    e."source_disclosure" AS "source_disclosure",
    e."formula_version" AS "formula_version",
    e."source_formula_version" AS "source_formula_version",
    e."source_table" AS "source_table",
    e."source_row_key" AS "source_row_key",
    e."subject_group_id" AS "subject_id",
    e."shortage_qty" AS "base_shortage_qty",
    MAX(
        CASE
            WHEN e."risk_priority_rank" IN (1, 2, 3) THEN 1
            ELSE 0
        END
    ) AS "breach_flag",
    COUNT(
        DISTINCT CASE
            WHEN s."risk_priority_rank" IN (1, 2, 3)
            THEN s."rule_id"
            ELSE NULL
        END
    ) AS "active_breach_count",
    CASE
        WHEN MIN(
                 CASE
                     WHEN s."risk_priority_rank" IN (1, 2, 3)
                     THEN s."risk_priority_rank"
                     ELSE 5
                 END
             ) <= 3
        THEN MIN(
                 CASE
                     WHEN s."risk_priority_rank" IN (1, 2, 3)
                     THEN s."risk_priority_rank"
                     ELSE 5
                 END
             )
        WHEN MAX(
                 CASE
                     WHEN s."risk_priority_rank" = 5 THEN 1
                     ELSE 0
                 END
             ) = 1
        THEN 5
        ELSE 4
    END AS "overall_priority_rank",
    CASE
        WHEN MAX(
                 CASE
                     WHEN s."risk_priority_rank" IN (1, 2, 3)
                     THEN s."risk_severity_level"
                     ELSE 0
                 END
             ) > 0
        THEN MAX(
                 CASE
                     WHEN s."risk_priority_rank" IN (1, 2, 3)
                     THEN s."risk_severity_level"
                     ELSE 0
                 END
             )
        WHEN MAX(
                 CASE
                     WHEN s."risk_priority_rank" = 5 THEN 1
                     ELSE 0
                 END
             ) = 1
        THEN 0
        ELSE 1
    END AS "overall_severity_level",
    MAX(
        CASE
            WHEN s."risk_priority_rank" IN (1, 2, 3)
            THEN s."breach_ratio"
            ELSE 0
        END
    ) AS "max_breach_ratio",
    CAST(ss."inventory_snapshot_date" AS DATE)
        AS "inventory_snapshot_date",
    ss."inventory_complete_flag" AS "inventory_complete_flag",
    ss."sales_complete_flag" AS "sales_complete_flag",
    ss."po_complete_flag" AS "po_complete_flag",
    ss."source_complete_flag" AS "source_complete_flag",
    ss."core_complete_flag" AS "core_complete_flag",
    ss."latest_valid_flag" AS "latest_valid_flag",
    ss."snapshot_selector" AS "snapshot_selector",
    ss."loaded_at" AS "snapshot_loaded_at",
    ss."load_id" AS "snapshot_load_id"
FROM evidence_union e
LEFT JOIN "CTL_Snapshot_Status" ss
  ON CAST(ss."evaluation_date" AS DATE) = e."as_of_date"
JOIN evidence_union s
  ON s."as_of_date" = e."as_of_date"
 AND s."subject_group_id" = e."subject_group_id"
GROUP BY
    e."as_of_date",
    e."evaluation_id",
    e."subject_group_id",
    e."subject_type",
    e."outlet_name",
    e."store_name",
    e."item_code",
    e."item_name",
    e."category_name",
    e."super_category_name",
    e."vendor_name",
    e."po_number",
    e."batch_number",
    e."expiry_date",
    e."batch_remaining_qty",
    e."total_item_stock_qty",
    e."expired_batch_qty",
    e."usable_nonexpired_qty",
    e."next_day_date",
    e."forecast_horizon_end_date",
    e."forecast_horizon_days",
    e."source_unit",
    e."canonical_uom",
    e."rule_id",
    e."actual_value",
    e."threshold_value",
    e."gap_value",
    e."breach_ratio",
    e."risk_color",
    e."risk_priority_rank",
    e."risk_severity_level",
    e."current_stock_qty",
    e."current_stock_value",
    e."forecast_required_qty",
    e."next_day_required_qty",
    e."required_qty_with_safety",
    e."valid_open_po_qty",
    e."available_qty",
    e."shortage_qty",
    e."monetary_exposure",
    e."next_day_requirement_value",
    e."next_day_shortage_qty",
    e."next_day_shortage_value",
    e."seven_day_requirement_value",
    e."impacted_menu_item_count",
    e."impacted_ingredient_count",
    e."impacted_ingredient_list",
    e."days_to_expiry",
    e."po_overdue_days",
    e."source_snapshot_date",
    e."data_status",
    e."source_disclosure",
    e."formula_version",
    e."source_formula_version",
    e."source_table",
    e."source_row_key",
    CAST(ss."inventory_snapshot_date" AS DATE),
    ss."inventory_complete_flag",
    ss."sales_complete_flag",
    ss."po_complete_flag",
    ss."source_complete_flag",
    ss."core_complete_flag",
    ss."latest_valid_flag",
    ss."snapshot_selector",
    ss."loaded_at",
    ss."load_id";
