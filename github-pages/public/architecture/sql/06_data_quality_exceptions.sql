/*
Query Table : QT_06_Data_Quality_Exceptions
Level       : 2
Depends on  : QT_01A_Menu_Forecast, QT_06A_Return_DQ and raw/control tables
CTE count   : 3

Stable public exception output. Inventory/recipe, procurement and
expiry/vendor rules are evaluated directly here. Only the return-reconciliation
domain remains staged because it already requires all three permitted CTEs.
Grouped exception keys and the one-row formula version use explicit aggregates
so Zoho's strict GROUP BY resolver sees only the true business grain.
*/

WITH
params AS
(
    SELECT
        MAX(CASE WHEN "parameter_id" = 'forecast_horizon_days'
                 AND "active_flag" = 1
                 THEN "parameter_value_numeric" END) AS "forecast_horizon_days",
        MAX(CASE WHEN "parameter_id" = 'uom_tolerance'
                 AND "active_flag" = 1
                 THEN "parameter_value_numeric" END) AS "uom_tolerance",
        MAX(CASE WHEN "active_flag" = 1 THEN "formula_version" END)
            AS "formula_version"
    FROM "CTL_Rule_Parameters"
),
forecast_by_snapshot_item AS
(
    SELECT
        CAST(s."Date" AS DATE) AS "snapshot_date",
        s."Deployment" AS "outlet_name",
        s."Item Code" AS "item_code",
        SUM(
            f."forecast_menu_qty_daily"
            * CASE
                WHEN u."multiplier" IS NULL THEN NULL
                WHEN u."to_unit" IS NULL THEN NULL
                WHEN COALESCE(u."offset", 0) <> 0 THEN NULL
                WHEN u."conversion_status" IS NULL
                  OR LOWER(u."conversion_status") NOT LIKE 'approved%'
                THEN NULL
                ELSE r."Qty" * u."multiplier"
              END
        ) AS "forecast_required_qty"
    FROM "RAW_Closing_Stock" s
    CROSS JOIN params p
    JOIN "QT_01A_Menu_Forecast" f
      ON f."as_of_date" = CAST(s."Date" AS DATE)
     AND f."outlet_name" = s."Deployment"
     AND DATEDIFF(f."forecast_date", CAST(s."Date" AS DATE))
         BETWEEN 1 AND p."forecast_horizon_days"
    JOIN "REF_Item_Recipe" r
      ON r."Item Number" = f."menu_item_code"
     AND r."Ingredient Code" = s."Item Code"
     AND r."Item Number" IS NOT NULL
     AND r."Ingredient Code" IS NOT NULL
    LEFT JOIN "CTL_UOM_Conversions" u
      ON LOWER(TRIM(u."from_unit")) = LOWER(TRIM(r."Recipe Unit"))
     AND (
            u."effective_from" IS NULL
            OR u."effective_from" <= f."as_of_date"
         )
     AND (
            u."effective_to" IS NULL
            OR u."effective_to" >= f."as_of_date"
         )
    GROUP BY
        CAST(s."Date" AS DATE),
        s."Deployment",
        s."Item Code"
),
po_keys AS
(
    SELECT DISTINCT
        "Deployment" AS "outlet_name",
        "PO Number" AS "po_number",
        "Item Code" AS "item_code"
    FROM "RAW_Enterprise_Purchase_Order"
)
SELECT
    CONCAT(
        'DQ_NEG_STOCK|',
        CAST(s."Date" AS CHAR),
        '|',
        s."Deployment",
        '|',
        s."Item Code"
    ) AS "exception_id",
    CAST(s."Date" AS DATE) AS "exception_date",
    'SOURCE_ROW_DATE' AS "date_provenance",
    'DQ_NEGATIVE_STOCK' AS "rule_code",
    'INVENTORY_ITEM' AS "subject_type",
    s."Deployment" AS "outlet_name",
    'SOURCE_TOTAL' AS "store_name",
    s."Item Code" AS "item_code",
    s."Item Name" AS "item_name",
    'RAW_Closing_Stock' AS "source_table",
    CONCAT(
        CAST(s."Date" AS CHAR),
        '|',
        s."Deployment",
        '|',
        s."Item Code"
    ) AS "source_row_key",
    CAST(s."Total Qty" AS DECIMAL(18,6)) AS "actual_value",
    CAST(0 AS DECIMAL(18,6)) AS "threshold_value",
    -CAST(s."Total Qty" AS DECIMAL(18,6)) AS "gap_value",
    CAST(1 AS DECIMAL(18,6)) AS "eligible_denominator",
    1 AS "exception_flag",
    p."formula_version" AS "formula_version",
    'EVALUATED_EXCEPTION' AS "evaluation_status"
FROM "RAW_Closing_Stock" s
CROSS JOIN params p
WHERE CAST(s."Total Qty" AS DECIMAL(18,6)) < 0

