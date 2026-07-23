from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

import numpy as np
import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
STATIC_DIR = DATA_DIR / "static"
EXPORT_DIR = ROOT_DIR / "exports" / "current"
DOCS_DIR = ROOT_DIR / "docs"

SEED = 260126

MONTHS: dict[str, tuple[date, date]] = {
    "month_01": (date(2026, 1, 1), date(2026, 1, 31)),
    "month_02": (date(2026, 2, 1), date(2026, 2, 28)),
    "month_03": (date(2026, 3, 1), date(2026, 3, 31)),
}

MONTH_DIRS = {month: DATA_DIR / month for month in MONTHS}


def ensure_dirs() -> None:
    for path in [DATA_DIR, STATIC_DIR, EXPORT_DIR, DOCS_DIR, *MONTH_DIRS.values()]:
        path.mkdir(parents=True, exist_ok=True)


def rng_for(name: str) -> np.random.Generator:
    salt = sum((idx + 1) * ord(ch) for idx, ch in enumerate(name))
    return np.random.default_rng(SEED + salt)


def month_code_for_date(value: date | datetime | str) -> str:
    if isinstance(value, str):
        day = datetime.strptime(value[:10], "%Y-%m-%d").date()
    elif isinstance(value, datetime):
        day = value.date()
    else:
        day = value

    for month_code, (start, end) in MONTHS.items():
        if start <= day <= end:
            return month_code
    raise ValueError(f"Date outside configured demo range: {day}")


def date_range(start: date, end: date) -> list[date]:
    return [d.date() for d in pd.date_range(start=start, end=end, freq="D")]


def month_date_ranges() -> dict[str, list[date]]:
    return {month: date_range(start, end) for month, (start, end) in MONTHS.items()}


def write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def read_csv(path: Path, parse_dates: list[str] | None = None) -> pd.DataFrame:
    return pd.read_csv(path, parse_dates=parse_dates or [])


def clean_money(value: float) -> float:
    return round(float(value), 2)


def clean_qty(value: float) -> float:
    return round(float(value), 4)
