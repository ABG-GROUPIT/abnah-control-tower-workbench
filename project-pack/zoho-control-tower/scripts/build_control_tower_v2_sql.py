from __future__ import annotations

import csv
import re
import shutil
from dataclasses import dataclass, replace
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "zoho_control_tower_v2_sql"

ZOHO_IMPORT_TABLE_NAMES = {
    "RAWN_CT_gross_net_margin": "RAWN_CT_gross_net_margin-Copy",
    "RAWN_CT_item_recipe_report": "RAWN_CT_item_recipe_report-Copy",
    "RAWN_CT_enterprise_variance_normal": "RAWN_CT_enterprise_variance_normal-Copy",
    "RAWN_CT_closing_stock": "RAWN_CT_closing_stock-Copy",
    "RAWN_CT_enterprise_transfer_from": "RAWN_CT_enterprise_transfer_from-Copy",
    "RAWN_CT_enterprise_transfer_to": "RAWN_CT_enterprise_transfer_to-Copy",
    "RAWN_CT_enterprise_wastage_normal": "RAWN_CT_enterprise_wastage_normal-Copy",
    "RAWN_CT_enterprise_purchase_order": "RAWN_CT_enterprise_purchase_order-Copy",
    "RAWN_CT_enterprise_entry": "RAWN_CT_enterprise_entry-Copy",
    "RAWN_CT_vendor_report": "RAWN_CT_vendor_report-Copy",
    "AUX_Expiry_Estimate": "AUX_Expiry_Estimate-Copy",
    "AUX_Theoretical_Consumption": "AUX_Theoretical_Consumption-Copy",
    "AUX_Menu_Demand_Forecast": "AUX_Menu_Demand_Forecast-Copy",
    "AUX_Outlet_Master": "AUX_Outlet_Master-Copy",
}


@dataclass(frozen=True)
class Query:
    order: int
    layer: str
    name: str
    purpose: str
    sources: tuple[str, ...]
    sql: str

    @property
    def filename(self) -> str:
        return f"{self.order:02d}_{self.name.lower()}.sql"


SIMPLE_PROJECTION_RE = re.compile(
    r'^(?P<indent>\s*)(?P<expression>(?:[A-Za-z_][A-Za-z0-9_]*\.)?"(?P<name>[^"]+)")'
    r'(?P<comma>,?)\s*$'
)
CTE_DEFINITION_RE = re.compile(
    r"(?im)^(?:WITH\s+)?[A-Za-z_][A-Za-z0-9_]*\s+AS\s*\(\s*$"
)
DERIVED_SUBQUERY_RE = re.compile(
    r"(?is)\b(?:FROM|JOIN)\s*\(\s*SELECT\b"
)
DERIVED_SUBQUERY_START_RE = re.compile(
    r"(?is)\b(?:FROM|JOIN)\s*(?P<open>\()(?=\s*SELECT\b)"
)


def alias_simple_projection_columns(sql: str) -> str:
    """Give passthrough SELECT columns stable names in Zoho and derived tables."""
    lines = sql.splitlines()
    in_projection = False

    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped in {"SELECT", "SELECT DISTINCT"}:
            in_projection = True
            continue
        if in_projection and stripped.startswith("FROM "):
            in_projection = False
            continue
        if not in_projection:
            continue

        match = SIMPLE_PROJECTION_RE.match(line)
        if match is None:
            continue

        next_significant = next(
            (
                candidate.strip()
                for candidate in lines[index + 1 :]
                if candidate.strip()
            ),
            "",
        )
        if not match.group("comma") and not next_significant.startswith("FROM "):
            continue

        lines[index] = (
            f'{match.group("indent")}{match.group("expression")} '
            f'AS "{match.group("name")}"{match.group("comma")}'
        )

    return "\n".join(lines)


def mask_sql_quoted_content(sql: str) -> str:
    masked = list(sql)
    quote: str | None = None
    index = 0
    while index < len(masked):
        character = masked[index]
        if quote is None:
            if character in {"'", '"'}:
                quote = character
                masked[index] = " "
        else:
            masked[index] = " "
            if character == quote:
                if index + 1 < len(masked) and masked[index + 1] == quote:
                    masked[index + 1] = " "
                    index += 1
                else:
                    quote = None
        index += 1
    return "".join(masked)


def matching_parenthesis(sql: str, opening_index: int, end: int) -> int:
    depth = 0
    for index in range(opening_index, end):
        if sql[index] == "(":
            depth += 1
        elif sql[index] == ")":
            depth -= 1
            if depth == 0:
                return index
    raise ValueError("Unbalanced SQL parentheses.")


def max_derived_subquery_depth(sql: str) -> int:
    masked = mask_sql_quoted_content(sql)

    def depth_between(start: int, end: int) -> int:
        maximum = 0
        position = start
        while match := DERIVED_SUBQUERY_START_RE.search(masked, position, end):
            opening = match.start("open")
            closing = matching_parenthesis(masked, opening, end)
            maximum = max(maximum, 1 + depth_between(opening + 1, closing))
            position = closing + 1
        return maximum

    return depth_between(0, len(masked))


def q(
    order: int,
    layer: str,
    name: str,
    purpose: str,
    sources: tuple[str, ...],
    sql: str,
) -> Query:
    normalized_sql = alias_simple_projection_columns(sql.strip())
    return Query(order, layer, name, purpose, sources, normalized_sql + "\n")


def inventory_risk_sql() -> str:
    """Render the stockout risk fact without CTEs for Zoho compatibility."""
    return """
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
FROM "STD_CT_Inventory_Snapshot" s
LEFT JOIN (
    SELECT
        "source_period_code" AS "source_period_code",
        "outlet_code" AS "outlet_code",
        "item_code" AS "item_code",
        SUM("forecast_ingredient_qty") AS "forecast_required_qty"
    FROM "FACT_CT_Forecast_Ingredient_Demand"
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
    FROM "FACT_CT_Purchase_Order"
    WHERE "is_open_po" = 1
    GROUP BY "source_period_code", "outlet_code", "item_code"
) p
  ON s."source_period_code" = p."source_period_code"
 AND s."outlet_code" = p."outlet_code"
 AND s."item_code" = p."item_code"
"""