UNION ALL

SELECT
    CONCAT(
        'DQ_ZERO_DEMAND|',
        CAST(s."Date" AS CHAR),
        '|',
        s."Deployment",
        '|',
        s."Item Code"
    ) AS "exception_id",
    CAST(s."Date" AS DATE) AS "exception_date",
    'SOURCE_ROW_DATE' AS "date_provenance",
    'DQ_ZERO_STOCK_POSITIVE_DEMAND' AS "rule_code",
    'INVENTORY_ITEM' AS "subject_type",
    s."Deployment" AS "outlet_name",
    'SOURCE_TOTAL' AS "store_name",
    s."Item Code" AS "item_code",
    s."Item Name" AS "item_name",
    'RAW_Closing_Stock;QT_01_Demand_Requirement' AS "source_table",
    CONCAT(
        CAST(s."Date" AS CHAR),
        '|',
        s."Deployment",
        '|',
        s."Item Code"
    ) AS "source_row_key",
    CAST(s."Total Qty" AS DECIMAL(18,6)) AS "actual_value",
    f."forecast_required_qty" AS "threshold_value",
    f."forecast_required_qty" AS "gap_value",
    CAST(1 AS DECIMAL(18,6)) AS "eligible_denominator",
    1 AS "exception_flag",
    p."formula_version" AS "formula_version",
    'EVALUATED_EXCEPTION' AS "evaluation_status"
FROM "RAW_Closing_Stock" s
CROSS JOIN params p
JOIN forecast_by_snapshot_item f
  ON f."snapshot_date" = CAST(s."Date" AS DATE)
 AND f."outlet_name" = s."Deployment"
 AND f."item_code" = s."Item Code"
WHERE CAST(s."Total Qty" AS DECIMAL(18,6)) = 0
  AND f."forecast_required_qty" > 0

UNION ALL

SELECT
    MAX(
        CONCAT(
            'DQ_RECIPE|',
            CAST(g."Date" AS DATE),
            '|',
            g."Store Name",
            '|',
            g."SKU Code / Item No"
        )
    ) AS "exception_id",
    CAST(g."Date" AS DATE) AS "exception_date",
    'SOURCE_ROW_DATE' AS "date_provenance",
    'DQ_SOLD_MENU_MISSING_RECIPE' AS "rule_code",
    'MENU_ITEM' AS "subject_type",
    g."Store Name" AS "outlet_name",
    CAST(NULL AS CHAR) AS "store_name",
    g."SKU Code / Item No" AS "item_code",
    MAX(g."SKU / Item Name") AS "item_name",
    'RAW_Gross_Net_Margin;REF_Item_Recipe' AS "source_table",
    MAX(
        CONCAT(
            CAST(g."Date" AS DATE),
            '|',
            g."Store Name",
            '|',
            g."SKU Code / Item No"
        )
    ) AS "source_row_key",
    SUM(CAST(g."Item Qty" AS DECIMAL(18,6))) AS "actual_value",
    CAST(0 AS DECIMAL(18,6)) AS "threshold_value",
    SUM(CAST(g."Item Qty" AS DECIMAL(18,6))) AS "gap_value",
    COUNT(*) AS "eligible_denominator",
    1 AS "exception_flag",
    MAX(p."formula_version") AS "formula_version",
    'EVALUATED_EXCEPTION' AS "evaluation_status"
FROM "RAW_Gross_Net_Margin" g
CROSS JOIN params p
LEFT JOIN "REF_Item_Recipe" r
  ON r."Item Number" = g."SKU Code / Item No"
WHERE CAST(g."Item Qty" AS DECIMAL(18,6)) > 0
  AND r."Item Number" IS NULL
GROUP BY
    CAST(g."Date" AS DATE),
    g."Store Name",
    g."SKU Code / Item No"

UNION ALL

SELECT
    CONCAT(
        'DQ_RECIPE_UOM|',
        r."Item Number",
        '|',
        r."Ingredient Code",
        '|',
        r."Recipe Unit"
    ) AS "exception_id",
    CAST(NULL AS DATE) AS "exception_date",
    'STATIC_UNMAPPED' AS "date_provenance",
    'DQ_RECIPE_UOM_UNMAPPED' AS "rule_code",
    'RECIPE_LINE' AS "subject_type",
    CAST(NULL AS CHAR) AS "outlet_name",
    CAST(NULL AS CHAR) AS "store_name",
    r."Ingredient Code" AS "item_code",
    r."Ingredient Name" AS "item_name",
    'REF_Item_Recipe;CTL_UOM_Conversions' AS "source_table",
    CONCAT(
        r."Item Number",
        '|',
        r."Ingredient Code",
        '|',
        r."Recipe Unit"
    ) AS "source_row_key",
    CAST(r."Qty" AS DECIMAL(18,6)) AS "actual_value",
    CAST(NULL AS DECIMAL(18,6)) AS "threshold_value",
    CAST(NULL AS DECIMAL(18,6)) AS "gap_value",
    CAST(1 AS DECIMAL(18,6)) AS "eligible_denominator",
    1 AS "exception_flag",
    p."formula_version" AS "formula_version",
    'EVALUATED_EXCEPTION' AS "evaluation_status"
