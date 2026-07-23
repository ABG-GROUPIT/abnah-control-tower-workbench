CREATE TABLE IF NOT EXISTS control.etl_load_batch (
    batch_id SERIAL PRIMARY KEY,
    month_code TEXT UNIQUE NOT NULL,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL,
    sales_rows INTEGER DEFAULT 0,
    purchase_rows INTEGER DEFAULT 0,
    entry_rows INTEGER DEFAULT 0,
    inventory_rows INTEGER DEFAULT 0,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS control.loaded_row_registry (
    registry_id SERIAL PRIMARY KEY,
    month_code TEXT NOT NULL,
    table_name TEXT NOT NULL,
    row_id TEXT NOT NULL,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(month_code, table_name, row_id)
);

