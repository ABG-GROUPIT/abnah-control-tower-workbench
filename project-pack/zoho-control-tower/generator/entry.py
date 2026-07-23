from __future__ import annotations

from datetime import date, timedelta

import pandas as pd

from generator.config import clean_money, rng_for


USERS = ["ops.cp", "ops.hk", "ops.saket", "store.manager", "inventory.lead"]


def build_entry_report(purchase_df: pd.DataFrame) -> pd.DataFrame:
    rng = rng_for("entry")
    rows = []
    usable = purchase_df[purchase_df["total_processed_qty"] > 0].copy()
    for idx, row in usable.reset_index(drop=True).iterrows():
        po_date = pd.to_datetime(row["po_date"]).date()
        receipt_date = po_date + timedelta(days=int(rng.integers(1, 4)))
        receipt_date = min(receipt_date, date(2026, 3, 31))
        qty = float(row["total_processed_qty"])
        unit_price = clean_money(float(row["unit_price"]) * rng.uniform(0.985, 1.02))
        amount = clean_money(qty * unit_price)
        discount = clean_money(amount * rng.choice([0, 0, 0, 0.01, 0.015]))
        gst_rate = 18 if row["category_name"] in {"Packaging", "Syrups & Sauces", "Dessert Inputs", "Fruit Inputs"} else 5
        if row["item_name"] == "Butter":
            gst_rate = 12
        taxable = max(amount - discount, 0)
        gst_value = clean_money(taxable * gst_rate / 100)
        item_charges = clean_money(rng.choice([0, 0, 0, 12, 18, 25]))
        return_qty = 0.0
        if rng.random() < 0.035:
            return_qty = round(max(1, qty * rng.uniform(0.02, 0.08)), 2)
        return_amount = clean_money(return_qty * unit_price)
        grand_total = clean_money(taxable + gst_value + item_charges - return_amount)
        rows.append(
            {
                "row_id": f"ENT_{receipt_date:%Y%m%d}_{idx + 1:05d}",
                "deployment_name": row["deployment"],
                "store_kitchen_name": row["store_name"],
                "user_name": str(rng.choice(USERS)),
                "vendor_name": row["vendor_name"],
                "date": receipt_date.isoformat(),
                "transaction_number": f"GRN-{receipt_date:%Y%m%d}-{idx + 1:05d}",
                "invoice_number": f"INV-{pd.to_datetime(row['po_date']).strftime('%y%m%d')}-{idx + 1:05d}",
                "invoice_date": receipt_date.isoformat(),
                "item_code": row["item_code"],
                "item_name": row["item_name"],
                "category_name": row["category_name"],
                "super_category_name": row["super_category_name"],
                "quantity": qty,
                "unit": row["unit"],
                "mrp": clean_money(unit_price * rng.uniform(1.08, 1.18)),
                "unit_price": unit_price,
                "amount": amount,
                "discount": discount,
                "gst_igst_rate": gst_rate,
                "gst_igst_value": gst_value,
                "total_tax": gst_value,
                "item_charges_amount": item_charges,
                "entry_total": clean_money(taxable + gst_value + item_charges),
                "return_quantity": return_qty,
                "return_amount": return_amount,
                "grand_total": grand_total,
            }
        )
    return pd.DataFrame(rows)
