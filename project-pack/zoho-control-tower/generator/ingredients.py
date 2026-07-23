from __future__ import annotations

import pandas as pd


INGREDIENT_ROWS = [
    ("ING001", "Coffee Beans", "Coffee Inputs", "Raw Material", "kg", 980.0, "BeanCraft Roasters Delhi", "Metro Wholesale Delhi", 5, 8, 12),
    ("ING002", "Milk", "Dairy", "Raw Material", "litre", 72.0, "FreshDairy Foods NCR", "Metro Wholesale Delhi", 5, 60, 120),
    ("ING003", "Oat Milk", "Dairy Alternative", "Raw Material", "litre", 185.0, "FreshDairy Foods NCR", "Metro Wholesale Delhi", 5, 14, 36),
    ("ING004", "Cream", "Dairy", "Raw Material", "litre", 210.0, "FreshDairy Foods NCR", "SweetBase Foods", 5, 10, 30),
    ("ING005", "Paneer", "Dairy", "Raw Material", "kg", 360.0, "FreshDairy Foods NCR", "Metro Wholesale Delhi", 5, 12, 35),
    ("ING006", "Cheese", "Dairy", "Raw Material", "kg", 480.0, "FreshDairy Foods NCR", "Metro Wholesale Delhi", 5, 10, 25),
    ("ING007", "Chicken", "Protein", "Raw Material", "kg", 330.0, "NorthStar Poultry", "Metro Wholesale Delhi", 5, 14, 45),
    ("ING008", "Egg", "Protein", "Raw Material", "pcs", 7.0, "NorthStar Poultry", "Metro Wholesale Delhi", 5, 120, 400),
    ("ING009", "Bread", "Bakery", "Raw Material", "pcs", 12.0, "Delhi Bakery Supply Co", "Metro Wholesale Delhi", 5, 150, 450),
    ("ING010", "Bagel", "Bakery", "Raw Material", "pcs", 28.0, "Delhi Bakery Supply Co", "Metro Wholesale Delhi", 5, 60, 180),
    ("ING011", "Tortilla", "Bakery", "Raw Material", "pcs", 15.0, "Delhi Bakery Supply Co", "Metro Wholesale Delhi", 5, 100, 300),
    ("ING012", "Croissant Base", "Bakery", "Raw Material", "pcs", 42.0, "Delhi Bakery Supply Co", "Metro Wholesale Delhi", 5, 65, 200),
    ("ING013", "Brownie Base", "Dessert Inputs", "Raw Material", "pcs", 34.0, "ChocoCraft Ingredients", "Delhi Bakery Supply Co", 18, 70, 220),
    ("ING014", "Cake Base", "Dessert Inputs", "Raw Material", "pcs", 46.0, "Delhi Bakery Supply Co", "ChocoCraft Ingredients", 18, 50, 160),
    ("ING015", "Cheesecake Base", "Dessert Inputs", "Raw Material", "pcs", 72.0, "Delhi Bakery Supply Co", "SweetBase Foods", 18, 35, 110),
    ("ING016", "Chocolate Sauce", "Syrups & Sauces", "Raw Material", "litre", 260.0, "ChocoCraft Ingredients", "SweetBase Foods", 18, 12, 36),
    ("ING017", "Caramel Syrup", "Syrups & Sauces", "Raw Material", "litre", 250.0, "SweetBase Foods", "ChocoCraft Ingredients", 18, 10, 32),
    ("ING018", "Vanilla Syrup", "Syrups & Sauces", "Raw Material", "litre", 240.0, "SweetBase Foods", "Metro Wholesale Delhi", 18, 10, 32),
    ("ING019", "Sugar Syrup", "Syrups & Sauces", "Raw Material", "litre", 90.0, "SweetBase Foods", "Metro Wholesale Delhi", 18, 18, 50),
    ("ING020", "Tea Leaves", "Tea Inputs", "Raw Material", "kg", 620.0, "TeaLeaf Traders NCR", "Metro Wholesale Delhi", 5, 5, 18),
    ("ING021", "Matcha Powder", "Tea Inputs", "Raw Material", "kg", 2150.0, "TeaLeaf Traders NCR", "Metro Wholesale Delhi", 18, 2, 8),
    ("ING022", "Ice", "Beverage Inputs", "Raw Material", "kg", 12.0, "Metro Wholesale Delhi", "FreshDairy Foods NCR", 5, 120, 400),
    ("ING023", "Lemon", "Produce", "Raw Material", "kg", 110.0, "GreenLeaf Produce Delhi", "Metro Wholesale Delhi", 5, 10, 36),
    ("ING024", "Hibiscus Concentrate", "Beverage Inputs", "Raw Material", "litre", 390.0, "SweetBase Foods", "TeaLeaf Traders NCR", 18, 4, 16),
    ("ING025", "Mixed Berry Pulp", "Fruit Inputs", "Raw Material", "kg", 420.0, "FrozenBerry Traders", "Metro Wholesale Delhi", 18, 10, 30),
    ("ING026", "Banana", "Produce", "Raw Material", "kg", 72.0, "GreenLeaf Produce Delhi", "Metro Wholesale Delhi", 5, 18, 60),
    ("ING027", "Butter", "Dairy", "Raw Material", "kg", 520.0, "FreshDairy Foods NCR", "SweetBase Foods", 12, 8, 24),
    ("ING028", "Lettuce", "Produce", "Raw Material", "kg", 95.0, "GreenLeaf Produce Delhi", "Metro Wholesale Delhi", 5, 7, 24),
    ("ING029", "Onion", "Produce", "Raw Material", "kg", 42.0, "GreenLeaf Produce Delhi", "Metro Wholesale Delhi", 5, 18, 60),
    ("ING030", "Capsicum", "Produce", "Raw Material", "kg", 84.0, "GreenLeaf Produce Delhi", "Metro Wholesale Delhi", 5, 10, 36),
    ("ING031", "Tomato", "Produce", "Raw Material", "kg", 54.0, "GreenLeaf Produce Delhi", "Metro Wholesale Delhi", 5, 18, 60),
    ("ING032", "Pesto Sauce", "Syrups & Sauces", "Raw Material", "kg", 340.0, "SpiceRoot Foods", "Metro Wholesale Delhi", 18, 8, 24),
    ("ING033", "Chipotle Sauce", "Syrups & Sauces", "Raw Material", "kg", 280.0, "SpiceRoot Foods", "Metro Wholesale Delhi", 18, 8, 24),
    ("ING034", "Salsa", "Syrups & Sauces", "Raw Material", "kg", 190.0, "SpiceRoot Foods", "Metro Wholesale Delhi", 18, 8, 24),
    ("ING035", "Aioli", "Syrups & Sauces", "Raw Material", "kg", 310.0, "SpiceRoot Foods", "Metro Wholesale Delhi", 18, 8, 24),
    ("ING036", "Cold Cup", "Packaging", "Consumable", "pcs", 3.2, "PackPro Disposables", "Metro Wholesale Delhi", 18, 700, 1600),
    ("ING037", "Hot Cup", "Packaging", "Consumable", "pcs", 2.8, "PackPro Disposables", "Metro Wholesale Delhi", 18, 700, 1600),
    ("ING038", "Lid", "Packaging", "Consumable", "pcs", 1.1, "PackPro Disposables", "Metro Wholesale Delhi", 18, 700, 1600),
    ("ING039", "Straw", "Packaging", "Consumable", "pcs", 0.55, "PackPro Disposables", "Metro Wholesale Delhi", 18, 500, 1200),
    ("ING040", "Napkin", "Packaging", "Consumable", "pcs", 0.32, "PackPro Disposables", "Metro Wholesale Delhi", 18, 900, 2200),
    ("ING041", "Dessert Box", "Packaging", "Consumable", "pcs", 5.0, "PackPro Disposables", "Metro Wholesale Delhi", 18, 180, 500),
    ("ING042", "Sandwich Box", "Packaging", "Consumable", "pcs", 6.5, "PackPro Disposables", "Metro Wholesale Delhi", 18, 180, 500),
    ("ING043", "Wrap Packaging", "Packaging", "Consumable", "pcs", 5.8, "PackPro Disposables", "Metro Wholesale Delhi", 18, 180, 500),
]


def build_ingredients() -> pd.DataFrame:
    columns = [
        "item_code",
        "item_name",
        "category_name",
        "super_category_name",
        "unit",
        "average_price",
        "primary_vendor",
        "alternate_vendor",
        "gst_rate",
        "low_stock_threshold",
        "standard_order_qty",
    ]
    return pd.DataFrame(INGREDIENT_ROWS, columns=columns)


def ingredient_lookup() -> dict[str, dict]:
    return build_ingredients().set_index("item_name").to_dict(orient="index")

