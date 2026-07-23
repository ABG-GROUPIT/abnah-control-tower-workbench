from __future__ import annotations

import argparse

from generator.generate_all import generate_all
from loaders.db import get_engine, print_row_counts
from loaders.delete_month import delete_month
from loaders.export_csv import export_current_csv
from loaders.load_month import load_month, month_is_loaded, month_number_to_code
from loaders.load_static import load_static
from loaders.schema import reset_schema
from loaders.status import print_status


def reset_month_1() -> None:
    print("Generating deterministic synthetic CSVs...")
    generate_all()

    engine = get_engine()
    print("Dropping old demo objects and recreating raw/control schemas...")
    reset_schema(engine)

    print("Loading static/master reports...")
    load_static(engine)

    print("Loading Month 1 operational reports...")
    load_month(engine, "month_01", notes="Initial baseline Month 1 load")

    print_row_counts(engine)
    print("Reset to Month 1 complete.")


def load_month_command(month: int | str) -> None:
    month_code = month_number_to_code(month)
    engine = get_engine()
    load_month(engine, month_code, notes=f"Loaded {month_code} from manage_demo.py")
    print_row_counts(engine)


def delete_month_command(month: int | str) -> None:
    engine = get_engine()
    delete_month(engine, month)
    print_row_counts(engine)


def reset_to_month(target_month: int | str) -> None:
    target_code = month_number_to_code(target_month)
    engine = get_engine()

    if not month_is_loaded(engine, "month_01"):
        reset_month_1()
        engine = get_engine()

    if target_code == "month_01":
        if month_is_loaded(engine, "month_03"):
            delete_month(engine, "month_03")
        if month_is_loaded(engine, "month_02"):
            delete_month(engine, "month_02")
    elif target_code == "month_02":
        if not month_is_loaded(engine, "month_02"):
            load_month(engine, "month_02", notes="Loaded Month 2 for reset-to-month 2")
        if month_is_loaded(engine, "month_03"):
            delete_month(engine, "month_03")
    else:
        raise ValueError("reset-to-month supports only 1 or 2 for this demo.")

    print_row_counts(engine)
    print(f"Reset to {target_code} complete.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage the ABNAH synthetic Zoho/FastAPI demo.")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("reset-month-1")

    load_parser = sub.add_parser("load-month")
    load_parser.add_argument("month", choices=["2", "3", "02", "03", "month_02", "month_03"])

    delete_parser = sub.add_parser("delete-month")
    delete_parser.add_argument("month", choices=["2", "3", "02", "03", "month_02", "month_03"])

    reset_to_parser = sub.add_parser("reset-to-month")
    reset_to_parser.add_argument("month", choices=["1", "2", "01", "02", "month_01", "month_02"])

    sub.add_parser("status")
    sub.add_parser("export-current-csv")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "reset-month-1":
        reset_month_1()
    elif args.command == "load-month":
        load_month_command(args.month)
    elif args.command == "delete-month":
        delete_month_command(args.month)
    elif args.command == "reset-to-month":
        reset_to_month(args.month)
    elif args.command == "status":
        print_status()
    elif args.command == "export-current-csv":
        export_current_csv()
    else:
        parser.error(f"Unknown command {args.command}")


if __name__ == "__main__":
    main()

