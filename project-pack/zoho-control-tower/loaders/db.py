from __future__ import annotations

import io
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


ROOT_DIR = Path(__file__).resolve().parents[1]
SQL_DIR = ROOT_DIR / "sql"
STATIC_DIR = ROOT_DIR / "data" / "static"
EXPORT_DIR = ROOT_DIR / "exports" / "current"


def get_database_url() -> str:
    load_dotenv(ROOT_DIR / ".env")
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set. Copy .env.example to .env and add your Neon connection string.")
    return database_url


def get_engine() -> Engine:
    return create_engine(get_database_url(), pool_pre_ping=True, future=True)


def quote_ident(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def split_table_name(table_name: str) -> tuple[str, str]:
    parts = table_name.split(".")
    if len(parts) != 2:
        raise ValueError(f"Expected schema.table, got {table_name}")
    return parts[0], parts[1]


def run_sql_file(engine: Engine, path: Path) -> None:
    sql = path.read_text(encoding="utf-8")
    raw = engine.raw_connection()
    try:
        with raw.cursor() as cur:
            cur.execute(sql)
        raw.commit()
    except Exception:
        raw.rollback()
        raise
    finally:
        raw.close()


def run_sql_files(engine: Engine, filenames: list[str]) -> None:
    for filename in filenames:
        run_sql_file(engine, SQL_DIR / filename)


def copy_csv_idempotent(engine: Engine, csv_path: Path, target_table: str) -> int:
    return len(copy_csv_idempotent_returning_ids(engine, csv_path, target_table))


def copy_csv_idempotent_returning_ids(engine: Engine, csv_path: Path, target_table: str) -> list[str]:
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing CSV: {csv_path}")
    df = pd.read_csv(csv_path)
    if df.empty:
        return []
    schema, table = split_table_name(target_table)
    temp_name = f"tmp_load_{schema}_{table}_{os.getpid()}"
    columns = list(df.columns)
    quoted_columns = ", ".join(quote_ident(col) for col in columns)
    full_target = f"{quote_ident(schema)}.{quote_ident(table)}"
    temp_table = quote_ident(temp_name)

    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)

    raw = engine.raw_connection()
    try:
        with raw.cursor() as cur:
            cur.execute(f"CREATE TEMP TABLE {temp_table} (LIKE {full_target} INCLUDING DEFAULTS) ON COMMIT DROP;")
            cur.copy_expert(
                f"COPY {temp_table} ({quoted_columns}) FROM STDIN WITH (FORMAT CSV, HEADER TRUE)",
                buffer,
            )
            cur.execute(
                f"""
                INSERT INTO {full_target} ({quoted_columns})
                SELECT {quoted_columns}
                FROM {temp_table}
                ON CONFLICT DO NOTHING
                RETURNING row_id;
                """
            )
            inserted_ids = [row[0] for row in cur.fetchall()]
        raw.commit()
        return inserted_ids
    except Exception:
        raw.rollback()
        raise
    finally:
        raw.close()


def table_row_count(engine: Engine, table_name: str) -> int:
    schema, table = split_table_name(table_name)
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {quote_ident(schema)}.{quote_ident(table)}"))
        return int(result.scalar_one())


def print_row_counts(engine: Engine) -> None:
    tables = [
        "raw.vendor_report",
        "raw.menu_master",
        "raw.brand_recipe_consumption",
        "raw.sales_report",
        "raw.purchase_report",
        "raw.entry_report",
        "raw.inventory_closing_report",
        "raw.indian_calendar_holidays",
        "raw.manual_calendar_events",
        "raw.competitor_pricing",
        "control.etl_load_batch",
        "control.loaded_row_registry",
    ]
    print("Current database row counts:")
    for table in tables:
        print(f"  {table}: {table_row_count(engine, table):,}")


def export_query_to_csv(engine: Engine, query: str, output_path: Path) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.read_sql_query(query, engine)
    df.to_csv(output_path, index=False)
    return len(df)


def order_by_sql(order_by: list[str] | None) -> str:
    columns = order_by or ["row_id"]
    return ", ".join(quote_ident(column) for column in columns)


def query_to_csv_text(engine: Engine, table_name: str, columns: list[str], order_by: list[str] | None = None) -> str:
    schema, table = split_table_name(table_name)
    ordered_columns = ", ".join(quote_ident(col) for col in columns)
    query = f"SELECT {ordered_columns} FROM {quote_ident(schema)}.{quote_ident(table)} ORDER BY {order_by_sql(order_by)}"
    df = pd.read_sql_query(query, engine)
    return df.to_csv(index=False)


def query_to_csv_text_filtered(
    engine: Engine,
    table_name: str,
    columns: list[str],
    filters: dict[str, str],
    order_by: list[str] | None = None,
) -> str:
    schema, table = split_table_name(table_name)
    ordered_columns = ", ".join(quote_ident(col) for col in columns)
    where_parts = []
    params = {}
    for index, (column, value) in enumerate(filters.items()):
        param_name = f"filter_{index}"
        where_parts.append(f"{quote_ident(column)} = :{param_name}")
        params[param_name] = value
    where_sql = " WHERE " + " AND ".join(where_parts) if where_parts else ""
    query = text(
        f"SELECT {ordered_columns} "
        f"FROM {quote_ident(schema)}.{quote_ident(table)}"
        f"{where_sql} "
        f"ORDER BY {order_by_sql(order_by)}"
    )
    df = pd.read_sql_query(query, engine, params=params)
    return df.to_csv(index=False)
