from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
MONTH_DIR = DATA / "month_01"
STATIC_DIR = DATA / "static"
SQL_DIR = ROOT / "docs" / "zoho_query_table_sql"
OUT_DIR = ROOT / "docs" / "month1_truth_tables"
README_PATH = ROOT / "docs" / "month1_truth_reference_readme.md"


OUTLETS = [
    {
        "outlet_code": "OUT001",
        "outlet_name": "ABNAH Cafe Connaught Place",
        "market_area": "Connaught Place",
        "persona": "corporate, office, tourist demand",
        "weekday_profile": "High Monday-Friday coffee and lunch demand",
    },
    {
        "outlet_code": "OUT002",
        "outlet_name": "ABNAH Cafe Hauz Khas",
        "market_area": "Hauz Khas",
        "persona": "student, youth, social, local event demand",
        "weekday_profile": "Strong Friday/weekend and student event demand",
    },
    {
        "outlet_code": "OUT003",
        "outlet_name": "ABNAH Cafe Saket Premium",
        "market_area": "Saket",
        "persona": "mall, leisure, premium weekend demand",
        "weekday_profile": "Strong desserts, shakes, premium beverages, and weekends",
    },
]


def read_folder(folder: str) -> pd.DataFrame:
    paths = sorted((MONTH_DIR / folder).glob("*.csv"))
    if not paths:
        raise FileNotFoundError(f"No CSV files found in {MONTH_DIR / folder}")
    frames = [pd.read_csv(path) for path in paths]
    return pd.concat(frames, ignore_index=True)


def read_static(name: str) -> pd.DataFrame:
    return pd.read_csv(STATIC_DIR / name)


def numeric(df: pd.DataFrame, cols: Iterable[str]) -> pd.DataFrame:
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df


def add_outlet_fields(df: pd.DataFrame, source_col: str) -> pd.DataFrame:
    mapping = pd.DataFrame(OUTLETS)
    out = df.merge(
        mapping[["outlet_code", "outlet_name", "market_area"]],
        left_on=source_col,
        right_on="outlet_name",
        how="left",
    )
    if source_col != "outlet_name":
        out = out.drop(columns=[source_col])
    return out


