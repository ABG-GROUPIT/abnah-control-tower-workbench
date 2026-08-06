/*
Query Table : QT_02A_Risk_Base_Evidence
Level       : 2
Depends on  : QT_01A_Menu_Forecast, REF_Item_Recipe,
              CTL_UOM_Conversions, RAW_Closing_Stock,
              RAW_Enterprise_Purchase_Order,
              SYN_Provisional_Expiry_Report, CTL_Calendar,
              CTL_Rule_Parameters
Grain       : as_of_date + evaluation_id

Purpose
-------
Materialize the three base numerical-risk evidence domains in one lean helper:
inventory coverage, provisional expiry, and open-PO timing. Recipe quantities
are converted directly from the raw recipe and governed UOM tables, removing
the need for a separate recipe Query Table.

Important
---------
Purple is emitted only by the inventory stockout rule. Provisional expiry is
visibly disclosed, never Purple, and incomplete evidence remains Grey.
Inventory evidence uses an exact Closing Stock date match. Missing snapshots
remain missing and are governed by CTL_Snapshot_Status in the public tables;
the query never silently carries an older stock row into a newer as-of date.

Zoho compatibility
------------------
Exactly three non-recursive CTEs are used. No CTE contains a subquery. The
three evidence branches are combined with UNION ALL in the main expression.
All passthrough fields used across CTE or saved-table boundaries keep explicit
same-name aliases for Zoho column-metadata stability.
*/