QUERIES = [
    q(
        1,
        "standardized",
        "STD_CT_Sales_Item",
        "Standardize bill-item sales, realized revenue and source-reported margin fields.",
        ("RAWN_CT_gross_net_margin",),
        """
SELECT
    s."source_period_code" AS "source_period_code",
    s."source_outlet_code" AS "outlet_code",
    s."source_outlet_name" AS "outlet_name",
    CAST(s."sale_date" AS DATE) AS "sales_date",
    s."bill_number" AS "bill_number",
    s."tab_type" AS "tab_type",
    s."source" AS "order_source",
    s."super_category_name" AS "super_category_name",
    s."category_name" AS "category_name",
    s."item_code" AS "item_code",
    s."item_name" AS "item_name",
    CAST(s."item_rate" AS DECIMAL(18,2)) AS "item_rate",
    CAST(s."item_qty" AS DECIMAL(18,4)) AS "sold_qty",
    CAST(s."item_subtotal" AS DECIMAL(18,2)) AS "item_subtotal",
    CAST(s."total_discount_amt" AS DECIMAL(18,2)) AS "discount_amount",
    CAST(s."net_sale_value" AS DECIMAL(18,2)) AS "net_sales",
    CAST(s."tax_amt" AS DECIMAL(18,2)) AS "tax_amount",
    CAST(s."gross_sale_value" AS DECIMAL(18,2)) AS "gross_sales",
    CAST(s."purchase_rate" AS DECIMAL(18,4)) AS "source_purchase_rate",
    CAST(s."purchase_value" AS DECIMAL(18,2)) AS "source_purchase_value"
FROM "RAWN_CT_gross_net_margin" s
WHERE CAST(s."item_qty" AS DECIMAL(18,4)) <> 0
""",
    ),
    q(
        2,
        "standardized",
        "STD_CT_Recipe",
        "Standardize menu-item-to-ingredient recipe quantities.",
        ("RAWN_CT_item_recipe_report",),
        """
SELECT
    r."menu_item_type" AS "menu_item_type",
    r."menu_item_number" AS "menu_item_code",
    r."menu_item_name" AS "menu_item_name",
    r."recipe_item_type" AS "recipe_item_type",
    r."ingredient_code" AS "ingredient_code",
    r."ingredient_name" AS "ingredient_name",
    CAST(r."recipe_qty_per_menu_unit" AS DECIMAL(18,6)) AS "recipe_qty_per_menu_unit",
    r."recipe_unit" AS "recipe_uom"
FROM "RAWN_CT_item_recipe_report" r
WHERE r."menu_item_number" IS NOT NULL
  AND r."ingredient_code" IS NOT NULL
""",
    ),
    q(
        3,
        "standardized",
        "STD_CT_Theoretical_Consumption",
        "Standardize the synthetic theoretical ingredient baseline at outlet-item-month grain.",
        ("AUX_Theoretical_Consumption",),
        """
SELECT
    t."source_period_code" AS "source_period_code",
    t."outlet_code" AS "outlet_code",
    t."outlet_name" AS "outlet_name",
    t."item_code" AS "item_code",
    t."item_name" AS "item_name",
    t."category_name" AS "category_name",
    t."super_category_name" AS "super_category_name",
    t."unit" AS "canonical_uom",
    CAST(t."average_price" AS DECIMAL(18,4)) AS "average_unit_cost",
    CAST(t."theoretical_qty" AS DECIMAL(18,6)) AS "theoretical_consumption_qty"
FROM "AUX_Theoretical_Consumption" t
""",
    ),
    q(
        4,
        "standardized",
        "STD_CT_Inventory_Period",
        "Standardize month-end inventory, actual consumption and source variance measures.",
        ("RAWN_CT_enterprise_variance_normal",),
        """
SELECT
    v."source_period_code" AS "source_period_code",
    v."source_outlet_code" AS "outlet_code",
    v."deployment_name" AS "outlet_name",
    v."store_kitchen_name" AS "store_kitchen_name",
    v."item_code" AS "item_code",
    v."item_name" AS "item_name",
    v."category_name" AS "category_name",
    v."super_category_name" AS "super_category_name",
    v."unit" AS "canonical_uom",
    CAST(v."average_price" AS DECIMAL(18,4)) AS "average_unit_cost",
    CAST(v."opening_date" AS DATE) AS "opening_date",
    CAST(v."closing_date" AS DATE) AS "closing_date",
    CAST(v."opening_qty" AS DECIMAL(18,6)) AS "opening_qty",
    CAST(v."purchase_qty" AS DECIMAL(18,6)) AS "purchase_qty",
    CAST(v."stock_in_qty" AS DECIMAL(18,6)) AS "transfer_in_qty",
    CAST(v."stock_out_qty" AS DECIMAL(18,6)) AS "transfer_out_qty",
    CAST(v."return_qty" AS DECIMAL(18,6)) AS "return_qty",
    CAST(v."wastage_qty" AS DECIMAL(18,6)) AS "wastage_qty",
    CAST(v."closing_qty" AS DECIMAL(18,6)) AS "closing_qty",
    CAST(v."physical_qty" AS DECIMAL(18,6)) AS "physical_qty",
    CAST(v."actual_consumption_qty" AS DECIMAL(18,6)) AS "actual_consumption_qty",
    CAST(v."variance_qty" AS DECIMAL(18,6)) AS "source_variance_qty",
    CAST(v."variance_percent" AS DECIMAL(18,4)) AS "source_variance_percent"
FROM "RAWN_CT_enterprise_variance_normal" v
""",
    ),
    q(
        5,
        "standardized",
        "STD_CT_Inventory_Snapshot",
        "Standardize closing stock quantity and value checkpoints.",
        ("RAWN_CT_closing_stock",),
        """
SELECT
    c."source_period_code" AS "source_period_code",
    c."source_outlet_code" AS "outlet_code",
    c."deployment_name" AS "outlet_name",
    CAST(c."stock_date" AS DATE) AS "snapshot_date",
    c."item_code" AS "item_code",
    c."item_name" AS "item_name",
    c."category_code" AS "category_code",
    c."category_name" AS "category_name",
    c."super_category_code" AS "super_category_code",
    c."super_category_name" AS "super_category_name",
    c."unit_name" AS "canonical_uom",
    CAST(c."average_price" AS DECIMAL(18,4)) AS "average_unit_cost",
    CAST(c."total_qty" AS DECIMAL(18,6)) AS "closing_qty",
    CAST(c."total_amt" AS DECIMAL(18,2)) AS "closing_value"
FROM "RAWN_CT_closing_stock" c
""",
    ),
    q(
        6,
        "standardized",
        "STD_CT_Inventory_Movement",
        "Unify internal transfers and wastage into signed inventory movements.",
        (
            "RAWN_CT_enterprise_transfer_from",
            "RAWN_CT_enterprise_transfer_to",
            "RAWN_CT_enterprise_wastage_normal",
        ),
        """
SELECT
    f."source_period_code" AS "source_period_code",
    f."source_outlet_code" AS "outlet_code",
    f."deployment_name" AS "outlet_name",
    CAST(f."transfer_date" AS DATE) AS "movement_date",
    f."transaction_number" AS "transaction_number",
    f."item_code" AS "item_code",
    f."item_name" AS "item_name",
    f."category_name" AS "category_name",
    f."super_category_name" AS "super_category_name",
    f."unit" AS "canonical_uom",
    'TRANSFER_OUT' AS "movement_type",
    -1 * CAST(f."transfer_qty" AS DECIMAL(18,6)) AS "signed_qty",
    -1 * CAST(f."transfer_amt" AS DECIMAL(18,2)) AS "signed_value"
FROM "RAWN_CT_enterprise_transfer_from" f
UNION ALL
SELECT
    t."source_period_code" AS "source_period_code",
    t."source_outlet_code" AS "outlet_code",
    t."deployment_name" AS "outlet_name",
    CAST(t."transfer_date" AS DATE) AS "movement_date",
    t."transaction_number" AS "transaction_number",
    t."item_code" AS "item_code",
    t."item_name" AS "item_name",
    t."category_name" AS "category_name",
    t."super_category_name" AS "super_category_name",
    t."unit" AS "canonical_uom",
    'TRANSFER_IN' AS "movement_type",
    CAST(t."transfer_qty" AS DECIMAL(18,6)) AS "signed_qty",
    CAST(t."transfer_amt" AS DECIMAL(18,2)) AS "signed_value"
FROM "RAWN_CT_enterprise_transfer_to" t
UNION ALL
SELECT
    w."source_period_code" AS "source_period_code",
    w."source_outlet_code" AS "outlet_code",
    w."deployment_name" AS "outlet_name",
    CAST(w."wastage_date" AS DATE) AS "movement_date",
    w."transaction_number" AS "transaction_number",
    w."item_code" AS "item_code",
    w."item_name" AS "item_name",
    w."category_name" AS "category_name",
    w."super_category_name" AS "super_category_name",
    w."unit" AS "canonical_uom",
    'WASTAGE' AS "movement_type",
    -1 * CAST(w."wastage_qty" AS DECIMAL(18,6)) AS "signed_qty",
    -1 * CAST(w."wastage_amt" AS DECIMAL(18,2)) AS "signed_value"
FROM "RAWN_CT_enterprise_wastage_normal" w
""",
    ),
    q(
        7,
        "standardized",
        "STD_CT_Purchase_Order",
        "Standardize purchase-order lines and normalized open/closed status.",
        ("RAWN_CT_enterprise_purchase_order",),
        """
SELECT
    p."source_period_code" AS "source_period_code",
    CAST(p."source_period_end" AS DATE) AS "as_of_date",
    p."source_outlet_code" AS "outlet_code",
    p."deployment_name" AS "outlet_name",
    p."store_name" AS "store_name",
    p."vendor_name" AS "vendor_name",
    p."po_number" AS "po_number",
    CAST(p."po_date" AS DATE) AS "po_date",
    CAST(p."expected_delivery_date" AS DATE) AS "expected_delivery_date",
    CAST(p."po_close_or_partial_receive_date" AS DATE) AS "close_or_partial_receive_date",
    p."po_status" AS "po_status",
    p."item_code" AS "item_code",
    p."item_name" AS "item_name",
    p."category_name" AS "category_name",
    p."super_category_name" AS "super_category_name",
    CAST(p."processed_qty" AS DECIMAL(18,6)) AS "processed_qty",
    CAST(p."remaining_balance_qty" AS DECIMAL(18,6)) AS "remaining_qty",
    CAST(p."ordered_qty" AS DECIMAL(18,6)) AS "ordered_qty",
    p."unit" AS "canonical_uom",
    CAST(p."unit_price" AS DECIMAL(18,4)) AS "unit_price",
    CAST(p."new_subtotal" AS DECIMAL(18,2)) AS "net_order_value",
    CAST(p."tax_amt" AS DECIMAL(18,2)) AS "tax_value",
    CAST(p."total_item_cost" AS DECIMAL(18,2)) AS "gross_order_value",
    CASE
        WHEN p."po_status" IN ('Pending', 'Partially Received') THEN 1
        WHEN CAST(p."remaining_balance_qty" AS DECIMAL(18,6)) > 0 THEN 1
        ELSE 0
    END AS "is_open_po"
FROM "RAWN_CT_enterprise_purchase_order" p
""",
    ),
    q(
        8,
        "standardized",
        "STD_CT_Purchase_Receipt",
        "Standardize PO-linked GRN/entry lines.",
        ("RAWN_CT_enterprise_entry",),
        """
SELECT
    e."source_period_code" AS "source_period_code",
    e."source_outlet_code" AS "outlet_code",
    e."deployment_name" AS "outlet_name",
    e."store_kitchen_name" AS "store_kitchen_name",
    e."vendor_name" AS "vendor_name",
    e."po_number" AS "po_number",
    e."transaction_number" AS "grn_number",
    e."invoice_number" AS "invoice_number",
    CAST(e."entry_date" AS DATE) AS "receipt_date",
    CAST(e."invoice_date" AS DATE) AS "invoice_date",
    e."item_code" AS "item_code",
    e."item_name" AS "item_name",
    e."category_name" AS "category_name",
    e."super_category_name" AS "super_category_name",
    CAST(e."entry_qty" AS DECIMAL(18,6)) AS "received_qty",
    e."unit" AS "canonical_uom",
    CAST(e."unit_price" AS DECIMAL(18,4)) AS "unit_price",
    CAST(e."base_amt" AS DECIMAL(18,2)) AS "receipt_subtotal",
    CAST(e."discount_amt" AS DECIMAL(18,2)) AS "discount_value",
    CAST(e."total_tax_amt" AS DECIMAL(18,2)) AS "tax_value",
    CAST(e."total_amt" AS DECIMAL(18,2)) AS "receipt_total"
FROM "RAWN_CT_enterprise_entry" e
""",
    ),
    q(
        9,
        "standardized",
        "STD_CT_Vendor_Return",
        "Standardize vendor return quantities and values.",
        ("RAWN_CT_enterprise_stock_return",),
        """
SELECT
    r."source_period_code",
    r."source_outlet_code" AS "outlet_code",
    r."deployment_name" AS "outlet_name",
    r."vendor_code",
    r."vendor_name",
    r."transaction_number" AS "grn_number",
    CAST(r."stock_entry_date" AS DATE) AS "stock_entry_date",
    CAST(r."return_date" AS DATE) AS "return_date",
    r."item_code",
    r."item_name",
    r."category_name",
    r."super_category_name",
    CAST(r."entry_qty" AS DECIMAL(18,6)) AS "entry_qty",
    CAST(r."return_qty" AS DECIMAL(18,6)) AS "return_qty",
    r."return_unit" AS "canonical_uom",
    CAST(r."unit_price" AS DECIMAL(18,4)) AS "unit_price",
    CAST(r."return_amt" AS DECIMAL(18,2)) AS "return_value",
    r."transaction_status"
FROM "RAWN_CT_enterprise_stock_return" r
""",
    ),
    q(
        10,
        "standardized",
        "STD_CT_Wastage",
        "Standardize inventory wastage transactions.",
        ("RAWN_CT_enterprise_wastage_normal",),
        """
SELECT
    w."source_period_code" AS "source_period_code",
    w."source_outlet_code" AS "outlet_code",
    w."deployment_name" AS "outlet_name",
    w."store_kitchen_name" AS "store_kitchen_name",
    CAST(w."wastage_date" AS DATE) AS "wastage_date",
    w."transaction_number" AS "transaction_number",
    w."item_code" AS "item_code",
    w."item_name" AS "item_name",
    w."category_name" AS "category_name",
    w."super_category_name" AS "super_category_name",
    w."comment" AS "wastage_reason",
    CAST(w."wastage_qty" AS DECIMAL(18,6)) AS "wastage_qty",
    w."unit" AS "canonical_uom",
    CAST(w."unit_price" AS DECIMAL(18,4)) AS "unit_price",
    CAST(w."wastage_amt" AS DECIMAL(18,2)) AS "wastage_value"
FROM "RAWN_CT_enterprise_wastage_normal" w
""",
    ),
    q(
        11,
        "standardized",
        "STD_CT_Vendor_Report",
        "Standardize the exact historical Vendor Report after local structural cleaning.",
        ("RAWN_CT_vendor_report",),
        """
SELECT
    v."vendor_name" AS "vendor_name",
    v."vendor_code" AS "vendor_code",
    v."description" AS "description",
    v."contact_person" AS "contact_person",
    v."contact_number" AS "contact_number",
    v."email" AS "email",
    v."tin_number" AS "tin_number",
    v."service_tax_number" AS "service_tax_number",
    v."gstin_number" AS "gstin_number",
    v."msme" AS "msme",
    v."fssai_number" AS "fssai_number",
    v."pan_number" AS "pan_number",
    CAST(v."from_date" AS DATE) AS "valid_from_date",
    CAST(v."to_date" AS DATE) AS "valid_to_date",
    v."state" AS "state",
    v."address" AS "address"
FROM "RAWN_CT_vendor_report" v
WHERE v."vendor_name" IS NOT NULL
""",
    ),
    q(
        12,
        "standardized",
        "STD_CT_Menu_Forecast",
        "Standardize seven-day menu demand forecasts.",
        ("AUX_Menu_Demand_Forecast",),
        """
SELECT
    f."forecast_as_of_month" AS "source_period_code",
    CAST(f."forecast_date" AS DATE) AS "forecast_date",
    f."outlet_code" AS "outlet_code",
    f."outlet_name" AS "outlet_name",
    f."menu_item_code" AS "menu_item_code",
    f."menu_item_name" AS "menu_item_name",
    f."super_category_name" AS "super_category_name",
    f."category_name" AS "category_name",
    CAST(f."forecast_qty" AS DECIMAL(18,6)) AS "forecast_menu_qty",
    CAST(f."forecast_net_sales" AS DECIMAL(18,2)) AS "forecast_net_sales",
    f."model_name" AS "model_name",
    f."confidence_band" AS "confidence_band"
FROM "AUX_Menu_Demand_Forecast" f
""",
    ),
    q(
        12,
        "standardized",
        "STD_CT_Expiry_Estimate",
        "Standardize the explicitly synthetic near-expiry batch-tranche scenario.",
        ("AUX_Expiry_Estimate",),
        """
SELECT
    e."source_period_code",
    CAST(e."as_of_date" AS DATE) AS "as_of_date",
    e."outlet_code",
    e."outlet_name",
    e."store_name",
    e."batch_allocation_id",
    e."batch_number",
    CAST(e."receipt_date" AS DATE) AS "receipt_date",
    e."grn_number",
    e."po_number",
    e."vendor_name",
    e."receipt_source_status",
    e."item_code",
    e."item_name",
    e."category_name",
    CAST(e."received_qty" AS DECIMAL(18,6)) AS "received_qty",
    CAST(e."batch_remaining_qty" AS DECIMAL(18,6)) AS "batch_remaining_qty",
    CAST(e."item_closing_qty" AS DECIMAL(18,6)) AS "item_closing_qty",
    CAST(e."qty_at_risk" AS DECIMAL(18,6)) AS "expiry_qty_at_risk",
    e."unit" AS "canonical_uom",
    CAST(e."average_unit_cost" AS DECIMAL(18,4)) AS "average_unit_cost",
    CAST(e."estimated_expiry_date" AS DATE) AS "estimated_expiry_date",
    CAST(e."days_to_expiry" AS INTEGER) AS "days_to_expiry",
    CAST(e."expiry_risk_value" AS DECIMAL(18,2)) AS "expiry_risk_value",
    e."risk_status",
    CAST(e."is_estimated" AS INTEGER) AS "is_estimated",
    e."estimation_method",
    e."source_evidence",
    e."production_use_status"
FROM "AUX_Expiry_Estimate" e
""",
    ),
    q(
        13,
        "dimension",
        "DIM_CT_Date",
        "Create the sales-date calendar used by the three-month baseline.",
        ("STD_CT_Sales_Item",),
        """
SELECT DISTINCT
    s."sales_date" AS "calendar_date",
    YEAR(s."sales_date") AS "calendar_year",
    MONTH(s."sales_date") AS "calendar_month_number",
    DAY(s."sales_date") AS "calendar_day",
    DAYOFWEEK(s."sales_date") AS "day_of_week_number",
    CASE
        WHEN DAYOFWEEK(s."sales_date") IN (1, 7) THEN 1
        ELSE 0
    END AS "is_weekend"
FROM "STD_CT_Sales_Item" s
""",
    ),
    q(
        14,
        "dimension",
        "DIM_CT_Outlet",
        "Create the outlet identity dimension from the captured stock source.",
        ("RAWN_CT_closing_stock",),
        """
SELECT
    c."source_outlet_code" AS "outlet_code",
    MAX(c."source_outlet_name") AS "outlet_name",
    NULL AS "region",
    NULL AS "city",
    NULL AS "market_area",
    NULL AS "latitude",
    NULL AS "longitude",
    NULL AS "new_matured_flag",
    NULL AS "active_status",
    'derived_from_closing_stock' AS "source_evidence"
FROM "RAWN_CT_closing_stock" c
WHERE c."source_outlet_code" IS NOT NULL
GROUP BY c."source_outlet_code"
""",
    ),
    q(
        15,
        "dimension",
        "DIM_CT_Item",
        "Create the item identity, category, UOM and cost reference from Closing Stock.",
        ("RAWN_CT_closing_stock",),
        """
SELECT
    c."item_code" AS "item_code",
    MAX(c."item_name") AS "item_name",
    MAX(c."category_name") AS "category_name",
    MAX(c."super_category_name") AS "super_category_name",
    MAX(c."unit_name") AS "canonical_uom",
    CASE
        WHEN COUNT(DISTINCT c."unit_name") = 1 THEN 1
        ELSE NULL
    END AS "uom_conversion_factor",
    AVG(
        CASE
            WHEN CAST(c."average_price" AS DECIMAL(18,4)) > 0
            THEN CAST(c."average_price" AS DECIMAL(18,4))
            ELSE NULL
        END
    ) AS "baseline_average_price",
    NULL AS "reorder_level_qty",
    NULL AS "standard_order_qty",
    NULL AS "primary_vendor",
    NULL AS "alternate_vendor",
    NULL AS "shelf_life_days",
    NULL AS "storage_type",
    NULL AS "food_beverage_non_food_flag",
    NULL AS "criticality",
    'derived_from_closing_stock' AS "source_evidence"
FROM "RAWN_CT_closing_stock" c
WHERE c."item_code" IS NOT NULL
GROUP BY c."item_code"
""",
    ),
    q(
        16,
        "dimension",
        "DIM_CT_Menu_Item",
        "Create the canonical menu-item dimension from validated sales.",
        ("STD_CT_Sales_Item",),
        """
SELECT
    s."item_code" AS "menu_item_code",
    s."item_name" AS "menu_item_name",
    MAX(s."super_category_name") AS "super_category_name",
    MAX(s."category_name") AS "category_name",
    AVG(s."item_rate") AS "average_menu_rate"
FROM "STD_CT_Sales_Item" s
GROUP BY s."item_code", s."item_name"
""",
    ),
    q(
        17,
        "dimension",
        "DIM_CT_Vendor",
        "Create the vendor identity dimension from Vendor Report with transaction-only fallbacks.",
        (
            "STD_CT_Vendor_Report",
            "RAWN_CT_enterprise_purchase_order",
            "RAWN_CT_enterprise_entry",
        ),
        """
SELECT
    MAX(v."vendor_code") AS "vendor_code",
    v."vendor_name" AS "vendor_name",
    MAX(v."description") AS "description",
    MAX(v."state") AS "state",
    MIN(v."valid_from_date") AS "valid_from_date",
    MAX(v."valid_to_date") AS "valid_to_date",
    MAX(v."msme") AS "msme",
    MAX(v."gstin_number") AS "gstin_number",
    MAX(v."fssai_number") AS "fssai_number",
    MAX(v."pan_number") AS "pan_number",
    NULL AS "active_status",
    NULL AS "default_lead_time_days",
    NULL AS "approved_category_mapping",
    'vendor_report' AS "source_evidence"
FROM "STD_CT_Vendor_Report" v
GROUP BY v."vendor_name"
UNION ALL
SELECT
    NULL AS "vendor_code",
    t."vendor_name" AS "vendor_name",
    NULL AS "description",
    NULL AS "state",
    NULL AS "valid_from_date",
    NULL AS "valid_to_date",
    NULL AS "msme",
    NULL AS "gstin_number",
    NULL AS "fssai_number",
    NULL AS "pan_number",
    NULL AS "active_status",
    NULL AS "default_lead_time_days",
    NULL AS "approved_category_mapping",
    'observed_in_po_or_entry_only' AS "source_evidence"
FROM (
    SELECT "vendor_name" AS "vendor_name"
    FROM "RAWN_CT_enterprise_purchase_order"
    WHERE "vendor_name" IS NOT NULL
    UNION
    SELECT "vendor_name" AS "vendor_name"
    FROM "RAWN_CT_enterprise_entry"
    WHERE "vendor_name" IS NOT NULL
) t
LEFT JOIN (
    SELECT DISTINCT "vendor_name" AS "vendor_name"
    FROM "STD_CT_Vendor_Report"
) v
  ON t."vendor_name" = v."vendor_name"
WHERE v."vendor_name" IS NULL
""",
    ),
    q(
        18,
        "dimension",
        "DIM_CT_Recipe_Effective",
        "Resolve recipe ingredients to canonical item UOM and unit cost.",
        ("RAWN_CT_item_recipe_report", "RAWN_CT_closing_stock"),
        """
SELECT
    r."menu_item_number" AS "menu_item_code",
    r."menu_item_name" AS "menu_item_name",
    r."ingredient_code" AS "ingredient_code",
    r."ingredient_name" AS "ingredient_name",
    CAST(r."recipe_qty_per_menu_unit" AS DECIMAL(18,6)) AS "recipe_qty_per_menu_unit",
    r."recipe_unit" AS "recipe_uom",
    i."canonical_uom" AS "canonical_uom",
    CASE
        WHEN LOWER(r."recipe_unit") = LOWER(i."canonical_uom") THEN 1
        ELSE NULL
    END AS "uom_conversion_factor",
    CASE
        WHEN LOWER(r."recipe_unit") = LOWER(i."canonical_uom")
        THEN CAST(r."recipe_qty_per_menu_unit" AS DECIMAL(18,6))
        ELSE NULL
    END AS "canonical_recipe_qty",
    CAST(i."average_price" AS DECIMAL(18,4)) AS "ingredient_unit_cost",
    CASE
        WHEN LOWER(r."recipe_unit") = LOWER(i."canonical_uom")
        THEN CAST(r."recipe_qty_per_menu_unit" AS DECIMAL(18,6))
          * CAST(i."average_price" AS DECIMAL(18,4))
        ELSE NULL
    END AS "ingredient_cost_per_menu_unit"
FROM "RAWN_CT_item_recipe_report" r
LEFT JOIN (
    SELECT
        "item_code",
        MAX("unit_name") AS "canonical_uom",
        AVG(
            CASE
                WHEN CAST("average_price" AS DECIMAL(18,4)) > 0
                THEN CAST("average_price" AS DECIMAL(18,4))
                ELSE NULL
            END
        ) AS "average_price"
    FROM "RAWN_CT_closing_stock"
    GROUP BY "item_code"
) i
  ON r."ingredient_code" = i."item_code"
WHERE r."menu_item_number" IS NOT NULL
  AND r."ingredient_code" IS NOT NULL
""",
    ),
    q(
        19,
        "fact",
        "FACT_CT_Sales",
        "Expose validated bill-item sales at its native grain.",
        ("STD_CT_Sales_Item",),
        """
SELECT
    s.*,
    CASE
        WHEN s."sold_qty" <> 0 THEN s."net_sales" / s."sold_qty"
        ELSE NULL
    END AS "realized_unit_price"
FROM "STD_CT_Sales_Item" s
""",
    ),
    q(
        20,
        "fact",
        "FACT_CT_Theoretical_Consumption",
        "Expose theoretical ingredient consumption at outlet-item-month grain.",
        ("STD_CT_Theoretical_Consumption",),
        """
SELECT
    t.*,
    t."theoretical_consumption_qty" * t."average_unit_cost" AS "theoretical_consumption_value"
FROM "STD_CT_Theoretical_Consumption" t
""",
    ),
    q(
        21,
        "fact",
        "FACT_CT_Actual_Consumption",
        "Calculate the approved inventory movement bridge for actual consumption.",
        ("STD_CT_Inventory_Period",),
        """
SELECT
    p.*,
    -1 * p."transfer_out_qty" AS "bridge_transfer_out_qty",
    -1 * p."return_qty" AS "bridge_return_qty",
    -1 * p."closing_qty" AS "bridge_closing_qty",
    p."opening_qty"
      + p."purchase_qty"
      + p."transfer_in_qty"
      - p."transfer_out_qty"
      - p."return_qty"
      - p."closing_qty" AS "calculated_actual_consumption_qty",
    (
      p."opening_qty"
      + p."purchase_qty"
      + p."transfer_in_qty"
      - p."transfer_out_qty"
      - p."return_qty"
      - p."closing_qty"
    ) * p."average_unit_cost" AS "calculated_actual_consumption_value"
FROM "STD_CT_Inventory_Period" p
""",
    ),
    q(
        22,
        "fact",
        "FACT_CT_Consumption_Variance",
        "Compare actual and theoretical ingredient consumption.",
        ("FACT_CT_Actual_Consumption", "FACT_CT_Theoretical_Consumption"),
        """
SELECT
    a."source_period_code" AS "source_period_code",
    a."outlet_code" AS "outlet_code",
    a."outlet_name" AS "outlet_name",
    a."closing_date" AS "closing_date",
    a."item_code" AS "item_code",
    a."item_name" AS "item_name",
    a."category_name" AS "category_name",
    a."super_category_name" AS "super_category_name",
    a."canonical_uom" AS "canonical_uom",
    a."average_unit_cost" AS "average_unit_cost",
    a."calculated_actual_consumption_qty" AS "actual_consumption_qty",
    COALESCE(t."theoretical_consumption_qty", 0) AS "theoretical_consumption_qty",
    a."calculated_actual_consumption_qty" - COALESCE(t."theoretical_consumption_qty", 0) AS "variance_qty",
    (
        a."calculated_actual_consumption_qty"
        - COALESCE(t."theoretical_consumption_qty", 0)
    ) * a."average_unit_cost"
      AS "signed_consumption_variance_value",
    CASE
        WHEN a."calculated_actual_consumption_qty"
           > COALESCE(t."theoretical_consumption_qty", 0)
        THEN 'OVER_CONSUMPTION'
        WHEN a."calculated_actual_consumption_qty"
           < COALESCE(t."theoretical_consumption_qty", 0)
        THEN 'UNDER_CONSUMPTION'
        ELSE 'MATCHED'
    END AS "consumption_variance_direction",
    CASE
        WHEN a."calculated_actual_consumption_qty" > COALESCE(t."theoretical_consumption_qty", 0)
        THEN (a."calculated_actual_consumption_qty" - COALESCE(t."theoretical_consumption_qty", 0)) * a."average_unit_cost"
        ELSE 0
    END AS "leakage_value",
    CASE
        WHEN a."calculated_actual_consumption_qty" < COALESCE(t."theoretical_consumption_qty", 0)
        THEN COALESCE(t."theoretical_consumption_qty", 0) - a."calculated_actual_consumption_qty"
        ELSE 0
    END AS "low_consumption_qty"
FROM "FACT_CT_Actual_Consumption" a
LEFT JOIN "FACT_CT_Theoretical_Consumption" t
  ON a."source_period_code" = t."source_period_code"
 AND a."outlet_code" = t."outlet_code"
 AND a."item_code" = t."item_code"
""",
    ),
    q(
        23,
        "fact",
        "FACT_CT_Purchase_Order",
        "Calculate ordered, pending and open PO values.",
        ("STD_CT_Purchase_Order",),
        """
SELECT
    p.*,
    p."remaining_qty" * p."unit_price" AS "open_po_value",
    p."processed_qty" * p."unit_price" AS "processed_po_value",
    CASE
        WHEN p."is_open_po" = 1 AND p."expected_delivery_date" IS NULL THEN 1
        ELSE 0
    END AS "missing_expected_delivery_flag",
    CASE
        WHEN p."is_open_po" = 1
         AND p."expected_delivery_date" < p."as_of_date"
        THEN 1 ELSE 0
    END AS "delayed_po_flag"
FROM "STD_CT_Purchase_Order" p
""",
    ),
    q(
        24,
        "fact",
        "FACT_CT_Purchase_Receipt",
        "Expose PO-linked accepted receipt lines.",
        ("STD_CT_Purchase_Receipt",),
        """
SELECT r.*
FROM "STD_CT_Purchase_Receipt" r
""",
    ),
    q(
        25,
        "fact",
        "FACT_CT_PO_Receipt_Line",
        "Join exact PO number, outlet and item to receipt lines for fill-rate and OTIF logic.",
        (
            "STD_CT_Purchase_Order",
            "STD_CT_Purchase_Receipt",
        ),
        """
SELECT
    p."source_period_code" AS "source_period_code",
    p."as_of_date" AS "as_of_date",
    p."outlet_code" AS "outlet_code",
    p."outlet_name" AS "outlet_name",
    p."vendor_name" AS "vendor_name",
    p."po_number" AS "po_number",
    p."po_date" AS "po_date",
    p."expected_delivery_date" AS "expected_delivery_date",
    p."po_status" AS "po_status",
    p."item_code" AS "item_code",
    p."item_name" AS "item_name",
    p."category_name" AS "category_name",
    p."canonical_uom" AS "canonical_uom",
    p."ordered_qty" AS "ordered_qty",
    p."processed_qty" AS "processed_qty",
    p."remaining_qty" AS "remaining_qty",
    p."unit_price" AS "unit_price",
    p."gross_order_value" AS "gross_order_value",
    p."is_open_po" AS "is_open_po",
    p."remaining_qty" * p."unit_price" AS "open_po_value",
    r."receipt_date" AS "receipt_date",
    COALESCE(r."received_qty", 0) AS "received_qty",
    COALESCE(r."receipt_total", 0) AS "receipt_total",
    CASE
        WHEN r."receipt_date" IS NOT NULL
         AND p."expected_delivery_date" IS NOT NULL
         AND r."receipt_date" <= p."expected_delivery_date"
        THEN 1 ELSE 0
    END AS "on_time_flag",
    CASE
        WHEN COALESCE(r."received_qty", 0) >= p."ordered_qty" THEN 1 ELSE 0
    END AS "in_full_flag",
    CASE
        WHEN p."is_open_po" = 0
         AND r."receipt_date" IS NOT NULL
         AND p."expected_delivery_date" IS NOT NULL
        THEN 1 ELSE 0
    END AS "eligible_closed_line_flag",
    CASE
        WHEN p."is_open_po" = 0
         AND r."receipt_date" IS NOT NULL
         AND p."expected_delivery_date" IS NOT NULL
         AND r."receipt_date" <= p."expected_delivery_date"
         AND COALESCE(r."received_qty", 0) >= p."ordered_qty"
        THEN 1 ELSE 0
    END AS "otif_success_flag",
    CASE
        WHEN r."receipt_date" IS NOT NULL
         AND p."expected_delivery_date" IS NOT NULL
        THEN DATEDIFF(r."receipt_date", p."expected_delivery_date")
        ELSE NULL
    END AS "lead_time_deviation_days",
    CASE
        WHEN p."is_open_po" = 0
         AND r."receipt_date" IS NOT NULL
         AND p."expected_delivery_date" IS NOT NULL
        THEN DATEDIFF(r."receipt_date", p."expected_delivery_date")
        ELSE NULL
    END AS "eligible_lead_time_deviation_days",
    CASE
        WHEN p."is_open_po" = 1
         AND p."expected_delivery_date" IS NULL
        THEN 1 ELSE 0
    END AS "missing_expected_delivery_flag",
    CASE
        WHEN p."is_open_po" = 1
         AND p."expected_delivery_date" < p."as_of_date"
        THEN 1 ELSE 0
    END AS "delayed_po_flag"
FROM "STD_CT_Purchase_Order" p
LEFT JOIN (
    SELECT
        e."source_period_code" AS "source_period_code",
        e."outlet_code" AS "outlet_code",
        e."po_number" AS "po_number",
        e."item_code" AS "item_code",
        MAX(e."receipt_date") AS "receipt_date",
        SUM(e."received_qty") AS "received_qty",
        SUM(e."receipt_total") AS "receipt_total"
    FROM "STD_CT_Purchase_Receipt" e
    GROUP BY
        e."source_period_code",
        e."outlet_code",
        e."po_number",
        e."item_code"
) r
  ON p."outlet_code" = r."outlet_code"
 AND p."po_number" = r."po_number"
 AND p."item_code" = r."item_code"
 AND p."source_period_code" = r."source_period_code"
""",
    ),
    q(
        26,
        "fact",
        "FACT_CT_Vendor_Performance",
        "Provide vendor-line evidence for OTIF, fill rate, delay and returns.",
        ("FACT_CT_PO_Receipt_Line",),
        """
SELECT
    l.*,
    CASE
        WHEN l."ordered_qty" <> 0 THEN l."received_qty" / l."ordered_qty"
        ELSE NULL
    END AS "fill_rate"
FROM "FACT_CT_PO_Receipt_Line" l
""",
    ),
    q(
        27,
        "fact",
        "FACT_CT_Menu_Profitability",
        "Aggregate menu sales, theoretical COGS and recipe gross margin.",
        ("STD_CT_Sales_Item", "DIM_CT_Recipe_Effective"),
        """
SELECT
    s.*,
    COALESCE(c."theoretical_cost_per_menu_unit", 0)
      * s."sold_qty" AS "theoretical_cogs",
    s."net_sales"
      - COALESCE(c."theoretical_cost_per_menu_unit", 0)
      * s."sold_qty" AS "gross_margin_value",
    CASE
        WHEN s."net_sales" <> 0
        THEN (
          s."net_sales"
          - COALESCE(c."theoretical_cost_per_menu_unit", 0) * s."sold_qty"
        ) / s."net_sales" * 100
        ELSE NULL
    END AS "gross_margin_percent"
FROM (
    SELECT
        "source_period_code",
        "outlet_code",
        "outlet_name",
        "item_code" AS "menu_item_code",
        "item_name" AS "menu_item_name",
        "super_category_name",
        "category_name",
        SUM("sold_qty") AS "sold_qty",
        SUM("net_sales") AS "net_sales",
        SUM("source_purchase_value") AS "source_reported_purchase_value"
    FROM "STD_CT_Sales_Item"
    GROUP BY
        "source_period_code",
        "outlet_code",
        "outlet_name",
        "item_code",
        "item_name",
        "super_category_name",
        "category_name"
) s
LEFT JOIN (
    SELECT
        "menu_item_code",
        SUM("ingredient_cost_per_menu_unit") AS "theoretical_cost_per_menu_unit"
    FROM "DIM_CT_Recipe_Effective"
    GROUP BY "menu_item_code"
) c
  ON s."menu_item_code" = c."menu_item_code"
""",
    ),
    q(
        28,
        "fact",
        "FACT_CT_Forecast_Ingredient_Demand",
        "Convert menu demand forecast into ingredient requirements through the effective recipe.",
        ("STD_CT_Menu_Forecast", "DIM_CT_Recipe_Effective"),
        """
SELECT
    f."source_period_code" AS "source_period_code",
    f."forecast_date" AS "forecast_date",
    f."outlet_code" AS "outlet_code",
    f."outlet_name" AS "outlet_name",
    f."menu_item_code" AS "menu_item_code",
    f."menu_item_name" AS "menu_item_name",
    r."ingredient_code" AS "item_code",
    r."ingredient_name" AS "item_name",
    r."canonical_uom" AS "canonical_uom",
    f."forecast_menu_qty" AS "forecast_menu_qty",
    r."canonical_recipe_qty" AS "canonical_recipe_qty",
    f."forecast_menu_qty" * r."canonical_recipe_qty" AS "forecast_ingredient_qty",
    f."forecast_net_sales" AS "forecast_net_sales"
FROM "STD_CT_Menu_Forecast" f
INNER JOIN "DIM_CT_Recipe_Effective" r
  ON f."menu_item_code" = r."menu_item_code"
""",
    ),
    q(
        29,
        "fact",
        "FACT_CT_Inventory_Risk",
        "Calculate source-supported stockout and days-cover risk at ingredient checkpoint grain.",
        (
            "STD_CT_Inventory_Snapshot",
            "FACT_CT_Forecast_Ingredient_Demand",
            "FACT_CT_Purchase_Order",
        ),
        inventory_risk_sql(),
    ),
    q(
        30,
        "fact",
        "FACT_CT_Action_Queue",
        "Generate owner and action recommendations from the risk facts.",
        ("FACT_CT_Inventory_Risk",),
        """
SELECT
    CONCAT(r."source_period_code", ':', r."outlet_code", ':', r."item_code") AS "action_id",
    r."source_period_code",
    r."snapshot_date",
    r."outlet_code",
    r."outlet_name",
    r."item_code",
    r."item_name",
    r."category_name",
    r."risk_severity",
    r."shortage_qty",
    r."expiry_qty_at_risk",
    r."valid_open_po_qty",
    r."total_risk_value",
    CASE
        WHEN r."risk_severity" = 'PURPLE' AND r."valid_open_po_qty" = 0 THEN 'Raise purchase order'
        WHEN r."shortage_qty" > 0 AND r."valid_open_po_qty" > 0 THEN 'Expedite existing PO'
        WHEN r."expiry_qty_at_risk" > 0 THEN 'Transfer or consume near-expiry stock'
        ELSE 'Monitor'
    END AS "recommended_action",
    CASE
        WHEN r."shortage_qty" > 0 THEN 'Procurement'
        WHEN r."expiry_qty_at_risk" > 0 THEN 'Operations'
        ELSE 'Supply Chain'
    END AS "action_owner",
    CASE
        WHEN r."risk_severity" IN ('PURPLE', 'RED') THEN 'Due today'
        WHEN r."risk_severity" = 'AMBER' THEN 'Due in 3 days'
        ELSE 'Monitor'
    END AS "due_band",
    r."primary_vendor",
    r."alternate_vendor"
FROM "FACT_CT_Inventory_Risk" r
WHERE r."risk_severity" <> 'GREEN'
""",
    ),
    q(
        31,
        "fact",
        "FACT_CT_Menu_Impact",
        "Connect risky ingredients back to forecast menu items and revenue at risk.",
        (
            "STD_CT_Inventory_Snapshot",
            "FACT_CT_Forecast_Ingredient_Demand",
            "FACT_CT_Purchase_Order",
        ),
        """
WITH forecast_menu AS (
    SELECT
        "source_period_code",
        "outlet_code",
        "outlet_name",
        "menu_item_code",
        "menu_item_name",
        "item_code",
        "item_name",
        SUM("forecast_menu_qty") AS "forecast_menu_qty",
        SUM("forecast_ingredient_qty") AS "forecast_ingredient_qty",
        SUM("forecast_net_sales") AS "forecast_net_sales"
    FROM "FACT_CT_Forecast_Ingredient_Demand"
    GROUP BY
        "source_period_code",
        "outlet_code",
        "outlet_name",
        "menu_item_code",
        "menu_item_name",
        "item_code",
        "item_name"
),
po_open AS (
    SELECT
        "source_period_code",
        "outlet_code",
        "item_code",
        SUM("remaining_qty") AS "valid_open_po_qty"
    FROM "FACT_CT_Purchase_Order"
    WHERE "is_open_po" = 1
    GROUP BY "source_period_code", "outlet_code", "item_code"
),
risk_count AS (
    SELECT
        f."source_period_code" AS "source_period_code",
        f."outlet_code" AS "outlet_code",
        f."menu_item_code" AS "menu_item_code",
        COUNT(DISTINCT f."item_code") AS "risk_ingredient_count"
    FROM forecast_menu f
    INNER JOIN "STD_CT_Inventory_Snapshot" s
      ON f."source_period_code" = s."source_period_code"
     AND f."outlet_code" = s."outlet_code"
     AND f."item_code" = s."item_code"
    LEFT JOIN po_open p
      ON f."source_period_code" = p."source_period_code"
     AND f."outlet_code" = p."outlet_code"
     AND f."item_code" = p."item_code"
    WHERE (
        s."closing_qty" <= 0
        AND f."forecast_ingredient_qty" > 0
    )
       OR f."forecast_ingredient_qty" * 1.15
          > s."closing_qty" + COALESCE(p."valid_open_po_qty", 0)
    GROUP BY f."source_period_code", f."outlet_code", f."menu_item_code"
)
SELECT
    f."source_period_code",
    f."outlet_code",
    f."outlet_name",
    f."item_code" AS "ingredient_code",
    f."item_name" AS "ingredient_name",
    CASE
        WHEN s."closing_qty" <= 0 AND f."forecast_ingredient_qty" > 0
        THEN 'PURPLE'
        WHEN f."forecast_ingredient_qty"
           > s."closing_qty" + COALESCE(p."valid_open_po_qty", 0)
        THEN 'RED'
        WHEN f."forecast_ingredient_qty" * 1.15
           > s."closing_qty" + COALESCE(p."valid_open_po_qty", 0)
        THEN 'AMBER'
        ELSE 'GREEN'
    END AS "risk_severity",
    CASE
        WHEN f."forecast_ingredient_qty" * 1.15
           > s."closing_qty" + COALESCE(p."valid_open_po_qty", 0)
        THEN f."forecast_ingredient_qty" * 1.15
           - s."closing_qty" - COALESCE(p."valid_open_po_qty", 0)
        ELSE 0
    END AS "shortage_qty",
    f."menu_item_code",
    f."menu_item_name",
    f."forecast_menu_qty",
    f."forecast_net_sales" AS "forecast_net_sales_at_risk",
    c."risk_ingredient_count",
    f."forecast_net_sales" / c."risk_ingredient_count"
      AS "allocated_forecast_net_sales_at_risk"
FROM forecast_menu f
INNER JOIN "STD_CT_Inventory_Snapshot" s
  ON f."source_period_code" = s."source_period_code"
 AND f."outlet_code" = s."outlet_code"
 AND f."item_code" = s."item_code"
LEFT JOIN po_open p
  ON f."source_period_code" = p."source_period_code"
 AND f."outlet_code" = p."outlet_code"
 AND f."item_code" = p."item_code"
INNER JOIN risk_count c
  ON f."source_period_code" = c."source_period_code"
 AND f."outlet_code" = c."outlet_code"
 AND f."menu_item_code" = c."menu_item_code"
WHERE (
    s."closing_qty" <= 0
    AND f."forecast_ingredient_qty" > 0
)
   OR f."forecast_ingredient_qty" * 1.15
      > s."closing_qty" + COALESCE(p."valid_open_po_qty", 0)
""",
    ),
    q(
        32,
        "summary",
        "SUM_CT_Risk_Action",
        "Summarize outlet, menu, stockout and expiry exposure for Page 1.",
        ("FACT_CT_Inventory_Risk", "FACT_CT_Menu_Impact"),
        """
SELECT
    r."source_period_code",
    r."outlet_code",
    r."outlet_name",
    r."risk_severity",
    r."risk_item_count",
    r."stockout_risk_value",
    r."expiry_risk_value",
    r."total_risk_value",
    COALESCE(m."menu_items_impacted", 0) AS "menu_items_impacted",
    COALESCE(m."forecast_sales_at_risk", 0) AS "forecast_sales_at_risk"
FROM (
    SELECT
        "source_period_code",
        "outlet_code",
        "outlet_name",
        "risk_severity",
        COUNT(DISTINCT "item_code") AS "risk_item_count",
        SUM("shortage_qty" * "average_unit_cost") AS "stockout_risk_value",
        SUM("expiry_risk_value") AS "expiry_risk_value",
        SUM("total_risk_value") AS "total_risk_value"
    FROM "FACT_CT_Inventory_Risk"
    WHERE "risk_severity" <> 'GREEN'
    GROUP BY
        "source_period_code",
        "outlet_code",
        "outlet_name",
        "risk_severity"
) r
LEFT JOIN (
    SELECT
        "source_period_code",
        "outlet_code",
        "risk_severity",
        COUNT(DISTINCT "menu_item_code") AS "menu_items_impacted",
        SUM("forecast_net_sales_at_risk") AS "forecast_sales_at_risk"
    FROM "FACT_CT_Menu_Impact"
    GROUP BY
        "source_period_code",
        "outlet_code",
        "risk_severity"
) m
  ON r."source_period_code" = m."source_period_code"
 AND r."outlet_code" = m."outlet_code"
 AND r."risk_severity" = m."risk_severity"
""",
    ),
    q(
        33,
        "summary",
        "SUM_CT_Procurement_Funnel",
        "Summarize ordered, received, pending and delayed PO value for Page 2.",
        ("FACT_CT_Purchase_Order",),
        """
SELECT
    p."source_period_code",
    p."outlet_code",
    p."outlet_name",
    p."vendor_name",
    SUM(p."gross_order_value") AS "ordered_value",
    SUM(p."processed_po_value") AS "processed_value",
    SUM(p."open_po_value") AS "pending_value",
    SUM(CASE WHEN p."delayed_po_flag" = 1 THEN p."open_po_value" ELSE 0 END) AS "delayed_value",
    COUNT(DISTINCT p."po_number") AS "po_count",
    COUNT(DISTINCT CASE WHEN p."is_open_po" = 1 THEN p."po_number" ELSE NULL END) AS "open_po_count"
FROM "FACT_CT_Purchase_Order" p
GROUP BY
    p."source_period_code",
    p."outlet_code",
    p."outlet_name",
    p."vendor_name"
""",
    ),
    q(
        34,
        "summary",
        "SUM_CT_Vendor_Scorecard",
        "Summarize fill rate, OTIF and open PO exposure by vendor.",
        ("FACT_CT_PO_Receipt_Line",),
        """
SELECT
    v."source_period_code",
    v."outlet_code",
    v."outlet_name",
    v."vendor_name",
    SUM(v."gross_order_value") AS "monthly_purchase_value",
    SUM(v."remaining_qty" * v."unit_price") AS "open_po_value",
    CASE
        WHEN SUM(v."eligible_closed_line_flag") <> 0
        THEN SUM(v."otif_success_flag")
          / SUM(v."eligible_closed_line_flag") * 100
        ELSE NULL
    END AS "otif_percent",
    CASE
        WHEN SUM(v."ordered_qty") <> 0
        THEN SUM(v."received_qty") / SUM(v."ordered_qty") * 100
        ELSE NULL
    END AS "fill_rate_percent",
    AVG(
        CASE
            WHEN v."eligible_closed_line_flag" = 1
            THEN v."lead_time_deviation_days"
            ELSE NULL
        END
    ) AS "average_lead_time_deviation_days",
    SUM(v."delayed_po_flag") AS "delayed_po_line_count"
FROM "FACT_CT_PO_Receipt_Line" v
GROUP BY
    v."source_period_code",
    v."outlet_code",
    v."outlet_name",
    v."vendor_name"
""",
    ),
    q(
        35,
        "summary",
        "SUM_CT_Price_Movement",
        "Compare weighted receipt prices with the immediately prior synthetic month.",
        ("FACT_CT_Purchase_Receipt",),
        """
SELECT
    c."source_period_code",
    c."outlet_code",
    c."outlet_name",
    c."vendor_name",
    c."item_code",
    c."item_name",
    c."canonical_uom",
    CONCAT(
        c."outlet_code", ' | ',
        c."vendor_name", ' | ',
        c."item_name", ' | ',
        c."canonical_uom"
    ) AS "price_comparison_key",
    c."current_unit_price",
    p."current_unit_price" AS "previous_unit_price",
    c."current_unit_price" - p."current_unit_price" AS "unit_price_change",
    CASE
        WHEN c."current_unit_price" > p."current_unit_price" THEN 'INCREASE'
        WHEN c."current_unit_price" < p."current_unit_price" THEN 'DECREASE'
        ELSE 'NO_CHANGE'
    END AS "price_movement_direction",
    CASE
        WHEN p."current_unit_price" <> 0
        THEN (c."current_unit_price" - p."current_unit_price") / p."current_unit_price" * 100
        ELSE NULL
    END AS "unit_price_change_percent",
    CASE
        WHEN p."current_unit_price" <> 0
        THEN ABS(
            (c."current_unit_price" - p."current_unit_price")
            / p."current_unit_price" * 100
        )
        ELSE NULL
    END AS "absolute_unit_price_change_percent"
FROM (
    SELECT
        "source_period_code",
        "outlet_code",
        "outlet_name",
        "vendor_name",
        "item_code",
        "item_name",
        "canonical_uom",
        SUM("receipt_subtotal") / NULLIF(SUM("received_qty"), 0) AS "current_unit_price"
    FROM "FACT_CT_Purchase_Receipt"
    GROUP BY
        "source_period_code",
        "outlet_code",
        "outlet_name",
        "vendor_name",
        "item_code",
        "item_name",
        "canonical_uom"
) c
LEFT JOIN (
    SELECT
        "source_period_code",
        "outlet_code",
        "vendor_name",
        "item_code",
        SUM("receipt_subtotal") / NULLIF(SUM("received_qty"), 0) AS "current_unit_price"
    FROM "FACT_CT_Purchase_Receipt"
    GROUP BY "source_period_code", "outlet_code", "vendor_name", "item_code"
) p
  ON c."outlet_code" = p."outlet_code"
 AND c."vendor_name" = p."vendor_name"
 AND c."item_code" = p."item_code"
 AND (
      (c."source_period_code" = 'month_02' AND p."source_period_code" = 'month_01')
   OR (c."source_period_code" = 'month_03' AND p."source_period_code" = 'month_02')
 )
""",
    ),
    q(
        36,
        "summary",
        "SUM_CT_Consumption_Variance",
        "Summarize consumption leakage and low-consumption checks for Page 3.",
        ("FACT_CT_Consumption_Variance",),
        """
SELECT
    v."source_period_code",
    v."outlet_code",
    v."outlet_name",
    v."item_code",
    v."item_name",
    v."category_name",
    v."canonical_uom",
    SUM(v."actual_consumption_qty") AS "actual_consumption_qty",
    SUM(v."theoretical_consumption_qty") AS "theoretical_consumption_qty",
    SUM(v."variance_qty") AS "variance_qty",
    SUM(v."leakage_value") AS "leakage_value",
    SUM(v."low_consumption_qty") AS "low_consumption_qty"
FROM "FACT_CT_Consumption_Variance" v
GROUP BY
    v."source_period_code",
    v."outlet_code",
    v."outlet_name",
    v."item_code",
    v."item_name",
    v."category_name",
    v."canonical_uom"
""",
    ),
    q(
        37,
        "summary",
        "SUM_CT_Menu_Profitability",
        "Expose menu profitability with BCG quadrant classification.",
        ("FACT_CT_Menu_Profitability",),
        """
SELECT
    m.*,
    CASE
        WHEN m."sold_qty" >= 150 AND m."gross_margin_percent" >= 60 THEN 'Stars'
        WHEN m."sold_qty" < 150 AND m."gross_margin_percent" >= 60 THEN 'Niche gems'
        WHEN m."sold_qty" >= 150 AND m."gross_margin_percent" < 60 THEN 'Volume drags'
        ELSE 'Review / rationalize'
    END AS "bcg_quadrant"
FROM "FACT_CT_Menu_Profitability" m
""",
    ),
    q(
        38,
        "summary",
        "SUM_CT_SCM_Monthly",
        "Join monthly sales, closing stock, open PO and actual consumption for Page 4.",
        (
            "FACT_CT_Sales",
            "STD_CT_Inventory_Snapshot",
            "FACT_CT_Purchase_Order",
            "FACT_CT_Actual_Consumption",
        ),
        """
SELECT
    k."source_period_code",
    k."outlet_code",
    k."outlet_name",
    COALESCE(s."net_sales", 0) AS "net_sales",
    COALESCE(i."closing_stock_value", 0) AS "closing_stock_value",
    COALESCE(p."open_po_value", 0) AS "open_po_value",
    COALESCE(i."closing_stock_value", 0)
      + COALESCE(p."open_po_value", 0) AS "working_capital_value",
    COALESCE(a."actual_consumption_value", 0) AS "actual_consumption_value"
FROM (
    SELECT DISTINCT
        "source_period_code" AS "source_period_code",
        "outlet_code" AS "outlet_code",
        "outlet_name" AS "outlet_name"
    FROM "STD_CT_Inventory_Snapshot"
) k
LEFT JOIN (
    SELECT
        "source_period_code" AS "source_period_code",
        "outlet_code" AS "outlet_code",
        SUM("net_sales") AS "net_sales"
    FROM "FACT_CT_Sales"
    GROUP BY "source_period_code", "outlet_code"
) s
  ON k."source_period_code" = s."source_period_code"
 AND k."outlet_code" = s."outlet_code"
LEFT JOIN (
    SELECT
        "source_period_code" AS "source_period_code",
        "outlet_code" AS "outlet_code",
        SUM("closing_value") AS "closing_stock_value"
    FROM "STD_CT_Inventory_Snapshot"
    GROUP BY "source_period_code", "outlet_code"
) i
  ON k."source_period_code" = i."source_period_code"
 AND k."outlet_code" = i."outlet_code"
LEFT JOIN (
    SELECT
        "source_period_code" AS "source_period_code",
        "outlet_code" AS "outlet_code",
        SUM("open_po_value") AS "open_po_value"
    FROM "FACT_CT_Purchase_Order"
    WHERE "is_open_po" = 1
    GROUP BY "source_period_code", "outlet_code"
) p
  ON k."source_period_code" = p."source_period_code"
 AND k."outlet_code" = p."outlet_code"
LEFT JOIN (
    SELECT
        "source_period_code" AS "source_period_code",
        "outlet_code" AS "outlet_code",
        SUM("calculated_actual_consumption_value") AS "actual_consumption_value"
    FROM "FACT_CT_Actual_Consumption"
    GROUP BY "source_period_code", "outlet_code"
) a
  ON k."source_period_code" = a."source_period_code"
 AND k."outlet_code" = a."outlet_code"
""",
    ),
    q(
        39,
        "fact",
        "FACT_CT_Data_Quality_Exception",
        "Produce drillable Page 4 exception rows with period, outlet and source references.",
        (
            "STD_CT_Inventory_Snapshot",
            "FACT_CT_Forecast_Ingredient_Demand",
            "STD_CT_Sales_Item",
            "STD_CT_Recipe",
            "FACT_CT_Purchase_Order",
            "STD_CT_Purchase_Order",
            "STD_CT_Purchase_Receipt",
            "STD_CT_Inventory_Movement",
            "STD_CT_Vendor_Report",
            "DIM_CT_Item",
        ),
        """
SELECT
    "source_period_code",
    "outlet_code",
    "outlet_name",
    'NEGATIVE_STOCK' AS "exception_type",
    CONCAT("source_period_code", ':', "outlet_code", ':', "item_code")
      AS "exception_record_key",
    "item_code",
    '' AS "reference_number",
    1 AS "exception_count",
    'Closing quantity below zero' AS "definition"
FROM "STD_CT_Inventory_Snapshot"
WHERE "closing_qty" < 0
UNION ALL
SELECT
    s."source_period_code",
    s."outlet_code",
    s."outlet_name",
    'ZERO_STOCK_WITH_DEMAND',
    CONCAT(s."source_period_code", ':', s."outlet_code", ':', s."item_code"),
    s."item_code",
    '',
    1,
    'Zero closing stock with positive seven-day forecast ingredient demand'
FROM "STD_CT_Inventory_Snapshot" s
INNER JOIN (
    SELECT
        "source_period_code",
        "outlet_code",
        "item_code",
        SUM("forecast_ingredient_qty") AS "forecast_required_qty"
    FROM "FACT_CT_Forecast_Ingredient_Demand"
    GROUP BY "source_period_code", "outlet_code", "item_code"
) f
  ON s."source_period_code" = f."source_period_code"
 AND s."outlet_code" = f."outlet_code"
 AND s."item_code" = f."item_code"
WHERE s."closing_qty" = 0
  AND f."forecast_required_qty" > 0
UNION ALL
SELECT DISTINCT
    s."source_period_code",
    s."outlet_code",
    s."outlet_name",
    'SOLD_ITEM_MISSING_RECIPE',
    CONCAT(s."source_period_code", ':', s."outlet_code", ':', s."item_code"),
    s."item_code",
    '',
    1,
    'Sold menu item without a recipe mapping'
FROM "STD_CT_Sales_Item" s
LEFT JOIN "STD_CT_Recipe" r
  ON s."item_code" = r."menu_item_code"
WHERE r."menu_item_code" IS NULL
UNION ALL
SELECT
    "source_period_code",
    "outlet_code",
    MAX("outlet_name") AS "outlet_name",
    'OPEN_PO_MISSING_EXPECTED_DELIVERY',
    CONCAT("source_period_code", ':', "outlet_code", ':', "po_number"),
    '' AS "item_code",
    "po_number" AS "reference_number",
    1,
    'Open PO without expected delivery date'
FROM "FACT_CT_Purchase_Order"
WHERE "missing_expected_delivery_flag" = 1
GROUP BY "source_period_code", "outlet_code", "po_number"
UNION ALL
SELECT DISTINCT
    x."source_period_code",
    x."outlet_code",
    x."outlet_name",
    'OPERATIONAL_ITEM_MISSING_MASTER',
    CONCAT(x."source_period_code", ':', x."outlet_code", ':', x."item_code"),
    x."item_code",
    '',
    1,
    'Operational item identifier absent from the canonical item master'
FROM (
    SELECT
        "source_period_code" AS "source_period_code",
        "outlet_code" AS "outlet_code",
        "outlet_name" AS "outlet_name",
        "item_code" AS "item_code"
    FROM "STD_CT_Inventory_Snapshot"
    UNION ALL
    SELECT
        "source_period_code" AS "source_period_code",
        "outlet_code" AS "outlet_code",
        "outlet_name" AS "outlet_name",
        "item_code" AS "item_code"
    FROM "FACT_CT_Purchase_Order"
    UNION ALL
    SELECT
        "source_period_code" AS "source_period_code",
        "outlet_code" AS "outlet_code",
        "outlet_name" AS "outlet_name",
        "item_code" AS "item_code"
    FROM "STD_CT_Purchase_Receipt"
    UNION ALL
    SELECT
        "source_period_code" AS "source_period_code",
        "outlet_code" AS "outlet_code",
        "outlet_name" AS "outlet_name",
        "item_code" AS "item_code"
    FROM "STD_CT_Inventory_Movement"
) x
LEFT JOIN "DIM_CT_Item" i
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
FROM "STD_CT_Vendor_Report" v
WHERE v."vendor_code" IS NOT NULL
GROUP BY v."vendor_name"
HAVING COUNT(DISTINCT v."vendor_code") > 1
UNION ALL
SELECT DISTINCT
    t."source_period_code",
    t."outlet_code",
    t."outlet_name",
    'TRANSACTION_VENDOR_MISSING_VENDOR_REPORT',
    CONCAT(t."source_period_code", ':', t."outlet_code", ':', t."vendor_name"),
    '',
    t."vendor_name",
    1,
    'Vendor observed in PO or Entry but absent from the cleaned Vendor Report'
FROM (
    SELECT
        "source_period_code",
        "outlet_code",
        "outlet_name",
        "vendor_name"
    FROM "STD_CT_Purchase_Order"
    UNION ALL
    SELECT
        "source_period_code",
        "outlet_code",
        "outlet_name",
        "vendor_name"
    FROM "STD_CT_Purchase_Receipt"
) t
LEFT JOIN (
    SELECT DISTINCT "vendor_name" AS "vendor_name"
    FROM "STD_CT_Vendor_Report"
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
    x."item_code",
    '',
    1,
    'Item observed in multiple units without a complete canonical conversion'
FROM (
    SELECT
        "item_code" AS "item_code",
        "canonical_uom" AS "observed_uom"
    FROM "STD_CT_Inventory_Snapshot"
    UNION ALL
    SELECT
        "item_code" AS "item_code",
        "canonical_uom" AS "observed_uom"
    FROM "FACT_CT_Purchase_Order"
    UNION ALL
    SELECT
        "item_code" AS "item_code",
        "canonical_uom" AS "observed_uom"
    FROM "STD_CT_Purchase_Receipt"
    UNION ALL
    SELECT
        "item_code" AS "item_code",
        "canonical_uom" AS "observed_uom"
    FROM "STD_CT_Inventory_Movement"
) x
LEFT JOIN "DIM_CT_Item" i
  ON x."item_code" = i."item_code"
GROUP BY x."item_code"
HAVING COUNT(DISTINCT x."observed_uom") > 1
   AND MAX(
       CASE
           WHEN i."item_code" IS NOT NULL
            AND i."uom_conversion_factor" IS NOT NULL
           THEN 1 ELSE 0
       END
   ) = 0
""",
    ),
    q(
        40,
        "summary",
        "SUM_CT_Financial_Leakage",
        "Summarize observed wastage separately from demo expiry and unavailable vendor returns.",
        ("STD_CT_Wastage",),
        """
SELECT
    "source_period_code",
    "outlet_code",
    "outlet_name",
    'WASTAGE' AS "leakage_type",
    SUM("wastage_value") AS "leakage_value",
    'observed' AS "evidence_type"
FROM "STD_CT_Wastage"
GROUP BY "source_period_code", "outlet_code", "outlet_name"
""",
    ),
    q(
        41,
        "fact",
        "FACT_CT_Risky_PO",
        "Retain exact open PO lines whose ingredients are currently red, purple or amber.",
        (
            "STD_CT_Inventory_Snapshot",
            "FACT_CT_Forecast_Ingredient_Demand",
            "FACT_CT_Purchase_Order",
        ),
        """
WITH forecast_item AS (
    SELECT
        "source_period_code",
        "outlet_code",
        "item_code",
        SUM("forecast_ingredient_qty") AS "forecast_required_qty"
    FROM "FACT_CT_Forecast_Ingredient_Demand"
    GROUP BY "source_period_code", "outlet_code", "item_code"
),
open_po AS (
    SELECT
        "source_period_code",
        "outlet_code",
        "item_code",
        SUM("remaining_qty") AS "valid_open_po_qty"
    FROM "FACT_CT_Purchase_Order"
    WHERE "is_open_po" = 1
    GROUP BY "source_period_code", "outlet_code", "item_code"
),
risk_item AS (
    SELECT
        s."source_period_code",
        s."outlet_code",
        s."item_code",
        CASE
            WHEN s."closing_qty" <= 0
             AND COALESCE(f."forecast_required_qty", 0) > 0
            THEN 'PURPLE'
            WHEN COALESCE(f."forecast_required_qty", 0)
               > s."closing_qty" + COALESCE(o."valid_open_po_qty", 0)
            THEN 'RED'
            WHEN COALESCE(f."forecast_required_qty", 0) * 1.15
               > s."closing_qty" + COALESCE(o."valid_open_po_qty", 0)
            THEN 'AMBER'
            ELSE 'GREEN'
        END AS "risk_severity"
    FROM "STD_CT_Inventory_Snapshot" s
    LEFT JOIN forecast_item f
      ON s."source_period_code" = f."source_period_code"
     AND s."outlet_code" = f."outlet_code"
     AND s."item_code" = f."item_code"
    LEFT JOIN open_po o
      ON s."source_period_code" = o."source_period_code"
     AND s."outlet_code" = o."outlet_code"
     AND s."item_code" = o."item_code"
)
SELECT
    p.*,
    r."risk_severity"
FROM "FACT_CT_Purchase_Order" p
INNER JOIN risk_item r
  ON p."source_period_code" = r."source_period_code"
 AND p."outlet_code" = r."outlet_code"
 AND p."item_code" = r."item_code"
WHERE p."is_open_po" = 1
  AND r."risk_severity" <> 'GREEN'
""",
    ),
]

