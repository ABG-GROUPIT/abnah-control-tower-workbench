from __future__ import annotations

import shutil
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EXPORTS = ROOT / "exports" / "control_tower_zoho"
NORMALIZED = EXPORTS / "normalized"
TRUTH = EXPORTS / "truth"
DOC = ROOT / "docs" / "control_tower_v2_truth_reference.md"

PERIODS = ["month_01", "month_02", "month_03"]
OUTLETS = ["OUT001", "OUT002", "OUT003"]


def _read_landing(stem: str) -> pd.DataFrame:
    return pd.read_csv(NORMALIZED / f"RAWN_CT_{stem}.csv", low_memory=False)


def _read_aux(name: str) -> pd.DataFrame:
    return pd.read_csv(EXPORTS / f"{name}.csv", low_memory=False)


def _numbers(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    result = frame.copy()
    for column in columns:
        result[column] = pd.to_numeric(result[column], errors="coerce").fillna(0)
    return result


def _dates(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    result = frame.copy()
    for column in columns:
        result[column] = pd.to_datetime(result[column], errors="coerce")
    return result


def _scope(frame: pd.DataFrame, period: str, outlet: str) -> pd.DataFrame:
    result = frame
    if period != "ALL":
        result = result[result["source_period_code"] == period]
    if outlet != "ALL":
        result = result[result["outlet_code"] == outlet]
    return result


def _scopes() -> list[tuple[str, str, str]]:
    rows = []
    for period in [*PERIODS, "ALL"]:
        for outlet in [*OUTLETS, "ALL"]:
            if period == "ALL" and outlet == "ALL":
                scope_type = "all_periods_all_outlets"
            elif period == "ALL":
                scope_type = "all_periods_one_outlet"
            elif outlet == "ALL":
                scope_type = "one_period_all_outlets"
            else:
                scope_type = "one_period_one_outlet"
            rows.append((scope_type, period, outlet))
    return rows


def _round_output(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    for column in result.select_dtypes(include=["number"]).columns:
        if column.endswith("_percent") or column.endswith("_pct"):
            result[column] = result[column].round(4)
        elif "qty" in column or "quantity" in column or "days" in column:
            result[column] = result[column].round(6)
        else:
            result[column] = result[column].round(2)
    return result


def _recipe_model() -> tuple[pd.DataFrame, pd.DataFrame]:
    recipe = _numbers(
        _read_landing("item_recipe_report"),
        ["recipe_qty_per_menu_unit"],
    )
    items = _numbers(
        _read_landing("closing_stock"),
        ["average_price"],
    )
    items = (
        items.groupby("item_code", as_index=False)
        .agg(
            canonical_uom=("unit_name", "max"),
            average_price=("average_price", "mean"),
            observed_uom_count=("unit_name", "nunique"),
        )
    )
    recipe = recipe.merge(
        items[
            [
                "item_code",
                "canonical_uom",
                "average_price",
            ]
        ],
        left_on="ingredient_code",
        right_on="item_code",
        how="left",
    )
    recipe["uom_conversion_factor"] = np.where(
        recipe["recipe_unit"].str.casefold()
        == recipe["canonical_uom"].str.casefold(),
        1.0,
        np.nan,
    )
    recipe["canonical_recipe_qty"] = (
        recipe["recipe_qty_per_menu_unit"] * recipe["uom_conversion_factor"]
    )
    recipe["ingredient_cost_per_menu_unit"] = (
        recipe["canonical_recipe_qty"] * recipe["average_price"]
    )
    recipe_unit_cost = (
        recipe.groupby(["menu_item_number", "menu_item_name"], as_index=False)
        .agg(
            theoretical_cost_per_menu_unit=(
                "ingredient_cost_per_menu_unit",
                "sum",
            ),
            recipe_ingredient_count=("ingredient_code", "nunique"),
        )
        .rename(columns={"menu_item_number": "menu_item_code"})
    )
    return recipe, recipe_unit_cost


def _purchase_model() -> tuple[pd.DataFrame, pd.DataFrame]:
    po = _numbers(
        _dates(
            _read_landing("enterprise_purchase_order"),
            ["po_date", "expected_delivery_date", "source_period_end"],
        ),
        [
            "processed_qty",
            "remaining_balance_qty",
            "ordered_qty",
            "unit_price",
            "total_item_cost",
        ],
    ).rename(
        columns={
            "source_outlet_code": "outlet_code",
            "source_outlet_name": "outlet_name",
        }
    )
    po["is_open_po"] = (
        po["po_status"].isin(["Pending", "Partially Received"])
        | (po["remaining_balance_qty"] > 0)
    )
    po["open_po_value"] = po["remaining_balance_qty"] * po["unit_price"]
    po["processed_po_value"] = po["processed_qty"] * po["unit_price"]
    po["missing_expected_delivery_flag"] = (
        po["is_open_po"] & po["expected_delivery_date"].isna()
    )
    po["delayed_po_flag"] = (
        po["is_open_po"]
        & po["expected_delivery_date"].notna()
        & (po["expected_delivery_date"] < po["source_period_end"])
    )

    entry = _numbers(
        _dates(
            _read_landing("enterprise_entry"),
            ["entry_date", "invoice_date"],
        ),
        ["entry_qty", "base_amt", "total_amt"],
    ).rename(
        columns={
            "source_outlet_code": "outlet_code",
            "source_outlet_name": "outlet_name",
            "transaction_number": "grn_number",
        }
    )
    returns = _numbers(
        _read_landing("enterprise_stock_return"),
        ["return_qty", "return_amt"],
    ).rename(
        columns={
            "source_outlet_code": "outlet_code",
            "transaction_number": "grn_number",
        }
    )
    return_source_available = not returns.empty
    return_by_grn = returns.groupby(
        ["source_period_code", "outlet_code", "grn_number", "item_code"],
        as_index=False,
    ).agg(return_qty=("return_qty", "sum"), return_value=("return_amt", "sum"))
    entry = entry.merge(
        return_by_grn,
        on=["source_period_code", "outlet_code", "grn_number", "item_code"],
        how="left",
    )
    entry[["return_qty", "return_value"]] = entry[
        ["return_qty", "return_value"]
    ].fillna(0)
    receipt = entry.groupby(
        ["source_period_code", "outlet_code", "po_number", "item_code"],
        as_index=False,
    ).agg(
        receipt_date=("entry_date", "max"),
        received_qty=("entry_qty", "sum"),
        receipt_subtotal=("base_amt", "sum"),
        receipt_total=("total_amt", "sum"),
        return_qty=("return_qty", "sum"),
        return_value=("return_value", "sum"),
    )
    performance = po.merge(
        receipt,
        on=["source_period_code", "outlet_code", "po_number", "item_code"],
        how="left",
    )
    for column in [
        "received_qty",
        "receipt_subtotal",
        "receipt_total",
        "return_qty",
        "return_value",
    ]:
        performance[column] = performance[column].fillna(0)
    performance["return_source_available"] = return_source_available
    performance["eligible_closed_line_flag"] = (
        ~performance["is_open_po"]
        & performance["receipt_date"].notna()
        & performance["expected_delivery_date"].notna()
    )
    performance["on_time_flag"] = (
        performance["receipt_date"].notna()
        & performance["expected_delivery_date"].notna()
        & (performance["receipt_date"] <= performance["expected_delivery_date"])
    )
    performance["in_full_flag"] = (
        performance["received_qty"] >= performance["ordered_qty"]
    )
    performance["otif_success_flag"] = (
        performance["eligible_closed_line_flag"]
        & performance["on_time_flag"]
        & performance["in_full_flag"]
    )
    performance["lead_time_deviation_days"] = (
        performance["receipt_date"] - performance["expected_delivery_date"]
    ).dt.days
    return po, performance


def _inventory_risk_model(
    recipe: pd.DataFrame,
    po: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    closing = _numbers(
        _read_landing("closing_stock"),
        ["total_qty", "average_price", "total_amt"],
    ).rename(
        columns={
            "source_outlet_code": "outlet_code",
            "source_outlet_name": "outlet_name",
            "total_qty": "current_stock_qty",
            "average_price": "average_unit_cost",
            "total_amt": "closing_value",
            "unit_name": "canonical_uom",
        }
    )
    forecast = _numbers(
        _read_aux("AUX_Menu_Demand_Forecast"),
        ["forecast_qty", "forecast_net_sales"],
    ).rename(columns={"forecast_as_of_month": "source_period_code"})
    forecast_ingredient = forecast.merge(
        recipe[
            [
                "menu_item_number",
                "ingredient_code",
                "ingredient_name",
                "canonical_recipe_qty",
                "canonical_uom",
            ]
        ],
        left_on="menu_item_code",
        right_on="menu_item_number",
        how="inner",
    )
    forecast_ingredient["forecast_ingredient_qty"] = (
        forecast_ingredient["forecast_qty"]
        * forecast_ingredient["canonical_recipe_qty"]
    )
    forecast_item = forecast_ingredient.groupby(
        ["source_period_code", "outlet_code", "ingredient_code"],
        as_index=False,
    ).agg(forecast_required_qty=("forecast_ingredient_qty", "sum"))
    forecast_item = forecast_item.rename(columns={"ingredient_code": "item_code"})

    open_po = (
        po[po["is_open_po"]]
        .groupby(["source_period_code", "outlet_code", "item_code"], as_index=False)
        .agg(
            valid_open_po_qty=("remaining_balance_qty", "sum"),
            open_po_value=("open_po_value", "sum"),
            valid_open_po_count=("po_number", "nunique"),
        )
    )
    expiry = _numbers(
        _dates(
            _read_aux("AUX_Expiry_Estimate"),
            ["as_of_date", "receipt_date", "estimated_expiry_date"],
        ),
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
    risk = closing.merge(
        forecast_item,
        on=["source_period_code", "outlet_code", "item_code"],
        how="left",
    ).merge(
        open_po,
        on=["source_period_code", "outlet_code", "item_code"],
        how="left",
    ).merge(
        expiry[
            [
                "source_period_code",
                "outlet_code",
                "item_code",
                "batch_allocation_id",
                "batch_number",
                "receipt_date",
                "grn_number",
                "po_number",
                "vendor_name",
                "receipt_source_status",
                "batch_remaining_qty",
                "expiry_qty_at_risk",
                "expiry_risk_value",
                "estimated_expiry_date",
                "days_to_expiry",
                "risk_status",
                "estimation_method",
                "production_use_status",
            ]
        ],
        on=["source_period_code", "outlet_code", "item_code"],
        how="left",
    )
    fill_columns = [
        "forecast_required_qty",
        "valid_open_po_qty",
        "open_po_value",
        "valid_open_po_count",
        "expiry_qty_at_risk",
        "expiry_risk_value",
    ]
    risk[fill_columns] = risk[fill_columns].fillna(0)
    risk["expiry_source_status"] = risk["production_use_status"].fillna(
        "no_estimated_expiry_exposure"
    )
    risk["required_qty_with_safety"] = risk["forecast_required_qty"] * 1.15
    risk["available_qty"] = risk["current_stock_qty"] + risk["valid_open_po_qty"]
    risk["shortage_qty"] = (
        risk["required_qty_with_safety"] - risk["available_qty"]
    ).clip(lower=0)
    risk["days_cover"] = np.where(
        risk["forecast_required_qty"] > 0,
        risk["available_qty"] / (risk["forecast_required_qty"] / 7),
        np.nan,
    )
    risk["stockout_risk_severity"] = "GREEN"
    risk.loc[
        risk["required_qty_with_safety"] > risk["available_qty"],
        "stockout_risk_severity",
    ] = "AMBER"
    risk.loc[
        risk["forecast_required_qty"] > risk["available_qty"],
        "stockout_risk_severity",
    ] = "RED"
    risk.loc[
        (risk["current_stock_qty"] <= 0)
        & (risk["forecast_required_qty"] > 0),
        "stockout_risk_severity",
    ] = "PURPLE"
    risk["expiry_risk_severity"] = "GREEN"
    risk.loc[risk["expiry_qty_at_risk"] > 0, "expiry_risk_severity"] = "AMBER"
    risk.loc[
        (risk["expiry_qty_at_risk"] > 0) & (risk["days_to_expiry"] <= 3),
        "expiry_risk_severity",
    ] = "RED"
    risk.loc[
        (risk["expiry_qty_at_risk"] > 0) & (risk["days_to_expiry"] <= 0),
        "expiry_risk_severity",
    ] = "PURPLE"
    severity_rank = {"GREEN": 1, "AMBER": 2, "RED": 3, "PURPLE": 4}
    risk["risk_severity_rank"] = np.maximum(
        risk["stockout_risk_severity"].map(severity_rank),
        risk["expiry_risk_severity"].map(severity_rank),
    )
    rank_severity = {value: key for key, value in severity_rank.items()}
    risk["risk_severity"] = risk["risk_severity_rank"].map(rank_severity)
    risk["risk_type"] = "HEALTHY"
    risk.loc[
        risk["stockout_risk_severity"] != "GREEN",
        "risk_type",
    ] = "STOCKOUT"
    risk.loc[
        risk["expiry_risk_severity"] != "GREEN",
        "risk_type",
    ] = "EXPIRY"
    risk.loc[
        (risk["stockout_risk_severity"] != "GREEN")
        & (risk["expiry_risk_severity"] != "GREEN"),
        "risk_type",
    ] = "STOCKOUT + EXPIRY"
    risk["shortage_cost_value"] = risk["shortage_qty"] * risk["average_unit_cost"]
    risk["total_risk_value"] = (
        risk["shortage_cost_value"] + risk["expiry_risk_value"]
    )
    risk["recommended_action"] = "Monitor"
    risk.loc[
        (risk["stockout_risk_severity"] == "PURPLE")
        & (risk["valid_open_po_qty"] == 0),
        "recommended_action",
    ] = "Raise purchase order"
    risk.loc[
        (risk["shortage_qty"] > 0) & (risk["valid_open_po_qty"] > 0),
        "recommended_action",
    ] = "Expedite existing PO"
    risk.loc[
        (risk["shortage_qty"] <= 0)
        & (risk["expiry_qty_at_risk"] > 0)
        & (risk["days_to_expiry"] <= 3),
        "recommended_action",
    ] = "Transfer, promote, or consume near-expiry stock"
    risk.loc[
        (risk["shortage_qty"] <= 0)
        & (risk["expiry_qty_at_risk"] > 0)
        & (risk["days_to_expiry"] > 3),
        "recommended_action",
    ] = "Review FIFO rotation and demand plan"
    risk.loc[
        (risk["shortage_qty"] <= 0)
        & (risk["expiry_risk_severity"] == "PURPLE"),
        "recommended_action",
    ] = "Quarantine expired batch and investigate"
    risk.loc[
        (risk["stockout_risk_severity"] != "GREEN")
        & (risk["expiry_risk_severity"] != "GREEN"),
        "recommended_action",
    ] = "Resolve stock shortage and quarantine or rotate at-risk batch"
    risk["action_owner"] = "Supply Chain"
    risk.loc[risk["shortage_qty"] > 0, "action_owner"] = "Procurement"
    risk.loc[risk["expiry_qty_at_risk"] > 0, "action_owner"] = "Operations"
    risk.loc[
        (risk["shortage_qty"] > 0) & (risk["expiry_qty_at_risk"] > 0),
        "action_owner",
    ] = "Operations / Procurement"
    risk["due_band"] = "Monitor"
    risk.loc[
        risk["risk_severity"] == "AMBER",
        "due_band",
    ] = "Due in 3 days"
    risk.loc[
        risk["risk_severity"].isin(["PURPLE", "RED"]),
        "due_band",
    ] = "Due today"
    forecast_menu_ingredient = forecast_ingredient.groupby(
        [
            "source_period_code",
            "outlet_code",
            "outlet_name",
            "menu_item_code",
            "menu_item_name",
            "ingredient_code",
            "ingredient_name",
        ],
        as_index=False,
    ).agg(
        forecast_menu_qty=("forecast_qty", "sum"),
        forecast_ingredient_qty=("forecast_ingredient_qty", "sum"),
        forecast_net_sales=("forecast_net_sales", "sum"),
    )
    menu_impact = forecast_menu_ingredient.merge(
        risk[
            [
                "source_period_code",
                "outlet_code",
                "item_code",
                "stockout_risk_severity",
                "shortage_qty",
            ]
        ],
        left_on=["source_period_code", "outlet_code", "ingredient_code"],
        right_on=["source_period_code", "outlet_code", "item_code"],
        how="inner",
    )
    menu_impact = menu_impact[
        menu_impact["stockout_risk_severity"] != "GREEN"
    ].copy()
    menu_impact = menu_impact.rename(
        columns={"stockout_risk_severity": "risk_severity"}
    )
    menu_impact["risk_ingredient_count"] = menu_impact.groupby(
        ["source_period_code", "outlet_code", "menu_item_code"]
    )["ingredient_code"].transform("nunique")
    menu_impact["allocated_forecast_net_sales_at_risk"] = (
        menu_impact["forecast_net_sales"] / menu_impact["risk_ingredient_count"]
    )
    return risk, menu_impact, forecast


def _consumption_model(
    recipe_unit_cost: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    actual = _numbers(
        _read_landing("enterprise_variance_normal"),
        [
            "actual_consumption_qty",
            "actual_consumption_amt",
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
        }
    )
    actual["actual_consumption_qty"] = (
        actual["opening_qty"]
        + actual["purchase_qty"]
        + actual["stock_in_qty"]
        - actual["stock_out_qty"]
        - actual["return_qty"]
        - actual["closing_qty"]
    )
    actual["actual_consumption_amt"] = (
        actual["actual_consumption_qty"] * actual["average_price"]
    )
    theoretical = _numbers(
        _read_aux("AUX_Theoretical_Consumption"),
        ["theoretical_qty", "average_price"],
    ).rename(columns={"unit": "canonical_uom"})
    variance = actual.merge(
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
        variance["actual_consumption_qty"] - variance["theoretical_qty"]
    )
    variance["variance_value"] = variance["variance_qty"] * variance["average_price"]
    variance["leakage_value"] = variance["variance_qty"].clip(lower=0) * variance[
        "average_price"
    ]
    variance["low_consumption_qty"] = (-variance["variance_qty"]).clip(lower=0)
    variance["low_consumption_value"] = (
        variance["low_consumption_qty"] * variance["average_price"]
    )

    sales = _numbers(
        _read_landing("gross_net_margin"),
        ["item_qty", "net_sale_value", "purchase_value"],
    ).rename(
        columns={
            "source_outlet_code": "outlet_code",
            "source_outlet_name": "outlet_name",
            "item_code": "menu_item_code",
            "item_name": "menu_item_name",
            "item_qty": "sold_qty",
            "net_sale_value": "net_sales",
            "purchase_value": "source_reported_purchase_value",
        }
    )
    menu_profit = sales.groupby(
        [
            "source_period_code",
            "outlet_code",
            "outlet_name",
            "menu_item_code",
            "menu_item_name",
            "super_category_name",
            "category_name",
        ],
        as_index=False,
    ).agg(
        sold_qty=("sold_qty", "sum"),
        net_sales=("net_sales", "sum"),
        source_reported_purchase_value=("source_reported_purchase_value", "sum"),
    )
    menu_profit = menu_profit.merge(
        recipe_unit_cost,
        on=["menu_item_code", "menu_item_name"],
        how="left",
    )
    menu_profit["theoretical_cost_per_menu_unit"] = menu_profit[
        "theoretical_cost_per_menu_unit"
    ].fillna(0)
    menu_profit["theoretical_cogs"] = (
        menu_profit["sold_qty"] * menu_profit["theoretical_cost_per_menu_unit"]
    )
    menu_profit["gross_margin_value"] = (
        menu_profit["net_sales"] - menu_profit["theoretical_cogs"]
    )
    menu_profit["gross_margin_percent"] = np.where(
        menu_profit["net_sales"] != 0,
        menu_profit["gross_margin_value"] / menu_profit["net_sales"] * 100,
        np.nan,
    )
    return variance, menu_profit, sales


def _page_1(
    risk: pd.DataFrame,
    menu_impact: pd.DataFrame,
    forecast: pd.DataFrame,
    po: pd.DataFrame,
    expiry: pd.DataFrame,
) -> pd.DataFrame:
    rows = []
    open_po = po[po["is_open_po"]]
    for scope_type, period, outlet in _scopes():
        r = _scope(risk, period, outlet)
        risky = r[r["stockout_risk_severity"] != "GREEN"]
        m = _scope(menu_impact, period, outlet)
        f = _scope(forecast, period, outlet)
        p = _scope(open_po, period, outlet)
        x = _scope(expiry, period, outlet)
        risky_keys = risky[["source_period_code", "outlet_code", "item_code"]]
        risky_po = p.merge(
            risky_keys,
            on=["source_period_code", "outlet_code", "item_code"],
            how="inner",
        )
        stockout_menu = m[m["shortage_qty"] > 0]
        rows.append(
            {
                "scope_type": scope_type,
                "source_period_code": period,
                "outlet_code": outlet,
                "outlets_at_risk": risky["outlet_code"].nunique(),
                "risk_item_count": len(risky),
                "menu_items_at_risk": m["menu_item_code"].nunique(),
                "stockout_risk_value": stockout_menu[
                    "allocated_forecast_net_sales_at_risk"
                ].sum(),
                "expiry_risk_value": x["expiry_risk_value"].sum(),
                "expiry_source_status": (
                    "synthetic_batch_linked_demo_no_posist_batch_source"
                ),
                "open_risky_po_count": risky_po["po_number"].nunique(),
                "forecast_menu_qty": f["forecast_qty"].sum(),
                "projected_shortage_qty_mixed_uom": risky["shortage_qty"].sum(),
                "shortage_cost_value": risky["shortage_cost_value"].sum(),
                "stockout_inventory_exposure": risky[
                    "shortage_cost_value"
                ].sum(),
                "total_risk_value": risky["shortage_cost_value"].sum(),
                "combined_demo_inventory_exposure_reference": (
                    risky["shortage_cost_value"].sum()
                    + x["expiry_risk_value"].sum()
                ),
                "action_count": len(risky),
                "purple_item_count": (
                    risky["stockout_risk_severity"] == "PURPLE"
                ).sum(),
                "red_item_count": (
                    risky["stockout_risk_severity"] == "RED"
                ).sum(),
                "amber_item_count": (
                    risky["stockout_risk_severity"] == "AMBER"
                ).sum(),
                "quantity_guardrail": (
                    "Do not display the mixed-UOM shortage total without a UOM filter."
                ),
            }
        )
    return _round_output(pd.DataFrame(rows))


def _query_27_projection(risk: pd.DataFrame) -> pd.DataFrame:
    projected = risk.copy()
    projected["snapshot_date"] = projected["stock_date"]
    projected["risk_severity"] = projected["stockout_risk_severity"]
    projected["risk_severity_rank"] = projected["risk_severity"].map(
        {"GREEN": 1, "AMBER": 2, "RED": 3, "PURPLE": 4}
    )
    projected["risk_type"] = np.where(
        projected["risk_severity"] == "GREEN",
        "HEALTHY",
        "STOCKOUT",
    )
    projected["total_risk_value"] = projected["shortage_cost_value"]
    projected["criticality"] = np.nan
    projected["primary_vendor"] = np.nan
    projected["alternate_vendor"] = np.nan
    projected["vendor_mapping_status"] = (
        "vendor_item_approval_mapping_unavailable"
    )
    projected["action_id"] = (
        projected["source_period_code"].astype(str)
        + ":"
        + projected["outlet_code"].astype(str)
        + ":"
        + projected["item_code"].astype(str)
    )
    projected["recommended_action"] = "Monitor"
    projected.loc[
        (projected["current_stock_qty"] <= 0)
        & (projected["forecast_required_qty"] > 0)
        & (projected["valid_open_po_qty"] == 0),
        "recommended_action",
    ] = "Raise purchase order"
    projected.loc[
        (projected["shortage_qty"] > 0)
        & (projected["valid_open_po_qty"] > 0),
        "recommended_action",
    ] = "Expedite existing PO"
    projected["action_owner"] = np.where(
        projected["shortage_qty"] > 0,
        "Procurement",
        "Supply Chain",
    )
    projected["due_band"] = "Monitor"
    projected.loc[
        projected["risk_severity"] == "AMBER",
        "due_band",
    ] = "Due in 3 days"
    projected.loc[
        projected["risk_severity"].isin(["PURPLE", "RED"]),
        "due_band",
    ] = "Due today"
    columns = [
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
        "stockout_risk_severity",
        "risk_severity",
        "risk_severity_rank",
        "risk_type",
        "shortage_cost_value",
        "total_risk_value",
        "criticality",
        "primary_vendor",
        "alternate_vendor",
        "vendor_mapping_status",
        "action_id",
        "recommended_action",
        "action_owner",
        "due_band",
    ]
    return projected[columns]


def _page_2(
    po: pd.DataFrame,
    performance: pd.DataFrame,
    closing: pd.DataFrame,
    wastage: pd.DataFrame,
) -> pd.DataFrame:
    expiry = _numbers(
        _read_aux("AUX_Expiry_Estimate"),
        ["expiry_risk_value"],
    )
    rows = []
    for scope_type, period, outlet in _scopes():
        p = _scope(po, period, outlet)
        v = _scope(performance, period, outlet)
        c = _scope(closing, period, outlet)
        w = _scope(wastage, period, outlet)
        x = _scope(expiry, period, outlet)
        eligible = v[v["eligible_closed_line_flag"]]
        ordered_qty = v["ordered_qty"].sum()
        received_qty = v["received_qty"].sum()
        returned_qty = v["return_qty"].sum()
        fill_rate = received_qty / ordered_qty * 100 if ordered_qty else np.nan
        otif = (
            eligible["otif_success_flag"].sum() / len(eligible) * 100
            if len(eligible)
            else np.nan
        )
        return_source_available = bool(v["return_source_available"].any())
        return_rate = (
            returned_qty / (received_qty + returned_qty) * 100
            if return_source_available and received_qty + returned_qty
            else np.nan
        )
        inventory_value = c["closing_value"].sum()
        open_po_value = p.loc[p["is_open_po"], "open_po_value"].sum()
        return_value = v["return_value"].sum() if return_source_available else np.nan
        wastage_value = w["wastage_value"].sum()
        rows.append(
            {
                "scope_type": scope_type,
                "source_period_code": period,
                "outlet_code": outlet,
                "monthly_purchase_value_ordered_gross": p[
                    "total_item_cost"
                ].sum(),
                "received_purchase_value": v["receipt_total"].sum(),
                "closing_inventory_value": inventory_value,
                "open_po_liability": open_po_value,
                "working_capital_locked": inventory_value + open_po_value,
                "open_po_count": p.loc[p["is_open_po"], "po_number"].nunique(),
                "delayed_po_count": p.loc[
                    p["delayed_po_flag"], "po_number"
                ].nunique(),
                "po_fill_rate_percent": fill_rate,
                "vendor_otif_percent": otif,
                "eligible_otif_line_count": len(eligible),
                "average_lead_time_deviation_days": eligible[
                    "lead_time_deviation_days"
                ].mean(),
                "vendor_return_source_status": (
                    "available" if return_source_available else "unavailable_header_only"
                ),
                "vendor_return_rate_percent": return_rate,
                "vendor_return_value_observed": return_value,
                "wastage_value_observed": wastage_value,
                "expiry_risk_value": x["expiry_risk_value"].sum(),
                "expiry_source_status": (
                    "synthetic_batch_linked_demo_no_posist_batch_source"
                ),
                "financial_leakage_observed": wastage_value,
                "financial_leakage_demo_scenario": (
                    wastage_value + x["expiry_risk_value"].sum()
                ),
            }
        )
    return _round_output(pd.DataFrame(rows))


def _page_3(
    variance: pd.DataFrame,
    menu_profit: pd.DataFrame,
) -> pd.DataFrame:
    rows = []
    for scope_type, period, outlet in _scopes():
        v = _scope(variance, period, outlet)
        m = _scope(menu_profit, period, outlet)
        net_sales = m["net_sales"].sum()
        cogs = m["theoretical_cogs"].sum()
        gross_margin = net_sales - cogs
        rows.append(
            {
                "scope_type": scope_type,
                "source_period_code": period,
                "outlet_code": outlet,
                "net_sales": net_sales,
                "quantity_sold": m["sold_qty"].sum(),
                "menu_item_count": m["menu_item_code"].nunique(),
                "theoretical_cogs": cogs,
                "source_reported_purchase_value": m[
                    "source_reported_purchase_value"
                ].sum(),
                "actual_consumption_value": v[
                    "actual_consumption_amt"
                ].sum(),
                "consumption_variance_value": v["variance_value"].sum(),
                "consumption_leakage_value": v["leakage_value"].sum(),
                "low_consumption_check_value": v[
                    "low_consumption_value"
                ].sum(),
                "menu_gross_margin": gross_margin,
                "menu_gross_margin_percent": (
                    gross_margin / net_sales * 100 if net_sales else np.nan
                ),
                "quantity_guardrail": (
                    "Ingredient quantities remain item-and-UOM grain; do not sum "
                    "kg, litre and pieces into one KPI."
                ),
            }
        )
    return _round_output(pd.DataFrame(rows))


def _page_4(
    page_2: pd.DataFrame,
    page_3: pd.DataFrame,
    risk: pd.DataFrame,
    sales: pd.DataFrame,
    recipe: pd.DataFrame,
    po: pd.DataFrame,
    operational_items: pd.DataFrame,
    item_master: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    dq_rows = []
    recipe_items = set(recipe["menu_item_number"].dropna())
    master_items = set(item_master["item_code"].dropna())
    for scope_type, period, outlet in _scopes():
        r = _scope(risk, period, outlet)
        s = _scope(sales, period, outlet)
        p = _scope(po, period, outlet)
        ops = _scope(operational_items, period, outlet)
        sold_items = set(s.loc[s["sold_qty"] > 0, "menu_item_code"].dropna())
        operational_item_ids = set(ops["item_code"].dropna())
        observed_uom_count = (
            ops.dropna(subset=["item_code", "observed_uom"])
            .groupby("item_code")["observed_uom"]
            .nunique()
        )
        mismatch_items = {
            item
            for item, count in observed_uom_count.items()
            if count > 1 and item not in master_items
        }
        dq_rows.append(
            {
                "scope_type": scope_type,
                "source_period_code": period,
                "outlet_code": outlet,
                "negative_stock_count": int((r["current_stock_qty"] < 0).sum()),
                "zero_stock_with_demand_count": int(
                    (
                        (r["current_stock_qty"] == 0)
                        & (r["forecast_required_qty"] > 0)
                    ).sum()
                ),
                "sold_items_missing_recipe_count": len(
                    sold_items - recipe_items
                ),
                "operational_items_missing_master_count": len(
                    operational_item_ids - master_items
                ),
                "uom_mismatch_without_conversion_count": len(mismatch_items),
                "open_po_missing_expected_delivery_count": p.loc[
                    p["missing_expected_delivery_flag"], "po_number"
                ].nunique(),
            }
        )
    dq = pd.DataFrame(dq_rows)
    page = page_2[
        [
            "scope_type",
            "source_period_code",
            "outlet_code",
            "closing_inventory_value",
            "open_po_liability",
        ]
    ].merge(
        page_3[
            [
                "scope_type",
                "source_period_code",
                "outlet_code",
                "net_sales",
                "actual_consumption_value",
                "consumption_variance_value",
                "consumption_leakage_value",
            ]
        ],
        on=["scope_type", "source_period_code", "outlet_code"],
        how="inner",
    ).merge(
        dq,
        on=["scope_type", "source_period_code", "outlet_code"],
        how="inner",
    )
    return _round_output(page), dq


def _operational_items(
    closing: pd.DataFrame,
    po: pd.DataFrame,
) -> pd.DataFrame:
    entry = _read_landing("enterprise_entry").rename(
        columns={
            "source_outlet_code": "outlet_code",
            "unit": "observed_uom",
        }
    )
    movement = _read_landing("stock_in_stock_out").rename(
        columns={
            "source_outlet_code": "outlet_code",
            "unit": "observed_uom",
        }
    )
    item_code_by_name = (
        _read_landing("closing_stock")
        .drop_duplicates("item_name")
        .set_index("item_name")["item_code"]
    )
    movement["item_code"] = movement["item_name"].map(item_code_by_name)
    frames = [
        closing[
            [
                "source_period_code",
                "outlet_code",
                "item_code",
                "canonical_uom",
            ]
        ].rename(columns={"canonical_uom": "observed_uom"}),
        po[
            [
                "source_period_code",
                "outlet_code",
                "item_code",
                "unit",
            ]
        ].rename(columns={"unit": "observed_uom"}),
        entry[
            [
                "source_period_code",
                "outlet_code",
                "item_code",
                "observed_uom",
            ]
        ],
        movement[
            [
                "source_period_code",
                "outlet_code",
                "item_code",
                "observed_uom",
            ]
        ],
    ]
    return pd.concat(frames, ignore_index=True)


def _acceptance_checks(
    page_1: pd.DataFrame,
    page_4: pd.DataFrame,
) -> pd.DataFrame:
    p1 = page_1[
        (page_1["source_period_code"] == "ALL")
        & (page_1["outlet_code"] == "ALL")
    ].iloc[0]
    p4 = page_4[
        (page_4["source_period_code"] == "ALL")
        & (page_4["outlet_code"] == "ALL")
    ].iloc[0]
    query_manifest = pd.read_csv(
        ROOT / "docs" / "zoho_control_tower_v2_sql" / "QUERY_TABLE_MANIFEST.csv"
    )
    checks = [
        ("negative_stock_count", p4["negative_stock_count"], 1, 0),
        (
            "zero_stock_with_demand_count",
            p4["zero_stock_with_demand_count"],
            2,
            0,
        ),
        (
            "open_po_missing_expected_delivery_count",
            p4["open_po_missing_expected_delivery_count"],
            3,
            0,
        ),
        (
            "sold_items_missing_recipe_count",
            p4["sold_items_missing_recipe_count"],
            0,
            0,
        ),
        (
            "operational_items_missing_master_count",
            p4["operational_items_missing_master_count"],
            0,
            0,
        ),
        ("query_table_count", len(query_manifest), 38, 0),
        (
            "maximum_query_dependency_level",
            query_manifest["dependency_level"].max(),
            3,
            0,
        ),
        (
            "all_period_stockout_risk_value_reference",
            p1["stockout_risk_value"],
            p1["stockout_risk_value"],
            0.01,
        ),
        (
            "all_period_stockout_action_count",
            p1["action_count"],
            16,
            0,
        ),
        (
            "all_period_stockout_risk_item_count",
            p1["risk_item_count"],
            16,
            0,
        ),
        (
            "all_period_open_risky_po_count",
            p1["open_risky_po_count"],
            1,
            0,
        ),
        (
            "expiry_demo_value_present",
            int(p1["expiry_risk_value"] > 0),
            1,
            0,
        ),
    ]
    rows = []
    for check_id, observed, expected, tolerance in checks:
        numeric_observed = float(observed)
        numeric_expected = float(expected)
        rows.append(
            {
                "check_id": check_id,
                "observed": numeric_observed,
                "expected": numeric_expected,
                "tolerance": tolerance,
                "status": (
                    "PASS"
                    if abs(numeric_observed - numeric_expected) <= tolerance
                    else "FAIL"
                ),
            }
        )
    return pd.DataFrame(rows)


def _write_reference(
    outputs: dict[str, pd.DataFrame],
    checks: pd.DataFrame,
) -> None:
    overall = {
        name: frame[
            (frame["source_period_code"] == "ALL")
            & (frame["outlet_code"] == "ALL")
        ].iloc[0]
        for name, frame in outputs.items()
        if {"source_period_code", "outlet_code"}.issubset(frame.columns)
    }
    lines = [
        "# Control Tower v2 Synthetic Truth Reference",
        "",
        "Generated by `python scripts/build_control_tower_truth_pack.py`.",
        "",
        "This pack is the acceptance baseline for the synthetic three-outlet, "
        "three-month demo. It is not ABNAH production truth.",
        "",
        "## Core Guardrails",
        "",
        "- Page 3 uses **consumption**, never yield.",
        "- Theoretical COGS is calculated from sold menu quantity, recipe quantity, "
        "UOM conversion, and average ingredient cost.",
        "- OTIF uses only eligible closed PO lines linked by outlet, PO number, "
        "item code, and GRN evidence. It remains a formula demo until actual "
        "PO-to-GRN coverage materially improves.",
        "- Stockout risk value is de-duplicated forecast menu net sales. Shared "
        "menu revenue is allocated equally across its risky ingredients.",
        "- Exact expiry remains unavailable because the POSIST expiry module and "
        "batch-expiry evidence are not enabled. The demo models one synthetic "
        "near-expiry FIFO tranche per qualifying outlet/item/period, not a complete "
        "batch ledger. Of 206 demo tranches, 79 inherit synthetic receipt/GRN/PO "
        "lineage and 127 are explicitly marked synthetic opening-stock fallbacks. "
        "None can be published as ABNAH production truth.",
        "- Ingredient quantities cannot be summed across kg, litre, and pieces "
        "without a UOM filter.",
        "",
        "## Overall Acceptance Values",
        "",
    ]
    for page_name, row in overall.items():
        lines.append(f"### {page_name.replace('_', ' ').title()}")
        lines.append("")
        for key, value in row.items():
            if key in {"scope_type", "source_period_code", "outlet_code"}:
                continue
            if isinstance(value, str):
                continue
            if pd.isna(value):
                lines.append(f"- `{key}`: unavailable")
                continue
            lines.append(f"- `{key}`: {value}")
        lines.append("")
    lines.extend(
        [
            "## Automated Checks",
            "",
            f"- Checks: {len(checks)}",
            f"- Passed: {(checks['status'] == 'PASS').sum()}",
            f"- Failed: {(checks['status'] != 'PASS').sum()}",
            "",
            "Every Zoho widget must reconcile to the matching outlet-month row in "
            "`exports/control_tower_zoho/truth/` before publication.",
        ]
    )
    with DOC.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines) + "\n")


def build() -> dict[str, int]:
    if TRUTH.exists():
        shutil.rmtree(TRUTH)
    TRUTH.mkdir(parents=True)

    recipe, recipe_unit_cost = _recipe_model()
    po, vendor_performance = _purchase_model()
    risk, menu_impact, forecast = _inventory_risk_model(recipe, po)
    variance, menu_profit, sales = _consumption_model(recipe_unit_cost)

    closing = _numbers(
        _read_landing("closing_stock"),
        ["total_qty", "average_price", "total_amt"],
    ).rename(
        columns={
            "source_outlet_code": "outlet_code",
            "source_outlet_name": "outlet_name",
            "total_qty": "current_stock_qty",
            "average_price": "average_unit_cost",
            "total_amt": "closing_value",
            "unit_name": "canonical_uom",
        }
    )
    wastage = _numbers(
        _read_landing("enterprise_wastage_normal"),
        ["wastage_amt"],
    ).rename(
        columns={
            "source_outlet_code": "outlet_code",
            "source_outlet_name": "outlet_name",
            "wastage_amt": "wastage_value",
        }
    )
    item_master = closing[
        ["item_code", "item_name", "canonical_uom"]
    ].drop_duplicates("item_code")
    operational_items = _operational_items(closing, po)
    expiry_detail = _numbers(
        _read_aux("AUX_Expiry_Estimate"),
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
    )

    page_1 = _page_1(risk, menu_impact, forecast, po, expiry_detail)
    page_2 = _page_2(po, vendor_performance, closing, wastage)
    page_3 = _page_3(variance, menu_profit)
    page_4, dq = _page_4(
        page_2,
        page_3,
        risk,
        sales,
        recipe,
        po,
        operational_items,
        item_master,
    )

    outputs = {
        "PAGE1_Risk_Action_Truth": page_1,
        "PAGE2_Procurement_Vendor_Truth": page_2,
        "PAGE3_Consumption_Profitability_Truth": page_3,
        "PAGE4_Explorer_Data_Quality_Truth": page_4,
        "PAGE1_Inventory_Risk_Detail": _round_output(
            _query_27_projection(risk)
        ),
        "PAGE1_Expiry_Risk_Detail": _round_output(expiry_detail),
        "PAGE1_Menu_Impact_Detail": _round_output(menu_impact),
        "PAGE2_Vendor_Performance_Detail": _round_output(vendor_performance),
        "PAGE3_Ingredient_Variance_Detail": _round_output(variance),
        "PAGE3_Menu_Profitability_Detail": _round_output(menu_profit),
        "PAGE4_Data_Quality_Truth": dq,
    }
    for name, frame in outputs.items():
        frame.to_csv(
            TRUTH / f"{name}.csv",
            index=False,
            encoding="utf-8-sig",
            lineterminator="\n",
        )

    checks = _acceptance_checks(page_1, page_4)
    checks.to_csv(
        TRUTH / "CONTROL_TOWER_ACCEPTANCE_CHECKS.csv",
        index=False,
        encoding="utf-8-sig",
        lineterminator="\n",
    )
    _write_reference(
        {
            "page_1": page_1,
            "page_2": page_2,
            "page_3": page_3,
            "page_4": page_4,
        },
        checks,
    )
    failed = checks[checks["status"] != "PASS"]
    if not failed.empty:
        raise RuntimeError(
            "Truth-pack acceptance checks failed: "
            + ", ".join(failed["check_id"].tolist())
        )
    return {
        "truth_files": len(outputs) + 1,
        "acceptance_checks": len(checks),
        "risk_detail_rows": len(risk),
        "menu_impact_rows": len(menu_impact),
        "vendor_performance_rows": len(vendor_performance),
        "ingredient_variance_rows": len(variance),
        "menu_profitability_rows": len(menu_profit),
    }


if __name__ == "__main__":
    result = build()
    print(result)
