from __future__ import annotations

from pathlib import Path

from sqlalchemy.engine import Engine

from loaders.db import STATIC_DIR, copy_csv_idempotent, get_engine
from loaders.schema import STATIC_TABLES


def load_static(engine: Engine, static_dir: Path = STATIC_DIR) -> dict[str, int]:
    counts = {}
    for report_name, config in STATIC_TABLES.items():
        filename = config["csv"]
        target = config["table"]
        inserted = copy_csv_idempotent(engine, static_dir / filename, target)
        counts[report_name] = inserted
        print(f"Loaded {inserted:,} rows into {target}")
    return counts


def main() -> None:
    engine = get_engine()
    load_static(engine)


if __name__ == "__main__":
    main()
