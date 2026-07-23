CREATE INDEX IF NOT EXISTS idx_sales_report_date_outlet ON raw.sales_report (date, outlet_name);
CREATE INDEX IF NOT EXISTS idx_sales_report_item ON raw.sales_report (item_number, item_name);
CREATE INDEX IF NOT EXISTS idx_purchase_report_month ON raw.purchase_report (po_date, vendor_name);
CREATE INDEX IF NOT EXISTS idx_entry_report_month ON raw.entry_report (date, vendor_name);
CREATE INDEX IF NOT EXISTS idx_inventory_closing_date_item ON raw.inventory_closing_report (date, deployment, item_name);
CREATE INDEX IF NOT EXISTS idx_events_dates ON raw.manual_calendar_events (start_date, end_date);
CREATE INDEX IF NOT EXISTS idx_competitor_area_item ON raw.competitor_pricing (market_area, abnah_item_number);
CREATE INDEX IF NOT EXISTS idx_loaded_row_registry_month_table ON control.loaded_row_registry (month_code, table_name);
CREATE INDEX IF NOT EXISTS idx_loaded_row_registry_row ON control.loaded_row_registry (table_name, row_id);