WITH
params AS
(
    SELECT
        MAX(CASE WHEN "parameter_id" = 'forecast_horizon_days'
                 AND "active_flag" = 1
                 THEN "parameter_value_numeric" END)
            AS "forecast_horizon_days",
        MAX(CASE WHEN "parameter_id" = 'inventory_safety_factor'
                 AND "active_flag" = 1
                 THEN "parameter_value_numeric" END)
            AS "inventory_safety_factor",
        MAX(CASE WHEN "parameter_id" = 'expiry_red_days'
                 AND "active_flag" = 1
                 THEN "parameter_value_numeric" END)
            AS "expiry_red_days",
        MAX(CASE WHEN "parameter_id" = 'expiry_amber_days'
                 AND "active_flag" = 1
                 THEN "parameter_value_numeric" END)
            AS "expiry_amber_days",
        MAX(CASE WHEN "parameter_id" = 'po_due_amber_days'
                 AND "active_flag" = 1
                 THEN "parameter_value_numeric" END)
            AS "po_due_amber_days",
        MAX(CASE WHEN "parameter_id" = 'po_overdue_red_days'
                 AND "active_flag" = 1
                 THEN "parameter_value_numeric" END)
            AS "po_overdue_red_days",
        MAX(CASE WHEN "parameter_id" = 'epsilon_qty'
                 AND "active_flag" = 1
                 THEN "parameter_value_numeric" END)
            AS "epsilon_qty",
        MAX(CASE WHEN "active_flag" = 1 THEN "formula_version" END)
            AS "formula_version"
    FROM "CTL_Rule_Parameters"
),
demand_by_item AS
(
    SELECT
        CAST(C."calendar_date" AS DATE) AS "as_of_date",
        F."outlet_name" AS "outlet_name",
        R."Ingredient Code" AS "item_code",
        MAX(R."Ingredient Name") AS "item_name",
        MAX(
            CASE
                WHEN U."multiplier" IS NULL
                  OR U."to_unit" IS NULL
                  OR COALESCE(U."offset", 0) <> 0
                  OR U."conversion_status" IS NULL
                  OR LOWER(U."conversion_status") NOT LIKE 'approved%'
                THEN NULL
                ELSE U."to_unit"
            END
        ) AS "canonical_uom",
        SUM(
            CASE
                WHEN U."multiplier" IS NULL
                  OR U."to_unit" IS NULL
                  OR COALESCE(U."offset", 0) <> 0
                  OR U."conversion_status" IS NULL
                  OR LOWER(U."conversion_status") NOT LIKE 'approved%'
                THEN NULL
                ELSE F."forecast_menu_qty_daily"
                     * R."Qty"
                     * U."multiplier"
            END
        ) AS "required_qty",
        SUM(
            CASE
                WHEN DATEDIFF(
                         F."forecast_date",
                         CAST(C."calendar_date" AS DATE)
                     ) <> 1
                THEN 0
                WHEN U."multiplier" IS NULL
                  OR U."to_unit" IS NULL
                  OR COALESCE(U."offset", 0) <> 0
                  OR U."conversion_status" IS NULL
                  OR LOWER(U."conversion_status") NOT LIKE 'approved%'
                THEN NULL
                ELSE F."forecast_menu_qty_daily"
                     * R."Qty"
                     * U."multiplier"
            END
        ) AS "next_day_required_qty",
        COUNT(DISTINCT F."menu_item_code")
            AS "impacted_menu_item_count",
        SUM(F."forecast_menu_qty_daily")
            AS "ingredient_linked_menu_qty",
        SUM(F."forecast_net_sales_daily")
            AS "ingredient_linked_forecast_sales",
        MIN(
            CASE
                WHEN U."multiplier" IS NULL THEN 'MISSING'
                WHEN U."to_unit" IS NULL THEN 'MISSING_TARGET_UOM'
                WHEN COALESCE(U."offset", 0) <> 0
                THEN 'NONZERO_OFFSET_BLOCKED'
                WHEN U."conversion_status" IS NULL
                  OR LOWER(U."conversion_status") NOT LIKE 'approved%'
                THEN 'UNAPPROVED'
                ELSE 'MAPPED'
            END
        ) AS "uom_mapping_status"
    FROM "CTL_Calendar" C
    CROSS JOIN params P
    JOIN "QT_01A_Menu_Forecast" F
      ON F."as_of_date" = CAST(C."calendar_date" AS DATE)
     AND DATEDIFF(
            F."forecast_date",
            CAST(C."calendar_date" AS DATE)
         ) BETWEEN 1 AND P."forecast_horizon_days"
    JOIN "REF_Item_Recipe" R
      ON R."Item Number" = F."menu_item_code"
     AND R."Item Number" IS NOT NULL
     AND R."Ingredient Code" IS NOT NULL
    JOIN "CTL_UOM_Conversions" U
      ON LOWER(TRIM(U."from_unit")) = LOWER(TRIM(R."Recipe Unit"))
     AND U."effective_from" <= F."as_of_date"
     AND (
            U."effective_to" IS NULL
            OR U."effective_to" >= F."as_of_date"
         )
    WHERE C."is_demo_operational_date" = 1
    GROUP BY
        CAST(C."calendar_date" AS DATE),
        F."outlet_name",
        R."Ingredient Code"
),
inventory_base AS
(
    SELECT
        CAST(C."calendar_date" AS DATE) AS "as_of_date",
        S."Deployment" AS "outlet_name",
        'SOURCE_TOTAL' AS "store_name",
        S."Item Code" AS "item_code",
        S."Item Name" AS "item_name",
        S."Category Name" AS "category_name",
        S."Super Category Name" AS "super_category_name",
        S."Unit Name" AS "stock_source_unit",
        MAX(D."canonical_uom") AS "canonical_uom",
        CAST(S."Total Qty" AS DECIMAL(18,6)) AS "current_stock_qty",
        CAST(S."Average Price" AS DECIMAL(18,6)) AS "average_unit_cost",
        CAST(S."Total Amt" AS DECIMAL(18,2)) AS "source_stock_value",
        CAST(S."Date" AS DATE) AS "stock_snapshot_date",
        MAX(D."required_qty") AS "required_qty",
        MAX(D."next_day_required_qty") AS "next_day_required_qty",
        CASE
            WHEN MAX(D."required_qty") IS NULL
              OR MAX(P."inventory_safety_factor") IS NULL
            THEN NULL
            ELSE
                MAX(D."required_qty")
                * MAX(P."inventory_safety_factor")
        END AS "required_qty_with_safety",
        COALESCE(
            SUM(
                CASE
                    WHEN COALESCE(TRIM(PO."Expected Delivery"), '') <> ''
                     AND DATEDIFF(
                            CAST(
                                NULLIF(TRIM(PO."Expected Delivery"), '')
                                AS DATE
                            ),
                            CAST(C."calendar_date" AS DATE)
                         ) <= P."forecast_horizon_days"
                    THEN CAST(
                             PO."Remaining Balance Qty"
                             AS DECIMAL(18,6)
                         )
                    ELSE 0
                END
            ),
            0
        ) AS "valid_open_po_qty",
        COALESCE(
            SUM(
                CASE
                    WHEN COALESCE(TRIM(PO."Expected Delivery"), '') <> ''
                     AND DATEDIFF(
                            CAST(
                                NULLIF(TRIM(PO."Expected Delivery"), '')
                                AS DATE
                            ),
                            CAST(C."calendar_date" AS DATE)
                         ) <= 1
                    THEN CAST(
                             PO."Remaining Balance Qty"
                             AS DECIMAL(18,6)
                         )
                    ELSE 0
                END
            ),
            0
        ) AS "next_day_valid_open_po_qty",
        CASE
            WHEN MAX(D."required_qty") IS NULL THEN NULL
            ELSE
                MAX(CAST(S."Total Qty" AS DECIMAL(18,6)))
                + COALESCE(
                    SUM(
                        CASE
                            WHEN COALESCE(
                                     TRIM(PO."Expected Delivery"),
                                     ''
                                 ) <> ''
                             AND DATEDIFF(
                                    CAST(
                                        NULLIF(
                                            TRIM(PO."Expected Delivery"),
                                            ''
                                        ) AS DATE
                                    ),
                                    CAST(C."calendar_date" AS DATE)
                                 ) <= P."forecast_horizon_days"
                            THEN CAST(
                                     PO."Remaining Balance Qty"
                                     AS DECIMAL(18,6)
                                 )
                            ELSE 0
                        END
                    ),
                    0
                  )
        END AS "available_qty",
        CASE
            WHEN MAX(D."next_day_required_qty") IS NULL THEN NULL
            ELSE
                MAX(CAST(S."Total Qty" AS DECIMAL(18,6)))
                + COALESCE(
                    SUM(
                        CASE
                            WHEN COALESCE(
                                     TRIM(PO."Expected Delivery"),
                                     ''
                                 ) <> ''
                             AND DATEDIFF(
                                    CAST(
                                        NULLIF(
                                            TRIM(PO."Expected Delivery"),
                                            ''
                                        ) AS DATE
                                    ),
                                    CAST(C."calendar_date" AS DATE)
                                 ) <= 1
                            THEN CAST(
                                     PO."Remaining Balance Qty"
                                     AS DECIMAL(18,6)
                                 )
                            ELSE 0
                        END
                    ),
                    0
                  )
        END AS "next_day_available_qty",
        MAX(COALESCE(D."impacted_menu_item_count", 0))
            AS "impacted_menu_item_count",
        MAX(D."ingredient_linked_forecast_sales")
            AS "ingredient_linked_forecast_sales",
        MAX(D."uom_mapping_status") AS "uom_mapping_status",
        MAX(P."inventory_safety_factor") AS "inventory_safety_factor",
        MAX(P."epsilon_qty") AS "epsilon_qty",
        MAX(P."forecast_horizon_days") AS "forecast_horizon_days",
        MAX(P."formula_version") AS "formula_version"
    FROM "CTL_Calendar" C
    JOIN "RAW_Closing_Stock" S
      ON CAST(S."Date" AS DATE) = CAST(C."calendar_date" AS DATE)
    CROSS JOIN params P
    LEFT JOIN demand_by_item D
      ON D."as_of_date" = CAST(C."calendar_date" AS DATE)
     AND D."outlet_name" = S."Deployment"
     AND D."item_code" = S."Item Code"
    LEFT JOIN "RAW_Enterprise_Purchase_Order" PO
      ON PO."Deployment" = S."Deployment"
     AND PO."Item Code" = S."Item Code"
     AND CAST(PO."PO Date" AS DATE)
         <= CAST(C."calendar_date" AS DATE)
     AND CAST(PO."Remaining Balance Qty" AS DECIMAL(18,6)) > 0
     AND LOWER(TRIM(PO."PO Status")) IN
         ('open', 'partially received', 'partial', 'pending')
    WHERE C."is_demo_operational_date" = 1
    GROUP BY
        CAST(C."calendar_date" AS DATE),
        S."Deployment",
        S."Item Code",
        S."Item Name",
        S."Category Name",
        S."Super Category Name",
        S."Unit Name",
        CAST(S."Total Qty" AS DECIMAL(18,6)),
        CAST(S."Average Price" AS DECIMAL(18,6)),
        CAST(S."Total Amt" AS DECIMAL(18,2)),
        CAST(S."Date" AS DATE)
)
SELECT
    b."as_of_date" AS "as_of_date",
    CONCAT(
        'INV|',
        CAST(b."as_of_date" AS CHAR),
        '|',
        b."outlet_name",
        '|',
        b."item_code"
    ) AS "evaluation_id",
    CONCAT('ITEM|', b."outlet_name", '|', b."item_code")
        AS "subject_group_id",
    'INVENTORY' AS "subject_type",
    b."outlet_name" AS "outlet_name",
    b."store_name" AS "store_name",
    b."item_code" AS "item_code",
    b."item_name" AS "item_name",
    b."category_name" AS "category_name",
    b."super_category_name" AS "super_category_name",
    CAST(NULL AS CHAR) AS "vendor_name",
    CAST(NULL AS CHAR) AS "po_number",
    CAST(NULL AS CHAR) AS "batch_number",
    CAST(NULL AS DATE) AS "expiry_date",
    CAST(NULL AS DECIMAL(18,6)) AS "batch_remaining_qty",
    b."current_stock_qty" AS "total_item_stock_qty",
    CAST(NULL AS DECIMAL(18,6)) AS "expired_batch_qty",
    CAST(NULL AS DECIMAL(18,6)) AS "usable_nonexpired_qty",
    ADDDATE(b."as_of_date", 1) AS "next_day_date",
    ADDDATE(
        b."as_of_date",
        b."forecast_horizon_days"
    ) AS "forecast_horizon_end_date",
    b."forecast_horizon_days" AS "forecast_horizon_days",
    b."stock_source_unit" AS "source_unit",
    b."canonical_uom" AS "canonical_uom",
    CASE
        WHEN b."item_code" IS NULL
          OR b."required_qty" IS NULL
          OR b."canonical_uom" IS NULL
          OR b."uom_mapping_status" <> 'MAPPED'
          OR b."inventory_safety_factor" IS NULL
        THEN 'INV_EVIDENCE_GREY'
        WHEN b."current_stock_qty" <= 0
         AND b."required_qty" > 0
         AND b."impacted_menu_item_count" > 0
        THEN 'INV_STOCKOUT_PURPLE'
        WHEN b."required_qty" > b."available_qty"
        THEN 'INV_SHORTAGE_RED'
        WHEN b."required_qty_with_safety" > b."available_qty"
        THEN 'INV_SAFETY_AMBER'
        ELSE 'INV_COVERED_GREEN'
    END AS "rule_id",
    CASE
        WHEN b."item_code" IS NULL
          OR b."required_qty" IS NULL
          OR b."canonical_uom" IS NULL
          OR b."uom_mapping_status" <> 'MAPPED'
          OR b."inventory_safety_factor" IS NULL
        THEN NULL
        WHEN b."current_stock_qty" <= 0
         AND b."required_qty" > 0
         AND b."impacted_menu_item_count" > 0
        THEN b."current_stock_qty"
        ELSE b."available_qty"
    END AS "actual_value",
    CASE
        WHEN b."item_code" IS NULL
          OR b."required_qty" IS NULL
          OR b."canonical_uom" IS NULL
          OR b."uom_mapping_status" <> 'MAPPED'
          OR b."inventory_safety_factor" IS NULL
        THEN NULL
        WHEN b."current_stock_qty" <= 0
         AND b."required_qty" > 0
         AND b."impacted_menu_item_count" > 0
        THEN 0
        WHEN b."required_qty" > b."available_qty"
        THEN b."required_qty"
        ELSE b."required_qty_with_safety"
    END AS "threshold_value",
    CASE
        WHEN b."item_code" IS NULL
          OR b."required_qty" IS NULL
          OR b."canonical_uom" IS NULL
          OR b."uom_mapping_status" <> 'MAPPED'
          OR b."inventory_safety_factor" IS NULL
        THEN NULL
        WHEN b."current_stock_qty" <= 0
         AND b."required_qty" > 0
         AND b."impacted_menu_item_count" > 0
        THEN CASE
                 WHEN -b."current_stock_qty" > 0
                 THEN -b."current_stock_qty"
                 ELSE 0
             END
        WHEN b."required_qty" > b."available_qty"
        THEN b."required_qty" - b."available_qty"
        WHEN b."required_qty_with_safety" > b."available_qty"
        THEN b."required_qty_with_safety" - b."available_qty"
        ELSE b."available_qty" - b."required_qty_with_safety"
    END AS "gap_value",
    CASE
        WHEN b."item_code" IS NULL
          OR b."required_qty" IS NULL
          OR b."canonical_uom" IS NULL
          OR b."uom_mapping_status" <> 'MAPPED'
          OR b."inventory_safety_factor" IS NULL
        THEN NULL
        WHEN b."current_stock_qty" <= 0
         AND b."required_qty" > 0
         AND b."impacted_menu_item_count" > 0
        THEN 1
             + CASE
                   WHEN -b."current_stock_qty" > 0
                   THEN -b."current_stock_qty"
                   ELSE 0
               END
               / CASE
                     WHEN b."required_qty" > b."epsilon_qty"
                     THEN b."required_qty"
                     ELSE b."epsilon_qty"
                 END
        WHEN b."required_qty" > b."available_qty"
        THEN (b."required_qty" - b."available_qty")
             / CASE
                   WHEN b."required_qty" > b."epsilon_qty"
                   THEN b."required_qty"
                   ELSE b."epsilon_qty"
               END
        WHEN b."required_qty_with_safety" > b."available_qty"
        THEN (b."required_qty_with_safety" - b."available_qty")
             / CASE
                   WHEN b."required_qty_with_safety" > b."epsilon_qty"
                   THEN b."required_qty_with_safety"
                   ELSE b."epsilon_qty"
               END
        ELSE 0
    END AS "breach_ratio",
    CASE
        WHEN b."item_code" IS NULL
          OR b."required_qty" IS NULL
          OR b."canonical_uom" IS NULL
          OR b."uom_mapping_status" <> 'MAPPED'
          OR b."inventory_safety_factor" IS NULL
        THEN 'Grey'
        WHEN b."current_stock_qty" <= 0
         AND b."required_qty" > 0
         AND b."impacted_menu_item_count" > 0
        THEN 'Purple'
        WHEN b."required_qty" > b."available_qty" THEN 'Red'
        WHEN b."required_qty_with_safety" > b."available_qty" THEN 'Amber'
        ELSE 'Green'
    END AS "risk_color",
    CASE
        WHEN b."item_code" IS NULL
          OR b."required_qty" IS NULL
          OR b."canonical_uom" IS NULL
          OR b."uom_mapping_status" <> 'MAPPED'
          OR b."inventory_safety_factor" IS NULL
        THEN 5
        WHEN b."current_stock_qty" <= 0
         AND b."required_qty" > 0
         AND b."impacted_menu_item_count" > 0
        THEN 1
        WHEN b."required_qty" > b."available_qty" THEN 2
        WHEN b."required_qty_with_safety" > b."available_qty" THEN 3
        ELSE 4
    END AS "risk_priority_rank",
    CASE
        WHEN b."item_code" IS NULL
          OR b."required_qty" IS NULL
          OR b."canonical_uom" IS NULL
          OR b."uom_mapping_status" <> 'MAPPED'
          OR b."inventory_safety_factor" IS NULL
        THEN 0
        WHEN b."current_stock_qty" <= 0
         AND b."required_qty" > 0
         AND b."impacted_menu_item_count" > 0
        THEN 4
        WHEN b."required_qty" > b."available_qty" THEN 3
        WHEN b."required_qty_with_safety" > b."available_qty" THEN 2
        ELSE 1
    END AS "risk_severity_level",
    b."current_stock_qty" AS "current_stock_qty",
    b."source_stock_value" AS "current_stock_value",
    b."required_qty" AS "forecast_required_qty",
    b."next_day_required_qty" AS "next_day_required_qty",
    b."required_qty_with_safety" AS "required_qty_with_safety",
    b."valid_open_po_qty" AS "valid_open_po_qty",
    b."available_qty" AS "available_qty",
    CASE
        WHEN b."required_qty" IS NULL
          OR b."available_qty" IS NULL
        THEN NULL
        WHEN b."required_qty" > b."available_qty"
        THEN b."required_qty" - b."available_qty"
        ELSE 0
    END AS "shortage_qty",
    CASE
        WHEN b."required_qty" IS NULL
          OR b."available_qty" IS NULL
        THEN NULL
        WHEN b."required_qty" > b."available_qty"
        THEN (b."required_qty" - b."available_qty")
             * b."average_unit_cost"
        ELSE 0
    END AS "monetary_exposure",
    CASE
        WHEN b."next_day_required_qty" IS NULL
          OR b."average_unit_cost" IS NULL
        THEN NULL
        ELSE b."next_day_required_qty" * b."average_unit_cost"
    END AS "next_day_requirement_value",
    CASE
        WHEN b."next_day_required_qty" IS NULL
          OR b."next_day_available_qty" IS NULL
        THEN NULL
        WHEN b."next_day_required_qty" > b."next_day_available_qty"
        THEN b."next_day_required_qty" - b."next_day_available_qty"
        ELSE 0
    END AS "next_day_shortage_qty",
    CASE
        WHEN b."next_day_required_qty" IS NULL
          OR b."next_day_available_qty" IS NULL
          OR b."average_unit_cost" IS NULL
        THEN NULL
        WHEN b."next_day_required_qty" > b."next_day_available_qty"
        THEN (b."next_day_required_qty" - b."next_day_available_qty")
             * b."average_unit_cost"
        ELSE 0
    END AS "next_day_shortage_value",
    CASE
        WHEN b."required_qty" IS NULL
          OR b."average_unit_cost" IS NULL
        THEN NULL
        ELSE b."required_qty" * b."average_unit_cost"
    END AS "seven_day_requirement_value",
    b."impacted_menu_item_count" AS "impacted_menu_item_count",
    CAST(NULL AS DECIMAL(18,0)) AS "impacted_ingredient_count",
    CAST(NULL AS DECIMAL(18,0)) AS "days_to_expiry",
    CAST(NULL AS DECIMAL(18,0)) AS "po_overdue_days",
    b."stock_snapshot_date" AS "source_snapshot_date",
    'OBSERVED_AND_MODEL_DERIVED' AS "data_status",
    CAST(NULL AS CHAR) AS "source_disclosure",
    b."formula_version" AS "formula_version",
    CAST(NULL AS CHAR) AS "source_formula_version",
    'RAW_Closing_Stock;QT_01_Demand_Requirement;RAW_Enterprise_Purchase_Order'
        AS "source_table",
    CONCAT(
        CAST(b."stock_snapshot_date" AS CHAR),
        '|',
        b."outlet_name",
        '|',
        b."item_code"
    ) AS "source_row_key"
