from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.engine import Engine

from generator.outlets import OUTLETS
from loaders.db import get_engine, table_row_count
from loaders.schema import ALL_FEED_TABLES, OPERATIONAL_TABLES, STATIC_TABLES


def loaded_months(engine: Engine) -> list[dict]:
    with engine.connect() as conn:
        return [
            dict(row)
            for row in conn.execute(
                text(
                    """
                    SELECT month_code, loaded_at, status, sales_rows, purchase_rows, entry_rows, inventory_rows, notes
                    FROM control.etl_load_batch
                    ORDER BY month_code
                    """
                )
            ).mappings()
        ]


def registry_counts(engine: Engine) -> list[dict]:
    with engine.connect() as conn:
        return [
            dict(row)
            for row in conn.execute(
                text(
                    """
                    SELECT month_code, table_name, COUNT(*) AS row_count, MAX(loaded_at) AS latest_loaded_at
                    FROM control.loaded_row_registry
                    GROUP BY month_code, table_name
                    ORDER BY month_code, table_name
                    """
                )
            ).mappings()
        ]


def raw_row_counts(engine: Engine) -> dict[str, int]:
    return {config["table"]: table_row_count(engine, config["table"]) for config in ALL_FEED_TABLES.values()}


def feed_urls(base_url: str = "http://127.0.0.1:8000") -> list[str]:
    base = base_url.rstrip("/")
    urls = []
    for report_name in OPERATIONAL_TABLES:
        for outlet in OUTLETS:
            urls.append(f"{base}/zoho/{report_name}_{outlet['outlet_code']}.csv")
    urls.extend(f"{base}/zoho/{report_name}.csv" for report_name in STATIC_TABLES)
    return urls


def combined_debug_feed_urls(base_url: str = "http://127.0.0.1:8000") -> list[str]:
    base = base_url.rstrip("/")
    return [f"{base}/zoho/{report_name}.csv" for report_name in OPERATIONAL_TABLES]


def print_status(engine: Engine | None = None, base_url: str = "http://127.0.0.1:8000") -> None:
    engine = engine or get_engine()
    print("Loaded months:")
    for row in loaded_months(engine):
        print(
            f"  {row['month_code']} status={row['status']} loaded_at={row['loaded_at']} "
            f"sales={row['sales_rows']} purchase={row['purchase_rows']} entry={row['entry_rows']} inventory={row['inventory_rows']}"
        )
    print("Raw table row counts:")
    for table_name, count in raw_row_counts(engine).items():
        print(f"  {table_name}: {count:,}")
    print("Operational row counts by month from control.loaded_row_registry:")
    for row in registry_counts(engine):
        print(f"  {row['month_code']} {row['table_name']}: {row['row_count']:,} latest={row['latest_loaded_at']}")
    print("FastAPI Zoho import feed URLs:")
    for url in feed_urls(base_url):
        print(f"  {url}")
    print("FastAPI combined operational debug feed URLs:")
    for url in combined_debug_feed_urls(base_url):
        print(f"  {url}")


def main() -> None:
    print_status()


if __name__ == "__main__":
    main()
