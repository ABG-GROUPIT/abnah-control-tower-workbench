-- Query Table: 34_fact_ct_data_quality_exception.sql
-- Logical model name: FACT_CT_Data_Quality_Exception
-- Layer: fact
-- Purpose: Produce drillable Page 4 exception rows with period, outlet and source references.
-- Sources: 05_std_ct_inventory_snapshot.sql, 26_fact_ct_forecast_ingredient_demand.sql, 01_std_ct_sales_item.sql, 02_std_ct_recipe.sql, 22_fact_ct_purchase_order.sql, 07_std_ct_purchase_order.sql, 08_std_ct_purchase_receipt.sql, 06_std_ct_inventory_movement.sql, 10_std_ct_vendor_report.sql, 14_dim_ct_item.sql
-- Validate CAST/date function behavior once in the target Zoho workspace.
SELECT
    "source_period_code" AS "source_period_code",
    "outlet_code" AS "outlet_code",
    "outlet_name" AS "outlet_name",
    'NEGATIVE_STOCK' AS "exception_type",
    CONCAT("source_period_code", ':', "outlet_code", ':', "item_code")
      AS "exception_record_key",
    "item_code" AS "item_code",
    '' AS "reference_number",
    1 AS "exception_count",
    'Closing quantity below zero' AS "definition"
FROM "05_std_ct_inventory_snapshot.sql"
WHERE "closing_qty" < 0
UNION ALL
SELECT
    s."source_period_code" AS "source_period_code",
    s."outlet_code" AS "outlet_code",
    s."outlet_name" AS "outlet_name",
    'ZERO_STOCK_WITH_DEMAND',
    CONCAT(s."source_period_code", ':', s."outlet_code", ':', s."item_code"),
    s."item_code" AS "item_code",
    '',
    1,
    'Zero closing stock with positive seven-day forecast ingredient demand'