FROM inventory_base b

UNION ALL

SELECT
    CAST(d."calendar_date" AS DATE) AS "as_of_date",
    CONCAT(
        'EXP|',
        CAST(CAST(d."calendar_date" AS DATE) AS CHAR),
        '|',
        e."Deployment Name",
        '|',
        e."Item Code",
        '|',
        e."Batch Number"
    ) AS "evaluation_id",
    CONCAT('ITEM|', e."Deployment Name", '|', e."Item Code")
        AS "subject_group_id",
    'EXPIRY' AS "subject_type",
    e."Deployment Name" AS "outlet_name",
    e."Store Name" AS "store_name",
    e."Item Code" AS "item_code",
    e."Item Name" AS "item_name",
    e."Category Name" AS "category_name",
    e."Super Category Name" AS "super_category_name",
    e."Vendor Name" AS "vendor_name",
    CAST(NULL AS CHAR) AS "po_number",
    e."Batch Number" AS "batch_number",
    CAST(e."Expiry Date" AS DATE) AS "expiry_date",
    CAST(e."Batch Remaining Qty" AS DECIMAL(18,6))
        AS "batch_remaining_qty",
    b."current_stock_qty" AS "total_item_stock_qty",
    CASE
        WHEN DATEDIFF(
                 CAST(e."Expiry Date" AS DATE),
                 CAST(d."calendar_date" AS DATE)
             ) <= 0
        THEN CAST(e."Batch Remaining Qty" AS DECIMAL(18,6))
        ELSE 0
    END AS "expired_batch_qty",
    CASE
        WHEN DATEDIFF(
                 CAST(e."Expiry Date" AS DATE),
                 CAST(d."calendar_date" AS DATE)
             ) > 0
        THEN CAST(e."Batch Remaining Qty" AS DECIMAL(18,6))
        ELSE 0
    END AS "usable_nonexpired_qty",
    ADDDATE(CAST(d."calendar_date" AS DATE), 1) AS "next_day_date",
    ADDDATE(
        CAST(d."calendar_date" AS DATE),
        p."forecast_horizon_days"
    ) AS "forecast_horizon_end_date",
    p."forecast_horizon_days" AS "forecast_horizon_days",
    e."Unit" AS "source_unit",
    CAST(NULL AS CHAR) AS "canonical_uom",
    CASE
        WHEN COALESCE(TRIM(e."Batch Number"), '') = ''
          OR e."Expiry Date" IS NULL
          OR COALESCE(TRIM(e."Unit"), '') = ''
          OR e."Batch Remaining Qty" IS NULL
          OR CAST(e."Batch Remaining Qty" AS DECIMAL(18,6)) <= 0
          OR e."Average Unit Cost" IS NULL
          OR CAST(e."Average Unit Cost" AS DECIMAL(18,6)) <= 0
          OR p."expiry_red_days" IS NULL
          OR p."expiry_amber_days" IS NULL
        THEN 'EXP_EVIDENCE_GREY'
        WHEN DATEDIFF(
                 CAST(e."Expiry Date" AS DATE),
                 CAST(d."calendar_date" AS DATE)
             ) <= 0
        THEN 'EXP_EXPIRED_RED'
        WHEN DATEDIFF(
                 CAST(e."Expiry Date" AS DATE),
                 CAST(d."calendar_date" AS DATE)
             ) <= p."expiry_red_days"
        THEN 'EXP_NEAR_RED'
        WHEN DATEDIFF(
                 CAST(e."Expiry Date" AS DATE),
                 CAST(d."calendar_date" AS DATE)
             ) <= p."expiry_amber_days"
        THEN 'EXP_NEAR_AMBER'
        ELSE 'EXP_CLEAR_GREEN'
    END AS "rule_id",
    CASE
        WHEN COALESCE(TRIM(e."Batch Number"), '') = ''
          OR e."Expiry Date" IS NULL
          OR COALESCE(TRIM(e."Unit"), '') = ''
          OR e."Batch Remaining Qty" IS NULL
          OR CAST(e."Batch Remaining Qty" AS DECIMAL(18,6)) <= 0
          OR e."Average Unit Cost" IS NULL
          OR CAST(e."Average Unit Cost" AS DECIMAL(18,6)) <= 0
          OR p."expiry_red_days" IS NULL
          OR p."expiry_amber_days" IS NULL
        THEN NULL
        ELSE DATEDIFF(
                 CAST(e."Expiry Date" AS DATE),
                 CAST(d."calendar_date" AS DATE)
             )
    END AS "actual_value",
    CASE
        WHEN COALESCE(TRIM(e."Batch Number"), '') = ''
          OR e."Expiry Date" IS NULL
          OR COALESCE(TRIM(e."Unit"), '') = ''
          OR e."Batch Remaining Qty" IS NULL
          OR CAST(e."Batch Remaining Qty" AS DECIMAL(18,6)) <= 0
          OR e."Average Unit Cost" IS NULL
          OR CAST(e."Average Unit Cost" AS DECIMAL(18,6)) <= 0
          OR p."expiry_red_days" IS NULL
          OR p."expiry_amber_days" IS NULL
        THEN NULL
        WHEN DATEDIFF(
                 CAST(e."Expiry Date" AS DATE),
                 CAST(d."calendar_date" AS DATE)
             ) <= p."expiry_red_days"
        THEN p."expiry_red_days"
        ELSE p."expiry_amber_days"
    END AS "threshold_value",
    CASE
        WHEN COALESCE(TRIM(e."Batch Number"), '') = ''
          OR e."Expiry Date" IS NULL
          OR COALESCE(TRIM(e."Unit"), '') = ''
          OR e."Batch Remaining Qty" IS NULL
          OR CAST(e."Batch Remaining Qty" AS DECIMAL(18,6)) <= 0
          OR e."Average Unit Cost" IS NULL
          OR CAST(e."Average Unit Cost" AS DECIMAL(18,6)) <= 0
          OR p."expiry_red_days" IS NULL
          OR p."expiry_amber_days" IS NULL
        THEN NULL
        WHEN DATEDIFF(
                 CAST(e."Expiry Date" AS DATE),
                 CAST(d."calendar_date" AS DATE)
             ) <= 0
        THEN -DATEDIFF(
                  CAST(e."Expiry Date" AS DATE),
                  CAST(d."calendar_date" AS DATE)
             )
        WHEN DATEDIFF(
                 CAST(e."Expiry Date" AS DATE),
                 CAST(d."calendar_date" AS DATE)
             ) <= p."expiry_red_days"
        THEN p."expiry_red_days"
             - DATEDIFF(
                   CAST(e."Expiry Date" AS DATE),
                   CAST(d."calendar_date" AS DATE)
               )
        WHEN DATEDIFF(
                 CAST(e."Expiry Date" AS DATE),
                 CAST(d."calendar_date" AS DATE)
             ) <= p."expiry_amber_days"
        THEN p."expiry_amber_days"
             - DATEDIFF(
                   CAST(e."Expiry Date" AS DATE),
                   CAST(d."calendar_date" AS DATE)
               )
        ELSE DATEDIFF(
                 CAST(e."Expiry Date" AS DATE),
                 CAST(d."calendar_date" AS DATE)
             ) - p."expiry_amber_days"
    END AS "gap_value",
    CASE
        WHEN COALESCE(TRIM(e."Batch Number"), '') = ''
          OR e."Expiry Date" IS NULL
          OR COALESCE(TRIM(e."Unit"), '') = ''
          OR e."Batch Remaining Qty" IS NULL
          OR CAST(e."Batch Remaining Qty" AS DECIMAL(18,6)) <= 0
          OR e."Average Unit Cost" IS NULL
          OR CAST(e."Average Unit Cost" AS DECIMAL(18,6)) <= 0
          OR p."expiry_red_days" IS NULL
          OR p."expiry_amber_days" IS NULL
        THEN NULL
        WHEN DATEDIFF(
                 CAST(e."Expiry Date" AS DATE),
                 CAST(d."calendar_date" AS DATE)
             ) <= 0
        THEN 1
             + (
                 -DATEDIFF(
                     CAST(e."Expiry Date" AS DATE),
                     CAST(d."calendar_date" AS DATE)
                 )
               )
               / CASE
                     WHEN p."expiry_red_days" > 1
                     THEN p."expiry_red_days"
                     ELSE 1
                 END
        WHEN DATEDIFF(
                 CAST(e."Expiry Date" AS DATE),
                 CAST(d."calendar_date" AS DATE)
             ) <= p."expiry_red_days"
        THEN (
                 p."expiry_red_days"
                 - DATEDIFF(
                     CAST(e."Expiry Date" AS DATE),
                     CAST(d."calendar_date" AS DATE)
                 )
                 + 1
             )
             / CASE
                   WHEN p."expiry_red_days" > 1
                   THEN p."expiry_red_days"
                   ELSE 1
               END
        WHEN DATEDIFF(
                 CAST(e."Expiry Date" AS DATE),
                 CAST(d."calendar_date" AS DATE)
             ) <= p."expiry_amber_days"
        THEN (
                 p."expiry_amber_days"
                 - DATEDIFF(
                     CAST(e."Expiry Date" AS DATE),
                     CAST(d."calendar_date" AS DATE)
                 )
                 + 1
             )
             / CASE
                   WHEN p."expiry_amber_days" - p."expiry_red_days" > 1
                   THEN p."expiry_amber_days" - p."expiry_red_days"
                   ELSE 1
               END
        ELSE 0
    END AS "breach_ratio",
    CASE
        WHEN COALESCE(TRIM(e."Batch Number"), '') = ''
          OR e."Expiry Date" IS NULL
          OR COALESCE(TRIM(e."Unit"), '') = ''
          OR e."Batch Remaining Qty" IS NULL
          OR CAST(e."Batch Remaining Qty" AS DECIMAL(18,6)) <= 0
          OR e."Average Unit Cost" IS NULL
          OR CAST(e."Average Unit Cost" AS DECIMAL(18,6)) <= 0
          OR p."expiry_red_days" IS NULL
          OR p."expiry_amber_days" IS NULL
        THEN 'Grey'
        WHEN DATEDIFF(
                 CAST(e."Expiry Date" AS DATE),
                 CAST(d."calendar_date" AS DATE)
             ) <= p."expiry_red_days"
        THEN 'Red'
        WHEN DATEDIFF(
                 CAST(e."Expiry Date" AS DATE),
                 CAST(d."calendar_date" AS DATE)
             ) <= p."expiry_amber_days"
        THEN 'Amber'
        ELSE 'Green'
    END AS "risk_color",
    CASE
        WHEN COALESCE(TRIM(e."Batch Number"), '') = ''
          OR e."Expiry Date" IS NULL
          OR COALESCE(TRIM(e."Unit"), '') = ''
          OR e."Batch Remaining Qty" IS NULL
          OR CAST(e."Batch Remaining Qty" AS DECIMAL(18,6)) <= 0
          OR e."Average Unit Cost" IS NULL
          OR CAST(e."Average Unit Cost" AS DECIMAL(18,6)) <= 0
          OR p."expiry_red_days" IS NULL
          OR p."expiry_amber_days" IS NULL
        THEN 5
        WHEN DATEDIFF(
                 CAST(e."Expiry Date" AS DATE),
                 CAST(d."calendar_date" AS DATE)
             ) <= p."expiry_red_days"
        THEN 2
        WHEN DATEDIFF(
                 CAST(e."Expiry Date" AS DATE),
                 CAST(d."calendar_date" AS DATE)
             ) <= p."expiry_amber_days"
        THEN 3
        ELSE 4
    END AS "risk_priority_rank",
    CASE
        WHEN COALESCE(TRIM(e."Batch Number"), '') = ''
          OR e."Expiry Date" IS NULL
          OR COALESCE(TRIM(e."Unit"), '') = ''
          OR e."Batch Remaining Qty" IS NULL
          OR CAST(e."Batch Remaining Qty" AS DECIMAL(18,6)) <= 0
          OR e."Average Unit Cost" IS NULL
          OR CAST(e."Average Unit Cost" AS DECIMAL(18,6)) <= 0
          OR p."expiry_red_days" IS NULL
          OR p."expiry_amber_days" IS NULL
        THEN 0
        WHEN DATEDIFF(
                 CAST(e."Expiry Date" AS DATE),
                 CAST(d."calendar_date" AS DATE)
             ) <= p."expiry_red_days"
        THEN 3
        WHEN DATEDIFF(
                 CAST(e."Expiry Date" AS DATE),
                 CAST(d."calendar_date" AS DATE)
             ) <= p."expiry_amber_days"
        THEN 2
        ELSE 1
    END AS "risk_severity_level",
    CAST(NULL AS DECIMAL(18,6)) AS "current_stock_qty",
    CAST(NULL AS DECIMAL(18,2)) AS "current_stock_value",
    b."required_qty" AS "forecast_required_qty",
    b."next_day_required_qty" AS "next_day_required_qty",
    CAST(NULL AS DECIMAL(18,6)) AS "required_qty_with_safety",
    CAST(NULL AS DECIMAL(18,6)) AS "valid_open_po_qty",
    CAST(NULL AS DECIMAL(18,6)) AS "available_qty",
    CAST(NULL AS DECIMAL(18,6)) AS "shortage_qty",
    CASE
        WHEN COALESCE(TRIM(e."Batch Number"), '') = ''
          OR e."Expiry Date" IS NULL
          OR COALESCE(TRIM(e."Unit"), '') = ''
          OR e."Batch Remaining Qty" IS NULL
          OR CAST(e."Batch Remaining Qty" AS DECIMAL(18,6)) <= 0
          OR e."Average Unit Cost" IS NULL
          OR CAST(e."Average Unit Cost" AS DECIMAL(18,6)) <= 0
        THEN NULL
        WHEN DATEDIFF(
                 CAST(e."Expiry Date" AS DATE),
                 CAST(d."calendar_date" AS DATE)
             ) <= p."expiry_amber_days"
        THEN CAST(e."Batch Remaining Qty" AS DECIMAL(18,6))
             * CAST(e."Average Unit Cost" AS DECIMAL(18,6))
        ELSE 0
    END AS "monetary_exposure",
    CASE
        WHEN b."next_day_required_qty" IS NULL
          OR b."average_unit_cost" IS NULL
        THEN NULL
        ELSE b."next_day_required_qty" * b."average_unit_cost"
    END AS "next_day_requirement_value",
    CASE
        WHEN b."next_day_required_qty" IS NULL
          OR b."next_day_available_qty" IS NULL
        THEN NULL
        WHEN b."next_day_required_qty" > b."next_day_available_qty"
        THEN b."next_day_required_qty" - b."next_day_available_qty"
        ELSE 0
    END AS "next_day_shortage_qty",
    CASE
        WHEN b."next_day_required_qty" IS NULL
          OR b."next_day_available_qty" IS NULL
          OR b."average_unit_cost" IS NULL
        THEN NULL
        WHEN b."next_day_required_qty" > b."next_day_available_qty"
        THEN (b."next_day_required_qty" - b."next_day_available_qty")
             * b."average_unit_cost"
        ELSE 0
    END AS "next_day_shortage_value",
    CASE
        WHEN b."required_qty" IS NULL
          OR b."average_unit_cost" IS NULL
        THEN NULL
        ELSE b."required_qty" * b."average_unit_cost"
    END AS "seven_day_requirement_value",
    CAST(NULL AS DECIMAL(18,0)) AS "impacted_menu_item_count",
    CAST(NULL AS DECIMAL(18,0)) AS "impacted_ingredient_count",
    DATEDIFF(
        CAST(e."Expiry Date" AS DATE),
        CAST(d."calendar_date" AS DATE)
    ) AS "days_to_expiry",
    CAST(NULL AS DECIMAL(18,0)) AS "po_overdue_days",
    CAST(e."As Of Date" AS DATE) AS "source_snapshot_date",
    e."Data Status" AS "data_status",
    e."Display Label" AS "source_disclosure",
    p."formula_version" AS "formula_version",
    e."Formula Version" AS "source_formula_version",
    'SYN_Provisional_Expiry_Report' AS "source_table",
    CONCAT(
        CAST(e."As Of Date" AS CHAR),
        '|',
        e."Deployment Name",
        '|',
        e."Item Code",
        '|',
        e."Batch Number"
    ) AS "source_row_key"