FROM "REF_Item_Recipe" r
CROSS JOIN params p
LEFT JOIN "CTL_UOM_Conversions" u
  ON LOWER(TRIM(u."from_unit")) = LOWER(TRIM(r."Recipe Unit"))
 AND u."conversion_status" IN
     ('approved_identity', 'approved_mathematical', 'approved_alias')
WHERE u."from_unit" IS NULL

UNION ALL

SELECT
    CONCAT(
        'DQ_PO_DATE|',
        po."Deployment",
        '|',
        po."PO Number",
        '|',
        po."Item Code"
    ) AS "exception_id",
    CAST(po."PO Date" AS DATE) AS "exception_date",
    'SOURCE_ROW_DATE' AS "date_provenance",
    'DQ_OPEN_PO_MISSING_EXPECTED_DATE' AS "rule_code",
    'PO_LINE' AS "subject_type",
    po."Deployment" AS "outlet_name",
    po."Store Name" AS "store_name",
    po."Item Code" AS "item_code",
    po."Item Name" AS "item_name",
    'RAW_Enterprise_Purchase_Order' AS "source_table",
    CONCAT(po."PO Number", '|', po."Item Code") AS "source_row_key",
    CAST(po."Remaining Balance Qty" AS DECIMAL(18,6)) AS "actual_value",
    CAST(0 AS DECIMAL(18,6)) AS "threshold_value",
    CAST(po."Remaining Balance Qty" AS DECIMAL(18,6)) AS "gap_value",
    CAST(1 AS DECIMAL(18,6)) AS "eligible_denominator",
    1 AS "exception_flag",
    p."formula_version" AS "formula_version",
    'EVALUATED_EXCEPTION' AS "evaluation_status"
FROM "RAW_Enterprise_Purchase_Order" po
CROSS JOIN params p
WHERE CAST(po."Remaining Balance Qty" AS DECIMAL(18,6)) > 0
  AND LOWER(TRIM(po."PO Status")) IN
      ('open', 'partially received', 'partial', 'pending')
  AND COALESCE(TRIM(po."Expected Delivery"), '') = ''

UNION ALL

SELECT
    CONCAT(
        'DQ_PO_QTY|',
        po."Deployment",
        '|',
        po."PO Number",
        '|',
        po."Item Code"
    ) AS "exception_id",
    CAST(po."PO Date" AS DATE) AS "exception_date",
    'SOURCE_ROW_DATE' AS "date_provenance",
    'DQ_PO_QUANTITY_BRIDGE_FAILURE' AS "rule_code",
    'PO_LINE' AS "subject_type",
    po."Deployment" AS "outlet_name",
    po."Store Name" AS "store_name",
    po."Item Code" AS "item_code",
    po."Item Name" AS "item_name",
    'RAW_Enterprise_Purchase_Order' AS "source_table",
    CONCAT(po."PO Number", '|', po."Item Code") AS "source_row_key",
    CAST(po."Quantity" AS DECIMAL(18,6)) AS "actual_value",
    CAST(po."Total Processed Qty" AS DECIMAL(18,6))
      + CAST(po."Remaining Balance Qty" AS DECIMAL(18,6))
        AS "threshold_value",
    ABS(
        CAST(po."Quantity" AS DECIMAL(18,6))
        - CAST(po."Total Processed Qty" AS DECIMAL(18,6))
        - CAST(po."Remaining Balance Qty" AS DECIMAL(18,6))
    ) AS "gap_value",
    CAST(1 AS DECIMAL(18,6)) AS "eligible_denominator",
    1 AS "exception_flag",
    p."formula_version" AS "formula_version",
    'EVALUATED_EXCEPTION' AS "evaluation_status"
FROM "RAW_Enterprise_Purchase_Order" po
CROSS JOIN params p
WHERE ABS(
    CAST(po."Quantity" AS DECIMAL(18,6))
    - CAST(po."Total Processed Qty" AS DECIMAL(18,6))
    - CAST(po."Remaining Balance Qty" AS DECIMAL(18,6))
) > p."uom_tolerance"

UNION ALL