REPORT_LAYER_VIEWS = {
    "FACT_CT_Vendor_Performance": (
        "Use FACT_CT_PO_Receipt_Line directly for vendor detail reports."
    ),
    "FACT_CT_Action_Queue": (
        "Action, owner and due-band fields are embedded in FACT_CT_Inventory_Risk."
    ),
    "SUM_CT_Risk_Action": (
        "Build Page 1 widgets from FACT_CT_Inventory_Risk and "
        "FACT_CT_Menu_Impact aggregate formulas."
    ),
    "SUM_CT_Consumption_Variance": (
        "Build Page 3 and Page 4 variance views directly from "
        "FACT_CT_Consumption_Variance."
    ),
}
GATED_QUERY_TABLES = {
    "STD_CT_Expiry_Estimate": (
        "The old expiry standardization step is retired. Query 38 exposes the "
        "new explicitly synthetic scenario directly, while production expiry "
        "remains gated until batch evidence exists."
    ),
    "STD_CT_Vendor_Return": (
        "Enterprise Stock Return is header-only in the audited UAT export. "
        "Create this table only after a populated extract passes the same audit."
    ),
}


def use_zoho_import_table_names(query: Query) -> Query:
    sql = query.sql
    for logical_name, zoho_name in ZOHO_IMPORT_TABLE_NAMES.items():
        sql = sql.replace(f'"{logical_name}"', f'"{zoho_name}"')
    return replace(
        query,
        sources=tuple(
            ZOHO_IMPORT_TABLE_NAMES.get(source, source) for source in query.sources
        ),
        sql=sql,
    )


