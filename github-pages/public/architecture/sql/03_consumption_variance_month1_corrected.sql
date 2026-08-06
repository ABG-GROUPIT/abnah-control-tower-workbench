/*
Query Table : QT_03_Consumption_Variance
Layer       : DERIVED_L1 (raw/control inputs only)
Grain       : outlet_name + store_name + ingredient_code
              + reporting_period_end

Purpose
-------
Rebuild actual ingredient consumption at each physical stock checkpoint,
calculate separately the recipe-based theoretical quantity for the same
opening/closing interval, and compare the two without joining transaction
facts to one another.

Required Zoho tables (use these exact import names)
---------------------------------------------------
RAW_Enterprise_Consumption_Detail
RAW_Enterprise_Variance_Normal
RAW_Bill_Item_Detail
REF_Item_Recipe
CTL_UOM_Conversions
CTL_Rule_Parameters

Actual bridge (CT_P3_005)
-------------------------
opening
+ GRN/purchase
+ transfer in (indent receive + internal-indent receive + stock in)
- transfer out (indent dispatch + internal-indent dispatch + stock out)
- stock return
- closing

The source "Consumption Qty" and the source variance report's
"Actual Consumption" remain separate reconciliation evidence.  Wastage is
also exposed separately; it is not silently inserted into or removed from
the registered CT_P3_005 equation.

Null/zero rules
---------------
* An approved canonical UOM mapping is required before cross-report math.
  Missing, unapproved, non-positive, or non-zero-offset mappings yield NULL
  canonical measures and an explicit status code.
* Component arithmetic deliberately does not COALESCE missing bridge inputs
  to zero.  A real source zero remains zero; missing evidence propagates NULL.
* A complete sales interval with no matched ingredient recipe contributes
  zero theoretical quantity.  A matched recipe line with a bad UOM mapping
  makes theoretical quantity NULL, not partial.
* variance_pct is NULL when theoretical quantity is NULL or zero.
* Positive variance is leakage quantity.  Negative/zero variance has zero
  leakage value.  Positive variance with missing cost has NULL leakage value.
* Threshold values may remain NULL until approved.  No colour is fabricated.

Parameter behavior
------------------
The effective consumption thresholds and value-basis code are pivoted from
CTL_Rule_Parameters.  A control-table edit plus refresh changes the exposed
thresholds; the SQL contains no embedded Amber/Red percentages.

Zoho compatibility
------------------
This uses two non-recursive CTEs, ANSI joins, and Zoho date().  No Query Table
is an input, so the object remains dependency level 1.
*/

