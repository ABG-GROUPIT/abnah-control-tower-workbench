#!/usr/bin/env python3
"""Import screenshot-derived schema notes and pasted headers into portable blueprints.

The input READMEs are local staging files. This importer writes only labels, semantic
keys, notes, and blank table structures. It never copies screenshots, paths, or rows.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


HEADING_RE = re.compile(r"^###\s+\d+\.\s+(.+?)\s*$")
FOLDER_RE = re.compile(r"^Known scaffold folder:\s+`([^`]+)`")
DATE_LABEL_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SOURCE_POLICY = "Schema definitions only. Local screenshots, paths, and source images are excluded."
FOLDER_ALIASES = {
    "Gross/Net Margin Report": "p2_reports/07_sales/33_food_sold_report",
}


@dataclass
class Capture:
    name: str
    folder: str
    headers: str = ""
    meaning: str = ""


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_") or "field"


def clean_text(value: str) -> str:
    replacements = {
        "\u00e2\u20ac\u201c": "-",
        "\u00e2\u20ac\u201d": "-",
        "\u00e2\u20ac\u2122": "'",
        "\u00c2": "",
    }
    text = value
    for source, replacement in replacements.items():
        text = text.replace(source, replacement)
    return "\n".join(line.rstrip() for line in text.splitlines()).strip()


def read_fence(lines: list[str], start: int) -> tuple[str, int]:
    index = start
    while index < len(lines) and lines[index].strip() != "```text":
        index += 1
    if index >= len(lines):
        return "", index
    index += 1
    captured: list[str] = []
    while index < len(lines) and lines[index].strip() != "```":
        captured.append(lines[index])
        index += 1
    return clean_text("\n".join(captured)), index


def parse_capture_readme(path: Path) -> list[Capture]:
    lines = path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    captures: list[Capture] = []
    current: Capture | None = None
    index = 0
    while index < len(lines):
        line = lines[index]
        heading = HEADING_RE.match(line)
        if heading:
            if current:
                captures.append(current)
            current = Capture(name=clean_text(heading.group(1)), folder="")
        elif current:
            folder_match = FOLDER_RE.match(line)
            if folder_match:
                raw_folder = clean_text(folder_match.group(1))
                current.folder = FOLDER_ALIASES.get(raw_folder, raw_folder)
            elif line.strip() == "CSV column headers exactly as exported:":
                current.headers, index = read_fence(lines, index + 1)
            elif line.strip() == "Important derived meaning or unclear columns:":
                current.meaning, index = read_fence(lines, index + 1)
        index += 1
    if current:
        captures.append(current)
    return captures


def infer_semantics(label: str) -> tuple[str, str]:
    lowered = label.lower()
    if "date" in lowered:
        return "date", "date"
    if "time" in lowered or "duration" in lowered:
        return "time", "time"
    if any(token in lowered for token in ("qty", "quantity", "count", "covers", "bills", "tickets")):
        return "measure", "integer"
    if any(
        token in lowered
        for token in (
            "amount",
            "subtotal",
            "total",
            "sales",
            "sale",
            "cost",
            "price",
            "rate",
            "discount",
            "tax",
            "margin",
            "variance",
            "contribution",
            "percent",
            "%",
            "round off",
            "revenue",
        )
    ):
        return "measure", "decimal"
    if any(token in lowered for token in ("number", " id", "id ", "code", "invoice", "transaction", "bill no", "po no")):
        return "document_identifier", "text"
    if any(
        token in lowered
        for token in (
            "name",
            "category",
            "section",
            "store",
            "deployment",
            "vendor",
            "supplier",
            "receiver",
            "source",
            "type",
            "status",
            "mode",
            "unit",
            "comment",
        )
    ):
        return "dimension", "text"
    return "unknown", "unknown"


def point(label: str, key: str | None = None, notes: str = "") -> dict[str, str]:
    semantic_role, data_type = infer_semantics(label)
    result = {
        "key": key or slug(label),
        "label": label,
        "semantic_role": semantic_role,
        "data_type": data_type,
    }
    if notes:
        result["notes"] = notes
    return result


def column(item: str | tuple[str, str] | dict[str, Any]) -> dict[str, Any]:
    if isinstance(item, dict):
        return dict(item)
    if isinstance(item, tuple):
        label, key = item
        return {"label": label, "key": key}
    label = item
    return {"label": label, "key": slug(label)}


def flat_block(
    block_id: str,
    name: str,
    labels: Iterable[str | tuple[str, str] | dict[str, Any]],
    *,
    kind: str = "flat_table",
) -> dict[str, Any]:
    return {"id": block_id, "name": name, "kind": kind, "columns": [column(item) for item in labels]}


def key_value_block(
    block_id: str,
    name: str,
    labels: Iterable[str | tuple[str, str]],
) -> dict[str, Any]:
    return {"id": block_id, "name": name, "kind": "key_value", "entries": [column(item) for item in labels]}


def matrix_block(
    block_id: str,
    name: str,
    groups: list[tuple[str, list[str | tuple[str, str]]]],
    value_columns: list[str | tuple[str, str]] | None = None,
) -> dict[str, Any]:
    values = value_columns or [
        ("Business Date (dynamic)", "business_date_value"),
        ("Period Total", "period_total"),
    ]
    return {
        "id": block_id,
        "name": name,
        "kind": "matrix",
        "row_headers": ["Section", "Metric"],
        "value_columns": [column(item) for item in values],
        "row_groups": [
            {"label": group, "metrics": [column(item) for item in metrics]}
            for group, metrics in groups
        ],
    }


def leaves(nodes: Iterable[dict[str, Any]]) -> Iterable[dict[str, Any]]:
    for node in nodes:
        children = node.get("children") or []
        if children:
            yield from leaves(children)
        else:
            yield node


def points_from_blocks(blocks: list[dict[str, Any]]) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    seen: set[str] = set()

    def add(label: str, key: str, notes: str = "") -> None:
        if key in seen:
            return
        seen.add(key)
        results.append(point(label, key, notes))

    for block in blocks:
        kind = block.get("kind")
        if kind in {"flat_table", "column_tree"}:
            for item in leaves(block.get("columns") or []):
                add(item.get("point_label") or item.get("label", ""), item.get("key") or slug(item.get("label", "")))
        elif kind == "key_value":
            for item in block.get("entries") or []:
                add(item.get("label", ""), item.get("key") or slug(item.get("label", "")))
        elif kind == "matrix":
            add("Business Date", "business_date")
            for group in block.get("row_groups") or []:
                for item in group.get("metrics") or []:
                    add(item.get("label", ""), item.get("key") or slug(item.get("label", "")))
            for item in leaves(block.get("value_columns") or []):
                add(item.get("point_label") or item.get("label", ""), item.get("key") or slug(item.get("label", "")))
    return results


def blueprint(
    folder: str,
    blocks: list[dict[str, Any]],
    *,
    layout_kind: str,
    notes: str,
    capture_method: str = "manual_visual_structure_review",
    additional_points: Iterable[dict[str, str]] = (),
) -> dict[str, Any]:
    data_points = points_from_blocks(blocks)
    seen = {item["key"] for item in data_points}
    for item in additional_points:
        if item["key"] not in seen:
            data_points.append(item)
            seen.add(item["key"])
    return {
        "report_id": "report:" + folder.replace("/", ":"),
        "schema_status": "captured",
        "verification_status": "reviewed",
        "layout_kind": layout_kind,
        "capture_method": capture_method,
        "source_policy": SOURCE_POLICY,
        "structure_notes": notes,
        "data_points": data_points,
        "blocks": blocks,
    }


def grouped(label: str, children: Iterable[str | tuple[str, str] | dict[str, Any]]) -> dict[str, Any]:
    return {"label": label, "children": [column(item) for item in children]}


def custom_blueprints() -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}

    def put(folder: str, blocks: list[dict[str, Any]], layout: str, notes: str, extra: Iterable[dict[str, str]] = ()) -> None:
        result[folder] = blueprint(folder, blocks, layout_kind=layout, notes=notes, additional_points=extra)

    put(
        "p2_reports/04_category_item/02_item_wise_enterprise_report",
        [
            flat_block(
                "primary",
                "Item sales by business date",
                [
                    "S.No.",
                    "Item",
                    "Tab Type",
                    grouped("Business Date (dynamic)", [("Qty", "business_date_qty"), ("Amt", "business_date_amount")]),
                    grouped("Total", [("Qty", "total_qty"), ("Amt", "total_amount")]),
                ],
                kind="column_tree",
            )
        ],
        "grouped_columns",
        "Business-date columns repeat dynamically across the selected period; each date and the final total contain quantity and amount children.",
        [point("Business Date", "business_date")],
    )
    put(
        "p2_reports/04_category_item/05_itemwise_consolidate",
        [
            flat_block(
                "primary",
                "Consolidated item sales",
                [
                    "Number", "Item Name", "Rate", "Qty", "Complimentary", "Non-Complimentary",
                    "Discount Amount", "Complimentary Amount", "Total Discount", "Net Amt",
                    "Total Tax", "Gross Amount", "Round Off", "G. Total",
                ],
            )
        ],
        "grouped_rows",
        "Rows are grouped by super category and category, with category and super-category total rows.",
        [point("Super Category", "super_category"), point("Category", "category")],
    )
    put(
        "p2_reports/04_category_item/06_section_category_wise_report",
        [flat_block("primary", "Section and category sales", ["Category", "Amount", "Quantity"])],
        "grouped_rows",
        "Category rows are nested under dynamic section headings and include section totals.",
        [point("Section", "section")],
    )
    put(
        "p2_reports/04_category_item/07_section_tabwise_sales_report",
        [flat_block("primary", "Section sales by tab", ["Tabs", "Sections", "Day Sale", "Month To Date"])],
        "grouped_rows",
        "Each tab expands into section rows and summary rows for revenue, bills, revenue per bill, covers, and revenue per cover.",
        [
            point("Total Revenue", "total_revenue"), point("Total Bills", "total_bills"),
            point("Average Revenue Per Bill", "average_revenue_per_bill"),
            point("Total Covers", "total_covers"),
            point("Average Revenue Per Cover", "average_revenue_per_cover"),
        ],
    )
    put(
        "p2_reports/04_category_item/09_menu_mix_report",
        [
            flat_block(
                "primary",
                "Menu mix",
                [
                    "Super Category", "Number", "Item Name", "Comp Qty", "Noncomp Qty",
                    "Number Sold", "Price Sold", "Amount", "Comp Amount", "Discount Amount",
                    "Total Discount", "Net Sales", "% Of Sales", "% Of Super Category",
                ],
            )
        ],
        "grouped_rows",
        "Item rows are grouped by super category and category with subtotal rows.",
        [point("Category", "category")],
    )
    put(
        "p2_reports/04_category_item/11_sessionwise_item_sale",
        [
            flat_block(
                "primary",
                "Item sales by session",
                ["Item Number", "Item Name", "Category", "Super Category", "Price Sold", "Number Sold", "Amount", "Discount", "Fixed Cost"],
            )
        ],
        "grouped_rows",
        "The same item table repeats for each dynamic day session and ends with a session total.",
        [point("Session", "session")],
    )
    put(
        "p2_reports/04_category_item/13_combo_report",
        [
            flat_block("combo", "Combo item", ["Number", "Name", "Category", "Quantity", "Subtotal", "Discount"]),
            flat_block(
                "constituents",
                "Constituent items",
                ["Item Number", "Item Name", "Item Category", "Item Quantity", "Item Subtotal", "Item Discount", "Applied Offer Weighted Discount", "Item Taxes"],
            ),
        ],
        "mixed",
        "Each combo item is followed by a separate constituent-item table.",
    )
    put(
        "p2_reports/04_category_item/15_addon_report",
        [
            flat_block("items", "Parent items", ["Item Number", "Item Name", "Item Quantity", "Item Subtotal", "Item Discount", "Item Taxes", "Cost Incurred", "Profit Per Item"]),
            flat_block("addons", "Addon items", ["Addon Number", "Addon Name", "Addon Quantity", "Addon Subtotal", "Addon Discount", "Addon Taxes", "Cost Incurred", "Profit Per Item"]),
        ],
        "mixed",
        "Each parent item is immediately followed by its addon-item table; the two grains must remain separate.",
    )
    put(
        "p2_reports/04_category_item/16_product_price_variation_report",
        [
            flat_block(
                "primary",
                "Product price variation",
                [
                    "Super Category", "Category", "Section", "Item Code", "Item Name",
                    grouped("A La Carte Sales", [("Qty Sold", "a_la_carte_qty_sold"), ("Price", "a_la_carte_price"), ("Taxes", "a_la_carte_taxes"), ("Discount", "a_la_carte_discount"), ("Net Sales", "a_la_carte_net_sales")]),
                    grouped("Combo Sales", [("Qty Sold", "combo_qty_sold"), ("MRP", "combo_mrp"), ("Price In Combo", "combo_price"), ("Taxes", "combo_taxes"), ("Discount", "combo_discount"), ("Net Sales", "combo_net_sales")]),
                    grouped("Sales Via Dynamic Price", [("Qty Sold", "dynamic_qty_sold"), ("MRP", "dynamic_mrp"), ("Dynamic Pricing", "dynamic_price"), ("Taxes", "dynamic_taxes"), ("Discount", "dynamic_discount"), ("Net Sales", "dynamic_net_sales")]),
                ],
                kind="column_tree",
            )
        ],
        "grouped_columns",
        "Measures are partitioned into a-la-carte, combo, and dynamic-price sales groups.",
    )

    put(
        "p2_reports/07_sales/01_payment_details_report",
        [
            flat_block(
                "primary",
                "Bill payment details",
                [
                    "Store ID", "Bill Number", "Advance Number", "Sync Time", "Open Time",
                    "Table Number", "Tab Name", "Tab Type", "Covers", "Print Time", "Close Time",
                    "Total Amount", "Discount", "Net Sales", "ECOM@5% Amount", "ECOM@5%", "GST@5% Amount",
                ],
            )
        ],
        "grouped_rows",
        "Bill rows are grouped by business date and end with a day-total row.",
        [point("Business Date", "business_date")],
    )
    put(
        "p2_reports/07_sales/04_taxation_sale_report",
        [
            matrix_block(
                "primary",
                "Taxation sale by date",
                [
                    ("Category sales", [("Category member", "category_member"), ("Net Sales", "net_sales")]),
                    ("Tax breakup", [("Tax rate row", "tax_rate_row"), ("Tax Breakup Total", "tax_breakup_total")]),
                    ("Charges", [("Charge row", "charge_row"), ("Charges Breakup Total", "charges_breakup_total")]),
                    ("Sales totals", ["Net Sales With Charges", "Gross Sales Without Round Off", "Round Off", "Gross Sales With Round Off"]),
                    ("Collection breakup", [("Payment mode row", "payment_mode_row"), "Total Collection"]),
                    ("Gross sales statistics", ["Covers", "Covers Excluding Complimentary", "Average Per Cover On Gross Sale", "Average Per Cover On Net Sale", "Cover Turn Ratio", "Number Of Bills", "Number Of Bills Excluding Complimentary", "Average Per Bill", "Average Per Bill Excluding Complimentary"]),
                ],
            )
        ],
        "matrix",
        "A dynamic date matrix combines category sales, tax, charge, collection, and gross-sales statistic sections with a final period total.",
    )
    put(
        "p2_reports/07_sales/05_category_wise_sales_report",
        [
            matrix_block(
                "primary",
                "Category-wise sales and collection",
                [
                    ("Category sales", [("Category member", "category_member"), ("Category total", "category_total")]),
                    ("Charges", [("Charge member", "charge_member"), ("Total Charges", "total_charges")]),
                    ("Collections", [("Payment mode member", "payment_mode_member"), ("Total Collection", "total_collection"), "Check"]),
                ],
                ["Total Sales", "Service Charge", "Discount", "GST@5%", "GST@18%", "GST@3%", "Gross Sales", "Net Sales", "Net Sales With Charges", "Complimentary"],
            )
        ],
        "matrix",
        "Each business date contains category, charge, collection, and reconciliation rows across the same sales measures.",
    )
    put(
        "p2_reports/07_sales/06_bill_item_detail_report",
        [
            flat_block(
                "primary",
                "Bill item detail",
                ["State", "Deployment", "Order Id", "Bill Number", "Day Serial", "Tab", "Table Number", "Open Time", "Close Time", "Category Name", "Item Name", "Item Number", "Item Section", "Item Classification", "Rate", "Qty", "Amount"],
            )
        ],
        "grouped_rows",
        "Rows are grouped by business date and bill, with a bill-total row after each bill.",
        [point("Business Date", "business_date")],
    )
    put(
        "p2_reports/07_sales/09_payments_breakup_report",
        [
            flat_block(
                "primary",
                "Payment and tax breakup",
                [
                    "Bill Number", "Bill Date", "Table Number", "Covers", "Sales Subtotal", "Discount",
                    grouped("Taxable Value", [("GST@5% Sales", "gst_5_sales"), ("GST@3% Sales", "gst_3_sales"), ("GST@18% Sales", "gst_18_sales")]),
                    "Total Taxable Sales",
                    grouped("Tax Value", [("GST@5% Amount", "gst_5_amount"), ("GST@3% Amount", "gst_3_amount"), ("GST@18% Amount", "gst_18_amount")]),
                    "Total Tax", "Non Taxable Sales", "Net Sales", "Gross Sales", "Round Off", "Grand Total",
                    grouped("Payments", [("Payment Cash", "payment_cash"), ("Payment Debitcard", "payment_debit_card"), ("Payment Creditcard", "payment_credit_card"), ("Payment Other", "payment_other"), ("Payment Coupon", "payment_coupon"), ("Payment BTC", "payment_btc"), ("Payment Smartcard", "payment_smart_card")]),
                    grouped("Types Of Advances", [("Advance Cash", "advance_cash"), ("Advance Credit Card", "advance_credit_card"), ("Advance Debit Card", "advance_debit_card")]),
                ],
                kind="column_tree",
            )
        ],
        "grouped_columns",
        "Taxable values, tax amounts, payments, and advance types are separate merged-header groups.",
    )
    put(
        "p2_reports/07_sales/10_btc_settlement_report",
        [
            key_value_block("summary", "BTC settlement summary", ["Payment Mode", "Payment Received", "Outstanding Amount"]),
            flat_block("detail", "BTC bill detail", ["Date", "Bill Number", "Bill Type", "Company Name", "Company Code", "Employee Name", "Employee Code", "Gross Amount", "Payment Status", "Payment Mode", "Payment Date", "Payment User", "Staff Meal Bill"]),
        ],
        "mixed",
        "A payment-mode summary precedes the bill-level BTC settlement detail.",
    )
    put(
        "p2_reports/07_sales/11_online_other_payment_detail_report",
        [flat_block("primary", "Online payment detail", ["Bill Number", "COD", "Online Payment", "Online-COD", "Transaction Number", "Order ID"])],
        "grouped_rows",
        "Rows are grouped first by online source and then by business date.",
        [point("Online Source", "online_source"), point("Business Date", "business_date")],
    )
    put(
        "p2_reports/07_sales/14_instance_wise_report",
        [flat_block("primary", "Instance-wise bill sales", ["Invoice Number", "Open Time", "Covers", "Total Amount", "Discount", "GST@5% Amount", "GST@5%", "GST@18% Amount", "GST@18%", "GST@3% Amount", "GST@3%", "Net Amount", "Round Off", "Gross Total", "Cash", "Others"])],
        "grouped_rows",
        "Bill rows are grouped by business date and POS instance.",
        [point("Business Date", "business_date"), point("Instance", "instance")],
    )
    put(
        "p2_reports/07_sales/16_daily_sales_report",
        [
            flat_block("session_sales", "Daily sales by session", ["Session", "Time Slot", "Sale Type", "Amount", "Gross Amount"]),
            key_value_block("grand_total", "Grand total", ["Total Beverage Sale", "Total Food Sale", "Total Sale", "Total Discount", "Total Charge Amount", "Total Source Amount", "Roundoff", "Total Gross", "Total Bills", "Total Covers", "Total APC"]),
            flat_block("collection", "Session-wise collection breakup", ["Session Name", "Mode", "Amount"]),
            flat_block("tax", "Session-wise tax breakup", ["Session Name", "Tax Name", "Rate", "Amount"]),
            flat_block("discount", "Session-wise discount breakup", ["Session Name", "Discount Name", "Discount Rate", "Discount Amount"]),
            flat_block("charge", "Session-wise charge breakup", ["Session Name", "Charge Name", "Charge Rate", "Charge Amount"]),
            flat_block("source", "Session-wise source breakup", ["Session Name", "Source Name", "Source Amount"]),
        ],
        "mixed",
        "The report is a seven-block daily pack: session sales, grand totals, collection, tax, discount, charge, and order-source breakups. Each repeating session block includes a session-total row.",
        [point("Session Covers", "session_covers"), point("Session Bills", "session_bills"), point("Session APC", "session_apc")],
    )
    put(
        "p2_reports/07_sales/17_daily_sales_summary_report",
        [
            flat_block("vat", "VAT breakup", ["VAT Break-Up", "Taxable Sale", "Service Charge", "Total", "VAT Amount"]),
            flat_block("service_tax", "Service tax breakup", ["Service Tax Break-Up", "Taxable Sale", "Service Charge", "Total", "Service Tax Amount"]),
            flat_block("gst", "GST breakup", ["GST Rate", "Taxable Sale", "Service Charge", "Total", "GST Amount"]),
            flat_block("tab", "Tab-wise breakup", ["Tab", "Taxable Sale", "Service Charge", "Total", "VAT", "GST", "Service Tax", "Charges"]),
            key_value_block("collection", "Collection breakup", ["Cash", "Credit Card", "Debit Card", "Coupon", "BTC", "TTR", "Smart Card", "Round Off", "Gross Sales"]),
            flat_block("credit_card", "Credit card breakup", ["Card Type", "Amount"]),
            flat_block("cash", "Cash breakup", ["Cash Type", "Amount"]),
            flat_block("tips", "Tips", ["Particular", "Count", "Amount"]),
            key_value_block("bill_counts", "Covers and bill counts", ["Cover", "No. Of HD/TA Bills", "Number Of Bills"]),
            flat_block("averages", "Average metrics", ["Metric", "On Gross Sale", "On Net Sale"]),
        ],
        "mixed",
        "A multi-block daily summary covers legacy tax sections, GST, tab totals, collections, tender subtypes, tips, counts, and gross/net averages.",
        [point("Gross Sales Without Round Off", "gross_sales_without_round_off")],
    )
    put(
        "p2_reports/07_sales/18_day_wise_sales_report",
        [
            matrix_block(
                "primary",
                "Day-wise sales matrix",
                [
                    ("Covers", ["Breakfast Cover", "Lunch Cover", "High Tea Cover", "Dinner Cover", "Extended Hours Cover", "NA Cover", "Total Covers"]),
                    ("Session-section net sales", ["Session Net Food Sales", "Session Net Beverage Sales", "Session Net Merchandise GST 18% Sales", "Session Net Merchandise GST 3% Sales", "Session Net Merchandise GST 0% Sales", "Session Net Merchandise GST 5% Sales"]),
                    ("Session-section APC", ["Session APC Food", "Session APC Beverage", "Session APC Merchandise GST 18%", "Session APC Merchandise GST 3%", "Session APC Merchandise GST 0%", "Session APC Merchandise GST 5%"]),
                    ("Session totals", ["Breakfast Sale", "Lunch Sale", "High Tea Sale", "Dinner Sale", "Extended Hours Sale", "NA Sale", "Breakfast APC", "Lunch APC", "High Tea APC", "Dinner APC", "Extended Hours APC", "NA APC"]),
                    ("Section totals", ["Food Sale", "Beverage Sale", "Merchandise GST 18% Sale", "Merchandise GST 3% Sale", "Merchandise GST 0% Sale", "Merchandise GST 5% Sale", "Food APC", "Beverage APC", "Merchandise GST 18% APC", "Merchandise GST 3% APC", "Merchandise GST 0% APC", "Merchandise GST 5% APC"]),
                    ("Daily summary", ["Net Sales", "Number Of Bills", "Number Of Tables", "Average Net Sale"]),
                    ("Month to date", ["Breakfast MTD Net Sale", "Lunch MTD Net Sale", "High Tea MTD Net Sale", "Dinner MTD Net Sale", "Extended Hours MTD Net Sale", "NA MTD Net Sale", "MTD Net Sale", "MTD Total Avg Sale"]),
                    ("Taxes", ["GST@5%", "GST@18%", "GST@3%", "Total Tax Amount"]),
                    ("Delivery", ["Delivery Net Amount", "Delivery MTD Amount", "Delivery Taxes", "Delivery Total Tax Amount"]),
                    ("Takeout", ["Takeout Net Amount", "Takeout MTD Amount", "Takeout Taxes", "Takeout GST@5%", "Takeout GST@18%", "Takeout Total Tax Amount"]),
                ],
                [("Business Date (dynamic)", "business_date_value")],
            )
        ],
        "matrix",
        "Dates are dynamic columns with a weekday subheader. Rows form several measure bands covering sessions, sections, APC, MTD, tax, delivery, and takeout.",
    )
    put(
        "p2_reports/07_sales/19_daily_sales_report_detailed",
        [
            key_value_block("revenue", "Revenue and discounts", ["Net Sales", "Charge Total", "Service Charge", "Product Level Charges", "Tax Collected", "Round Off", "Total Revenue", "Item Discount", "Subtotal Discount", "Total Discounts", "Total Discounts Complimentary", "Total Discounts Non-Complimentary"]),
            key_value_block("voids", "Void summary", ["Voids", "Manager Voids", "Other Voids"]),
            flat_block("order_type", "Order type performance", ["Order Type", "Net Sales", "% Of Total Sales", "Guest", "% Of Total Guests", "Avg/Guest", "Checks", "% Of Total Checks", "Avg/Check", "Tables", "% Of Total Tables", "Avg/Table", "Turn Time (Min.)"]),
            flat_block("order_source", "Order source performance", ["Order Source", "Net Sales", "% Of Total Sales", "Guest", "% Of Total Guests", "Avg/Guest", "Checks", "% Of Total Checks", "Avg/Check", "Tables", "% Of Total Tables", "Avg/Table", "Turn Time (Min.)"]),
            flat_block("section", "Section tracking", ["Particulars", "Items", "Amount"]),
            flat_block("super_category", "Super category tracking", ["Particulars", "Items", "Amount"]),
            flat_block("collection", "Collection breakup", ["Particulars", "Bills", "Amount"]),
            flat_block("discounts", "Discounts", ["Particulars", "Count", "Amount"]),
            flat_block("taxes", "Taxes tracking", ["Particulars", "Taxable Amount", "Amount"]),
            flat_block("bills_covers", "Bills and covers", ["Particulars", "Bills", "Covers", "KOTs (Settled Bills)"]),
            flat_block("bill_void", "Bill void segregation", ["Type", "Count", "Amount"]),
        ],
        "mixed",
        "The detailed report is a dashboard-style pack of revenue, void, order, section, tender, discount, tax, bill, and cover structures rather than one rectangular export.",
        [point("Deployment", "deployment"), point("Period From", "period_from"), point("Period To", "period_to"), point("Tips Count", "tips_count"), point("Tips Amount", "tips_amount")],
    )
    day_close_measure_groups = [
        grouped("Sale By Dimension", ["Total Sales", "Discount", "Total Charges", "Tax Excluded Sales", "Total Tax", "Round Off", "Gross Sales", "No. Of Bills", "Average Per Bill", "No. Of Covers", "Average Cover", "Order %", "Sale %"]),
        grouped("Payment", ["Cash", "Online", "Visa"]),
        grouped("Voids & Cancellations", [("No. Of Bills", "void_bill_count"), ("Amount", "void_amount")]),
    ]
    put(
        "p2_reports/07_sales/20_day_closing_report",
        [
            key_value_block("sale_summary", "Sale summary", ["Total Sales", "Discount", "Tax", "Net Sales", "Total With Charges", "Round Off", "Gross Sales"]),
            flat_block("order_type", "Order type analysis", ["Tab Name", *day_close_measure_groups], kind="column_tree"),
            flat_block("source", "Source analysis", ["Source", *day_close_measure_groups], kind="column_tree"),
            flat_block("coupon_btc", "Coupon and BTC", ["Name", "No. Of Bills", "Amount"]),
            flat_block("offers", "Offers and complimentary", ["Name", "No. Of Bills", "Amount"]),
        ],
        "mixed",
        "A period sale summary is followed by parallel order-type and source analyses, then coupon/BTC and offer/complimentary tables.",
        [point("Deployment", "deployment"), point("Period From", "period_from"), point("Period To", "period_to")],
    )
    source_summary_columns = [
        "Deployment", "Date",
        grouped("POS", ["Net Sales", "Orders", "Cancel Orders", "% Vs Total Sales"]),
        grouped("Total Sale", [("Total Sale", "overall_total_sale"), ("Total Order", "overall_total_order")]),
    ]
    source_detail_columns = [
        "Brand", "Format", "Cluster", "Deployment Name", "State", "City", "Tab Name",
        "Source Order No.", "Source Order Date", "Invoice Number", "Invoice Date", "Source",
        "Section", "Super Category", "Category", "Item Name", "Quantity", "HSN/SAC Code",
        "Rate", "Amount", "Discount", "Net Amount", "Total", "Status", "Payment Via",
        "Delivered Via", "Order Time", "Source Sync Time", "Accept Time", "Reject Time",
        "Mark Food Ready Time", "Food Preparation Time", "Bill Print Time", "Dispatch Time",
        "Delivered Time", "Settle Time",
    ]
    put(
        "p2_reports/07_sales/24_source_wise_analysis_report",
        [
            flat_block("summary", "Source analysis summary", source_summary_columns, kind="column_tree"),
            flat_block("detail_export", "Source-wise detailed export", source_detail_columns),
        ],
        "mixed",
        "The visible report is a deployment/date summary with POS and total-sale groups. The export also exposes a richer source-order and item-level detail schema; both grains are retained separately.",
    )
    put(
        "p2_reports/07_sales/25_bill_no_wise_report",
        [
            key_value_block(
                "primary",
                "Bill-wise summary fields",
                [
                    "Deployment", "Bill Number", "Advance Number", "Order Id", "Bill Date", "Bill Open Time", "Print Time", "Close Time", "Tab Name", "Table Number", "Covers", "Sales", "Discount", "Net Sales", "Gross Bill Amount", "Packaging Charge [CART - SWIGGY]", "Restaurant Packaging Charges",
                    ("BEVERAGE", "beverage_sales"), ("CGST", "beverage_cgst"), ("SGST", "beverage_sgst"),
                    ("FOOD", "food_sales"), ("CGST", "food_cgst"), ("SGST", "food_sgst"),
                    "Total Service Charge", "Round Off", "Cash", "Credit Card", "Debit Card", "Coupon", "BTC", "TTR", "Smart Card", "Swiggy", "Zomato", "Tip Amount", "Offer Code", "Electronic Bill",
                ],
            )
        ],
        "key_value",
        "The captured field list was repeated twice in the staging text. One structural sequence is retained; beverage and food CGST/SGST positions use contextual keys rather than being collapsed.",
    )
    put(
        "p2_reports/07_sales/31_online_orders_report",
        [
            flat_block(
                "primary",
                "Online order detail",
                [
                    "Date", "Bill Number", "Time", "Outlet Name", "Order ID", "Order Status", "Order Type", "Tab Type", "Order Source", "Customer Name", "Customer Address", "Customer Phone",
                    grouped("Ordered Items", ["Item", "Rate", "Quantity", "Subtotal", "Category", "Super Category", "Comment"]),
                    "Total Discount Amount", "Amount", "Restaurant Packaging Charges", "Packaging Charge [CART - SWIGGY]", "Net Amount", "Round Off", "G Total", "Payment Mode", "Executive Name", "Delivery Rider Name", "Delivery Boy Mobile",
                ],
                kind="column_tree",
            )
        ],
        "grouped_columns",
        "Order-level context is followed by an Ordered Items group and payment/delivery fields. The export can repeat order context for item lines.",
    )
    put(
        "p2_reports/07_sales/38_daily_sales_reversal",
        [flat_block("primary", "Daily sales revenue", ["Particulars", "Session", "Section", ("Business Date (dynamic)", "business_date_value"), "Total"])],
        "matrix",
        "The source screen is Daily Sales Revenue despite the legacy catalogue label. Rows cover sales, covers, bills, cover turn, APC, APT, and contribution; the selected business date is a dynamic value column.",
        [point("Business Date", "business_date"), point("Sales", "sales"), point("Covers", "covers"), point("Bills", "bills"), point("Covers Turn", "covers_turn"), point("APC", "apc"), point("APT", "apt"), point("Contribution", "contribution"), point("Contribution %", "contribution_percent")],
    )
    put(
        "p2_reports/07_sales/39_day_wise_revenue_report",
        [
            matrix_block(
                "primary",
                "Day-wise revenue",
                [
                    ("Session and channel revenue", ["Dine In Sale", "Dine In Consolidated Sale", "Dine In Covers", "Dine In Bills", "Ecom Sale", "Ecom Consolidated Sale", "Ecom Covers", "Ecom Bills", "Online-Payment Sales", "Online-Payment Bills", "QR Code Sale", "QR Code Consolidated Sale", "QR Code Covers", "QR Code Bills", "Takeaway Sale", "Takeaway Consolidated Sale", "Takeaway Covers", "Takeaway Bills", "Cover Turns"]),
                    ("APT", ["NA APT", "Breakfast APT", "Lunch APT", "High Tea APT", "Dinner APT", "Extended Hours APT", "Total APT"]),
                    ("Transactions", ["NA Transaction", "Breakfast Transaction", "Lunch Transaction", "High Tea Transaction", "Dinner Transaction", "Extended Hours Transaction", "Total Transaction"]),
                    ("Contribution", ["NA Amount", "NA Count", "NA To Covers", "Contribution %"]),
                ],
                [("Business Date (dynamic)", "business_date_value")],
            )
        ],
        "matrix",
        "Business dates and weekdays are dynamic columns. Revenue rows repeat by session and order channel, followed by APT, transaction, and contribution bands.",
    )

    po_columns = [
        "Deployment", "Store Name", "Vendor Name", "PO Number", "PR Number", "PR Deployment",
        "PO Date", "Expected Delivery", "PO Close Date/Partial Recieve Date", "PO Status",
        "Item Code", "Item Name", "Item Brand", "Category Name", "Super Category Name",
        "Comment", "Total Processed Qty", "Remaining Balance Qty", "Quantity", "Unit", "Unit Price",
        "Subtotal", "Item Wise Discount Amount", "Bill Wise Discount Amount", "New Subtotal", "Tax", "Total Item Cost",
    ]
    movement_groups = [
        grouped("Opening", [("Date", "opening_date"), ("Qty", "opening_qty"), ("Unit", "opening_unit"), ("Amt", "opening_amount")]),
        grouped("Purchase", [("Qty", "purchase_qty"), ("Amt", "purchase_amount")]),
        grouped("Indent Receive", [("Qty", "indent_receive_qty"), ("Amt", "indent_receive_amount")]),
        grouped("Indent Dispatch", [("Qty", "indent_dispatch_qty"), ("Amt", "indent_dispatch_amount")]),
        grouped("Internal Indent Receive", [("Qty", "internal_indent_receive_qty"), ("Amt", "internal_indent_receive_amount")]),
        grouped("Internal Indent Dispatch", [("Qty", "internal_indent_dispatch_qty"), ("Amt", "internal_indent_dispatch_amount")]),
        grouped("Stock In", [("Qty", "stock_in_qty"), ("Amt", "stock_in_amount")]),
        grouped("Consumption", [("Qty", "consumption_qty"), ("Amt", "consumption_amount")]),
        grouped("Yield Wastage", [("Qty", "yield_wastage_qty"), ("Amt", "yield_wastage_amount")]),
        grouped("Stock Out", [("Qty", "stock_out_qty"), ("Amt", "stock_out_amount")]),
        grouped("Total (Stock Out + Consumption Qty)", [("Qty", "stock_out_plus_consumption_qty"), ("Amt", "stock_out_plus_consumption_amount")]),
        grouped("Wastage", [("Qty", "wastage_qty"), ("Amt", "wastage_amount")]),
        grouped("Reuse", [("Qty", "reuse_qty"), ("Amt", "reuse_amount")]),
        grouped("Return", [("Qty", "return_qty"), ("Amt", "return_amount")]),
        grouped("Closing", [("Date", "closing_date"), ("Qty", "closing_qty"), ("Amt", "closing_amount")]),
        grouped("Physical Gain/Loss", [("Qty", "physical_gain_loss_qty"), ("Amt", "physical_gain_loss_amount")]),
        grouped("Ideal Closing", [("Qty", "ideal_closing_qty"), ("Amt", "ideal_closing_amount")]),
        grouped("Physical Adjusted Closing", [("Qty", "physical_adjusted_closing_qty"), ("Amt", "physical_adjusted_closing_amount")]),
    ]
    put(
        "p4_stock_admin/01_enterprise_reports/04_enterprise_consumption",
        [
            flat_block(
                "primary",
                "Enterprise consumption lifecycle",
                ["Deployment Name", "StoreKitchen Name", "Item Code", "Item Name", "Category Name", "Super Category Name", "Average Price", *movement_groups],
                kind="column_tree",
            )
        ],
        "grouped_columns",
        "Repeated Amt headers are positionally paired with their movement quantity or checkpoint. Yield Wastage is retained as a source field label and is not treated as the Page 3 KPI terminology. Pairing must be checked again against the CSV export.",
    )
    put(
        "p4_stock_admin/01_enterprise_reports/06_enterprise_purchase_order",
        [flat_block("primary", "Enterprise purchase order lines", po_columns)],
        "flat",
        "The enterprise PO schema is captured, but the ABNAH UAT result was empty. It is retained for comparison only; the operational Purchase Order report is the planned authority unless populated evidence proves otherwise.",
    )
    put(
        "p4_stock_admin/03_po_so_reports/01_purchase_order",
        [flat_block("primary", "Purchase order lines", po_columns)],
        "flat",
        "This operational Purchase Order export has the same captured line schema as Enterprise Purchase Order and is the current planned PO authority because the enterprise result was empty.",
    )
    put(
        "p4_stock_admin/01_enterprise_reports/07_enterprise_consolidated_indent",
        [
            flat_block(
                "primary",
                "Enterprise consolidated indent",
                [
                    "Supplier", "Receiver", "SuperCategory", "Category", "Item Code", "Item Name", "Master Preferred Unit",
                    grouped("Requested", [("Qty", "requested_qty"), ("Subtotal", "requested_subtotal")]),
                    grouped("Supplied", [("Qty", "supplied_qty"), ("Subtotal", "supplied_subtotal")]),
                    grouped("Received", [("Qty", "received_qty"), ("Subtotal", "received_subtotal")]),
                    grouped("Suspicious", [("Qty", "suspicious_qty"), ("Subtotal", "suspicious_subtotal")]),
                ],
                kind="column_tree",
            )
        ],
        "grouped_columns",
        "Repeated Subtotal headers are positionally paired with requested, supplied, received, and suspicious quantities.",
    )
    normal_variance = [
        "Item Id", "Item Code", "Item Name", "Category Name", "Super Category Name", "Opening Date", "Opening Qty", "Unit", "Opening Amt",
        "Purchase Qty", "Purchase Amt", "Stock In Qty", "Stock In Amt", "Consumption Qty", "Consumption Amt", "Yield Wastage", "Yield Wastage Amt",
        "Stock Out Qty", "Stock Out Amt", "Total (Stock Out + Consumption Qty)", "Total (Stock Out + Consumption Qty) Amt", "Wastage Qty", "Wastage Amt",
        "Reuse Qty", "Reuse Amt", "Return Qty", "Return Amt", "Closing Date", "Closing Qty", "Closing Amt", "Physical Qty", "Physical Amt",
        "Variance Qty", "Variance Amt", "Variance Percent", "PhysicalGain/Loss Qty", "PhysicalGain/Loss Amt", "Actual Consumption", "Actual Consumption Amt",
    ]
    master_variance = [
        "Deployment", "Store/Kitchen", "Category", "Item Type", "Is Asset", "Item Name", "Unit", "Price", "Opening Qty", "Opening Amt",
        "Purchase Qty", "Purchase Amt", "Production Qty", "Production Amt", "Consumption Qty", "Consumption Amt", "Stock In Qty", "Stock In Amt",
        "Stock Out Qty", "Stock Out Amt", "Wastage Qty", "Wastage Amt", "Resue Qty", "Reuse Amt", "Return Qty", "Return Amt", "Closing Qty", "Closing Amt",
        "Physical Qty", "Physical Amt", "Variance Qty", "Variance Amt", "Physical Gain/Loss Qty", "Physical Gain/Loss Amt", "Actual Consumption Qty",
        "Actual Consumption Amt", "Physical Adjusted Closing Qty", "Physical Adjusted Closing Amt",
    ]
    put(
        "p4_stock_admin/01_enterprise_reports/08_enterprise_variance",
        [flat_block("normal", "Normal variance", normal_variance), flat_block("master", "Master variance", master_variance)],
        "mixed",
        "Normal and Master are distinct report modes with different grains. Source spelling, including Resue, is preserved; mode fields are not merged into one assumed table.",
    )
    put(
        "p4_stock_admin/01_enterprise_reports/12_enterprise_wastage_report",
        [
            flat_block(
                "normal",
                "Normal wastage",
                [
                    "Deployment Name", "Store Kitchen Name", "Item Code", "Item Name", "Category Name", "Super Category Name", "Unit", "Average Price",
                    grouped("Stock Wastage", [("Qty", "stock_wastage_qty"), ("Amt", "stock_wastage_amount")]),
                    grouped("Consumption", [("Qty", "consumption_qty"), ("Amt", "consumption_amount")]),
                    grouped("Billing Wastage", [("Qty", "billing_wastage_qty"), ("Amt", "billing_wastage_amount")]),
                    grouped("Total Wastage", [("Qty", "total_wastage_qty"), ("Amt", "total_wastage_amount")]),
                    "Percentage Wastage",
                ],
                kind="column_tree",
            ),
            flat_block("master", "Master wastage", ["Deployment", "Store/Kitchen", "Category", "Opening", "Stock In", "Total Stock", "Wastage", "Wastage Percentage"]),
        ],
        "mixed",
        "Normal wastage is item-level with paired quantity and amount groups; Master wastage is a separate higher-level summary mode.",
    )
    food_cost_columns = [
        column("Deployment Name"),
        column("Recipe Cost"),
        {"label": "Wastage Cost", "key": "wastage_cost_position_1", "point_label": "Wastage Cost (position 1)"},
        column("Ideal Cost"), column("Ideal Percent"),
        {"label": "Wastage Cost", "key": "wastage_cost_position_2", "point_label": "Wastage Cost (position 2)"},
        column("Cost Through Physical Entry (Gain /Loss)"), column("Actual Cost"), column("Actual Percent"), column("Total Sale"),
    ]
    put(
        "p4_stock_admin/01_enterprise_reports/15_enterprise_food_cost_report",
        [flat_block("primary", "Enterprise food cost", food_cost_columns)],
        "flat",
        "Wastage Cost appears twice in the captured sequence. Both positions are retained with separate keys; their exact business distinction remains a CSV/value-validation question.",
    )
    put(
        "p4_stock_admin/02_transactional_reports/01_entry_report",
        [
            flat_block(
                "primary",
                "Stock entry item lines",
                ["Item Code", "Item Name", "Quantity", "Unit", "Unit Price", "Amount", "Discount", grouped("GST Tax", [("CGST Tax", "cgst_tax"), ("SGST Tax", "sgst_tax")]), "IGST Tax", "Non GST Tax", "Total"],
                kind="column_tree",
            )
        ],
        "grouped_columns",
        "The line table uses a merged GST Tax header over CGST and SGST. A footer carries charge, tax-on-charge, amount, discount, tax, and grand-total values.",
        [point("Total Charge", "total_charge"), point("Total Tax On Charge", "total_tax_on_charge")],
    )
    put(
        "p4_stock_admin/02_transactional_reports/02_entry_sync_report",
        [flat_block("primary", "Entry synchronization audit", ["#", "Temp Number", "Transaction Number", "Transaction Date", "Sync Date", "Current User", "Back Date Transaction", "Is Edited", "Is Direct Issue", "History", "Invoice"])],
        "flat",
        "Entry synchronization audit rows include transaction flags, history access, and an invoice attachment indicator; attachment content is not retained.",
    )
    put(
        "p4_stock_admin/02_transactional_reports/10_stock_in_stock_out_report",
        [
            flat_block(
                "primary",
                "Stock in and stock out",
                [
                    "Date", "Store/Kitchen", "Supplier", "Receiver", "Item Name", "Unit", "Unit Price",
                    grouped("Stock In", [("Reference", "stock_in_reference"), ("Qty", "stock_in_qty"), ("Subtotal", "stock_in_subtotal")]),
                    grouped("Stock Out", [("Reference", "stock_out_reference"), ("Qty", "stock_out_qty"), ("Subtotal", "stock_out_subtotal")]),
                ],
                kind="column_tree",
            )
        ],
        "grouped_columns",
        "Repeated Subtotal fields are positionally paired with the Stock In and Stock Out movement groups.",
    )
    consumption_main = [
        grouped("Item", ["Deployment Name", "Item Code", "Item Name", "Category Name", "Unit", "Supercategory Name", "Average Price"]),
        grouped("Opening", [("Date", "opening_date"), ("Qty", "opening_qty"), ("Amount", "opening_amount")]),
        grouped("Purchase", [("Qty", "purchase_qty"), ("Amount", "purchase_amount")]),
        grouped("Stock In", [("Qty", "stock_in_qty"), ("Amount", "stock_in_amount")]),
        grouped("Consumption", [("Qty", "consumption_qty"), ("Amount", "consumption_amount")]),
        grouped("Stock Out", [("Qty", "stock_out_qty"), ("Amount", "stock_out_amount")]),
        grouped("Amount (Stock Out + Consumption)", [("Qty", "stock_out_plus_consumption_qty"), ("Amount", "stock_out_plus_consumption_amount")]),
        grouped("Wastage", [("Qty", "wastage_qty"), ("Amount", "wastage_amount"), ("percent", "wastage_percent")]),
        grouped("Reuse", [("Qty", "reuse_qty"), ("Amount", "reuse_amount")]),
        grouped("Return", [("Qty", "return_qty"), ("Amount", "return_amount")]),
        grouped("Closing", [("Date", "closing_date"), ("Qty", "closing_qty"), ("Amount", "closing_amount")]),
        grouped("Physical Gain/Loss", [("Qty", "physical_gain_loss_qty"), ("Amount", "physical_gain_loss_amount")]),
        grouped("Ideal Closing", [("Qty", "ideal_closing_qty"), ("Amount", "ideal_closing_amount")]),
        grouped("Physical adjusted Closing", [("Qty", "physical_adjusted_closing_qty"), ("Amount", "physical_adjusted_closing_amount")]),
    ]
    unit_consumption = [
        grouped("Store Kitchen", ["Store Kitchen Name"]),
        grouped("Item", ["Item Code", "Item Name", "Category Name", "Average Price"]),
        grouped("Opening", [("Date", "unit_opening_date"), ("Qty", "unit_opening_qty"), ("Unit Name", "unit_name"), ("Amt", "unit_opening_amount")]),
        grouped("Purchase", [("Qty", "unit_purchase_qty"), ("Amt", "unit_purchase_amount")]),
        grouped("Stock In", [("Qty", "unit_stock_in_qty"), ("Amt", "unit_stock_in_amount")]),
        grouped("Internal Indent Received", [("Qty", "unit_internal_indent_received_qty"), ("Amt", "unit_internal_indent_received_amount")]),
        grouped("Indent Received", [("Qty", "unit_indent_received_qty"), ("Amt", "unit_indent_received_amount")]),
        grouped("Stock Out", [("Qty", "unit_stock_out_qty"), ("Amt", "unit_stock_out_amount")]),
        grouped("Internal Indent Dispatched", [("Qty", "unit_internal_indent_dispatched_qty"), ("Amt", "unit_internal_indent_dispatched_amount")]),
        grouped("Indent Dispatched", [("Qty", "unit_indent_dispatched_qty"), ("Amt", "unit_indent_dispatched_amount")]),
        grouped("Wastage", [("Qty", "unit_wastage_qty"), ("Amt", "unit_wastage_amount"), ("percent", "unit_wastage_percent")]),
        grouped("Reuse", [("Qty", "unit_reuse_qty"), ("Amt", "unit_reuse_amount")]),
        grouped("Return", [("Qty", "unit_return_qty"), ("Amt", "unit_return_amount")]),
        grouped("Ideal Closing", [("Qty", "unit_ideal_closing_qty"), ("Amt", "unit_ideal_closing_amount")]),
        grouped("System Closing", [("Date", "unit_system_closing_date"), ("Qty", "unit_system_closing_qty"), ("Amt", "unit_system_closing_amount")]),
        grouped("Physical", [("Qty", "unit_physical_qty"), ("Amt", "unit_physical_amount")]),
        grouped("Consumption as Physical", [("Qty", "consumption_as_physical_qty"), ("Amt", "consumption_as_physical_amount")]),
        grouped("Consumption Via Recipe", [("Qty", "consumption_via_recipe_qty"), ("Amt", "consumption_via_recipe_amount")]),
        grouped("Variance", [("Qty", "unit_variance_qty"), ("Amt", "unit_variance_amount"), ("percent", "unit_variance_percent")]),
        grouped("Physical Gain/Loss", [("Qty", "unit_physical_gain_loss_qty"), ("Amt", "unit_physical_gain_loss_amount")]),
    ]
    put(
        "p4_stock_admin/05_aggregation_reports/02_consumption_report",
        [
            flat_block("consumption", "Consumption Report", consumption_main, kind="column_tree"),
            flat_block("slow_moving", "Slow Moving Report", [grouped("Item", ["Item Code", "Item Name", "Category Name", "Average Price"]), grouped("Consumption", [("Qty", "slow_consumption_qty"), ("Unit", "slow_consumption_unit"), ("Amount", "slow_consumption_amount")])], kind="column_tree"),
            flat_block("unit_consumption", "Unit Consumption Report", unit_consumption, kind="column_tree"),
            flat_block("cost_consumption", "Cost Of Consumption Report", [grouped("Item", ["Item Code", "Item Name", "Category Name", "Average Price"]), grouped("Consumption", [("Qty", "cost_consumption_qty"), ("Unit", "cost_consumption_unit"), ("Amount", "cost_consumption_amount")])], kind="column_tree"),
        ],
        "mixed",
        "One report page exposes four distinct modes: Consumption, Slow Moving, Unit Consumption, and Cost Of Consumption. Their grains and movement groups are retained as separate blank tables; repeated Qty/Amt labels use mode- and movement-specific keys.",
    )

    return result


def normalized_generic_labels(header_text: str) -> list[str]:
    candidates: list[list[str]] = []
    for raw_line in header_text.splitlines():
        line = raw_line.strip()
        if not line or "\t" not in line:
            continue
        if ":" in line.split("\t", 1)[0]:
            line = line.split(":", 1)[1].lstrip()
        labels = [clean_text(item).strip() for item in line.split("\t") if clean_text(item).strip()]
        if len(labels) > 1:
            candidates.append(labels)
    if not candidates:
        return []
    labels = max(candidates, key=len)
    return ["Business Date (dynamic)" if DATE_LABEL_RE.fullmatch(label) else label for label in labels]


def generic_blueprint(capture: Capture) -> dict[str, Any] | None:
    labels = normalized_generic_labels(capture.headers)
    if not labels:
        return None
    unique_columns: list[dict[str, Any]] = []
    counts: dict[str, int] = {}
    for label in labels:
        base = slug(label)
        counts[base] = counts.get(base, 0) + 1
        key = base if counts[base] == 1 else f"{base}_{counts[base]}"
        unique_columns.append({"label": label, "key": key})
    notes = "Exact exported header order captured from the local schema staging README."
    if capture.meaning:
        notes += " " + capture.meaning
    return blueprint(
        capture.folder,
        [flat_block("primary", f"{capture.name} export", unique_columns)],
        layout_kind="flat",
        notes=notes,
        capture_method="pasted_export_headers",
    )


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def known_report_folders(root: Path) -> set[str]:
    path = root / "schema-pack" / "source" / "catalog" / "reports.csv"
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return {row.get("report_folder", "") for row in csv.DictReader(handle)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p2", type=Path, help="Local P2 schema capture README")
    parser.add_argument("--p4", type=Path, help="Local P4 schema capture README")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--overwrite-existing", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    known = known_report_folders(root)
    custom = custom_blueprints()
    captures: dict[str, Capture] = {}
    for path in (args.p2, args.p4):
        if path:
            for capture in parse_capture_readme(path.resolve()):
                if capture.folder:
                    captures[capture.folder] = capture

    unknown = sorted((set(captures) | set(custom)) - known)
    if unknown:
        raise ValueError(f"Capture input references unknown report folders: {unknown}")

    source_root = root / "schema-pack" / "source" / "report_structures"
    written: list[str] = []
    skipped: list[str] = []
    for folder in sorted(set(captures) | set(custom)):
        payload = custom.get(folder)
        if payload is None:
            payload = generic_blueprint(captures[folder])
        if payload is None:
            continue
        destination = source_root / f"{folder}.json"
        if destination.exists() and not args.overwrite_existing:
            skipped.append(folder)
            continue
        write_json(destination, payload)
        written.append(folder)

    print(f"Schema capture import complete: {len(written)} written, {len(skipped)} existing blueprints preserved.")
    for folder in written:
        print(f"+ {folder}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
