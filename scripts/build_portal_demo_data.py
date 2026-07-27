"""Build the secret-free synthetic data pack used to verify the custom portal."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TRUTH = (
    ROOT
    / "project-pack"
    / "zoho-control-tower"
    / "exports"
    / "control_tower_zoho"
    / "truth"
)
NORMALIZED = TRUTH.parent / "normalized"
OUTPUTS = (
    ROOT / "public" / "data" / "control-tower-portal-demo.json",
    ROOT / "github-pages" / "public" / "data" / "control-tower-portal-demo.json",
)

OUTLETS = {
    "OUT001": {
        "region": "North",
        "city": "New Delhi",
        "market_area": "Connaught Place",
        "latitude": 28.6315,
        "longitude": 77.2167,
    },
    "OUT002": {
        "region": "North",
        "city": "New Delhi",
        "market_area": "Hauz Khas",
        "latitude": 28.5494,
        "longitude": 77.2001,
    },
    "OUT003": {
        "region": "North",
        "city": "New Delhi",
        "market_area": "Saket",
        "latitude": 28.5245,
        "longitude": 77.2066,
    },
}

NUMERIC_FIELDS = {
    "average_unit_cost",
    "current_stock_qty",
    "closing_value",
    "forecast_required_qty",
    "required_qty_with_safety",
    "valid_open_po_qty",
    "valid_open_po_count",
    "open_po_value",
    "shortage_qty",
    "days_cover",
    "risk_severity_rank",
    "shortage_cost_value",
    "total_risk_value",
    "forecast_menu_qty",
    "risk_ingredient_count",
    "forecast_net_sales_at_risk",
    "allocated_forecast_net_sales_at_risk",
    "available_qty",
    "received_qty",
    "batch_remaining_qty",
    "item_closing_qty",
    "expiry_qty_at_risk",
    "qty_at_risk",
    "shelf_life_days_assumption",
    "estimated_fifo_tranche_qty",
    "daily_theoretical_demand",
    "expected_consumption_before_expiry",
    "days_to_expiry",
    "expiry_risk_value",
    "is_estimated",
    "processed_qty",
    "remaining_balance_qty",
    "ordered_qty",
    "unit_price",
    "subtotal",
    "new_subtotal",
    "tax_amt",
    "total_item_cost",
    "is_open_po",
    "processed_po_value",
    "missing_expected_delivery_flag",
    "delayed_po_flag",
    "receipt_subtotal",
    "receipt_total",
    "return_qty",
    "return_value",
    "return_source_available",
    "eligible_closed_line_flag",
    "on_time_flag",
    "in_full_flag",
    "otif_success_flag",
    "lead_time_deviation_days",
    "current_unit_price",
    "previous_unit_price",
    "unit_price_change",
    "unit_price_change_percent",
    "absolute_unit_price_change_percent",
}

BOOLEAN_FIELDS = {
    "is_open_po",
    "missing_expected_delivery_flag",
    "delayed_po_flag",
    "return_source_available",
    "eligible_closed_line_flag",
    "on_time_flag",
    "in_full_flag",
    "otif_success_flag",
}


def read_rows(name: str) -> list[dict[str, str]]:
    with (TRUTH / name).open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_normalized(name: str) -> list[dict[str, str]]:
    with (NORMALIZED / name).open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        return list(csv.DictReader(handle))


def coerce(field: str, value: str) -> Any:
    clean = value.strip()
    if not clean:
        return None
    if field in BOOLEAN_FIELDS:
        return clean.casefold() in {"1", "true", "yes"}
    if field in NUMERIC_FIELDS:
        try:
            return float(clean)
        except ValueError:
            return None
    return clean


def select(row: dict[str, str], fields: tuple[str, ...]) -> dict[str, Any]:
    return {field: coerce(field, row.get(field, "")) for field in fields}


def with_outlet(row: dict[str, Any]) -> dict[str, Any]:
    outlet = OUTLETS.get(str(row.get("outlet_code") or ""), {})
    return {**outlet, **row}


INVENTORY_FIELDS = (
    "source_period_code",
    "snapshot_date",
    "outlet_code",
    "outlet_name",
    "item_code",
    "item_name",
    "category_name",
    "super_category_name",
    "canonical_uom",
    "average_unit_cost",
    "current_stock_qty",
    "closing_value",
    "forecast_required_qty",
    "required_qty_with_safety",
    "valid_open_po_qty",
    "valid_open_po_count",
    "open_po_value",
    "shortage_qty",
    "days_cover",
    "risk_severity",
    "risk_severity_rank",
    "risk_type",
    "shortage_cost_value",
    "total_risk_value",
    "action_id",
    "recommended_action",
    "action_owner",
    "due_band",
)

MENU_FIELDS = (
    "source_period_code",
    "outlet_code",
    "outlet_name",
    "ingredient_code",
    "ingredient_name",
    "risk_severity",
    "shortage_qty",
    "menu_item_code",
    "menu_item_name",
    "forecast_menu_qty",
    "forecast_net_sales_at_risk",
    "risk_ingredient_count",
    "allocated_forecast_net_sales_at_risk",
)

EXPIRY_FIELDS = (
    "source_period_code",
    "as_of_date",
    "outlet_code",
    "outlet_name",
    "region",
    "city",
    "market_area",
    "latitude",
    "longitude",
    "batch_allocation_id",
    "batch_number",
    "receipt_date",
    "grn_number",
    "po_number",
    "vendor_name",
    "receipt_source_status",
    "item_code",
    "item_name",
    "category_name",
    "unit",
    "available_qty",
    "received_qty",
    "batch_remaining_qty",
    "item_closing_qty",
    "qty_at_risk",
    "average_unit_cost",
    "shelf_life_days_assumption",
    "estimated_fifo_tranche_qty",
    "daily_theoretical_demand",
    "expected_consumption_before_expiry",
    "estimated_expiry_date",
    "days_to_expiry",
    "expiry_risk_value",
    "risk_status",
    "is_estimated",
    "estimation_method",
    "source_evidence",
    "production_use_status",
)

PO_FIELDS = (
    "source_period_code",
    "source_period_start",
    "source_period_end",
    "outlet_code",
    "outlet_name",
    "vendor_name",
    "po_number",
    "po_date",
    "expected_delivery_date",
    "po_close_or_partial_receive_date",
    "po_status",
    "item_code",
    "item_name",
    "category_name",
    "super_category_name",
    "processed_qty",
    "remaining_balance_qty",
    "ordered_qty",
    "unit",
    "unit_price",
    "subtotal",
    "new_subtotal",
    "tax_amt",
    "total_item_cost",
    "is_open_po",
    "open_po_value",
    "processed_po_value",
    "missing_expected_delivery_flag",
    "delayed_po_flag",
    "receipt_date",
    "received_qty",
    "receipt_subtotal",
    "receipt_total",
    "eligible_closed_line_flag",
    "on_time_flag",
    "in_full_flag",
    "otif_success_flag",
    "lead_time_deviation_days",
)


def build_price_movement(po_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    weighted: dict[tuple[str, str, str, str, str], dict[str, Any]] = defaultdict(
        lambda: {"value": 0.0, "qty": 0.0, "price_as_of_date": ""}
    )
    labels: dict[tuple[str, str, str, str, str], dict[str, Any]] = {}
    for row in po_rows:
        if not row.get("receipt_date"):
            continue
        key = (
            str(row["source_period_code"]),
            str(row["outlet_code"]),
            str(row["vendor_name"]),
            str(row["item_code"]),
            str(row["canonical_uom"]),
        )
        weighted[key]["value"] += float(row.get("receipt_subtotal") or 0)
        weighted[key]["qty"] += float(row.get("received_qty") or 0)
        weighted[key]["price_as_of_date"] = max(
            str(weighted[key]["price_as_of_date"]),
            str(row.get("receipt_date") or ""),
        )
        labels[key] = row

    order = {"month_01": None, "month_02": "month_01", "month_03": "month_02"}
    result: list[dict[str, Any]] = []
    for key, totals in weighted.items():
        period, outlet, vendor, item, unit = key
        previous_period = order.get(period)
        if not totals["qty"]:
            continue
        previous = (
            weighted.get((previous_period, outlet, vendor, item, unit))
            if previous_period
            else None
        )
        current_price = totals["value"] / totals["qty"]
        previous_price = (
            previous["value"] / previous["qty"]
            if previous and previous["qty"]
            else None
        )
        change = (
            current_price - previous_price
            if previous_price is not None
            else None
        )
        change_percent = (
            change / previous_price * 100
            if change is not None and previous_price
            else None
        )
        label = labels[key]
        result.append(
            {
                "source_period_code": period,
                "price_as_of_date": totals["price_as_of_date"],
                "outlet_code": outlet,
                "outlet_name": label.get("outlet_name"),
                "vendor_name": vendor,
                "item_code": item,
                "item_name": label.get("item_name"),
                "category_name": label.get("category_name"),
                "canonical_uom": unit,
                "current_purchase_qty": round(float(totals["qty"]), 6),
                "current_purchase_value": round(float(totals["value"]), 2),
                "current_unit_price": round(current_price, 6),
                "previous_unit_price": (
                    round(previous_price, 6)
                    if previous_price is not None
                    else None
                ),
                "price_change_amount": (
                    round(change, 6)
                    if change is not None
                    else None
                ),
                "unit_price_change": (
                    round(change, 6)
                    if change is not None
                    else None
                ),
                "price_change_percent": (
                    round(change_percent, 6)
                    if change_percent is not None
                    else None
                ),
                "unit_price_change_percent": (
                    round(change_percent, 6)
                    if change_percent is not None
                    else None
                ),
                "absolute_price_change_percent": (
                    round(abs(change_percent), 6)
                    if change_percent is not None
                    else None
                ),
                "absolute_unit_price_change_percent": (
                    round(abs(change_percent), 6)
                    if change_percent is not None
                    else None
                ),
                "price_change_value_impact": (
                    round(change * float(totals["qty"]), 2)
                    if change is not None
                    else None
                ),
                "price_movement_direction": (
                    "NO_BASELINE"
                    if change is None
                    else "INCREASE"
                    if change > 0
                    else "DECREASE"
                    if change < 0
                    else "NO_CHANGE"
                ),
            }
        )
    return sorted(
        result,
        key=lambda row: (
            str(row["source_period_code"]),
            -float(row["absolute_unit_price_change_percent"] or 0),
        ),
    )


def main() -> None:
    inventory = [
        with_outlet(select(row, INVENTORY_FIELDS))
        for row in read_rows("PAGE1_Inventory_Risk_Detail.csv")
    ]
    inventory_index = {
        (
            row["source_period_code"],
            row["outlet_code"],
            row["item_code"],
        ): row
        for row in inventory
    }

    menu = []
    for source in read_rows("PAGE1_Menu_Impact_Detail.csv"):
        row = with_outlet(select(source, MENU_FIELDS))
        inventory_row = inventory_index.get(
            (
                row["source_period_code"],
                row["outlet_code"],
                row["ingredient_code"],
            ),
            {},
        )
        row["snapshot_date"] = inventory_row.get("snapshot_date")
        row["category_name"] = inventory_row.get("category_name")
        row["super_category_name"] = inventory_row.get("super_category_name")
        menu.append(row)

    expiry = []
    for source in read_rows("PAGE1_Expiry_Risk_Detail.csv"):
        row = with_outlet(select(source, EXPIRY_FIELDS))
        status = str(row.pop("risk_status") or "")
        unit = row.pop("unit")
        qty_at_risk = row.pop("qty_at_risk")
        if status in {"EXPIRED", "EXPIRES_TODAY"}:
            severity = "PURPLE"
            severity_rank = 4
        elif status == "CRITICAL":
            severity = "RED"
            severity_rank = 3
        else:
            severity = "AMBER"
            severity_rank = 2
        if status == "EXPIRED":
            recommendation = "Quarantine expired batch and investigate"
        elif status in {"EXPIRES_TODAY", "CRITICAL"}:
            recommendation = "Transfer, promote, or consume near-expiry stock"
        else:
            recommendation = "Review FIFO rotation and demand plan"
        expiry.append(
            {
                **row,
                "canonical_uom": unit,
                "expiry_qty_at_risk": qty_at_risk,
                "expiry_batch_risk_status": status,
                "risk_type": "EXPIRY",
                "risk_severity": severity,
                "risk_severity_rank": severity_rank,
                "action_id": row.get("batch_allocation_id"),
                "recommended_action": recommendation,
                "action_owner": "Operations",
                "due_band": (
                    "Due today"
                    if status in {"EXPIRED", "EXPIRES_TODAY", "CRITICAL"}
                    else "Due in 3 days"
                ),
            }
        )
    po_rows = [
        with_outlet(select(row, PO_FIELDS))
        for row in read_rows("PAGE2_Vendor_Performance_Detail.csv")
    ]
    receipts = []
    for source in read_normalized("RAWN_CT_enterprise_entry.csv"):
        receipts.append(
            with_outlet(
                {
                    "source_period_code": source["source_period_code"],
                    "outlet_code": source["source_outlet_code"],
                    "outlet_name": source["deployment_name"],
                    "store_kitchen_name": source["store_kitchen_name"],
                    "vendor_name": source["vendor_name"],
                    "po_number": source["po_number"],
                    "grn_number": source["transaction_number"],
                    "invoice_number": source["invoice_number"],
                    "receipt_date": source["entry_date"],
                    "invoice_date": source["invoice_date"],
                    "item_code": source["item_code"],
                    "item_name": source["item_name"],
                    "category_name": source["category_name"],
                    "super_category_name": source["super_category_name"],
                    "received_qty": coerce("received_qty", source["entry_qty"]),
                    "canonical_uom": source["unit"],
                    "unit_price": coerce("unit_price", source["unit_price"]),
                    "receipt_subtotal": coerce(
                        "receipt_subtotal",
                        source["base_amt"],
                    ),
                    "discount_value": coerce(
                        "discount_value",
                        source["discount_amt"],
                    ),
                    "tax_value": coerce("tax_value", source["total_tax_amt"]),
                    "receipt_total": coerce(
                        "receipt_total",
                        source["total_amt"],
                    ),
                }
            )
        )

    risky_keys = {
        (
            row["source_period_code"],
            row["outlet_code"],
            row["item_code"],
        ): row
        for row in inventory
        if row.get("risk_severity") != "GREEN"
    }
    risky_po = []
    for row in po_rows:
        key = (
            row["source_period_code"],
            row["outlet_code"],
            row["item_code"],
        )
        risk = risky_keys.get(key)
        if row.get("is_open_po") and risk:
            risky_po.append({**row, "risk_severity": risk["risk_severity"]})

    payload = {
        "schema": "abnah-control-tower-portal-data/v1",
        "generatedAt": "2026-07-27T00:00:00+05:30",
        "source": "synthetic_validation_truth",
        "dataBoundary": (
            "Synthetic three-outlet validation data only. No screenshots or "
            "operational POS rows are included."
        ),
        "defaultRange": {"start": "2026-03-01", "end": "2026-03-31"},
        "outlets": [
            {
                "outlet_code": code,
                **details,
            }
            for code, details in OUTLETS.items()
        ],
        "pages": {
            "p1": {
                "inventoryRisk": inventory,
                "menuImpact": menu,
                "expiryRisk": expiry,
                "riskyPo": risky_po,
            },
            "p2": {
                "purchaseOrders": po_rows,
                "poReceiptLines": po_rows,
                "purchaseReceipts": receipts,
                "priceMovement": build_price_movement(receipts),
            },
        },
    }
    encoded = json.dumps(payload, ensure_ascii=True, separators=(",", ":"))
    for output in OUTPUTS:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(encoded, encoding="utf-8")
    print(
        "Built portal demo data:",
        len(inventory),
        "inventory rows,",
        len(menu),
        "menu rows,",
        len(expiry),
        "expiry rows,",
        len(po_rows),
        "PO rows.",
    )


if __name__ == "__main__":
    main()
