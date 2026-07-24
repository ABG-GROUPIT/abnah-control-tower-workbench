from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pandas as pd

import build_control_tower_truth_pack as truth


ROOT = Path(__file__).resolve().parents[1]
TRUTH_DIR = ROOT / "exports" / "control_tower_zoho" / "truth"
OUTPUT_CSV = TRUTH_DIR / "DASHBOARD_CHART_ACCEPTANCE.csv"
OUTPUT_MD = ROOT / "docs" / "ZOHO_DASHBOARD_EXPECTED_RESULTS.md"
DEFAULT_PERIOD = "month_03"
DEFAULT_OUTLET = "ALL"


def _scope(
    frame: pd.DataFrame,
    period: str = DEFAULT_PERIOD,
    outlet: str = DEFAULT_OUTLET,
) -> pd.DataFrame:
    result = frame
    if period != "ALL":
        result = result[result["source_period_code"] == period]
    if outlet != "ALL":
        result = result[result["outlet_code"] == outlet]
    return result.copy()


def _numbers(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    result = frame.copy()
    for column in columns:
        result[column] = pd.to_numeric(result[column], errors="coerce").fillna(0)
    return result


def _money(value: object) -> str:
    if value is None or pd.isna(value):
        return "Unavailable"
    return f"INR {float(value):,.2f}"


def _number(value: object, decimals: int = 0) -> str:
    if value is None or pd.isna(value):
        return "Unavailable"
    return f"{float(value):,.{decimals}f}"


def _percent(value: object, decimals: int = 2) -> str:
    if value is None or pd.isna(value):
        return "Unavailable"
    return f"{float(value):,.{decimals}f}%"


def _text(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    return str(value).replace("|", "/")


def _md_table(headers: list[str], rows: list[list[object]]) -> list[str]:
    rendered = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    rendered.extend(
        "| " + " | ".join(_text(value) for value in row) + " |"
        for row in rows
    )
    return rendered


def _load_truth(name: str) -> pd.DataFrame:
    return pd.read_csv(TRUTH_DIR / name, encoding="utf-8-sig")


def _query_models() -> dict[str, pd.DataFrame]:
    recipe, recipe_unit_cost = truth._recipe_model()
    po, performance = truth._purchase_model()
    risk_source, menu_impact, forecast = truth._inventory_risk_model(recipe, po)
    risk = truth._query_27_projection(risk_source)
    variance_source, menu_profit, sales = truth._consumption_model(
        recipe_unit_cost
    )
    sales = sales.rename(columns={"sale_date": "sales_date"})

    closing = _numbers(
        truth._read_landing("closing_stock"),
        ["total_qty", "average_price", "total_amt"],
    ).rename(
        columns={
            "source_outlet_code": "outlet_code",
            "source_outlet_name": "outlet_name",
            "total_qty": "closing_qty",
            "average_price": "average_unit_cost",
            "total_amt": "closing_value",
            "unit_name": "canonical_uom",
        }
    )
    wastage = _numbers(
        truth._read_landing("enterprise_wastage_normal"),
        ["wastage_amt"],
    ).rename(
        columns={
            "source_outlet_code": "outlet_code",
            "source_outlet_name": "outlet_name",
            "wastage_amt": "wastage_value",
        }
    )
    expiry = _numbers(
        truth._read_aux("AUX_Expiry_Estimate"),
        [
            "available_qty",
            "received_qty",
            "batch_remaining_qty",
            "item_closing_qty",
            "qty_at_risk",
            "average_unit_cost",
            "days_to_expiry",
            "expiry_risk_value",
        ],
    ).rename(columns={"qty_at_risk": "expiry_qty_at_risk"})
    expiry["risk_severity"] = np.where(
        expiry["risk_status"].isin(["EXPIRED", "EXPIRES_TODAY"]),
        "PURPLE",
        np.where(expiry["risk_status"] == "CRITICAL", "RED", "AMBER"),
    )

    receipt = _numbers(
        truth._read_landing("enterprise_entry"),
        [
            "entry_qty",
            "unit_price",
            "base_amt",
            "discount_amt",
            "total_tax_amt",
            "total_amt",
        ],
    ).rename(
        columns={
            "source_outlet_code": "outlet_code",
            "source_outlet_name": "outlet_name",
            "transaction_number": "grn_number",
            "entry_date": "receipt_date",
            "entry_qty": "received_qty",
            "unit": "canonical_uom",
            "base_amt": "receipt_subtotal",
            "discount_amt": "discount_value",
            "total_tax_amt": "tax_value",
            "total_amt": "receipt_total",
        }
    )

    inventory_period = _numbers(
        truth._read_landing("enterprise_variance_normal"),
        [
            "average_price",
            "opening_qty",
            "purchase_qty",
            "stock_in_qty",
            "stock_out_qty",
            "return_qty",
            "closing_qty",
        ],
    ).rename(
        columns={
            "source_outlet_code": "outlet_code",
            "source_outlet_name": "outlet_name",
            "unit": "canonical_uom",
            "average_price": "average_unit_cost",
            "stock_in_qty": "transfer_in_qty",
            "stock_out_qty": "transfer_out_qty",
        }
    )
    inventory_period["calculated_actual_consumption_qty"] = (
        inventory_period["opening_qty"]
        + inventory_period["purchase_qty"]
        + inventory_period["transfer_in_qty"]
        - inventory_period["transfer_out_qty"]
        - inventory_period["return_qty"]
        - inventory_period["closing_qty"]
    )
    inventory_period["calculated_actual_consumption_value"] = (
        inventory_period["calculated_actual_consumption_qty"]
        * inventory_period["average_unit_cost"]
    )
    theoretical = _numbers(
        truth._read_aux("AUX_Theoretical_Consumption"),
        ["theoretical_qty", "average_price"],
    ).rename(
        columns={
            "unit": "canonical_uom",
            "average_price": "theoretical_average_price",
        }
    )
    variance = inventory_period.merge(
        theoretical[
            [
                "source_period_code",
                "outlet_code",
                "item_code",
                "theoretical_qty",
            ]
        ],
        on=["source_period_code", "outlet_code", "item_code"],
        how="left",
    )
    variance["theoretical_qty"] = variance["theoretical_qty"].fillna(0)
    variance["variance_qty"] = (
        variance["calculated_actual_consumption_qty"]
        - variance["theoretical_qty"]
    )
    variance["signed_variance_value"] = (
        variance["variance_qty"] * variance["average_unit_cost"]
    )
    variance["leakage_value"] = (
        variance["variance_qty"].clip(lower=0)
        * variance["average_unit_cost"]
    )
    variance["low_consumption_qty"] = (-variance["variance_qty"]).clip(lower=0)
    variance["low_consumption_value"] = (
        variance["low_consumption_qty"] * variance["average_unit_cost"]
    )

    po = po.rename(
        columns={
            "remaining_balance_qty": "remaining_qty",
            "unit": "canonical_uom",
            "total_item_cost": "gross_order_value",
        }
    )
    performance = performance.rename(
        columns={
            "remaining_balance_qty": "remaining_qty",
            "unit": "canonical_uom",
            "total_item_cost": "gross_order_value",
        }
    )
    risky_po = po[po["is_open_po"]].merge(
        risk.loc[
            risk["risk_severity"] != "GREEN",
            [
                "source_period_code",
                "outlet_code",
                "item_code",
                "risk_severity",
            ],
        ],
        on=["source_period_code", "outlet_code", "item_code"],
        how="inner",
    )

    procurement = (
        po.groupby(
            [
                "source_period_code",
                "outlet_code",
                "outlet_name",
                "vendor_name",
            ],
            as_index=False,
        )
        .agg(
            ordered_value=("gross_order_value", "sum"),
            processed_value=("processed_po_value", "sum"),
            pending_value=("open_po_value", "sum"),
            po_count=("po_number", "nunique"),
        )
    )
    delayed = (
        po[po["delayed_po_flag"]]
        .groupby(
            [
                "source_period_code",
                "outlet_code",
                "outlet_name",
                "vendor_name",
            ],
            as_index=False,
        )
        .agg(delayed_value=("open_po_value", "sum"))
    )
    open_counts = (
        po[po["is_open_po"]]
        .groupby(
            [
                "source_period_code",
                "outlet_code",
                "outlet_name",
                "vendor_name",
            ],
            as_index=False,
        )
        .agg(open_po_count=("po_number", "nunique"))
    )
    procurement = procurement.merge(
        delayed,
        on=[
            "source_period_code",
            "outlet_code",
            "outlet_name",
            "vendor_name",
        ],
        how="left",
    ).merge(
        open_counts,
        on=[
            "source_period_code",
            "outlet_code",
            "outlet_name",
            "vendor_name",
        ],
        how="left",
    )
    procurement[["delayed_value", "open_po_count"]] = procurement[
        ["delayed_value", "open_po_count"]
    ].fillna(0)

    vendor_rows: list[dict[str, object]] = []
    for keys, group in performance.groupby(
        ["source_period_code", "outlet_code", "outlet_name", "vendor_name"]
    ):
        eligible = group[group["eligible_closed_line_flag"]]
        ordered_qty = group["ordered_qty"].sum()
        vendor_rows.append(
            {
                "source_period_code": keys[0],
                "outlet_code": keys[1],
                "outlet_name": keys[2],
                "vendor_name": keys[3],
                "monthly_purchase_value": group["gross_order_value"].sum(),
                "open_po_value": group["open_po_value"].sum(),
                "otif_success_count": eligible["otif_success_flag"].sum(),
                "eligible_line_count": len(eligible),
                "otif_percent": (
                    eligible["otif_success_flag"].sum() / len(eligible) * 100
                    if len(eligible)
                    else np.nan
                ),
                "received_qty": group["received_qty"].sum(),
                "ordered_qty": ordered_qty,
                "fill_rate_percent": (
                    group["received_qty"].sum() / ordered_qty * 100
                    if ordered_qty
                    else np.nan
                ),
                "lead_time_days_sum": eligible[
                    "lead_time_deviation_days"
                ].sum(),
                "average_lead_time_deviation_days": eligible[
                    "lead_time_deviation_days"
                ].mean(),
                "delayed_po_line_count": group["delayed_po_flag"].sum(),
            }
        )
    vendor_scorecard = pd.DataFrame(vendor_rows)

    receipt_price = (
        receipt.groupby(
            [
                "source_period_code",
                "outlet_code",
                "outlet_name",
                "vendor_name",
                "item_code",
                "item_name",
                "canonical_uom",
            ],
            as_index=False,
        )
        .agg(
            received_qty=("received_qty", "sum"),
            receipt_subtotal=("receipt_subtotal", "sum"),
        )
    )
    receipt_price["current_unit_price"] = (
        receipt_price["receipt_subtotal"] / receipt_price["received_qty"]
    )
    previous = receipt_price[
        [
            "source_period_code",
            "outlet_code",
            "vendor_name",
            "item_code",
            "current_unit_price",
        ]
    ].rename(
        columns={
            "source_period_code": "previous_period_code",
            "current_unit_price": "previous_unit_price",
        }
    )
    period_pairs = pd.DataFrame(
        [
            {"source_period_code": "month_02", "previous_period_code": "month_01"},
            {"source_period_code": "month_03", "previous_period_code": "month_02"},
        ]
    )
    price_movement = receipt_price.merge(
        period_pairs,
        on="source_period_code",
        how="left",
    ).merge(
        previous,
        on=[
            "previous_period_code",
            "outlet_code",
            "vendor_name",
            "item_code",
        ],
        how="left",
    )
    price_movement["unit_price_change"] = (
        price_movement["current_unit_price"]
        - price_movement["previous_unit_price"]
    )
    price_movement["unit_price_change_percent"] = np.where(
        price_movement["previous_unit_price"].notna()
        & price_movement["previous_unit_price"].ne(0),
        price_movement["unit_price_change"]
        / price_movement["previous_unit_price"]
        * 100,
        np.nan,
    )

    scm_rows: list[dict[str, object]] = []
    for period in sorted(closing["source_period_code"].unique()):
        for outlet in sorted(closing["outlet_code"].unique()):
            c = _scope(closing, period, outlet)
            p = _scope(po, period, outlet)
            s = _scope(sales, period, outlet)
            a = _scope(inventory_period, period, outlet)
            scm_rows.append(
                {
                    "source_period_code": period,
                    "outlet_code": outlet,
                    "outlet_name": c["outlet_name"].iloc[0],
                    "net_sales": s["net_sales"].sum(),
                    "closing_stock_value": c["closing_value"].sum(),
                    "open_po_value": p.loc[p["is_open_po"], "open_po_value"].sum(),
                    "actual_consumption_value": a[
                        "calculated_actual_consumption_value"
                    ].sum(),
                }
            )
    scm = pd.DataFrame(scm_rows)

    menu_summary = menu_profit.copy()
    menu_summary["bcg_quadrant"] = np.where(
        (menu_summary["sold_qty"] >= 150)
        & (menu_summary["gross_margin_percent"] >= 60),
        "Stars",
        np.where(
            (menu_summary["sold_qty"] < 150)
            & (menu_summary["gross_margin_percent"] >= 60),
            "Niche gems",
            np.where(
                (menu_summary["sold_qty"] >= 150)
                & (menu_summary["gross_margin_percent"] < 60),
                "Volume drags",
                "Review / rationalize",
            ),
        ),
    )

    return {
        "recipe": recipe,
        "po": po,
        "performance": performance,
        "risk": risk,
        "menu_impact": menu_impact,
        "forecast": forecast,
        "expiry": expiry,
        "receipt": receipt,
        "closing": closing,
        "wastage": wastage,
        "inventory_period": inventory_period,
        "theoretical": theoretical,
        "variance": variance,
        "menu_profit": menu_profit,
        "menu_summary": menu_summary,
        "sales": sales,
        "risky_po": risky_po,
        "procurement": procurement,
        "vendor_scorecard": vendor_scorecard,
        "price_movement": price_movement,
        "scm": scm,
        "page1_truth": _load_truth("PAGE1_Risk_Action_Truth.csv"),
        "page2_truth": _load_truth("PAGE2_Procurement_Vendor_Truth.csv"),
        "page3_truth": _load_truth("PAGE3_Consumption_Profitability_Truth.csv"),
        "page4_truth": _load_truth("PAGE4_Explorer_Data_Quality_Truth.csv"),
        "dq_truth": _load_truth("PAGE4_Data_Quality_Truth.csv"),
    }


def _truth_row(frame: pd.DataFrame) -> pd.Series:
    return frame[
        (frame["source_period_code"] == DEFAULT_PERIOD)
        & (frame["outlet_code"] == DEFAULT_OUTLET)
    ].iloc[0]


def _record(
    records: list[dict[str, object]],
    page: str,
    report: str,
    metric: str,
    value: object,
    *,
    period: str = DEFAULT_PERIOD,
    outlet: str = DEFAULT_OUTLET,
    series: str = "",
    category: str = "",
    secondary_category: str = "",
    display_format: str = "number",
    notes: str = "",
) -> None:
    records.append(
        {
            "page": page,
            "report_name": report,
            "source_period_code": period,
            "outlet_code": outlet,
            "series": series,
            "category": category,
            "secondary_category": secondary_category,
            "metric": metric,
            "expected_value": (
                "" if value is None or pd.isna(value) else float(value)
            ),
            "display_format": display_format,
            "notes": notes,
        }
    )


def _build_records(models: dict[str, pd.DataFrame]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    p1 = _truth_row(models["page1_truth"])
    p2 = _truth_row(models["page2_truth"])
    p3 = _truth_row(models["page3_truth"])
    p4 = _truth_row(models["page4_truth"])
    risk = _scope(models["risk"])
    risky = risk[risk["risk_severity"] != "GREEN"]
    menu = _scope(models["menu_impact"])
    expiry = _scope(models["expiry"])
    risky_po = _scope(models["risky_po"])
    po = _scope(models["po"])
    receipt = _scope(models["receipt"])
    variance = _scope(models["variance"])
    menu_profit = _scope(models["menu_profit"])
    sales = _scope(models["sales"])

    page_1_kpis = [
        (
            "CT_P1_KPI_Outlets_At_Stockout_Risk",
            "outlets_at_risk",
            p1["outlets_at_risk"],
            "count",
        ),
        (
            "CT_P1_KPI_Menu_Items_At_Risk",
            "menu_items_at_risk",
            p1["menu_items_at_risk"],
            "count",
        ),
        (
            "CT_P1_KPI_Stockout_Risk_Value",
            "stockout_risk_value",
            p1["stockout_risk_value"],
            "currency",
        ),
        (
            "CT_P1_KPI_Expiry_Risk_Value_Demo",
            "expiry_risk_value",
            p1["expiry_risk_value"],
            "currency",
        ),
        (
            "CT_P1_KPI_Open_Risky_PO",
            "open_risky_po_count",
            p1["open_risky_po_count"],
            "count",
        ),
    ]
    for report, metric, value, fmt in page_1_kpis:
        _record(records, "Page 1", report, metric, value, display_format=fmt)

    for (outlet, severity), group in risky.groupby(
        ["outlet_code", "risk_severity"]
    ):
        _record(
            records,
            "Page 1",
            "CT_P1_Stockout_Priority_Stack",
            "shortage_cost_value",
            group["shortage_cost_value"].sum(),
            outlet=outlet,
            series=severity,
            category=outlet,
            display_format="currency",
        )
        _record(
            records,
            "Page 1",
            "CT_P1_Stockout_Priority_Stack",
            "risk_item_count",
            len(group),
            outlet=outlet,
            series=severity,
            category=outlet,
            display_format="count",
        )
    for outlet, group in risky.groupby("outlet_code"):
        _record(
            records,
            "Page 1",
            "CT_P1_Outlet_Risk_Map",
            "risk_item_count",
            len(group),
            outlet=outlet,
            category=outlet,
            display_format="count",
        )
        _record(
            records,
            "Page 1",
            "CT_P1_Outlet_Risk_Map",
            "shortage_cost_value",
            group["shortage_cost_value"].sum(),
            outlet=outlet,
            category=outlet,
            display_format="currency",
        )
    for report, frame, value_column in [
        ("CT_P1_Action_Center", risky, "shortage_cost_value"),
        ("CT_P1_Stockout_Risk_Detail", risky, "shortage_cost_value"),
        (
            "CT_P1_Menu_Impact_Detail",
            menu,
            "allocated_forecast_net_sales_at_risk",
        ),
        ("CT_P1_Expiry_Risk_Detail_Demo", expiry, "expiry_risk_value"),
        ("CT_P1_Vendor_PO_Risk", risky_po, "open_po_value"),
    ]:
        _record(
            records,
            "Page 1",
            report,
            "row_count",
            len(frame),
            display_format="count",
        )
        _record(
            records,
            "Page 1",
            report,
            value_column,
            frame[value_column].sum() if value_column in frame else 0,
            display_format="currency",
        )

    _record(
        records,
        "Page 2",
        "CT_P2_Pending_Ingredient_Risk",
        "row_count",
        len(risky_po),
        display_format="count",
    )
    _record(
        records,
        "Page 2",
        "CT_P2_Pending_Ingredient_Risk",
        "open_po_liability",
        risky_po["open_po_value"].sum(),
        display_format="currency",
    )

    page_2_kpis = [
        ("CT_P2_KPI_Monthly_Purchase", p2["monthly_purchase_value_ordered_gross"], "currency"),
        ("CT_P2_KPI_Closing_Inventory", p2["closing_inventory_value"], "currency"),
        ("CT_P2_KPI_Open_PO_Liability", p2["open_po_liability"], "currency"),
        ("CT_P2_KPI_Working_Capital", p2["working_capital_locked"], "currency"),
        ("CT_P2_KPI_Open_PO_Count", p2["open_po_count"], "count"),
        ("CT_P2_KPI_Fill_Rate", p2["po_fill_rate_percent"], "percentage"),
        ("CT_P2_KPI_OTIF", p2["vendor_otif_percent"], "percentage"),
    ]
    for report, value, fmt in page_2_kpis:
        _record(records, "Page 2", report, "display_value", value, display_format=fmt)
    for metric, column in [
        ("Ordered", "gross_order_value"),
        ("Processed", "processed_po_value"),
        ("Pending", "open_po_value"),
    ]:
        _record(
            records,
            "Page 2",
            "CT_P2_Procurement_Funnel",
            "stage_value",
            po[column].sum(),
            series=metric,
            category=metric,
            display_format="currency",
        )
    _record(
        records,
        "Page 2",
        "CT_P2_Procurement_Funnel",
        "stage_value",
        po.loc[po["delayed_po_flag"], "open_po_value"].sum(),
        series="Delayed",
        category="Delayed",
        display_format="currency",
    )
    for status, group in po.groupby("po_status"):
        _record(
            records,
            "Page 2",
            "CT_P2_PO_Status_Distribution",
            "distinct_po_count",
            group["po_number"].nunique(),
            category=status,
            display_format="count",
        )
        _record(
            records,
            "Page 2",
            "CT_P2_PO_Status_Distribution",
            "open_po_liability",
            group["open_po_value"].sum(),
            category=status,
            display_format="currency",
        )
    for vendor, group in po.groupby("vendor_name"):
        _record(
            records,
            "Page 2",
            "CT_P2_Pending_By_Vendor",
            "pending_value",
            group["open_po_value"].sum(),
            category=vendor,
            display_format="currency",
        )
    breach = po[po["delayed_po_flag"]]
    _record(
        records,
        "Page 2",
        "CT_P2_Expected_Delivery_Breach",
        "row_count",
        len(breach),
        display_format="count",
    )
    _record(
        records,
        "Page 2",
        "CT_P2_Expected_Delivery_Breach",
        "distinct_po_count",
        breach["po_number"].nunique(),
        display_format="count",
    )
    _record(
        records,
        "Page 2",
        "CT_P2_Expected_Delivery_Breach",
        "open_po_liability",
        breach["open_po_value"].sum(),
        display_format="currency",
    )
    vendor_cross = []
    for vendor, group in models["performance"][
        models["performance"]["source_period_code"] == DEFAULT_PERIOD
    ].groupby("vendor_name"):
        eligible = group[group["eligible_closed_line_flag"]]
        ordered = group["ordered_qty"].sum()
        vendor_cross.append(
            {
                "vendor_name": vendor,
                "purchase_value": group["gross_order_value"].sum(),
                "open_po_value": group["open_po_value"].sum(),
                "fill_rate_percent": (
                    group["received_qty"].sum() / ordered * 100
                    if ordered
                    else np.nan
                ),
                "otif_percent": (
                    eligible["otif_success_flag"].sum() / len(eligible) * 100
                    if len(eligible)
                    else np.nan
                ),
                "average_lead_time_deviation_days": eligible[
                    "lead_time_deviation_days"
                ].mean(),
                "delayed_po_line_count": group["delayed_po_flag"].sum(),
            }
        )
    vendor_cross_frame = pd.DataFrame(vendor_cross)
    for _, row in vendor_cross_frame.iterrows():
        for report in [
            "CT_P2_Vendor_Performance_Matrix",
            "CT_P2_Vendor_Scorecard",
        ]:
            for metric, fmt in [
                ("purchase_value", "currency"),
                ("open_po_value", "currency"),
                ("fill_rate_percent", "percentage"),
                ("otif_percent", "percentage"),
                ("average_lead_time_deviation_days", "decimal"),
                ("delayed_po_line_count", "count"),
            ]:
                _record(
                    records,
                    "Page 2",
                    report,
                    metric,
                    row[metric],
                    category=row["vendor_name"],
                    display_format=fmt,
                    notes=(
                        "Cross-outlet result recalculated from Query 24; do not "
                        "average Query 30 percentages."
                    ),
                )
    price_all = models["receipt"]
    for (period, item_code, item_name, uom), group in price_all.groupby(
        ["source_period_code", "item_code", "item_name", "canonical_uom"]
    ):
        _record(
            records,
            "Page 2",
            "CT_P2_Ingredient_Price_Trend",
            "weighted_unit_price",
            group["receipt_subtotal"].sum() / group["received_qty"].sum(),
            period=period,
            series=f"{item_code} - {item_name}",
            category=item_code,
            secondary_category=uom,
            display_format="currency_per_uom",
        )
    price_current = _scope(models["receipt"])
    for (vendor, item_code, item_name, uom), group in price_current.groupby(
        ["vendor_name", "item_code", "item_name", "canonical_uom"]
    ):
        _record(
            records,
            "Page 2",
            "CT_P2_Vendor_Price_Comparison",
            "weighted_unit_price",
            group["receipt_subtotal"].sum() / group["received_qty"].sum(),
            category=vendor,
            secondary_category=f"{item_code} - {item_name} / {uom}",
            display_format="currency_per_uom",
        )
    movement = _scope(models["price_movement"]).dropna(
        subset=["unit_price_change_percent"]
    )
    for _, row in movement.iterrows():
        _record(
            records,
            "Page 2",
            "CT_P2_Top_Price_Movement",
            "unit_price_change_percent",
            row["unit_price_change_percent"],
            outlet=row["outlet_code"],
            category=f"{row['item_code']} - {row['item_name']}",
            secondary_category=row["vendor_name"],
            display_format="percentage",
            notes="Tuple grain is outlet + vendor + item + UOM.",
        )
    current_closing = _scope(models["closing"])
    for (outlet, category), group in current_closing.groupby(
        ["outlet_code", "category_name"]
    ):
        _record(
            records,
            "Page 2",
            "CT_P2_Inventory_Value",
            "closing_value",
            group["closing_value"].sum(),
            outlet=outlet,
            series=category,
            category=outlet,
            display_format="currency",
        )
    _record(
        records,
        "Page 2",
        "CT_P2_High_Value_Slow_Stock",
        "row_count",
        len(risk),
        display_format="count",
    )
    for period, group in models["wastage"].groupby("source_period_code"):
        _record(
            records,
            "Page 2",
            "CT_P2_Observed_Wastage",
            "observed_wastage_value",
            group["wastage_value"].sum(),
            period=period,
            category=period,
            display_format="currency",
        )
    for period, group in models["expiry"].groupby("source_period_code"):
        _record(
            records,
            "Page 2",
            "CT_P2_Expiry_Exposure_Demo",
            "expiry_risk_value",
            group["expiry_risk_value"].sum(),
            period=period,
            category=period,
            display_format="currency",
        )

    page_3_kpis = [
        ("CT_P3_KPI_Net_Sales", p3["net_sales"], "currency"),
        ("CT_P3_KPI_Quantity_Sold", p3["quantity_sold"], "count"),
        ("CT_P3_KPI_Theoretical_COGS", p3["theoretical_cogs"], "currency"),
        (
            "CT_P3_KPI_Consumption_Leakage",
            p3["consumption_leakage_value"],
            "currency",
        ),
        (
            "CT_P3_KPI_Menu_Gross_Margin",
            p3["menu_gross_margin_percent"],
            "percentage",
        ),
    ]
    for report, value, fmt in page_3_kpis:
        _record(records, "Page 3", report, "display_value", value, display_format=fmt)
    for (period, uom), group in models["inventory_period"].groupby(
        ["source_period_code", "canonical_uom"]
    ):
        bridge_values = {
            "Opening": group["opening_qty"].sum(),
            "Purchase": group["purchase_qty"].sum(),
            "Transfer In": group["transfer_in_qty"].sum(),
            "Transfer Out (signed)": -group["transfer_out_qty"].sum(),
            "Return (signed)": -group["return_qty"].sum(),
            "Closing (signed)": -group["closing_qty"].sum(),
            "Actual Consumption": group[
                "calculated_actual_consumption_qty"
            ].sum(),
        }
        for series, value in bridge_values.items():
            _record(
                records,
                "Page 3",
                "CT_P3_Consumption_Bridge",
                "quantity",
                value,
                period=period,
                series=series,
                category=period,
                secondary_category=uom,
                display_format="quantity",
                notes="Display only with exactly one UOM selected.",
            )
    for (item_code, item_name, uom), group in variance.groupby(
        ["item_code", "item_name", "canonical_uom"]
    ):
        for metric, column in [
            ("actual_consumption_qty", "calculated_actual_consumption_qty"),
            ("theoretical_consumption_qty", "theoretical_qty"),
        ]:
            _record(
                records,
                "Page 3",
                "CT_P3_Actual_vs_Theoretical",
                metric,
                group[column].sum(),
                series=metric,
                category=f"{item_code} - {item_name}",
                secondary_category=uom,
                display_format="quantity",
            )
        _record(
            records,
            "Page 3",
            "CT_P3_Consumption_Leakage_Rank",
            "leakage_value",
            group["leakage_value"].sum(),
            category=f"{item_code} - {item_name}",
            secondary_category=uom,
            display_format="currency",
        )
        _record(
            records,
            "Page 3",
            "CT_P3_Low_Consumption_Check",
            "low_consumption_value",
            group["low_consumption_value"].sum(),
            category=f"{item_code} - {item_name}",
            secondary_category=uom,
            display_format="currency",
        )
    theoretical_current = _scope(models["theoretical"])
    _record(
        records,
        "Page 3",
        "CT_P3_Theoretical_Consumption_Detail",
        "row_count",
        len(theoretical_current),
        display_format="count",
    )
    _record(
        records,
        "Page 3",
        "CT_P3_Theoretical_Consumption_Detail",
        "theoretical_consumption_value",
        (
            theoretical_current["theoretical_qty"]
            * theoretical_current["theoretical_average_price"]
        ).sum(),
        display_format="currency",
    )
    _record(
        records,
        "Page 3",
        "CT_P3_Menu_COGS_Detail",
        "row_count",
        len(menu_profit),
        display_format="count",
    )
    _record(
        records,
        "Page 3",
        "CT_P3_Menu_COGS_Detail",
        "net_sales",
        menu_profit["net_sales"].sum(),
        display_format="currency",
    )
    _record(
        records,
        "Page 3",
        "CT_P3_Menu_COGS_Detail",
        "theoretical_cogs",
        menu_profit["theoretical_cogs"].sum(),
        display_format="currency",
    )
    menu_current = _scope(models["menu_summary"])
    for (outlet, quadrant), group in menu_current.groupby(
        ["outlet_code", "bcg_quadrant"]
    ):
        _record(
            records,
            "Page 3",
            "CT_P3_Menu_BCG",
            "menu_item_count",
            len(group),
            outlet=outlet,
            series=quadrant,
            category=outlet,
            display_format="count",
            notes="Query 32 quadrant is valid at outlet + menu-item grain.",
        )
        _record(
            records,
            "Page 3",
            "CT_P3_Menu_BCG",
            "net_sales",
            group["net_sales"].sum(),
            outlet=outlet,
            series=quadrant,
            category=outlet,
            display_format="currency",
        )
    for (item_code, item_name), group in menu_current.groupby(
        ["menu_item_code", "menu_item_name"]
    ):
        sales_value = group["net_sales"].sum()
        cogs = group["theoretical_cogs"].sum()
        margin = group["gross_margin_value"].sum()
        sold = group["sold_qty"].sum()
        margin_percent = margin / sales_value * 100 if sales_value else np.nan
        label = f"{item_code} - {item_name}"
        for report in [
            "CT_P3_Menu_Margin_Rank",
            "CT_P3_Top_Slow_Menu_Ranking",
        ]:
            for metric, value, fmt in [
                ("sold_qty", sold, "count"),
                ("net_sales", sales_value, "currency"),
                ("theoretical_cogs", cogs, "currency"),
                ("gross_margin_value", margin, "currency"),
                ("gross_margin_percent", margin_percent, "percentage"),
            ]:
                _record(
                    records,
                    "Page 3",
                    report,
                    metric,
                    value,
                    category=label,
                    display_format=fmt,
                )
    for (date, outlet), group in models["sales"].groupby(
        ["sales_date", "outlet_code"]
    ):
        _record(
            records,
            "Page 3",
            "CT_P3_Sales_Trend",
            "net_sales",
            group["net_sales"].sum(),
            period=str(group["source_period_code"].iloc[0]),
            outlet=outlet,
            category=str(date),
            display_format="currency",
        )
        _record(
            records,
            "Page 3",
            "CT_P3_Sales_Trend",
            "sold_qty",
            group["sold_qty"].sum(),
            period=str(group["source_period_code"].iloc[0]),
            outlet=outlet,
            category=str(date),
            display_format="count",
        )
    for category, group in menu_profit.groupby("category_name"):
        _record(
            records,
            "Page 3",
            "CT_P3_Category_Contribution",
            "net_sales",
            group["net_sales"].sum(),
            category=category,
            display_format="currency",
        )
    for (outlet, category), group in menu_profit.groupby(
        ["outlet_code", "category_name"]
    ):
        _record(
            records,
            "Page 3",
            "CT_P3_Outlet_Item_Heatmap",
            "net_sales",
            group["net_sales"].sum(),
            outlet=outlet,
            category=category,
            display_format="currency",
            notes="Acceptance fixture uses category on X and net sales as color.",
        )

    actual_current = _scope(models["inventory_period"])
    page_4_kpis = [
        ("CT_P4_KPI_Closing_Stock", p4["closing_inventory_value"], "currency"),
        ("CT_P4_KPI_Open_PO", p4["open_po_liability"], "currency"),
        ("CT_P4_KPI_Net_Sales", p4["net_sales"], "currency"),
        (
            "CT_P4_KPI_Actual_Consumption",
            actual_current["calculated_actual_consumption_value"].sum(),
            "currency",
        ),
        (
            "CT_P4_KPI_Consumption_Variance",
            variance["signed_variance_value"].sum(),
            "currency",
        ),
        ("CT_P4_KPI_Quantity_Sold", sales["sold_qty"].sum(), "count"),
        (
            "CT_P4_KPI_Active_Menu_Items",
            sales["menu_item_code"].nunique(),
            "count",
        ),
        ("CT_P4_KPI_Open_PO_Lines", po["is_open_po"].sum(), "count"),
        ("CT_P4_KPI_GRN_Value", receipt["receipt_total"].sum(), "currency"),
        (
            "CT_P4_KPI_Active_Vendors",
            po["vendor_name"].nunique(),
            "count",
        ),
    ]
    for report, value, fmt in page_4_kpis:
        _record(records, "Page 4", report, "display_value", value, display_format=fmt)
    _record(
        records,
        "Page 4",
        "CT_P4_Descriptive_Explorer",
        "row_count",
        len(_scope(models["scm"])),
        display_format="count",
    )
    for period, group in models["scm"].groupby("source_period_code"):
        for metric in [
            "closing_stock_value",
            "open_po_value",
            "net_sales",
            "actual_consumption_value",
        ]:
            _record(
                records,
                "Page 4",
                "CT_P4_SCM_Monthly_Trend",
                metric,
                group[metric].sum(),
                period=period,
                series=metric,
                category=period,
                display_format="currency",
            )
    for period, group in models["variance"].groupby("source_period_code"):
        _record(
            records,
            "Page 4",
            "CT_P4_Consumption_Variance_Trend",
            "signed_variance_value",
            group["signed_variance_value"].sum(),
            period=period,
            series="Signed variance",
            category=period,
            display_format="currency",
        )
        _record(
            records,
            "Page 4",
            "CT_P4_Consumption_Variance_Trend",
            "leakage_value",
            group["leakage_value"].sum(),
            period=period,
            series="Leakage",
            category=period,
            display_format="currency",
        )
    dq = models["dq_truth"]
    dq_all = dq[
        (dq["source_period_code"] == "ALL") & (dq["outlet_code"] == "ALL")
    ].iloc[0]
    dq_mapping = {
        "NEGATIVE_STOCK": "negative_stock_count",
        "ZERO_STOCK_WITH_DEMAND": "zero_stock_with_demand_count",
        "SOLD_ITEM_MISSING_RECIPE": "sold_items_missing_recipe_count",
        "OPERATIONAL_ITEM_MISSING_MASTER": (
            "operational_items_missing_master_count"
        ),
        "UOM_MISMATCH_WITHOUT_CONVERSION": (
            "uom_mismatch_without_conversion_count"
        ),
        "OPEN_PO_MISSING_EXPECTED_DELIVERY": (
            "open_po_missing_expected_delivery_count"
        ),
    }
    for exception_type, column in dq_mapping.items():
        _record(
            records,
            "Page 4",
            "CT_P4_Data_Quality_Tiles",
            "exception_count",
            dq_all[column],
            period="ALL",
            outlet="ALL",
            category=exception_type,
            display_format="count",
            notes="Query 34 is deliberately outside global period/outlet filters.",
        )
    _record(
        records,
        "Page 4",
        "CT_P4_Data_Quality_Detail",
        "row_count",
        sum(float(dq_all[column]) for column in dq_mapping.values()),
        period="ALL",
        outlet="ALL",
        display_format="count",
    )
    for report, frame in [
        ("CT_P4_Sales_Explorer", sales),
        ("CT_P4_Item_Explorer", risk),
        ("CT_P4_PO_Explorer", _scope(models["performance"])),
        ("CT_P4_GRN_Explorer", receipt),
        ("CT_P4_Vendor_Explorer", vendor_cross_frame),
        ("CT_P4_Expiry_Explorer_Demo", expiry),
    ]:
        _record(
            records,
            "Page 4",
            report,
            "row_count",
            len(frame),
            display_format="count",
        )
    return records


def _write_csv(records: list[dict[str, object]]) -> None:
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "page",
        "report_name",
        "source_period_code",
        "outlet_code",
        "series",
        "category",
        "secondary_category",
        "metric",
        "expected_value",
        "display_format",
        "notes",
    ]
    with OUTPUT_CSV.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def _default_kpi_rows(
    records: list[dict[str, object]],
    page: str,
) -> list[list[object]]:
    result = []
    for row in records:
        if row["page"] != page or "_KPI_" not in str(row["report_name"]):
            continue
        value = row["expected_value"]
        fmt = row["display_format"]
        if fmt == "currency":
            display = _money(value)
        elif fmt == "percentage":
            display = _percent(value, 4)
        else:
            display = _number(value, 0)
        result.append([row["report_name"], display])
    return result


def _write_markdown(
    models: dict[str, pd.DataFrame],
    records: list[dict[str, object]],
) -> None:
    lines = [
        "# ABNAH Control Tower v2 - Expected Dashboard Results",
        "",
        "Generated by `python scripts/build_dashboard_expected_results.py` from "
        "the packaged synthetic imports and the final 38-Query-Table logic.",
        "",
        "Use this document while building the Zoho dashboard. It is the expected "
        "synthetic demo baseline, not ABNAH production truth.",
        "",
        "## Acceptance Display State",
        "",
        "- Current-state cards and details: `source_period_code = month_03`.",
        "- Outlet: All outlets (`OUT001`, `OUT002`, `OUT003`).",
        "- Historical charts: all three periods; do not apply the global As-of "
        "filter.",
        "- Query 34 quality controls: all periods/all outlets; do not apply either "
        "global filter.",
        "- Quantity comparisons: select exactly one UOM. This reference provides "
        "all UOM points in the companion CSV.",
        "- Currency tolerance: INR 0.02; quantity tolerance: 0.0001; percentage "
        "tolerance: 0.01 percentage point; counts must match exactly.",
        "",
        "The exhaustive machine-readable point set is "
        "`04_VALIDATION_AND_LIMITATIONS/TRUTH_PACK/"
        "DASHBOARD_CHART_ACCEPTANCE.csv`. It includes every KPI, trend point, "
        "price tuple, category contribution, heat-map cell and chart control "
        "generated below.",
        "",
        "## Correct Query 27 / Query 38 Boundary",
        "",
        "Query 27 contains stockout risk only. Query 38 contains the synthetic "
        "expiry estimate. Under the default `month_03 / All outlets` state:",
        "",
        "- Query 27 stockout action rows: **6**, not 74.",
        "- Query 38 expiry estimate rows: **68**.",
        "- Stockout shortage exposure: **INR 28,503.39**.",
        "- Expiry demo exposure: **INR 271,399.12**.",
        "- Do not merge the two evidence classes into one dashboard KPI.",
        "",
    ]
    for page in ["Page 1", "Page 2", "Page 3", "Page 4"]:
        lines.extend([f"## {page} Default KPI Cards", ""])
        lines.extend(
            _md_table(
                ["Zoho report", "Expected display"],
                _default_kpi_rows(records, page),
            )
        )
        lines.append("")

    risk = _scope(models["risk"])
    risky = risk[risk["risk_severity"] != "GREEN"]
    map_rows = []
    severity_rank = {"GREEN": 1, "AMBER": 2, "RED": 3, "PURPLE": 4}
    for outlet, group in risky.groupby("outlet_code"):
        max_severity = max(
            group["risk_severity"],
            key=lambda value: severity_rank[value],
        )
        map_rows.append(
            [
                outlet,
                group["outlet_name"].iloc[0],
                len(group),
                max_severity,
                _money(group["shortage_cost_value"].sum()),
            ]
        )
    lines.extend(
        [
            "## Page 1 Chart Checks",
            "",
            "### Outlet Risk Map And Priority Stack",
            "",
            *_md_table(
                [
                    "Outlet",
                    "Outlet name",
                    "Stockout rows",
                    "Maximum severity",
                    "Shortage exposure",
                ],
                map_rows,
            ),
            "",
        ]
    )
    stack_rows = []
    for (outlet, severity), group in risky.groupby(
        ["outlet_code", "risk_severity"]
    ):
        stack_rows.append(
            [
                outlet,
                severity,
                len(group),
                _money(group["shortage_cost_value"].sum()),
            ]
        )
    lines.extend(
        _md_table(
            ["Outlet", "Severity", "Rows", "Stack value"],
            stack_rows,
        )
    )
    lines.extend(["", "### Action Center - All Expected Rows", ""])
    action_rows = []
    for _, row in risky.sort_values(
        ["risk_severity_rank", "shortage_cost_value"],
        ascending=[False, False],
    ).iterrows():
        action_rows.append(
            [
                row["outlet_code"],
                row["item_code"],
                row["item_name"],
                row["canonical_uom"],
                row["risk_severity"],
                _number(row["shortage_qty"], 4),
                _money(row["shortage_cost_value"]),
                row["recommended_action"],
                row["due_band"],
            ]
        )
    lines.extend(
        _md_table(
            [
                "Outlet",
                "Item",
                "Item name",
                "UOM",
                "Severity",
                "Shortage",
                "Exposure",
                "Action",
                "Due",
            ],
            action_rows,
        )
    )
    menu_rows = []
    for outlet, group in _scope(models["menu_impact"]).groupby("outlet_code"):
        menu_rows.append(
            [
                outlet,
                len(group),
                group["menu_item_code"].nunique(),
                _money(group["allocated_forecast_net_sales_at_risk"].sum()),
            ]
        )
    lines.extend(
        [
            "",
            "### Menu Impact Control Totals",
            "",
            *_md_table(
                ["Outlet", "Rows", "Distinct menu items", "Sales at risk"],
                menu_rows,
            ),
            "",
        ]
    )
    expiry_rows = []
    for (outlet, severity), group in _scope(models["expiry"]).groupby(
        ["outlet_code", "risk_severity"]
    ):
        expiry_rows.append(
            [
                outlet,
                severity,
                len(group),
                _money(group["expiry_risk_value"].sum()),
            ]
        )
    lines.extend(
        [
            "### Expiry Demo Control Totals",
            "",
            *_md_table(
                ["Outlet", "Severity", "Rows", "Expiry value"],
                expiry_rows,
            ),
            "",
            "`CT_P1_Vendor_PO_Risk` must return **0 rows** for `month_03 / All "
            "outlets`. The all-period synthetic control is one risky PO.",
            "",
            "`CT_P2_Pending_Ingredient_Risk` uses the same Query 36 population "
            "and must also return **0 rows** in the default state.",
            "",
        ]
    )

    po = _scope(models["po"])
    funnel_rows = [
        ["Ordered", _money(po["gross_order_value"].sum())],
        ["Processed", _money(po["processed_po_value"].sum())],
        ["Pending", _money(po["open_po_value"].sum())],
        [
            "Delayed",
            _money(po.loc[po["delayed_po_flag"], "open_po_value"].sum()),
        ],
    ]
    lines.extend(
        [
            "## Page 2 Chart Checks",
            "",
            "### Procurement Funnel",
            "",
            *_md_table(["Stage", "Expected value"], funnel_rows),
            "",
            "Ordered uses gross PO value while processed/pending use quantity "
            "multiplied by unit price. Treat the four values as operational "
            "stages, not an arithmetic waterfall.",
            "",
            "### PO Status Distribution",
            "",
        ]
    )
    status_rows = []
    for status, group in po.groupby("po_status"):
        status_rows.append(
            [
                status,
                len(group),
                group["po_number"].nunique(),
                _money(group["open_po_value"].sum()),
            ]
        )
    lines.extend(
        _md_table(
            ["Status", "Line rows", "Distinct POs", "Open liability"],
            status_rows,
        )
    )
    lines.extend(
        [
            "",
            "A PO can contain lines in different statuses in this synthetic "
            "source, so status-level distinct PO counts do not add to the overall "
            "33 distinct POs.",
            "",
            "### Pending Liability By Vendor",
            "",
        ]
    )
    vendor_pending_rows = []
    for vendor, group in po.groupby("vendor_name"):
        vendor_pending_rows.append(
            [vendor, _money(group["open_po_value"].sum())]
        )
    vendor_pending_rows.sort(
        key=lambda row: float(row[1].replace("INR ", "").replace(",", "")),
        reverse=True,
    )
    lines.extend(
        _md_table(["Vendor", "Pending value"], vendor_pending_rows)
    )
    breach = po[po["delayed_po_flag"]]
    lines.extend(
        [
            "",
            "### Expected Delivery Breach Control",
            "",
            f"- Delayed line rows: **{len(breach)}**",
            f"- Distinct delayed POs: **{breach['po_number'].nunique()}**",
            f"- Delayed open liability: **{_money(breach['open_po_value'].sum())}**",
            "",
            "### Cross-Outlet Vendor Scorecard",
            "",
            "These rates are recalculated from Query 24. Never average Query 30 "
            "outlet-level percentages.",
            "",
        ]
    )
    vendor_rows = []
    performance = models["performance"][
        models["performance"]["source_period_code"] == DEFAULT_PERIOD
    ]
    for vendor, group in performance.groupby("vendor_name"):
        eligible = group[group["eligible_closed_line_flag"]]
        ordered = group["ordered_qty"].sum()
        vendor_rows.append(
            [
                vendor,
                _money(group["gross_order_value"].sum()),
                _money(group["open_po_value"].sum()),
                _percent(
                    group["received_qty"].sum() / ordered * 100
                    if ordered
                    else np.nan
                ),
                _percent(
                    eligible["otif_success_flag"].sum() / len(eligible) * 100
                    if len(eligible)
                    else np.nan
                ),
                _number(
                    eligible["lead_time_deviation_days"].mean(),
                    3,
                ),
                int(group["delayed_po_flag"].sum()),
            ]
        )
    vendor_rows.sort(key=lambda row: row[0])
    lines.extend(
        _md_table(
            [
                "Vendor",
                "Purchase",
                "Open PO",
                "Fill",
                "OTIF",
                "Lead deviation days",
                "Delayed lines",
            ],
            vendor_rows,
        )
    )
    lines.extend(
        [
            "",
            "### Price QA Fixture",
            "",
            "Use `ING001 - Coffee Beans`, `kg`, vendor All and outlet All to "
            "validate the price trend. The comparison chart is naturally sparse "
            "because each synthetic ingredient has one mapped transaction vendor.",
            "",
        ]
    )
    price_rows = []
    price = models["receipt"]
    fixture = price[
        (price["item_code"] == "ING001")
        & (price["canonical_uom"] == "kg")
    ]
    for period, group in fixture.groupby("source_period_code"):
        price_rows.append(
            [
                period,
                _number(group["received_qty"].sum(), 4),
                _money(
                    group["receipt_subtotal"].sum()
                    / group["received_qty"].sum()
                ),
            ]
        )
    lines.extend(
        _md_table(
            ["Period", "Received quantity", "Weighted unit price"],
            price_rows,
        )
    )
    movement = _scope(models["price_movement"]).dropna(
        subset=["unit_price_change_percent"]
    )
    movement = movement.assign(
        absolute_change=movement["unit_price_change_percent"].abs()
    ).sort_values("absolute_change", ascending=False)
    movement_rows = []
    for _, row in movement.head(10).iterrows():
        movement_rows.append(
            [
                row["outlet_code"],
                row["vendor_name"],
                row["item_code"],
                row["item_name"],
                row["canonical_uom"],
                _percent(row["unit_price_change_percent"], 4),
            ]
        )
    lines.extend(
        [
            "",
            "### Top 10 Price Movements",
            "",
            *_md_table(
                [
                    "Outlet",
                    "Vendor",
                    "Item",
                    "Item name",
                    "UOM",
                    "Change",
                ],
                movement_rows,
            ),
            "",
            "Keep outlet + vendor + item + UOM as the displayed tuple. Do not "
            "sum or average these percentages.",
            "",
            "### Inventory Value By Outlet",
            "",
        ]
    )
    inventory_rows = []
    for outlet, group in _scope(models["closing"]).groupby("outlet_code"):
        inventory_rows.append(
            [outlet, _money(group["closing_value"].sum())]
        )
    lines.extend(_md_table(["Outlet", "Closing value"], inventory_rows))
    leakage_rows = []
    for period in ["month_01", "month_02", "month_03"]:
        w = models["wastage"][
            models["wastage"]["source_period_code"] == period
        ]["wastage_value"].sum()
        e = models["expiry"][
            models["expiry"]["source_period_code"] == period
        ]["expiry_risk_value"].sum()
        leakage_rows.append([period, _money(w), _money(e)])
    lines.extend(
        [
            "",
            "### Wastage And Expiry Trends",
            "",
            *_md_table(
                ["Period", "Observed wastage", "Expiry demo estimate"],
                leakage_rows,
            ),
            "",
        ]
    )

    lines.extend(
        [
            "## Page 3 Chart Checks",
            "",
            "### Consumption Bridge By UOM",
            "",
            "Select one UOM before checking quantities. Transfer out, return and "
            "closing are signed negative bars.",
            "",
        ]
    )
    bridge_rows = []
    for (period, uom), group in models["inventory_period"].groupby(
        ["source_period_code", "canonical_uom"]
    ):
        bridge_rows.append(
            [
                period,
                uom,
                _number(group["opening_qty"].sum(), 4),
                _number(group["purchase_qty"].sum(), 4),
                _number(group["transfer_in_qty"].sum(), 4),
                _number(-group["transfer_out_qty"].sum(), 4),
                _number(-group["return_qty"].sum(), 4),
                _number(-group["closing_qty"].sum(), 4),
                _number(
                    group["calculated_actual_consumption_qty"].sum(),
                    4,
                ),
            ]
        )
    lines.extend(
        _md_table(
            [
                "Period",
                "UOM",
                "Opening",
                "Purchase",
                "Transfer in",
                "Transfer out",
                "Return",
                "Closing",
                "Actual",
            ],
            bridge_rows,
        )
    )
    variance = _scope(models["variance"])
    item_variance = (
        variance.groupby(
            ["item_code", "item_name", "canonical_uom"],
            as_index=False,
        )
        .agg(
            actual=("calculated_actual_consumption_qty", "sum"),
            theoretical=("theoretical_qty", "sum"),
            signed_variance_value=("signed_variance_value", "sum"),
            leakage_value=("leakage_value", "sum"),
            low_consumption_value=("low_consumption_value", "sum"),
        )
    )
    item_variance["absolute_variance"] = (
        item_variance["actual"] - item_variance["theoretical"]
    ).abs()
    variance_rows = []
    for _, row in item_variance.sort_values(
        "absolute_variance", ascending=False
    ).head(15).iterrows():
        variance_rows.append(
            [
                row["item_code"],
                row["item_name"],
                row["canonical_uom"],
                _number(row["actual"], 4),
                _number(row["theoretical"], 4),
                _money(row["signed_variance_value"]),
                _money(row["leakage_value"]),
            ]
        )
    lines.extend(
        [
            "",
            "### Largest 15 Ingredient Variances",
            "",
            *_md_table(
                [
                    "Item",
                    "Item name",
                    "UOM",
                    "Actual qty",
                    "Theoretical qty",
                    "Signed value",
                    "Leakage",
                ],
                variance_rows,
            ),
            "",
            "The companion CSV contains all 43 ingredient points. The low-"
            "consumption table must total "
            f"**{_money(variance['low_consumption_value'].sum())}** and the "
            "leakage rank must total "
            f"**{_money(variance['leakage_value'].sum())}**.",
            "",
            "The theoretical-consumption detail must contain "
            f"**{len(_scope(models['theoretical']))} rows**. The menu COGS "
            f"detail must contain **{len(_scope(models['menu_profit']))} rows**, "
            f"reconciling to **{_money(_scope(models['menu_profit'])['net_sales'].sum())}** "
            "net sales and "
            f"**{_money(_scope(models['menu_profit'])['theoretical_cogs'].sum())}** "
            "theoretical COGS.",
            "",
            "### BCG Quadrant Control",
            "",
        ]
    )
    menu = _scope(models["menu_summary"])
    bcg_rows = []
    for (outlet, quadrant), group in menu.groupby(
        ["outlet_code", "bcg_quadrant"]
    ):
        bcg_rows.append(
            [
                outlet,
                quadrant,
                len(group),
                _money(group["net_sales"].sum()),
            ]
        )
    lines.extend(
        _md_table(
            ["Outlet", "Quadrant", "Menu items", "Net sales"],
            bcg_rows,
        )
    )
    menu_rollup = (
        menu.groupby(["menu_item_code", "menu_item_name"], as_index=False)
        .agg(
            sold_qty=("sold_qty", "sum"),
            net_sales=("net_sales", "sum"),
            theoretical_cogs=("theoretical_cogs", "sum"),
            gross_margin_value=("gross_margin_value", "sum"),
        )
    )
    menu_rollup["gross_margin_percent"] = (
        menu_rollup["gross_margin_value"] / menu_rollup["net_sales"] * 100
    )
    top_menu_rows = []
    for _, row in menu_rollup.sort_values(
        "gross_margin_value", ascending=False
    ).head(10).iterrows():
        top_menu_rows.append(
            [
                row["menu_item_code"],
                row["menu_item_name"],
                _number(row["sold_qty"], 0),
                _money(row["net_sales"]),
                _money(row["theoretical_cogs"]),
                _money(row["gross_margin_value"]),
                _percent(row["gross_margin_percent"], 2),
            ]
        )
    lines.extend(
        [
            "",
            "### Top 10 Menu Items By Gross Margin Value",
            "",
            *_md_table(
                [
                    "Item",
                    "Menu item",
                    "Sold qty",
                    "Net sales",
                    "COGS",
                    "Gross margin",
                    "Margin %",
                ],
                top_menu_rows,
            ),
            "",
            "### Category Contribution",
            "",
        ]
    )
    category_rows = []
    for category, group in menu.groupby("category_name"):
        category_rows.append(
            [
                category,
                _money(group["net_sales"].sum()),
                _percent(
                    group["net_sales"].sum() / menu["net_sales"].sum() * 100,
                    2,
                ),
            ]
        )
    category_rows.sort(
        key=lambda row: float(row[1].replace("INR ", "").replace(",", "")),
        reverse=True,
    )
    lines.extend(
        _md_table(["Category", "Net sales", "Contribution"], category_rows)
    )
    sales_month_rows = []
    for period, group in models["sales"].groupby("source_period_code"):
        sales_month_rows.append(
            [
                period,
                _money(group["net_sales"].sum()),
                _number(group["sold_qty"].sum(), 0),
            ]
        )
    lines.extend(
        [
            "",
            "### Sales Trend Monthly Control Totals",
            "",
            *_md_table(
                ["Period", "Net sales", "Sold quantity"],
                sales_month_rows,
            ),
            "",
            "The chart remains daily. Reconcile its daily points to these monthly "
            "totals; all daily outlet points are in the companion CSV.",
            "",
        ]
    )

    lines.extend(
        [
            "## Page 4 Chart And Explorer Checks",
            "",
            "### SCM Monthly Trend",
            "",
        ]
    )
    scm_rows = []
    for period, group in models["scm"].groupby("source_period_code"):
        scm_rows.append(
            [
                period,
                _money(group["closing_stock_value"].sum()),
                _money(group["open_po_value"].sum()),
                _money(group["net_sales"].sum()),
                _money(group["actual_consumption_value"].sum()),
            ]
        )
    lines.extend(
        _md_table(
            [
                "Period",
                "Closing stock",
                "Open PO",
                "Net sales",
                "Actual consumption",
            ],
            scm_rows,
        )
    )
    variance_trend_rows = []
    for period, group in models["variance"].groupby("source_period_code"):
        variance_trend_rows.append(
            [
                period,
                _money(group["signed_variance_value"].sum()),
                _money(group["leakage_value"].sum()),
            ]
        )
    lines.extend(
        [
            "",
            "### Consumption Variance Trend",
            "",
            *_md_table(
                ["Period", "Signed variance", "Leakage"],
                variance_trend_rows,
            ),
            "",
            "### Data-Quality Tiles",
            "",
        ]
    )
    dq = models["dq_truth"]
    dq_all = dq[
        (dq["source_period_code"] == "ALL") & (dq["outlet_code"] == "ALL")
    ].iloc[0]
    dq_rows = [
        ["NEGATIVE_STOCK", int(dq_all["negative_stock_count"])],
        [
            "ZERO_STOCK_WITH_DEMAND",
            int(dq_all["zero_stock_with_demand_count"]),
        ],
        [
            "SOLD_ITEM_MISSING_RECIPE",
            int(dq_all["sold_items_missing_recipe_count"]),
        ],
        [
            "OPERATIONAL_ITEM_MISSING_MASTER",
            int(dq_all["operational_items_missing_master_count"]),
        ],
        [
            "UOM_MISMATCH_WITHOUT_CONVERSION",
            int(dq_all["uom_mismatch_without_conversion_count"]),
        ],
        [
            "OPEN_PO_MISSING_EXPECTED_DELIVERY",
            int(dq_all["open_po_missing_expected_delivery_count"]),
        ],
    ]
    lines.extend(_md_table(["Exception type", "Expected count"], dq_rows))
    lines.extend(
        [
            "",
            "The two additional Query 34 detail-only controls, "
            "`VENDOR_NAME_MULTIPLE_CODES` and "
            "`TRANSACTION_VENDOR_MISSING_VENDOR_REPORT`, both return **0** in "
            "this synthetic baseline.",
            "",
            "### Explorer Row Counts - Default State",
            "",
        ]
    )
    explorer_rows = []
    for report in [
        "CT_P4_Descriptive_Explorer",
        "CT_P4_Data_Quality_Detail",
        "CT_P4_Sales_Explorer",
        "CT_P4_Item_Explorer",
        "CT_P4_PO_Explorer",
        "CT_P4_GRN_Explorer",
        "CT_P4_Vendor_Explorer",
        "CT_P4_Expiry_Explorer_Demo",
    ]:
        row = next(
            record
            for record in records
            if record["report_name"] == report
            and record["metric"] == "row_count"
        )
        explorer_rows.append([report, int(row["expected_value"])])
    lines.extend(_md_table(["Explorer", "Expected rows"], explorer_rows))
    lines.extend(
        [
            "",
            "## Stop Conditions",
            "",
            "Stop dashboard construction and investigate when:",
            "",
            "- Query 27 shows 74 current actions; that means expiry has been "
            "incorrectly merged back into stockout risk.",
            "- Query 36 shows 21 current risky POs; the correct `month_03` result "
            "is zero.",
            "- a current-state card adds all three inventory snapshots;",
            "- a trend collapses to only `month_03`; the global As-of filter was "
            "mapped to it incorrectly;",
            "- Query 34 zero-count controls disappear;",
            "- mixed kg, litre and pcs quantities are summed together;",
            "- Query 30 vendor percentages are averaged across outlets; or",
            "- price-change percentages are aggregated across different tuples.",
            "",
            "After each tab passes this reference, record the result in "
            "`IMPLEMENTATION_STATUS.md` and continue to the next dashboard tab.",
        ]
    )
    with OUTPUT_MD.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines) + "\n")


def build() -> dict[str, int]:
    truth.build()
    models = _query_models()
    records = _build_records(models)
    _write_csv(records)
    _write_markdown(models, records)
    return {
        "acceptance_points": len(records),
        "markdown_lines": len(OUTPUT_MD.read_text(encoding="utf-8").splitlines()),
    }


if __name__ == "__main__":
    print(build())