QUERIES = [
    replace(use_zoho_import_table_names(query), order=index)
    for index, query in enumerate(
        [
            query
            for query in QUERIES
            if query.name not in REPORT_LAYER_VIEWS
            and query.name not in GATED_QUERY_TABLES
        ],
        start=1,
    )
]

EXTENSION_QUERIES = [
    q(
        1,
        "dimension",
        "DIM_CT_Outlet_Enriched",
        "Enrich source-derived outlet identity with synthetic demonstrator geography.",
        ("DIM_CT_Outlet",),
        """
SELECT
    d."outlet_code" AS "outlet_code",
    d."outlet_name" AS "outlet_name",
    'North' AS "region",
    'Delhi' AS "city",
    CASE
        WHEN d."outlet_code" = 'OUT001' THEN 'Connaught Place'
        WHEN d."outlet_code" = 'OUT002' THEN 'Hauz Khas'
        WHEN d."outlet_code" = 'OUT003' THEN 'Saket'
        ELSE 'Unmapped'
    END AS "market_area",
    CASE
        WHEN d."outlet_code" = 'OUT001' THEN 28.6315
        WHEN d."outlet_code" = 'OUT002' THEN 28.5494
        WHEN d."outlet_code" = 'OUT003' THEN 28.5245
        ELSE 0
    END AS "latitude",
    CASE
        WHEN d."outlet_code" = 'OUT001' THEN 77.2167
        WHEN d."outlet_code" = 'OUT002' THEN 77.2001
        WHEN d."outlet_code" = 'OUT003' THEN 77.2066
        ELSE 0
    END AS "longitude",
    CASE
        WHEN d."outlet_code" = 'OUT003' THEN 'New'
        ELSE 'Matured'
    END AS "new_matured_flag",
    'Active' AS "active_status",
    'synthetic_demo_geography_on_source_derived_outlet'
      AS "source_evidence",
    1 AS "is_synthetic",
    'replace_with_approved_abnah_outlet_reference'
      AS "production_use_status"
FROM "DIM_CT_Outlet" d
WHERE d."outlet_code" IN ('OUT001', 'OUT002', 'OUT003')
""",
    ),
    q(
        2,
        "fact",
        "FACT_CT_Expiry_Risk",
        "Expose traceable batch-linked demo expiry exposure without claiming POSIST batch truth.",
        ("AUX_Expiry_Estimate",),
        """
SELECT
    e."source_period_code" AS "source_period_code",
    e."as_of_date" AS "as_of_date",
    e."outlet_code" AS "outlet_code",
    e."outlet_name" AS "outlet_name",
    e."region" AS "region",
    e."city" AS "city",
    e."market_area" AS "market_area",
    e."latitude" AS "latitude",
    e."longitude" AS "longitude",
    e."store_name" AS "store_name",
    e."batch_allocation_id" AS "batch_allocation_id",
    e."batch_number" AS "batch_number",
    e."receipt_date" AS "receipt_date",
    e."grn_number" AS "grn_number",
    e."po_number" AS "po_number",
    e."vendor_name" AS "vendor_name",
    e."receipt_source_status" AS "receipt_source_status",
    e."item_code" AS "item_code",
    e."item_name" AS "item_name",
    e."category_name" AS "category_name",
    e."unit" AS "canonical_uom",
    e."available_qty" AS "available_qty",
    e."received_qty" AS "received_qty",
    e."batch_remaining_qty" AS "batch_remaining_qty",
    e."item_closing_qty" AS "item_closing_qty",
    e."qty_at_risk" AS "expiry_qty_at_risk",
    e."average_unit_cost" AS "average_unit_cost",
    e."shelf_life_days_assumption" AS "shelf_life_days_assumption",
    e."estimated_fifo_tranche_qty" AS "estimated_fifo_tranche_qty",
    e."daily_theoretical_demand" AS "daily_theoretical_demand",
    e."expected_consumption_before_expiry"
      AS "expected_consumption_before_expiry",
    e."estimated_expiry_date" AS "estimated_expiry_date",
    e."days_to_expiry" AS "days_to_expiry",
    e."expiry_risk_value" AS "expiry_risk_value",
    e."risk_status" AS "expiry_batch_risk_status",
    'EXPIRY' AS "risk_type",
    CASE
        WHEN e."risk_status" IN ('EXPIRED', 'EXPIRES_TODAY')
        THEN 'PURPLE'
        WHEN e."risk_status" = 'CRITICAL' THEN 'RED'
        ELSE 'AMBER'
    END AS "risk_severity",
    CASE
        WHEN e."risk_status" IN ('EXPIRED', 'EXPIRES_TODAY') THEN 4
        WHEN e."risk_status" = 'CRITICAL' THEN 3
        ELSE 2
    END AS "risk_severity_rank",
    e."batch_allocation_id" AS "action_id",
    CASE
        WHEN e."risk_status" = 'EXPIRED'
        THEN 'Quarantine expired batch and investigate'
        WHEN e."risk_status" IN ('EXPIRES_TODAY', 'CRITICAL')
        THEN 'Transfer, promote, or consume near-expiry stock'
        ELSE 'Review FIFO rotation and demand plan'
    END AS "recommended_action",
    'Operations' AS "action_owner",
    CASE
        WHEN e."risk_status" IN (
            'EXPIRED', 'EXPIRES_TODAY', 'CRITICAL'
        )
        THEN 'Due today'
        ELSE 'Due in 3 days'
    END AS "due_band",
    e."is_estimated" AS "is_estimated",
    e."estimation_method" AS "estimation_method",
    e."source_evidence" AS "source_evidence",
    e."production_use_status" AS "production_use_status"
FROM "AUX_Expiry_Estimate" e
""",
    ),
]
CORE_QUERY_COUNT = len(QUERIES)
QUERIES.extend(
    [
        replace(
            use_zoho_import_table_names(query),
            order=CORE_QUERY_COUNT + index,
        )
        for index, query in enumerate(EXTENSION_QUERIES, start=1)
    ]
)

