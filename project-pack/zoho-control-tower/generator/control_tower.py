from __future__ import annotations

import csv
import hashlib
import json
import shutil
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

from generator.config import DATA_DIR, EXPORT_DIR, MONTHS, ROOT_DIR, clean_money, clean_qty
from generator.outlets import OUTLETS


CONTROL_TOWER_DATA_DIR = DATA_DIR / "control_tower"
CONTROL_TOWER_EXPORT_DIR = EXPORT_DIR.parent / "control_tower_zoho"
CONTRACT_DIR = ROOT_DIR / "local_data_auditor" / "contracts"
VALIDATION_DOC = ROOT_DIR / "docs" / "control_tower_synthetic_validation.md"

OUTLET_BY_NAME = {row["outlet_name"]: row for row in OUTLETS}
OUTLET_BY_CODE = {row["outlet_code"]: row for row in OUTLETS}

CONTRACT_STEMS = [
    "vendor_report",
    "bill_item_detail",
    "bulk_return",
    "closing_stock",
    "enterprise_consumption_detail",
    "enterprise_entry",
    "enterprise_opening",
    "enterprise_physical",
    "enterprise_purchase_order",
    "enterprise_reorder",
    "enterprise_stock_return",
    "enterprise_transfer_from",
    "enterprise_transfer_to",
    "enterprise_variance_master",
    "enterprise_variance_normal",
    "enterprise_wastage_normal",
    "gross_net_margin",
    "item_recipe_report",
    "purchase_detail",
    "recipe_consumption",
    "stock_in_stock_out",
]

STATIC_CONTRACTS = {"item_recipe_report", "vendor_report"}
LATEST_SNAPSHOT_CONTRACTS = {"enterprise_reorder"}

OBSERVED_HEADER_ONLY_REPORTS = {
    "enterprise_reorder",
    "enterprise_stock_return",
}

ACTIVE_V2_REPORT_STEMS = {
    "vendor_report",
    "closing_stock",
    "enterprise_entry",
    "enterprise_purchase_order",
    "enterprise_transfer_from",
    "enterprise_transfer_to",
    "enterprise_variance_normal",
    "enterprise_wastage_normal",
    "gross_net_margin",
    "item_recipe_report",
}

ACTIVE_V2_MODEL_OUTPUTS = {
    "AUX_Expiry_Estimate",
    "AUX_Menu_Demand_Forecast",
    "AUX_Outlet_Master",
    "AUX_Theoretical_Consumption",
}

OBSERVED_ALL_BLANK_FIELDS = {
    "bill_item_detail": {
        "customer_name",
        "customer_mobile",
        "covers",
        "order_id",
        "waiter_name",
        "source",
    },
    "bulk_return": {"comment", "source"},
    "enterprise_entry": {
        "batch_number",
        "cess_rate",
        "cess_value",
        "comment",
        "item_brand",
        "other_tax_rate",
        "other_tax_value",
        "pr_number",
        "source",
    },
    "enterprise_opening": {"comment", "source"},
    "enterprise_physical": {"item_brand", "source"},
    "enterprise_purchase_order": {
        "comment",
        "item_brand",
        "pr_deployment",
        "pr_number",
    },
    "enterprise_transfer_from": {
        "comment",
        "receiver_store_kitchen_name",
        "source",
        "supplier_store_kitchen_code",
    },
    "enterprise_transfer_to": {"comment", "source"},
    "enterprise_wastage_normal": {"source"},
    "purchase_detail": {"batch_number", "company_name", "po_comment"},
    "recipe_consumption": {
        "parent_item_qty",
        "parent_subtotal",
        "parent_unit_price",
    },
}

OBSERVED_ALL_ZERO_FIELDS = {
    "enterprise_consumption_detail": {
        "indent_dispatch_qty",
        "indent_dispatch_amt",
        "internal_indent_receive_qty",
        "internal_indent_receive_amt",
        "internal_indent_dispatch_qty",
        "internal_indent_dispatch_amt",
        "source_yield_wastage_qty",
        "source_yield_wastage_amt",
        "reuse_qty",
        "reuse_amt",
    },
    "enterprise_entry": {"mrp", "item_charges_amt"},
    "enterprise_opening": {"unit_price", "opening_subtotal"},
    "enterprise_purchase_order": {"item_discount_amt", "bill_discount_amt"},
    "enterprise_variance_master": {
        "purchase_qty",
        "purchase_amt",
        "production_qty",
        "production_amt",
        "stock_out_qty",
        "stock_out_amt",
        "reuse_qty",
        "reuse_amt",
        "return_qty",
        "return_amt",
    },
    "enterprise_variance_normal": {
        "source_yield_wastage_qty",
        "source_yield_wastage_amt",
        "reuse_qty",
        "reuse_amt",
    },
    "purchase_detail": {"other_tax_amt"},
}

OUTLET_COORDINATES = {
    "OUT001": {
        "region": "North",
        "city": "Delhi",
        "latitude": 28.6315,
        "longitude": 77.2167,
        "new_matured_flag": "Matured",
    },
    "OUT002": {
        "region": "North",
        "city": "Delhi",
        "latitude": 28.5494,
        "longitude": 77.2001,
        "new_matured_flag": "Matured",
    },
    "OUT003": {
        "region": "North",
        "city": "Delhi",
        "latitude": 28.5245,
        "longitude": 77.2066,
        "new_matured_flag": "New",
    },
}

SHELF_LIFE_DAYS = {
    "Dairy": 7,
    "Dairy Alternative": 12,
    "Protein": 5,
    "Produce": 5,
    "Bakery": 4,
    "Dessert Inputs": 10,
    "Fruit Inputs": 10,
    "Beverage Inputs": 30,
    "Coffee Inputs": 120,
    "Tea Inputs": 180,
    "Syrups & Sauces": 90,
    "Packaging": 365,
}

STORAGE_TYPE = {
    "Dairy": "Chilled",
    "Dairy Alternative": "Chilled",
    "Protein": "Chilled",
    "Produce": "Chilled",
    "Fruit Inputs": "Frozen",
    "Dessert Inputs": "Frozen",
    "Bakery": "Ambient",
    "Coffee Inputs": "Ambient",
    "Tea Inputs": "Ambient",
    "Syrups & Sauces": "Ambient",
    "Beverage Inputs": "Ambient",
    "Packaging": "Ambient",
}

VENDOR_DELAY_DAYS = {
    "BeanCraft Roasters Delhi": 0,
    "FreshDairy Foods NCR": 1,
    "Delhi Bakery Supply Co": 0,
    "PackPro Disposables": 0,
    "GreenLeaf Produce Delhi": 2,
    "SpiceRoot Foods": 1,
    "NorthStar Poultry": 1,
    "ChocoCraft Ingredients": 0,
    "FrozenBerry Traders": 1,
    "Metro Wholesale Delhi": 0,
    "TeaLeaf Traders NCR": 0,
    "SweetBase Foods": 1,
}


@dataclass(frozen=True)
class Contract:
    stem: str
    report_id: str
    display_name: str
    grain: str
    expected_header: list[str]
    row_columns: list[str]


def _stable_int(*parts: Any) -> int:
    text = "|".join(str(part) for part in parts)
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:12], 16)


def _choice(values: list[str], *parts: Any) -> str:
    return values[_stable_int(*parts) % len(values)]


def _month_code(value: date | datetime | str) -> str:
    day = pd.to_datetime(value).date()
    for code, (start, end) in MONTHS.items():
        if start <= day <= end:
            return code
    raise ValueError(f"Date {day} is outside the configured three-month demo range.")


def _month_number(code: str) -> int:
    return int(code.split("_")[-1])


def _month_end(code: str) -> date:
    return MONTHS[code][1]


def _load_contract(stem: str) -> Contract:
    payload = json.loads((CONTRACT_DIR / f"{stem}.json").read_text(encoding="utf-8"))
    return Contract(
        stem=stem,
        report_id=payload["report_id"],
        display_name=payload["display_name"],
        grain=payload["grain"],
        expected_header=list(payload["expected_header"]),
        row_columns=[column["name"] for column in payload["row_columns"]],
    )


def _contracts() -> dict[str, Contract]:
    return {stem: _load_contract(stem) for stem in CONTRACT_STEMS}


def _outlet_meta(outlet_name: str) -> tuple[str, str, str]:
    outlet = OUTLET_BY_NAME[outlet_name]
    return outlet["outlet_code"], outlet["outlet_name"], outlet["market_area"]


def _normal_bom(bom: pd.DataFrame) -> pd.DataFrame:
    result = bom.copy()
    result["recipe_name"] = result["recipe_name"].replace("", pd.NA).ffill()
    return result


def _money(value: Any) -> float:
    return clean_money(0 if pd.isna(value) else float(value))


def _qty(value: Any) -> float:
    return clean_qty(0 if pd.isna(value) else float(value))


