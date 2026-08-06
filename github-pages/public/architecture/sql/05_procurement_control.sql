/*
Query Table : QT_05_Procurement_Control
Level       : 2
Depends on  : QT_05A_Receipt_Return_As_Of, raw purchase orders,
              raw stock returns, raw entries, references, CTL_Snapshot_Status
              and controls
CTE count   : 2

Stable public procurement output. PO aging and physical return flow are
calculated directly; only the aggregation-heavy receipt cohort is materialized
as a helper. Use record_type explicitly in every report.
*/

WITH
params AS
(
    SELECT
        MAX(CASE WHEN "parameter_id" = 'po_due_amber_days'
                 AND "active_flag" = 1
                 THEN "parameter_value_numeric" END) AS "po_due_amber_days",
        MAX(CASE WHEN "parameter_id" = 'po_overdue_red_days'
                 AND "active_flag" = 1
                 THEN "parameter_value_numeric" END) AS "po_overdue_red_days",
        MAX(CASE WHEN "active_flag" = 1 THEN "formula_version" END)
            AS "formula_version"
    FROM "CTL_Rule_Parameters"
),
as_of_dates AS
(
    SELECT
        CAST(c."calendar_date" AS DATE) AS "as_of_date",
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
    FROM "CTL_Calendar" c
    LEFT JOIN "CTL_Snapshot_Status" ss
      ON CAST(ss."evaluation_date" AS DATE)
         = CAST(c."calendar_date" AS DATE)
    WHERE c."is_demo_operational_date" = 1
)
SELECT
    'PO_AS_OF' AS "record_type",
    d."as_of_date" AS "as_of_date",
    CAST(po."PO Date" AS DATE) AS "business_date",
    'PO_DATE' AS "date_role",
    po."Deployment" AS "outlet_name",
    po."Store Name" AS "store_name",
    vendor."vendorCode" AS "vendor_code",
    po."Vendor Name" AS "vendor_name",
    po."PO Number" AS "po_number",
    CAST(NULL AS CHAR) AS "transaction_number",
    CAST(NULL AS CHAR) AS "invoice_number",
    po."Item Code" AS "item_code",
    po."Item Name" AS "item_name",
    po."Category Name" AS "category_name",
    po."Super Category Name" AS "super_category_name",
    po."Unit" AS "source_unit",
    uom."to_unit" AS "canonical_uom",
    uom."multiplier" AS "uom_multiplier",
    CASE WHEN uom."multiplier" IS NULL THEN 'UNMAPPED' ELSE 'MAPPED' END
        AS "uom_mapping_status",
    CAST(po."Quantity" AS DECIMAL(18,6)) * uom."multiplier"
        AS "ordered_qty_canonical",
    CAST(po."Total Processed Qty" AS DECIMAL(18,6)) * uom."multiplier"
        AS "processed_qty_canonical",
    CAST(po."Remaining Balance Qty" AS DECIMAL(18,6)) * uom."multiplier"
        AS "remaining_qty_canonical",
    CAST(NULL AS DECIMAL(18,6)) AS "eligible_received_qty_canonical",
    CAST(NULL AS DECIMAL(18,6)) AS "observed_return_qty_canonical",
    CAST(NULL AS DECIMAL(18,6)) AS "observed_vendor_return_rate",
    CAST(po."Unit Price" AS DECIMAL(18,6)) / uom."multiplier"
        AS "normalized_unit_price",
    CAST(po."Subtotal" AS DECIMAL(18,2)) AS "ordered_value_pre_tax",
    CAST(po."Remaining Balance Qty" AS DECIMAL(18,6))
        * CAST(po."Unit Price" AS DECIMAL(18,6))
        AS "open_po_liability_pre_tax",
    CAST(NULL AS DECIMAL(18,2)) AS "receipt_value_pre_tax",
    CAST(NULL AS DECIMAL(18,2)) AS "return_value_pre_tax",
    po."PO Status" AS "po_status",
    CASE
        WHEN COALESCE(TRIM(po."Expected Delivery"), '') = '' THEN NULL
        ELSE CAST(NULLIF(TRIM(po."Expected Delivery"), '') AS DATE)
    END AS "expected_delivery_date",
    CASE
        WHEN COALESCE(TRIM(po."Expected Delivery"), '') = '' THEN NULL
        WHEN CAST(NULLIF(TRIM(po."Expected Delivery"), '') AS DATE) < d."as_of_date"
        THEN DATEDIFF(
                 d."as_of_date",
                 CAST(NULLIF(TRIM(po."Expected Delivery"), '') AS DATE)
             )
        ELSE 0
    END AS "overdue_days",
    CASE
        WHEN COALESCE(TRIM(po."Expected Delivery"), '') = ''
        THEN 'PO_DATE_EVIDENCE_GREY'
        WHEN DATEDIFF(
                 d."as_of_date",
                 CAST(NULLIF(TRIM(po."Expected Delivery"), '') AS DATE)
             ) >= p."po_overdue_red_days"
        THEN 'PO_OVERDUE_RED'
        WHEN DATEDIFF(
                 CAST(NULLIF(TRIM(po."Expected Delivery"), '') AS DATE),
                 d."as_of_date"
             ) <= p."po_due_amber_days"
        THEN 'PO_DUE_AMBER'
        ELSE 'PO_TIMING_GREEN'
    END AS "rule_id",
    CASE
        WHEN COALESCE(TRIM(po."Expected Delivery"), '') = '' THEN 'Grey'
        WHEN DATEDIFF(
                 d."as_of_date",
                 CAST(NULLIF(TRIM(po."Expected Delivery"), '') AS DATE)
             ) >= p."po_overdue_red_days"
        THEN 'Red'
        WHEN DATEDIFF(
                 CAST(NULLIF(TRIM(po."Expected Delivery"), '') AS DATE),
                 d."as_of_date"
             ) <= p."po_due_amber_days"
        THEN 'Amber'
        ELSE 'Green'
    END AS "risk_color",
    CASE
        WHEN COALESCE(TRIM(po."Expected Delivery"), '') = '' THEN 5
        WHEN DATEDIFF(
                 d."as_of_date",
                 CAST(NULLIF(TRIM(po."Expected Delivery"), '') AS DATE)
             ) >= p."po_overdue_red_days"
        THEN 2
        WHEN DATEDIFF(
                 CAST(NULLIF(TRIM(po."Expected Delivery"), '') AS DATE),
                 d."as_of_date"
             ) <= p."po_due_amber_days"
        THEN 3
        ELSE 4
    END AS "risk_priority_rank",
    'NOT_APPLICABLE' AS "return_link_status",
    p."formula_version" AS "formula_version",
    'RAW_Enterprise_Purchase_Order' AS "source_table",
    CONCAT(po."PO Number", '|', po."Item Code") AS "source_row_key",
    d."inventory_snapshot_date" AS "inventory_snapshot_date",
    d."inventory_complete_flag" AS "inventory_complete_flag",
    d."sales_complete_flag" AS "sales_complete_flag",
    d."po_complete_flag" AS "po_complete_flag",
    d."source_complete_flag" AS "source_complete_flag",
    d."core_complete_flag" AS "core_complete_flag",
    d."latest_valid_flag" AS "latest_valid_flag",
    d."snapshot_selector" AS "snapshot_selector",
    d."snapshot_loaded_at" AS "snapshot_loaded_at",
    d."snapshot_load_id" AS "snapshot_load_id"
