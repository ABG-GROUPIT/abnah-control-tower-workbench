from __future__ import annotations

from datetime import date
import re

import pandas as pd

from generator.config import rng_for


ACTIVE_VENDOR_NAMES = [
    "BeanCraft Roasters Delhi",
    "FreshDairy Foods NCR",
    "Delhi Bakery Supply Co",
    "PackPro Disposables",
    "GreenLeaf Produce Delhi",
    "SpiceRoot Foods",
    "NorthStar Poultry",
    "ChocoCraft Ingredients",
    "FrozenBerry Traders",
    "Metro Wholesale Delhi",
    "TeaLeaf Traders NCR",
    "SweetBase Foods",
]

ACTIVE_VENDOR_DESCRIPTIONS = {
    "BeanCraft Roasters Delhi": "coffee beans",
    "FreshDairy Foods NCR": "milk, cream, paneer, cheese",
    "Delhi Bakery Supply Co": "bread, croissants, cake bases",
    "PackPro Disposables": "cups, lids, straws, boxes",
    "GreenLeaf Produce Delhi": "vegetables, fruits, lettuce",
    "SpiceRoot Foods": "sauces, spices, chutneys",
    "NorthStar Poultry": "chicken, eggs",
    "ChocoCraft Ingredients": "chocolate sauce, cocoa, dessert inputs",
    "FrozenBerry Traders": "berry pulp, smoothie inputs",
    "Metro Wholesale Delhi": "fallback/general vendor",
    "TeaLeaf Traders NCR": "tea, matcha, chai inputs",
    "SweetBase Foods": "sugar, syrups, cream inputs",
}


def _tax_id(prefix: str, idx: int) -> str:
    return f"{prefix}{idx:04d}{chr(65 + (idx % 20))}{chr(65 + ((idx + 7) % 20))}"


def _contact_name(idx: int) -> str:
    first_names = ["Aarav", "Meera", "Kabir", "Riya", "Ishaan", "Anaya", "Arjun", "Diya"]
    last_names = ["Sharma", "Verma", "Kapoor", "Mehta", "Gupta", "Nair", "Singh", "Iyer"]
    return f"{first_names[(idx - 1) % len(first_names)]} {last_names[(idx * 3) % len(last_names)]}"


def _email_for(name: str, idx: int) -> str:
    slug = re.sub(r"[^a-z0-9]+", ".", name.lower()).strip(".")
    return f"accounts.{idx:03d}@{slug}.example"


def build_vendor_report() -> pd.DataFrame:
    rng = rng_for("vendor_master")
    filler_names = [
        "Urban Farm Collective",
        "Capital Kitchen Services",
        "NCR Beverage Inputs",
        "Prime Tableware Traders",
        "Saffron Route Foods",
        "Apex Cold Chain",
        "Lotus Paper Products",
        "Heritage Spice Market",
        "Civic Facility Supplies",
        "North Ridge Dairy",
        "Blue Mountain Staples",
        "Indus Hospitality Supply",
        "Ridgeway Fruit Co",
        "Delhi Fresh Mills",
        "Market Yard Essentials",
        "Central Packaging Hub",
        "Cafe Equipment Care",
        "Patel Nagar Provisions",
        "South Delhi Organics",
        "Nexus Dessert Inputs",
        "Aravali Grain Traders",
        "Citywide Cleaning Supply",
        "Dilli Gourmet Foods",
        "Select Bakery Partners",
        "Monsoon Beverage Co",
        "Kitchen Line Services",
        "NCR Cold Storage",
        "Urban Harvest Foods",
        "Daily Fresh Produce Co",
        "Capital Dairy Alternatives",
        "Delhi Gourmet Sauces",
        "Pioneer Hospitality Goods",
        "Karol Bagh Dry Fruits",
        "Old Delhi Spice Works",
        "Crescent Food Services",
        "Elite Disposable Traders",
        "Saket Bakery Inputs",
        "Hauz Khas Fresh Mart",
        "CP Office Pantry Supply",
        "Rohini Frozen Foods",
        "Noida Beverage Base",
        "Gurgaon Premium Dairy",
        "Faridabad Food Logistics",
        "Azadpur Fresh Fruits",
        "Lajpat Wholesale Supply",
        "Okhla Culinary Inputs",
        "Rajouri Gourmet Pantry",
        "Mayapuri Kitchen Goods",
        "Yamuna Fresh Farms",
        "Connaught Cafe Care",
        "South City Sweeteners",
        "Vasant Vihar Hospitality",
        "Dwarka Provisions",
        "Greater Kailash Supplies",
        "Defence Colony Bakers",
        "Janakpuri Pantry Hub",
        "Model Town Essentials",
        "Nehru Place Food Mart",
    ]
    names = ACTIVE_VENDOR_NAMES + filler_names
    rows = []
    for idx, name in enumerate(names[:70], start=1):
        optional_blank = rng.random(6) < [0.25, 0.4, 0.22, 0.2, 0.35, 0.12]
        state = rng.choice(["Delhi", "Haryana", "Uttar Pradesh"])
        rows.append(
            {
                "vendor_name": name,
                "vendor_code": f"VEND{idx:03d}",
                "description": ACTIVE_VENDOR_DESCRIPTIONS.get(name, "" if rng.random() < 0.35 else "synthetic inactive/demo vendor"),
                "contact_person": _contact_name(idx),
                "contact_number": f"98{idx:08d}"[-10:],
                "email": _email_for(name, idx),
                "tin_number": "" if optional_blank[0] else _tax_id("TIN", idx),
                "service_tax_number": "" if optional_blank[1] else _tax_id("ST", idx),
                "gstin_number": "" if optional_blank[2] else f"07ABCDE{idx:04d}F1Z{idx % 9}",
                "msme": "" if optional_blank[3] else rng.choice(["Micro", "Small", "Medium"]),
                "fssai_number": "" if optional_blank[4] else f"FSSAI{11000000000000 + idx}",
                "pan_number": "" if optional_blank[5] else f"ABCDE{1000 + idx}F",
                "from_date": date(2024, int(rng.integers(1, 12)), int(rng.integers(1, 25))).isoformat(),
                "to_date": "",
                "state": state,
                "address": f"{100 + idx}, Supply Market Road, Delhi NCR, {state}",
            }
        )
    return pd.DataFrame(rows)
