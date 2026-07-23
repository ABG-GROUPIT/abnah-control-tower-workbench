from __future__ import annotations

import pandas as pd


OUTLETS = [
    {
        "outlet_code": "OUT001",
        "outlet_name": "ABNAH Cafe Connaught Place",
        "market_area": "Connaught Place",
        "persona": "corporate, office, tourist demand",
        "weekday_profile": "High Monday-Friday coffee and lunch demand",
    },
    {
        "outlet_code": "OUT002",
        "outlet_name": "ABNAH Cafe Hauz Khas",
        "market_area": "Hauz Khas",
        "persona": "student, youth, social, local event demand",
        "weekday_profile": "Strong Friday/weekend and student event demand",
    },
    {
        "outlet_code": "OUT003",
        "outlet_name": "ABNAH Cafe Saket Premium",
        "market_area": "Saket",
        "persona": "mall, leisure, premium weekend demand",
        "weekday_profile": "Strong desserts, shakes, premium beverages, and weekends",
    },
]


OUTLET_BY_NAME = {row["outlet_name"]: row for row in OUTLETS}


def build_outlets() -> pd.DataFrame:
    return pd.DataFrame(OUTLETS)