FROM as_of_dates d
CROSS JOIN params p
JOIN "RAW_Enterprise_Purchase_Order" po
  ON CAST(po."PO Date" AS DATE) <= d."as_of_date"
 AND CAST(po."Remaining Balance Qty" AS DECIMAL(18,6)) > 0
 AND LOWER(TRIM(po."PO Status")) IN
     ('open', 'partially received', 'partial', 'pending')
LEFT JOIN "REF_Vendor" vendor
  ON vendor."vendorName" = po."Vendor Name"
LEFT JOIN "CTL_UOM_Conversions" uom
  ON LOWER(TRIM(uom."from_unit")) = LOWER(TRIM(po."Unit"))
 AND uom."conversion_status" IN
     ('approved_identity', 'approved_mathematical', 'approved_alias')

UNION ALL

SELECT
    h."record_type" AS "record_type",
    h."as_of_date" AS "as_of_date",
    h."business_date" AS "business_date",
    h."date_role" AS "date_role",
    h."outlet_name" AS "outlet_name",
    h."store_name" AS "store_name",
    h."vendor_code" AS "vendor_code",
    h."vendor_name" AS "vendor_name",
    h."po_number" AS "po_number",
    h."transaction_number" AS "transaction_number",
    h."invoice_number" AS "invoice_number",
    h."item_code" AS "item_code",
    h."item_name" AS "item_name",
    h."category_name" AS "category_name",
    h."super_category_name" AS "super_category_name",
    h."source_unit" AS "source_unit",
    h."canonical_uom" AS "canonical_uom",
    h."uom_multiplier" AS "uom_multiplier",
    h."uom_mapping_status" AS "uom_mapping_status",
    h."ordered_qty_canonical" AS "ordered_qty_canonical",
    h."processed_qty_canonical" AS "processed_qty_canonical",
    h."remaining_qty_canonical" AS "remaining_qty_canonical",
    h."eligible_received_qty_canonical" AS "eligible_received_qty_canonical",
    h."observed_return_qty_canonical" AS "observed_return_qty_canonical",
    h."observed_vendor_return_rate" AS "observed_vendor_return_rate",
    h."normalized_unit_price" AS "normalized_unit_price",
    h."ordered_value_pre_tax" AS "ordered_value_pre_tax",
    h."open_po_liability_pre_tax" AS "open_po_liability_pre_tax",
    h."receipt_value_pre_tax" AS "receipt_value_pre_tax",
    h."return_value_pre_tax" AS "return_value_pre_tax",
    h."po_status" AS "po_status",
    h."expected_delivery_date" AS "expected_delivery_date",
    h."overdue_days" AS "overdue_days",
    h."rule_id" AS "rule_id",
    h."risk_color" AS "risk_color",
    h."risk_priority_rank" AS "risk_priority_rank",
    h."return_link_status" AS "return_link_status",
    h."formula_version" AS "formula_version",
    h."source_table" AS "source_table",
    h."source_row_key" AS "source_row_key",
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
FROM "QT_05A_Receipt_Return_As_Of" h
LEFT JOIN "CTL_Snapshot_Status" ss
  ON CAST(ss."evaluation_date" AS DATE) = h."as_of_date"

