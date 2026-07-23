from __future__ import annotations

from sqlalchemy.engine import Engine

from loaders.db import get_engine, run_sql_files


SQL_FILES = [
    "001_create_raw_tables.sql",
    "002_create_control_tables.sql",
    "003_indexes.sql",
]

STATIC_TABLES = {
    "vendor_report": {
        "table": "raw.vendor_report",
        "csv": "vendor_report.csv",
        "order_by": ["vendor_code", "row_id"],
        "columns": [
            "row_id",
            "vendor_name",
            "vendor_code",
            "description",
            "contact_person",
            "contact_number",
            "email",
            "tin_number",
            "service_tax_number",
            "gstin_number",
            "msme",
            "fssai_number",
            "pan_number",
            "from_date",
            "to_date",
            "state",
            "address",
        ],
    },
    "menu_master": {
        "table": "raw.menu_master",
        "csv": "menu_master.csv",
        "order_by": ["item_number", "row_id"],
        "columns": [
            "row_id",
            "item_number",
            "item_name",
            "uid",
            "item_description",
            "rate",
            "category_name",
            "super_category_name",
            "non_veg",
            "hsn_code",
            "aggregator_alias_name",
            "aggregator_alias_description",
            "not_in_sweetshop",
            "has_variant",
            "is_inclusive_item",
            "is_scannable_item",
            "do_not_print_sticker",
        ],
    },
    "brand_recipe_consumption": {
        "table": "raw.brand_recipe_consumption",
        "csv": "brand_recipe_consumption.csv",
        "order_by": ["row_id"],
        "columns": [
            "row_id",
            "recipe_name",
            "recipe_qty",
            "recipe_unit",
            "item_name",
            "item_qty",
            "item_unit",
            "item_tab_type",
        ],
    },
    "indian_calendar_holidays": {
        "table": "raw.indian_calendar_holidays",
        "csv": "indian_calendar_holidays.csv",
        "order_by": ["calendar_date", "row_id"],
        "columns": [
            "row_id",
            "calendar_date",
            "holiday_name",
            "holiday_type",
            "region",
            "is_public_holiday",
            "is_bank_holiday",
            "expected_business_impact",
            "impact_direction",
            "notes",
        ],
    },
    "manual_calendar_events": {
        "table": "raw.manual_calendar_events",
        "csv": "manual_calendar_events.csv",
        "order_by": ["start_date", "row_id"],
        "columns": [
            "row_id",
            "event_id",
            "event_name",
            "event_type",
            "start_date",
            "end_date",
            "outlet_scope",
            "affected_outlets",
            "affected_category",
            "affected_items",
            "expected_impact_pct",
            "impact_direction",
            "confidence_level",
            "event_source",
            "admin_status",
            "notes",
        ],
    },
    "competitor_pricing": {
        "table": "raw.competitor_pricing",
        "csv": "competitor_pricing.csv",
        "order_by": ["market_area", "abnah_item_number", "competitor_id", "row_id"],
        "columns": [
            "row_id",
            "competitor_id",
            "competitor_name",
            "market_area",
            "competitor_category",
            "competitor_item_name",
            "competitor_price",
            "abnah_item_number",
            "abnah_item_name",
            "abnah_price",
            "price_difference",
            "price_index",
            "price_position",
            "expected_sales_impact",
            "notes",
        ],
    },
}