FROM "CTL_Calendar" d
JOIN "SYN_Provisional_Expiry_Report" e
  ON CAST(e."As Of Date" AS DATE) = CAST(d."calendar_date" AS DATE)
LEFT JOIN inventory_base b
  ON b."as_of_date" = CAST(d."calendar_date" AS DATE)
 AND b."outlet_name" = e."Deployment Name"
 AND b."item_code" = e."Item Code"
CROSS JOIN params p
WHERE d."is_demo_operational_date" = 1

UNION ALL

SELECT
    CAST(d."calendar_date" AS DATE) AS "as_of_date",
    CONCAT(
        'PO|',
        CAST(CAST(d."calendar_date" AS DATE) AS CHAR),
        '|',
        po."Deployment",
        '|',
        po."PO Number",
        '|',
        po."Item Code"
    ) AS "evaluation_id",
    CONCAT('ITEM|', po."Deployment", '|', po."Item Code")
        AS "subject_group_id",
    'OPEN_PO_TIMING' AS "subject_type",
    po."Deployment" AS "outlet_name",
    po."Store Name" AS "store_name",
    po."Item Code" AS "item_code",
    po."Item Name" AS "item_name",
    po."Category Name" AS "category_name",
    po."Super Category Name" AS "super_category_name",
    po."Vendor Name" AS "vendor_name",
    po."PO Number" AS "po_number",
    CAST(NULL AS CHAR) AS "batch_number",
    CAST(NULL AS DATE) AS "expiry_date",
    CAST(NULL AS DECIMAL(18,6)) AS "batch_remaining_qty",
    CAST(NULL AS DECIMAL(18,6)) AS "total_item_stock_qty",
    CAST(NULL AS DECIMAL(18,6)) AS "expired_batch_qty",
    CAST(NULL AS DECIMAL(18,6)) AS "usable_nonexpired_qty",
    ADDDATE(CAST(d."calendar_date" AS DATE), 1) AS "next_day_date",
    ADDDATE(
        CAST(d."calendar_date" AS DATE),
        p."forecast_horizon_days"
    ) AS "forecast_horizon_end_date",
    p."forecast_horizon_days" AS "forecast_horizon_days",
    po."Unit" AS "source_unit",
    CAST(NULL AS CHAR) AS "canonical_uom",
    CASE
        WHEN COALESCE(TRIM(po."Expected Delivery"), '') = ''
        THEN 'PO_DATE_EVIDENCE_GREY'
        WHEN DATEDIFF(
                 CAST(d."calendar_date" AS DATE),
                 CAST(NULLIF(TRIM(po."Expected Delivery"), '') AS DATE)
             ) >= p."po_overdue_red_days"
        THEN 'PO_OVERDUE_RED'
        WHEN DATEDIFF(
                 CAST(NULLIF(TRIM(po."Expected Delivery"), '') AS DATE),
                 CAST(d."calendar_date" AS DATE)
             ) <= p."po_due_amber_days"
        THEN 'PO_DUE_AMBER'
        ELSE 'PO_TIMING_GREEN'
    END AS "rule_id",
    CASE
        WHEN COALESCE(TRIM(po."Expected Delivery"), '') = '' THEN NULL
        WHEN CAST(NULLIF(TRIM(po."Expected Delivery"), '') AS DATE)
             < CAST(d."calendar_date" AS DATE)
        THEN DATEDIFF(
                 CAST(d."calendar_date" AS DATE),
                 CAST(NULLIF(TRIM(po."Expected Delivery"), '') AS DATE)
             )
        ELSE DATEDIFF(
                 CAST(NULLIF(TRIM(po."Expected Delivery"), '') AS DATE),
                 CAST(d."calendar_date" AS DATE)
             )
    END AS "actual_value",
    CASE
        WHEN COALESCE(TRIM(po."Expected Delivery"), '') = '' THEN NULL
        WHEN CAST(NULLIF(TRIM(po."Expected Delivery"), '') AS DATE)
             < CAST(d."calendar_date" AS DATE)
        THEN p."po_overdue_red_days"
        ELSE p."po_due_amber_days"
    END AS "threshold_value",
    CASE
        WHEN COALESCE(TRIM(po."Expected Delivery"), '') = '' THEN NULL
        WHEN CAST(NULLIF(TRIM(po."Expected Delivery"), '') AS DATE)
             < CAST(d."calendar_date" AS DATE)
        THEN DATEDIFF(
                 CAST(d."calendar_date" AS DATE),
                 CAST(NULLIF(TRIM(po."Expected Delivery"), '') AS DATE)
             ) - p."po_overdue_red_days"
        WHEN DATEDIFF(
                 CAST(NULLIF(TRIM(po."Expected Delivery"), '') AS DATE),
                 CAST(d."calendar_date" AS DATE)
             ) <= p."po_due_amber_days"
        THEN p."po_due_amber_days"
             - DATEDIFF(
                 CAST(NULLIF(TRIM(po."Expected Delivery"), '') AS DATE),
                 CAST(d."calendar_date" AS DATE)
             )
        ELSE DATEDIFF(
                 CAST(NULLIF(TRIM(po."Expected Delivery"), '') AS DATE),
                 CAST(d."calendar_date" AS DATE)
             ) - p."po_due_amber_days"
    END AS "gap_value",
    CASE
        WHEN COALESCE(TRIM(po."Expected Delivery"), '') = '' THEN NULL
        WHEN CAST(NULLIF(TRIM(po."Expected Delivery"), '') AS DATE)
             < CAST(d."calendar_date" AS DATE)
        THEN DATEDIFF(
                 CAST(d."calendar_date" AS DATE),
                 CAST(NULLIF(TRIM(po."Expected Delivery"), '') AS DATE)
             )
             / CASE
                   WHEN p."po_overdue_red_days" > 1
                   THEN p."po_overdue_red_days"
                   ELSE 1
               END
        WHEN DATEDIFF(
                 CAST(NULLIF(TRIM(po."Expected Delivery"), '') AS DATE),
                 CAST(d."calendar_date" AS DATE)
             ) <= p."po_due_amber_days"
        THEN (
                p."po_due_amber_days"
                - DATEDIFF(
                    CAST(NULLIF(TRIM(po."Expected Delivery"), '') AS DATE),
                    CAST(d."calendar_date" AS DATE)
                )
                + 1
             )
             / CASE
                   WHEN p."po_due_amber_days" > 1
                   THEN p."po_due_amber_days"
                   ELSE 1
               END
        ELSE 0
    END AS "breach_ratio",
    CASE
        WHEN COALESCE(TRIM(po."Expected Delivery"), '') = '' THEN 'Grey'
        WHEN DATEDIFF(
                 CAST(d."calendar_date" AS DATE),
                 CAST(NULLIF(TRIM(po."Expected Delivery"), '') AS DATE)
             ) >= p."po_overdue_red_days"
        THEN 'Red'
        WHEN DATEDIFF(
                 CAST(NULLIF(TRIM(po."Expected Delivery"), '') AS DATE),
                 CAST(d."calendar_date" AS DATE)
             ) <= p."po_due_amber_days"
        THEN 'Amber'
        ELSE 'Green'
    END AS "risk_color",
    CASE
        WHEN COALESCE(TRIM(po."Expected Delivery"), '') = '' THEN 5
        WHEN DATEDIFF(
                 CAST(d."calendar_date" AS DATE),
                 CAST(NULLIF(TRIM(po."Expected Delivery"), '') AS DATE)
             ) >= p."po_overdue_red_days"
        THEN 2
        WHEN DATEDIFF(
                 CAST(NULLIF(TRIM(po."Expected Delivery"), '') AS DATE),
                 CAST(d."calendar_date" AS DATE)
             ) <= p."po_due_amber_days"
        THEN 3
        ELSE 4
    END AS "risk_priority_rank",
    CASE
        WHEN COALESCE(TRIM(po."Expected Delivery"), '') = '' THEN 0
        WHEN DATEDIFF(
                 CAST(d."calendar_date" AS DATE),
                 CAST(NULLIF(TRIM(po."Expected Delivery"), '') AS DATE)
             ) >= p."po_overdue_red_days"
        THEN 3
        WHEN DATEDIFF(
                 CAST(NULLIF(TRIM(po."Expected Delivery"), '') AS DATE),
                 CAST(d."calendar_date" AS DATE)
             ) <= p."po_due_amber_days"
        THEN 2
        ELSE 1
    END AS "risk_severity_level",
    CAST(NULL AS DECIMAL(18,6)) AS "current_stock_qty",
    CAST(NULL AS DECIMAL(18,2)) AS "current_stock_value",
    demand."required_qty" AS "forecast_required_qty",
    demand."next_day_required_qty" AS "next_day_required_qty",
    CAST(NULL AS DECIMAL(18,6)) AS "required_qty_with_safety",
    CAST(po."Remaining Balance Qty" AS DECIMAL(18,6))
        AS "valid_open_po_qty",
    CAST(NULL AS DECIMAL(18,6)) AS "available_qty",
    CAST(NULL AS DECIMAL(18,6)) AS "shortage_qty",
    CAST(po."Remaining Balance Qty" AS DECIMAL(18,6))
        * CAST(po."Unit Price" AS DECIMAL(18,6))
        AS "monetary_exposure",
    CAST(NULL AS DECIMAL(18,2)) AS "next_day_requirement_value",
    CAST(NULL AS DECIMAL(18,6)) AS "next_day_shortage_qty",
    CAST(NULL AS DECIMAL(18,2)) AS "next_day_shortage_value",
    CAST(NULL AS DECIMAL(18,2)) AS "seven_day_requirement_value",
    demand."impacted_menu_item_count" AS "impacted_menu_item_count",
    CAST(NULL AS DECIMAL(18,0)) AS "impacted_ingredient_count",
    CAST(NULL AS DECIMAL(18,0)) AS "days_to_expiry",
    CASE
        WHEN COALESCE(TRIM(po."Expected Delivery"), '') = '' THEN NULL
        WHEN CAST(NULLIF(TRIM(po."Expected Delivery"), '') AS DATE)
             < CAST(d."calendar_date" AS DATE)
        THEN DATEDIFF(
                 CAST(d."calendar_date" AS DATE),
                 CAST(NULLIF(TRIM(po."Expected Delivery"), '') AS DATE)
             )
        ELSE 0
    END AS "po_overdue_days",
    CAST(po."PO Date" AS DATE) AS "source_snapshot_date",
    'OBSERVED_SOURCE' AS "data_status",
    CAST(NULL AS CHAR) AS "source_disclosure",
    p."formula_version" AS "formula_version",
    CAST(NULL AS CHAR) AS "source_formula_version",
    'RAW_Enterprise_Purchase_Order' AS "source_table",
    CONCAT(po."PO Number", '|', po."Item Code") AS "source_row_key"
FROM "CTL_Calendar" d
CROSS JOIN params p
JOIN "RAW_Enterprise_Purchase_Order" po
  ON CAST(po."PO Date" AS DATE) <= CAST(d."calendar_date" AS DATE)
 AND CAST(po."Remaining Balance Qty" AS DECIMAL(18,6)) > 0
 AND LOWER(TRIM(po."PO Status")) IN
     ('open', 'partially received', 'partial', 'pending')
LEFT JOIN demand_by_item demand
  ON demand."as_of_date" = CAST(d."calendar_date" AS DATE)
 AND demand."outlet_name" = po."Deployment"
 AND demand."item_code" = po."Item Code"
WHERE d."is_demo_operational_date" = 1;