UNION ALL

SELECT
    'RETURN_FLOW' AS "record_type",
    CAST(r."Return Date" AS DATE) AS "as_of_date",
    CAST(r."Return Date" AS DATE) AS "business_date",
    'RETURN_DATE' AS "date_role",
    r."Deployment Name" AS "outlet_name",
    r."Store Name" AS "store_name",
    r."Vendor Code" AS "vendor_code",
    r."Vendor Name" AS "vendor_name",
    CAST(NULL AS CHAR) AS "po_number",
    r."Transaction Number" AS "transaction_number",
    r."Invoice Number" AS "invoice_number",
    r."Item Code" AS "item_code",
    r."Item Name" AS "item_name",
    r."Category Name" AS "category_name",
    r."Super Category Name" AS "super_category_name",
    r."Return Unit" AS "source_unit",
    uom."to_unit" AS "canonical_uom",
    uom."multiplier" AS "uom_multiplier",
    CASE WHEN uom."multiplier" IS NULL THEN 'UNMAPPED' ELSE 'MAPPED' END
        AS "uom_mapping_status",
    CAST(NULL AS DECIMAL(18,6)) AS "ordered_qty_canonical",
    CAST(NULL AS DECIMAL(18,6)) AS "processed_qty_canonical",
    CAST(NULL AS DECIMAL(18,6)) AS "remaining_qty_canonical",
    CAST(NULL AS DECIMAL(18,6)) AS "eligible_received_qty_canonical",
    CAST(r."Return Qty" AS DECIMAL(18,6)) * uom."multiplier"
        AS "observed_return_qty_canonical",
    CAST(NULL AS DECIMAL(18,6)) AS "observed_vendor_return_rate",
    CAST(r."Unit Price" AS DECIMAL(18,6)) / uom."multiplier"
        AS "normalized_unit_price",
    CAST(NULL AS DECIMAL(18,2)) AS "ordered_value_pre_tax",
    CAST(NULL AS DECIMAL(18,2)) AS "open_po_liability_pre_tax",
    CAST(NULL AS DECIMAL(18,2)) AS "receipt_value_pre_tax",
    CAST(r."Return SubTotal" AS DECIMAL(18,2)) AS "return_value_pre_tax",
    CAST(NULL AS CHAR) AS "po_status",
    CAST(NULL AS DATE) AS "expected_delivery_date",
    CAST(NULL AS DECIMAL(18,0)) AS "overdue_days",
    CAST(NULL AS CHAR) AS "rule_id",
    CAST(NULL AS CHAR) AS "risk_color",
    CAST(NULL AS DECIMAL(18,0)) AS "risk_priority_rank",
    CASE
        WHEN e."Transaction Number" IS NULL THEN 'UNMATCHED'
        ELSE 'LINKED'
    END AS "return_link_status",
    p."formula_version" AS "formula_version",
    'RAW_Enterprise_Stock_Return' AS "source_table",
    CONCAT(
        r."Transaction Number",
        '|',
        r."Item Code",
        '|',
        CAST(r."Return Date" AS CHAR)
    ) AS "source_row_key",
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
FROM "RAW_Enterprise_Stock_Return" r
CROSS JOIN params p
LEFT JOIN "CTL_Snapshot_Status" ss
  ON CAST(ss."evaluation_date" AS DATE)
     = CAST(r."Return Date" AS DATE)
LEFT JOIN "RAW_Enterprise_Entry" e
  ON e."Deployment Name" = r."Deployment Name"
 AND e."Store/Kitchen Name" = r."Store Name"
 AND CAST(e."Date" AS DATE) = CAST(r."Stock Entry Date" AS DATE)
 AND e."Transaction Number" = r."Transaction Number"
 AND e."Item Code" = r."Item Code"
LEFT JOIN "CTL_UOM_Conversions" uom
  ON LOWER(TRIM(uom."from_unit")) = LOWER(TRIM(r."Return Unit"))
 AND uom."conversion_status" IN
     ('approved_identity', 'approved_mathematical', 'approved_alias');