OPERATIONAL_TABLES = {
    "sales_report": {
        "table": "raw.sales_report",
        "count_key": "sales_rows",
        "outlet_column": "outlet_name",
        "order_by": ["date", "row_id"],
        "columns": [
            "row_id",
            "outlet_name",
            "date",
            "super_category",
            "category",
            "item_number",
            "item_name",
            "qty",
            "net_sale",
        ],
    },
    "purchase_report": {
        "table": "raw.purchase_report",
        "count_key": "purchase_rows",
        "outlet_column": "deployment",
        "order_by": ["po_date", "row_id"],
        "columns": [
            "row_id",
            "deployment",
            "store_name",
            "vendor_name",
            "po_number",
            "po_date",
            "expected_delivery",
            "po_status",
            "item_code",
            "item_name",
            "category_name",
            "super_category_name",
            "total_processed_qty",
            "remaining_balance_qty",
            "quantity",
            "unit",
            "unit_price",
            "subtotal",
            "tax",
            "total_item_cost",
        ],
    },
    "entry_report": {
        "table": "raw.entry_report",
        "count_key": "entry_rows",
        "outlet_column": "deployment_name",
        "order_by": ["date", "row_id"],
        "columns": [
            "row_id",
            "deployment_name",
            "store_kitchen_name",
            "user_name",
            "vendor_name",
            "date",
            "transaction_number",
            "invoice_number",
            "invoice_date",
            "item_code",
            "item_name",
            "category_name",
            "super_category_name",
            "quantity",
            "unit",
            "mrp",
            "unit_price",
            "amount",
            "discount",
            "gst_igst_rate",
            "gst_igst_value",
            "total_tax",
            "item_charges_amount",
            "entry_total",
            "return_quantity",
            "return_amount",
            "grand_total",
        ],
    },
    "inventory_closing_report": {
        "table": "raw.inventory_closing_report",
        "count_key": "inventory_rows",
        "outlet_column": "deployment",
        "order_by": ["date", "item_code", "row_id"],
        "columns": [
            "row_id",
            "deployment",
            "date",
            "generation_date",
            "generation_time",
            "item_code",
            "item_name",
            "super_category_code",
            "super_category_name",
            "category_code",
            "category_name",
            "unit_name",
            "average_price",
            "store_stock_qty",
            "total_qty",
            "total_amt",
        ],
    },
}

ALL_FEED_TABLES = {
    **STATIC_TABLES,
    **OPERATIONAL_TABLES,
}


def drop_demo_schemas(engine: Engine) -> None:
    raw = engine.raw_connection()
    try:
        with raw.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS analytics CASCADE;")
            cur.execute("DROP SCHEMA IF EXISTS staging CASCADE;")
            cur.execute("DROP SCHEMA IF EXISTS raw CASCADE;")
            cur.execute("DROP SCHEMA IF EXISTS control CASCADE;")
            for object_name in [
                "vendor_report",
                "entry_report",
                "brand_recipe_consumption",
                "inventory_closing_report",
                "menu_master",
                "purchase_report",
                "sales_report",
                "indian_calendar_holidays",
                "manual_calendar_events",
                "competitor_pricing",
                "etl_load_batch",
                "loaded_row_registry",
            ]:
                cur.execute(f'DROP TABLE IF EXISTS public."{object_name}" CASCADE;')
            for view_name in [
                "v_vendor_report",
                "v_entry_report",
                "v_recipe_bom",
                "v_inventory_closing_report",
                "v_menu_master",
                "v_purchase_report",
                "v_sales_report",
                "v_holiday_calendar",
                "v_manual_events",
                "v_competitor_pricing",
                "v_sales_daily_outlet",
                "v_sales_item_performance",
                "v_vendor_spend_summary",
                "v_inventory_low_stock",
                "v_event_sales_impact",
                "v_theoretical_consumption",
                "v_competitor_price_position",
                "v_po_receipt_comparison",
                "v_category_mix_by_outlet",
                "v_vendor_material_mapping",
            ]:
                cur.execute(f'DROP VIEW IF EXISTS public."{view_name}" CASCADE;')
        raw.commit()
    except Exception:
        raw.rollback()
        raise
    finally:
        raw.close()


def create_schema(engine: Engine) -> None:
    run_sql_files(engine, SQL_FILES)


def reset_schema(engine: Engine | None = None) -> Engine:
    engine = engine or get_engine()
    drop_demo_schemas(engine)
    create_schema(engine)
    return engine


def main() -> None:
    engine = get_engine()
    create_schema(engine)
    print("Raw/control schemas and tables are ready.")


if __name__ == "__main__":
    main()
