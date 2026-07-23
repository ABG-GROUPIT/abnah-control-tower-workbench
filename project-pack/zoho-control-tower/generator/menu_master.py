from __future__ import annotations

import pandas as pd

from generator.config import rng_for


def _variant_prices(base: int, step: int = 25) -> dict[str, int]:
    return {"Regular": base, "Medium": base + step, "Large": base + (step * 2)}


def build_menu_master() -> pd.DataFrame:
    rng = rng_for("menu_master")
    rows: list[dict] = []

    def add_item(name: str, category: str, super_category: str, rate: int, non_veg: int = 0, has_variant: int = 0) -> None:
        idx = len(rows) + 1
        item_number = f"MENU{idx:04d}"
        desc_missing = rng.random() < 0.18
        alias_missing = rng.random() < 0.22
        hsn_missing = rng.random() < 0.14
        rows.append(
            {
                "item_number": item_number,
                "item_name": name,
                "uid": f"ABNAH-{item_number}",
                "item_description": "" if desc_missing else f"Premium cafe preparation: {name}",
                "rate": rate,
                "category_name": category,
                "super_category_name": super_category,
                "non_veg": non_veg,
                "hsn_code": "" if hsn_missing else ("996331" if super_category in {"Beverage", "Food"} else "996333"),
                "aggregator_alias_name": "" if alias_missing else name.replace(" - ", " "),
                "aggregator_alias_description": "" if alias_missing else f"{name} available for cafe and delivery orders",
                "not_in_sweetshop": bool(super_category != "Dessert"),
                "has_variant": has_variant,
                "is_inclusive_item": False,
                "is_scannable_item": False,
                "do_not_print_sticker": False,
            }
        )

    def add_variants(base_name: str, category: str, super_category: str, prices: dict[str, int], non_veg: int = 0) -> None:
        for variant, rate in prices.items():
            add_item(f"{base_name} - {variant}", category, super_category, rate, non_veg=non_veg, has_variant=1)

    add_item("Espresso Shot - Solo", "Espresso", "Beverage", 145)
    add_item("Espresso Shot - Doppio", "Espresso", "Beverage", 185)
    add_variants("Americano", "Coffee Classics", "Beverage", _variant_prices(185, 25))
    add_variants("Latte", "Coffee Classics", "Beverage", _variant_prices(225, 25))
    add_variants("Cappuccino", "Coffee Classics", "Beverage", _variant_prices(225, 25))
    add_variants("Flat White", "Coffee Classics", "Beverage", _variant_prices(235, 25))
    add_variants("Mocha", "Coffee Classics", "Beverage", _variant_prices(245, 25))
    add_variants("Sea Salt Mocha", "Signature Coffee", "Beverage", _variant_prices(275, 30))
    add_variants("Orange Zest Mocha", "Signature Coffee", "Beverage", _variant_prices(270, 30))
    add_variants("Caramel Macchiato", "Signature Coffee", "Beverage", _variant_prices(265, 30))
    add_variants("French Vanilla Latte", "Signature Coffee", "Beverage", _variant_prices(265, 30))
    add_variants("Vegan Iced Latte", "Signature Coffee", "Beverage", _variant_prices(285, 25))
    add_variants("Classic Cold Brew", "Cold Brew", "Beverage", _variant_prices(225, 25))
    add_variants("Coffee Lemonade", "Cold Brew", "Beverage", _variant_prices(235, 25))
    add_variants("Vietnamese Shakerato", "Cold Brew", "Beverage", _variant_prices(255, 25))
    add_variants("Classic Cold Coffee", "Cold Coffee", "Beverage", _variant_prices(255, 35))
    add_variants("Mocha Cold Coffee", "Cold Coffee", "Beverage", _variant_prices(285, 35))
    add_variants("Caramel Cold Coffee", "Cold Coffee", "Beverage", _variant_prices(285, 35))
    add_variants("Masala Chai Latte", "Tea", "Beverage", _variant_prices(195, 25))
    add_item("Himalayan Green Tea", "Tea", "Beverage", 210)
    add_variants("Japanese Matcha Latte", "Tea", "Beverage", _variant_prices(265, 30))
    add_variants("Lemon Iced Tea", "Iced Tea", "Beverage", _variant_prices(205, 25))
    add_variants("Hibiscus Lime Iced Tea", "Iced Tea", "Beverage", _variant_prices(225, 25))
    add_variants("Hot Chocolate", "Kids Beverage", "Beverage", _variant_prices(220, 25))
    add_item("Babyccino - Regular", "Kids Beverage", "Beverage", 165, has_variant=1)
    add_variants("Choco Chip Shake", "Shake", "Beverage", _variant_prices(295, 35))
    add_variants("Mixed Berry Shake", "Shake", "Beverage", _variant_prices(315, 35))
    add_variants("Seasonal Smoothie", "Smoothie", "Beverage", _variant_prices(305, 35))

    add_item("Spicy Paneer Wrap", "Wraps", "Food", 275)
    add_item("Shredded Chicken Wrap", "Wraps", "Food", 295, non_veg=1)
    add_item("Smoked Chipotle Paneer Sandwich", "Sandwiches", "Food", 295)
    add_item("Pesto Veg Sandwich", "Sandwiches", "Food", 280)
    add_item("Pepper Chicken Sandwich", "Sandwiches", "Food", 315, non_veg=1)
    add_item("Tandoori Chicken Sandwich", "Sandwiches", "Food", 320, non_veg=1)
    add_item("Chilli Cheese Garlic Toast", "Toasts", "Food", 235)
    add_item("Chicken Pepperoni Avocado Toast", "Toasts", "Food", 330, non_veg=1)
    add_item("Hummus and Pita Platter", "Platter", "Food", 310)
    add_item("Breakfast Pancakes", "Breakfast", "Food", 285)
    add_item("Cream Cheese Bagel", "Breakfast", "Food", 250)
    add_item("Scallion Pepper Cream Cheese Bagel", "Breakfast", "Food", 265)
    add_item("Masala Egg Bun", "Breakfast", "Food", 225, non_veg=1)
    add_item("Marinara Cheese Pin Wheels", "Snacks", "Food", 215)
    add_item("Pesto Sundried Tomato Pin Wheel", "Snacks", "Food", 225)
    add_item("Turnover with Brioche Dough Chicken", "Snacks", "Food", 255, non_veg=1)
    add_item("Turnover with Brioche Dough Veg", "Snacks", "Food", 235)
    add_item("Butter Croissant", "Baked Goods", "Food", 195)
    add_item("Almond Croissant", "Baked Goods", "Food", 245)
    add_item("Chocolate Croissant", "Baked Goods", "Food", 235)
    add_item("Mushroom Cheese Croissant", "Baked Goods", "Food", 255)
    add_item("Sriracha Chicken Croissant", "Baked Goods", "Food", 275, non_veg=1)
    add_item("Cinnamon Roll with Cream Cheese", "Baked Goods", "Dessert", 220)
    add_item("Banana Walnut Tea Cake", "Baked Goods", "Dessert", 205)
    add_item("Lemon Raspberry Tea Cake", "Baked Goods", "Dessert", 215)
    add_item("Double Chocolate Truffle Cake", "Desserts", "Dessert", 295)
    add_item("Banoffee Pie", "Desserts", "Dessert", 285)
    add_item("Classic Chocolate Fudge Brownie", "Desserts", "Dessert", 195)
    add_item("Soft-Centred Caramel Cookie", "Desserts", "Dessert", 180)
    add_item("Death by Chocolate Cookie", "Desserts", "Dessert", 190)
    add_item("Jaggery Parmesan Cookie", "Desserts", "Dessert", 170)
    add_item("Apple Pie", "Desserts", "Dessert", 270)
    add_item("Basque Cheesecake", "Desserts", "Dessert", 310)
    add_item("Multigrain Walnut Tea Cake", "Baked Goods", "Dessert", 225)

    return pd.DataFrame(rows)
