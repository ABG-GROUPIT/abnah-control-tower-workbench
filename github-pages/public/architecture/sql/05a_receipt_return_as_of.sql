/*
Query Table : QT_05A_Receipt_Return_As_Of
Level       : 1
Depends on  : raw entries, raw stock returns, vendor reference, calendar and controls
CTE count   : 3

One entry item line per as-of date with the linked return quantity observed by
that date. This is the only staging Query Table required by
QT_05_Procurement_Control and preserves the final QT_05 column contract.
*/

WITH
params AS
(
    SELECT
        MAX(CASE WHEN "parameter_id" = 'vendor_return_amber_pct'
                 AND "active_flag" = 1
                 THEN "parameter_value_numeric" END) AS "vendor_return_amber_pct",
        MAX(CASE WHEN "parameter_id" = 'vendor_return_red_pct'
                 AND "active_flag" = 1
                 THEN "parameter_value_numeric" END) AS "vendor_return_red_pct",
        MAX(CASE WHEN "active_flag" = 1 THEN "formula_version" END)
            AS "formula_version"
    FROM "CTL_Rule_Parameters"
),
as_of_dates AS
(
    SELECT CAST("calendar_date" AS DATE) AS "as_of_date"
    FROM "CTL_Calendar"
    WHERE "is_demo_operational_date" = 1
),
return_by_entry_line AS
(
    SELECT
        "Deployment Name" AS "outlet_name",
        "Store Name" AS "store_name",
        CAST("Stock Entry Date" AS DATE) AS "stock_entry_date",
        "Transaction Number" AS "transaction_number",
        "Item Code" AS "item_code",
        CAST("Return Date" AS DATE) AS "return_date",
        SUM(CAST("Return Qty" AS DECIMAL(18,6))) AS "return_qty",
        SUM(CAST("Return SubTotal" AS DECIMAL(18,2)))
            AS "return_subtotal"
    FROM "RAW_Enterprise_Stock_Return"
    GROUP BY
        "Deployment Name",
        "Store Name",
        CAST("Stock Entry Date" AS DATE),
        "Transaction Number",
        "Item Code",
        CAST("Return Date" AS DATE)
)
SELECT
    'RECEIPT_COHORT_AS_OF' AS "record_type",
    d."as_of_date" AS "as_of_date",
    CAST(e."Date" AS DATE) AS "business_date",
    'RECEIPT_DATE' AS "date_role",
    e."Deployment Name" AS "outlet_name",
    e."Store/Kitchen Name" AS "store_name",
    vendor."vendorCode" AS "vendor_code",
    e."Vendor Name" AS "vendor_name",
    e."PO Number" AS "po_number",
    e."Transaction Number" AS "transaction_number",
    e."Invoice Number" AS "invoice_number",
    e."Item Code" AS "item_code",
    e."Item Name" AS "item_name",
    e."Category Name" AS "category_name",
    e."Super Category Name" AS "super_category_name",
    e."Unit" AS "source_unit",
    uom."to_unit" AS "canonical_uom",
    uom."multiplier" AS "uom_multiplier",
    CASE WHEN uom."multiplier" IS NULL THEN 'UNMAPPED' ELSE 'MAPPED' END
        AS "uom_mapping_status",
    CAST(NULL AS DECIMAL(18,6)) AS "ordered_qty_canonical",
    CAST(NULL AS DECIMAL(18,6)) AS "processed_qty_canonical",
    CAST(NULL AS DECIMAL(18,6)) AS "remaining_qty_canonical",
    CAST(e."Quantity" AS DECIMAL(18,6)) * uom."multiplier"
        AS "eligible_received_qty_canonical",
    SUM(
        CASE
            WHEN r."return_date" <= d."as_of_date"
            THEN r."return_qty" * uom."multiplier"
            ELSE 0
        END
    ) AS "observed_return_qty_canonical",
    CASE
        WHEN CAST(e."Quantity" AS DECIMAL(18,6)) * uom."multiplier" > 0
        THEN SUM(
                 CASE
                     WHEN r."return_date" <= d."as_of_date"
                     THEN r."return_qty" * uom."multiplier"
                     ELSE 0
                 END
             )
             / (CAST(e."Quantity" AS DECIMAL(18,6)) * uom."multiplier")
        ELSE NULL
    END AS "observed_vendor_return_rate",
    CAST(e."Unit Price" AS DECIMAL(18,6)) / uom."multiplier"
        AS "normalized_unit_price",
    CAST(NULL AS DECIMAL(18,2)) AS "ordered_value_pre_tax",
    CAST(NULL AS DECIMAL(18,2)) AS "open_po_liability_pre_tax",
    CAST(e."Amount" AS DECIMAL(18,2)) AS "receipt_value_pre_tax",
    SUM(
        CASE
            WHEN r."return_date" <= d."as_of_date"
            THEN r."return_subtotal"
            ELSE 0
        END
    ) AS "return_value_pre_tax",
    CAST(NULL AS CHAR) AS "po_status",
    CAST(NULL AS DATE) AS "expected_delivery_date",
    CAST(NULL AS DECIMAL(18,0)) AS "overdue_days",
    CASE
        WHEN uom."multiplier" IS NULL
          OR CAST(e."Quantity" AS DECIMAL(18,6)) <= 0
        THEN 'VRET_EVIDENCE_GREY'
        WHEN p."vendor_return_amber_pct" IS NULL
          OR p."vendor_return_red_pct" IS NULL
        THEN 'VRET_EVIDENCE_GREY'
        WHEN (
            SUM(
                CASE
                    WHEN r."return_date" <= d."as_of_date"
                    THEN r."return_qty" * uom."multiplier"
                    ELSE 0
                END
            )
            / (CAST(e."Quantity" AS DECIMAL(18,6)) * uom."multiplier")
        ) >= p."vendor_return_red_pct"
        THEN 'VRET_RATE_RED'
        WHEN (
            SUM(
                CASE
                    WHEN r."return_date" <= d."as_of_date"
                    THEN r."return_qty" * uom."multiplier"
                    ELSE 0
                END
            )
            / (CAST(e."Quantity" AS DECIMAL(18,6)) * uom."multiplier")
        ) >= p."vendor_return_amber_pct"
        THEN 'VRET_RATE_AMBER'
        ELSE 'VRET_RATE_GREEN'
    END AS "rule_id",
    CASE
        WHEN uom."multiplier" IS NULL
          OR CAST(e."Quantity" AS DECIMAL(18,6)) <= 0
          OR p."vendor_return_amber_pct" IS NULL
          OR p."vendor_return_red_pct" IS NULL
        THEN 'Grey'
        WHEN (
            SUM(
                CASE
                    WHEN r."return_date" <= d."as_of_date"
                    THEN r."return_qty" * uom."multiplier"
                    ELSE 0
                END
            )
            / (CAST(e."Quantity" AS DECIMAL(18,6)) * uom."multiplier")
        ) >= p."vendor_return_red_pct"
        THEN 'Red'
        WHEN (
            SUM(
                CASE
                    WHEN r."return_date" <= d."as_of_date"
                    THEN r."return_qty" * uom."multiplier"
                    ELSE 0
                END
            )
            / (CAST(e."Quantity" AS DECIMAL(18,6)) * uom."multiplier")
        ) >= p."vendor_return_amber_pct"
        THEN 'Amber'
        ELSE 'Green'
    END AS "risk_color",
    CASE
        WHEN uom."multiplier" IS NULL
          OR CAST(e."Quantity" AS DECIMAL(18,6)) <= 0
          OR p."vendor_return_amber_pct" IS NULL
          OR p."vendor_return_red_pct" IS NULL
        THEN 5
        WHEN (
            SUM(
                CASE
                    WHEN r."return_date" <= d."as_of_date"
                    THEN r."return_qty" * uom."multiplier"
                    ELSE 0
                END
            )
            / (CAST(e."Quantity" AS DECIMAL(18,6)) * uom."multiplier")
        ) >= p."vendor_return_red_pct"
        THEN 2
        WHEN (
            SUM(
                CASE
                    WHEN r."return_date" <= d."as_of_date"
                    THEN r."return_qty" * uom."multiplier"
                    ELSE 0
                END
            )
            / (CAST(e."Quantity" AS DECIMAL(18,6)) * uom."multiplier")
        ) >= p."vendor_return_amber_pct"
        THEN 3
        ELSE 4
    END AS "risk_priority_rank",
    CASE
        WHEN COUNT(r."transaction_number") = 0 THEN 'NO_RETURN_OBSERVED'
        ELSE 'LINKED'
    END AS "return_link_status",
    p."formula_version" AS "formula_version",
    'RAW_Enterprise_Entry;RAW_Enterprise_Stock_Return'
        AS "source_table",
    CONCAT(e."Transaction Number", '|', e."Item Code")
        AS "source_row_key"