QUERY_TABLE_NAME_BY_LOGICAL = {
    query.name: query.filename for query in QUERIES
}


def zoho_source_name(source: str) -> str:
    return QUERY_TABLE_NAME_BY_LOGICAL.get(source, source)


def render_query_sql(query: Query) -> str:
    sql = query.sql
    for logical_name, query_table_name in QUERY_TABLE_NAME_BY_LOGICAL.items():
        sql = sql.replace(f'"{logical_name}"', f'"{query_table_name}"')
    return sql


def dependency_levels(queries: list[Query]) -> dict[str, int]:
    levels: dict[str, int] = {}
    for query in queries:
        source_levels = [levels.get(source, 0) for source in query.sources]
        levels[query.name] = max(source_levels, default=0) + 1
    return levels


def validate_queries(queries: list[Query]) -> None:
    if [query.order for query in queries] != list(range(1, len(queries) + 1)):
        raise ValueError("Query order must be contiguous and start at 1.")
    names = [query.name for query in queries]
    if len(names) != len(set(names)):
        raise ValueError("Query table names must be unique.")
    available = set(ZOHO_IMPORT_TABLE_NAMES.values())
    levels: dict[str, int] = {}
    for query in queries:
        missing = set(query.sources) - available
        if missing:
            raise ValueError(f"{query.name} references sources not yet built: {sorted(missing)}")
        level = max((levels.get(source, 0) for source in query.sources), default=0) + 1
        if level > 3:
            raise ValueError(
                f"{query.name} would be Query Table level {level}; Zoho allows at most 3."
            )
        levels[query.name] = level
        available.add(query.name)
        if not query.sql.rstrip().endswith(";"):
            object.__setattr__(query, "sql", query.sql.rstrip() + ";\n")
        if query.sql.lstrip().upper().startswith("WITH "):
            cte_count = len(CTE_DEFINITION_RE.findall(query.sql))
            if cte_count > 3:
                raise ValueError(
                    f"{query.name} defines {cte_count} CTEs; Zoho allows at most 3."
                )
            if DERIVED_SUBQUERY_RE.search(query.sql):
                raise ValueError(
                    f"{query.name} contains a subquery inside a CTE query, "
                    "which Zoho does not support."
                )
        subquery_depth = max_derived_subquery_depth(query.sql)
        if subquery_depth > 1:
            raise ValueError(
                f"{query.name} nests FROM subqueries {subquery_depth} levels deep; "
                "Zoho allows only 1."
            )
        rendered_sql = render_query_sql(query)
        unresolved = [
            logical_name
            for logical_name in QUERY_TABLE_NAME_BY_LOGICAL
            if f'"{logical_name}"' in rendered_sql
        ]
        if unresolved:
            raise ValueError(
                f"{query.name} has unresolved Zoho Query Table names: {unresolved}"
            )


