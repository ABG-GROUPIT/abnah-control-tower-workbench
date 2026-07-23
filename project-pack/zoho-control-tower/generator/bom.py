from __future__ import annotations

from collections import defaultdict

import pandas as pd


def _size_multiplier(item_name: str) -> float:
    if "Large" in item_name:
        return 1.3
    if "Medium" in item_name:
        return 1.15
    if "Doppio" in item_name:
        return 1.45
    if "Solo" in item_name:
        return 0.8
    return 1.0


def _is_cold(item_name: str, category: str) -> bool:
    cold_categories = {"Cold Brew", "Cold Coffee", "Iced Tea", "Shake", "Smoothie"}
    return category in cold_categories or "Iced" in item_name or "Shakerato" in item_name or "Lemonade" in item_name


def _add(recipe: dict[str, float], ingredient: str, qty: float) -> None:
    recipe[ingredient] += qty


def build_recipe_bom(menu_df: pd.DataFrame, ingredients_df: pd.DataFrame) -> pd.DataFrame:
    units = ingredients_df.set_index("item_name")["unit"].to_dict()
    rows = []

    for _, item in menu_df.iterrows():
        item_name = item["item_name"]
        lower = item_name.lower()
        category = item["category_name"]
        super_category = item["super_category_name"]
        mult = _size_multiplier(item_name)
        recipe: dict[str, float] = defaultdict(float)

        if super_category == "Beverage":
            if "espresso" in lower:
                _add(recipe, "Coffee Beans", 0.012 * mult)
            elif any(word in lower for word in ["americano", "cold brew", "coffee lemonade", "shakerato"]):
                _add(recipe, "Coffee Beans", 0.018 * mult)
            elif any(word in lower for word in ["latte", "cappuccino", "flat white", "mocha", "macchiato", "cold coffee"]):
                _add(recipe, "Coffee Beans", 0.018 * mult)
                _add(recipe, "Oat Milk" if "vegan" in lower else "Milk", 0.18 * mult)
            elif "chai" in lower:
                _add(recipe, "Tea Leaves", 0.006 * mult)
                _add(recipe, "Milk", 0.16 * mult)
            elif "green tea" in lower:
                _add(recipe, "Tea Leaves", 0.005)
            elif "matcha" in lower:
                _add(recipe, "Matcha Powder", 0.006 * mult)
                _add(recipe, "Milk", 0.16 * mult)
            elif "iced tea" in lower:
                _add(recipe, "Tea Leaves", 0.004 * mult)
            elif "hot chocolate" in lower or "chocolate milk" in lower:
                _add(recipe, "Milk", 0.2 * mult)
                _add(recipe, "Chocolate Sauce", 0.035 * mult)
            elif "babyccino" in lower:
                _add(recipe, "Milk", 0.12)
            elif "shake" in lower or "smoothie" in lower:
                _add(recipe, "Milk", 0.2 * mult)
                _add(recipe, "Cream", 0.025 * mult)

            if "mocha" in lower or "choco" in lower or "chocolate" in lower:
                _add(recipe, "Chocolate Sauce", 0.025 * mult)
            if "caramel" in lower:
                _add(recipe, "Caramel Syrup", 0.025 * mult)
            if "vanilla" in lower:
                _add(recipe, "Vanilla Syrup", 0.025 * mult)
            if "lemon" in lower:
                _add(recipe, "Lemon", 0.035 * mult)
            if "hibiscus" in lower:
                _add(recipe, "Hibiscus Concentrate", 0.035 * mult)
            if "berry" in lower:
                _add(recipe, "Mixed Berry Pulp", 0.08 * mult)
            if "smoothie" in lower:
                _add(recipe, "Banana", 0.08 * mult)
            if "cold" in lower or "iced" in lower or category in {"Cold Brew", "Cold Coffee", "Iced Tea", "Shake", "Smoothie"}:
                _add(recipe, "Ice", 0.12 * mult)
            if "shot" not in lower:
                _add(recipe, "Sugar Syrup", 0.015 * mult)

            if _is_cold(item_name, category):
                _add(recipe, "Cold Cup", 1)
                _add(recipe, "Lid", 1)
                _add(recipe, "Straw", 1)
            else:
                _add(recipe, "Hot Cup", 1)
                _add(recipe, "Lid", 1)
            _add(recipe, "Napkin", 1)

        elif super_category == "Food":
            if "wrap" in lower:
                _add(recipe, "Tortilla", 1)
                _add(recipe, "Paneer" if "paneer" in lower else "Chicken", 0.11)
                _add(recipe, "Lettuce", 0.025)
                _add(recipe, "Onion", 0.02)
                _add(recipe, "Capsicum", 0.025)
                _add(recipe, "Chipotle Sauce", 0.025)
                _add(recipe, "Wrap Packaging", 1)
            elif "sandwich" in lower:
                _add(recipe, "Bread", 2)
                _add(recipe, "Cheese", 0.03)
                _add(recipe, "Paneer" if "paneer" in lower or "veg" in lower else "Chicken", 0.1)
                _add(recipe, "Lettuce", 0.02)
                _add(recipe, "Tomato", 0.03)
                _add(recipe, "Pesto Sauce" if "pesto" in lower else "Chipotle Sauce", 0.02)
                _add(recipe, "Sandwich Box", 1)
            elif "toast" in lower:
                _add(recipe, "Bread", 1)
                _add(recipe, "Cheese", 0.035)
                if "chicken" in lower:
                    _add(recipe, "Chicken", 0.08)
                _add(recipe, "Aioli", 0.02)
                _add(recipe, "Sandwich Box", 1)
            elif "platter" in lower:
                _add(recipe, "Bread", 2)
                _add(recipe, "Lettuce", 0.03)
                _add(recipe, "Tomato", 0.04)
                _add(recipe, "Aioli", 0.03)
                _add(recipe, "Sandwich Box", 1)
            elif "pancakes" in lower:
                _add(recipe, "Cake Base", 1)
                _add(recipe, "Butter", 0.025)
                _add(recipe, "Sugar Syrup", 0.025)
                _add(recipe, "Dessert Box", 1)
            elif "bagel" in lower:
                _add(recipe, "Bagel", 1)
                _add(recipe, "Cream", 0.035)
                _add(recipe, "Cheese", 0.025)
                _add(recipe, "Sandwich Box", 1)
            elif "egg" in lower:
                _add(recipe, "Bread", 1)
                _add(recipe, "Egg", 2)
                _add(recipe, "Cheese", 0.02)
                _add(recipe, "Sandwich Box", 1)
            elif "pin wheel" in lower:
                _add(recipe, "Bread", 1)
                _add(recipe, "Cheese", 0.03)
                _add(recipe, "Pesto Sauce" if "pesto" in lower else "Salsa", 0.025)
                _add(recipe, "Sandwich Box", 1)
            elif "turnover" in lower:
                _add(recipe, "Croissant Base", 1)
                _add(recipe, "Chicken" if "chicken" in lower else "Paneer", 0.08)
                _add(recipe, "Cheese", 0.025)
                _add(recipe, "Sandwich Box", 1)
            elif "croissant" in lower:
                _add(recipe, "Croissant Base", 1)
                _add(recipe, "Butter", 0.02)
                if "chocolate" in lower:
                    _add(recipe, "Chocolate Sauce", 0.025)
                if "chicken" in lower:
                    _add(recipe, "Chicken", 0.07)
                if "cheese" in lower:
                    _add(recipe, "Cheese", 0.035)
                _add(recipe, "Dessert Box", 1)
            _add(recipe, "Napkin", 2)

        else:
            if "brownie" in lower:
                _add(recipe, "Brownie Base", 1)
                _add(recipe, "Chocolate Sauce", 0.02)
            elif "cheesecake" in lower:
                _add(recipe, "Cheesecake Base", 1)
                _add(recipe, "Cream", 0.025)
            elif "cake" in lower or "pie" in lower:
                _add(recipe, "Cake Base", 1)
                _add(recipe, "Cream", 0.025)
            elif "cookie" in lower:
                _add(recipe, "Cake Base", 0.55)
                _add(recipe, "Butter", 0.02)
            elif "cinnamon" in lower:
                _add(recipe, "Croissant Base", 1)
                _add(recipe, "Cream", 0.025)
            else:
                _add(recipe, "Cake Base", 1)
            if "banana" in lower:
                _add(recipe, "Banana", 0.07)
            if "chocolate" in lower:
                _add(recipe, "Chocolate Sauce", 0.025)
            if "caramel" in lower:
                _add(recipe, "Caramel Syrup", 0.02)
            _add(recipe, "Dessert Box", 1)
            _add(recipe, "Napkin", 1)

        first_row_for_recipe = True
        for ingredient, qty in sorted(recipe.items()):
            if ingredient not in units:
                continue
            rows.append(
                {
                    "row_id": f"BOM{len(rows) + 1:05d}",
                    "recipe_name": item_name if first_row_for_recipe else "",
                    "recipe_qty": 1 if first_row_for_recipe else "",
                    "recipe_unit": "Piece" if first_row_for_recipe else "",
                    "item_name": ingredient,
                    "item_qty": round(qty, 4),
                    "item_unit": units[ingredient],
                    "item_tab_type": "Base Recipe",
                }
            )
            first_row_for_recipe = False

    return pd.DataFrame(rows)
