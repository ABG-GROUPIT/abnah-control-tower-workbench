from __future__ import annotations

from collections import defaultdict

import pandas as pd

from generator.config import MONTHS, clean_money, clean_qty, rng_for
from generator.outlets import OUTLETS


INVENTORY_ITEM_NAMES = [
    "Coffee Beans",
    "Milk",
    "Oat Milk",
    "Cream",
    "Paneer",
    "Cheese",
    "Chicken",
    "Egg",
    "Bread",
    "Bagel",
    "Tortilla",
    "Croissant Base",
    "Brownie Base",
    "Cake Base",
    "Cheesecake Base",
    "Chocolate Sauce",
    "Caramel Syrup",
    "Vanilla Syrup",
    "Sugar Syrup",
    "Tea Leaves",
    "Matcha Powder",
    "Ice",
    "Lemon",
    "Hibiscus Concentrate",
    "Mixed Berry Pulp",
    "Banana",
    "Butter",
    "Lettuce",
    "Onion",
    "Capsicum",
    "Tomato",
    "Pesto Sauce",
    "Chipotle Sauce",
    "Aioli",
    "Cold Cup",
    "Hot Cup",
]


def _initial_stock(unit: str, category: str, standard_order_qty: float, rng) -> float:
    if unit == "pcs":
        return float(standard_order_qty) * rng.uniform(1.2, 2.4)
    if category == "Packaging":
        return float(standard_order_qty) * rng.uniform(1.3, 2.0)
    return float(standard_order_qty) * rng.uniform(0.8, 1.7)


def build_inventory_closing(
    sales_df: pd.DataFrame,
    bom_df: pd.DataFrame,
    entry_df: pd.DataFrame,
    ingredients_df: pd.DataFrame,
) -> pd.DataFrame:
    rng = rng_for("inventory")
    inventory_items = ingredients_df[ingredients_df["item_name"].isin(INVENTORY_ITEM_NAMES)].copy()
    ingredient_meta = inventory_items.set_index("item_name").to_dict(orient="index")

    sales_bom = sales_df.merge(bom_df, left_on="item_name", right_on="recipe_name", suffixes=("_sale", "_ingredient"))
    sales_bom["consumed_qty"] = sales_bom["qty"] * sales_bom["item_qty"]
    consumption = (
        sales_bom.groupby(["date", "outlet_name", "item_name_ingredient"], as_index=False)["consumed_qty"].sum()
    )
    consumption_key = {
        (row["date"], row["outlet_name"], row["item_name_ingredient"]): float(row["consumed_qty"])
        for _, row in consumption.iterrows()
    }

    receipts = entry_df.groupby(["date", "deployment_name", "item_name"], as_index=False)["quantity"].sum()
    receipt_key = {
        (row["date"], row["deployment_name"], row["item_name"]): float(row["quantity"])
        for _, row in receipts.iterrows()
    }

    all_days = [d.date() for d in pd.date_range(start=MONTHS["month_01"][0], end=MONTHS["month_03"][1], freq="D")]
    rows = []
    stock_state: dict[tuple[str, str], float] = {}

    for outlet in OUTLETS:
        outlet_name = outlet["outlet_name"]
        for _, ingredient in inventory_items.iterrows():
            key = (outlet_name, ingredient["item_name"])
            stock_state[key] = _initial_stock(
                ingredient["unit"],
                ingredient["category_name"],
                float(ingredient["standard_order_qty"]),
                rng,
            )

    category_codes: dict[str, str] = {}
    super_codes: dict[str, str] = {}

    for day in all_days:
        day_text = day.isoformat()
        for outlet in OUTLETS:
            outlet_name = outlet["outlet_name"]
            for _, ingredient in inventory_items.iterrows():
                item_name = ingredient["item_name"]
                key = (outlet_name, item_name)
                stock = stock_state[key]
                stock += receipt_key.get((day_text, outlet_name, item_name), 0.0)
                consumed = consumption_key.get((day_text, outlet_name, item_name), 0.0)
                stock -= consumed * rng.uniform(0.98, 1.07)

                threshold = float(ingredient["low_stock_threshold"])
                if stock < 0:
                    stock = rng.uniform(0.2, max(1.0, threshold * 0.18))
                if stock < threshold * 0.22 and rng.random() < 0.08:
                    stock += float(ingredient["standard_order_qty"]) * rng.uniform(0.2, 0.45)

                stock_state[key] = stock
                avg_price = clean_money(float(ingredient["average_price"]) * rng.uniform(0.97, 1.04))
                category_name = ingredient["category_name"]
                super_category_name = ingredient["super_category_name"]
                category_codes.setdefault(category_name, f"CAT{len(category_codes) + 1:03d}")
                super_codes.setdefault(super_category_name, f"SUP{len(super_codes) + 1:03d}")
                category_code = "" if rng.random() < 0.08 else category_codes[category_name]
                super_code = "" if rng.random() < 0.06 else super_codes[super_category_name]
                total_qty = clean_qty(stock)
                rows.append(
                    {
                        "row_id": f"INV_{day:%Y%m%d}_{outlet['outlet_code']}_{ingredient['item_code']}",
                        "deployment": outlet_name,
                        "date": day_text,
                        "generation_date": day_text,
                        "generation_time": "23:55:00",
                        "item_code": ingredient["item_code"],
                        "item_name": item_name,
                        "super_category_code": super_code,
                        "super_category_name": super_category_name,
                        "category_code": category_code,
                        "category_name": category_name,
                        "unit_name": ingredient["unit"],
                        "average_price": avg_price,
                        "store_stock_qty": total_qty,
                        "total_qty": total_qty,
                        "total_amt": clean_money(total_qty * avg_price),
                    }
                )

    return pd.DataFrame(rows)

