from __future__ import annotations

from pathlib import Path

from loaders.db import EXPORT_DIR, export_query_to_csv, get_engine, order_by_sql, quote_ident
from loaders.schema import ALL_FEED_TABLES


def export_current_csv(output_dir: Path = EXPORT_DIR) -> dict[str, int]:
    engine = get_engine()
    output_dir.mkdir(parents=True, exist_ok=True)
    counts = {}
    for report_name, config in ALL_FEED_TABLES.items():
        columns = ", ".join(quote_ident(column) for column in config["columns"])
        table_name = config["table"]
        count = export_query_to_csv(
            engine,
            f"SELECT {columns} FROM {table_name} ORDER BY {order_by_sql(config.get('order_by'))}",
            output_dir / f"{report_name}.csv",
        )
        counts[report_name] = count
        print(f"Exported {count:,} rows from {table_name}")
    return counts


def main() -> None:
    export_current_csv()


if __name__ == "__main__":
    main()
