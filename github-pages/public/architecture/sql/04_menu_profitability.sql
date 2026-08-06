/*
Query Table : QT_04_Menu_Profitability
Layer       : DERIVED_L1 (raw/control inputs only)
Grain       : outlet_name + sales_date + menu_item_code

Purpose
-------
Calculate recipe-based theoretical COGS and menu gross margin from physical
sales dates.  Retain the Gross/Net Margin report's Purchase Value as source
reconciliation evidence; do not present it as recipe-derived cost.

Required Zoho tables (use these exact import names)
---------------------------------------------------
RAW_Gross_Net_Margin
REF_Item_Recipe
RAW_Enterprise_Variance_Normal
CTL_UOM_Conversions
CTL_Rule_Parameters

Cost rule
---------
The approved demo cost source is the ingredient Average Price whose
Enterprise Variance Normal opening/closing interval contains sales_date.
No future closing snapshot is backfilled and no missing cost is replaced by
zero.  Both recipe quantity and ingredient cost UOMs must convert to the same
canonical UOM:

recipe_qty_canonical = recipe_qty_source * recipe_uom_multiplier
cost_per_canonical    = source_average_price / cost_uom_multiplier
ingredient_cost_per_menu_unit =
    recipe_qty_canonical * cost_per_canonical

If any recipe line lacks a valid recipe mapping, period cost row, or valid
cost mapping, theoretical COGS and theoretical margin are NULL for the menu
row.  Coverage counts remain available for data-quality drill-through.

Margin and reconciliation rules
-------------------------------
theoretical_cogs       = sold_qty * complete_recipe_cost_per_menu_unit
menu_gross_margin      = net_sales - theoretical_cogs
menu_gross_margin_pct  = menu_gross_margin / net_sales
source_net_margin      = net_sales - source_reported_purchase_value
cogs_reconciliation   = theoretical_cogs - source_reported_purchase_value

Percentages are recomputed from additive numerators/denominators.  Division
by zero returns NULL.  Negative sales, costs, and margins are retained.

BCG rule
--------
No fixed quantity or margin cutoff is embedded here.  The effective cutoff
method codes are pivoted from CTL_Rule_Parameters.  SELECTED_SCOPE_MEDIAN is
therefore evaluated as a report-level aggregate after dashboard filtering;
this daily-grain Query Table does not falsely substitute an all-data median.

Zoho compatibility
------------------
This uses three non-recursive CTEs, ANSI joins, and Zoho date().  No Query
Table input is used, so the object remains dependency level 1.
*/