WITH
Actual_Bridge AS
(
    SELECT
        B."Deployment Name" AS "outlet_name",
        B."StoreKitchen Name" AS "store_name",
        B."Item Code" AS "ingredient_code",
        B."Item Name" AS "ingredient_name",
        B."Category Name" AS "category_name",
        B."Super Category Name" AS "super_category_name",
        date(B."Opening Date") AS "reporting_period_start",
        date(B."Closing Date") AS "reporting_period_end",
        B."Unit" AS "source_uom",
        CASE
            WHEN U."multiplier" IS NULL OR U."multiplier" <= 0 THEN NULL
            WHEN COALESCE(U."offset", 0) <> 0 THEN NULL
            WHEN U."conversion_status" IS NULL
              OR LOWER(U."conversion_status") NOT LIKE 'approved%'
            THEN NULL
            ELSE U."to_unit"
        END AS "canonical_uom",
        CASE
            WHEN U."multiplier" IS NULL OR U."multiplier" <= 0 THEN
                'MISSING_OR_NONPOSITIVE'
            WHEN COALESCE(U."offset", 0) <> 0 THEN
                'NONZERO_OFFSET_BLOCKED'
            WHEN U."conversion_status" IS NULL
              OR LOWER(U."conversion_status") NOT LIKE 'approved%' THEN
                'UNAPPROVED'
            ELSE 'APPROVED'
        END AS "uom_mapping_status",

        /* Component quantities are converted independently for auditability. */
        CASE
            WHEN U."multiplier" IS NULL OR U."multiplier" <= 0
              OR COALESCE(U."offset", 0) <> 0
              OR U."conversion_status" IS NULL
              OR LOWER(U."conversion_status") NOT LIKE 'approved%'
            THEN NULL
            ELSE B."Opening Qty" * U."multiplier"
        END AS "opening_qty_canonical",
        CASE
            WHEN U."multiplier" IS NULL OR U."multiplier" <= 0
              OR COALESCE(U."offset", 0) <> 0
              OR U."conversion_status" IS NULL
              OR LOWER(U."conversion_status") NOT LIKE 'approved%'
            THEN NULL
            ELSE B."Purchase Qty" * U."multiplier"
        END AS "grn_qty_canonical",
        CASE
            WHEN U."multiplier" IS NULL OR U."multiplier" <= 0
              OR COALESCE(U."offset", 0) <> 0
              OR U."conversion_status" IS NULL
              OR LOWER(U."conversion_status") NOT LIKE 'approved%'
            THEN NULL
            ELSE
                (
                    B."Indent Receive Qty"
                    + B."InternalIndent Receive Qty"
                    + B."Stock In Qty"
                ) * U."multiplier"
        END AS "transfer_in_qty_canonical",
        CASE
            WHEN U."multiplier" IS NULL OR U."multiplier" <= 0
              OR COALESCE(U."offset", 0) <> 0
              OR U."conversion_status" IS NULL
              OR LOWER(U."conversion_status") NOT LIKE 'approved%'
            THEN NULL
            ELSE
                (
                    B."Indent Dispatch Qty"
                    + B."InternalIndent Dispatch Qty"
                    + B."Stock Out Qty"
                ) * U."multiplier"
        END AS "transfer_out_qty_canonical",
        CASE
            WHEN U."multiplier" IS NULL OR U."multiplier" <= 0
              OR COALESCE(U."offset", 0) <> 0
              OR U."conversion_status" IS NULL
              OR LOWER(U."conversion_status") NOT LIKE 'approved%'
            THEN NULL
            ELSE B."Return Qty" * U."multiplier"
        END AS "stock_return_qty_canonical",
        CASE
            WHEN U."multiplier" IS NULL OR U."multiplier" <= 0
              OR COALESCE(U."offset", 0) <> 0
              OR U."conversion_status" IS NULL
              OR LOWER(U."conversion_status") NOT LIKE 'approved%'
            THEN NULL
            ELSE B."Closing Qty" * U."multiplier"
        END AS "closing_qty_canonical",
        CASE
            WHEN U."multiplier" IS NULL OR U."multiplier" <= 0
              OR COALESCE(U."offset", 0) <> 0
              OR U."conversion_status" IS NULL
              OR LOWER(U."conversion_status") NOT LIKE 'approved%'
            THEN NULL
            ELSE B."Wastage Qty" * U."multiplier"
        END AS "observed_wastage_qty_canonical",

        /* CT_P3_005.  Missing source components propagate NULL. */
        CASE
            WHEN U."multiplier" IS NULL OR U."multiplier" <= 0
              OR COALESCE(U."offset", 0) <> 0
              OR U."conversion_status" IS NULL
              OR LOWER(U."conversion_status") NOT LIKE 'approved%'
            THEN NULL
            ELSE
                (
                    B."Opening Qty"
                    + B."Purchase Qty"
                    + B."Indent Receive Qty"
                    + B."InternalIndent Receive Qty"
                    + B."Stock In Qty"
                    - B."Indent Dispatch Qty"
                    - B."InternalIndent Dispatch Qty"
                    - B."Stock Out Qty"
                    - B."Return Qty"
                    - B."Closing Qty"
                ) * U."multiplier"
        END AS "actual_consumption_qty",

        /* Source fields retained only as numerical reconciliation evidence. */
        CASE
            WHEN U."multiplier" IS NULL OR U."multiplier" <= 0
              OR COALESCE(U."offset", 0) <> 0
              OR U."conversion_status" IS NULL
              OR LOWER(U."conversion_status") NOT LIKE 'approved%'
            THEN NULL
            ELSE B."Consumption Qty" * U."multiplier"
        END AS "source_consumption_qty_canonical",
        CASE
            WHEN U."multiplier" IS NULL OR U."multiplier" <= 0
              OR COALESCE(U."offset", 0) <> 0
              OR U."conversion_status" IS NULL
              OR LOWER(U."conversion_status") NOT LIKE 'approved%'
            THEN NULL
            ELSE
                (B."Consumption Qty" + B."Wastage Qty")
                * U."multiplier"
        END AS "source_consumption_plus_wastage_qty_canonical",
        CASE
            WHEN V."Actual Consumption" IS NULL THEN NULL
            WHEN U."multiplier" IS NULL OR U."multiplier" <= 0
              OR COALESCE(U."offset", 0) <> 0
              OR U."conversion_status" IS NULL
              OR LOWER(U."conversion_status") NOT LIKE 'approved%'
            THEN NULL
            ELSE V."Actual Consumption" * U."multiplier"
        END AS "source_reported_actual_consumption_qty",
        CASE
            WHEN U."multiplier" IS NULL OR U."multiplier" <= 0
              OR COALESCE(U."offset", 0) <> 0
              OR U."conversion_status" IS NULL
              OR LOWER(U."conversion_status") NOT LIKE 'approved%'
            THEN NULL
            ELSE B."Average Price" / U."multiplier"
        END AS "normalized_average_unit_cost",
        B."Average Price" AS "source_average_unit_cost",
        CASE WHEN V."Item Code" IS NULL THEN 0 ELSE 1 END
            AS "source_variance_reconciliation_row_count"
    FROM "RAW_Enterprise_Consumption_Detail" B
    LEFT JOIN "RAW_Enterprise_Variance_Normal" V
      ON V."Deployment Name" = B."Deployment Name"
     AND V."StoreKitchen Name" = B."StoreKitchen Name"
     AND V."Item Code" = B."Item Code"
     AND date(V."Opening Date") = date(B."Opening Date")
     AND date(V."Closing Date") = date(B."Closing Date")
    LEFT JOIN "CTL_UOM_Conversions" U
      ON LOWER(TRIM(U."from_unit")) = LOWER(TRIM(B."Unit"))
     AND U."effective_from" <= date(B."Closing Date")
     AND (U."effective_to" IS NULL
          OR U."effective_to" >= date(B."Closing Date"))
    WHERE B."Deployment Name" IS NOT NULL
      AND B."StoreKitchen Name" IS NOT NULL
      AND B."Item Code" IS NOT NULL
      AND B."Opening Date" IS NOT NULL
      AND B."Closing Date" IS NOT NULL
),
Theoretical_By_Checkpoint AS
(
    SELECT
        B."Deployment Name" AS "outlet_name",
        B."StoreKitchen Name" AS "store_name",
        B."Item Code" AS "ingredient_code",
        date(B."Opening Date") AS "reporting_period_start",
        date(B."Closing Date") AS "reporting_period_end",
        MAX(
            CASE
                WHEN BU."multiplier" IS NULL OR BU."multiplier" <= 0
                  OR COALESCE(BU."offset", 0) <> 0
                  OR BU."conversion_status" IS NULL
                  OR LOWER(BU."conversion_status") NOT LIKE 'approved%'
                THEN NULL
                ELSE BU."to_unit"
            END
        ) AS "canonical_uom",
        COUNT(S."billNumber") AS "sales_line_count",
        COUNT(DISTINCT S."Item Number") AS "sold_menu_item_count",
        SUM(
            CASE WHEN R."Ingredient Code" IS NOT NULL
                 THEN 1 ELSE 0 END
        ) AS "matched_recipe_line_count",
        SUM(
            CASE
                WHEN R."Ingredient Code" IS NOT NULL
                 AND RU."multiplier" IS NOT NULL
                 AND RU."multiplier" > 0
                 AND BU."multiplier" IS NOT NULL
                 AND BU."multiplier" > 0
                 AND COALESCE(RU."offset", 0) = 0
                 AND COALESCE(BU."offset", 0) = 0
                 AND LOWER(RU."conversion_status") LIKE 'approved%'
                 AND LOWER(BU."conversion_status") LIKE 'approved%'
                 AND LOWER(RU."to_unit") = LOWER(BU."to_unit")
                THEN 1 ELSE 0
            END
        ) AS "valid_recipe_uom_line_count",
        SUM(
            CASE
                WHEN R."Ingredient Code" IS NOT NULL
                 AND
                     (
                         RU."multiplier" IS NULL
                         OR RU."multiplier" <= 0
                         OR BU."multiplier" IS NULL
                         OR BU."multiplier" <= 0
                         OR COALESCE(RU."offset", 0) <> 0
                         OR COALESCE(BU."offset", 0) <> 0
                         OR RU."conversion_status" IS NULL
                         OR BU."conversion_status" IS NULL
                         OR LOWER(RU."conversion_status") NOT LIKE 'approved%'
                         OR LOWER(BU."conversion_status") NOT LIKE 'approved%'
                         OR LOWER(RU."to_unit") <> LOWER(BU."to_unit")
                     )
                THEN 1 ELSE 0
            END
        ) AS "invalid_recipe_uom_line_count",

        /* CT_P3_003: recipe explosion occurs only after interval alignment. */
        CASE
            WHEN COUNT(S."billNumber") = 0 THEN NULL
            WHEN
                SUM(
                    CASE
                        WHEN R."Ingredient Code" IS NOT NULL
                         AND
                             (
                                 RU."multiplier" IS NULL
                                 OR RU."multiplier" <= 0
                                 OR BU."multiplier" IS NULL
                                 OR BU."multiplier" <= 0
                                 OR COALESCE(RU."offset", 0) <> 0
                                 OR COALESCE(BU."offset", 0) <> 0
                                 OR RU."conversion_status" IS NULL
                                 OR BU."conversion_status" IS NULL
                                 OR LOWER(RU."conversion_status")
                                    NOT LIKE 'approved%'
                                 OR LOWER(BU."conversion_status")
                                    NOT LIKE 'approved%'
                                 OR LOWER(RU."to_unit") <> LOWER(BU."to_unit")
                             )
                        THEN 1 ELSE 0
                    END
                ) > 0
            THEN NULL
            ELSE
                SUM(
                    CASE
                        WHEN R."Ingredient Code" IS NOT NULL
                        THEN
                            S."Qty"
                            * R."Qty"
                            * RU."multiplier"
                        ELSE 0
                    END
                )
        END AS "theoretical_consumption_qty"
    FROM "RAW_Enterprise_Consumption_Detail" B
    LEFT JOIN "RAW_Bill_Item_Detail" S
      ON S."Deployment" = B."Deployment Name"
     AND date(S."Close Time") >= date(B."Opening Date")
     AND date(S."Close Time") <= date(B."Closing Date")
    LEFT JOIN "REF_Item_Recipe" R
      ON R."Item Number" = S."Item Number"
     AND R."Ingredient Code" = B."Item Code"
    LEFT JOIN "CTL_UOM_Conversions" RU
      ON LOWER(TRIM(RU."from_unit")) = LOWER(TRIM(R."Recipe Unit"))
     AND RU."effective_from" <= date(S."Close Time")
     AND (RU."effective_to" IS NULL
          OR RU."effective_to" >= date(S."Close Time"))
    LEFT JOIN "CTL_UOM_Conversions" BU
      ON LOWER(TRIM(BU."from_unit")) = LOWER(TRIM(B."Unit"))
     AND BU."effective_from" <= date(B."Closing Date")
     AND (BU."effective_to" IS NULL
          OR BU."effective_to" >= date(B."Closing Date"))
    WHERE B."Deployment Name" IS NOT NULL
      AND B."StoreKitchen Name" IS NOT NULL
      AND B."Item Code" IS NOT NULL
      AND B."Opening Date" IS NOT NULL
      AND B."Closing Date" IS NOT NULL
    GROUP BY
        B."Deployment Name",
        B."StoreKitchen Name",
        B."Item Code",
        date(B."Opening Date"),
        date(B."Closing Date")
)
SELECT
    B."reporting_period_start" AS "reporting_period_start",
    B."reporting_period_end" AS "reporting_period_end",
    B."outlet_name" AS "outlet_name",
    B."store_name" AS "store_name",
    B."ingredient_code" AS "ingredient_code",
    B."ingredient_name" AS "ingredient_name",
    B."category_name" AS "category_name",
    B."super_category_name" AS "super_category_name",
    B."source_uom" AS "source_uom",
    B."canonical_uom" AS "canonical_uom",
    B."uom_mapping_status" AS "uom_mapping_status",
    B."opening_qty_canonical" AS "opening_qty_canonical",
    B."grn_qty_canonical" AS "grn_qty_canonical",
    B."transfer_in_qty_canonical" AS "transfer_in_qty_canonical",
    B."transfer_out_qty_canonical" AS "transfer_out_qty_canonical",
    B."stock_return_qty_canonical" AS "stock_return_qty_canonical",
    B."closing_qty_canonical" AS "closing_qty_canonical",

    /*
    Presentation-safe signed bridge components.
    Keep the original positive source measures above for source reconciliation.
    These signed fields are the only fields approved for the P3-006 equation
    visual, and the report must still filter to one ingredient/canonical UOM.
    */
    B."opening_qty_canonical" AS "bridge_opening_qty_signed",
    B."grn_qty_canonical" AS "bridge_grn_qty_signed",
    B."transfer_in_qty_canonical" AS "bridge_transfer_in_qty_signed",
    -B."transfer_out_qty_canonical" AS "bridge_transfer_out_qty_signed",
    -B."stock_return_qty_canonical" AS "bridge_stock_return_qty_signed",
    -B."closing_qty_canonical" AS "bridge_closing_qty_signed",

    B."observed_wastage_qty_canonical"
        AS "observed_wastage_qty_canonical",
    B."actual_consumption_qty" AS "actual_consumption_qty",
    B."source_consumption_qty_canonical"
        AS "source_consumption_qty_canonical",
    B."source_consumption_plus_wastage_qty_canonical"
        AS "source_consumption_plus_wastage_qty_canonical",
    B."source_reported_actual_consumption_qty"
        AS "source_reported_actual_consumption_qty",
    CASE
        WHEN B."actual_consumption_qty" IS NULL
          OR B."source_reported_actual_consumption_qty" IS NULL
        THEN NULL
        ELSE
            B."actual_consumption_qty"
            - B."source_reported_actual_consumption_qty"
    END AS "actual_reconciliation_difference_qty",
    T."theoretical_consumption_qty" AS "theoretical_consumption_qty",

    /* CT_P3_006: positive means actual exceeds theoretical. */
    CASE
        WHEN B."actual_consumption_qty" IS NULL
          OR T."theoretical_consumption_qty" IS NULL
        THEN NULL
        ELSE
            B."actual_consumption_qty"
            - T."theoretical_consumption_qty"
    END AS "consumption_variance_qty",
    CASE
        WHEN B."actual_consumption_qty" IS NULL
          OR T."theoretical_consumption_qty" IS NULL
          OR T."theoretical_consumption_qty" = 0
        THEN NULL
        ELSE
            (
                B."actual_consumption_qty"
                - T."theoretical_consumption_qty"
            )
            / T."theoretical_consumption_qty"
    END AS "consumption_variance_pct",

    /* CT_P3_007: value is partial only when positive variance has a cost. */
    CASE
        WHEN B."actual_consumption_qty" IS NULL
          OR T."theoretical_consumption_qty" IS NULL
        THEN NULL
        WHEN
            B."actual_consumption_qty"
            - T."theoretical_consumption_qty" <= 0
        THEN 0
        WHEN B."normalized_average_unit_cost" IS NULL
        THEN NULL
        ELSE
            (
                B."actual_consumption_qty"
                - T."theoretical_consumption_qty"
            )
            * B."normalized_average_unit_cost"
    END AS "consumption_leakage_value",

    /* CT_P3_008: numerical data check only; never an attributed saving. */
    CASE
        WHEN B."actual_consumption_qty" IS NULL
          OR T."theoretical_consumption_qty" IS NULL
        THEN NULL
        WHEN
            T."theoretical_consumption_qty"
            - B."actual_consumption_qty" > 0
        THEN
            T."theoretical_consumption_qty"
            - B."actual_consumption_qty"
        ELSE 0
    END AS "low_consumption_check_qty",
    B."source_average_unit_cost" AS "source_average_unit_cost",
    B."normalized_average_unit_cost" AS "normalized_average_unit_cost",
    T."sales_line_count" AS "sales_line_count",
    T."sold_menu_item_count" AS "sold_menu_item_count",
    T."matched_recipe_line_count" AS "matched_recipe_line_count",
    T."valid_recipe_uom_line_count" AS "valid_recipe_uom_line_count",
    T."invalid_recipe_uom_line_count" AS "invalid_recipe_uom_line_count",
    CASE
        WHEN T."matched_recipe_line_count" IS NULL
          OR T."matched_recipe_line_count" = 0
        THEN NULL
        ELSE
            T."valid_recipe_uom_line_count"
            / T."matched_recipe_line_count"
    END AS "theoretical_recipe_uom_coverage_ratio",
    CASE
        WHEN T."sales_line_count" IS NULL OR T."sales_line_count" = 0
        THEN 'NO_SALES_EVIDENCE'
        WHEN T."invalid_recipe_uom_line_count" > 0
        THEN 'INVALID_RECIPE_UOM'
        WHEN T."matched_recipe_line_count" = 0
        THEN 'OBSERVED_ZERO_MATCHED_INGREDIENT_DEMAND'
        ELSE 'EVALUATED'
    END AS "theoretical_evaluation_status_code",
    B."source_variance_reconciliation_row_count"
        AS "source_variance_reconciliation_row_count",
    P."consumption_variance_amber_pct"
        AS "consumption_variance_amber_threshold",
    P."consumption_variance_red_pct"
        AS "consumption_variance_red_threshold",
    CASE
        WHEN P."consumption_variance_amber_pct" IS NULL
          OR P."consumption_variance_red_pct" IS NULL
        THEN 'THRESHOLDS_UNAPPROVED'
        ELSE 'THRESHOLDS_AVAILABLE'
    END AS "threshold_evaluation_status_code",
    P."value_basis_code" AS "value_basis_code",
    'CT_P3_003|CT_P3_005|CT_P3_006|CT_P3_007|CT_P3_008|CT_P3_011'
        AS "formula_id",
    P."formula_version" AS "formula_version",
    'RAW_Enterprise_Consumption_Detail|RAW_Enterprise_Variance_Normal|RAW_Bill_Item_Detail|REF_Item_Recipe|CTL_UOM_Conversions|CTL_Rule_Parameters'
        AS "lineage_code"