SELECT
    CONCAT(
        'DQ_RECEIPT_PO|',
        e."Deployment Name",
        '|',
        e."Transaction Number",
        '|',
        e."Item Code"
    ) AS "exception_id",
    CAST(e."Date" AS DATE) AS "exception_date",
    'SOURCE_ROW_DATE' AS "date_provenance",
    'DQ_RECEIPT_PO_UNMATCHED' AS "rule_code",
    'RECEIPT_LINE' AS "subject_type",
    e."Deployment Name" AS "outlet_name",
    e."Store/Kitchen Name" AS "store_name",
    e."Item Code" AS "item_code",
    e."Item Name" AS "item_name",
    'RAW_Enterprise_Entry;RAW_Enterprise_Purchase_Order' AS "source_table",
    CONCAT(e."Transaction Number", '|', e."Item Code") AS "source_row_key",
    CAST(e."Quantity" AS DECIMAL(18,6)) AS "actual_value",
    CAST(NULL AS DECIMAL(18,6)) AS "threshold_value",
    CAST(NULL AS DECIMAL(18,6)) AS "gap_value",
    CAST(1 AS DECIMAL(18,6)) AS "eligible_denominator",
    1 AS "exception_flag",
    p."formula_version" AS "formula_version",
    'EVALUATED_EXCEPTION' AS "evaluation_status"
FROM "RAW_Enterprise_Entry" e
CROSS JOIN params p
LEFT JOIN po_keys po
  ON po."outlet_name" = e."Deployment Name"
 AND po."po_number" = e."PO Number"
 AND po."item_code" = e."Item Code"
WHERE COALESCE(TRIM(e."PO Number"), '') <> ''
  AND po."po_number" IS NULL

UNION ALL

SELECT *
FROM "QT_06A_Return_DQ"

UNION ALL

SELECT
    CONCAT(
        'DQ_EXPIRY_LABEL|',
        CAST(e."As Of Date" AS CHAR),
        '|',
        e."Deployment Name",
        '|',
        e."Item Code",
        '|',
        e."Batch Number"
    ) AS "exception_id",
    CAST(e."As Of Date" AS DATE) AS "exception_date",
    'SOURCE_ROW_DATE' AS "date_provenance",
    'DQ_PROVISIONAL_EXPIRY_LABEL_INVALID' AS "rule_code",
    'PROVISIONAL_EXPIRY_ROW' AS "subject_type",
    e."Deployment Name" AS "outlet_name",
    e."Store Name" AS "store_name",
    e."Item Code" AS "item_code",
    e."Item Name" AS "item_name",
    'SYN_Provisional_Expiry_Report' AS "source_table",
    CONCAT(
        CAST(e."As Of Date" AS CHAR),
        '|',
        e."Deployment Name",
        '|',
        e."Item Code",
        '|',
        e."Batch Number"
    ) AS "source_row_key",
    CAST(0 AS DECIMAL(18,6)) AS "actual_value",
    CAST(1 AS DECIMAL(18,6)) AS "threshold_value",
    CAST(1 AS DECIMAL(18,6)) AS "gap_value",
    CAST(1 AS DECIMAL(18,6)) AS "eligible_denominator",
    1 AS "exception_flag",
    p."formula_version" AS "formula_version",
    'EVALUATED_EXCEPTION' AS "evaluation_status"
FROM "SYN_Provisional_Expiry_Report" e
CROSS JOIN params p
WHERE e."Data Status" <> 'PROVISIONAL_SYNTHETIC'
   OR e."Schema Status" <> 'ASSUMED_PENDING_POSIST_EXPORT'
   OR e."Display Label"
      <> 'PROVISIONAL SYNTHETIC EXPIRY DEMONSTRATION - NOT POSIST ACTUALS'

UNION ALL

SELECT
    MAX(CONCAT('DQ_VENDOR_ID|', "vendorCode")) AS "exception_id",
    CAST(NULL AS DATE) AS "exception_date",
    'STATIC_UNMAPPED' AS "date_provenance",
    'DQ_DUPLICATE_VENDOR_IDENTITY' AS "rule_code",
    'VENDOR' AS "subject_type",
    CAST(NULL AS CHAR) AS "outlet_name",
    CAST(NULL AS CHAR) AS "store_name",
    CAST(NULL AS CHAR) AS "item_code",
    CAST(NULL AS CHAR) AS "item_name",
    'REF_Vendor' AS "source_table",
    "vendorCode" AS "source_row_key",
    COUNT(DISTINCT "vendorName") AS "actual_value",
    CAST(1 AS DECIMAL(18,6)) AS "threshold_value",
    COUNT(DISTINCT "vendorName") - 1 AS "gap_value",
    COUNT(*) AS "eligible_denominator",
    1 AS "exception_flag",
    MAX(p."formula_version") AS "formula_version",
    'EVALUATED_EXCEPTION' AS "evaluation_status"
FROM "REF_Vendor"
CROSS JOIN params p
GROUP BY "vendorCode"
HAVING COUNT(DISTINCT "vendorName") > 1;