WITH
Sales_Daily AS
(
    SELECT
        G."Store Name" AS "outlet_name",
        date(G."Date") AS "sales_date",
        G."SKU Code / Item No" AS "menu_item_code",
        MAX(G."SKU / Item Name") AS "menu_item_name",
        MAX(G."Super Category") AS "super_category_name",
        MAX(G."Category") AS "category_name",
        SUM(G."Item Qty") AS "sold_menu_qty",
        SUM(G."Net Sale Value") AS "net_sales_value",
        SUM(G."Gross Sale Value") AS "gross_sales_value",
        SUM(G."Purchase Value") AS "source_reported_purchase_value",
        COUNT(G."Bill No.") AS "source_sales_line_count"
    FROM "RAW_Gross_Net_Margin" G
    WHERE G."Store Name" IS NOT NULL
      AND G."Date" IS NOT NULL
      AND G."SKU Code / Item No" IS NOT NULL
    GROUP BY
        G."Store Name",
        date(G."Date"),
        G."SKU Code / Item No"
),
Recipe_Lines AS
(
    SELECT
        R."Item Number" AS "menu_item_code",
        R."Ingredient Code" AS "ingredient_code",
        MAX(R."Ingredient Name") AS "ingredient_name",
        R."Recipe Unit" AS "recipe_source_unit",
        SUM(R."Qty") AS "recipe_source_qty_per_menu_unit"
    FROM "REF_Item_Recipe" R
    WHERE R."Item Number" IS NOT NULL
      AND R."Ingredient Code" IS NOT NULL
    GROUP BY
        R."Item Number",
        R."Ingredient Code",
        R."Recipe Unit"
),
Ingredient_Cost_Period AS
(
    SELECT
        C."Deployment Name" AS "outlet_name",
        C."StoreKitchen Name" AS "store_name",
        C."Item Code" AS "ingredient_code",
        C."Item Name" AS "ingredient_name",
        date(C."Opening Date") AS "cost_period_start",
        date(C."Closing Date") AS "cost_period_end",
        C."Unit" AS "cost_source_uom",
        C."Average Price" AS "source_average_unit_cost"
    FROM "RAW_Enterprise_Variance_Normal" C
    WHERE C."Deployment Name" IS NOT NULL
      AND C."Item Code" IS NOT NULL
      AND C."Opening Date" IS NOT NULL
      AND C."Closing Date" IS NOT NULL
)
SELECT
    S."sales_date" AS "sales_date",
    S."outlet_name" AS "outlet_name",
    S."menu_item_code" AS "menu_item_code",
    S."menu_item_name" AS "menu_item_name",
    S."super_category_name" AS "super_category_name",
    S."category_name" AS "category_name",
    S."sold_menu_qty" AS "sold_menu_qty",
    S."net_sales_value" AS "net_sales_value",
    S."gross_sales_value" AS "gross_sales_value",
    S."source_reported_purchase_value"
        AS "source_reported_purchase_value",

    /* Complete recipe cost per one sold menu unit. */
    CASE
        WHEN COUNT(R."ingredient_code") = 0 THEN NULL
        WHEN
            SUM(
                CASE
                    WHEN R."ingredient_code" IS NOT NULL
                     AND C."ingredient_code" IS NOT NULL
                     AND RU."multiplier" IS NOT NULL
                     AND RU."multiplier" > 0
                     AND CU."multiplier" IS NOT NULL
                     AND CU."multiplier" > 0
                     AND COALESCE(RU."offset", 0) = 0
                     AND COALESCE(CU."offset", 0) = 0
                     AND LOWER(RU."conversion_status") LIKE 'approved%'
                     AND LOWER(CU."conversion_status") LIKE 'approved%'
                     AND LOWER(RU."to_unit") = LOWER(CU."to_unit")
                     AND C."source_average_unit_cost" IS NOT NULL
                    THEN 1 ELSE 0
                END
            ) <> COUNT(R."ingredient_code")
        THEN NULL
        ELSE
            SUM(
                R."recipe_source_qty_per_menu_unit"
                * RU."multiplier"
                * (
                    C."source_average_unit_cost"
                    / CU."multiplier"
                  )
            )
    END AS "theoretical_cost_per_menu_unit",

    /* CT_P3_004: recipe-based theoretical COGS. */
    CASE
        WHEN COUNT(R."ingredient_code") = 0 THEN NULL
        WHEN
            SUM(
                CASE
                    WHEN R."ingredient_code" IS NOT NULL
                     AND C."ingredient_code" IS NOT NULL
                     AND RU."multiplier" IS NOT NULL
                     AND RU."multiplier" > 0
                     AND CU."multiplier" IS NOT NULL
                     AND CU."multiplier" > 0
                     AND COALESCE(RU."offset", 0) = 0
                     AND COALESCE(CU."offset", 0) = 0
                     AND LOWER(RU."conversion_status") LIKE 'approved%'
                     AND LOWER(CU."conversion_status") LIKE 'approved%'
                     AND LOWER(RU."to_unit") = LOWER(CU."to_unit")
                     AND C."source_average_unit_cost" IS NOT NULL
                    THEN 1 ELSE 0
                END
            ) <> COUNT(R."ingredient_code")
        THEN NULL
        ELSE
            S."sold_menu_qty"
            * SUM(
                R."recipe_source_qty_per_menu_unit"
                * RU."multiplier"
                * (
                    C."source_average_unit_cost"
                    / CU."multiplier"
                  )
              )
    END AS "theoretical_cogs",

    /* CT_P3_009: theoretical recipe-cost margin. */
    CASE
        WHEN COUNT(R."ingredient_code") = 0 THEN NULL
        WHEN
            SUM(
                CASE
                    WHEN R."ingredient_code" IS NOT NULL
                     AND C."ingredient_code" IS NOT NULL
                     AND RU."multiplier" IS NOT NULL
                     AND RU."multiplier" > 0
                     AND CU."multiplier" IS NOT NULL
                     AND CU."multiplier" > 0
                     AND COALESCE(RU."offset", 0) = 0
                     AND COALESCE(CU."offset", 0) = 0
                     AND LOWER(RU."conversion_status") LIKE 'approved%'
                     AND LOWER(CU."conversion_status") LIKE 'approved%'
                     AND LOWER(RU."to_unit") = LOWER(CU."to_unit")
                     AND C."source_average_unit_cost" IS NOT NULL
                    THEN 1 ELSE 0
                END
            ) <> COUNT(R."ingredient_code")
        THEN NULL
        ELSE
            S."net_sales_value"
            -
            (
                S."sold_menu_qty"
                * SUM(
                    R."recipe_source_qty_per_menu_unit"
                    * RU."multiplier"
                    * (
                        C."source_average_unit_cost"
                        / CU."multiplier"
                      )
                  )
            )
    END AS "menu_gross_margin",

    /* CT_P3_010: ratio is NULL for zero/missing net sales or incomplete COGS. */
    CASE
        WHEN S."net_sales_value" IS NULL OR S."net_sales_value" = 0
        THEN NULL
        WHEN COUNT(R."ingredient_code") = 0 THEN NULL
        WHEN
            SUM(
                CASE
                    WHEN R."ingredient_code" IS NOT NULL
                     AND C."ingredient_code" IS NOT NULL
                     AND RU."multiplier" IS NOT NULL
                     AND RU."multiplier" > 0
                     AND CU."multiplier" IS NOT NULL
                     AND CU."multiplier" > 0
                     AND COALESCE(RU."offset", 0) = 0
                     AND COALESCE(CU."offset", 0) = 0
                     AND LOWER(RU."conversion_status") LIKE 'approved%'
                     AND LOWER(CU."conversion_status") LIKE 'approved%'
                     AND LOWER(RU."to_unit") = LOWER(CU."to_unit")
                     AND C."source_average_unit_cost" IS NOT NULL
                    THEN 1 ELSE 0
                END
            ) <> COUNT(R."ingredient_code")
        THEN NULL
        ELSE
            (
                S."net_sales_value"
                -
                (
                    S."sold_menu_qty"
                    * SUM(
                        R."recipe_source_qty_per_menu_unit"
                        * RU."multiplier"
                        * (
                            C."source_average_unit_cost"
                            / CU."multiplier"
                          )
                      )
                )
            )
            / S."net_sales_value"
    END AS "menu_gross_margin_pct",

    /* Source-reported margin is recomputed from additive source measures. */
    S."net_sales_value" - S."source_reported_purchase_value"
        AS "source_net_margin_value",
    CASE
        WHEN S."net_sales_value" IS NULL OR S."net_sales_value" = 0
        THEN NULL
        ELSE
            (
                S."net_sales_value"
                - S."source_reported_purchase_value"
            )
            / S."net_sales_value"
    END AS "source_net_margin_pct_recomputed",
    S."gross_sales_value" - S."source_reported_purchase_value"
        AS "source_gross_margin_value",
    CASE
        WHEN S."gross_sales_value" IS NULL OR S."gross_sales_value" = 0
        THEN NULL
        ELSE
            (
                S."gross_sales_value"
                - S."source_reported_purchase_value"
            )
            / S."gross_sales_value"
    END AS "source_gross_margin_pct_recomputed",

    /* Positive means recipe-based COGS exceeds the source Purchase Value. */
    CASE
        WHEN COUNT(R."ingredient_code") = 0 THEN NULL
        WHEN
            SUM(
                CASE
                    WHEN R."ingredient_code" IS NOT NULL
                     AND C."ingredient_code" IS NOT NULL
                     AND RU."multiplier" IS NOT NULL
                     AND RU."multiplier" > 0
                     AND CU."multiplier" IS NOT NULL
                     AND CU."multiplier" > 0
                     AND COALESCE(RU."offset", 0) = 0
                     AND COALESCE(CU."offset", 0) = 0
                     AND LOWER(RU."conversion_status") LIKE 'approved%'
                     AND LOWER(CU."conversion_status") LIKE 'approved%'
                     AND LOWER(RU."to_unit") = LOWER(CU."to_unit")
                     AND C."source_average_unit_cost" IS NOT NULL
                    THEN 1 ELSE 0
                END
            ) <> COUNT(R."ingredient_code")
        THEN NULL
        ELSE
            (
                S."sold_menu_qty"
                * SUM(
                    R."recipe_source_qty_per_menu_unit"
                    * RU."multiplier"
                    * (
                        C."source_average_unit_cost"
                        / CU."multiplier"
                      )
                  )
            )
            - S."source_reported_purchase_value"
    END AS "theoretical_cogs_reconciliation_difference",
    CASE
        WHEN COUNT(R."ingredient_code") = 0 THEN NULL
        WHEN
            SUM(
                CASE
                    WHEN R."ingredient_code" IS NOT NULL
                     AND C."ingredient_code" IS NOT NULL
                     AND RU."multiplier" IS NOT NULL
                     AND RU."multiplier" > 0
                     AND CU."multiplier" IS NOT NULL
                     AND CU."multiplier" > 0
                     AND COALESCE(RU."offset", 0) = 0
                     AND COALESCE(CU."offset", 0) = 0
                     AND LOWER(RU."conversion_status") LIKE 'approved%'
                     AND LOWER(CU."conversion_status") LIKE 'approved%'
                     AND LOWER(RU."to_unit") = LOWER(CU."to_unit")
                     AND C."source_average_unit_cost" IS NOT NULL
                    THEN 1 ELSE 0
                END
            ) <> COUNT(R."ingredient_code")
        THEN NULL
        ELSE
            (
                S."net_sales_value"
                -
                (
                    S."sold_menu_qty"
                    * SUM(
                        R."recipe_source_qty_per_menu_unit"
                        * RU."multiplier"
                        * (
                            C."source_average_unit_cost"
                            / CU."multiplier"
                          )
                      )
                )
            )
            -
            (
                S."net_sales_value"
                - S."source_reported_purchase_value"
            )
    END AS "theoretical_margin_reconciliation_difference",
    S."source_sales_line_count" AS "source_sales_line_count",
    COUNT(R."ingredient_code") AS "recipe_line_count",
    SUM(
        CASE
            WHEN R."ingredient_code" IS NOT NULL
             AND C."ingredient_code" IS NOT NULL
             AND RU."multiplier" IS NOT NULL
             AND RU."multiplier" > 0
             AND CU."multiplier" IS NOT NULL
             AND CU."multiplier" > 0
             AND COALESCE(RU."offset", 0) = 0
             AND COALESCE(CU."offset", 0) = 0
             AND LOWER(RU."conversion_status") LIKE 'approved%'
             AND LOWER(CU."conversion_status") LIKE 'approved%'
             AND LOWER(RU."to_unit") = LOWER(CU."to_unit")
             AND C."source_average_unit_cost" IS NOT NULL
            THEN 1 ELSE 0
        END
    ) AS "costed_recipe_line_count",
    CASE
        WHEN COUNT(R."ingredient_code") = 0 THEN NULL
        ELSE
            SUM(
                CASE
                    WHEN R."ingredient_code" IS NOT NULL
                     AND C."ingredient_code" IS NOT NULL
                     AND RU."multiplier" IS NOT NULL
                     AND RU."multiplier" > 0
                     AND CU."multiplier" IS NOT NULL
                     AND CU."multiplier" > 0
                     AND COALESCE(RU."offset", 0) = 0
                     AND COALESCE(CU."offset", 0) = 0
                     AND LOWER(RU."conversion_status") LIKE 'approved%'
                     AND LOWER(CU."conversion_status") LIKE 'approved%'
                     AND LOWER(RU."to_unit") = LOWER(CU."to_unit")
                     AND C."source_average_unit_cost" IS NOT NULL
                    THEN 1 ELSE 0
                END
            )
            / COUNT(R."ingredient_code")
    END AS "recipe_cost_coverage_ratio",
    CASE
        WHEN COUNT(R."ingredient_code") = 0 THEN 'MISSING_RECIPE'
        WHEN
            SUM(
                CASE
                    WHEN R."ingredient_code" IS NOT NULL
                     AND C."ingredient_code" IS NOT NULL
                     AND RU."multiplier" IS NOT NULL
                     AND RU."multiplier" > 0
                     AND CU."multiplier" IS NOT NULL
                     AND CU."multiplier" > 0
                     AND COALESCE(RU."offset", 0) = 0
                     AND COALESCE(CU."offset", 0) = 0
                     AND LOWER(RU."conversion_status") LIKE 'approved%'
                     AND LOWER(CU."conversion_status") LIKE 'approved%'
                     AND LOWER(RU."to_unit") = LOWER(CU."to_unit")
                     AND C."source_average_unit_cost" IS NOT NULL
                    THEN 1 ELSE 0
                END
            ) <> COUNT(R."ingredient_code")
        THEN 'INCOMPLETE_RECIPE_COST'
        ELSE 'COMPLETE_RECIPE_COST'
    END AS "cost_evaluation_status_code",
    'ENTERPRISE_VARIANCE_PERIOD_AVERAGE_PRICE'
        AS "ingredient_cost_source_code",
    'SALE_DATE_WITHIN_OPENING_CLOSING_PERIOD'
        AS "ingredient_cost_date_rule_code",
    P."value_basis_code" AS "value_basis_code",
    P."bcg_quantity_cutoff_method" AS "bcg_quantity_cutoff_method",
    P."bcg_margin_cutoff_method" AS "bcg_margin_cutoff_method",
    'REPORT_SELECTED_SCOPE' AS "bcg_evaluation_stage_code",
    'CT_P3_001|CT_P3_002|CT_P3_004|CT_P3_009|CT_P3_010'
        AS "formula_id",
    P."formula_version" AS "formula_version",
    'RAW_Gross_Net_Margin|REF_Item_Recipe|RAW_Enterprise_Variance_Normal|CTL_UOM_Conversions|CTL_Rule_Parameters'
        AS "lineage_code"