FROM "05_std_ct_inventory_snapshot.sql" s
INNER JOIN (
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
WHERE s."closing_qty" = 0
  AND f."forecast_required_qty" > 0
UNION ALL
SELECT DISTINCT
    s."source_period_code" AS "source_period_code",
    s."outlet_code" AS "outlet_code",
    s."outlet_name" AS "outlet_name",
    'SOLD_ITEM_MISSING_RECIPE',
    CONCAT(s."source_period_code", ':', s."outlet_code", ':', s."item_code"),
    s."item_code" AS "item_code",
    '',
    1,
    'Sold menu item without a recipe mapping'
FROM "01_std_ct_sales_item.sql" s
LEFT JOIN "02_std_ct_recipe.sql" r
  ON s."item_code" = r."menu_item_code"
WHERE r."menu_item_code" IS NULL
UNION ALL
SELECT
    "source_period_code" AS "source_period_code",
    "outlet_code" AS "outlet_code",
    MAX("outlet_name") AS "outlet_name",
    'OPEN_PO_MISSING_EXPECTED_DELIVERY',
    CONCAT("source_period_code", ':', "outlet_code", ':', "po_number"),
    '' AS "item_code",
    "po_number" AS "reference_number",
    1,
    'Open PO without expected delivery date'
FROM "22_fact_ct_purchase_order.sql"
WHERE "missing_expected_delivery_flag" = 1
GROUP BY "source_period_code", "outlet_code", "po_number"
UNION ALL
SELECT DISTINCT
    x."source_period_code" AS "source_period_code",
    x."outlet_code" AS "outlet_code",
    x."outlet_name" AS "outlet_name",
    'OPERATIONAL_ITEM_MISSING_MASTER',
    CONCAT(x."source_period_code", ':', x."outlet_code", ':', x."item_code"),
    x."item_code" AS "item_code",
    '',
    1,
    'Operational item identifier absent from the canonical item master'
FROM (
    SELECT
        "source_period_code" AS "source_period_code",
        "outlet_code" AS "outlet_code",
        "outlet_name" AS "outlet_name",
        "item_code" AS "item_code"
    FROM "05_std_ct_inventory_snapshot.sql"
    UNION ALL
    SELECT
        "source_period_code" AS "source_period_code",
        "outlet_code" AS "outlet_code",
        "outlet_name" AS "outlet_name",
        "item_code" AS "item_code"
    FROM "22_fact_ct_purchase_order.sql"
    UNION ALL
    SELECT
        "source_period_code" AS "source_period_code",
        "outlet_code" AS "outlet_code",
        "outlet_name" AS "outlet_name",
        "item_code" AS "item_code"
    FROM "08_std_ct_purchase_receipt.sql"
    UNION ALL
    SELECT
        "source_period_code" AS "source_period_code",
        "outlet_code" AS "outlet_code",
        "outlet_name" AS "outlet_name",
        "item_code" AS "item_code"
    FROM "06_std_ct_inventory_movement.sql"
) x
LEFT JOIN "14_dim_ct_item.sql" i
  ON x."item_code" = i."item_code"
WHERE i."item_code" IS NULL
UNION ALL
SELECT
    'ALL' AS "source_period_code",
    'ALL' AS "outlet_code",
    'All outlets' AS "outlet_name",
    'VENDOR_NAME_MULTIPLE_CODES' AS "exception_type",
    CONCAT('ALL:ALL:', v."vendor_name") AS "exception_record_key",
    '' AS "item_code",
    v."vendor_name" AS "reference_number",
    1 AS "exception_count",
    'Vendor Report contains more than one populated vendor code for the same vendor name'
      AS "definition"
FROM "10_std_ct_vendor_report.sql" v
WHERE v."vendor_code" IS NOT NULL
GROUP BY v."vendor_name"
HAVING COUNT(DISTINCT v."vendor_code") > 1
UNION ALL
SELECT DISTINCT
    t."source_period_code" AS "source_period_code",
    t."outlet_code" AS "outlet_code",
    t."outlet_name" AS "outlet_name",
    'TRANSACTION_VENDOR_MISSING_VENDOR_REPORT',
    CONCAT(t."source_period_code", ':', t."outlet_code", ':', t."vendor_name"),
    '',
    t."vendor_name" AS "vendor_name",
    1,
    'Vendor observed in PO or Entry but absent from the cleaned Vendor Report'
FROM (
    SELECT
        "source_period_code" AS "source_period_code",
        "outlet_code" AS "outlet_code",
        "outlet_name" AS "outlet_name",
        "vendor_name" AS "vendor_name"
    FROM "07_std_ct_purchase_order.sql"
    UNION ALL
    SELECT
        "source_period_code" AS "source_period_code",
        "outlet_code" AS "outlet_code",
        "outlet_name" AS "outlet_name",
        "vendor_name" AS "vendor_name"
    FROM "08_std_ct_purchase_receipt.sql"
) t
LEFT JOIN (
    SELECT DISTINCT "vendor_name" AS "vendor_name"
    FROM "10_std_ct_vendor_report.sql"
) v
  ON t."vendor_name" = v."vendor_name"
WHERE t."vendor_name" IS NOT NULL
  AND v."vendor_name" IS NULL
UNION ALL
SELECT
    'ALL' AS "source_period_code",
    'ALL' AS "outlet_code",
    'All outlets' AS "outlet_name",
    'UOM_MISMATCH_WITHOUT_CONVERSION',
    CONCAT('ALL:ALL:', x."item_code"),
    x."item_code" AS "item_code",
    '',
    1,
    'Item observed in multiple units without a complete canonical conversion'
FROM (
    SELECT
        "item_code" AS "item_code",
        "canonical_uom" AS "observed_uom"
    FROM "05_std_ct_inventory_snapshot.sql"
    UNION ALL
    SELECT
        "item_code" AS "item_code",
        "canonical_uom" AS "observed_uom"
    FROM "22_fact_ct_purchase_order.sql"
    UNION ALL
    SELECT
        "item_code" AS "item_code",
        "canonical_uom" AS "observed_uom"
    FROM "08_std_ct_purchase_receipt.sql"
    UNION ALL
    SELECT
        "item_code" AS "item_code",
        "canonical_uom" AS "observed_uom"
    FROM "06_std_ct_inventory_movement.sql"
) x
LEFT JOIN "14_dim_ct_item.sql" i
  ON x."item_code" = i."item_code"
GROUP BY x."item_code"
HAVING COUNT(DISTINCT x."observed_uom") > 1
   AND MAX(
       CASE
           WHEN i."item_code" IS NOT NULL
            AND i."uom_conversion_factor" IS NOT NULL
           THEN 1 ELSE 0
       END
   ) = 0;
