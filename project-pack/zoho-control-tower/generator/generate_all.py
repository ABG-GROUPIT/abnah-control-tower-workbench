from __future__ import annotations

import pandas as pd

from generator.bom import build_recipe_bom
from generator.competitors import build_competitor_pricing
from generator.config import DATA_DIR, DOCS_DIR, MONTHS, MONTH_DIRS, STATIC_DIR, ensure_dirs, month_code_for_date, write_csv
from generator.control_tower import build_control_tower_reports
from generator.entry import build_entry_report
from generator.events import build_events
from generator.holidays import build_holidays
from generator.ingredients import build_ingredients
from generator.inventory import build_inventory_closing
from generator.menu_master import build_menu_master
from generator.outlets import OUTLETS
from generator.purchase import build_purchase_report
from generator.sales import build_sales_report
from generator.vendor_master import ACTIVE_VENDOR_NAMES, build_vendor_report


STATIC_TABLES = {
    "vendor_report": "vendor_report.csv",
    "menu_master": "menu_master.csv",
    "brand_recipe_consumption": "brand_recipe_consumption.csv",
    "indian_calendar_holidays": "indian_calendar_holidays.csv",
    "manual_calendar_events": "manual_calendar_events.csv",
    "competitor_pricing": "competitor_pricing.csv",
}


OUTLET_CODE_BY_NAME = {row["outlet_name"]: row["outlet_code"] for row in OUTLETS}

MONTHLY_REPORTS = {
    "sales_report": ("outlet_name", "date"),
    "purchase_report": ("deployment", "po_date"),
    "entry_report": ("deployment_name", "date"),
    "inventory_closing_report": ("deployment", "date"),
}


def _remove_generated_csvs() -> None:
    for path in DATA_DIR.rglob("*.csv"):
        try:
            path.unlink()
        except PermissionError:
            print(f"Warning: could not remove locked generated CSV: {path}")


def _with_row_id(df: pd.DataFrame, prefix: str) -> pd.DataFrame:
    result = df.copy()
    if "row_id" not in result.columns:
        result.insert(0, "row_id", [f"{prefix}{idx + 1:05d}" for idx in range(len(result))])
    return result


def _normalized_bom(display_bom: pd.DataFrame) -> pd.DataFrame:
    normalized = display_bom.copy()
    normalized["recipe_name"] = normalized["recipe_name"].replace("", pd.NA).ffill()
    return normalized


def _split_and_write_outlet_monthly(df: pd.DataFrame, report_name: str, outlet_col: str, date_col: str) -> dict[str, dict[str, int]]:
    row_counts: dict[str, dict[str, int]] = {}
    dated = df.copy()
    dated["_month_code"] = dated[date_col].map(month_code_for_date)
    for month_code in MONTHS:
        row_counts[month_code] = {}
        for outlet in OUTLETS:
            outlet_code = outlet["outlet_code"]
            outlet_name = outlet["outlet_name"]
            outlet_df = dated[(dated["_month_code"] == month_code) & (dated[outlet_col] == outlet_name)].drop(columns=["_month_code"])
            sort_columns = [column for column in [date_col, "row_id"] if column in outlet_df.columns]
            outlet_df = outlet_df.sort_values(sort_columns).reset_index(drop=True)
            write_csv(outlet_df, MONTH_DIRS[month_code] / report_name / f"{outlet_code}_{report_name}.csv")
            row_counts[month_code][outlet_code] = len(outlet_df)
    return row_counts


def _dupe_count(df: pd.DataFrame, key: str | list[str]) -> int:
    return int(df.duplicated(subset=key).sum())