def _frame(rows: list[dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def _write_contract_csv(frame: pd.DataFrame, contract: Contract, path: Path) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    missing = [column for column in contract.row_columns if column not in frame.columns]
    if missing and not frame.empty:
        raise ValueError(f"{contract.stem} is missing canonical columns: {missing}")

    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(contract.expected_header)
        if not frame.empty:
            for row in frame.to_dict(orient="records"):
                values = [row.get(column, "") for column in contract.row_columns]
                if len(contract.expected_header) > len(values):
                    values.extend([""] * (len(contract.expected_header) - len(values)))
                writer.writerow(values)
    return len(frame)


def _clear_generated_outputs() -> None:
    for path in (CONTROL_TOWER_DATA_DIR, CONTROL_TOWER_EXPORT_DIR):
        resolved = path.resolve()
        allowed_roots = {DATA_DIR.resolve(), EXPORT_DIR.parent.resolve()}
        if not any(root == resolved or root in resolved.parents for root in allowed_roots):
            raise RuntimeError(f"Refusing to clear unexpected output path: {resolved}")
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True, exist_ok=True)


def _apply_observed_source_shape(
    report_frames: dict[str, pd.DataFrame],
) -> dict[str, pd.DataFrame]:
    """Mirror confirmed UAT blank, zero-only, and header-only source behavior."""
    shaped: dict[str, pd.DataFrame] = {}
    for stem, source in report_frames.items():
        frame = source.copy()
        for column in OBSERVED_ALL_BLANK_FIELDS.get(stem, set()):
            if column in frame.columns:
                frame[column] = ""
        for column in OBSERVED_ALL_ZERO_FIELDS.get(stem, set()):
            if column in frame.columns:
                frame[column] = 0

        if stem == "enterprise_entry" and not frame.empty:
            frame["total_amt"] = (
                pd.to_numeric(frame["base_amt"], errors="coerce").fillna(0)
                - pd.to_numeric(frame["discount_amt"], errors="coerce").fillna(0)
                + pd.to_numeric(frame["total_tax_amt"], errors="coerce").fillna(0)
                + pd.to_numeric(frame["item_charges_amt"], errors="coerce").fillna(0)
            ).round(2)

        if stem == "purchase_detail" and not frame.empty:
            frame["total_amt"] = (
                pd.to_numeric(frame["purchase_amount"], errors="coerce").fillna(0)
                - pd.to_numeric(frame["discount_amt"], errors="coerce").fillna(0)
                + pd.to_numeric(frame["cgst_tax_amt"], errors="coerce").fillna(0)
                + pd.to_numeric(frame["sgst_tax_amt"], errors="coerce").fillna(0)
                + pd.to_numeric(frame["igst_tax_amt"], errors="coerce").fillna(0)
                + pd.to_numeric(frame["other_tax_amt"], errors="coerce").fillna(0)
            ).round(2)

        if stem == "enterprise_purchase_order" and not frame.empty:
            previous_net = pd.to_numeric(
                frame["new_subtotal"], errors="coerce"
            ).replace(0, np.nan)
            tax_rate = (
                pd.to_numeric(frame["tax_amt"], errors="coerce") / previous_net
            ).fillna(0)
            frame["new_subtotal"] = pd.to_numeric(
                frame["subtotal"], errors="coerce"
            ).fillna(0)
            frame["tax_amt"] = (frame["new_subtotal"] * tax_rate).round(2)
            frame["total_item_cost"] = (
                frame["new_subtotal"] + frame["tax_amt"]
            ).round(2)

        if stem in OBSERVED_HEADER_ONLY_REPORTS:
            frame = frame.iloc[0:0].copy()
        shaped[stem] = frame
    return shaped


def _ingredient_cost_map(bom: pd.DataFrame, ingredients: pd.DataFrame) -> dict[str, float]:
    normalized = _normal_bom(bom)
    prices = ingredients.set_index("item_name")["average_price"].to_dict()
    normalized["ingredient_cost"] = normalized.apply(
        lambda row: float(row["item_qty"]) * float(prices.get(row["item_name"], 0)),
        axis=1,
    )
    return normalized.groupby("recipe_name")["ingredient_cost"].sum().to_dict()


def _build_sales_reports(
    sales: pd.DataFrame,
    menu: pd.DataFrame,
    bom: pd.DataFrame,
    ingredients: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    menu_by_number = menu.set_index("item_number").to_dict(orient="index")
    recipe_cost = _ingredient_cost_map(bom, ingredients)
    daily_counter: defaultdict[tuple[str, str], int] = defaultdict(int)
    bill_rows: list[dict[str, Any]] = []
    margin_rows: list[dict[str, Any]] = []

    source_options = {
        "OUT001": ["Dine In", "Takeaway", "Corporate Order"],
        "OUT002": ["Dine In", "Online", "Takeaway"],
        "OUT003": ["Dine In", "Online", "Mall Walk-in"],
    }
    waiter_options = {
        "OUT001": ["Aarav", "Meera", "Kabir"],
        "OUT002": ["Riya", "Vivaan", "Ishaan"],
        "OUT003": ["Anaya", "Arjun", "Diya"],
    }

    ordered = sales.sort_values(["date", "outlet_name", "item_number"]).reset_index(drop=True)
    for _, row in ordered.iterrows():
        sales_date = pd.to_datetime(row["date"]).date()
        outlet_code, outlet_name, _ = _outlet_meta(row["outlet_name"])
        counter_key = (outlet_code, sales_date.isoformat())
        daily_counter[counter_key] += 1
        line_number = daily_counter[counter_key]
        meta = menu_by_number.get(row["item_number"], {})
        item_qty = float(row["qty"])
        net_sale = _money(row["net_sale"])
        base_rate = float(meta.get("rate", net_sale / max(item_qty, 1)))
        item_rate = _money(max(base_rate, net_sale / max(item_qty, 1)))
        item_subtotal = _money(item_rate * item_qty)
        discount = _money(max(0, item_subtotal - net_sale))
        gst_rate = 5.0
        gst_amt = _money(net_sale * gst_rate / 100)
        gross_sale = _money(net_sale + gst_amt)
        item_cost_rate = _money(recipe_cost.get(row["item_name"], 0))
        purchase_value = _money(item_cost_rate * item_qty)
        net_margin = round((net_sale - purchase_value) / net_sale * 100, 2) if net_sale else 0
        gross_margin = round((gross_sale - purchase_value) / gross_sale * 100, 2) if gross_sale else 0
        open_minute = 8 * 60 + (_stable_int(row["row_id"], "open") % (12 * 60))
        close_minute = open_minute + 8 + (_stable_int(row["row_id"], "duration") % 42)
        open_time = f"{open_minute // 60:02d}:{open_minute % 60:02d}:00"
        close_time = f"{close_minute // 60:02d}:{close_minute % 60:02d}:00"
        source = _choice(source_options[outlet_code], row["row_id"], "source")
        tab_type = "Dine In" if source == "Dine In" else "Delivery/Takeaway"
        bill_number = f"BILL-{outlet_code}-{sales_date:%y%m%d}-{line_number:04d}"
        order_id = f"ORD-{outlet_code}-{sales_date:%y%m%d}-{line_number:04d}"
        has_customer = _stable_int(row["row_id"], "customer") % 6 == 0
        customer_seq = _stable_int(row["row_id"], "customer-seq") % 9000
        customer_name = f"Guest {customer_seq:04d}" if has_customer else ""
        customer_mobile = f"90000{customer_seq:05d}" if has_customer else ""
        waiter = _choice(waiter_options[outlet_code], row["row_id"], "waiter")
        month_code = _month_code(sales_date)
        common_meta = {
            "_month_code": month_code,
            "_outlet_code": outlet_code,
            "_outlet_name": outlet_name,
        }

        bill_rows.append(
            {
                **common_meta,
                "bill_state": "Delhi",
                "deployment_name": outlet_name,
                "order_id": order_id,
                "bill_number": bill_number,
                "day_serial": line_number,
                "tab_name": tab_type,
                "table_number": f"T{1 + _stable_int(row['row_id'], 'table') % 24:02d}" if source == "Dine In" else "",
                "open_time": f"{sales_date:%Y-%m-%d} {open_time}",
                "close_time": f"{sales_date:%Y-%m-%d} {close_time}",
                "category_name": row["category"],
                "item_name": row["item_name"],
                "item_number": row["item_number"],
                "item_section": row["super_category"],
                "item_classification": "Menu Item",
                "item_rate": item_rate,
                "item_qty": item_qty,
                "line_amt": item_subtotal,
                "discount_amt": discount,
                "discount_type": "Bill Discount" if discount else "",
                "discount_remarks": "Synthetic promotion" if discount else "",
                "gst_5_taxable_amt": net_sale,
                "gst_5_tax_amt": gst_amt,
                "gst_18_taxable_amt": 0,
                "gst_18_tax_amt": 0,
                "gst_3_taxable_amt": 0,
                "gst_3_tax_amt": 0,
                "net_amt": gross_sale,
                "customer_name": customer_name,
                "customer_mobile": customer_mobile,
                "covers": 1 + _stable_int(row["row_id"], "covers") % 4,
                "waiter_name": waiter,
                "source": source,
            }
        )

        margin_rows.append(
            {
                **common_meta,
                "store_name": outlet_name,
                "sale_date": sales_date.isoformat(),
                "bill_number": bill_number,
                "tab_type": tab_type,
                "source": source,
                "customer_name": customer_name,
                "customer_number": customer_mobile,
                "super_category_name": row["super_category"],
                "category_name": row["category"],
                "sac_hsn_number": "996331",
                "item_code": row["item_number"],
                "item_name": row["item_name"],
                "item_rate": item_rate,
                "item_qty": item_qty,
                "item_subtotal": item_subtotal,
                "offer_name": "Synthetic promotion" if discount else "",
                "discount_amt": discount,
                "complimentary_amt": 0,
                "total_discount_amt": discount,
                "net_sale_value": net_sale,
                "tax_amt": gst_amt,
                "gross_sale_value": gross_sale,
                "purchase_rate": item_cost_rate,
                "purchase_value": purchase_value,
                "net_margin_percent": net_margin,
                "gross_margin_percent": gross_margin,
            }
        )

    return _frame(bill_rows), _frame(margin_rows)


def _build_item_recipe(
    bom: pd.DataFrame,
    menu: pd.DataFrame,
    ingredients: pd.DataFrame,
) -> pd.DataFrame:
    normalized = _normal_bom(bom)
    menu_meta = menu.set_index("item_name").to_dict(orient="index")
    ingredient_meta = ingredients.set_index("item_name").to_dict(orient="index")
    rows = []
    for _, row in normalized.iterrows():
        menu_row = menu_meta[row["recipe_name"]]
        ingredient_row = ingredient_meta[row["item_name"]]
        rows.append(
            {
                "menu_item_type": menu_row["super_category_name"],
                "menu_item_number": menu_row["item_number"],
                "menu_item_name": row["recipe_name"],
                "recipe_item_type": ingredient_row["super_category_name"],
                "recipe_qty_per_menu_unit": _qty(row["item_qty"]),
                "recipe_unit": row["item_unit"],
                "ingredient_code": ingredient_row["item_code"],
                "ingredient_name": row["item_name"],
            }
        )
    return _frame(rows)


def _price_multiplier(month_code: str, category: str) -> float:
    month = _month_number(month_code)
    if month == 1:
        return 1.0
    if month == 2:
        return {
            "Dairy": 1.02,
            "Coffee Inputs": 1.015,
            "Produce": 0.98,
            "Protein": 1.01,
            "Packaging": 1.005,
        }.get(category, 1.01)
    return {
        "Dairy": 1.045,
        "Coffee Inputs": 1.03,
        "Produce": 1.06,
        "Protein": 1.035,
        "Packaging": 1.015,
        "Bakery": 1.025,
    }.get(category, 1.02)


def _build_purchase_order(purchase: pd.DataFrame, ingredients: pd.DataFrame) -> pd.DataFrame:
    ingredient_meta = ingredients.set_index("item_code").to_dict(orient="index")
    rows = []
    ordered = purchase.sort_values(["po_date", "deployment", "po_number", "item_code"]).reset_index(drop=True)
    missing_expected_assigned: set[str] = set()
    for idx, row in ordered.iterrows():
        po_date = pd.to_datetime(row["po_date"]).date()
        month_code = _month_code(po_date)
        outlet_code, outlet_name, _ = _outlet_meta(row["deployment"])
        ingredient = ingredient_meta[row["item_code"]]
        unit_price = _money(float(row["unit_price"]) * _price_multiplier(month_code, row["category_name"]))
        ordered_qty = _qty(row["quantity"])
        processed_qty = _qty(row["total_processed_qty"])
        remaining_qty = _qty(row["remaining_balance_qty"])
        subtotal = _money(ordered_qty * unit_price)
        item_discount = _money(subtotal * (0.01 if _stable_int(row["row_id"], "item-discount") % 17 == 0 else 0))
        bill_discount = _money(subtotal * (0.005 if _stable_int(row["row_id"], "bill-discount") % 23 == 0 else 0))
        new_subtotal = _money(subtotal - item_discount - bill_discount)
        tax_amt = _money(new_subtotal * float(ingredient["gst_rate"]) / 100)
        total_item_cost = _money(new_subtotal + tax_amt)
        expected = pd.to_datetime(row["expected_delivery"]).date()
        status = str(row["po_status"])
        delay = VENDOR_DELAY_DAYS.get(row["vendor_name"], 0)
        jitter = (_stable_int(row["row_id"], "delivery") % 3) - 1
        actual_receipt = min(expected + timedelta(days=max(-1, delay + jitter)), MONTHS["month_03"][1])
        close_date = actual_receipt.isoformat() if status in {"Closed", "Partially Received"} else ""
        expected_text = expected.isoformat()
        if (
            month_code == "month_03"
            and status in {"Pending", "Partially Received"}
            and outlet_code not in missing_expected_assigned
        ):
            expected_text = ""
            missing_expected_assigned.add(outlet_code)
        rows.append(
            {
                "_month_code": month_code,
                "_outlet_code": outlet_code,
                "_outlet_name": outlet_name,
                "_purchase_row_id": row["row_id"],
                "_actual_receipt_date": actual_receipt.isoformat(),
                "deployment_name": outlet_name,
                "store_name": row["store_name"],
                "vendor_name": row["vendor_name"],
                "po_number": row["po_number"],
                "pr_number": f"PR-{po_date:%y%m}-{idx + 1:05d}",
                "pr_deployment": outlet_name,
                "po_date": po_date.isoformat(),
                "expected_delivery_date": expected_text,
                "po_close_or_partial_receive_date": close_date,
                "po_status": status,
                "item_code": row["item_code"],
                "item_name": row["item_name"],
                "item_brand": "ABNAH Approved",
                "category_name": row["category_name"],
                "super_category_name": row["super_category_name"],
                "comment": "Synthetic control-tower baseline",
                "processed_qty": processed_qty,
                "remaining_balance_qty": remaining_qty,
                "ordered_qty": ordered_qty,
                "unit": row["unit"],
                "unit_price": unit_price,
                "subtotal": subtotal,
                "item_discount_amt": item_discount,
                "bill_discount_amt": bill_discount,
                "new_subtotal": new_subtotal,
                "tax_amt": tax_amt,
                "total_item_cost": total_item_cost,
            }
        )
    return _frame(rows)


def _build_entry_and_returns(
    po: pd.DataFrame,
    ingredients: pd.DataFrame,
    vendors: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    ingredient_meta = ingredients.set_index("item_code").to_dict(orient="index")
    vendor_code = vendors.set_index("vendor_name")["vendor_code"].to_dict()
    entry_rows = []
    purchase_detail_rows = []
    stock_return_rows = []
    bulk_return_rows = []
    users = ["store.manager", "inventory.lead", "ops.cp", "ops.hk", "ops.saket"]

    usable = po[po["processed_qty"] > 0].reset_index(drop=True)
    for idx, row in usable.iterrows():
        receipt_date = pd.to_datetime(row["_actual_receipt_date"]).date()
        month_code = _month_code(receipt_date)
        ingredient = ingredient_meta[row["item_code"]]
        qty = _qty(row["processed_qty"])
        unit_price = _money(row["unit_price"])
        base_amt = _money(qty * unit_price)
        discount = _money(base_amt * (0.01 if _stable_int(row["_purchase_row_id"], "entry-discount") % 19 == 0 else 0))
        taxable = _money(base_amt - discount)
        gst_rate = float(ingredient["gst_rate"])
        gst_value = _money(taxable * gst_rate / 100)
        charges = _money(18 if _stable_int(row["_purchase_row_id"], "charges") % 13 == 0 else 0)
        total = _money(taxable + gst_value + charges)
        transaction_number = f"GRN-{row['_outlet_code']}-{receipt_date:%y%m%d}-{idx + 1:05d}"
        invoice_number = f"INV-{receipt_date:%y%m}-{idx + 1:05d}"
        batch_number = f"BATCH-{receipt_date:%y%m}-{row['item_code']}-{idx % 97:02d}"
        user = _choice(users, transaction_number)
        entry_rows.append(
            {
                "_month_code": month_code,
                "_outlet_code": row["_outlet_code"],
                "_outlet_name": row["_outlet_name"],
                "_actual_receipt_date": receipt_date.isoformat(),
                "deployment_name": row["deployment_name"],
                "store_kitchen_name": row["store_name"],
                "user_name": user,
                "vendor_name": row["vendor_name"],
                "entry_date": receipt_date.isoformat(),
                "transaction_number": transaction_number,
                "invoice_number": invoice_number,
                "batch_number": batch_number,
                "pr_number": row["pr_number"],
                "po_number": row["po_number"],
                "invoice_date": receipt_date.isoformat(),
                "item_code": row["item_code"],
                "item_name": row["item_name"],
                "item_brand": row["item_brand"],
                "category_name": row["category_name"],
                "super_category_name": row["super_category_name"],
                "comment": "PO-linked synthetic receipt",
                "entry_qty": qty,
                "unit": row["unit"],
                "mrp": _money(unit_price * 1.12),
                "unit_price": unit_price,
                "charges_name": "Freight" if charges else "",
                "base_amt": base_amt,
                "discount_amt": discount,
                "gst_igst_rate": gst_rate,
                "gst_igst_value": gst_value,
                "cess_rate": 0,
                "cess_value": 0,
                "other_tax_rate": 0,
                "other_tax_value": 0,
                "total_tax_amt": gst_value,
                "item_charges_amt": charges,
                "total_amt": total,
                "source": "Purchase Order",
            }
        )

        cgst = _money(gst_value / 2)
        sgst = _money(gst_value - cgst)
        purchase_detail_rows.append(
            {
                "_month_code": month_code,
                "_outlet_code": row["_outlet_code"],
                "_outlet_name": row["_outlet_name"],
                "item_code": row["item_code"],
                "item_name": row["item_name"],
                "company_name": "ABNAH Hospitality",
                "deployment_name": row["deployment_name"],
                "transaction_date": receipt_date.isoformat(),
                "invoice_date": receipt_date.isoformat(),
                "po_date": row["po_date"],
                "po_number": row["po_number"],
                "transaction_number": transaction_number,
                "vendor_code": vendor_code.get(row["vendor_name"], ""),
                "vendor_name": row["vendor_name"],
                "invoice_number": invoice_number,
                "batch_number": batch_number,
                "category_code": f"CAT-{ingredient['category_name'][:3].upper()}",
                "category_name": row["category_name"],
                "super_category_code": f"SUP-{ingredient['super_category_name'][:3].upper()}",
                "super_category_name": row["super_category_name"],
                "po_qty": row["ordered_qty"],
                "po_unit": row["unit"],
                "po_unit_price": row["unit_price"],
                "po_amount": row["new_subtotal"],
                "po_comment": row["comment"],
                "purchase_qty": qty,
                "purchase_unit": row["unit"],
                "purchase_unit_price": unit_price,
                "purchase_amount": base_amt,
                "discount_amt": discount,
                "cgst_tax_amt": cgst,
                "sgst_tax_amt": sgst,
                "igst_tax_amt": 0,
                "other_tax_amt": charges,
                "total_amt": total,
            }
        )

        should_return = idx % 17 == 0 or (
            row["category_name"] in {"Dairy", "Produce", "Protein"} and idx % 29 == 0
        )
        if should_return:
            return_qty = _qty(max(0.01, min(qty * 0.045, qty)))
            return_date = min(receipt_date + timedelta(days=1 + idx % 3), MONTHS["month_03"][1])
            return_subtotal = _money(return_qty * unit_price)
            return_discount = 0
            return_tax = _money(return_subtotal * gst_rate / 100)
            return_cgst = _money(return_tax / 2)
            return_sgst = _money(return_tax - return_cgst)
            return_amt = _money(return_subtotal + return_tax)
            stock_return_rows.append(
                {
                    "_month_code": _month_code(return_date),
                    "_outlet_code": row["_outlet_code"],
                    "_outlet_name": row["_outlet_name"],
                    "deployment_name": row["deployment_name"],
                    "store_name": row["store_name"],
                    "stock_entry_date": receipt_date.isoformat(),
                    "transaction_number": transaction_number,
                    "invoice_number": invoice_number,
                    "batch_number": batch_number,
                    "vendor_code": vendor_code.get(row["vendor_name"], ""),
                    "vendor_name": row["vendor_name"],
                    "super_category_code": f"SUP-{ingredient['super_category_name'][:3].upper()}",
                    "super_category_name": row["super_category_name"],
                    "category_code": f"CAT-{ingredient['category_name'][:3].upper()}",
                    "category_name": row["category_name"],
                    "item_code": row["item_code"],
                    "item_name": row["item_name"],
                    "comment": "Quality rejection from synthetic receipt",
                    "entry_unit": row["unit"],
                    "entry_qty": qty,
                    "unit_price": unit_price,
                    "entry_subtotal": base_amt,
                    "entry_discount_amt": discount,
                    "entry_cgst_amt": cgst,
                    "entry_sgst_amt": sgst,
                    "entry_igst_amt": 0,
                    "entry_non_gst_amt": charges,
                    "entry_amt": total,
                    "return_date": return_date.isoformat(),
                    "return_unit": row["unit"],
                    "return_qty": return_qty,
                    "return_subtotal": return_subtotal,
                    "return_discount_amt": return_discount,
                    "return_cgst_amt": return_cgst,
                    "return_sgst_amt": return_sgst,
                    "return_igst_amt": 0,
                    "return_non_gst_amt": 0,
                    "return_amt": return_amt,
                    "transaction_status": "Completed",
                }
            )

        if idx % 31 == 0:
            bulk_qty = _qty(max(0.01, qty * 0.025))
            bulk_date = min(receipt_date + timedelta(days=2), MONTHS["month_03"][1])
            bulk_return_rows.append(
                {
                    "_month_code": _month_code(bulk_date),
                    "_outlet_code": row["_outlet_code"],
                    "_outlet_name": row["_outlet_name"],
                    "deployment_name": row["deployment_name"],
                    "store_kitchen_name": row["store_name"],
                    "user_name": user,
                    "return_date": bulk_date.isoformat(),
                    "transaction_number": f"BRT-{row['_outlet_code']}-{bulk_date:%y%m%d}-{idx + 1:04d}",
                    "item_code": row["item_code"],
                    "item_name": row["item_name"],
                    "category_name": row["category_name"],
                    "super_category_name": row["super_category_name"],
                    "comment": "Excess stock returned to central supply",
                    "return_qty": bulk_qty,
                    "unit": row["unit"],
                    "source": "Bulk Return",
                }
            )

    return (
        _frame(entry_rows),
        _frame(purchase_detail_rows),
        _frame(stock_return_rows),
        _frame(bulk_return_rows),
    )


def _build_transfers(
    ingredients: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    ingredient_meta = ingredients.set_index("item_name").to_dict(orient="index")
    transfer_plan = [
        ("OUT001", "OUT002", "Milk", 12),
        ("OUT001", "OUT002", "Cold Cup", 140),
        ("OUT003", "OUT002", "Brownie Base", 18),
        ("OUT001", "OUT003", "Coffee Beans", 3),
        ("OUT002", "OUT001", "Wrap Packaging", 35),
        ("OUT003", "OUT001", "Cream", 5),
    ]
    from_rows = []
    to_rows = []
    movement_rows = []

    for month_code in MONTHS:
        month_no = _month_number(month_code)
        transfer_date = date(2026, month_no, 12 + month_no)
        for idx, (supplier_code, receiver_code, item_name, base_qty) in enumerate(transfer_plan, start=1):
            supplier = OUTLET_BY_CODE[supplier_code]
            receiver = OUTLET_BY_CODE[receiver_code]
            ingredient = ingredient_meta[item_name]
            qty = _qty(base_qty * (1 + (month_no - 1) * 0.08))
            price = _money(float(ingredient["average_price"]) * _price_multiplier(month_code, ingredient["category_name"]))
            amount = _money(qty * price)
            transaction = f"TRF-{month_no:02d}-{supplier_code}-{receiver_code}-{idx:03d}"
            common = {
                "_month_code": month_code,
                "_outlet_code": supplier_code,
                "_outlet_name": supplier["outlet_name"],
                "_supplier_code": supplier_code,
                "_receiver_code": receiver_code,
                "_supplier_outlet": supplier["outlet_name"],
                "_receiver_outlet": receiver["outlet_name"],
                "_item_code": ingredient["item_code"],
                "_transfer_qty": qty,
                "_unit_price": price,
            }
            from_rows.append(
                {
                    **common,
                    "deployment_name": supplier["outlet_name"],
                    "supplier_store_kitchen_code": f"{supplier_code}-MAIN",
                    "supplier_store_kitchen_name": f"{supplier['outlet_name']} Main Store",
                    "receiver_store_kitchen_code": f"{receiver_code}-MAIN",
                    "receiver_store_kitchen_name": f"{receiver['outlet_name']} Main Store",
                    "user_name": "inventory.lead",
                    "transfer_date": transfer_date.isoformat(),
                    "transaction_number": transaction,
                    "item_code": ingredient["item_code"],
                    "item_name": item_name,
                    "category_name": ingredient["category_name"],
                    "super_category_name": ingredient["super_category_name"],
                    "comment": "Cross-outlet balancing transfer",
                    "transfer_qty": qty,
                    "unit": ingredient["unit"],
                    "unit_price": price,
                    "transfer_amt": amount,
                    "source": "Internal Transfer",
                }
            )
            to_rows.append(
                {
                    **common,
                    "_outlet_code": receiver_code,
                    "_outlet_name": receiver["outlet_name"],
                    "deployment_name": receiver["outlet_name"],
                    "receiver_store_name": f"{receiver['outlet_name']} Main Store",
                    "supplier_store_name": f"{supplier['outlet_name']} Main Store",
                    "user_name": "inventory.lead",
                    "transfer_date": transfer_date.isoformat(),
                    "transaction_number": transaction,
                    "item_code": ingredient["item_code"],
                    "item_name": item_name,
                    "category_name": ingredient["category_name"],
                    "super_category_name": ingredient["super_category_name"],
                    "comment": "Cross-outlet balancing receipt",
                    "transfer_qty": qty,
                    "unit": ingredient["unit"],
                    "unit_price": price,
                    "transfer_amt": amount,
                    "source": "Internal Transfer",
                }
            )
            movement_rows.extend(
                [
                    {
                        "_month_code": month_code,
                        "_outlet_code": supplier_code,
                        "_outlet_name": supplier["outlet_name"],
                        "movement_date": transfer_date.isoformat(),
                        "store_kitchen_name": f"{supplier['outlet_name']} Main Store",
                        "supplier_name": supplier["outlet_name"],
                        "receiver_name": receiver["outlet_name"],
                        "item_name": item_name,
                        "unit": ingredient["unit"],
                        "unit_price": price,
                        "stock_in_reference": "",
                        "stock_in_qty": 0,
                        "stock_in_subtotal": 0,
                        "stock_out_reference": transaction,
                        "stock_out_qty": qty,
                        "stock_out_subtotal": amount,
                    },
                    {
                        "_month_code": month_code,
                        "_outlet_code": receiver_code,
                        "_outlet_name": receiver["outlet_name"],
                        "movement_date": transfer_date.isoformat(),
                        "store_kitchen_name": f"{receiver['outlet_name']} Main Store",
                        "supplier_name": supplier["outlet_name"],
                        "receiver_name": receiver["outlet_name"],
                        "item_name": item_name,
                        "unit": ingredient["unit"],
                        "unit_price": price,
                        "stock_in_reference": transaction,
                        "stock_in_qty": qty,
                        "stock_in_subtotal": amount,
                        "stock_out_reference": "",
                        "stock_out_qty": 0,
                        "stock_out_subtotal": 0,
                    },
                ]
            )
    return _frame(from_rows), _frame(to_rows), _frame(movement_rows)


def _theoretical_consumption(
    sales: pd.DataFrame,
    bom: pd.DataFrame,
    ingredients: pd.DataFrame,
) -> pd.DataFrame:
    normalized = _normal_bom(bom)
    ingredient_meta = ingredients[
        ["item_code", "item_name", "category_name", "super_category_name", "unit", "average_price"]
    ]
    merged = sales.merge(
        normalized[["recipe_name", "item_name", "item_qty", "item_unit"]],
        left_on="item_name",
        right_on="recipe_name",
        suffixes=("_menu", "_ingredient"),
    )
    merged["theoretical_qty"] = merged["qty"] * merged["item_qty"]
    merged["_month_code"] = merged["date"].map(_month_code)
    merged["_outlet_code"] = merged["outlet_name"].map(
        lambda value: OUTLET_BY_NAME[value]["outlet_code"]
    )
    grouped = (
        merged.groupby(
            ["_month_code", "_outlet_code", "outlet_name", "item_name_ingredient"],
            as_index=False,
        )["theoretical_qty"]
        .sum()
        .rename(columns={"item_name_ingredient": "item_name"})
    )
    return grouped.merge(ingredient_meta, on="item_name", how="left")


def _build_recipe_consumption(
    sales: pd.DataFrame,
    bom: pd.DataFrame,
    ingredients: pd.DataFrame,
) -> pd.DataFrame:
    normalized = _normal_bom(bom)
    ingredient_meta = ingredients.set_index("item_name").to_dict(orient="index")
    grouped_sales = sales.copy()
    grouped_sales["_month_code"] = grouped_sales["date"].map(_month_code)
    grouped_sales["_outlet_code"] = grouped_sales["outlet_name"].map(
        lambda value: OUTLET_BY_NAME[value]["outlet_code"]
    )
    grouped_sales = (
        grouped_sales.groupby(
            ["_month_code", "_outlet_code", "outlet_name", "item_number", "item_name"],
            as_index=False,
        )
        .agg(parent_item_qty=("qty", "sum"), parent_subtotal=("net_sale", "sum"))
    )
    rows = []
    recipe_groups = {name: frame for name, frame in normalized.groupby("recipe_name")}
    for _, sale in grouped_sales.iterrows():
        recipe = recipe_groups.get(sale["item_name"])
        if recipe is None:
            continue
        parent_qty = float(sale["parent_item_qty"])
        parent_subtotal = _money(sale["parent_subtotal"])
        parent_price = _money(parent_subtotal / parent_qty) if parent_qty else 0
        for _, component in recipe.iterrows():
            ingredient = ingredient_meta[component["item_name"]]
            consumed_qty = _qty(parent_qty * float(component["item_qty"]))
            consumed_price = _money(ingredient["average_price"])
            rows.append(
                {
                    "_month_code": sale["_month_code"],
                    "_outlet_code": sale["_outlet_code"],
                    "_outlet_name": sale["outlet_name"],
                    "item_type": "Menu Item",
                    "item_code": sale["item_number"],
                    "item_name": sale["item_name"],
                    "parent_item_qty": parent_qty,
                    "parent_unit_price": parent_price,
                    "parent_subtotal": parent_subtotal,
                    "consumed_qty": consumed_qty,
                    "consumed_unit": component["item_unit"],
                    "consumed_unit_price": consumed_price,
                    "consumed_subtotal": _money(consumed_qty * consumed_price),
                    "consumption_source": f"Recipe:{ingredient['item_code']}",
                }
            )
    return _frame(rows)


def _build_wastage(theoretical: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (month_code, outlet_code), group in theoretical.groupby(["_month_code", "_outlet_code"]):
        outlet_name = OUTLET_BY_CODE[outlet_code]["outlet_name"]
        candidates = group.sort_values("theoretical_qty", ascending=False).head(12)
        for idx, (_, item) in enumerate(candidates.iterrows(), start=1):
            base_rate = {
                "OUT001": 0.007,
                "OUT002": 0.014,
                "OUT003": 0.011,
            }[outlet_code]
            if item["category_name"] in {"Dairy", "Produce", "Protein"}:
                base_rate += 0.006
            month_no = _month_number(month_code)
            waste_qty = _qty(max(0.001, float(item["theoretical_qty"]) * base_rate * (1 + 0.08 * (month_no - 1))))
            price = _money(float(item["average_price"]) * _price_multiplier(month_code, item["category_name"]))
            waste_date = date(2026, month_no, min(25, 8 + idx))
            rows.append(
                {
                    "_month_code": month_code,
                    "_outlet_code": outlet_code,
                    "_outlet_name": outlet_name,
                    "deployment_name": outlet_name,
                    "store_kitchen_name": "Main Store",
                    "user_name": "inventory.lead",
                    "wastage_date": waste_date.isoformat(),
                    "transaction_number": f"WST-{outlet_code}-{month_no:02d}-{idx:03d}",
                    "item_code": item["item_code"],
                    "item_name": item["item_name"],
                    "category_name": item["category_name"],
                    "super_category_name": item["super_category_name"],
                    "comment": _choice(
                        ["Preparation loss", "Quality rejection", "Shelf-life loss"],
                        month_code,
                        outlet_code,
                        item["item_code"],
                    ),
                    "wastage_qty": waste_qty,
                    "unit": item["unit"],
                    "unit_price": price,
                    "wastage_amt": _money(waste_qty * price),
                    "source": "Wastage Entry",
                }
            )
    return _frame(rows)


def _group_sum(
    frame: pd.DataFrame,
    value_column: str,
    item_column: str = "item_code",
) -> dict[tuple[str, str, str], float]:
    if frame.empty:
        return {}
    grouped = frame.groupby(["_month_code", "_outlet_code", item_column], as_index=False)[
        value_column
    ].sum()
    return {
        (row["_month_code"], row["_outlet_code"], row[item_column]): float(row[value_column])
        for _, row in grouped.iterrows()
    }


def _variance_factor(outlet_code: str, category: str, month_code: str, item_code: str) -> float:
    base = {
        "OUT001": 0.012,
        "OUT002": 0.035,
        "OUT003": 0.026,
    }[outlet_code]
    if outlet_code == "OUT002" and category in {"Dairy", "Packaging", "Produce"}:
        base += 0.025
    if outlet_code == "OUT003" and category in {"Dessert Inputs", "Dairy", "Bakery"}:
        base += 0.022
    if outlet_code == "OUT001" and category in {"Coffee Inputs", "Bakery"}:
        base += 0.012
    jitter = ((_stable_int(outlet_code, month_code, item_code, "variance") % 9) - 4) / 1000
    return base + jitter


def _build_inventory_period_reports(
    theoretical: pd.DataFrame,
    ingredients: pd.DataFrame,
    entry: pd.DataFrame,
    stock_return: pd.DataFrame,
    bulk_return: pd.DataFrame,
    transfer_from: pd.DataFrame,
    transfer_to: pd.DataFrame,
    wastage: pd.DataFrame,
    po: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    ingredient_rows = ingredients.sort_values("item_code").to_dict(orient="records")
    theoretical_key = _group_sum(theoretical, "theoretical_qty")
    purchase_key = _group_sum(entry, "entry_qty")
    stock_return_key = _group_sum(stock_return, "return_qty")
    bulk_return_key = _group_sum(bulk_return, "return_qty")
    transfer_out_key = _group_sum(transfer_from, "transfer_qty")
    transfer_in_key = _group_sum(transfer_to, "transfer_qty")
    wastage_key = _group_sum(wastage, "wastage_qty")

    price_frame = po.copy()
    if not price_frame.empty:
        price_frame["weighted_price_value"] = price_frame["processed_qty"] * price_frame["unit_price"]
        price_group = price_frame.groupby(
            ["_month_code", "_outlet_code", "item_code"], as_index=False
        ).agg(qty=("processed_qty", "sum"), value=("weighted_price_value", "sum"))
        price_group["weighted_price"] = np.where(
            price_group["qty"] > 0,
            price_group["value"] / price_group["qty"],
            0,
        )
        price_key = {
            (row["_month_code"], row["_outlet_code"], row["item_code"]): float(
                row["weighted_price"]
            )
            for _, row in price_group.iterrows()
        }
    else:
        price_key = {}

    consumption_rows = []
    variance_normal_rows = []
    variance_master_rows = []
    opening_rows = []
    physical_rows = []
    closing_rows = []
    reorder_rows = []
    state: dict[tuple[str, str], float] = {}

    month1 = "month_01"
    for outlet in OUTLETS:
        for ingredient in ingredient_rows:
            theoretical_qty = theoretical_key.get(
                (month1, outlet["outlet_code"], ingredient["item_code"]), 0
            )
            initial = max(
                float(ingredient["low_stock_threshold"]) * 2.2,
                float(ingredient["standard_order_qty"]) * 0.75,
                theoretical_qty * 0.9,
            )
            state[(outlet["outlet_code"], ingredient["item_code"])] = _qty(initial)

    forced_exception = {
        ("month_03", "OUT001", "ING001"): 0.0,
        ("month_03", "OUT002", "ING002"): 0.0,
        ("month_03", "OUT003", "ING004"): -2.0,
    }

    for month_code in MONTHS:
        start, end = MONTHS[month_code]
        month_no = _month_number(month_code)
        for outlet in OUTLETS:
            outlet_code = outlet["outlet_code"]
            outlet_name = outlet["outlet_name"]
            for ingredient in ingredient_rows:
                item_code = ingredient["item_code"]
                item_name = ingredient["item_name"]
                key = (month_code, outlet_code, item_code)
                opening_qty = _qty(state[(outlet_code, item_code)])
                purchase_qty = _qty(purchase_key.get(key, 0))
                transfer_in_qty = _qty(transfer_in_key.get(key, 0))
                transfer_out_qty = _qty(transfer_out_key.get(key, 0))
                return_qty = _qty(
                    stock_return_key.get(key, 0) + bulk_return_key.get(key, 0)
                )
                wastage_qty = _qty(wastage_key.get(key, 0))
                theoretical_qty = _qty(theoretical_key.get(key, 0))
                available = (
                    opening_qty
                    + purchase_qty
                    + transfer_in_qty
                    - transfer_out_qty
                    - return_qty
                )
                planned_consumption = _qty(
                    theoretical_qty
                    * (
                        1
                        + _variance_factor(
                            outlet_code,
                            ingredient["category_name"],
                            month_code,
                            item_code,
                        )
                    )
                )
                closing_qty = _qty(available - planned_consumption - wastage_qty)
                if closing_qty < 0 and key not in forced_exception:
                    closing_qty = _qty(max(0, available * 0.04))
                if key in forced_exception:
                    closing_qty = forced_exception[key]
                actual_consumption_qty = _qty(
                    opening_qty
                    + purchase_qty
                    + transfer_in_qty
                    - transfer_out_qty
                    - return_qty
                    - closing_qty
                )
                operating_consumption_qty = _qty(
                    max(0, actual_consumption_qty - wastage_qty)
                )
                price = _money(
                    price_key.get(
                        key,
                        float(ingredient["average_price"])
                        * _price_multiplier(month_code, ingredient["category_name"]),
                    )
                )
                physical_adjustment = _qty(
                    (
                        (_stable_int(month_code, outlet_code, item_code, "physical") % 7)
                        - 3
                    )
                    * max(0.001, float(ingredient["low_stock_threshold"]) * 0.002)
                )
                physical_qty = _qty(closing_qty + physical_adjustment)
                if key in forced_exception:
                    physical_qty = closing_qty
                    physical_adjustment = 0
                variance_qty = _qty(actual_consumption_qty - theoretical_qty)
                variance_percent = (
                    round(variance_qty / theoretical_qty * 100, 2)
                    if theoretical_qty
                    else 0
                )
                ideal_closing_qty = _qty(
                    opening_qty
                    + purchase_qty
                    + transfer_in_qty
                    - transfer_out_qty
                    - return_qty
                    - theoretical_qty
                    - wastage_qty
                )
                source_yield_wastage_qty = 0
                stock_out_plus_consumption_qty = _qty(
                    transfer_out_qty + operating_consumption_qty
                )
                common = {
                    "_month_code": month_code,
                    "_outlet_code": outlet_code,
                    "_outlet_name": outlet_name,
                    "deployment_name": outlet_name,
                    "store_kitchen_name": "Main Store",
                    "item_code": item_code,
                    "item_name": item_name,
                    "category_name": ingredient["category_name"],
                    "super_category_name": ingredient["super_category_name"],
                    "average_price": price,
                    "opening_date": start.isoformat(),
                    "opening_qty": opening_qty,
                    "unit": ingredient["unit"],
                    "opening_amt": _money(opening_qty * price),
                    "purchase_qty": purchase_qty,
                    "purchase_amt": _money(purchase_qty * price),
                    "stock_in_qty": transfer_in_qty,
                    "stock_in_amt": _money(transfer_in_qty * price),
                    "consumption_qty": operating_consumption_qty,
                    "consumption_amt": _money(operating_consumption_qty * price),
                    "source_yield_wastage_qty": source_yield_wastage_qty,
                    "source_yield_wastage_amt": 0,
                    "stock_out_qty": transfer_out_qty,
                    "stock_out_amt": _money(transfer_out_qty * price),
                    "stock_out_plus_consumption_qty": stock_out_plus_consumption_qty,
                    "stock_out_plus_consumption_amt": _money(
                        stock_out_plus_consumption_qty * price
                    ),
                    "wastage_qty": wastage_qty,
                    "wastage_amt": _money(wastage_qty * price),
                    "reuse_qty": 0,
                    "reuse_amt": 0,
                    "return_qty": return_qty,
                    "return_amt": _money(return_qty * price),
                    "closing_date": end.isoformat(),
                    "closing_qty": closing_qty,
                    "closing_amt": _money(closing_qty * price),
                    "physical_gain_loss_qty": physical_adjustment,
                    "physical_gain_loss_amt": _money(physical_adjustment * price),
                    "ideal_closing_qty": ideal_closing_qty,
                    "ideal_closing_amt": _money(ideal_closing_qty * price),
                    "physical_adjusted_closing_qty": physical_qty,
                    "physical_adjusted_closing_amt": _money(physical_qty * price),
                }
                consumption_rows.append(
                    {
                        **common,
                        "indent_receive_qty": 0,
                        "indent_receive_amt": 0,
                        "indent_dispatch_qty": 0,
                        "indent_dispatch_amt": 0,
                        "internal_indent_receive_qty": transfer_in_qty,
                        "internal_indent_receive_amt": _money(
                            transfer_in_qty * price
                        ),
                        "internal_indent_dispatch_qty": transfer_out_qty,
                        "internal_indent_dispatch_amt": _money(
                            transfer_out_qty * price
                        ),
                    }
                )
                variance_normal_rows.append(
                    {
                        **common,
                        "latest_physical_date": end.isoformat(),
                        "physical_qty": physical_qty,
                        "physical_amt": _money(physical_qty * price),
                        "variance_qty": variance_qty,
                        "variance_amt": _money(variance_qty * price),
                        "variance_percent": variance_percent,
                        "actual_consumption_qty": actual_consumption_qty,
                        "actual_consumption_amt": _money(
                            actual_consumption_qty * price
                        ),
                    }
                )
                variance_master_rows.append(
                    {
                        "_month_code": month_code,
                        "_outlet_code": outlet_code,
                        "_outlet_name": outlet_name,
                        "deployment_name": outlet_name,
                        "store_kitchen_name": "Main Store",
                        "category_name": ingredient["category_name"],
                        "item_type": ingredient["super_category_name"],
                        "is_asset": "No",
                        "item_name": item_name,
                        "unit": ingredient["unit"],
                        "price": price,
                        "opening_qty": opening_qty,
                        "opening_amt": _money(opening_qty * price),
                        "purchase_qty": purchase_qty,
                        "purchase_amt": _money(purchase_qty * price),
                        "production_qty": 0,
                        "production_amt": 0,
                        "consumption_qty": operating_consumption_qty,
                        "consumption_amt": _money(operating_consumption_qty * price),
                        "stock_in_qty": transfer_in_qty,
                        "stock_in_amt": _money(transfer_in_qty * price),
                        "stock_out_qty": transfer_out_qty,
                        "stock_out_amt": _money(transfer_out_qty * price),
                        "wastage_qty": wastage_qty,
                        "wastage_amt": _money(wastage_qty * price),
                        "reuse_qty": 0,
                        "reuse_amt": 0,
                        "return_qty": return_qty,
                        "return_amt": _money(return_qty * price),
                        "closing_qty": closing_qty,
                        "closing_amt": _money(closing_qty * price),
                        "physical_qty": physical_qty,
                        "physical_amt": _money(physical_qty * price),
                        "variance_qty": variance_qty,
                        "variance_amt": _money(variance_qty * price),
                        "physical_gain_loss_qty": physical_adjustment,
                        "physical_gain_loss_amt": _money(
                            physical_adjustment * price
                        ),
                        "actual_consumption_qty": actual_consumption_qty,
                        "actual_consumption_amt": _money(
                            actual_consumption_qty * price
                        ),
                        "physical_adjusted_closing_qty": physical_qty,
                        "physical_adjusted_closing_amt": _money(
                            physical_qty * price
                        ),
                    }
                )
                opening_rows.append(
                    {
                        "_month_code": month_code,
                        "_outlet_code": outlet_code,
                        "_outlet_name": outlet_name,
                        "deployment_name": outlet_name,
                        "store_kitchen_name": "Main Store",
                        "user_name": "inventory.lead",
                        "opening_date": start.isoformat(),
                        "transaction_number": f"OPEN-{outlet_code}-{month_no:02d}-{item_code}",
                        "item_code": item_code,
                        "item_name": item_name,
                        "category_name": ingredient["category_name"],
                        "super_category_name": ingredient["super_category_name"],
                        "comment": "Opening stock for synthetic month",
                        "opening_qty": opening_qty,
                        "unit": ingredient["unit"],
                        "unit_price": price,
                        "opening_subtotal": _money(opening_qty * price),
                        "source": "Opening Stock",
                    }
                )
                physical_rows.append(
                    {
                        "_month_code": month_code,
                        "_outlet_code": outlet_code,
                        "_outlet_name": outlet_name,
                        "deployment_name": outlet_name,
                        "store_kitchen_name": "Main Store",
                        "user_name": "inventory.lead",
                        "physical_date": end.isoformat(),
                        "transaction_number": f"PHY-{outlet_code}-{month_no:02d}-{item_code}",
                        "item_code": item_code,
                        "item_name": item_name,
                        "item_brand": "ABNAH Approved",
                        "category_name": ingredient["category_name"],
                        "super_category_name": ingredient["super_category_name"],
                        "comment": "Month-end physical stock take",
                        "physical_qty": physical_qty,
                        "unit": ingredient["unit"],
                        "unit_price": price,
                        "physical_amt": _money(physical_qty * price),
                        "source": "Physical Stock",
                    }
                )
                closing_rows.append(
                    {
                        "_month_code": month_code,
                        "_outlet_code": outlet_code,
                        "_outlet_name": outlet_name,
                        "deployment_name": outlet_name,
                        "stock_date": end.isoformat(),
                        "generation_date": end.isoformat(),
                        "generation_time": "23:59:00",
                        "item_code": item_code,
                        "item_name": item_name,
                        "super_category_code": f"SUP-{ingredient['super_category_name'][:3].upper()}",
                        "super_category_name": ingredient["super_category_name"],
                        "category_code": f"CAT-{ingredient['category_name'][:3].upper()}",
                        "category_name": ingredient["category_name"],
                        "unit_name": ingredient["unit"],
                        "average_price": price,
                        "gk2_main_store_qty": closing_qty,
                        "total_qty": closing_qty,
                        "total_amt": _money(closing_qty * price),
                    }
                )
                reorder_rows.append(
                    {
                        "_month_code": month_code,
                        "_outlet_code": outlet_code,
                        "_outlet_name": outlet_name,
                        "deployment_name": outlet_name,
                        "store_name": "Main Store",
                        "item_code": item_code,
                        "item_name": item_name,
                        "reorder_level_qty": ingredient["low_stock_threshold"],
                        "minimum_order_level_qty": _qty(
                            float(ingredient["low_stock_threshold"]) * 0.6
                        ),
                        "available_qty": closing_qty,
                        "unit_name": ingredient["unit"],
                    }
                )
                state[(outlet_code, item_code)] = physical_qty

    return {
        "enterprise_consumption_detail": _frame(consumption_rows),
        "enterprise_variance_normal": _frame(variance_normal_rows),
        "enterprise_variance_master": _frame(variance_master_rows),
        "enterprise_opening": _frame(opening_rows),
        "enterprise_physical": _frame(physical_rows),
        "closing_stock": _frame(closing_rows),
        "enterprise_reorder": _frame(reorder_rows),
    }


def _build_forecast(
    sales: pd.DataFrame,
    menu: pd.DataFrame,
) -> pd.DataFrame:
    menu_meta = menu.set_index("item_number").to_dict(orient="index")
    source = sales.copy()
    source["_month_code"] = source["date"].map(_month_code)
    source["_outlet_code"] = source["outlet_name"].map(
        lambda value: OUTLET_BY_NAME[value]["outlet_code"]
    )
    grouped = source.groupby(
        ["_month_code", "_outlet_code", "outlet_name", "item_number", "item_name"],
        as_index=False,
    ).agg(actual_qty=("qty", "sum"), net_sale=("net_sale", "sum"))
    rows = []
    for _, row in grouped.iterrows():
        month_code = row["_month_code"]
        month_days = (MONTHS[month_code][1] - MONTHS[month_code][0]).days + 1
        daily_qty = float(row["actual_qty"]) / month_days
        meta = menu_meta[row["item_number"]]
        for horizon_day in range(1, 8):
            forecast_date = _month_end(month_code) + timedelta(days=horizon_day)
            weekend = forecast_date.weekday() >= 5
            outlet_factor = 1.0
            if row["_outlet_code"] == "OUT001":
                outlet_factor = 0.72 if weekend else 1.12
            elif row["_outlet_code"] == "OUT002":
                outlet_factor = 1.18 if weekend else 1.0
            elif row["_outlet_code"] == "OUT003":
                outlet_factor = 1.28 if weekend else 0.94
            forecast_qty = _qty(
                daily_qty
                * outlet_factor
                * (
                    0.96
                    + (_stable_int(row["item_number"], forecast_date, "forecast") % 9)
                    / 100
                )
            )
            rows.append(
                {
                    "forecast_as_of_month": month_code,
                    "forecast_date": forecast_date.isoformat(),
                    "outlet_code": row["_outlet_code"],
                    "outlet_name": row["outlet_name"],
                    "menu_item_code": row["item_number"],
                    "menu_item_name": row["item_name"],
                    "super_category_name": meta["super_category_name"],
                    "category_name": meta["category_name"],
                    "forecast_qty": forecast_qty,
                    "forecast_net_sales": _money(
                        forecast_qty * float(meta["rate"]) * 0.97
                    ),
                    "model_name": "Synthetic 28-day seasonal baseline",
                    "confidence_band": _choice(
                        ["High", "Medium", "Medium"],
                        row["item_number"],
                        forecast_date,
                    ),
                }
            )
    return _frame(rows)


def _build_auxiliary_masters(
    ingredients: pd.DataFrame,
    vendors: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    outlet_rows = []
    for outlet in OUTLETS:
        coords = OUTLET_COORDINATES[outlet["outlet_code"]]
        outlet_rows.append(
            {
                "outlet_code": outlet["outlet_code"],
                "outlet_name": outlet["outlet_name"],
                "region": coords["region"],
                "city": coords["city"],
                "market_area": outlet["market_area"],
                "latitude": coords["latitude"],
                "longitude": coords["longitude"],
                "new_matured_flag": coords["new_matured_flag"],
                "active_status": "Active",
                "source_evidence": (
                    "synthetic_demo_reference_correlated_to_operational_outlet_keys"
                ),
                "is_synthetic": 1,
                "production_use_status": (
                    "replace_with_approved_abnah_outlet_reference"
                ),
            }
        )

    item_master = ingredients.copy()
    item_master["canonical_uom"] = item_master["unit"]
    item_master["uom_conversion_factor"] = 1
    item_master["shelf_life_days"] = item_master["category_name"].map(
        SHELF_LIFE_DAYS
    ).fillna(30)
    item_master["storage_type"] = item_master["category_name"].map(
        STORAGE_TYPE
    ).fillna("Ambient")
    item_master["food_beverage_non_food_flag"] = np.where(
        item_master["category_name"] == "Packaging", "Non-food", "Food/Beverage"
    )
    item_master["criticality"] = np.where(
        item_master["category_name"].isin(
            ["Coffee Inputs", "Dairy", "Protein", "Packaging"]
        ),
        "Critical",
        "Standard",
    )
    item_master = item_master[
        [
            "item_code",
            "item_name",
            "category_name",
            "super_category_name",
            "unit",
            "canonical_uom",
            "uom_conversion_factor",
            "average_price",
            "low_stock_threshold",
            "standard_order_qty",
            "primary_vendor",
            "alternate_vendor",
            "shelf_life_days",
            "storage_type",
            "food_beverage_non_food_flag",
            "criticality",
        ]
    ]

    vendor_master = vendors.copy()
    vendor_master["active_status"] = "Active"
    vendor_master["region_served"] = vendor_master["state"].map(
        lambda value: "North" if value in {"Delhi", "Haryana", "Uttar Pradesh"} else "Other"
    )
    vendor_master["default_lead_time_days"] = vendor_master["vendor_name"].map(
        lambda value: 2 + VENDOR_DELAY_DAYS.get(value, 1)
    )
    vendor_master["approved_category_mapping"] = vendor_master["vendor_name"].map(
        lambda value: "; ".join(
            ingredients.loc[
                ingredients["primary_vendor"] == value, "category_name"
            ].drop_duplicates()
        )
    )
    vendor_master = vendor_master[
        [
            "vendor_code",
            "vendor_name",
            "description",
            "state",
            "region_served",
            "active_status",
            "default_lead_time_days",
            "approved_category_mapping",
        ]
    ]

    return {
        "AUX_Outlet_Master": _frame(outlet_rows),
        "AUX_Item_Master": item_master,
        "AUX_Vendor_Master": vendor_master,
    }


def _build_expiry_estimate(
    closing: pd.DataFrame,
    theoretical: pd.DataFrame,
    item_master: pd.DataFrame,
    purchase_detail: pd.DataFrame,
) -> pd.DataFrame:
    item_meta = item_master.set_index("item_code").to_dict(orient="index")
    theoretical_lookup = (
        theoretical.groupby(
            ["_month_code", "_outlet_code", "item_code"],
            as_index=False,
        )["theoretical_qty"]
        .sum()
        .set_index(["_month_code", "_outlet_code", "item_code"])[
            "theoretical_qty"
        ]
        .to_dict()
    )
    receipts = purchase_detail.copy()
    receipts["_receipt_date"] = pd.to_datetime(
        receipts["transaction_date"],
        errors="coerce",
    ).dt.date
    receipt_lookup = {
        key: group.sort_values(
            ["_receipt_date", "transaction_number"],
            ascending=[False, False],
        ).to_dict(orient="records")
        for key, group in receipts.groupby(["_outlet_code", "item_code"])
    }
    rows = []
    for _, row in closing.iterrows():
        if row["total_qty"] <= 0:
            continue
        meta = item_meta[row["item_code"]]
        if meta["food_beverage_non_food_flag"] == "Non-food":
            continue
        shelf_life = int(meta["shelf_life_days"])
        if shelf_life > 30:
            continue
        as_of_date = pd.to_datetime(row["stock_date"]).date()
        month_days = (
            MONTHS[row["_month_code"]][1] - MONTHS[row["_month_code"]][0]
        ).days + 1
        theoretical_qty = float(
            theoretical_lookup.get(
                (row["_month_code"], row["_outlet_code"], row["item_code"]),
                0,
            )
        )
        daily_theoretical_demand = theoretical_qty / month_days
        item_closing_qty = float(row["total_qty"])
        candidate_receipts = []
        for receipt in receipt_lookup.get(
            (row["_outlet_code"], row["item_code"]),
            [],
        ):
            receipt_date = receipt["_receipt_date"]
            if receipt_date is None or receipt_date > as_of_date:
                continue
            estimated_expiry_date = receipt_date + timedelta(
                days=shelf_life
            )
            days_to_expiry = (estimated_expiry_date - as_of_date).days
            if days_to_expiry < -2 or days_to_expiry > 7:
                continue
            candidate_receipts.append(
                {
                    "batch_number": receipt["batch_number"],
                    "batch_allocation_id": (
                        f"{receipt['batch_number']}|"
                        f"{receipt['transaction_number']}"
                    ),
                    "receipt_date": receipt_date,
                    "grn_number": receipt["transaction_number"],
                    "po_number": receipt["po_number"],
                    "vendor_name": receipt["vendor_name"],
                    "received_qty": max(
                        0,
                        float(receipt["purchase_qty"]),
                    ),
                    "average_unit_cost": float(receipt["purchase_unit_price"]),
                    "receipt_source_status": (
                        "synthetic_internal_receipt_lineage"
                    ),
                    "estimated_expiry_date": estimated_expiry_date,
                    "days_to_expiry": days_to_expiry,
                }
            )
        candidate_receipts.sort(
            key=lambda batch: (
                batch["estimated_expiry_date"],
                batch["receipt_date"],
                batch["batch_allocation_id"],
            )
        )
        if candidate_receipts:
            batch = candidate_receipts[0]
        else:
            days_to_expiry = 1 + (
                _stable_int(
                    row["_month_code"],
                    row["_outlet_code"],
                    row["item_code"],
                    "expiry-scenario-days",
                )
                % min(7, shelf_life)
            )
            estimated_expiry_date = as_of_date + timedelta(
                days=days_to_expiry
            )
            receipt_date = estimated_expiry_date - timedelta(
                days=shelf_life
            )
            batch_number = (
                f"SYN-EXP-{row['_month_code']}-"
                f"{row['_outlet_code']}-{row['item_code']}"
            )
            batch = {
                "batch_number": batch_number,
                "batch_allocation_id": batch_number,
                "receipt_date": receipt_date,
                "grn_number": "",
                "po_number": "",
                "vendor_name": "",
                "received_qty": item_closing_qty,
                "average_unit_cost": float(row["average_price"]),
                "receipt_source_status": (
                    "synthetic_near_expiry_opening_tranche"
                ),
                "estimated_expiry_date": estimated_expiry_date,
                "days_to_expiry": days_to_expiry,
            }

        fifo_tranche_fraction = 0.12 + (
            _stable_int(
                row["_month_code"],
                row["_outlet_code"],
                row["item_code"],
                "fifo-tranche",
            )
            % 9
        ) / 100
        estimated_fifo_tranche_qty = min(
            item_closing_qty * fifo_tranche_fraction,
            batch["received_qty"],
        )
        expected_consumption_before_expiry = (
            daily_theoretical_demand * max(0, batch["days_to_expiry"])
        )
        qty_at_risk = _qty(
            max(
                0,
                estimated_fifo_tranche_qty
                - expected_consumption_before_expiry,
            )
        )
        if qty_at_risk <= 0:
            continue
        if batch["days_to_expiry"] < 0:
            risk_status = "EXPIRED"
        elif batch["days_to_expiry"] == 0:
            risk_status = "EXPIRES_TODAY"
        elif batch["days_to_expiry"] <= 3:
            risk_status = "CRITICAL"
        elif batch["days_to_expiry"] <= 7:
            risk_status = "WATCH"
        else:
            risk_status = "MONITOR"
        coords = OUTLET_COORDINATES[row["_outlet_code"]]
        rows.append(
            {
                "source_period_code": row["_month_code"],
                "as_of_date": row["stock_date"],
                "outlet_code": row["_outlet_code"],
                "outlet_name": row["_outlet_name"],
                "region": coords["region"],
                "city": coords["city"],
                "market_area": OUTLET_BY_CODE[
                    row["_outlet_code"]
                ]["market_area"],
                "latitude": coords["latitude"],
                "longitude": coords["longitude"],
                "store_name": "Main Store",
                "batch_allocation_id": batch["batch_allocation_id"],
                "batch_number": batch["batch_number"],
                "receipt_date": batch["receipt_date"].isoformat(),
                "grn_number": batch["grn_number"],
                "po_number": batch["po_number"],
                "vendor_name": batch["vendor_name"],
                "receipt_source_status": batch["receipt_source_status"],
                "item_code": row["item_code"],
                "item_name": row["item_name"],
                "category_name": row["category_name"],
                "unit": row["unit_name"],
                "received_qty": _qty(batch["received_qty"]),
                "batch_remaining_qty": _qty(
                    estimated_fifo_tranche_qty
                ),
                "item_closing_qty": _qty(item_closing_qty),
                "available_qty": _qty(item_closing_qty),
                "average_unit_cost": _money(batch["average_unit_cost"]),
                "shelf_life_days_assumption": shelf_life,
                "estimated_fifo_tranche_qty": _qty(
                    estimated_fifo_tranche_qty
                ),
                "daily_theoretical_demand": _qty(
                    daily_theoretical_demand
                ),
                "expected_consumption_before_expiry": _qty(
                    expected_consumption_before_expiry
                ),
                "estimated_expiry_date": batch[
                    "estimated_expiry_date"
                ].isoformat(),
                "days_to_expiry": batch["days_to_expiry"],
                "qty_at_risk": qty_at_risk,
                "expiry_risk_value": _money(
                    qty_at_risk * batch["average_unit_cost"]
                ),
                "risk_status": risk_status,
                "is_estimated": 1,
                "estimation_method": (
                    "One synthetic near-expiry FIFO tranche linked to a "
                    "receipt batch where available; expiry equals receipt "
                    "date plus category shelf life; theoretical demand is "
                    "deducted before expiry"
                ),
                "source_evidence": (
                    "closing_stock+synthetic_receipt_lineage+"
                    "theoretical_consumption+"
                    "category_shelf_life_assumption"
                ),
                "production_use_status": (
                    "demo_only_no_posist_batch_or_expiry_source"
                ),
            }
        )
    return _frame(rows)


def _build_vendor_price(po: pd.DataFrame, vendors: pd.DataFrame) -> pd.DataFrame:
    vendor_codes = vendors.set_index("vendor_name")["vendor_code"].to_dict()
    grouped = po.groupby(
        [
            "_month_code",
            "_outlet_code",
            "_outlet_name",
            "vendor_name",
            "item_code",
            "unit",
        ],
        as_index=False,
    ).agg(unit_price=("unit_price", "mean"))
    rows = []
    for idx, row in grouped.iterrows():
        month_end = _month_end(row["_month_code"])
        rows.append(
            {
                "_month_code": row["_month_code"],
                "_outlet_code": row["_outlet_code"],
                "_outlet_name": row["_outlet_name"],
                "erp_doc_id": f"EVP-{row['_month_code']}-{idx + 1:05d}",
                "vendor_id": vendor_codes.get(row["vendor_name"], ""),
                "vendor_name": row["vendor_name"],
                "outlet": row["_outlet_code"],
                "outlet_name": row["_outlet_name"],
                "status": "Approved",
                "published": "Yes",
                "received_on": month_end.isoformat(),
                "inserted_by": "synthetic.generator",
                "comment": "Monthly approved synthetic vendor price",
                "updated_on": month_end.isoformat(),
                "item_id": row["item_code"],
                "uom": row["unit"],
                "unit_price": _money(row["unit_price"]),
            }
        )
    return _frame(rows)


def _build_purchase_summary(
    purchase_detail: pd.DataFrame,
) -> pd.DataFrame:
    if purchase_detail.empty:
        return pd.DataFrame()
    grouped = purchase_detail.groupby(
        [
            "_month_code",
            "_outlet_code",
            "_outlet_name",
            "vendor_code",
            "vendor_name",
        ],
        as_index=False,
    ).agg(
        subtotal=("purchase_amount", "sum"),
        discount=("discount_amt", "sum"),
        cgst=("cgst_tax_amt", "sum"),
        sgst=("sgst_tax_amt", "sum"),
        igst=("igst_tax_amt", "sum"),
        other=("other_tax_amt", "sum"),
        total=("total_amt", "sum"),
    )
    grouped["total_tax"] = grouped["cgst"] + grouped["sgst"] + grouped["igst"] + grouped["other"]
    return grouped.rename(
        columns={
            "_outlet_name": "deployment_name",
            "subtotal": "subtotal",
            "discount": "discount",
            "total": "total",
        }
    )


def _captured_schema_exports(
    vendor_price: pd.DataFrame,
    purchase_summary: pd.DataFrame,
    inventory_reports: dict[str, pd.DataFrame],
    ingredients: pd.DataFrame,
) -> dict[str, tuple[list[str], pd.DataFrame]]:
    erp_headers = [
        "ERP Doc ID",
        "Vendor ID",
        "Vendor Name",
        "Outlet #",
        "Outlet Name",
        "Status",
        "Published",
        "Received On",
        "Inserted By",
        "Comment",
        "Updated On",
        "Item ID",
        "UOM",
        "Unit Price",
    ]
    erp_columns = [
        "erp_doc_id",
        "vendor_id",
        "vendor_name",
        "outlet",
        "outlet_name",
        "status",
        "published",
        "received_on",
        "inserted_by",
        "comment",
        "updated_on",
        "item_id",
        "uom",
        "unit_price",
    ]
    summary_headers = [
        "DeploymentName",
        "vendorCode",
        "vendorName",
        "subTotal",
        "discount",
        "totalTax",
        "Total",
    ]
    summary_columns = [
        "deployment_name",
        "vendor_code",
        "vendor_name",
        "subtotal",
        "discount",
        "total_tax",
        "total",
    ]
    summary_frame = purchase_summary.copy()
    ingredient_meta = ingredients.set_index("item_code").to_dict(orient="index")
    indent_rows = []
    reorder = inventory_reports["enterprise_reorder"]
    for _, row in reorder[
        reorder["available_qty"] < reorder["reorder_level_qty"]
    ].iterrows():
        ingredient = ingredient_meta[row["item_code"]]
        requested = _qty(
            max(
                0,
                float(row["reorder_level_qty"]) * 2
                - float(row["available_qty"]),
            )
        )
        price = float(ingredient["average_price"]) * _price_multiplier(
            row["_month_code"], ingredient["category_name"]
        )
        supplied = _qty(requested * 0.85)
        received = _qty(supplied * 0.96)
        suspicious = _qty(max(0, supplied - received))
        indent_rows.append(
            {
                "_month_code": row["_month_code"],
                "_outlet_code": row["_outlet_code"],
                "_outlet_name": row["_outlet_name"],
                "supplier": ingredient["primary_vendor"],
                "receiver": row["_outlet_name"],
                "supercategory": ingredient["super_category_name"],
                "category": ingredient["category_name"],
                "item_code": row["item_code"],
                "item_name": row["item_name"],
                "master_preferred_unit": ingredient["unit"],
                "requested_qty": requested,
                "requested_subtotal": _money(requested * price),
                "supplied_qty": supplied,
                "supplied_subtotal": _money(supplied * price),
                "received_qty": received,
                "received_subtotal": _money(received * price),
                "suspicious_qty": suspicious,
                "suspicious_subtotal": _money(suspicious * price),
            }
        )
    indent = _frame(indent_rows)
    indent_headers = [
        "Supplier",
        "Receiver",
        "SuperCategory",
        "Category",
        "Item Code",
        "Item Name",
        "Master Preferred Unit",
        "Requested Qty",
        "Requested Subtotal",
        "Supplied Qty",
        "Supplied Subtotal",
        "Received Qty",
        "Received Subtotal",
        "Suspicious Qty",
        "Suspicious Subtotal",
    ]
    indent_columns = [
        "supplier",
        "receiver",
        "supercategory",
        "category",
        "item_code",
        "item_name",
        "master_preferred_unit",
        "requested_qty",
        "requested_subtotal",
        "supplied_qty",
        "supplied_subtotal",
        "received_qty",
        "received_subtotal",
        "suspicious_qty",
        "suspicious_subtotal",
    ]

    frames = {
        "ERP_Vendor_Price": (erp_headers, vendor_price[erp_columns + [column for column in vendor_price.columns if column.startswith("_")]]),
        "Enterprise_Purchase_Summary": (
            summary_headers,
            summary_frame[summary_columns + [column for column in summary_frame.columns if column.startswith("_")]],
        ),
        "Enterprise_Consolidated_Indent": (
            indent_headers,
            indent[indent_columns + [column for column in indent.columns if column.startswith("_")]] if not indent.empty else indent,
        ),
    }
    return frames


def _write_schema_capture_csv(
    frame: pd.DataFrame,
    headers: list[str],
    columns: list[str],
    path: Path,
) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        if not frame.empty:
            for row in frame.to_dict(orient="records"):
                writer.writerow([row.get(column, "") for column in columns])
    return len(frame)


def _write_normalized_landing_csv(
    frame: pd.DataFrame,
    contract: Contract,
    path: Path,
) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    landing = frame.copy()
    if contract.stem not in STATIC_CONTRACTS:
        landing.insert(
            0,
            "source_period_end",
            landing["_month_code"].map(lambda value: MONTHS[value][1].isoformat()),
        )
        landing.insert(
            0,
            "source_period_start",
            landing["_month_code"].map(lambda value: MONTHS[value][0].isoformat()),
        )
        landing.insert(0, "source_outlet_name", landing["_outlet_name"])
        landing.insert(0, "source_outlet_code", landing["_outlet_code"])
        landing.insert(0, "source_period_code", landing["_month_code"])
        output_columns = [
            "source_period_code",
            "source_outlet_code",
            "source_outlet_name",
            "source_period_start",
            "source_period_end",
            *contract.row_columns,
        ]
    else:
        output_columns = contract.row_columns
    landing[output_columns].to_csv(path, index=False, encoding="utf-8-sig")
    return len(landing)


def _validate(
    report_frames: dict[str, pd.DataFrame],
    captured_frames: dict[str, tuple[list[str], pd.DataFrame]],
    auxiliary_frames: dict[str, pd.DataFrame],
) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []

    def add(check_id: str, passed: bool, observed: Any, expected: Any, notes: str) -> None:
        checks.append(
            {
                "check_id": check_id,
                "status": "PASS" if passed else "FAIL",
                "observed": observed,
                "expected": expected,
                "notes": notes,
            }
        )

    bill = report_frames["bill_item_detail"]
    margin = report_frames["gross_net_margin"]
    add(
        "sales_line_count",
        len(bill) == len(margin),
        len(bill),
        len(margin),
        "Bill Item Detail and Gross/Net Margin use the same synthetic sale lines.",
    )
    add(
        "sales_qty_reconciliation",
        abs(float(bill["item_qty"].sum()) - float(margin["item_qty"].sum())) < 0.001,
        round(float(bill["item_qty"].sum()), 4),
        round(float(margin["item_qty"].sum()), 4),
        "Sold quantity must reconcile across the two sales authorities.",
    )
    bill_tax = (
        bill["gst_5_tax_amt"]
        + bill["gst_18_tax_amt"]
        + bill["gst_3_tax_amt"]
    )
    bill_net_gap = (
        bill["net_amt"]
        - (bill["line_amt"] - bill["discount_amt"] + bill_tax)
    ).abs()
    add(
        "bill_item_net_bridge",
        bool((bill_net_gap <= 0.05).all()),
        int((bill_net_gap > 0.05).sum()),
        0,
        "Bill-item net amount uses exported GST tax values, not the taxable-base columns.",
    )

    po = report_frames["enterprise_purchase_order"]
    non_cancelled = po[po["po_status"] != "Cancelled"]
    po_gap = (
        non_cancelled["ordered_qty"]
        - non_cancelled["processed_qty"]
        - non_cancelled["remaining_balance_qty"]
    ).abs()
    add(
        "po_quantity_bridge",
        bool((po_gap < 0.001).all()),
        int((po_gap >= 0.001).sum()),
        0,
        "Cancelled lines are excluded because Restroworks may retain original ordered quantity.",
    )

    transfer_from = report_frames["enterprise_transfer_from"]
    transfer_to = report_frames["enterprise_transfer_to"]
    add(
        "transfer_quantity_balance",
        abs(float(transfer_from["transfer_qty"].sum()) - float(transfer_to["transfer_qty"].sum())) < 0.001,
        round(float(transfer_from["transfer_qty"].sum()), 4),
        round(float(transfer_to["transfer_qty"].sum()), 4),
        "Every synthetic transfer has a supplier and receiver side.",
    )

    closing = report_frames["closing_stock"]
    closing_gap = (
        closing["total_amt"] - closing["total_qty"] * closing["average_price"]
    ).abs()
    add(
        "closing_value_bridge",
        bool((closing_gap <= 0.05).all()),
        int((closing_gap > 0.05).sum()),
        0,
        "Closing amount equals quantity multiplied by average price within rounding tolerance.",
    )

    variance = report_frames["enterprise_variance_normal"]
    actual_bridge = (
        variance["opening_qty"]
        + variance["purchase_qty"]
        + variance["stock_in_qty"]
        - variance["stock_out_qty"]
        - variance["return_qty"]
        - variance["closing_qty"]
    )
    actual_gap = (actual_bridge - variance["actual_consumption_qty"]).abs()
    add(
        "actual_consumption_bridge",
        bool((actual_gap < 0.001).all()),
        int((actual_gap >= 0.001).sum()),
        0,
        "Actual consumption follows the approved opening plus receipts plus transfer-in less transfer-out, returns and closing rule.",
    )
    theoretical_lookup = _group_sum(
        auxiliary_frames["AUX_Theoretical_Consumption"], "theoretical_qty"
    )
    expected_variance = variance.apply(
        lambda row: float(row["actual_consumption_qty"])
        - theoretical_lookup.get(
            (row["_month_code"], row["_outlet_code"], row["item_code"]), 0
        ),
        axis=1,
    )
    variance_gap = (variance["variance_qty"] - expected_variance).astype(float)
    add(
        "variance_bridge",
        bool((variance_gap.abs() < 0.001).all()),
        int((variance_gap.abs() >= 0.001).sum()),
        0,
        "Consumption variance equals actual less theoretical at outlet-item-month grain.",
    )

    negative_count = int((closing["total_qty"] < 0).sum())
    zero_count = int((closing["total_qty"] == 0).sum())
    add(
        "controlled_data_quality_exceptions",
        negative_count == 1 and zero_count >= 2,
        f"negative={negative_count}; zero={zero_count}",
        "negative=1; zero>=2",
        "Controlled exceptions keep the data-quality page demonstrable and are listed in the truth pack.",
    )

    outlet_master = auxiliary_frames["AUX_Outlet_Master"]
    add(
        "aux_outlet_master_unique",
        len(outlet_master) == len(OUTLETS)
        and outlet_master["outlet_code"].nunique() == len(OUTLETS),
        (
            f"rows={len(outlet_master)}; "
            f"unique_outlets={outlet_master['outlet_code'].nunique()}"
        ),
        f"rows={len(OUTLETS)}; unique_outlets={len(OUTLETS)}",
        "The scenario geography must contain exactly one row per synthetic outlet.",
    )

    expiry = auxiliary_frames["AUX_Expiry_Estimate"]
    expiry_value_gap = (
        expiry["expiry_risk_value"]
        - expiry["qty_at_risk"] * expiry["average_unit_cost"]
    ).abs()
    expiry_tranche_gap = (
        expiry["batch_remaining_qty"]
        - expiry["estimated_fifo_tranche_qty"]
    ).abs()
    expiry_receipt_dates = pd.to_datetime(expiry["receipt_date"])
    expiry_as_of_dates = pd.to_datetime(expiry["as_of_date"])
    expiry_dates = pd.to_datetime(expiry["estimated_expiry_date"])
    expiry_key_duplicates = expiry.duplicated(
        [
            "source_period_code",
            "outlet_code",
            "item_code",
            "batch_allocation_id",
        ]
    )
    expiry_valid = (
        not expiry.empty
        and bool((expiry["batch_remaining_qty"] > 0).all())
        and bool((expiry["qty_at_risk"] >= 0).all())
        and bool(
            (
                expiry["qty_at_risk"]
                <= expiry["batch_remaining_qty"] + 0.0001
            ).all()
        )
        and bool(
            (
                expiry["batch_remaining_qty"]
                <= expiry["item_closing_qty"] + 0.0001
            ).all()
        )
        and bool((expiry_value_gap <= 0.05).all())
        and bool((expiry_tranche_gap <= 0.0001).all())
        and bool((expiry_receipt_dates <= expiry_as_of_dates).all())
        and bool((expiry_dates >= expiry_receipt_dates).all())
        and not bool(expiry_key_duplicates.any())
        and bool((expiry["qty_at_risk"] > 0).any())
        and set(expiry["is_estimated"].unique()) == {1}
    )
    add(
        "aux_expiry_estimate_traceable",
        expiry_valid,
        (
            f"rows={len(expiry)}; "
            f"risky_rows={int((expiry['qty_at_risk'] > 0).sum())}; "
            f"value_gap_rows={int((expiry_value_gap > 0.05).sum())}; "
            "tranche_gap_rows="
            f"{int((expiry_tranche_gap > 0.0001).sum())}; "
            f"duplicate_batch_keys={int(expiry_key_duplicates.sum())}"
        ),
        (
            "rows>0; risky_rows>0; value_gap_rows=0; "
            "tranche_gap_rows=0; duplicate_batch_keys=0"
        ),
        (
            "Expiry demo tranches must remain within item closing stock, "
            "retain unique batch lineage and stay visibly non-production."
        ),
    )

    for stem, frame in report_frames.items():
        if stem in OBSERVED_HEADER_ONLY_REPORTS:
            add(
                f"report_header_only:{stem}",
                frame.empty,
                len(frame),
                0,
                "The synthetic export mirrors the header-only UAT source state.",
            )
        else:
            add(
                f"report_non_empty:{stem}",
                not frame.empty,
                len(frame),
                ">0",
                "Every populated validated source contract has synthetic rows.",
            )
    for name, (_, frame) in captured_frames.items():
        add(
            f"schema_capture_non_empty:{name}",
            not frame.empty,
            len(frame),
            ">0",
            "Schema-capture-only reports are generated separately from validated CSV contracts.",
        )
    return checks


def _write_validation_doc(
    report_frames: dict[str, pd.DataFrame],
    checks: list[dict[str, Any]],
    contracts: dict[str, Contract],
    manifest: pd.DataFrame,
) -> None:
    failures = [check for check in checks if check["status"] != "PASS"]
    lines = [
        "# ABNAH Control Tower Synthetic Validation",
        "",
        "This pack extends the original three-outlet story into Restroworks-shaped control-tower reports.",
        "",
        "## Outlet Narrative",
        "",
        "- OUT001 Connaught Place: corporate and weekday-led coffee/lunch demand.",
        "- OUT002 Hauz Khas: youth, social-event, cold-beverage and wrap demand with higher consumption pressure.",
        "- OUT003 Saket Premium: mall, premium beverage, dessert and weekend demand with higher chilled/dessert exposure.",
        "",
        "## Contract Coverage",
        "",
        f"- Validated CSV contracts generated: {len(report_frames)}",
        f"- Exact source export files generated: {int(manifest['file_count'].sum())}",
        f"- Total synthetic source rows: {int(manifest['row_count'].sum()):,}",
        f"- Reconciliation checks: {len(checks)}",
        f"- Failed checks: {len(failures)}",
        "",
        "The `RAW_CT_` source files preserve Restroworks header spelling and order, including repeated headers and trailing blank columns where observed. Fields proven fully blank or zero-only in the audited POSIST exports remain in those raw contracts but carry no synthetic signal. `AUX_` files are explicitly labelled and are never presented as Restroworks exports. Forecast and theoretical consumption are model outputs; outlet geography and expiry exposure are demo-only reference scenarios that must be replaced before production.",
        "",
        "## Source Fidelity Boundary",
        "",
        f"- Audited fields mirrored as fully blank: {sum(len(fields) for fields in OBSERVED_ALL_BLANK_FIELDS.values())}",
        f"- Audited decimal fields mirrored as zero-only: {sum(len(fields) for fields in OBSERVED_ALL_ZERO_FIELDS.values())}",
        f"- Header-only report contracts mirrored with zero rows: {len(OBSERVED_HEADER_ONLY_REPORTS)}",
        "- Blank and zero-only fields are excluded from active Query Table projections and dashboard measures until a later populated POSIST extract proves usable signal.",
        "- `RAWN_CT_` files are intentionally normalized landing tables with canonical source-period and outlet metadata; they are not byte-for-byte POSIST exports.",
        "- Synthetic rows preserve the observed report grain and column behavior, but they do not claim to reproduce actual POSIST row counts, transaction identifiers, or operational value distributions.",
        "",
        "## Controlled Demo Exceptions",
        "",
        "- One negative month-end stock row is intentionally retained for Page 4 data-quality validation.",
        "- Two zero-stock-with-demand rows are intentionally retained for Page 1 and Page 4 validation.",
        "- Three March open/partial PO lines have blank expected-delivery dates to validate the PO completeness control.",
        "- Formula and identity fields otherwise reconcile through the common synthetic ledger.",
        "",
        "## Report Rows",
        "",
        "| Report | Contract | Rows | Files |",
        "|---|---|---:|---:|",
    ]
    for _, row in manifest.sort_values("report_name").iterrows():
        lines.append(
            f"| {row['report_name']} | {row['contract_status']} | {int(row['row_count']):,} | {int(row['file_count'])} |"
        )
    lines.extend(
        [
            "",
            "## Reconciliation Results",
            "",
            "| Check | Status | Observed | Expected |",
            "|---|---|---|---|",
        ]
    )
    for check in checks:
        lines.append(
            f"| {check['check_id']} | {check['status']} | {check['observed']} | {check['expected']} |"
        )
    lines.extend(
        [
            "",
            "## Remaining Source Gaps",
            "",
            "- Approved item/UOM reference for shelf life, reorder quantity, order quantity and criticality",
            "- Vendor lead time, service SLA and approved vendor-item relationships; Vendor Report supports identity, validity dates, compliance context, state and address only",
            "- Expiry Report or batch-expiry evidence; the ABNAH module is not enabled, so the packaged expiry table remains a visibly labelled demo estimate",
            "- Standing Purchase Order export schema and release linkage",
            "- Food Cost Report missing child columns",
            "",
            "There is no verified report named `Raw Material Item Detail`. Item identity, category, UOM and observed cost are derived from Closing Stock, Entry, Purchase Order and Item Recipe. Vendor identity comes from the exact historical `Vendor Report` schema after structural cleaning. Exact expiry and Standing PO remain unavailable; the demonstrator's AUX expiry output is an explicit scenario estimate, not a POSIST fact.",
        ]
    )
    VALIDATION_DOC.write_text("\n".join(lines), encoding="utf-8")


def build_control_tower_reports(
    *,
    menu: pd.DataFrame,
    ingredients: pd.DataFrame,
    vendors: pd.DataFrame,
    bom: pd.DataFrame,
    sales: pd.DataFrame,
    purchase: pd.DataFrame,
) -> dict[str, int]:
    _clear_generated_outputs()
    contracts = _contracts()

    bill, margin = _build_sales_reports(sales, menu, bom, ingredients)
    item_recipe = _build_item_recipe(bom, menu, ingredients)
    po = _build_purchase_order(purchase, ingredients)
    entry, purchase_detail, stock_return, bulk_return = _build_entry_and_returns(
        po, ingredients, vendors
    )
    stock_return = stock_return.iloc[0:0].copy()
    transfer_from, transfer_to, stock_movement = _build_transfers(ingredients)
    theoretical = _theoretical_consumption(sales, bom, ingredients)
    recipe_consumption = _build_recipe_consumption(sales, bom, ingredients)
    wastage = _build_wastage(theoretical)
    inventory_reports = _build_inventory_period_reports(
        theoretical,
        ingredients,
        entry,
        stock_return,
        bulk_return,
        transfer_from,
        transfer_to,
        wastage,
        po,
    )

    report_frames: dict[str, pd.DataFrame] = {
        "vendor_report": vendors.drop(columns=["row_id"], errors="ignore"),
        "bill_item_detail": bill,
        "bulk_return": bulk_return,
        "enterprise_consumption_detail": inventory_reports[
            "enterprise_consumption_detail"
        ],
        "enterprise_entry": entry,
        "enterprise_purchase_order": po,
        "enterprise_reorder": inventory_reports["enterprise_reorder"],
        "enterprise_stock_return": stock_return,
        "enterprise_transfer_from": transfer_from,
        "enterprise_transfer_to": transfer_to,
        "enterprise_variance_master": inventory_reports[
            "enterprise_variance_master"
        ],
        "enterprise_variance_normal": inventory_reports[
            "enterprise_variance_normal"
        ],
        "enterprise_wastage_normal": wastage,
        "gross_net_margin": margin,
        "item_recipe_report": item_recipe,
        "purchase_detail": purchase_detail,
        "recipe_consumption": recipe_consumption,
        "stock_in_stock_out": stock_movement,
        "enterprise_opening": inventory_reports["enterprise_opening"],
        "enterprise_physical": inventory_reports["enterprise_physical"],
        "closing_stock": inventory_reports["closing_stock"],
    }
    report_frames = _apply_observed_source_shape(report_frames)

    auxiliary_frames: dict[str, pd.DataFrame] = {}
    auxiliary_masters = _build_auxiliary_masters(ingredients, vendors)
    auxiliary_frames["AUX_Outlet_Master"] = auxiliary_masters[
        "AUX_Outlet_Master"
    ]
    forecast = _build_forecast(sales, menu)
    auxiliary_frames["AUX_Menu_Demand_Forecast"] = forecast
    theoretical_for_validation = theoretical.sort_values(
        ["_month_code", "_outlet_code", "item_code"]
    ).reset_index(drop=True)
    auxiliary_frames["AUX_Theoretical_Consumption"] = theoretical_for_validation
    auxiliary_frames["AUX_Expiry_Estimate"] = _build_expiry_estimate(
        report_frames["closing_stock"],
        theoretical_for_validation,
        auxiliary_masters["AUX_Item_Master"],
        purchase_detail,
    )
    vendor_price = _build_vendor_price(po, vendors)
    purchase_summary = _build_purchase_summary(purchase_detail)
    captured_frames = _captured_schema_exports(
        vendor_price, purchase_summary, inventory_reports, ingredients
    )

    manifest_rows = []
    for stem, contract in contracts.items():
        frame = report_frames[stem]
        file_count = 0
        if stem in STATIC_CONTRACTS:
            path = CONTROL_TOWER_DATA_DIR / "static" / f"{stem}.csv"
            _write_contract_csv(frame, contract, path)
            file_count = 1
        else:
            for month_code in MONTHS:
                for outlet in OUTLETS:
                    subset = frame[
                        (frame["_month_code"] == month_code)
                        & (frame["_outlet_code"] == outlet["outlet_code"])
                    ]
                    path = (
                        CONTROL_TOWER_DATA_DIR
                        / month_code
                        / stem
                        / f"{outlet['outlet_code']}_{stem}.csv"
                    )
                    _write_contract_csv(subset, contract, path)
                    file_count += 1

        consolidated = frame
        if stem in LATEST_SNAPSHOT_CONTRACTS:
            consolidated = frame[frame["_month_code"] == "month_03"]
        consolidated_path = CONTROL_TOWER_EXPORT_DIR / f"RAW_CT_{stem}.csv"
        _write_contract_csv(consolidated, contract, consolidated_path)
        normalized_path = (
            CONTROL_TOWER_EXPORT_DIR / "normalized" / f"RAWN_CT_{stem}.csv"
        )
        _write_normalized_landing_csv(consolidated, contract, normalized_path)
        manifest_rows.append(
            {
                "report_name": contract.display_name,
                "report_stem": stem,
                "report_id": contract.report_id,
                "contract_status": (
                    "validated_historical_abnah_contract"
                    if stem == "vendor_report"
                    else "validated_uat_csv_contract"
                ),
                "grain": contract.grain,
                "row_count": len(frame),
                "file_count": file_count,
                "exact_schema_file": consolidated_path.name,
                "zoho_import_file": f"normalized/{normalized_path.name}",
                "active_v2_import": "yes" if stem in ACTIVE_V2_REPORT_STEMS else "no",
                "active_v2_role": (
                    (
                        "qualified_master_source"
                        if stem == "vendor_report"
                        else "operational_source"
                    )
                    if stem in ACTIVE_V2_REPORT_STEMS
                    else (
                        "gated_unavailable"
                        if stem in OBSERVED_HEADER_ONLY_REPORTS
                        else "reconciliation_or_evidence_only"
                    )
                ),
            }
        )

    capture_columns = {
        "ERP_Vendor_Price": [
            "erp_doc_id",
            "vendor_id",
            "vendor_name",
            "outlet",
            "outlet_name",
            "status",
            "published",
            "received_on",
            "inserted_by",
            "comment",
            "updated_on",
            "item_id",
            "uom",
            "unit_price",
        ],
        "Enterprise_Purchase_Summary": [
            "deployment_name",
            "vendor_code",
            "vendor_name",
            "subtotal",
            "discount",
            "total_tax",
            "total",
        ],
        "Enterprise_Consolidated_Indent": [
            "supplier",
            "receiver",
            "supercategory",
            "category",
            "item_code",
            "item_name",
            "master_preferred_unit",
            "requested_qty",
            "requested_subtotal",
            "supplied_qty",
            "supplied_subtotal",
            "received_qty",
            "received_subtotal",
            "suspicious_qty",
            "suspicious_subtotal",
        ],
    }
    for name, (headers, frame) in captured_frames.items():
        columns = capture_columns[name]
        output = CONTROL_TOWER_EXPORT_DIR / f"SCHEMA_CAPTURE_CT_{name}.csv"
        _write_schema_capture_csv(frame, headers, columns, output)
        manifest_rows.append(
            {
                "report_name": name.replace("_", " "),
                "report_stem": name.lower(),
                "report_id": "",
                "contract_status": "schema_capture_only_pending_uat_csv_validation",
                "grain": "See Workbench schema blueprint",
                "row_count": len(frame),
                "file_count": 1,
                "exact_schema_file": output.name,
                "zoho_import_file": output.name,
                "active_v2_import": "no",
                "active_v2_role": "schema_capture_only",
            }
        )

    for name, frame in auxiliary_frames.items():
        output = CONTROL_TOWER_EXPORT_DIR / f"{name}.csv"
        export_frame = frame
        if name == "AUX_Theoretical_Consumption":
            export_frame = frame.rename(
                columns={
                    "_month_code": "source_period_code",
                    "_outlet_code": "outlet_code",
                }
            )
        export_frame.to_csv(output, index=False, encoding="utf-8-sig")
        if name == "AUX_Expiry_Estimate":
            contract_status = "synthetic_demo_batch_scenario"
            grain = (
                "One synthetic near-expiry FIFO tranche per period, outlet, "
                "item and batch allocation"
            )
            active_role = "demo_only_scenario"
        elif name == "AUX_Outlet_Master":
            contract_status = "synthetic_demo_reference"
            grain = "One synthetic reference row per demonstrator outlet"
            active_role = "demo_only_reference"
        else:
            contract_status = "approved_model_output"
            grain = "Model-defined; see the active import runbook"
            active_role = "approved_model_output"
        manifest_rows.append(
            {
                "report_name": name.replace("_", " "),
                "report_stem": name.lower(),
                "report_id": "",
                "contract_status": contract_status,
                "grain": grain,
                "row_count": len(export_frame),
                "file_count": 1,
                "exact_schema_file": output.name,
                "zoho_import_file": output.name,
                "active_v2_import": "yes"
                if name in ACTIVE_V2_MODEL_OUTPUTS
                else "no",
                "active_v2_role": active_role
                if name in ACTIVE_V2_MODEL_OUTPUTS
                else "scenario_only",
            }
        )

    manifest = pd.DataFrame(manifest_rows)
    manifest.to_csv(
        CONTROL_TOWER_EXPORT_DIR / "_CONTROL_TOWER_IMPORT_MANIFEST.csv",
        index=False,
        encoding="utf-8-sig",
    )
    manifest[manifest["active_v2_import"] == "yes"].to_csv(
        CONTROL_TOWER_EXPORT_DIR / "_CONTROL_TOWER_ACTIVE_IMPORT_MANIFEST.csv",
        index=False,
        encoding="utf-8-sig",
    )
    checks = _validate(report_frames, captured_frames, auxiliary_frames)
    pd.DataFrame(checks).to_csv(
        CONTROL_TOWER_EXPORT_DIR / "_RECONCILIATION_RESULTS.csv",
        index=False,
        encoding="utf-8-sig",
    )
    _write_validation_doc(report_frames, checks, contracts, manifest)
    failed = [check for check in checks if check["status"] != "PASS"]
    if failed:
        messages = "; ".join(
            f"{check['check_id']} observed={check['observed']}" for check in failed
        )
        raise RuntimeError(f"Control-tower synthetic validation failed: {messages}")

    return {
        "validated_reports": len(report_frames),
        "schema_capture_reports": len(captured_frames),
        "auxiliary_tables": len(auxiliary_frames),
        "source_rows": int(sum(len(frame) for frame in report_frames.values())),
        "reconciliation_checks": len(checks),
    }
