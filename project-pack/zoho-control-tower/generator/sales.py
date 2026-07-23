from __future__ import annotations

from datetime import date

import pandas as pd

from generator.config import MONTHS, clean_money, month_code_for_date, month_date_ranges, rng_for
from generator.outlets import OUTLETS


CATEGORY_BASE_DEMAND = {
    "Espresso": 0.28,
    "Coffee Classics": 1.85,
    "Signature Coffee": 0.95,
    "Cold Brew": 0.72,
    "Cold Coffee": 1.15,
    "Tea": 0.8,
    "Iced Tea": 0.7,
    "Kids Beverage": 0.28,
    "Shake": 0.55,
    "Smoothie": 0.45,
    "Wraps": 0.75,
    "Sandwiches": 0.78,
    "Toasts": 0.42,
    "Platter": 0.22,
    "Breakfast": 0.55,
    "Snacks": 0.48,
    "Baked Goods": 0.7,
    "Desserts": 0.72,
}

GLOBAL_DEMAND_SCALE = 0.68


OUTLET_CATEGORY_MULTIPLIER = {
    "ABNAH Cafe Connaught Place": {
        "Coffee Classics": 1.35,
        "Signature Coffee": 1.1,
        "Tea": 1.2,
        "Sandwiches": 1.35,
        "Breakfast": 1.25,
        "Cold Coffee": 0.85,
        "Desserts": 0.85,
    },
    "ABNAH Cafe Hauz Khas": {
        "Cold Coffee": 1.55,
        "Iced Tea": 1.35,
        "Wraps": 1.35,
        "Snacks": 1.25,
        "Desserts": 1.25,
        "Signature Coffee": 0.82,
        "Shake": 1.15,
    },
    "ABNAH Cafe Saket Premium": {
        "Signature Coffee": 1.35,
        "Shake": 1.4,
        "Smoothie": 1.3,
        "Desserts": 1.55,
        "Baked Goods": 1.35,
        "Cold Brew": 1.15,
        "Sandwiches": 0.9,
    },
}


def _weekday_multiplier(outlet_name: str, day: date) -> float:
    weekday = day.weekday()
    if outlet_name == "ABNAH Cafe Connaught Place":
        if weekday < 5:
            return 1.22
        return 0.82 if weekday == 5 else 0.58
    if outlet_name == "ABNAH Cafe Hauz Khas":
        if weekday in {4, 5}:
            return 1.28
        if weekday == 6:
            return 1.15
        return 0.98
    if weekday in {5, 6}:
        return 1.45
    if weekday == 4:
        return 1.12
    return 0.9


def _holiday_multiplier(outlet_name: str, category: str, day: date, holidays_df: pd.DataFrame) -> float:
    hits = holidays_df[holidays_df["calendar_date"] == day.isoformat()]
    if hits.empty:
        return 1.0
    name = " ".join(hits["holiday_name"].astype(str)).lower()
    if outlet_name == "ABNAH Cafe Connaught Place":
        mult = 0.72 if bool(hits["is_public_holiday"].any()) else 0.92
    elif outlet_name == "ABNAH Cafe Saket Premium":
        mult = 1.28 if bool(hits["is_public_holiday"].any()) else 1.12
    else:
        mult = 1.08 if bool(hits["is_public_holiday"].any()) else 1.05

    if "valentine" in name and category in {"Desserts", "Cold Coffee", "Shake", "Baked Goods"}:
        mult *= 1.22
    if "holi" in name and category in {"Cold Coffee", "Iced Tea", "Shake", "Smoothie", "Desserts"}:
        mult *= 1.18
    return mult


def _event_multiplier(outlet_name: str, category: str, item_name: str, day: date, events_df: pd.DataFrame) -> float:
    active = events_df[(pd.to_datetime(events_df["start_date"]).dt.date <= day) & (pd.to_datetime(events_df["end_date"]).dt.date >= day)]
    mult = 1.0
    for _, event in active.iterrows():
        outlets = str(event["affected_outlets"])
        categories = str(event["affected_category"])
        items = str(event["affected_items"])
        outlet_match = "All outlets" in str(event["outlet_scope"]) or outlet_name in outlets
        category_match = "All" in categories or category in categories
        item_match = item_name in items
        if outlet_match and (category_match or item_match):
            pct = float(event["expected_impact_pct"]) / 100.0
            if str(event["impact_direction"]).lower() == "mixed" and outlet_name == "ABNAH Cafe Connaught Place":
                mult *= max(0.78, 1 - pct)
            else:
                mult *= 1 + pct
    return mult


def _item_popularity(item_name: str, category: str, rate: float, outlet_name: str) -> float:
    name = item_name.lower()
    mult = 1.0
    if "regular" in name:
        mult *= 1.1
    if "medium" in name:
        mult *= 1.02
    if "large" in name:
        mult *= 0.66
    for token in ["latte", "cappuccino", "americano", "classic cold coffee", "brownie", "croissant", "wrap", "sandwich"]:
        if token in name:
            mult *= 1.16
    if rate > 310 and outlet_name == "ABNAH Cafe Hauz Khas":
        mult *= 0.78
    if rate > 285 and outlet_name == "ABNAH Cafe Saket Premium":
        mult *= 1.12
    if category in {"Espresso", "Platter", "Kids Beverage"}:
        mult *= 0.72
    return mult


def build_sales_report(menu_df: pd.DataFrame, holidays_df: pd.DataFrame, events_df: pd.DataFrame) -> pd.DataFrame:
    rng = rng_for("sales")
    all_days = [day for days in month_date_ranges().values() for day in days]
    month_mult = {"month_01": 1.0, "month_02": 1.07, "month_03": 1.11}
    rows = []

    for day in all_days:
        month_code = month_code_for_date(day)
        for outlet in OUTLETS:
            outlet_name = outlet["outlet_name"]
            for _, item in menu_df.iterrows():
                category = item["category_name"]
                base = CATEGORY_BASE_DEMAND.get(category, 0.4)
                lam = base
                lam *= OUTLET_CATEGORY_MULTIPLIER.get(outlet_name, {}).get(category, 1.0)
                lam *= _weekday_multiplier(outlet_name, day)
                lam *= _holiday_multiplier(outlet_name, category, day, holidays_df)
                lam *= _event_multiplier(outlet_name, category, item["item_name"], day, events_df)
                lam *= _item_popularity(item["item_name"], category, float(item["rate"]), outlet_name)
                lam *= month_mult[month_code]
                lam *= GLOBAL_DEMAND_SCALE
                lam *= rng.uniform(0.78, 1.24)
                qty = int(rng.poisson(max(lam, 0.03)))
                if qty <= 0:
                    continue
                sale_factor = rng.uniform(0.94, 1.02)
                net_sale = clean_money(qty * float(item["rate"]) * sale_factor)
                rows.append(
                    {
                        "row_id": f"SALE_{day:%Y%m%d}_{outlet['outlet_code']}_{item['item_number']}",
                        "outlet_name": outlet_name,
                        "date": day.isoformat(),
                        "super_category": item["super_category_name"],
                        "category": category,
                        "item_number": item["item_number"],
                        "item_name": item["item_name"],
                        "qty": qty,
                        "net_sale": net_sale,
                    }
                )

    sales = pd.DataFrame(rows)
    for month_code, (start, end) in MONTHS.items():
        mask = (pd.to_datetime(sales["date"]).dt.date >= start) & (pd.to_datetime(sales["date"]).dt.date <= end)
        if sales.loc[mask].empty:
            raise RuntimeError(f"No sales generated for {month_code}")
    return sales