FROM Sales_Daily S
LEFT JOIN Recipe_Lines R
  ON R."menu_item_code" = S."menu_item_code"
LEFT JOIN Ingredient_Cost_Period C
  ON C."outlet_name" = S."outlet_name"
 AND C."ingredient_code" = R."ingredient_code"
 AND S."sales_date" >= C."cost_period_start"
 AND S."sales_date" <= C."cost_period_end"
LEFT JOIN "CTL_UOM_Conversions" RU
  ON LOWER(TRIM(RU."from_unit")) = LOWER(TRIM(R."recipe_source_unit"))
 AND RU."effective_from" <= S."sales_date"
 AND (RU."effective_to" IS NULL OR RU."effective_to" >= S."sales_date")
LEFT JOIN "CTL_UOM_Conversions" CU
  ON LOWER(TRIM(CU."from_unit")) = LOWER(TRIM(C."cost_source_uom"))
 AND CU."effective_from" <= S."sales_date"
 AND (CU."effective_to" IS NULL OR CU."effective_to" >= S."sales_date")
LEFT JOIN
(
    SELECT
        P0."scope" AS "scope",
        P0."effective_from" AS "effective_from",
        P0."effective_to" AS "effective_to",
        MAX(
            CASE
                WHEN P0."parameter_id" = 'value_basis'
                THEN P0."parameter_value_text"
                ELSE NULL
            END
        ) AS "value_basis_code",
        MAX(
            CASE
                WHEN P0."parameter_id" = 'bcg_quantity_cutoff_method'
                THEN P0."parameter_value_text"
                ELSE NULL
            END
        ) AS "bcg_quantity_cutoff_method",
        MAX(
            CASE
                WHEN P0."parameter_id" = 'bcg_margin_cutoff_method'
                THEN P0."parameter_value_text"
                ELSE NULL
            END
        ) AS "bcg_margin_cutoff_method",
        MAX(P0."formula_version") AS "formula_version"
    FROM "CTL_Rule_Parameters" P0
    WHERE P0."active_flag" = 1
      AND P0."parameter_id" IN
          (
              'value_basis',
              'bcg_quantity_cutoff_method',
              'bcg_margin_cutoff_method'
          )
    GROUP BY
        P0."scope",
        P0."effective_from",
        P0."effective_to"
) P
  ON P."scope" = 'global'
 AND S."sales_date" >= P."effective_from"
 AND (P."effective_to" IS NULL OR S."sales_date" <= P."effective_to")
GROUP BY
    S."sales_date",
    S."outlet_name",
    S."menu_item_code",
    S."menu_item_name",
    S."super_category_name",
    S."category_name",
    S."sold_menu_qty",
    S."net_sales_value",
    S."gross_sales_value",
    S."source_reported_purchase_value",
    S."source_sales_line_count",
    P."value_basis_code",
    P."bcg_quantity_cutoff_method",
    P."bcg_margin_cutoff_method",
    P."formula_version";