def money(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "-"
    value = float(value)
    sign = "-" if value < 0 else ""
    value_abs = abs(value)
    if value_abs >= 100000:
        return f"{sign}{value_abs / 100000:.2f}L"
    if value_abs >= 1000:
        return f"{sign}{value_abs / 1000:.2f}K"
    return f"{sign}{value_abs:,.0f}"


def number(value: float | int | None, decimals: int = 0) -> str:
    if value is None or pd.isna(value):
        return "-"
    return f"{float(value):,.{decimals}f}"


def pct(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "-"
    return f"{float(value):.1f}%"


def safe_div(numerator: float, denominator: float) -> float:
    return float(numerator) / float(denominator) if denominator else 0.0


def md_table(
    df: pd.DataFrame,
    columns: list[str],
    headers: list[str] | None = None,
    formats: dict[str, str] | None = None,
    max_rows: int | None = None,
) -> str:
    formats = formats or {}
    headers = headers or columns
    view = df.loc[:, columns].copy()
    if max_rows is not None:
        view = view.head(max_rows)
    if view.empty:
        return "_No rows._"

    def fmt(col: str, val) -> str:
        kind = formats.get(col)
        if kind == "money":
            return money(val)
        if kind == "number0":
            return number(val, 0)
        if kind == "number1":
            return number(val, 1)
        if kind == "number2":
            return number(val, 2)
        if kind == "pct":
            return pct(val)
        if pd.isna(val):
            return ""
        text = str(val)
        text = text.replace("\n", " ").replace("|", "/")
        return text

    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for _, row in view.iterrows():
        lines.append("| " + " | ".join(fmt(col, row[col]) for col in columns) + " |")
    return "\n".join(lines)


def list_join(values: Iterable[str], limit: int = 10) -> str:
    unique = [str(v) for v in values if pd.notna(v)]
    unique = sorted(dict.fromkeys(unique))
    if len(unique) <= limit:
        return ", ".join(unique)
    return ", ".join(unique[:limit]) + f", +{len(unique) - limit} more"


def load_data() -> dict[str, pd.DataFrame]:
    sales = read_folder("sales_report")
    sales = add_outlet_fields(sales, "outlet_name")
    sales["sales_date"] = pd.to_datetime(sales["date"]).dt.date
    sales = numeric(sales, ["qty", "net_sale"])
    sales["net_sale_per_qty"] = sales.apply(
        lambda row: safe_div(row["net_sale"], row["qty"]), axis=1
    )

    purchase = read_folder("purchase_report")
    purchase = add_outlet_fields(purchase, "deployment")
    purchase["po_date"] = pd.to_datetime(purchase["po_date"]).dt.date
    purchase["expected_delivery_date"] = pd.to_datetime(
        purchase["expected_delivery"]
    ).dt.date
    purchase = numeric(
        purchase,
        [
            "total_processed_qty",
            "remaining_balance_qty",
            "quantity",
            "unit_price",
            "subtotal",
            "tax",
            "total_item_cost",
        ],
    )
    purchase = purchase.rename(
        columns={
            "quantity": "ordered_qty",
            "total_processed_qty": "processed_qty",
            "remaining_balance_qty": "remaining_qty",
        }
    )
    purchase["is_open_or_partial_sql"] = (
        purchase["po_status"].isin(["Pending", "Partially Received"])
        | (purchase["remaining_qty"] > 0)
    ).astype(int)
    purchase["pending_or_partial_flag"] = (
        purchase["po_status"].isin(["Pending", "Partially Received"])
        | (purchase["remaining_qty"] > 0)
    ).astype(int)
    purchase["processed_value_est"] = purchase.apply(
        lambda row: safe_div(row["total_item_cost"] * row["processed_qty"], row["ordered_qty"]),
        axis=1,
    )
    purchase["remaining_value_est"] = purchase.apply(
        lambda row: safe_div(row["total_item_cost"] * row["remaining_qty"], row["ordered_qty"]),
        axis=1,
    )

    entry = read_folder("entry_report")
    entry = add_outlet_fields(entry, "deployment_name")
    entry["receipt_date"] = pd.to_datetime(entry["date"]).dt.date
    entry["invoice_date"] = pd.to_datetime(entry["invoice_date"]).dt.date
    entry = numeric(
        entry,
        [
            "quantity",
            "mrp",
            "unit_price",
            "amount",
            "discount",
            "gst_igst_rate",
            "gst_igst_value",
            "total_tax",
            "item_charges_amount",
            "entry_total",
            "return_quantity",
            "return_amount",
            "grand_total",
        ],
    )
    entry = entry.rename(columns={"quantity": "received_qty", "return_quantity": "return_qty"})

    inventory = read_folder("inventory_closing_report")
    inventory = add_outlet_fields(inventory, "deployment")
    inventory["inventory_date"] = pd.to_datetime(inventory["date"]).dt.date
    inventory = numeric(
        inventory,
        ["average_price", "store_stock_qty", "total_qty", "total_amt"],
    )
    inventory["low_stock_flag"] = (inventory["total_qty"] <= 10).astype(int)
    inventory["inventory_pressure_band"] = "OK"
    inventory.loc[inventory["total_qty"] <= 25, "inventory_pressure_band"] = "Watch"
    inventory.loc[inventory["total_qty"] <= 10, "inventory_pressure_band"] = "Low"

    return {
        "sales": sales,
        "purchase": purchase,
        "entry": entry,
        "inventory": inventory,
        "menu": read_static("menu_master.csv"),
        "recipe": read_static("brand_recipe_consumption.csv"),
        "events": read_static("manual_calendar_events.csv"),
        "competitors": read_static("competitor_pricing.csv"),
        "vendors": read_static("vendor_report.csv"),
        "outlets": pd.DataFrame(OUTLETS),
    }


def build_daily_health(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    sales = data["sales"]
    purchase = data["purchase"]
    entry = data["entry"]
    inventory = data["inventory"]
    events = data["events"].copy()

    sales_daily = (
        sales.groupby(["sales_date", "outlet_code", "outlet_name", "market_area"], dropna=False)
        .agg(
            net_sales=("net_sale", "sum"),
            sold_qty=("qty", "sum"),
            sales_line_count=("row_id", "count"),
        )
        .reset_index()
        .rename(columns={"sales_date": "activity_date"})
    )

    po_daily = (
        purchase.groupby(["po_date", "outlet_code", "outlet_name", "market_area"], dropna=False)
        .agg(
            po_value=("total_item_cost", "sum"),
            open_or_partial_po_count=("is_open_or_partial_sql", "sum"),
            pending_or_partial_po_count=("pending_or_partial_flag", "sum"),
            remaining_value_est=("remaining_value_est", "sum"),
        )
        .reset_index()
        .rename(columns={"po_date": "activity_date"})
    )

    receipt_daily = (
        entry.groupby(["receipt_date", "outlet_code", "outlet_name", "market_area"], dropna=False)
        .agg(receipt_value=("grand_total", "sum"))
        .reset_index()
        .rename(columns={"receipt_date": "activity_date"})
    )

    inv_daily = (
        inventory.groupby(["inventory_date", "outlet_code", "outlet_name", "market_area"], dropna=False)
        .agg(
            inventory_value=("total_amt", "sum"),
            low_stock_item_count=("low_stock_flag", "sum"),
            watch_stock_item_count=(
                "inventory_pressure_band",
                lambda s: int((s == "Watch").sum()),
            ),
        )
        .reset_index()
        .rename(columns={"inventory_date": "activity_date"})
    )

    events["start_date"] = pd.to_datetime(events["start_date"]).dt.date
    events["end_date"] = pd.to_datetime(events["end_date"]).dt.date
    event_rows: list[dict] = []
    for _, ev in events.iterrows():
        if ev["end_date"].month != 1 and ev["start_date"].month != 1:
            continue
        days = pd.date_range(ev["start_date"], ev["end_date"], freq="D")
        affected = [x.strip() for x in str(ev["affected_outlets"]).split(";") if x.strip()]
        for day in days:
            if day.month != 1:
                continue
            for outlet_name in affected:
                outlet = next((o for o in OUTLETS if o["outlet_name"] == outlet_name), None)
                if not outlet:
                    continue
                event_rows.append(
                    {
                        "activity_date": day.date(),
                        "outlet_code": outlet["outlet_code"],
                        "outlet_name": outlet_name,
                        "event_id": ev["event_id"],
                        "event_name": ev["event_name"],
                        "event_type": ev["event_type"],
                    }
                )
    if event_rows:
        event_count = (
            pd.DataFrame(event_rows)
            .groupby(["activity_date", "outlet_code", "outlet_name"], dropna=False)
            .agg(event_count=("event_id", "nunique"), event_names=("event_name", list_join))
            .reset_index()
        )
    else:
        event_count = pd.DataFrame(
            columns=["activity_date", "outlet_code", "outlet_name", "event_count", "event_names"]
        )

    health = sales_daily.merge(
        po_daily,
        on=["activity_date", "outlet_code", "outlet_name", "market_area"],
        how="left",
    )
    health = health.merge(
        receipt_daily,
        on=["activity_date", "outlet_code", "outlet_name", "market_area"],
        how="left",
    )
    health = health.merge(
        inv_daily,
        on=["activity_date", "outlet_code", "outlet_name", "market_area"],
        how="left",
    )
    health = health.merge(
        event_count,
        on=["activity_date", "outlet_code", "outlet_name"],
        how="left",
    )
    fill_cols = [
        "po_value",
        "open_or_partial_po_count",
        "pending_or_partial_po_count",
        "remaining_value_est",
        "receipt_value",
        "inventory_value",
        "low_stock_item_count",
        "watch_stock_item_count",
        "event_count",
    ]
    for col in fill_cols:
        health[col] = health[col].fillna(0)
    health["event_names"] = health["event_names"].fillna("")
    health["health_note"] = "Normal"
    health.loc[health["event_count"] > 0, "health_note"] = "Event Day"
    health.loc[health["low_stock_item_count"] >= 5, "health_note"] = "Inventory Pressure"
    return health


def build_vendor_spend(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    purchase = data["purchase"]
    entry = data["entry"]

    po = (
        purchase.groupby(
            [
                "po_date",
                "outlet_code",
                "outlet_name",
                "market_area",
                "vendor_name",
                "item_code",
                "item_name",
                "category_name",
                "super_category_name",
                "po_status",
            ],
            dropna=False,
        )
        .agg(
            ordered_value=("total_item_cost", "sum"),
            received_value=("total_item_cost", lambda _: 0),
            po_line_count=("row_id", "count"),
            receipt_line_count=("row_id", lambda _: 0),
            open_or_partial_po_count=("is_open_or_partial_sql", "sum"),
            pending_or_partial_flag_count=("pending_or_partial_flag", "sum"),
            remaining_value_est=("remaining_value_est", "sum"),
        )
        .reset_index()
        .rename(columns={"po_date": "activity_date"})
    )

    receipt = (
        entry.groupby(
            [
                "receipt_date",
                "outlet_code",
                "outlet_name",
                "market_area",
                "vendor_name",
                "item_code",
                "item_name",
                "category_name",
                "super_category_name",
            ],
            dropna=False,
        )
        .agg(
            received_value=("grand_total", "sum"),
            receipt_line_count=("row_id", "count"),
        )
        .reset_index()
        .rename(columns={"receipt_date": "activity_date"})
    )
    receipt["po_status"] = "Receipt row - no PO status"
    receipt["ordered_value"] = 0.0
    receipt["po_line_count"] = 0
    receipt["open_or_partial_po_count"] = 0
    receipt["pending_or_partial_flag_count"] = 0
    receipt["remaining_value_est"] = 0.0

    cols = [
        "activity_date",
        "outlet_code",
        "outlet_name",
        "market_area",
        "vendor_name",
        "item_code",
        "item_name",
        "category_name",
        "super_category_name",
        "po_status",
        "ordered_value",
        "received_value",
        "po_line_count",
        "receipt_line_count",
        "open_or_partial_po_count",
        "pending_or_partial_flag_count",
        "remaining_value_est",
    ]
    spend = pd.concat([po[cols], receipt[cols]], ignore_index=True)
    spend = (
        spend.groupby(
            [
                "activity_date",
                "outlet_code",
                "outlet_name",
                "market_area",
                "vendor_name",
                "item_code",
                "item_name",
                "category_name",
                "super_category_name",
                "po_status",
            ],
            dropna=False,
        )
        .sum(numeric_only=True)
        .reset_index()
    )
    spend["po_vs_receipt_gap"] = spend["ordered_value"] - spend["received_value"]
    return spend


def build_event_lift(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    sales = data["sales"].copy()
    events = data["events"].copy()
    events["start_date"] = pd.to_datetime(events["start_date"]).dt.date
    events["end_date"] = pd.to_datetime(events["end_date"]).dt.date
    rows = []
    jan_events = events[
        (pd.to_datetime(events["start_date"]).dt.month == 1)
        | (pd.to_datetime(events["end_date"]).dt.month == 1)
    ]
    for _, ev in jan_events.iterrows():
        affected_outlets = [x.strip() for x in str(ev["affected_outlets"]).split(";") if x.strip()]
        affected_categories = [x.strip() for x in str(ev["affected_category"]).split(";") if x.strip()]
        event_days = [d.date() for d in pd.date_range(ev["start_date"], ev["end_date"], freq="D") if d.month == 1]
        for outlet_name in affected_outlets:
            mask = (sales["outlet_name"] == outlet_name) & (sales["sales_date"].isin(event_days))
            if affected_categories:
                mask = mask & sales["category"].isin(affected_categories)
            event_sales = sales.loc[mask, "net_sale"].sum()

            baseline_start = min(event_days) - pd.Timedelta(days=7).to_pytimedelta()
            baseline_days = [
                d.date()
                for d in pd.date_range(baseline_start, min(event_days) - pd.Timedelta(days=1), freq="D")
            ]
            baseline_mask = (sales["outlet_name"] == outlet_name) & (
                sales["sales_date"].isin(baseline_days)
            )
            if affected_categories:
                baseline_mask = baseline_mask & sales["category"].isin(affected_categories)
            daily_baseline = (
                sales.loc[baseline_mask]
                .groupby("sales_date")
                .agg(net_sale=("net_sale", "sum"))
                .reset_index()
            )
            baseline_sales = daily_baseline["net_sale"].mean() * max(len(event_days), 1)
            rows.append(
                {
                    "event_id": ev["event_id"],
                    "event_name": ev["event_name"],
                    "event_type": ev["event_type"],
                    "outlet_name": outlet_name,
                    "affected_category": ev["affected_category"],
                    "event_days": ", ".join(str(x) for x in event_days),
                    "event_day_sales": event_sales,
                    "baseline_sales": baseline_sales,
                    "sales_lift_value": event_sales - baseline_sales,
                    "sales_lift_pct": safe_div(event_sales - baseline_sales, baseline_sales) * 100,
                    "expected_impact_pct": ev["expected_impact_pct"],
                    "impact_direction": ev["impact_direction"],
                    "confidence_level": ev["confidence_level"],
                }
            )
    return pd.DataFrame(rows)


def build_theoretical_consumption_summary(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    sales = data["sales"].copy()
    recipe = data["recipe"].copy()
    inventory = data["inventory"].copy()

    recipe["recipe_name"] = recipe["recipe_name"].ffill()
    recipe["recipe_qty"] = recipe["recipe_qty"].ffill().fillna(1)
    recipe = recipe.dropna(subset=["recipe_name", "item_name"]).copy()
    recipe = numeric(recipe, ["recipe_qty", "item_qty"])
    recipe["recipe_qty"] = recipe["recipe_qty"].replace(0, 1)

    consumption = sales.merge(
        recipe,
        left_on="item_name",
        right_on="recipe_name",
        how="inner",
        suffixes=("_menu", "_ingredient"),
    )
    consumption["theoretical_ingredient_qty"] = (
        consumption["qty"] * consumption["item_qty"] / consumption["recipe_qty"]
    )
    consumption = consumption.rename(
        columns={
            "item_name_menu": "menu_item_name",
            "item_name_ingredient": "ingredient_name",
            "item_unit": "ingredient_unit",
        }
    )

    ingredient_meta = (
        inventory.sort_values("inventory_date")
        .groupby("item_name", dropna=False)
        .agg(
            item_code=("item_code", "last"),
            category_name=("category_name", "last"),
            super_category_name=("super_category_name", "last"),
        )
        .reset_index()
        .rename(columns={"item_name": "ingredient_name"})
    )

    top_menu_by_ingredient = (
        consumption.groupby(["outlet_name", "ingredient_name", "menu_item_name"], dropna=False)
        .agg(menu_contribution_qty=("theoretical_ingredient_qty", "sum"))
        .reset_index()
        .sort_values(
            ["outlet_name", "ingredient_name", "menu_contribution_qty"],
            ascending=[True, True, False],
        )
    )

    top_lists = (
        top_menu_by_ingredient.groupby(["outlet_name", "ingredient_name"], dropna=False)
        .agg(top_menu_items=("menu_item_name", lambda s: list_join(s, 5)))
        .reset_index()
    )

    summary = (
        consumption.groupby(
            ["outlet_code", "outlet_name", "market_area", "ingredient_name", "ingredient_unit"],
            dropna=False,
        )
        .agg(
            total_theoretical_qty=("theoretical_ingredient_qty", "sum"),
            source_menu_items=("item_number", "nunique"),
            sales_rows=("row_id_menu", "count"),
        )
        .reset_index()
    )
    summary = summary.merge(ingredient_meta, on="ingredient_name", how="left")
    summary = summary.merge(top_lists, on=["outlet_name", "ingredient_name"], how="left")
    return summary.sort_values(
        ["outlet_name", "total_theoretical_qty"], ascending=[True, False]
    )


def build_competitor_positioning_summary(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    competitors = data["competitors"].copy()
    competitors = numeric(
        competitors,
        ["competitor_price", "abnah_price", "price_difference", "price_index", "expected_sales_impact"],
    )
    outlet_map = pd.DataFrame(OUTLETS)[["outlet_name", "market_area"]]
    summary = (
        competitors.groupby(["market_area", "competitor_category", "price_position"], dropna=False)
        .agg(
            mapped_items=("abnah_item_number", "nunique"),
            avg_price_index=("price_index", "mean"),
            avg_price_difference=("price_difference", "mean"),
            avg_expected_sales_impact=("expected_sales_impact", "mean"),
            competitor_examples=("competitor_name", lambda s: list_join(s, 5)),
        )
        .reset_index()
    )
    summary = summary.merge(outlet_map, on="market_area", how="left")
    return summary.sort_values(
        ["market_area", "avg_price_index"], ascending=[True, False]
    )


def add_prediction(
    rows: list[dict],
    dashboard: str,
    visual: str,
    filter_setup: str,
    expected_result: str,
    expected_value: str,
    source_table: str,
    validation_rule: str,
    demo_story: str,
) -> None:
    rows.append(
        {
            "dashboard": dashboard,
            "visual": visual,
            "filter_setup": filter_setup,
            "expected_result": expected_result,
            "expected_value": expected_value,
            "source_table": source_table,
            "validation_rule": validation_rule,
            "demo_story": demo_story,
        }
    )


def build_dashboard_predictions(
    data: dict[str, pd.DataFrame], outputs: dict[str, pd.DataFrame]
) -> pd.DataFrame:
    rows: list[dict] = []
    health = outputs["fact_outlet_daily_health_truth"].copy()
    outlet_summary = outputs["outlet_summary_truth"].copy()
    sales_category = outputs["sales_category_truth"].copy()
    menu_item = outputs["menu_item_truth"].copy()
    vendor_outlet = outputs["vendor_outlet_truth"].copy()
    vendor_material_status = outputs["vendor_material_status_truth"].copy()
    po_status = outputs["po_status_summary_truth"].copy()
    inventory_latest = outputs["inventory_latest_truth"].copy()
    inventory_category = outputs["inventory_category_truth"].copy()
    event_lift = outputs["event_lift_truth"].copy()
    theoretical = outputs["theoretical_consumption_summary_truth"].copy()
    competitor = outputs["competitor_positioning_truth"].copy()

    total_sales = outlet_summary["net_sales"].sum()
    total_po = outlet_summary["po_raised_value"].sum()
    total_receipt = outlet_summary["receipt_booked_value"].sum()
    total_dates = health["activity_date"].nunique()
    all_inventory_turn = safe_div(total_sales * total_dates, health["inventory_value"].sum())
    best_outlet = outlet_summary.sort_values("net_sales", ascending=False).iloc[0]

    add_prediction(
        rows,
        "01_Executive_Outlet_Health",
        "KPI row, All outlets",
        "Outlet = All; Date Range = 2026-01-01 to 2026-01-31",
        "Net Sales, Avg Daily Revenue, PO/Sales, and inventory turnover must match Month 1 totals.",
        f"Net Sales {money(total_sales)}; Avg Daily {money(total_sales / total_dates)}; PO/Sales {pct(total_po / total_sales * 100)}; Revenue/Avg Inventory {number(all_inventory_turn, 2)}",
        "FACT_Outlet_Daily_Health",
        "Use aggregate formulas, not summed row formulas.",
        "All-outlet executive view should show total chain Month 1 scale.",
    )
    add_prediction(
        rows,
        "01_Executive_Outlet_Health",
        "Outlet Sales Ranking",
        "Outlet = All; Date Range = full Month 1",
        "Saket Premium should rank first by net sales.",
        f"Top outlet {best_outlet['outlet_name']} at {money(best_outlet['net_sales'])}",
        "FACT_Outlet_Daily_Health",
        "X outlet_name, Y SUM(net_sales), sort descending.",
        "Saket is the premium mall/leisure story and should lead Month 1 revenue.",
    )

    for _, outlet in outlet_summary.iterrows():
        add_prediction(
            rows,
            "01_Executive_Outlet_Health",
            "KPI row by outlet",
            f"Outlet = {outlet['outlet_name']}; Date Range = full Month 1",
            "Each KPI card should recalculate, not show the all-outlet value.",
            f"Sales {money(outlet['net_sales'])}; PO {money(outlet['po_raised_value'])}; Receipt {money(outlet['receipt_booked_value'])}; Gap {money(outlet['po_vs_receipt_gap'])}; Inv pressure {number(outlet['inventory_pressure_item_days'])}",
            "FACT_Outlet_Daily_Health",
            "Map Outlet to outlet_name and Date Range to activity_date for every KPI.",
            f"{outlet['outlet_name']} should have its own executive story, not a copied global total.",
        )
        top_day = health[health["outlet_name"] == outlet["outlet_name"]].sort_values(
            "net_sales", ascending=False
        ).iloc[0]
        add_prediction(
            rows,
            "01_Executive_Outlet_Health",
            "Daily Sales Trend By Outlet",
            f"Outlet = {outlet['outlet_name']}",
            "The highest point in the line should be the computed top sales day.",
            f"{top_day['activity_date']} at {money(top_day['net_sales'])}; note {top_day['health_note']}",
            "FACT_Outlet_Daily_Health",
            "X activity_date, Y SUM(net_sales), source must be date-grain fact.",
            "Use this to verify date filtering and event/pressure labels.",
        )

    for outlet_name in outlet_summary["outlet_name"]:
        outlet_cats = sales_category[sales_category["outlet_name"] == outlet_name].sort_values(
            "net_sales", ascending=False
        )
        top_cat = outlet_cats.iloc[0]
        outlet_items = menu_item[menu_item["outlet_name"] == outlet_name].copy()
        top_sales_item = outlet_items.sort_values("total_net_sale", ascending=False).iloc[0]
        top_qty_item = outlet_items.sort_values("total_qty", ascending=False).iloc[0]
        add_prediction(
            rows,
            "02_Sales_Menu_Intelligence",
            "Category Revenue Mix",
            f"Outlet = {outlet_name}; Date Range = full Month 1",
            "Coffee Classics should be the top category for this outlet in Month 1.",
            f"{top_cat['category']} = {money(top_cat['net_sales'])}, {pct(top_cat['sales_share_pct'])} outlet share",
            "FACT_Sales",
            "Use FACT_Sales, not SUM_Sales_Category_Mix, if Date Range must work.",
            "This validates that the category chart changes with outlet/date filters.",
        )
        add_prediction(
            rows,
            "02_Sales_Menu_Intelligence",
            "Top Items By Net Sales",
            f"Outlet = {outlet_name}; Sort = SUM(net_sale) descending; Top 10",
            "The top item should match the computed outlet item leader.",
            f"{top_sales_item['item_name']} = {money(top_sales_item['total_net_sale'])}",
            "FACT_Sales for date-safe chart, or SUM_Menu_Item_Performance for full-month chart",
            "If the table repeats the item across outlets, add outlet_name filter or group across outlets intentionally.",
            "This is the menu winner story for the selected cafe.",
        )
        add_prediction(
            rows,
            "02_Sales_Menu_Intelligence",
            "Top Items By Quantity",
            f"Outlet = {outlet_name}; Sort = SUM(qty) descending; Top 10",
            "The volume leader may differ from the revenue leader.",
            f"{top_qty_item['item_name']} = {number(top_qty_item['total_qty'], 1)} units",
            "FACT_Sales or SUM_Menu_Item_Performance",
            "X item_name, Y SUM(qty), sort descending.",
            "Use revenue and quantity together to separate premium winners from high-volume items.",
        )

    for _, outlet in outlet_summary.iterrows():
        outlet_name = outlet["outlet_name"]
        vendor_rows = vendor_outlet[vendor_outlet["outlet_name"] == outlet_name]
        top_po_vendor = vendor_rows.sort_values("po_raised_value", ascending=False).iloc[0]
        top_receipt_vendor = vendor_rows.sort_values("receipt_booked_value", ascending=False).iloc[0]
        top_gap_vendor = vendor_rows.sort_values("po_vs_receipt_gap", ascending=False).iloc[0]
        add_prediction(
            rows,
            "03_Vendor_Procurement_Analytics",
            "Procurement KPI row",
            f"Outlet = {outlet_name}; Date Range = full Month 1; Vendor = All; Material = All",
            "PO, receipt, gap, and open/partial status count should all recalculate for this outlet.",
            f"PO {money(outlet['po_raised_value'])}; Receipt {money(outlet['receipt_booked_value'])}; Gap {money(outlet['po_vs_receipt_gap'])}; Open/partial {number(outlet['po_open_or_partial_status_count'])}",
            "FACT_Vendor_Spend",
            "Do not map PO Status to Receipt Booked Value or PO vs Receipt Value Gap.",
            "This gives the outlet procurement headline before vendor drilldown.",
        )
        add_prediction(
            rows,
            "03_Vendor_Procurement_Analytics",
            "Vendor PO Raised Share",
            f"Outlet = {outlet_name}; Date Range = full Month 1",
            "Top PO vendor should match the computed vendor leader.",
            f"{top_po_vendor['vendor_name']} = {money(top_po_vendor['po_raised_value'])}",
            "FACT_Vendor_Spend",
            "X vendor_name, Y SUM(ordered_value), sort descending.",
            "Vendor concentration story for PO raised value.",
        )
        add_prediction(
            rows,
            "03_Vendor_Procurement_Analytics",
            "Vendor Receipt Booked Share",
            f"Outlet = {outlet_name}; Date Range = full Month 1",
            "Top receipt vendor should match the computed receipt leader.",
            f"{top_receipt_vendor['vendor_name']} = {money(top_receipt_vendor['receipt_booked_value'])}",
            "FACT_Vendor_Spend",
            "X vendor_name, Y SUM(received_value), sort descending.",
            "Receipt movement can differ from PO movement because entries are not PO-number matched.",
        )
        add_prediction(
            rows,
            "03_Vendor_Procurement_Analytics",
            "PO vs Receipt Value Gap",
            f"Outlet = {outlet_name}; Date Range = full Month 1",
            "Largest value gap vendor should be visible when sorted by gap.",
            f"{top_gap_vendor['vendor_name']} gap = {money(top_gap_vendor['po_vs_receipt_gap'])}",
            "FACT_Vendor_Spend",
            "Aggregate formula SUM(ordered_value) - SUM(received_value).",
            "This answers why value cards differ without misusing open/partial status.",
        )

    zero_open = outputs["po_gap_with_zero_open_status_truth"].sort_values(
        "po_vs_receipt_gap", ascending=False
    )
    for _, row in zero_open.head(10).iterrows():
        add_prediction(
            rows,
            "03_Vendor_Procurement_Analytics",
            "Gap-with-zero-open validation",
            f"Outlet = {row['outlet_name']}; Vendor = {row['vendor_name']}; Date Range = full Month 1",
            "Value gap should be positive while open/partial status count remains zero.",
            f"PO {money(row['po_raised_value'])}; Receipt {money(row['receipt_booked_value'])}; Gap {money(row['po_vs_receipt_gap'])}; Open/partial 0",
            "FACT_Vendor_Spend",
            "This proves value gap and status count are separate KPIs.",
            "Use this in the demo if someone asks why raised and booked values differ.",
        )

    for _, row in po_status.iterrows():
        add_prediction(
            rows,
            "03_Vendor_Procurement_Analytics",
            "PO Status Count/Value",
            f"Outlet = {row['outlet_name']}; PO Status = {row['po_status']}",
            "Status chart should show this status bucket for the selected outlet.",
            f"{number(row['po_lines'])} lines; {money(row['po_raised_value'])} PO value; remaining est {money(row['remaining_value_est'])}",
            "FACT_Purchase_Order",
            "X po_status, Y COUNT rows or SUM(total_item_cost).",
            "This validates PO Status filter and cancelled/closed/open distinction.",
        )

    for outlet_name in outlet_summary["outlet_name"]:
        latest = inventory_latest[inventory_latest["outlet_name"] == outlet_name]
        low_count = int((latest["inventory_pressure_band"] == "Low").sum())
        watch_count = int((latest["inventory_pressure_band"] == "Watch").sum())
        top_inv_item = latest.sort_values("total_amt", ascending=False).iloc[0]
        top_inv_cat = (
            latest.groupby(["category_name", "super_category_name"], as_index=False)
            .agg(latest_inventory_value=("total_amt", "sum"))
            .sort_values("latest_inventory_value", ascending=False)
            .iloc[0]
        )
        top_theoretical = theoretical[theoretical["outlet_name"] == outlet_name].sort_values(
            "total_theoretical_qty", ascending=False
        ).iloc[0]
        add_prediction(
            rows,
            "04_Inventory_Consumption_Intelligence",
            "Latest Inventory Pressure KPIs",
            f"Outlet = {outlet_name}; Latest inventory snapshot",
            "Low/Watch item counts should match the latest inventory snapshot.",
            f"Low {low_count}; Watch {watch_count}; top value item {top_inv_item['item_name']} at {money(top_inv_item['total_amt'])}",
            "SUM_Inventory_Risk",
            "Use latest snapshot table for current inventory pressure, not a date-summed fact unless item-days are intended.",
            "This separates current low-stock count from historical item-days.",
        )
        add_prediction(
            rows,
            "04_Inventory_Consumption_Intelligence",
            "Inventory Value By Category",
            f"Outlet = {outlet_name}",
            "Top inventory value category should match the latest inventory snapshot.",
            f"{top_inv_cat['category_name']} latest value {money(top_inv_cat['latest_inventory_value'])}",
            "SUM_Inventory_Risk",
            "X category_name, Y SUM(total_amt). Do not sum FACT_Inventory_Closing across dates for a current inventory chart.",
            "Shows where stock capital is sitting by material category.",
        )
        add_prediction(
            rows,
            "04_Inventory_Consumption_Intelligence",
            "Top Theoretical Ingredients",
            f"Outlet = {outlet_name}; Month 1 sales",
            "The leading theoretical ingredient should match recipe BOM x sales computation.",
            f"{top_theoretical['ingredient_name']} = {number(top_theoretical['total_theoretical_qty'], 1)} {top_theoretical['ingredient_unit']}; top menu drivers {top_theoretical['top_menu_items']}",
            "FACT_Theoretical_Consumption",
            "Y should be SUM(theoretical_ingredient_qty), not inventory quantity.",
            "This connects menu sales to material demand.",
        )

    for _, row in event_lift.iterrows():
        add_prediction(
            rows,
            "05_Calendar_Event_Competitor_Intelligence",
            "Event Lift / Spike Explanation",
            f"Event = {row['event_name']}; Outlet = {row['outlet_name']}",
            "Event panel should show computed event sales and baseline lift.",
            f"Event sales {money(row['event_day_sales'])}; Baseline {money(row['baseline_sales'])}; Lift {pct(row['sales_lift_pct'])}",
            "SUM_Event_Impact / SUM_Event_Markers",
            "Use event table filters for event visuals; do not infer causality from lift.",
            "This is the calendar story to explain spikes.",
        )

    for _, row in competitor.groupby(["outlet_name", "market_area"], dropna=False).head(3).iterrows():
        add_prediction(
            rows,
            "05_Calendar_Event_Competitor_Intelligence",
            "Competitor Price Positioning",
            f"Outlet/Market = {row['outlet_name']} / {row['market_area']}; Category = {row['competitor_category']}",
            "Price positioning chart should use market area and competitor category context.",
            f"Avg price index {number(row['avg_price_index'], 2)}; avg difference {money(row['avg_price_difference'])}; position {row['price_position']}",
            "SUM_Competitor_Positioning",
            "Use market_area for competitor filters because competitor data is market-contextual.",
            "This tells whether ABNAH is premium/discounted against nearby competitors.",
        )

    predictions = pd.DataFrame(rows)
    predictions.insert(0, "prediction_id", range(1, len(predictions) + 1))
    return predictions


def build_outputs(data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    health = build_daily_health(data)
    vendor_spend = build_vendor_spend(data)
    event_lift = build_event_lift(data)
    theoretical = build_theoretical_consumption_summary(data)
    competitor_positioning = build_competitor_positioning_summary(data)
    sales = data["sales"]
    purchase = data["purchase"]
    inventory = data["inventory"]

    active_vendor_base = (
        vendor_spend.groupby(["outlet_code", "outlet_name"], dropna=False)
        .agg(active_vendors=("vendor_name", "nunique"))
        .reset_index()
    )

    outlet_summary = (
        health.groupby(["outlet_code", "outlet_name", "market_area"], dropna=False)
        .agg(
            active_days=("activity_date", "nunique"),
            net_sales=("net_sales", "sum"),
            sold_qty=("sold_qty", "sum"),
            po_raised_value=("po_value", "sum"),
            receipt_booked_value=("receipt_value", "sum"),
            avg_inventory_value=("inventory_value", "mean"),
            inventory_pressure_item_days=("low_stock_item_count", "sum"),
            watch_stock_item_days=("watch_stock_item_count", "sum"),
            event_day_markers=("event_count", "sum"),
            po_open_or_partial_status_count=("open_or_partial_po_count", "sum"),
            po_pending_or_partial_flag_count=("pending_or_partial_po_count", "sum"),
            remaining_value_est=("remaining_value_est", "sum"),
        )
        .reset_index()
    )
    outlet_summary["avg_daily_revenue"] = outlet_summary["net_sales"] / outlet_summary["active_days"]
    outlet_summary["po_vs_receipt_gap"] = (
        outlet_summary["po_raised_value"] - outlet_summary["receipt_booked_value"]
    )
    outlet_summary["purchase_to_sales_pct"] = (
        outlet_summary["po_raised_value"] / outlet_summary["net_sales"] * 100
    )
    outlet_summary["revenue_per_avg_inventory_rupee"] = (
        outlet_summary["net_sales"] / outlet_summary["avg_inventory_value"]
    )
    outlet_summary = outlet_summary.merge(active_vendor_base, on=["outlet_code", "outlet_name"], how="left")
    outlet_summary = outlet_summary.merge(pd.DataFrame(OUTLETS), on=["outlet_code", "outlet_name", "market_area"], how="left")
    outlet_summary = outlet_summary.sort_values("net_sales", ascending=False)

    sales_category = (
        sales.groupby(["outlet_code", "outlet_name", "super_category", "category"], dropna=False)
        .agg(net_sales=("net_sale", "sum"), qty=("qty", "sum"), line_count=("row_id", "count"))
        .reset_index()
    )
    sales_category["sales_share_pct"] = sales_category.groupby("outlet_name")["net_sales"].transform(
        lambda s: s / s.sum() * 100
    )
    sales_category = sales_category.sort_values(["outlet_name", "net_sales"], ascending=[True, False])

    menu_item = (
        sales.groupby(
            [
                "outlet_code",
                "outlet_name",
                "market_area",
                "item_number",
                "item_name",
                "super_category",
                "category",
            ],
            dropna=False,
        )
        .agg(
            total_qty=("qty", "sum"),
            total_net_sale=("net_sale", "sum"),
            avg_realized_unit_price=("net_sale_per_qty", "mean"),
            selling_days=("sales_date", "nunique"),
        )
        .reset_index()
    )
    menu_item["sales_rank_in_outlet"] = menu_item.groupby("outlet_name")["total_net_sale"].rank(
        ascending=False, method="dense"
    )
    menu_item = menu_item.sort_values(["outlet_name", "total_net_sale"], ascending=[True, False])

    vendor_outlet = (
        vendor_spend.groupby(["outlet_code", "outlet_name", "market_area", "vendor_name"], dropna=False)
        .agg(
            po_raised_value=("ordered_value", "sum"),
            receipt_booked_value=("received_value", "sum"),
            po_line_count=("po_line_count", "sum"),
            receipt_line_count=("receipt_line_count", "sum"),
            open_or_partial_status_count=("open_or_partial_po_count", "sum"),
            pending_or_partial_flag_count=("pending_or_partial_flag_count", "sum"),
            remaining_value_est=("remaining_value_est", "sum"),
        )
        .reset_index()
    )
    vendor_outlet["po_vs_receipt_gap"] = (
        vendor_outlet["po_raised_value"] - vendor_outlet["receipt_booked_value"]
    )
    vendor_outlet["receipt_coverage_pct"] = (
        vendor_outlet["receipt_booked_value"] / vendor_outlet["po_raised_value"].replace(0, pd.NA) * 100
    ).fillna(0)
    vendor_outlet = vendor_outlet.sort_values(
        ["outlet_name", "po_raised_value"], ascending=[True, False]
    )

    vendor_material_status = (
        vendor_spend.groupby(
            ["outlet_name", "vendor_name", "item_name", "category_name", "po_status"],
            dropna=False,
        )
        .agg(
            po_raised_value=("ordered_value", "sum"),
            receipt_booked_value=("received_value", "sum"),
            po_line_count=("po_line_count", "sum"),
            receipt_line_count=("receipt_line_count", "sum"),
            open_or_partial_status_count=("open_or_partial_po_count", "sum"),
            pending_or_partial_flag_count=("pending_or_partial_flag_count", "sum"),
            remaining_value_est=("remaining_value_est", "sum"),
        )
        .reset_index()
    )
    vendor_material_status["po_vs_receipt_gap"] = (
        vendor_material_status["po_raised_value"]
        - vendor_material_status["receipt_booked_value"]
    )
    vendor_material_status["activity_value"] = (
        vendor_material_status["po_raised_value"].abs()
        + vendor_material_status["receipt_booked_value"].abs()
    )
    vendor_material_status = vendor_material_status.sort_values(
        "activity_value", ascending=False
    )

    po_status_summary = (
        purchase.groupby(["outlet_name", "po_status"], dropna=False)
        .agg(
            po_lines=("row_id", "count"),
            po_raised_value=("total_item_cost", "sum"),
            ordered_qty=("ordered_qty", "sum"),
            processed_qty=("processed_qty", "sum"),
            remaining_qty=("remaining_qty", "sum"),
            remaining_value_est=("remaining_value_est", "sum"),
        )
        .reset_index()
    )
    po_status_summary = po_status_summary.sort_values(["outlet_name", "po_status"])

    gap_zero_open = vendor_outlet[
        (vendor_outlet["po_raised_value"] > vendor_outlet["receipt_booked_value"])
        & (vendor_outlet["open_or_partial_status_count"] == 0)
    ].sort_values("po_vs_receipt_gap", ascending=False)

    inventory_latest = inventory.loc[
        inventory.groupby(["outlet_name", "item_code"])["inventory_date"].idxmax()
    ].copy()
    inventory_latest = inventory_latest.sort_values(
        ["outlet_name", "low_stock_flag", "total_amt"],
        ascending=[True, False, False],
    )

    inventory_category = (
        inventory.groupby(["outlet_name", "category_name", "super_category_name"], dropna=False)
        .agg(
            avg_inventory_value=("total_amt", "mean"),
            latest_total_amt=("total_amt", "last"),
            low_stock_item_days=("low_stock_flag", "sum"),
            avg_total_qty=("total_qty", "mean"),
        )
        .reset_index()
        .sort_values(["outlet_name", "avg_inventory_value"], ascending=[True, False])
    )

    daily_sales_rank = health.sort_values(["outlet_name", "net_sales"], ascending=[True, False])

    qa_rows: list[dict] = []
    for _, row in sales_category.iterrows():
        qa_rows.append(
            {
                "domain": "Sales category",
                "filter_1": row["outlet_name"],
                "filter_2": row["category"],
                "filter_3": row["super_category"],
                "expected_measure": "SUM(net_sale)",
                "expected_value": round(row["net_sales"], 2),
                "expected_display": money(row["net_sales"]),
                "source_table": "FACT_Sales",
                "note": "Use FACT_Sales so outlet, date, category and item filters work.",
            }
        )
    for _, row in menu_item.head(90).iterrows():
        qa_rows.append(
            {
                "domain": "Menu item",
                "filter_1": row["outlet_name"],
                "filter_2": row["category"],
                "filter_3": row["item_name"],
                "expected_measure": "SUM(net_sale)",
                "expected_value": round(row["total_net_sale"], 2),
                "expected_display": money(row["total_net_sale"]),
                "source_table": "FACT_Sales or date-safe menu query",
                "note": "SUM_Menu_Item_Performance is month-level. Use FACT_Sales for date-sensitive tests.",
            }
        )
    for _, row in vendor_material_status.head(95).iterrows():
        qa_rows.append(
            {
                "domain": "Procurement vendor/material/status",
                "filter_1": row["outlet_name"],
                "filter_2": row["vendor_name"],
                "filter_3": row["item_name"],
                "expected_measure": f"PO {row['po_status']}",
                "expected_value": round(row["po_raised_value"] + row["receipt_booked_value"], 2),
                "expected_display": (
                    f"PO {money(row['po_raised_value'])}; "
                    f"Receipt {money(row['receipt_booked_value'])}; "
                    f"Open {number(row['open_or_partial_status_count'])}"
                ),
                "source_table": "FACT_Vendor_Spend",
                "note": "PO Status only exists on PO rows; receipt rows have no PO status.",
            }
        )
    for _, row in daily_sales_rank.head(45).iterrows():
        qa_rows.append(
            {
                "domain": "Daily outlet health",
                "filter_1": row["outlet_name"],
                "filter_2": str(row["activity_date"]),
                "filter_3": row["health_note"],
                "expected_measure": "SUM(net_sales)",
                "expected_value": round(row["net_sales"], 2),
                "expected_display": money(row["net_sales"]),
                "source_table": "FACT_Outlet_Daily_Health",
                "note": f"Event names: {row['event_names'] or 'None'}",
            }
        )
    for _, row in inventory_latest.head(45).iterrows():
        qa_rows.append(
            {
                "domain": "Latest inventory pressure",
                "filter_1": row["outlet_name"],
                "filter_2": row["category_name"],
                "filter_3": row["item_name"],
                "expected_measure": "latest total_qty / total_amt",
                "expected_value": round(row["total_amt"], 2),
                "expected_display": f"Qty {number(row['total_qty'], 1)}; Value {money(row['total_amt'])}; Band {row['inventory_pressure_band']}",
                "source_table": "SUM_Inventory_Risk for latest, FACT_Inventory_Closing for date-sensitive",
                "note": "low_stock_flag is total_qty <= 10 in the Zoho SQL.",
            }
        )
    qa_bank = pd.DataFrame(qa_rows).head(220)

    outputs = {
        "fact_outlet_daily_health_truth": health,
        "outlet_summary_truth": outlet_summary,
        "fact_vendor_spend_truth": vendor_spend,
        "vendor_outlet_truth": vendor_outlet,
        "vendor_material_status_truth": vendor_material_status,
        "po_status_summary_truth": po_status_summary,
        "po_gap_with_zero_open_status_truth": gap_zero_open,
        "sales_category_truth": sales_category,
        "menu_item_truth": menu_item,
        "inventory_latest_truth": inventory_latest,
        "inventory_category_truth": inventory_category,
        "theoretical_consumption_summary_truth": theoretical,
        "event_lift_truth": event_lift,
        "competitor_positioning_truth": competitor_positioning,
        "qa_filter_bank_month1": qa_bank,
    }
    outputs["dashboard_prediction_pack_month1"] = build_dashboard_predictions(data, outputs)
    return outputs


def audit_query_sql() -> pd.DataFrame:
    rows = []
    for path in sorted(SQL_DIR.glob("*.sql")):
        text = path.read_text(encoding="utf-8")
        table_match = re.search(r"-- Query Table:\s*(.+)", text)
        purpose_match = re.search(r"-- Purpose:\s*(.+)", text)
        sources_match = re.search(r"-- Sources:\s*(.+)", text)
        table_name = table_match.group(1).strip() if table_match else path.stem
        has_date = bool(
            re.search(
                r'"(sales_date|activity_date|po_date|receipt_date|inventory_date|event_date|start_date|date_value|latest_inventory_date)"',
                text,
            )
        )
        layer = table_name.split("_", 1)[0]
        note = "Date-safe for matching date field filters." if has_date else "No date grain; do not expect dashboard Date Range to change this table."
        if table_name in {"SUM_Menu_Item_Performance", "SUM_Sales_Category_Mix"}:
            note = "Month-level sales summary. Use FACT_Sales for date-sensitive charts."
        elif table_name == "SUM_Vendor_Share":
            note = "Month-level vendor summary. Use FACT_Vendor_Spend for date/vendor/material filters."
        elif table_name == "SUM_Inventory_Risk":
            note = "Latest inventory snapshot only. Use FACT_Inventory_Closing for inventory date filters."
        elif table_name == "FACT_Vendor_Spend":
            note = "Unified PO and receipt fact. PO Status applies only to PO rows; receipt rows do not carry PO status."
        elif table_name == "FACT_PO_Receipt_Comparison":
            note = "Approximate PO/receipt matching because entry rows have no po_number."
        rows.append(
            {
                "file": path.name,
                "query_table": table_name,
                "layer": layer,
                "sources": sources_match.group(1).strip() if sources_match else "",
                "purpose": purpose_match.group(1).strip() if purpose_match else "",
                "has_date_field": "Yes" if has_date else "No",
                "dashboard_filter_note": note,
            }
        )
    return pd.DataFrame(rows)


def write_csv_outputs(outputs: dict[str, pd.DataFrame], query_audit: pd.DataFrame) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, df in outputs.items():
        df.to_csv(OUT_DIR / f"{name}.csv", index=False)
    query_audit.to_csv(OUT_DIR / "query_table_audit.csv", index=False)


def build_readme(data: dict[str, pd.DataFrame], outputs: dict[str, pd.DataFrame], query_audit: pd.DataFrame) -> str:
    sales = data["sales"]
    purchase = data["purchase"]
    entry = data["entry"]
    inventory = data["inventory"]
    outlet_summary = outputs["outlet_summary_truth"].copy()
    vendor_outlet = outputs["vendor_outlet_truth"].copy()
    vendor_material_status = outputs["vendor_material_status_truth"].copy()
    sales_category = outputs["sales_category_truth"].copy()
    menu_item = outputs["menu_item_truth"].copy()
    inventory_latest = outputs["inventory_latest_truth"].copy()
    event_lift = outputs["event_lift_truth"].copy()
    qa_bank = outputs["qa_filter_bank_month1"].copy()
    dashboard_predictions = outputs["dashboard_prediction_pack_month1"].copy()

    lines: list[str] = []
    lines.append("# Month 1 Truth Reference For Zoho Dashboard QA")
    lines.append("")
    lines.append("This file is generated from the actual Month 1 synthetic CSVs in `data/month_01` plus the static master CSVs in `data/static`.")
    lines.append("")
    lines.append("It exists for one reason: while building Zoho dashboards, do not guess. Use these computed truths to test whether filters, KPI cards, charts, and query-table grains are behaving correctly.")
    lines.append("")
    lines.append("Generated by:")
    lines.append("")
    lines.append("```powershell")
    lines.append("python scripts/analyze_month1_truth.py")
    lines.append("```")
    lines.append("")
    lines.append("## Source Files Checked")
    lines.append("")
    lines.append(md_table(
        pd.DataFrame(
            [
                {"area": "Sales", "rows": len(sales), "grain": "outlet + date + menu item aggregate row"},
                {"area": "Purchase orders", "rows": len(purchase), "grain": "outlet + PO line + material/vendor/status"},
                {"area": "Receipt entries", "rows": len(entry), "grain": "outlet + receipt/entry line + material/vendor"},
                {"area": "Inventory closing", "rows": len(inventory), "grain": "outlet + date + material closing stock"},
                {"area": "Menu master", "rows": len(data["menu"]), "grain": "menu item master"},
                {"area": "Recipe BOM", "rows": len(data["recipe"]), "grain": "menu item + ingredient mapping"},
                {"area": "Manual events", "rows": len(data["events"]), "grain": "event annotation"},
                {"area": "Competitor pricing", "rows": len(data["competitors"]), "grain": "market competitor item mapping"},
                {"area": "Vendor report", "rows": len(data["vendors"]), "grain": "vendor/material master rows"},
            ]
        ),
        ["area", "rows", "grain"],
        ["Area", "Rows", "Grain"],
        {"rows": "number0"},
    ))
    lines.append("")
    lines.append("## Month 1 Executive Truth")
    lines.append("")
    lines.append(md_table(
        outlet_summary,
        [
            "outlet_name",
            "net_sales",
            "avg_daily_revenue",
            "po_raised_value",
            "receipt_booked_value",
            "po_vs_receipt_gap",
            "purchase_to_sales_pct",
            "revenue_per_avg_inventory_rupee",
            "inventory_pressure_item_days",
            "active_vendors",
        ],
        [
            "Outlet",
            "Net sales",
            "Avg daily revenue",
            "PO raised",
            "Receipt booked",
            "PO vs receipt gap",
            "PO/Sales",
            "Revenue per avg inv rupee",
            "Inventory pressure item-days",
            "Active vendors",
        ],
        {
            "net_sales": "money",
            "avg_daily_revenue": "money",
            "po_raised_value": "money",
            "receipt_booked_value": "money",
            "po_vs_receipt_gap": "money",
            "purchase_to_sales_pct": "pct",
            "revenue_per_avg_inventory_rupee": "number2",
            "inventory_pressure_item_days": "number2",
            "active_vendors": "number2",
        },
    ))
    lines.append("")
    lines.append("Executive card formulas that should match Zoho:")
    lines.append("")
    lines.append("- `Net Sales Revenue`: `SUM(FACT_Outlet_Daily_Health.net_sales)`.")
    lines.append("- `Average Daily Revenue`: `SUM(net_sales) / DISTINCTCOUNT(activity_date)`.")
    lines.append("- `PO Raised Value`: `SUM(FACT_Vendor_Spend.ordered_value)` or `SUM(FACT_Outlet_Daily_Health.po_value)` depending on dashboard.")
    lines.append("- `Receipt Booked Value`: `SUM(FACT_Vendor_Spend.received_value)` or `SUM(FACT_Outlet_Daily_Health.receipt_value)`.")
    lines.append("- `PO vs Receipt Value Gap`: `SUM(ordered_value) - SUM(received_value)`.")
    lines.append("- `Revenue Per Avg Inventory Rupee`: `SUM(net_sales) * DISTINCTCOUNT(activity_date) / SUM(inventory_value)` when using `FACT_Outlet_Daily_Health`.")
    lines.append("- `Inventory Pressure Item-Days`: `SUM(low_stock_item_count)` from `FACT_Outlet_Daily_Health`; this is not current item count.")
    lines.append("")
    lines.append("## Required Zoho Query Update From This Audit")
    lines.append("")
    lines.append("The audit tightened `STD_Purchase_Report.is_open_or_partial`.")
    lines.append("")
    lines.append("Correct definition:")
    lines.append("")
    lines.append("```text")
    lines.append("1 only when po_status is Pending / Partially Received, or remaining_qty > 0")
    lines.append("0 for Closed and Cancelled rows with no remaining quantity")
    lines.append("```")
    lines.append("")
    lines.append("If Zoho already has the old query table, update `02_std_purchase_report.sql` first, then refresh/recreate dependent tables that use purchase status:")
    lines.append("")
    lines.append("```text")
    lines.append("STD_Purchase_Report")
    lines.append("FACT_Purchase_Order")
    lines.append("FACT_PO_Receipt_Comparison")
    lines.append("FACT_Outlet_Daily_Health")
    lines.append("FACT_Vendor_Spend")
    lines.append("SUM_Vendor_Share")
    lines.append("SUM_Outlet_Health")
    lines.append("```")
    lines.append("")
    lines.append("## Pre-Mediated Dashboard Predictions")
    lines.append("")
    lines.append("Use this section before building or testing each dashboard. These are not assumptions. They are computed Month 1 expectations from the synthetic source files.")
    lines.append("")
    lines.append("Full prediction/assertion pack:")
    lines.append("")
    lines.append("```text")
    lines.append("docs/month1_truth_tables/dashboard_prediction_pack_month1.csv")
    lines.append("```")
    lines.append("")
    lines.append("Prediction pack columns:")
    lines.append("")
    lines.append("- `dashboard`: which dashboard module the assertion belongs to.")
    lines.append("- `visual`: KPI, chart, table, or filter behavior being tested.")
    lines.append("- `filter_setup`: exact filter state to apply in Zoho.")
    lines.append("- `expected_result`: what should happen.")
    lines.append("- `expected_value`: exact value or leading item/vendor/category expected.")
    lines.append("- `source_table`: the Zoho Query Table that should drive the visual.")
    lines.append("- `validation_rule`: how to know the visual is wired correctly.")
    lines.append("- `demo_story`: how to explain the result in the demo.")
    lines.append("")
    for dashboard_name in dashboard_predictions["dashboard"].drop_duplicates():
        dash_rows = dashboard_predictions[
            dashboard_predictions["dashboard"] == dashboard_name
        ].head(8)
        lines.append(f"### {dashboard_name}")
        lines.append("")
        lines.append(md_table(
            dash_rows,
            [
                "visual",
                "filter_setup",
                "expected_result",
                "expected_value",
                "source_table",
                "validation_rule",
            ],
            [
                "Visual",
                "Filter setup",
                "Expected result",
                "Expected value",
                "Source table",
                "Validation rule",
            ],
        ))
        lines.append("")
    lines.append("## Cafe Stories From The Month 1 Data")
    lines.append("")
    for _, outlet in outlet_summary.iterrows():
        outlet_name = outlet["outlet_name"]
        cats = sales_category[sales_category["outlet_name"] == outlet_name].head(5)
        top_items = menu_item[menu_item["outlet_name"] == outlet_name].head(5)
        vendors = vendor_outlet[vendor_outlet["outlet_name"] == outlet_name].head(5)
        inv = inventory_latest[inventory_latest["outlet_name"] == outlet_name]
        low_count = int((inv["inventory_pressure_band"] == "Low").sum())
        watch_count = int((inv["inventory_pressure_band"] == "Watch").sum())
        lines.append(f"### {outlet_name}")
        lines.append("")
        lines.append(f"- Persona: {outlet['persona']}.")
        lines.append(f"- Demand profile: {outlet['weekday_profile']}.")
        lines.append(f"- Month 1 truth: {money(outlet['net_sales'])} sales, {money(outlet['po_raised_value'])} PO raised, {money(outlet['receipt_booked_value'])} receipt booked.")
        lines.append(f"- Operating read: PO/Sales is {pct(outlet['purchase_to_sales_pct'])}; revenue per average inventory rupee is {number(outlet['revenue_per_avg_inventory_rupee'], 2)}.")
        lines.append(f"- Inventory read: {number(outlet['inventory_pressure_item_days'])} pressure item-days; latest snapshot has {low_count} Low items and {watch_count} Watch items.")
        lines.append("- Leading sales categories:")
        lines.append(md_table(
            cats,
            ["category", "super_category", "net_sales", "sales_share_pct", "qty"],
            ["Category", "Super category", "Net sales", "Outlet share", "Menu units"],
            {"net_sales": "money", "sales_share_pct": "pct", "qty": "number1"},
        ))
        lines.append("")
        lines.append("- Top menu items by revenue:")
        lines.append(md_table(
            top_items,
            ["item_name", "category", "total_net_sale", "total_qty", "avg_realized_unit_price"],
            ["Item", "Category", "Net sales", "Units", "Avg realized price"],
            {"total_net_sale": "money", "total_qty": "number1", "avg_realized_unit_price": "money"},
        ))
        lines.append("")
        lines.append("- Top vendors by PO raised value:")
        lines.append(md_table(
            vendors,
            [
                "vendor_name",
                "po_raised_value",
                "receipt_booked_value",
                "po_vs_receipt_gap",
                "open_or_partial_status_count",
            ],
            ["Vendor", "PO raised", "Receipt booked", "Gap", "Open/partial status count"],
            {
                "po_raised_value": "money",
                "receipt_booked_value": "money",
                "po_vs_receipt_gap": "money",
                "open_or_partial_status_count": "number2",
            },
        ))
        lines.append("")
    lines.append("## Vendor And Procurement Truth")
    lines.append("")
    lines.append("Use these rules in the demo and in Zoho setup:")
    lines.append("")
    lines.append("- `PO Raised Value` means purchase order line value from `purchase_report.total_item_cost`.")
    lines.append("- `Receipt Booked Value` means goods/entry receipt value from `entry_report.grand_total`.")
    lines.append("- `PO Raised Value` can be higher than `Receipt Booked Value` even when `Open / Partial PO Status Count` is zero. That means there is a value gap in the selected period, not necessarily an open-status PO.")
    lines.append("- Receipt rows do not carry `po_number` or `po_status`. Because of that, `PO Status` should be mapped only to PO status visuals and the open/partial KPI, not to receipt booked value.")
    lines.append("- If you want a card that explains the gap, add `PO vs Receipt Value Gap = SUM(ordered_value) - SUM(received_value)`.")
    lines.append("")
    lines.append("Top vendor/outlet truth:")
    lines.append("")
    lines.append(md_table(
        vendor_outlet.sort_values("po_raised_value", ascending=False).head(20),
        [
            "outlet_name",
            "vendor_name",
            "po_raised_value",
            "receipt_booked_value",
            "po_vs_receipt_gap",
            "receipt_coverage_pct",
            "open_or_partial_status_count",
            "pending_or_partial_flag_count",
            "remaining_value_est",
        ],
        [
            "Outlet",
            "Vendor",
            "PO raised",
            "Receipt booked",
            "Gap",
            "Receipt coverage",
            "Open/partial status",
            "Pending/partial flag",
            "Remaining value est",
        ],
        {
            "po_raised_value": "money",
            "receipt_booked_value": "money",
            "po_vs_receipt_gap": "money",
            "receipt_coverage_pct": "pct",
            "open_or_partial_status_count": "number2",
            "pending_or_partial_flag_count": "number2",
            "remaining_value_est": "money",
        },
    ))
    lines.append("")
    zero_open = outputs["po_gap_with_zero_open_status_truth"].head(20)
    lines.append("Cases where PO raised value is higher than receipt booked value while open/partial status count is zero:")
    lines.append("")
    lines.append(md_table(
        zero_open,
        ["outlet_name", "vendor_name", "po_raised_value", "receipt_booked_value", "po_vs_receipt_gap"],
        ["Outlet", "Vendor", "PO raised", "Receipt booked", "Gap"],
        {
            "po_raised_value": "money",
            "receipt_booked_value": "money",
            "po_vs_receipt_gap": "money",
        },
    ))
    lines.append("")
    lines.append("This is the direct answer to the confusing screenshot pattern: zero open/partial status count does not mean PO value equals receipt value. It only means no selected PO line is currently marked `Pending` / `Partially Received` or carrying a positive remaining quantity.")
    lines.append("")
    lines.append("PO status truth by outlet:")
    lines.append("")
    lines.append(md_table(
        outputs["po_status_summary_truth"],
        ["outlet_name", "po_status", "po_lines", "po_raised_value", "ordered_qty", "processed_qty", "remaining_qty", "remaining_value_est"],
        ["Outlet", "PO status", "PO lines", "PO raised", "Ordered qty", "Processed qty", "Remaining qty", "Remaining value est"],
        {
            "po_lines": "number2",
            "po_raised_value": "money",
            "ordered_qty": "number1",
            "processed_qty": "number1",
            "remaining_qty": "number1",
            "remaining_value_est": "money",
        },
    ))
    lines.append("")
    lines.append("## Sales And Menu Truth")
    lines.append("")
    lines.append("For date-sensitive sales charts, use `FACT_Sales`. Do not use `SUM_Sales_Category_Mix` for date-filtered category mix because that summary has no sales date grain.")
    lines.append("")
    lines.append("Month 1 category mix by outlet:")
    lines.append("")
    lines.append(md_table(
        sales_category.head(30),
        ["outlet_name", "category", "super_category", "net_sales", "sales_share_pct", "qty"],
        ["Outlet", "Category", "Super category", "Net sales", "Outlet share", "Menu units"],
        {"net_sales": "money", "sales_share_pct": "pct", "qty": "number1"},
    ))
    lines.append("")
    lines.append("Top 20 menu items overall:")
    lines.append("")
    lines.append(md_table(
        menu_item.sort_values("total_net_sale", ascending=False).head(20),
        ["outlet_name", "item_name", "category", "total_net_sale", "total_qty", "avg_realized_unit_price"],
        ["Outlet", "Item", "Category", "Net sales", "Units", "Avg realized price"],
        {"total_net_sale": "money", "total_qty": "number1", "avg_realized_unit_price": "money"},
    ))
    lines.append("")
    lines.append("Menu-item table repeat rule:")
    lines.append("")
    lines.append("- `SUM_Menu_Item_Performance` is at outlet + item grain. If no outlet filter is selected, the same menu item can appear once per outlet. That is expected, not a duplicate.")
    lines.append("- If you need one row per item across all outlets, create a Summary/Pivot View from `SUM_Menu_Item_Performance` with `item_number` and `item_name` as rows, then aggregate `total_net_sale` and `total_qty`.")
    lines.append("- If you need Date Range to change the table, build the table from `FACT_Sales`, not from `SUM_Menu_Item_Performance`.")
    lines.append("")
    lines.append("## Event Truth")
    lines.append("")
    lines.append("Month 1 has two configured event stories: the Coffee Subscription Launch on 2026-01-15 to 2026-01-16 for Connaught Place and Saket Premium, and the Republic Day leisure/corporate contrast on 2026-01-26 for all outlets.")
    lines.append("")
    lines.append(md_table(
        event_lift,
        [
            "event_name",
            "outlet_name",
            "affected_category",
            "event_days",
            "event_day_sales",
            "baseline_sales",
            "sales_lift_value",
            "sales_lift_pct",
            "expected_impact_pct",
        ],
        [
            "Event",
            "Outlet",
            "Affected categories",
            "Event days",
            "Event sales",
            "Baseline sales",
            "Lift value",
            "Lift %",
            "Expected impact",
        ],
        {
            "event_day_sales": "money",
            "baseline_sales": "money",
            "sales_lift_value": "money",
            "sales_lift_pct": "pct",
            "expected_impact_pct": "pct",
        },
    ))
    lines.append("")
    lines.append("Use event lift as explanatory context, not proof of causality.")
    lines.append("")
    lines.append("## Inventory Truth")
    lines.append("")
    lines.append("Current Zoho SQL defines low stock as `total_qty <= 10`. That is a simple pressure heuristic. It does not use ingredient-specific thresholds from the generator.")
    lines.append("")
    lines.append("Latest inventory pressure sample:")
    lines.append("")
    lines.append(md_table(
        inventory_latest.sort_values(["low_stock_flag", "total_amt"], ascending=[False, False]).head(30),
        ["outlet_name", "item_name", "category_name", "total_qty", "total_amt", "inventory_pressure_band"],
        ["Outlet", "Item", "Category", "Latest qty", "Latest value", "Band"],
        {"total_qty": "number1", "total_amt": "money"},
    ))
    lines.append("")
    lines.append("Use `SUM_Inventory_Risk` for latest-stock cards and latest low-stock tables. Use `FACT_Inventory_Closing` for inventory-date charts.")
    lines.append("")
    lines.append("## Filter Architecture To Use In Zoho")
    lines.append("")
    filter_rows = pd.DataFrame(
        [
            {
                "dashboard": "01 Executive Outlet Health",
                "primary_table": "FACT_Outlet_Daily_Health",
                "filter_order": "Outlet -> Date Range -> Event Type",
                "mapping": "Outlet maps to outlet_name; Date Range maps to activity_date. Event Type maps only to event tables.",
            },
            {
                "dashboard": "02 Sales Menu Intelligence",
                "primary_table": "FACT_Sales",
                "filter_order": "Outlet -> Sales Date -> Super Category -> Category -> Menu Item",
                "mapping": "Build category mix and date-sensitive top items from FACT_Sales. Summary item tables are not date-safe.",
            },
            {
                "dashboard": "03 Vendor Procurement Analytics",
                "primary_table": "FACT_Vendor_Spend",
                "filter_order": "Outlet -> Procurement Date -> Vendor -> Material -> Category; PO Status separate",
                "mapping": "Outlet/date/vendor/material apply to PO and receipt cards. PO Status applies only to PO status/open-count visuals.",
            },
            {
                "dashboard": "04 Inventory Consumption Intelligence",
                "primary_table": "FACT_Inventory_Closing for date charts; SUM_Inventory_Risk for latest snapshot",
                "filter_order": "Outlet -> Inventory Date -> Category -> Inventory Item -> Pressure Band",
                "mapping": "Do not expect SUM_Inventory_Risk to respond to historical inventory date ranges.",
            },
            {
                "dashboard": "05 Calendar Event Competitor Intelligence",
                "primary_table": "SUM_Event_Impact, SUM_Event_Markers, SUM_Competitor_Positioning",
                "filter_order": "Outlet/Market -> Event Type -> Competitor Category -> Price Position -> Item",
                "mapping": "Event and competitor data are contextual. Use market_area for competitor filters.",
            },
        ]
    )
    lines.append(md_table(filter_rows, ["dashboard", "primary_table", "filter_order", "mapping"], ["Dashboard", "Primary table", "Filter order", "Mapping rule"]))
    lines.append("")
    lines.append("Zoho build rule for cascading filters:")
    lines.append("")
    lines.append("1. Create the broadest dropdown first from the dashboard primary table.")
    lines.append("2. Create narrow dropdowns from the same primary table when possible.")
    lines.append("3. Enable `List only relevant values` for each dropdown.")
    lines.append("4. If a widget does not change, open the widget and map the dashboard filter to that widget source table's own field.")
    lines.append("5. Do not rely on `DIM_*` filters until direct source-table filters work.")
    lines.append("")
    lines.append("## Query Table Audit")
    lines.append("")
    lines.append(md_table(
        query_audit,
        ["query_table", "sources", "has_date_field", "dashboard_filter_note"],
        ["Query table", "Sources", "Date field", "Filter note"],
        max_rows=60,
    ))
    lines.append("")
    lines.append("## Dashboard Source Corrections")
    lines.append("")
    correction_rows = pd.DataFrame(
        [
            {
                "issue": "Category revenue mix does not change with date filters",
                "cause": "Built from SUM_Sales_Category_Mix or unmapped filter",
                "fix": "Rebuild from FACT_Sales: X category, Y SUM(net_sale), filters outlet_name, sales_date, category, super_category.",
            },
            {
                "issue": "Menu item detail repeats entities",
                "cause": "The table has outlet + item grain or a raw/detail table is being viewed without grouping",
                "fix": "Use outlet filter or create Summary/Pivot View grouped by item_number, item_name. Use FACT_Sales if date filter must work.",
            },
            {
                "issue": "Receipt booked value does not respond correctly to PO Status",
                "cause": "Receipt rows have no PO status or PO number",
                "fix": "Do not map PO Status to receipt booked value. Keep PO Status for PO raised/open/partial status charts.",
            },
            {
                "issue": "Open/partial count is zero while PO raised value exceeds receipt value",
                "cause": "Open count is status-based, while value gap is value-based",
                "fix": "Add separate PO vs Receipt Value Gap KPI. Keep open/partial status count as a status-control KPI.",
            },
            {
                "issue": "Revenue per inventory rupee adds across outlets",
                "cause": "Zoho is summing outlet-level ratio values",
                "fix": "Use aggregate formula SUM(net_sales) * DISTINCTCOUNT(activity_date) / SUM(inventory_value).",
            },
        ]
    )
    lines.append(md_table(correction_rows, ["issue", "cause", "fix"], ["Issue", "Cause", "Fix"]))
    lines.append("")
    lines.append("## Month 1 QA Filter Bank")
    lines.append("")
    lines.append(f"The generated QA bank has {len(qa_bank)} filter combinations across sales, menu, procurement, daily health, and inventory. Full file:")
    lines.append("")
    lines.append("```text")
    lines.append("docs/month1_truth_tables/qa_filter_bank_month1.csv")
    lines.append("```")
    lines.append("")
    lines.append("Preview:")
    lines.append("")
    lines.append(md_table(
        qa_bank.head(40),
        ["domain", "filter_1", "filter_2", "filter_3", "expected_measure", "expected_display", "source_table", "note"],
        ["Domain", "Filter 1", "Filter 2", "Filter 3", "Measure", "Expected display", "Source", "Note"],
    ))
    lines.append("")
    lines.append("## Supporting Truth Tables")
    lines.append("")
    for name in outputs:
        lines.append(f"- `docs/month1_truth_tables/{name}.csv`")
    lines.append("- `docs/month1_truth_tables/query_table_audit.csv`")
    lines.append("")
    lines.append("## Final Rules For Demo Confidence")
    lines.append("")
    lines.append("- Start every dashboard QA from the source table grain, not the visual label.")
    lines.append("- Date filters only work when the visual source table has a compatible date field.")
    lines.append("- Cascading filters work best when all dropdown values come from the same dashboard primary fact table.")
    lines.append("- Ratios must be aggregate formulas. Never sum an already-calculated ratio across outlets.")
    lines.append("- PO value, receipt value, and open status answer different questions. Keep them as separate KPIs.")
    lines.append("- The synthetic story is deterministic. If Zoho disagrees with these numbers for Month 1, the issue is table grain, filter mapping, refresh state, or chart aggregation.")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    data = load_data()
    outputs = build_outputs(data)
    query_audit = audit_query_sql()
    write_csv_outputs(outputs, query_audit)
    README_PATH.write_text(build_readme(data, outputs, query_audit), encoding="utf-8")
    print(f"Wrote {README_PATH}")
    print(f"Wrote truth CSVs to {OUT_DIR}")
    print(f"QA combinations: {len(outputs['qa_filter_bank_month1'])}")


if __name__ == "__main__":
    main()
