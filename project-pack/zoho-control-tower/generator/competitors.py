from __future__ import annotations

import pandas as pd

from generator.config import clean_money, rng_for


COMPETITORS_BY_AREA = {
    "Connaught Place": ["Blue Tokai CP", "Starbucks CP", "Chaayos CP", "Local Brew Bar CP"],
    "Hauz Khas": ["Blue Tokai HKV", "Third Wave Hauz Khas", "Social Coffee HK", "Campus Brew House"],
    "Saket": ["Starbucks Select Citywalk", "Coffee Bean Saket", "Third Wave Saket", "Artisan Dessert Cafe Saket"],
}


FOCUS_CATEGORIES = {
    "Coffee Classics",
    "Signature Coffee",
    "Cold Brew",
    "Cold Coffee",
    "Iced Tea",
    "Shake",
    "Smoothie",
    "Wraps",
    "Sandwiches",
    "Baked Goods",
    "Desserts",
}


def _price_position(index: float) -> str:
    if index <= 0.95:
        return "Below competitor"
    if index <= 1.05:
        return "At parity"
    return "Premium vs competitor"


def _impact(position: str, area: str) -> str:
    if position == "Below competitor":
        return "Likely supportive context for sales performance"
    if position == "At parity":
        return "Neutral competitive context"
    if area == "Hauz Khas":
        return "Potential pressure for price-sensitive student demand"
    if area == "Saket":
        return "Premium may still work due to mall/leisure positioning"
    return "Potential pressure unless corporate convenience offsets premium"


def build_competitor_pricing(menu_df: pd.DataFrame) -> pd.DataFrame:
    rng = rng_for("competitors")
    focus = menu_df[menu_df["category_name"].isin(FOCUS_CATEGORIES)].copy()
    focus["rank_key"] = focus["item_name"].str.contains("Regular|Medium|Brownie|Cheesecake|Croissant|Wrap|Sandwich", regex=True)
    focus = focus.sort_values(["rank_key", "category_name", "item_name"], ascending=[False, True, True]).head(42)

    rows = []
    for area, competitors in COMPETITORS_BY_AREA.items():
        for _, item in focus.iterrows():
            competitor = str(rng.choice(competitors))
            if area == "Hauz Khas":
                factor = rng.uniform(0.82, 1.02)
            elif area == "Saket":
                factor = rng.uniform(0.94, 1.16)
            else:
                factor = rng.uniform(0.88, 1.1)
            competitor_price = max(120, round(float(item["rate"]) * factor / 5) * 5)
            price_difference = clean_money(float(item["rate"]) - competitor_price)
            price_index = round(float(item["rate"]) / competitor_price, 3)
            position = _price_position(price_index)
            rows.append(
                {
                    "competitor_id": f"COMP{len(rows) + 1:04d}",
                    "competitor_name": competitor,
                    "market_area": area,
                    "competitor_category": item["category_name"],
                    "competitor_item_name": item["item_name"].replace("ABNAH", "").replace(" - ", " "),
                    "competitor_price": clean_money(competitor_price),
                    "abnah_item_number": item["item_number"],
                    "abnah_item_name": item["item_name"],
                    "abnah_price": clean_money(item["rate"]),
                    "price_difference": price_difference,
                    "price_index": price_index,
                    "price_position": position,
                    "expected_sales_impact": _impact(position, area),
                    "notes": "Synthetic competitor context; do not interpret as causation.",
                }
            )
    return pd.DataFrame(rows)

