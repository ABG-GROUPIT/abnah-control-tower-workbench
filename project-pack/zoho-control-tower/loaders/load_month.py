from __future__ import annotations

import csv
import io

from sqlalchemy import text
from sqlalchemy.engine import Engine

from generator.config import MONTH_DIRS, MONTHS
from generator.generate_all import generate_all
from generator.outlets import OUTLETS
from loaders.db import ROOT_DIR, copy_csv_idempotent_returning_ids, get_engine
from loaders.schema import OPERATIONAL_TABLES


def ensure_generated_csvs() -> None:
    required = [
        ROOT_DIR / "data" / "static" / "menu_master.csv",
        ROOT_DIR / "data" / "month_01" / "sales_report" / "OUT001_sales_report.csv",
        ROOT_DIR / "data" / "month_02" / "sales_report" / "OUT001_sales_report.csv",
        ROOT_DIR / "data" / "month_03" / "sales_report" / "OUT001_sales_report.csv",
    ]
    if not all(path.exists() for path in required):
        print("Generated CSVs not found. Running generator first.")
        generate_all()


def month_is_loaded(engine: Engine, month_code: str) -> bool:
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT COUNT(*) FROM control.etl_load_batch WHERE month_code = :month_code AND status = 'LOADED'"),
            {"month_code": month_code},
        )
        return int(result.scalar_one()) > 0


def month_number_to_code(month: int | str) -> str:
    value = str(month)
    if value.startswith("month_"):
        return value
    if value in {"1", "01"}:
        return "month_01"
    if value in {"2", "02"}:
        return "month_02"
    if value in {"3", "03"}:
        return "month_03"
    raise ValueError(f"Unsupported demo month: {month}")


def register_loaded_rows(engine: Engine, month_code: str, table_name: str, row_ids: list[str]) -> None:
    if not row_ids:
        return
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    for row_id in row_ids:
        writer.writerow([month_code, table_name, row_id])
    buffer.seek(0)

    raw = engine.raw_connection()
    try:
        with raw.cursor() as cur:
            cur.execute(
                """
                CREATE TEMP TABLE tmp_loaded_row_registry (
                    month_code TEXT NOT NULL,
                    table_name TEXT NOT NULL,
                    row_id TEXT NOT NULL
                ) ON COMMIT DROP;
                """
            )
            cur.copy_expert(
                "COPY tmp_loaded_row_registry (month_code, table_name, row_id) FROM STDIN WITH (FORMAT CSV)",
                buffer,
            )
            cur.execute(
                """
                INSERT INTO control.loaded_row_registry (month_code, table_name, row_id)
                SELECT month_code, table_name, row_id
                FROM tmp_loaded_row_registry
                ON CONFLICT DO NOTHING;
                """
            )
        raw.commit()
    except Exception:
        raw.rollback()
        raise
    finally:
        raw.close()


def record_month_loaded(engine: Engine, month_code: str, counts: dict[str, int], notes: str) -> None:
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO control.etl_load_batch (
                    month_code,
                    status,
                    sales_rows,
                    purchase_rows,
                    entry_rows,
                    inventory_rows,
                    notes
                )
                VALUES (
                    :month_code,
                    'LOADED',
                    :sales_rows,
                    :purchase_rows,
                    :entry_rows,
                    :inventory_rows,
                    :notes
                )
                ON CONFLICT (month_code) DO NOTHING;
                """
            ),
            {
                "month_code": month_code,
                "sales_rows": counts.get("sales_rows", 0),
                "purchase_rows": counts.get("purchase_rows", 0),
                "entry_rows": counts.get("entry_rows", 0),
                "inventory_rows": counts.get("inventory_rows", 0),
                "notes": notes,
            },
        )


def load_month(engine: Engine, month_code: str, notes: str = "") -> dict[str, int]:
    month_code = month_number_to_code(month_code)
    if month_code not in MONTHS:
        raise ValueError(f"Unknown month_code {month_code}; expected one of {', '.join(MONTHS)}")
    ensure_generated_csvs()
    if month_is_loaded(engine, month_code):
        print(f"{month_code} is already marked LOADED in control.etl_load_batch. Skipping month load safely.")
        return {"sales_rows": 0, "purchase_rows": 0, "entry_rows": 0, "inventory_rows": 0}

    counts: dict[str, int] = {}
    for report_name, config in OPERATIONAL_TABLES.items():
        target = config["table"]
        count_key = config["count_key"]
        total_inserted = 0
        for outlet in OUTLETS:
            outlet_code = outlet["outlet_code"]
            csv_path = MONTH_DIRS[month_code] / report_name / f"{outlet_code}_{report_name}.csv"
            inserted_ids = copy_csv_idempotent_returning_ids(engine, csv_path, target)
            register_loaded_rows(engine, month_code, target, inserted_ids)
            total_inserted += len(inserted_ids)
            print(f"Loaded {len(inserted_ids):,} rows into {target} from {month_code}/{outlet_code}")
        counts[count_key] = total_inserted

    record_month_loaded(engine, month_code, counts, notes or f"Loaded {month_code} synthetic data")
    return counts


def main() -> None:
    engine = get_engine()
    load_month(engine, "month_01")


if __name__ == "__main__":
    main()
