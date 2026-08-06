/*
Query Table : QT_06A_Return_DQ
Level       : 1
Depends on  : raw stock returns, bulk returns, entries and rule controls
CTE count   : 3

Return linkage, quantity, value and report-reconciliation exceptions.
*/

WITH
params AS
(
    SELECT
        MAX(CASE WHEN "parameter_id" = 'uom_tolerance'
                 AND "active_flag" = 1
                 THEN "parameter_value_numeric" END) AS "uom_tolerance",
        MAX(CASE WHEN "parameter_id" = 'reconciliation_value_tolerance'
                 AND "active_flag" = 1
                 THEN "parameter_value_numeric" END)
            AS "reconciliation_value_tolerance",
        MAX(CASE WHEN "active_flag" = 1 THEN "formula_version" END)
            AS "formula_version"
    FROM "CTL_Rule_Parameters"
),
bulk_return_totals AS
(
    SELECT
        "Deployment Name" AS "outlet_name",
        CAST("Date" AS DATE) AS "return_date",
        "Item Code" AS "item_code",
        SUM(CAST("Quantity" AS DECIMAL(18,6))) AS "bulk_return_qty"
    FROM "RAW_Bulk_Return"
    GROUP BY
        "Deployment Name",
        CAST("Date" AS DATE),
        "Item Code"
),
stock_return_totals AS
(
    SELECT
        "Deployment Name" AS "outlet_name",
        CAST("Return Date" AS DATE) AS "return_date",
        "Item Code" AS "item_code",
        SUM(CAST("Return Qty" AS DECIMAL(18,6))) AS "stock_return_qty"
    FROM "RAW_Enterprise_Stock_Return"
    GROUP BY
        "Deployment Name",
        CAST("Return Date" AS DATE),
        "Item Code"
)
SELECT
    CONCAT(
        'DQ_RETURN_ENTRY|',
        r."Deployment Name",
        '|',
        r."Transaction Number",
        '|',
        r."Item Code",
        '|',
        CAST(r."Return Date" AS CHAR)
    ) AS "exception_id",
    CAST(r."Return Date" AS DATE) AS "exception_date",
    'SOURCE_ROW_DATE' AS "date_provenance",
    'DQ_RETURN_ENTRY_UNMATCHED' AS "rule_code",
    'RETURN_LINE' AS "subject_type",
    r."Deployment Name" AS "outlet_name",
    r."Store Name" AS "store_name",
    r."Item Code" AS "item_code",
    r."Item Name" AS "item_name",
    'RAW_Enterprise_Stock_Return;RAW_Enterprise_Entry' AS "source_table",
    CONCAT(
        r."Transaction Number",
        '|',
        r."Item Code",
        '|',
        CAST(r."Return Date" AS CHAR)
    ) AS "source_row_key",
    CAST(r."Return Qty" AS DECIMAL(18,6)) AS "actual_value",
    CAST(NULL AS DECIMAL(18,6)) AS "threshold_value",
    CAST(NULL AS DECIMAL(18,6)) AS "gap_value",
    CAST(1 AS DECIMAL(18,6)) AS "eligible_denominator",
    1 AS "exception_flag",
    p."formula_version",
    'EVALUATED_EXCEPTION' AS "evaluation_status"
FROM "RAW_Enterprise_Stock_Return" r
CROSS JOIN params p
LEFT JOIN "RAW_Enterprise_Entry" e
  ON e."Deployment Name" = r."Deployment Name"
 AND e."Store/Kitchen Name" = r."Store Name"
 AND CAST(e."Date" AS DATE) = CAST(r."Stock Entry Date" AS DATE)
 AND e."Transaction Number" = r."Transaction Number"
 AND e."Item Code" = r."Item Code"
WHERE e."Transaction Number" IS NULL

UNION ALL

SELECT
    CONCAT(
        'DQ_RETURN_QTY|',
        r."Deployment Name",
        '|',
        r."Transaction Number",
        '|',
        r."Item Code",
        '|',
        CAST(r."Return Date" AS CHAR)
    ) AS "exception_id",
    CAST(r."Return Date" AS DATE) AS "exception_date",
    'SOURCE_ROW_DATE' AS "date_provenance",
    'DQ_RETURN_QTY_ABOVE_ENTRY' AS "rule_code",
    'RETURN_LINE' AS "subject_type",
    r."Deployment Name" AS "outlet_name",
    r."Store Name" AS "store_name",
    r."Item Code" AS "item_code",
    r."Item Name" AS "item_name",
    'RAW_Enterprise_Stock_Return' AS "source_table",
    CONCAT(
        r."Transaction Number",
        '|',
        r."Item Code",
        '|',
        CAST(r."Return Date" AS CHAR)
    ) AS "source_row_key",
    CAST(r."Return Qty" AS DECIMAL(18,6)) AS "actual_value",
    CAST(r."Entry Qty" AS DECIMAL(18,6)) AS "threshold_value",
    CAST(r."Return Qty" AS DECIMAL(18,6))
      - CAST(r."Entry Qty" AS DECIMAL(18,6)) AS "gap_value",
    CAST(1 AS DECIMAL(18,6)) AS "eligible_denominator",
    1 AS "exception_flag",
    p."formula_version",
    'EVALUATED_EXCEPTION' AS "evaluation_status"