def build() -> None:
    validate_queries(QUERIES)
    levels = dependency_levels(QUERIES)
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir(parents=True)

    for query in QUERIES:
        rendered_sources = [zoho_source_name(source) for source in query.sources]
        header = "\n".join(
            [
                f"-- Query Table: {query.filename}",
                f"-- Logical model name: {query.name}",
                f"-- Layer: {query.layer}",
                f"-- Purpose: {query.purpose}",
                f"-- Sources: {', '.join(rendered_sources)}",
                "-- Validate CAST/date function behavior once in the target Zoho workspace.",
                "",
            ]
        )
        (OUTPUT / query.filename).write_text(
            header + render_query_sql(query),
            encoding="utf-8",
        )

    with (OUTPUT / "QUERY_TABLE_MANIFEST.csv").open(
        "w", encoding="utf-8-sig", newline=""
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "build_order",
                "layer",
                "query_table_name",
                "logical_model_name",
                "dependency_level",
                "purpose",
                "sources",
                "sql_file",
            ],
        )
        writer.writeheader()
        for query in QUERIES:
            writer.writerow(
                {
                    "build_order": query.order,
                    "layer": query.layer,
                    "query_table_name": query.filename,
                    "logical_model_name": query.name,
                    "dependency_level": levels[query.name],
                    "purpose": query.purpose,
                    "sources": ";".join(
                        zoho_source_name(source) for source in query.sources
                    ),
                    "sql_file": query.filename,
                }
            )

    readme = [
        "# ABNAH Control Tower v2 Query Tables",
        "",
        f"Build the SQL files in numeric order. The pack contains {len(QUERIES)} Query Tables:",
        "",
        f"- {sum(query.layer == 'standardized' for query in QUERIES)} standardized tables",
        f"- {sum(query.layer == 'dimension' for query in QUERIES)} dimensions",
        f"- {sum(query.layer == 'fact' for query in QUERIES)} facts",
        f"- {sum(query.layer == 'summary' for query in QUERIES)} summaries",
        "",
        "Every Query Table is dependency level 1, 2, or 3. This is a hard build constraint in Zoho Analytics.",
        "",
        f"This build targets the {len(ZOHO_IMPORT_TABLE_NAMES)} Zoho import tables whose names end in `-Copy`.",
        "",
        "Save every Query Table with the exact SQL filename, including the numeric prefix and `.sql` suffix. All downstream SQL already references that exact Zoho table name.",
        "",
        "In `QUERY_TABLE_MANIFEST.csv`, `query_table_name` is the physical Zoho name and `logical_model_name` is the semantic label used in dashboard documentation.",
        "",
        "The following conceptual views are implemented as reports or aggregate formulas instead of additional Query Tables:",
        "",
        *[f"- `{name}`: {reason}" for name, reason in REPORT_LAYER_VIEWS.items()],
        "",
        "The following legacy or unavailable-source Query Tables remain gated:",
        "",
        *[f"- `{name}`: {reason}" for name, reason in GATED_QUERY_TABLES.items()],
        "",
        "The original 37-table model remains a legacy reference. This v2 package uses the validated Restroworks landing contracts and should be used for the four-page control tower.",
        "",
        "Do not create a Query Table until every source listed in its file header exists. Run the validation queries documented in `../zoho_control_tower_v2_validation.md` after each layer.",
    ]
    (OUTPUT / "README.md").write_text("\n".join(readme) + "\n", encoding="utf-8")


if __name__ == "__main__":
    build()
    print(f"Generated {len(QUERIES)} Control Tower v2 SQL files in {OUTPUT}")
