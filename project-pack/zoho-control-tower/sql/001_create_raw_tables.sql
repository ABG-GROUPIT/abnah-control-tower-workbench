CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS control;

CREATE TABLE IF NOT EXISTS raw.vendor_report (
    row_id TEXT PRIMARY KEY,
    vendor_name TEXT NOT NULL,
    vendor_code TEXT UNIQUE,
    description TEXT,
    contact_person TEXT,
    contact_number TEXT,
    email TEXT,
    tin_number TEXT,
    service_tax_number TEXT,
    gstin_number TEXT,
    msme TEXT,
    fssai_number TEXT,
    pan_number TEXT,
    from_date DATE,
    to_date DATE,
    state TEXT,
    address TEXT
);

CREATE TABLE IF NOT EXISTS raw.menu_master (
    row_id TEXT PRIMARY KEY,
    item_number TEXT UNIQUE,
    item_name TEXT NOT NULL,
    uid TEXT,
    item_description TEXT,
    rate NUMERIC(12,2),
    category_name TEXT,
    super_category_name TEXT,
    non_veg INTEGER,
    hsn_code TEXT,
    aggregator_alias_name TEXT,
    aggregator_alias_description TEXT,
    not_in_sweetshop BOOLEAN,
    has_variant INTEGER,
    is_inclusive_item BOOLEAN,
    is_scannable_item BOOLEAN,
    do_not_print_sticker BOOLEAN
);

CREATE TABLE IF NOT EXISTS raw.brand_recipe_consumption (
    row_id TEXT PRIMARY KEY,
    recipe_name TEXT,
    recipe_qty NUMERIC(12,4),
    recipe_unit TEXT,
    item_name TEXT NOT NULL,
    item_qty NUMERIC(12,4),
    item_unit TEXT,
    item_tab_type TEXT
);

CREATE TABLE IF NOT EXISTS raw.sales_report (
    row_id TEXT PRIMARY KEY,
    outlet_name TEXT NOT NULL,
    date DATE NOT NULL,
    super_category TEXT,
    category TEXT,
    item_number TEXT NOT NULL,
    item_name TEXT NOT NULL,
    qty NUMERIC(12,4),
    net_sale NUMERIC(14,2)
);

CREATE TABLE IF NOT EXISTS raw.purchase_report (
    row_id TEXT PRIMARY KEY,
    deployment TEXT NOT NULL,
    store_name TEXT,
    vendor_name TEXT,
    po_number TEXT,
    po_date DATE,
    expected_delivery DATE,
    po_status TEXT,
    item_code TEXT,
    item_name TEXT,
    category_name TEXT,
    super_category_name TEXT,
    total_processed_qty NUMERIC(14,4),
    remaining_balance_qty NUMERIC(14,4),
    quantity NUMERIC(14,4),
    unit TEXT,
    unit_price NUMERIC(14,2),
    subtotal NUMERIC(14,2),
    tax NUMERIC(14,2),
    total_item_cost NUMERIC(14,2)
);

CREATE TABLE IF NOT EXISTS raw.entry_report (
    row_id TEXT PRIMARY KEY,
    deployment_name TEXT NOT NULL,
    store_kitchen_name TEXT,
    user_name TEXT,
    vendor_name TEXT,
    date DATE,
    transaction_number TEXT,
    invoice_number TEXT,
    invoice_date DATE,
    item_code TEXT,
    item_name TEXT,
    category_name TEXT,
    super_category_name TEXT,
    quantity NUMERIC(14,4),
    unit TEXT,
    mrp NUMERIC(14,2),
    unit_price NUMERIC(14,2),
    amount NUMERIC(14,2),
    discount NUMERIC(14,2),
    gst_igst_rate NUMERIC(8,2),
    gst_igst_value NUMERIC(14,2),
    total_tax NUMERIC(14,2),
    item_charges_amount NUMERIC(14,2),
    entry_total NUMERIC(14,2),
    return_quantity NUMERIC(14,4),
    return_amount NUMERIC(14,2),
    grand_total NUMERIC(14,2)
);

CREATE TABLE IF NOT EXISTS raw.inventory_closing_report (
    row_id TEXT PRIMARY KEY,
    deployment TEXT NOT NULL,
    date DATE NOT NULL,
    generation_date DATE,
    generation_time TIME,
    item_code TEXT,
    item_name TEXT,
    super_category_code TEXT,
    super_category_name TEXT,
    category_code TEXT,
    category_name TEXT,
    unit_name TEXT,
    average_price NUMERIC(14,2),
    store_stock_qty NUMERIC(14,4),
    total_qty NUMERIC(14,4),
    total_amt NUMERIC(14,2)
);

CREATE TABLE IF NOT EXISTS raw.indian_calendar_holidays (
    row_id TEXT PRIMARY KEY,
    calendar_date DATE NOT NULL,
    holiday_name TEXT NOT NULL,
    holiday_type TEXT,
    region TEXT,
    is_public_holiday BOOLEAN,
    is_bank_holiday BOOLEAN,
    expected_business_impact TEXT,
    impact_direction TEXT,
    notes TEXT,
    UNIQUE (calendar_date, holiday_name)
);

CREATE TABLE IF NOT EXISTS raw.manual_calendar_events (
    row_id TEXT PRIMARY KEY,
    event_id TEXT UNIQUE,
    event_name TEXT NOT NULL,
    event_type TEXT,
    start_date DATE,
    end_date DATE,
    outlet_scope TEXT,
    affected_outlets TEXT,
    affected_category TEXT,
    affected_items TEXT,
    expected_impact_pct NUMERIC(8,2),
    impact_direction TEXT,
    confidence_level TEXT,
    event_source TEXT,
    admin_status TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS raw.competitor_pricing (
    row_id TEXT PRIMARY KEY,
    competitor_id TEXT UNIQUE,
    competitor_name TEXT,
    market_area TEXT,
    competitor_category TEXT,
    competitor_item_name TEXT,
    competitor_price NUMERIC(14,2),
    abnah_item_number TEXT,
    abnah_item_name TEXT,
    abnah_price NUMERIC(14,2),
    price_difference NUMERIC(14,2),
    price_index NUMERIC(10,3),
    price_position TEXT,
    expected_sales_impact TEXT,
    notes TEXT
);

