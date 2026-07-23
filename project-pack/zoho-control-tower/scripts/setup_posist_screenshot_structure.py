"""Create the structured POSist screenshot dump folders for Codex intake.

This script creates an operator-friendly folder scaffold under:

    source_intake/posist_uat/_incoming_drop/posist_ss/

The generated folders are intentionally ignored by git. They are a local
workspace where screenshots, exports, and notes can be dropped during UAT.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


REPORT_SLOT_DIRS = [
    "01_filters",
    "02_headers",
    "03_hscroll",
    "04_vscroll",
    "05_exports",
    "06_notes",
]

MAX_REPORT_SLUG_LEN = 34


PAGES: dict[str, dict[str, list[str]]] = {
    "p1_main": {
        "01_sales_analysis": [
            "Outlet Sales",
            "Brand Order Type Sales",
            "Hourly Sales Analysis",
            "Hourly Item Sales Analysis",
            "Daily Item Sales Analysis",
            "Consolidated Hourly Sales",
            "Consolidated Hourly Sales Tabwise",
            "Daily Sales",
            "Daily Sales Analysis",
            "Daily Sales Tabwise",
            "Daily Sales Sourcewise",
            "Daily Sales With Categories",
            "Item Hourly Sales By Tab",
            "Hourly Sales By Source",
            "Day Part Sales",
            "Day Part Product Sales",
            "day_part_product_detailed",
            "Brand Sales",
            "Sales Contribution",
            "Billwise Section Sales Analysis",
            "section_sales_analysis",
            "source_analysis_summary",
            "source_wise_tab_wise_item_analysis",
        ],
        "02_settlements": [
            "Settlement Analysis",
            "Settlement Analysis Consolidated",
            "Daily Payments Breakup",
            "Daily Payments Breakup Consolidated",
            "Billwise Settlement Analysis",
            "Enterprise BTC Report",
        ],
        "03_discounts_offers": [
            "Daily Item Wise Discount",
            "Daily Discount Billwise",
            "Offers Analysis",
            "Offer Budget",
            "Discount Billwise Analysis",
            "Offer Code Report",
            "Offer Code Usage Report",
            "Discount And Complimentary Analysis",
            "Entp Item Based Offer",
            "Complimentary Head",
            "Complimentary Head Itemwise",
            "Consolidated Item Complimentary",
        ],
        "04_tax_analysis": [
            "Daily Tax Analysis",
            "Daily No VAT Analysis",
            "Super Category Wise Daily Taxes",
            "Super Category Wise No VAT",
            "Tax Summary",
        ],
        "05_performance": [
            "Menu Mix",
            "Category Analysis",
            "Super Category Sourcewise Sales",
            "Super Category Tabwise Sourcewise Sales",
            "Item Analysis",
            "item_source_report",
            "itemwise Enterprise",
            "Tab Wise Item Analysis",
            "item_incidence",
            "Highest And Lowest Selling Items",
            "Tab Wise Analysis",
            "Brand Performance Section Wise",
            "Brand Performance Report",
            "Combo Report",
            "Meal Count Report",
            "user_attendance_report_detailed",
            "user_attendance_report_summary",
        ],
        "06_misc": [
            "Void Bill Item Wise",
            "Cashier Report",
            "Budget DSR Report",
            "CRM Report",
            "Voucher Report",
            "sales_and_reload_report",
            "msr_reload_report",
            "Gift Card Report",
            "Super Categories DSR",
            "Online Orders Time Log",
            "Entp EDC Report",
            "Entp Day Report",
            "Entp Reprint Report",
            "filter_invoices_report",
            "item_out_of_stock",
            "Whatsapp Message Report",
            "Call Center Report",
            "Item Recipe Report",
            "Refund Item Detail Report",
            "Shift Report",
            "Expense Report",
            "Aggregator Status Report",
            "Staff Meal Report",
            "Advance Booking Report",
            "Removed Taxes Charges Report",
            "Unknown Miscellaneous Report 26",
            "Unknown Miscellaneous Report 27",
        ],
    },
    "p2_reports": {
        "01_analytics": [
            "Hourly Sales Report",
            "half_hourly_sales_report",
            "Hourly Sales By Category",
            "Growth Report",
            "Average Bill",
            "Income Analysis Report",
            "Forecast Comparison Report",
            "Food Cost Report",
            "KDS Report",
            "Location Wise Sales",
        ],
        "02_attendance": [
            "User Attendance Report",
            "Single User Attendance Report",
        ],
        "03_audit": [
            "KOT Detail Report",
            "Day Opening Variance Report",
            "KOT Delete History Report",
            "Complimentary Report",
            "Complimentary Detail Report Headwise",
            "Discount Report",
            "discount_and_voucher_report",
            "Offers Report",
            "Reprint Report",
            "KOT Tracking Report",
            "Removed Taxes Charges Report",
            "Report By Time",
            "Feedback Report",
            "No Feedback Report",
            "Wis Report",
            "Feedback Report Advance",
            "Feedback Followup Report",
            "Feedback Without Bill Report",
            "OMS Report Detail",
            "OMS Report Analysis",
            "Revenue Report",
            "Negative Orders Report",
            "Call Center Report",
            "Delivery Audit Report",
            "Service Charge Report",
            "Tips Report",
            "Charity Report",
            "Non Taxable Item Report",
            "Edited Bills Report",
            "Food Bills Void Tax Report",
            "Online Orders Time Log",
            "Happy Hour Report",
            "Item Based Offer Report",
            "Virtual User Report",
            "BI Logs Report",
            "RMS Error Logs Report",
            "Offline Log Report",
            "Aggregator Status Report",
            "Custom Group Report",
            "Bill Transfer In Report",
            "audit_report",
            "msr_card_report",
            "billwise_distribution",
            "bill_reprint_report",
            "Billwise_sale_GST",
            "cred_note_issued",
            "day_part_daily_sales",
            "button_disc_detail_report",
            "staff_meal_report",
            "BTS Itemwise Report",
        ],
        "04_category_item": [
            "Item By Source Report",
            "Item Wise Enterprise Report",
            "Sale By Item Category",
            "Item Comment Wise Consolidated Report",
            "Itemwise Consolidate",
            "Section Category Wise Report",
            "Section Tabwise Sales Report",
            "Itemwise Contribution",
            "Menu Mix Report",
            "item_incidence_report",
            "Sessionwise Item Sale",
            "Product Report",
            "Combo Report",
            "assorted_items_report",
            "AddOn Report",
            "Product Price Variation Report",
            "Hourly Item Detail Billwise With Settlement Mode",
            "Item Stock Status Report",
        ],
        "05_crm": [
            "CRM Report",
            "Bill And Customer Consolidated Report",
            "Call Details Report",
        ],
        "06_prepaid_card": [
            "Card Report",
        ],
        "07_sales": [
            "Payment Details Report",
            "payments_breakup_detailed",
            "Tax Summary Report",
            "Taxation Sale Report",
            "Category Wise Sales Report",
            "Bill Item Detail Report",
            "Settlement Report",
            "TTR Settlement Report",
            "Payments Breakup Report",
            "BTC Settlement Report",
            "Online Other Payment Detail Report",
            "Online Other Payment Consolidated Report",
            "Coupon Report",
            "Instance Wise Report",
            "Delivery Report",
            "Daily Sales Report",
            "Daily Sales Summary Report",
            "Day Wise Sales Report",
            "Daily Sales Report Detailed",
            "Day Closing Report",
            "Week Cost Report",
            "MTAX Log Report",
            "hourly_sales_summary",
            "Source Wise Analysis Report",
            "Bill No Wise Report",
            "Bill Status Sales Report",
            "Advance Booking Report",
            "Advance Booking Session Consolidated",
            "Day Check Close Report",
            "Enterprise Settlement Report",
            "Online Orders Report",
            "Daily Sales Breakup",
            "Food Sold Report",
            "Bill Wise Sales GST BillWise",
            "WTD SOS Comparison",
            "Gross Sale Wastage Report",
            "DSH Item Wise Report",
            "Daily Sales Reversal",
            "Day Wise Revenue Report",
            "Online Order Payment Details Report",
            "msr_card_reload_report",
        ],
        "08_gst": [
            "Item Wise GST Report",
            "GST Wise Report",
            "Non GST Wise Report",
            "Instance Wise GST Report",
            "GSTR_report",
            "tab_wise_gst_report",
            "hsn_report",
            "item_per_bill_count_report",
        ],
        "09_staff_perf": [
            "Tab User Waiter Cashier Breakdown Report",
            "Server Report Card",
            "Compare Servers",
            "Delivery Rider Tracking Report",
            "Employee Performance By Category",
        ],
        "10_cash_mgmt": [
            "Day Report",
            "Shift Report",
            "Envelope Report",
            "Cash In Cash Out Report",
            "Multi Currency Detail Report",
        ],
        "11_banquet": [
            "Banquet Function List Report",
            "Banquet Sales Register",
            "Day Wise Sales Register",
        ],
        "12_bir": [
            "CashierWise X Report",
            "Z Report",
            "Audit Log Report",
            "NAAC Sales Report",
            "PWD Sales Report",
            "BIR Sales Summary Report",
            "Solo Parent Sales Report",
            "Senior Citizen Sales Report",
            "20 E Journal Report",
        ],
        "13_master_dash": [],
    },
    "p3_examples": {
        "01_hourly_sales_category": [
            "Hourly Sales By Category",
        ],
    },
    "p4_stock_admin": {
        "01_enterprise_reports": [
            "Enterprise Entry",
            "ERP Vendor Price",
            "Enterprise Stock Return",
            "Enterprise Consumption",
            "Enterprise Stock Re-Order",
            "Enterprise Purchase Order",
            "Enterprise Consolidated Indent",
            "Enterprise Variance",
            "Enterprise categorywise cogs",
            "Enterprise Bill Passing",
            "Enterprise Credit Note Report",
            "Enterprise Wastage Report",
            "Enterprise Purchase Summary Report",
            "Enterprise Internal Indent Report",
            "Enterprise Food Cost Report",
        ],
        "02_transactional_reports": [
            "Entry Report",
            "Entry Sync Report",
            "Payment Report",
            "Stock Return",
            "Purchase Detail",
            "Purchase Detail Consolidated",
            "Purchase Requisition Report",
            "Cut Code Report",
            "Bill Passing Report",
            "Stock In Stock Out Report",
        ],
        "03_po_so_reports": [
            "Purchase Order",
            "Standing Purchase Order",
            "Sales Order",
            "OpenReturn Sales Order Report",
            "ERP Vendor Invoice",
            "Consolidated salesorder Report receiverWise",
        ],
        "04_indent_reports": [
            "Indent Report",
            "Consolidated Indent",
            "Consolidated Indent Items",
            "Issue Report",
            "Consolidated Indent Report Outlet Wise",
            "Suspense Report",
            "Bulk Return Report",
        ],
        "05_aggregation_reports": [
            "Item Wise Inflation Report",
            "Consumption Report",
            "Variance Report",
            "Intermediate (Semi)",
            "Movement Report",
            "Finished Food",
            "Recipe Consumption Report",
        ],
        "06_analytical_reports": [
            "Booking Journal",
            "Food Cost Report",
            "Re-Order Level",
            "Closing Stock Report",
            "Cost margin Report",
            "Pricing Ledger",
            "Purchase Summary",
            "Stock Recipe Report",
        ],
        "07_other_reports": [
            "Advance Ordering Report",
            "NC Head Consumption Cost",
            "Expiry Report",
            "Default Cost Report",
            "Kitchen Wise Item Report",
            "Vendor Pricing Report",
            "Late Delivery Report",
            "RR Reports",
            "Pending Requests",
            "Manual Month End Report",
            "HSN Wise Summary",
            "Sales Payout Report",
            "Vendor Last 5 Purchase Price",
            "Yield Report",
            "Production Plan Report",
            "Gate Pass Report",
            "Bin Packaging Report",
        ],
        "08_summary": [
            "Deployment Summary",
        ],
        "09_bill_passing": [
            "Bill Passing",
        ],
        "10_catering": [
            "Catering",
        ],
    },
}


def slugify(value: str) -> str:
    clean = []
    prev_underscore = False
    for char in value.strip().lower():
        if char.isalnum():
            clean.append(char)
            prev_underscore = False
        else:
            if not prev_underscore:
                clean.append("_")
                prev_underscore = True
    slug = "".join(clean).strip("_") or "unnamed"
    return slug[:MAX_REPORT_SLUG_LEN].rstrip("_")


def create_scaffold(root: Path) -> tuple[int, int]:
    root.mkdir(parents=True, exist_ok=True)
    report_rows: list[dict[str, str]] = []
    folder_rows: list[dict[str, str]] = []

    for page_name, sections in PAGES.items():
        page_dir = root / page_name
        page_dir.mkdir(parents=True, exist_ok=True)
        (page_dir / "00_page_menu_screenshots").mkdir(exist_ok=True)
        (page_dir / "_unknown_or_new_sections").mkdir(exist_ok=True)
        folder_rows.append(
            {
                "folder_type": "page",
                "page": page_name,
                "section": "",
                "report": "",
                "relative_path": str(page_dir.relative_to(root)),
                "purpose": "Top-level POSist page screenshots and report sections.",
            }
        )

        for section_name, reports in sections.items():
            section_dir = page_dir / section_name
            section_dir.mkdir(exist_ok=True)
            (section_dir / "00_section_menu_screenshots").mkdir(exist_ok=True)
            (section_dir / "_unknown_or_new_reports").mkdir(exist_ok=True)
            folder_rows.append(
                {
                    "folder_type": "section",
                    "page": page_name,
                    "section": section_name,
                    "report": "",
                    "relative_path": str(section_dir.relative_to(root)),
                    "purpose": "Section menu screenshots and report-specific folders.",
                }
            )

            for index, report in enumerate(reports, start=1):
                report_dir = section_dir / f"{index:02d}_{slugify(report)}"
                report_dir.mkdir(exist_ok=True)
                for slot in REPORT_SLOT_DIRS:
                    (report_dir / slot).mkdir(exist_ok=True)
                folder_rows.append(
                    {
                        "folder_type": "report",
                        "page": page_name,
                        "section": section_name,
                        "report": report,
                        "relative_path": str(report_dir.relative_to(root)),
                        "purpose": "Report screenshots, scroll parts, exports, and notes.",
                    }
                )
                report_rows.append(
                    {
                        "page": page_name,
                        "section": section_name,
                        "report_name": report,
                        "report_folder": str(report_dir.relative_to(root)),
                        "capture_status": "not_started",
                        "configured_in_uat": "unknown",
                        "api_endpoint_candidate": "",
                        "priority_domain": "",
                        "notes": "",
                    }
                )

    write_csv(
        root / "00_FOLDER_MAP.csv",
        [
            "folder_type",
            "page",
            "section",
            "report",
            "relative_path",
            "purpose",
        ],
        folder_rows,
    )
    write_csv(
        root / "00_REPORT_STATUS.csv",
        [
            "page",
            "section",
            "report_name",
            "report_folder",
            "capture_status",
            "configured_in_uat",
            "api_endpoint_candidate",
            "priority_domain",
            "notes",
        ],
        report_rows,
    )
    write_csv(
        root / "00_CAPTURE_MANIFEST.csv",
        [
            "capture_id",
            "page",
            "section",
            "report_name",
            "file_name",
            "capture_type",
            "part_order",
            "scroll_axis",
            "filter_context",
            "visible_columns_or_metrics",
            "configured_in_uat",
            "api_endpoint_candidate",
            "priority_domain",
            "notes",
        ],
        [],
    )
    write_readme(root)
    return len(folder_rows), len(report_rows)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_readme(root: Path) -> None:
    readme = """# Structured POSist Screenshots