FROM Actual_Bridge B
LEFT JOIN Theoretical_By_Checkpoint T
  ON T."outlet_name" = B."outlet_name"
 AND T."store_name" = B."store_name"
 AND T."ingredient_code" = B."ingredient_code"
 AND T."reporting_period_start" = B."reporting_period_start"
 AND T."reporting_period_end" = B."reporting_period_end"
LEFT JOIN
(
    SELECT
        P0."scope" AS "scope",
        P0."effective_from" AS "effective_from",
        P0."effective_to" AS "effective_to",
        MAX(
            CASE
                WHEN P0."parameter_id" = 'consumption_variance_amber_pct'
                THEN P0."parameter_value_numeric"
                ELSE NULL
            END
        ) AS "consumption_variance_amber_pct",
        MAX(
            CASE
                WHEN P0."parameter_id" = 'consumption_variance_red_pct'
                THEN P0."parameter_value_numeric"
                ELSE NULL
            END
        ) AS "consumption_variance_red_pct",
        MAX(
            CASE
                WHEN P0."parameter_id" = 'value_basis'
                THEN P0."parameter_value_text"
                ELSE NULL
            END
        ) AS "value_basis_code",
        MAX(P0."formula_version") AS "formula_version"
    FROM "CTL_Rule_Parameters" P0
    WHERE P0."active_flag" = 1
      AND P0."parameter_id" IN
          (
              'consumption_variance_amber_pct',
              'consumption_variance_red_pct',
              'value_basis'
          )
    GROUP BY
        P0."scope",
        P0."effective_from",
        P0."effective_to"
) P
  ON P."scope" = 'global'
 AND B."reporting_period_end" >= P."effective_from"
 AND (P."effective_to" IS NULL
      OR B."reporting_period_end" <= P."effective_to");
