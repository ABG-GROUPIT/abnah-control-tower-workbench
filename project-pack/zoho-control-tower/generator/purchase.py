from __future__ import annotations

from datetime import timedelta

import pandas as pd

from generator.config import MONTHS, clean_money, rng_for
from generator.outlets import OUTLETS


STATUS_PROBS = ["Closed", "Closed", "Closed", "Partially Received", "Pending", "Cancelled"]


def _procurement_lift(day, outlet_name: str, item_name: str, events_df: pd.DataFrame) -> float:
    window_start = day
    window_end = day + timedelta(days=4)
    active = events_df[(pd.to_datetime(events_df["start_date"]).dt.date >= window_start) & (pd.to_datetime(events_df["start_date"]).dt.date <= window_end)]
    lift = 1.0
    for _, event in active.iterrows():
        if outlet_name in str(event["affected_outlets"]) and any(token in str(event["affected_items"]) for token in [item_name, "Coffee", "Wrap", "Dessert"]):
            lift *= 1.18
    return lift


def build_purchase_report(ingredients_df: pd.DataFrame, events_df: pd.DataFrame) -> pd.DataFrame:
    rng = rng_for("purchase")
    rows = []
    weighted_items = ingredients_df.copy()
    weighted_items["weight"] = weighted_items["category_name"].map(
        {
            "Coffee Inputs": 9,
            "Dairy": 10,
            "Dairy Alternative": 4,
            "Bakery": 8,
            "Packaging": 10,
            "Produce": 6,
            "Protein": 6,
            "Dessert Inputs": 6,
            "Syrups & Sauces": 5,
            "Tea Inputs": 4,
            "Beverage Inputs": 5,
            "Fruit Inputs": 4,
        }
    ).fillna(3)
    probs = weighted_items["weight"] / weighted_items["weight"].sum()

    po_seq = 1
    for month_code, (start, end) in MONTHS.items():
        for day in pd.date_range(start=start, end=end, freq="3D"):
            day_date = day.date()
            for outlet in OUTLETS:
                item_count = int(rng.integers(5, 9))
                chosen = weighted_items.sample(n=item_count, replace=False, weights=probs, random_state=int(rng.integers(1, 10_000)))
                po_number = f"PO-{day_date:%Y%m%d}-{outlet['outlet_code']}-{po_seq:04d}"
                po_seq += 1
                for _, ingredient in chosen.iterrows():
                    status = str(rng.choice(STATUS_PROBS, p=[0.45, 0.2, 0.1, 0.17, 0.06, 0.02]))
                    lift = _procurement_lift(day_date, outlet["outlet_name"], ingredient["item_name"], events_df)
                    base_qty = float(ingredient["standard_order_qty"]) * rng.uniform(0.55, 1.35) * lift
                    if ingredient["unit"] == "pcs":
                        quantity = round(base_qty / 5) * 5
                    else:
                        quantity = round(base_qty, 2)
                    unit_price = clean_money(float(ingredient["average_price"]) * rng.uniform(0.96, 1.06))
                    subtotal = clean_money(quantity * unit_price)
                    tax = clean_money(subtotal * float(ingredient["gst_rate"]) / 100.0)
                    total_cost = clean_money(subtotal + tax)
                    if status == "Closed":
                        processed = quantity
                        remaining = 0
                    elif status == "Partially Received":
                        processed = round(quantity * rng.uniform(0.45, 0.82), 2)
                        remaining = round(quantity - processed, 2)
                    elif status == "Pending":
                        processed = 0
                        remaining = quantity
                    else:
                        processed = 0
                        remaining = 0

                    rows.append(
                        {
                            "row_id": f"PUR_{day_date:%Y%m%d}_{outlet['outlet_code']}_{ingredient['item_code']}_{po_seq:04d}",
                            "deployment": outlet["outlet_name"],
                            "store_name": "Main Store",
                            "vendor_name": ingredient["primary_vendor"],
                            "po_number": po_number,
                            "po_date": day_date.isoformat(),
                            "expected_delivery": (day_date + timedelta(days=int(rng.integers(1, 4)))).isoformat(),
                            "po_status": status,
                            "item_code": ingredient["item_code"],
                            "item_name": ingredient["item_name"],
                            "category_name": ingredient["category_name"],
                            "super_category_name": ingredient["super_category_name"],
                            "total_processed_qty": processed,
                            "remaining_balance_qty": remaining,
                            "quantity": quantity,
                            "unit": ingredient["unit"],
                            "unit_price": unit_price,
                            "subtotal": subtotal,
                            "tax": tax,
                            "total_item_cost": total_cost,
                        }
                    )
    return pd.DataFrame(rows)