FROM as_of_dates d
CROSS JOIN params p
JOIN "RAW_Enterprise_Entry" e
  ON CAST(e."Date" AS DATE) <= d."as_of_date"
LEFT JOIN return_by_entry_line r
  ON r."outlet_name" = e."Deployment Name"
 AND r."store_name" = e."Store/Kitchen Name"
 AND r."stock_entry_date" = CAST(e."Date" AS DATE)
 AND r."transaction_number" = e."Transaction Number"
 AND r."item_code" = e."Item Code"
LEFT JOIN "REF_Vendor" vendor
  ON vendor."vendorName" = e."Vendor Name"
LEFT JOIN "CTL_UOM_Conversions" uom
  ON LOWER(TRIM(uom."from_unit")) = LOWER(TRIM(e."Unit"))
 AND uom."conversion_status" IN
     ('approved_identity', 'approved_mathematical', 'approved_alias')
GROUP BY
    d."as_of_date",
    CAST(e."Date" AS DATE),
    e."Deployment Name",
    e."Store/Kitchen Name",
    vendor."vendorCode",
    e."Vendor Name",
    e."PO Number",
    e."Transaction Number",
    e."Invoice Number",
    e."Item Code",
    e."Item Name",
    e."Category Name",
    e."Super Category Name",
    e."Unit",
    uom."to_unit",
    uom."multiplier",
    e."Quantity",
    e."Unit Price",
    e."Amount",
    p."vendor_return_amber_pct",
    p."vendor_return_red_pct",
    p."formula_version";