This folder is for ABNAH POSist UAT screenshot dumping.

Use this hierarchy:

```text
POSist page -> report section -> individual report -> screenshot slot
```

For each report, use:

- `01_filters`: report title, selected filters, date range, outlet/deployment, generate/export buttons.
- `02_headers`: first table view with column headers and visible grain.
- `03_hscroll`: left-to-right table screenshots when the report has horizontal scrolling.
- `04_vscroll`: top-to-bottom table screenshots when the report has vertical scrolling or pagination.
- `05_exports`: CSV/XLS/PDF exports when available.
- `06_notes`: short text notes, odd behavior, unavailable report notes, API hints.

Naming convention:

```text
report_slug__filters__part01.png
report_slug__columns_left__part02.png
report_slug__columns_right__part03.png
report_slug__export.csv
```

Fill or update:

- `00_CAPTURE_MANIFEST.csv` for every screenshot/export.
- `00_REPORT_STATUS.csv` when a report is configured, not configured, useful, not useful, or API-backed.
- `00_FOLDER_MAP.csv` only if a new folder is added manually.

Do not paste credentials or API secrets in screenshots.
"""
    (root / "README.md").write_text(readme, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--target",
        default=(
            "source_intake/posist_uat/_incoming_drop/"
            "posist_ss"
        ),
        help="Target folder for the generated screenshot scaffold.",
    )
    args = parser.parse_args()

    target = Path(args.target)
    folder_count, report_count = create_scaffold(target)
    print(f"Created/updated: {target.resolve()}")
    print(f"Folder rows: {folder_count}")
    print(f"Report rows: {report_count}")


if __name__ == "__main__":
    main()