FROM "RAW_Enterprise_Stock_Return" r
CROSS JOIN params p
WHERE CAST(r."Return Qty" AS DECIMAL(18,6))
    > CAST(r."Entry Qty" AS DECIMAL(18,6)) + p."uom_tolerance"

UNION ALL

SELECT
    CONCAT(
        'DQ_RETURN_AMT|',
        r."Deployment Name",
        '|',
        r."Transaction Number",
        '|',
        r."Item Code",
        '|',
        CAST(r."Return Date" AS CHAR)
    ) AS "exception_id",
    CAST(r."Return Date" AS DATE) AS "exception_date",
    'SOURCE_ROW_DATE' AS "date_provenance",
    'DQ_RETURN_AMOUNT_BRIDGE_FAILURE' AS "rule_code",
    'RETURN_LINE' AS "subject_type",
    r."Deployment Name" AS "outlet_name",
    r."Store Name" AS "store_name",
    r."Item Code" AS "item_code",
    r."Item Name" AS "item_name",
    'RAW_Enterprise_Stock_Return' AS "source_table",
    CONCAT(
        r."Transaction Number",
        '|',
        r."Item Code",
        '|',
        CAST(r."Return Date" AS CHAR)
    ) AS "source_row_key",
    CAST(r."Return Amount" AS DECIMAL(18,2)) AS "actual_value",
    CAST(r."Return SubTotal" AS DECIMAL(18,2))
      - CAST(r."Return Discount" AS DECIMAL(18,2))
      + CAST(r."Return CGST" AS DECIMAL(18,2))
      + CAST(r."Return SGST" AS DECIMAL(18,2))
      + CAST(r."Return IGST" AS DECIMAL(18,2))
      + CAST(r."Return Non GST" AS DECIMAL(18,2))
        AS "threshold_value",
    ABS(
        CAST(r."Return Amount" AS DECIMAL(18,2))
        - CAST(r."Return SubTotal" AS DECIMAL(18,2))
        + CAST(r."Return Discount" AS DECIMAL(18,2))
        - CAST(r."Return CGST" AS DECIMAL(18,2))
        - CAST(r."Return SGST" AS DECIMAL(18,2))
        - CAST(r."Return IGST" AS DECIMAL(18,2))
        - CAST(r."Return Non GST" AS DECIMAL(18,2))
    ) AS "gap_value",
    CAST(1 AS DECIMAL(18,6)) AS "eligible_denominator",
    1 AS "exception_flag",
    p."formula_version",
    'EVALUATED_EXCEPTION' AS "evaluation_status"
FROM "RAW_Enterprise_Stock_Return" r
CROSS JOIN params p
WHERE ABS(
    CAST(r."Return Amount" AS DECIMAL(18,2))
    - CAST(r."Return SubTotal" AS DECIMAL(18,2))
    + CAST(r."Return Discount" AS DECIMAL(18,2))
    - CAST(r."Return CGST" AS DECIMAL(18,2))
    - CAST(r."Return SGST" AS DECIMAL(18,2))
    - CAST(r."Return IGST" AS DECIMAL(18,2))
    - CAST(r."Return Non GST" AS DECIMAL(18,2))
) > p."reconciliation_value_tolerance"

UNION ALL

SELECT
    CONCAT(
        'DQ_RETURN_REPORT|',
        b."outlet_name",
        '|',
        CAST(b."return_date" AS CHAR),
        '|',
        b."item_code"
    ) AS "exception_id",
    b."return_date" AS "exception_date",
    'SOURCE_ROW_DATE' AS "date_provenance",
    'DQ_RETURN_REPORT_QUANTITY_MISMATCH' AS "rule_code",
    'RETURN_RECONCILIATION' AS "subject_type",
    b."outlet_name",
    CAST(NULL AS CHAR) AS "store_name",
    b."item_code",
    CAST(NULL AS CHAR) AS "item_name",
    'RAW_Bulk_Return;RAW_Enterprise_Stock_Return' AS "source_table",
    CONCAT(
        b."outlet_name",
        '|',
        CAST(b."return_date" AS CHAR),
        '|',
        b."item_code"
    ) AS "source_row_key",
    b."bulk_return_qty" AS "actual_value",
    COALESCE(s."stock_return_qty", 0) AS "threshold_value",
    ABS(b."bulk_return_qty" - COALESCE(s."stock_return_qty", 0))
        AS "gap_value",
    CAST(1 AS DECIMAL(18,6)) AS "eligible_denominator",
    1 AS "exception_flag",
    p."formula_version",
    'EVALUATED_EXCEPTION' AS "evaluation_status"
FROM bulk_return_totals b
CROSS JOIN params p
LEFT JOIN stock_return_totals s
  ON s."outlet_name" = b."outlet_name"
 AND s."return_date" = b."return_date"
 AND s."item_code" = b."item_code"
WHERE ABS(b."bulk_return_qty" - COALESCE(s."stock_return_qty", 0))
    > p."uom_tolerance";