def _write_validation_report(
    vendors: pd.DataFrame,
    menu: pd.DataFrame,
    ingredients: pd.DataFrame,
    bom: pd.DataFrame,
    holidays: pd.DataFrame,
    events: pd.DataFrame,
    competitors: pd.DataFrame,
    sales: pd.DataFrame,
    purchase: pd.DataFrame,
    entry: pd.DataFrame,
    inventory: pd.DataFrame,
    monthly_counts: dict[str, dict[str, dict[str, int]]],
) -> None:
    sales_dates = pd.to_datetime(sales["date"])
    inventory_dates = pd.to_datetime(inventory["date"])
    missing_sales_items = sorted(set(sales["item_number"]) - set(menu["item_number"]))
    populated_bom_recipe_names = set(bom.loc[bom["recipe_name"].astype(str) != "", "recipe_name"])
    missing_bom_recipes = sorted(populated_bom_recipe_names - set(menu["item_name"]))
    vendor_names = set(vendors["vendor_name"])
    missing_purchase_vendors = sorted(set(purchase["vendor_name"]) - vendor_names)
    missing_entry_vendors = sorted(set(entry["vendor_name"]) - vendor_names)
    missing_inventory_items = sorted(set(inventory["item_name"]) - set(ingredients["item_name"]))

    static_files = sorted(path.name for path in STATIC_DIR.glob("*.csv"))
    outlet_files = sorted(path for month in MONTH_DIRS.values() for path in month.glob("*/*.csv"))
    ingredients_internal_exists = (STATIC_DIR / "ingredients_internal.csv").exists()
    outlets_internal_exists = (STATIC_DIR / "outlets_internal.csv").exists()
    bom_populated = int((bom["recipe_name"].astype(str) != "").sum())
    bom_blank = int((bom["recipe_name"].astype(str) == "").sum())
    first_recipe = bom.loc[bom["recipe_name"].astype(str) != "", "recipe_name"].iloc[0]
    first_block_start = bom.index[bom["recipe_name"] == first_recipe][0]
    next_populated = bom.index[(bom.index > first_block_start) & (bom["recipe_name"].astype(str) != "")]
    first_block_end = int(next_populated[0]) if len(next_populated) else len(bom)
    bom_sample = bom.iloc[first_block_start:first_block_end].head(8)

    lines = [
        "# ABNAH Synthetic Demo Validation Report",
        "",
        "Generated by `python -m generator.generate_all`.",
        "",
        "## Row Counts By Raw Table",
        "",
        f"- vendor_report: {len(vendors):,}",
        f"- menu_master: {len(menu):,}",
        f"- brand_recipe_consumption: {len(bom):,}",
        f"- indian_calendar_holidays: {len(holidays):,}",
        f"- manual_calendar_events: {len(events):,}",
        f"- competitor_pricing: {len(competitors):,}",
        f"- sales_report: {len(sales):,}",
        f"- purchase_report: {len(purchase):,}",
        f"- entry_report: {len(entry):,}",
        f"- inventory_closing_report: {len(inventory):,}",
        "",
        "## File Generation Checks",
        "",
        f"- Static files generated: {len(static_files)}",
        f"- Outlet-wise operational files generated: {len(outlet_files)}",
        f"- ingredients_internal.csv exists: {ingredients_internal_exists}",
        f"- outlets_internal.csv exists: {outlets_internal_exists}",
        f"- Analytics schema/views created by generator: False",
        "",
        "## Coverage",
        "",
        f"- Sales date range: {sales_dates.min().date()} to {sales_dates.max().date()}",
        f"- Inventory date range: {inventory_dates.min().date()} to {inventory_dates.max().date()}",
        f"- Outlet count in sales: {sales['outlet_name'].nunique()}",
        f"- Menu item count: {menu['item_number'].nunique()}",
        f"- Vendor count: {vendors['vendor_code'].nunique()}",
        f"- Active purchase vendors: {purchase['vendor_name'].nunique()}",
        f"- Required active vendors represented: {len(set(ACTIVE_VENDOR_NAMES) & set(purchase['vendor_name']))} of {len(ACTIVE_VENDOR_NAMES)}",
        f"- Event count: {len(events)}",
        f"- Holiday/calendar marker count: {len(holidays)}",
        f"- Competitor mapping count: {len(competitors)}",
        "",
        "## Duplicate Primary Key Checks",
        "",
        f"- vendor row_id duplicates: {_dupe_count(vendors, 'row_id')}",
        f"- menu row_id duplicates: {_dupe_count(menu, 'row_id')}",
        f"- BOM row_id duplicates: {_dupe_count(bom, 'row_id')}",
        f"- holiday row_id duplicates: {_dupe_count(holidays, 'row_id')}",
        f"- event row_id duplicates: {_dupe_count(events, 'row_id')}",
        f"- competitor row_id duplicates: {_dupe_count(competitors, 'row_id')}",
        f"- sales row_id duplicates: {_dupe_count(sales, 'row_id')}",
        f"- purchase row_id duplicates: {_dupe_count(purchase, 'row_id')}",
        f"- entry row_id duplicates: {_dupe_count(entry, 'row_id')}",
        f"- inventory row_id duplicates: {_dupe_count(inventory, 'row_id')}",
        "",
        "## Business Rule Checks",
        "",
        f"- Negative inventory rows: {int((inventory['total_qty'] < 0).sum())}",
        f"- Positive sales quantity with zero net_sale rows: {int(((sales['qty'] > 0) & (sales['net_sale'] <= 0)).sum())}",
        f"- Missing sales menu keys: {len(missing_sales_items)}",
        f"- Missing BOM recipe keys: {len(missing_bom_recipes)}",
        f"- Missing purchase vendor keys: {len(missing_purchase_vendors)}",
        f"- Missing entry vendor keys: {len(missing_entry_vendors)}",
        f"- Missing inventory ingredient keys: {len(missing_inventory_items)}",
        "",
        "## Row Counts By Month And Outlet",
        "",
    ]
    for table_name, month_counts in monthly_counts.items():
        lines.append(f"### {table_name}")
        lines.append("")
        for month, outlet_counts in month_counts.items():
            total = sum(outlet_counts.values())
            outlet_bits = ", ".join(f"{outlet}={count:,}" for outlet, count in outlet_counts.items())
            lines.append(f"- {month}: total={total:,}; {outlet_bits}")
        lines.append("")

    lines.extend(
        [
            "## Brand Recipe Consumption Formatting Check",
            "",
            f"- Rows with recipe_name populated: {bom_populated:,}",
            f"- Continuation rows with recipe_name blank: {bom_blank:,}",
            "",
            "Sample recipe block:",
            "",
            "```csv",
            bom_sample.to_csv(index=False).strip(),
            "```",
            "",
            "",
            "## Load Status",
            "",
            "- Month 1: generated locally; database load status is recorded in `control.etl_load_batch` after loader execution.",
            "- Month 2: generated locally; database load status is recorded in `control.etl_load_batch` after loader execution.",
            "- Month 3: generated locally; database load status is recorded in `control.etl_load_batch` after loader execution.",
            "",
            "## Caveats",
            "",
            "- Calendar and holiday rows are configurable synthetic markers and are not official holiday verification.",
            "- Competitor pricing rows are contextual demo inputs and do not prove causality.",
            "- Stock risk is approximated from closing stock and consumption pressure, not a production stockout forecast.",
        ]
    )
    (DOCS_DIR / "validation_report.md").write_text("\n".join(lines), encoding="utf-8")


