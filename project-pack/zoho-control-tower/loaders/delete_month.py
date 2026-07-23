from __future__ import annotations

from sqlalchemy.engine import Engine

from loaders.db import get_engine, quote_ident, split_table_name
from loaders.load_month import month_number_to_code
from loaders.schema import OPERATIONAL_TABLES


def delete_month(engine: Engine, month: int | str) -> dict[str, int]:
    month_code = month_number_to_code(month)
    deleted_counts: dict[str, int] = {}
    raw = engine.raw_connection()
    try:
        with raw.cursor() as cur:
            for report_name, config in OPERATIONAL_TABLES.items():
                table_name = config["table"]
                schema, table = split_table_name(table_name)
                cur.execute(
                    f"""
                    DELETE FROM {quote_ident(schema)}.{quote_ident(table)} target
                    USING control.loaded_row_registry reg
                    WHERE reg.month_code = %s
                      AND reg.table_name = %s
                      AND reg.row_id = target.row_id
                    """,
                    (month_code, table_name),
                )
                deleted_counts[report_name] = cur.rowcount
                cur.execute(
                    """
                    DELETE FROM control.loaded_row_registry
                    WHERE month_code = %s
                      AND table_name = %s
                    """,
                    (month_code, table_name),
                )
            cur.execute("DELETE FROM control.etl_load_batch WHERE month_code = %s", (month_code,))
        raw.commit()
    except Exception:
        raw.rollback()
        raise
    finally:
        raw.close()

    print(f"Deleted {month_code}: " + ", ".join(f"{k}={v:,}" for k, v in deleted_counts.items()))
    return deleted_counts


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("month")
    args = parser.parse_args()
    delete_month(get_engine(), args.month)


if __name__ == "__main__":
    main()