def generate_all() -> dict[str, int]:
    ensure_dirs()
    _remove_generated_csvs()
    ingredients = build_ingredients()
    vendors = _with_row_id(build_vendor_report(), "VROW")
    menu = _with_row_id(build_menu_master(), "MROW")
    bom = build_recipe_bom(menu, ingredients)
    normalized_bom = _normalized_bom(bom)
    holidays = _with_row_id(build_holidays(), "HROW")
    events = _with_row_id(build_events(), "EROW")
    competitors = _with_row_id(build_competitor_pricing(menu), "CROW")
    sales = build_sales_report(menu, holidays, events)
    purchase = build_purchase_report(ingredients, events)
    entry = build_entry_report(purchase)
    inventory = build_inventory_closing(sales, normalized_bom, entry, ingredients)
    control_tower_counts = build_control_tower_reports(
        menu=menu,
        ingredients=ingredients,
        vendors=vendors,
        bom=bom,
        sales=sales,
        purchase=purchase,
    )

    static_frames = {
        "vendor_report": vendors,
        "menu_master": menu,
        "brand_recipe_consumption": bom,
        "indian_calendar_holidays": holidays,
        "manual_calendar_events": events,
        "competitor_pricing": competitors,
    }
    for table_name, filename in STATIC_TABLES.items():
        write_csv(static_frames[table_name], STATIC_DIR / filename)

    monthly_counts = {
        report_name: _split_and_write_outlet_monthly(frame, report_name, outlet_col, date_col)
        for report_name, frame, outlet_col, date_col in [
            ("sales_report", sales, *MONTHLY_REPORTS["sales_report"]),
            ("purchase_report", purchase, *MONTHLY_REPORTS["purchase_report"]),
            ("entry_report", entry, *MONTHLY_REPORTS["entry_report"]),
            ("inventory_closing_report", inventory, *MONTHLY_REPORTS["inventory_closing_report"]),
        ]
    }

    _write_validation_report(vendors, menu, ingredients, bom, holidays, events, competitors, sales, purchase, entry, inventory, monthly_counts)

    return {
        "vendors": len(vendors),
        "menu_items": len(menu),
        "bom_rows": len(bom),
        "sales_rows": len(sales),
        "purchase_rows": len(purchase),
        "entry_rows": len(entry),
        "inventory_rows": len(inventory),
        "events": len(events),
        "holidays": len(holidays),
        "competitors": len(competitors),
        **{f"control_tower_{key}": value for key, value in control_tower_counts.items()},
    }


def main() -> None:
    counts = generate_all()
    print("Generated ABNAH synthetic demo data:")
    for key, value in counts.items():
        print(f"  {key}: {value:,}")
    print("Validation report written to docs/validation_report.md")


if __name__ == "__main__":
    main()
