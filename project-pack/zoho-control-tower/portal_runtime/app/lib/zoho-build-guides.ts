import {
  allDashboardFilters,
  type DashboardObject,
} from "./lean-architecture-data";

export interface AggregateMetricBuildGuide {
  expression: string;
  dataType: "Currency" | "Percentage" | "Decimal Number" | "Number";
  display: string;
  priority: string;
  synonyms: string;
  guardrail: string;
}

export const aggregateMetricBuildGuides: Record<string, AggregateMetricBuildGuide> = {
  AF_Flow_Net_Sales: {
    expression: 'sum("RAW_Gross_Net_Margin"."Net Sale Value")',
    dataType: "Currency",
    display: "INR, 2 decimals",
    priority: "P5",
    synonyms: "net sales, recognized sales, revenue",
    guardrail: "Use the physical sales Date range only.",
  },
  AF_Flow_Quantity_Sold: {
    expression: 'sum("RAW_Gross_Net_Margin"."Item Qty")',
    dataType: "Decimal Number",
    display: "Number",
    priority: "P4",
    synonyms: "quantity sold, units sold",
    guardrail: "Do not mix unlike item units as one business total.",
  },
  AF_Flow_Purchase_Value: {
    expression: 'sum("RAW_Purchase_Detail"."Purchase Amount")',
    dataType: "Currency",
    display: "INR, 2 decimals",
    priority: "P5",
    synonyms: "received value, receipt value",
    guardrail: "Use Purchase Amount, not Total and not ordered value.",
  },
  AF_Flow_Weighted_Purchase_Unit_Price: {
    expression: 'if(sum("RAW_Purchase_Detail"."Purchase Quantity") = 0,null,sum("RAW_Purchase_Detail"."Purchase Amount")/sum("RAW_Purchase_Detail"."Purchase Quantity"))',
    dataType: "Currency",
    display: "INR per source UOM, 2 decimals",
    priority: "P4",
    synonyms: "weighted purchase unit price",
    guardrail: "Compare only within the same Item, Vendor and Purchase Unit.",
  },
  AF_Period_Actual_Consumption_Qty: {
    expression: 'sum("QT_03_Consumption_Variance"."actual_consumption_qty")',
    dataType: "Decimal Number",
    display: "4 decimals; show canonical UOM",
    priority: "P4",
    synonyms: "actual usage, observed consumption",
    guardrail: "Display one canonical UOM; never total kg, litre and pcs together.",
  },
  AF_Period_Theoretical_Consumption_Qty: {
    expression: 'sum("QT_03_Consumption_Variance"."theoretical_consumption_qty")',
    dataType: "Decimal Number",
    display: "4 decimals; show canonical UOM",
    priority: "P4",
    synonyms: "recipe usage, expected usage",
    guardrail: "Requires evaluated recipe and approved UOM evidence.",
  },
  AF_Period_Consumption_Variance_Qty: {
    expression: 'sum("QT_03_Consumption_Variance"."consumption_variance_qty")',
    dataType: "Decimal Number",
    display: "4 decimals; show canonical UOM",
    priority: "P4",
    synonyms: "usage variance, consumption variance",
    guardrail: "Actual minus theoretical; it is not a savings measure.",
  },
  AF_Period_Consumption_Variance_Pct: {
    expression: 'if(sum("QT_03_Consumption_Variance"."theoretical_consumption_qty") = 0,null,sum("QT_03_Consumption_Variance"."consumption_variance_qty")/sum("QT_03_Consumption_Variance"."theoretical_consumption_qty"))',
    dataType: "Percentage",
    display: "Percentage, 2 decimals",
    priority: "P4",
    synonyms: "usage variance rate, consumption variance percentage",
    guardrail: "Use the ratio of sums; never average row percentages.",
  },
  AF_Period_Positive_Leakage_Value: {
    expression: 'sum("QT_03_Consumption_Variance"."consumption_leakage_value")',
    dataType: "Currency",
    display: "INR, 2 decimals",
    priority: "P5",
    synonyms: "positive consumption leakage, positive consumption variance value",
    guardrail: "A signal only; do not call it proven waste, theft or savings.",
  },
  AF_Flow_Theoretical_COGS: {
    expression: 'sum("QT_04_Menu_Profitability"."theoretical_cogs")',
    dataType: "Currency",
    display: "INR, 2 decimals",
    priority: "P5",
    synonyms: "theoretical recipe COGS, recipe cost",
    guardrail: "Use complete recipe-cost rows only.",
  },
  AF_Flow_Theoretical_Gross_Margin: {
    expression: 'sum("QT_04_Menu_Profitability"."menu_gross_margin")',
    dataType: "Currency",
    display: "INR, 2 decimals",
    priority: "P5",
    synonyms: "theoretical menu margin, theoretical gross margin",
    guardrail: "This is not source net margin or accounting profit.",
  },
  AF_Flow_Theoretical_Gross_Margin_Pct: {
    expression: 'if(sum("QT_04_Menu_Profitability"."net_sales_value") = 0,null,100*sum("QT_04_Menu_Profitability"."menu_gross_margin")/sum("QT_04_Menu_Profitability"."net_sales_value"))',
    dataType: "Percentage",
    display: "Percentage, 2 decimals",
    priority: "P5",
    synonyms: "theoretical gross margin percentage, recipe GM percent",
    guardrail: "Zoho Percentage expects percent units here. Keep the 100 multiplier and never average the physical row percentage.",
  },
  AF_DQ_Exception_Count: {
    expression: 'count_distinct("QT_06_Data_Quality_Exceptions"."exception_id")',
    dataType: "Number",
    display: "Whole number",
    priority: "P4",
    synonyms: "data-quality exception count",
    guardrail: "Use the evaluated exception scope.",
  },
  AF_DQ_Affected_Subject_Count: {
    expression: 'count_distinct(concat("QT_06_Data_Quality_Exceptions"."source_table",\'|\',"QT_06_Data_Quality_Exceptions"."source_row_key"))',
    dataType: "Number",
    display: "Whole number",
    priority: "P3",
    synonyms: "affected source subjects, affected source records",
    guardrail: "Distinct source table plus source-row key; never use raw row count.",
  },
};

export interface DashboardFilterBuildGuide {
  seed: string;
  control: string;
  tabs: string;
  defaultValue: string;
  mappingRule: string;
  steps: string[];
  warning: string;
}

export const dashboardFilterBuildGuides: Record<(typeof allDashboardFilters)[number], DashboardFilterBuildGuide> = {
  "Reporting Period": {
    seed: "RAW_Gross_Net_Margin.Date",
    control: "Date Range User Filter",
    tabs: "01 Executive Control · 02 Procurement Vendor Consumption · 03 Sales & Menu Economics",
    defaultValue: "01 Jan 2026 through 31 Jan 2026",
    mappingRule: "Map only to each flow object's physical Date, PO Date, receipt Date, reporting_period_end, sales_date or current_date.",
    steps: ["Edit DB_02_ABNAH_SCM_Control_Tower_Final.", "Add a Date Range User Filter and name it Reporting Period.", "Seed it from RAW_Gross_Net_Margin.Date.", "Set the Month-1 default range and keep it visible on all three tabs.", "Open Customize dashboard filters on every object and apply only the exact physical flow-date mapping shown for that object."],
    warning: "Never map Reporting Period to as_of_date merely to force a value.",
  },
  "Snapshot As Of": {
    seed: "QT_02_Numerical_Risk_Center.as_of_date",
    control: "Single-select User Filter; All disabled",
    tabs: "01 Executive Control · 02 Procurement Vendor Consumption",
    defaultValue: "31 Jan 2026 through 31 Jan 2026 for Month 1",
    mappingRule: "Map only to QT_02_Numerical_Risk_Center.as_of_date and QT_05_Procurement_Control.as_of_date.",
    steps: ["Add a User Filter named Snapshot As Of.", "Seed it from QT_02_Numerical_Risk_Center.as_of_date; do not use Include Timeline Filter.", "Use individual-value Single Select and disable All when the tenant offers it.", "If Zoho renders a range control, set identical start and end dates.", "Map it only to QT02/QT05 state objects and never add 31 Jan as a report-local fixed filter."],
    warning: "A multi-date state range repeats snapshot rows and overstates liability, stock and risk.",
  },
  Outlet: {
    seed: "QT_02_Numerical_Risk_Center.outlet_name",
    control: "Single-select User Filter; All enabled",
    tabs: "All three tabs",
    defaultValue: "All",
    mappingRule: "Map to the compatible outlet field: outlet_name, Store Name or Deployment according to the selected object.",
    steps: ["Add a User Filter named Outlet.", "Seed it from QT_02_Numerical_Risk_Center.outlet_name.", "Choose Single Select and retain All.", "Use each object's exact mapping; do not rely on automatic same-name mapping.", "Reset to All before saving the meeting default."],
    warning: "The sales source uses Store Name and raw procurement uses Deployment; those are intentional mappings.",
  },
  "Menu Item": {
    seed: "QT_04_Menu_Profitability.menu_item_name",
    control: "Single-select User Filter; All enabled",
    tabs: "All three tabs",
    defaultValue: "All",
    mappingRule: "Map only to menu sales/profitability fields and REF_Item_Recipe.Item Name.",
    steps: ["Place a QT04 report before opening Add User Filters.", "Add Menu Item from QT_04_Menu_Profitability.menu_item_name.", "Choose Single Select and retain All.", "Map to QT04 menu_item_name, raw sales SKU / Item Name, or REF_Item_Recipe.Item Name only where listed.", "Leave every inventory, consumption and procurement object unmapped."],
    warning: "Do not map Menu Item to QT02 item_name; that field is polymorphic across risk domains.",
  },
  "Menu Category": {
    seed: "QT_04_Menu_Profitability.category_name",
    control: "Single-select User Filter; All enabled",
    tabs: "All three tabs",
    defaultValue: "All",
    mappingRule: "Map only to QT04 menu category or RAW_Gross_Net_Margin.Category.",
    steps: ["Add a User Filter named Menu Category.", "Seed it from QT_04_Menu_Profitability.category_name.", "Choose Single Select and retain All.", "Map only to the menu-sales and menu-economics objects listed.", "Leave material and procurement categories unmapped."],
    warning: "Menu Category and Material Category are different business dimensions.",
  },
  "Raw Material": {
    seed: "QT_03_Consumption_Variance.ingredient_name",
    control: "Single-select User Filter; All enabled",
    tabs: "All three tabs; recipe-map-only on Tab 3",
    defaultValue: "All",
    mappingRule: "Map to QT02 item_name, QT03 ingredient_name, QT05 item_name, raw procurement Item Name and REF_Item_Recipe.Ingredient Name exactly as listed.",
    steps: ["Place Positive Consumption Leakage or RPT_V2_S08_Ingredient_Leakage_Top10 so QT03 is exposed.", "Add Raw Material from QT_03_Consumption_Variance.ingredient_name.", "Choose Single Select and retain All.", "Map it manually to each compatible inventory/procurement/consumption object.", "On Tab 3 map it only to REF_Item_Recipe.Ingredient Name."],
    warning: "QT03 supplies all 43 materials; QT05 has only 29 current open-PO materials and is too narrow as the seed.",
  },
  "Material Category": {
    seed: "QT_03_Consumption_Variance.category_name",
    control: "Single-select User Filter; All enabled",
    tabs: "01 Executive Control · 02 Procurement Vendor Consumption",
    defaultValue: "All",
    mappingRule: "Map to QT02/QT03/QT05 category_name and raw procurement Category Name only.",
    steps: ["Add Material Category after QT03 is visible in Add User Filters.", "Seed it from QT_03_Consumption_Variance.category_name.", "Choose Single Select and retain All.", "Show it on Tabs 1 and 2 only.", "Map manually to the exact material-category column for each compatible object."],
    warning: "Do not map this control to QT04 or raw-sales menu categories.",
  },
  "Canonical UOM": {
    seed: "QT_03_Consumption_Variance.canonical_uom",
    control: "Single-select User Filter; All enabled",
    tabs: "01 Executive Control · 02 Procurement Vendor Consumption",
    defaultValue: "All; expected members kg, litre and pcs",
    mappingRule: "Map only to QT02/QT03/QT05 canonical_uom.",
    steps: ["Add Canonical UOM from QT_03_Consumption_Variance.canonical_uom.", "Choose Single Select and retain All.", "Show it on Tabs 1 and 2 only.", "Map only to canonical_uom in compatible query-table objects.", "Keep totals disabled whenever more than one UOM is visible."],
    warning: "Purchase Unit, Recipe Unit and source_unit are source units, not the governed canonical field.",
  },
  "Risk Domain": {
    seed: "QT_02_Numerical_Risk_Center.subject_type",
    control: "Single-select User Filter; All enabled",
    tabs: "01 Executive Control only",
    defaultValue: "All",
    mappingRule: "Map only to Red Numerical Breaches and RPT_V2_E08_Active_Risk_Load_By_Outlet.",
    steps: ["Add Risk Domain on the Executive tab only.", "Seed it from QT_02_Numerical_Risk_Center.subject_type.", "Choose Single Select and retain All.", "Map it to the two broad-domain objects only.", "Leave fixed INVENTORY/EXPIRY action objects unmapped."],
    warning: "A Raw Material plus a non-INVENTORY Risk Domain can truthfully return no rows.",
  },
  Vendor: {
    seed: "QT_05_Procurement_Control.vendor_name",
    control: "Single-select User Filter; All enabled",
    tabs: "02 Procurement Vendor Consumption only",
    defaultValue: "All",
    mappingRule: "Map to QT05 procurement objects and the raw ordered/received flow KPIs only.",
    steps: ["Add Vendor on Tab 2 only.", "Seed it from QT_05_Procurement_Control.vendor_name.", "Choose Single Select and retain All.", "Map to QT05 vendor_name, RAW_Enterprise_Purchase_Order.Vendor Name or RAW_Purchase_Detail.Vendor Name as listed.", "Leave sales, risk, profitability and consumption reports unmapped."],
    warning: "Vendor is intentionally absent from Executive and Sales & Menu Economics.",
  },
};

export interface DashboardObjectBuildGuide {
  visual: string;
  status: string;
  shelves?: string[];
  formatting: string[];
  acceptance: string;
  noData: string;
}

const objectGuides: Record<string, DashboardObjectBuildGuide> = {
  "Net Sales": { visual: "KPI Widget", status: "Existing widget 333330000004501758", formatting: ["Currency: INR, 2 decimals"], acceptance: "Month 1, all outlets: INR 1,945,189.00 from 4,855 sales rows.", noData: "The selected physical period/outlet/menu scope has no sales rows." },
  "Theoretical Gross Margin": { visual: "KPI Widget", status: "Existing widget 333330000004505038", formatting: ["Currency: INR, 2 decimals"], acceptance: "Month 1, all outlets: INR 1,600,209.12 from 4,855 complete-recipe-cost sales rows.", noData: "The selected menu scope has no complete recipe-cost row." },
  "Theoretical Gross Margin %": { visual: "KPI Widget", status: "Create new", formatting: ["Percentage, 2 decimals", "Use Aggregate Formula as Actual"], acceptance: "82.264969%; ratio of INR 1,600,209.12 to INR 1,945,189.00.", noData: "No complete recipe-cost row or net sales is zero." },
  "Open PO Liability": { visual: "KPI Widget", status: "Repair existing widget 333330000004506025", formatting: ["Currency: INR, 2 decimals", "GroupBy/Data Column: None"], acceptance: "31 Jan 2026: INR 202,722.30 across 54 open lines and 30 POs.", noData: "No eligible open-PO row exists in the selected compatible scope." },
  "Outlets With Inventory Risk": { visual: "KPI Widget", status: "Locate by visible title", formatting: ["Whole number"], acceptance: "31 Jan 2026: 3 outlets across six eligible inventory subjects.", noData: "No active inventory-risk evidence exists in the selected compatible scope." },
  "Critical Inventory Risk Subjects": { visual: "KPI Widget", status: "Rename the existing Raw Material Stockouts card", formatting: ["Whole number", "Red #D32F2F for Month 1"], acceptance: "31 Jan 2026: 6 Red and 0 Amber subjects; never call these Purple stockouts.", noData: "No Red/Amber inventory subject exists in the selected compatible scope." },
  "Red Numerical Breaches": { visual: "KPI Widget", status: "Create new", formatting: ["Whole number", "Red #D32F2F"], acceptance: "31 Jan 2026: 315 distinct Red evaluation rows.", noData: "No Red evaluation exists for the selected compatible scope." },
  "Shortage by Canonical UOM": { visual: "KPI Widget with GroupBy/Data Column", status: "Rebuild the incorrectly totalled Projected Shortage by UOM widget", shelves: ["Data column: base_shortage_qty · Sum", "GroupBy/Data Column: canonical_uom", "Grand total: Off"], formatting: ["4 decimals", "Never combine kg, litre and pcs"], acceptance: "31 Jan 2026: 13.600600 kg; 21.392200 litre; 359.844000 pcs.", noData: "The selected material/UOM/outlet has no shortage; do not replace it with a cross-UOM total." },
  "RPT_V2_E06_Daily_Net_Sales_By_Outlet": { visual: "Line chart", status: "Existing view 333330000004500166", shelves: ["X: Date · exact Date grain", "Y: AF_Flow_Net_Sales · Actual", "Color: Store Name"], formatting: ["INR Y-axis", "Markers and data labels off"], acceptance: "93 date/outlet points; period total INR 1,945,189.00.", noData: "No sales exist for the selected physical flow scope." },
  "RPT_V2_E08_Active_Risk_Load_By_Outlet": { visual: "Stacked horizontal bar", status: "Existing view 333330000004476016", shelves: ["Category: outlet_name", "Value: subject_id · Distinct Count", "Color: subject_type"], formatting: ["Use governed domain colors", "Do not add a rank-range filter"], acceptance: "12 outlet/domain segments from 334 eligible evaluations.", noData: "A contradictory Raw Material and non-INVENTORY Risk Domain selection may truthfully return no rows." },
  "RPT_V2_R08A_Provisional_Synthetic_Expiry_Top10_By_Exposure": { visual: "Compact Summary View", status: "Approved view 333330000004480190", shelves: ["Rows: as_of_date, source_snapshot_date, risk_color, outlet_name, item_name, batch_number, expiry_date, source_unit, data_status", "Data: MIN(days_to_expiry), MAX(batch_remaining_qty), MAX(monetary_exposure)", "Subtotals and grand total: Off"], formatting: ["Signed whole days: Days Remaining (+) / Overdue (-)", "Batch quantity: 4 decimals with source unit", "Exposure: INR", "Visible disclosure: PROVISIONAL SYNTHETIC EXPIRY DEMONSTRATION - NOT POSIST ACTUALS"], acceptance: "Filtered 31 Jan export: 10 distinct highest-exposure provisional batches.", noData: "No eligible provisional expiry batch exists for the selected snapshot and compatible scope." },
  "RPT_V2_R08B_7_Day_Inventory_Shortage_Action_Table": { visual: "Compact Summary View", status: "Approved view 333330000004528076", shelves: ["Rows: as_of_date, source_snapshot_date, risk_color, outlet_name, item_name, canonical_uom", "Data: MAX(current_stock_qty), MAX(forecast_required_qty), MAX(valid_open_po_qty), MAX(available_qty), MAX(shortage_qty), MAX(monetary_exposure)", "Subtotals and grand total: Off"], formatting: ["Quantities: 4 decimals with visible canonical UOM", "Exposure: INR", "Keep risk_color visible"], acceptance: "31 Jan: all 6 positive shortages; 10 Feb: all 3 valid shortages with the source snapshot visible.", noData: "No Purple/Red positive seven-day shortage exists in the selected compatible scope." },
  "Ordered Value": { visual: "KPI Widget", status: "Rename/move existing widget 333330000004507371", formatting: ["Currency: INR, 2 decimals"], acceptance: "Month 1: INR 1,469,567.50 across 224 PO lines and 33 POs.", noData: "No orders exist in the selected physical flow scope." },
  "Received Value": { visual: "KPI Widget", status: "Create new", formatting: ["Currency: INR, 2 decimals", "Use AF_Flow_Purchase_Value as Actual"], acceptance: "Month 1: INR 1,074,670.41 across 177 receipt lines.", noData: "No receipts exist in the selected physical flow scope." },
  "Pending Open PO Liability": { visual: "KPI Widget", status: "Duplicate the governed Open PO component", formatting: ["Currency: INR, 2 decimals"], acceptance: "31 Jan 2026: INR 202,722.30 across 54 open lines and 30 POs.", noData: "No eligible open-PO row exists for the selected snapshot scope." },
  "Delayed Open PO Liability": { visual: "KPI Widget", status: "Create new", formatting: ["Currency: INR, 2 decimals"], acceptance: "31 Jan 2026: INR 177,161.97 across 47 overdue lines and 27 POs.", noData: "The selected scope has open POs but none with overdue_days greater than zero." },
  "Closing Inventory Value": { visual: "KPI Widget", status: "Create new", formatting: ["Currency: INR, 2 decimals"], acceptance: "31 Jan 2026: INR 1,460,065.92 across 129 inventory rows.", noData: "The selected material/outlet does not exist at the selected snapshot." },
  "Positive Consumption Leakage": { visual: "KPI Widget", status: "Create new", formatting: ["Currency: INR, 2 decimals", "Use Aggregate Formula as Actual"], acceptance: "Month 1: INR 10,868.09 across 120 positive rows and 42 ingredients.", noData: "No positive leakage exists in the selected compatible scope." },
  "RPT_V2_P05_Vendor_Exposure": { visual: "Stacked horizontal bar", status: "Existing view 333330000004476045", shelves: ["Category: vendor_name", "Value: SUM(open_po_liability_pre_tax)", "Color: risk_color"], formatting: ["Amber #F9A825", "Red #D32F2F", "Currency: INR"], acceptance: "Top 8 vendors from 54 lines; total INR 202,722.30.", noData: "The selected vendor/material/category/UOM has no open PO at that snapshot." },
  Open_Liability_Flow: { visual: "Sankey", status: "Use approved view 333330000004501018; not fallback 333330000004478059", shelves: ["Path: vendor_name → category_name → outlet_name", "Weight: SUM(open_po_liability_pre_tax)"], formatting: ["Use neutral procurement colors", "Keep the flow readable; if limited to two levels use Vendor → Category and keep Outlet in tooltip/filter"], acceptance: "22 Vendor/Category/Outlet paths; total INR 202,722.30.", noData: "No open-liability path exists in the selected compatible scope." },
  "RPT_V2_P07A_Top_Unit_Price_Movement_Action_Table": { visual: "Summary View", status: "Approved view 333330000004528030", shelves: ["Rows: movement_direction, item_name, vendor_name, outlet_name, purchase_uom, current_date, source_transaction_number", "Data: MAX(previous_unit_price), MAX(current_unit_price), MAX(unit_price_change_pct)"], formatting: ["INR per source UOM", "Percentage: 2 decimals", "Keep movement_direction visible"], acceptance: "Exactly 10 unique receipt events; all 177 receipt unit prices reconcile to Purchase Amount / Purchase Quantity within tolerance.", noData: "Fewer than two dated observations exist for the selected Item + Vendor + UOM group." },
  "RPT_V2_S08_Ingredient_Leakage_Top10": { visual: "One-series horizontal stacked bar", status: "Approved view 333330000004480039", shelves: ["Category: ingredient_name", "Value: SUM(consumption_leakage_value)", "Tooltip: canonical_uom", "Color: none"], formatting: ["Gold #B8872B", "Currency: INR", "Label: Positive Consumption Variance Value"], acceptance: "10 unique ingredients; Top-10 INR 7,745.49; full eligible INR 10,868.09.", noData: "No positive consumption variance value exists in the selected scope." },
  "RPT_V2_P08_Delivery_Breach_Action_Top10": { visual: "Compact Summary View", status: "Approved view 333330000004476262", shelves: ["Rows: risk_color, vendor_name, po_number, outlet_name, item_name, expected_delivery_date", "Data: MAX(overdue_days), MAX(open_po_liability_pre_tax)", "Subtotals: Off"], formatting: ["Keep risk_color visible", "Liability: INR", "Label: Expected delivery breach evidence - not OTIF"], acceptance: "Exactly 10 action rows; full overdue population is 47 lines / 27 POs / INR 177,161.97.", noData: "No overdue PO line exists in the selected snapshot/vendor/material/outlet scope." },
  "RPT_V2_S06_Category_Economics": { visual: "Horizontal stacked bar", status: "Approved view 333330000004476081", shelves: ["Category: category_name", "Values: SUM(theoretical_cogs), SUM(menu_gross_margin)", "Tooltip: AF_Flow_Theoretical_Gross_Margin_Pct · Actual"], formatting: ["COGS Blue #2F6B9A", "Gross Margin Teal #2A7F84", "Values: INR; tooltip: Percentage"], acceptance: "Every category satisfies Theoretical COGS + Theoretical Gross Margin = Net Sales.", noData: "The selected menu scope has no complete recipe-cost row." },
  "RPT_V2_S07B_Top_12_Menu_Items_By_Net_Sales": { visual: "Horizontal bar", status: "Approved immutable view 333330000004478284", shelves: ["Category: menu_item_name", "Value: SUM(net_sales_value)", "Tooltips: SUM(sold_menu_qty), AF_Flow_Theoretical_Gross_Margin_Pct · Actual"], formatting: ["Navy #17324D", "Net Sales: INR", "Quantity: Number; margin: Percentage"], acceptance: "Exactly 12 descending menu-item bars; the first bar is the highest Net Sales item in the same scope.", noData: "No complete recipe-cost menu sale exists in the selected scope." },
  "RPT_V2_S10A_Source_Net_Margin_Heatmap": { visual: "Heat map", status: "Approved view 333330000004528053", shelves: ["X: outlet_name", "Y: category_name", "Color: SUM(source_net_margin_value)", "Hover: SUM(net_sales_value), SUM(source_reported_purchase_value)"], formatting: ["Scale #EAF2F8 → #8CB9D9 → #17324D", "Axis titles: Outlet, Menu Category", "Color title: Source Net Margin (INR)"], acceptance: "54 cells = 3 outlets × 18 categories; source net margin INR 1,594,123.48.", noData: "No sales row exists in the selected physical flow scope." },
  "RPT_V2_S09_Menu_Item_Raw_Material_Map": { visual: "Pivot", status: "Reuse existing view 333330000004473123", shelves: ["Rows: Item Name, Ingredient Name, Recipe Unit", "Data: Qty · Sum", "Grand totals and subtotals: Off"], formatting: ["Headings: Menu Item, Raw Material, Recipe Source UOM, Recipe Quantity", "Sort Menu Item then Raw Material ascending"], acceptance: "723 current recipe relationships across 110 menu items and 42 ingredients; no Top-N.", noData: "The selected pair is not a current recipe relationship; no historical recipe version is available." },
};

export function dashboardObjectBuildGuide(object: DashboardObject): DashboardObjectBuildGuide {
  return objectGuides[object.name] ?? {
    visual: object.kind === "KPI" ? "KPI Widget" : object.kind,
    status: "Create or verify by the exact visible object name",
    formatting: [],
    acceptance: "Reconcile the filtered object to its governed underlying rows.",
    noData: "No eligible rows exist for the selected compatible scope.",
  };
}

export interface DashboardTabBuildGuide {
  filters: string[];
  rows: string[];
  steps: string[];
}

export const dashboardTabBuildGuides: Record<string, DashboardTabBuildGuide> = {
  executive: {
    filters: ["Row 1 · Reporting Period · Snapshot As Of · Outlet · Menu Item · Menu Category", "Row 2 · Raw Material · Material Category · Canonical UOM · Risk Domain"],
    rows: ["KPI row 1 · Net Sales · Theoretical Gross Margin · Theoretical Gross Margin % · Open PO Liability · 25% each", "KPI row 2 · Outlets With Inventory Risk · Critical Inventory Risk Subjects · Red Numerical Breaches · Shortage by Canonical UOM · 25% each", "Visual row · RPT_V2_E06_Daily_Net_Sales_By_Outlet 60% · RPT_V2_E08_Active_Risk_Load_By_Outlet 40%", "Evidence rows · RPT_V2_R08A_Provisional_Synthetic_Expiry_Top10_By_Exposure 100% · RPT_V2_R08B_7_Day_Inventory_Shortage_Action_Table 100%"],
    steps: ["Open DB_02_ABNAH_SCM_Control_Tower_Final in Edit Design.", "Create or rename this tab exactly 01 Executive Control.", "Place the two filter rows in the listed left-to-right order.", "Place the two four-card KPI rows, then the 60/40 visual row.", "Place R08A and R08B full width so the action columns remain readable.", "Map each filter per object; save, enter View Mode and run the Month-1 acceptance checks."],
  },
  procurement: {
    filters: ["Row 1 · Reporting Period · Snapshot As Of · Outlet · Menu Item · Menu Category", "Row 2 · Raw Material · Material Category · Canonical UOM · Vendor"],
    rows: ["KPI row 1 · Ordered Value · Received Value · Pending Open PO Liability · 33.3% each", "KPI row 2 · Delayed Open PO Liability · Closing Inventory Value · Positive Consumption Leakage · 33.3% each", "Visual row · RPT_V2_P05_Vendor_Exposure 50% · Open_Liability_Flow 50%", "Visual row · RPT_V2_S08_Ingredient_Leakage_Top10 100%", "Evidence rows · RPT_V2_P08_Delivery_Breach_Action_Top10 100% · RPT_V2_P07A_Top_Unit_Price_Movement_Action_Table 100%"],
    steps: ["Create or rename this tab exactly 02 Procurement Vendor Consumption.", "Place the two filter rows and add Vendor only here.", "Place the two three-card KPI rows.", "Place Vendor Exposure and the approved Sankey side by side.", "Keep leakage and both action tables full width; price movement may sit below the initial viewport.", "Map flow dates and snapshot dates independently, then reconcile ordered, received, pending and overdue values."],
  },
  sales: {
    filters: ["One row · Reporting Period · Outlet · Menu Item · Menu Category · Raw Material"],
    rows: ["Visual row · RPT_V2_S06_Category_Economics 40% · RPT_V2_S07B_Top_12_Menu_Items_By_Net_Sales 60%", "Visual row · RPT_V2_S10A_Source_Net_Margin_Heatmap 100%", "Evidence row · RPT_V2_S09_Menu_Item_Raw_Material_Map 100%"],
    steps: ["Create or rename this tab exactly 03 Sales & Menu Economics.", "Place its one readable filter row.", "Place Category Economics and Top 12 Menu Items in a 40/60 row.", "Place the source-margin heatmap full width.", "Keep the current-recipe map full width below the heatmap.", "Do not add Snapshot As Of, Material Category, Canonical UOM, Risk Domain or Vendor to this tab."],
  },
};

export const forecastProductBuildGuides = {
  deterministic: {
    entities: [
      "QT_01A_Menu_Forecast · menu quantity by future day",
      "QT_01_Demand_Requirement · recipe-expanded ingredient quantity",
      "QT_02A_Risk_Base_Evidence · next-day and seven-day requirement, shortage and exposure",
      "QT_02_Numerical_Risk_Center · final filterable action evidence",
    ],
    steps: [
      "Build or refresh QT_01A_Menu_Forecast from the exact SQL in position 01.",
      "Confirm same-weekday observations use the prior four weeks and the fallback uses the trailing 14 observed days.",
      "Refresh QT_01_Demand_Requirement, then QT_02A_Risk_Base_Evidence, then QT_02_Numerical_Risk_Center.",
      "Use the resulting physical columns in R08A/R08B; do not reproduce the forecast in a dashboard formula.",
    ],
  },
  native: {
    entities: [
      "NEW_RPT_FC04R_PVT_Daily_Net_Sales_Forecast_7D · Rows sales_date · Data SUM(net_sales_value)",
      "NEW_RPT_FC04_PVT_Category_Net_Sales_Forecast_7D · Rows sales_date · Columns category_name · Data SUM(net_sales_value)",
      "NEW_RPT_FC05_PVT_Category_Theoretical_Gross_Margin_Forecast_7D · Rows sales_date · Columns category_name · Data SUM(menu_gross_margin)",
      "NEW_RPT_FC06_PVT_Daily_Menu_Quantity_Forecast_7D · Rows sales_date · Columns category_name · Data SUM(sold_menu_qty)",
    ],
    steps: [
      "Create each Pivot from QT_04_Menu_Profitability and save it with the complete NEW_RPT name shown above.",
      "Keep sales_date at exact daily grain; use category_name only for the three category-series pivots.",
      "On FC05 add cost_evaluation_status_code = COMPLETE_RECIPE_COST; the other three have no recipe-completeness fixed filter.",
      "Open Analysis > Forecast, choose Automatic, set 7 daily periods, Ignore Last 0 and confidence bands off, then save.",
      "Map Reporting Period to sales_date and compatible menu/outlet controls only; never map Snapshot As Of, material, UOM or Vendor.",
      "Reopen and verify 31 Actual rows followed by 7 Forecast rows; native forecast output is report-layer evidence and does not feed shortage SQL.",
    ],
  },
  automl: {
    entities: [
      "Training/scoring feature table · date × outlet × menu item",
      "Accepted physical prediction table · model version, cutoff, forecast date, prediction and confidence metadata",
      "QT_01-compatible view · deterministic fallback preserved",
    ],
    steps: [
      "Materialize complete historical features and known-at-cutoff weather/calendar inputs.",
      "Train chronologically and validate against the deterministic baseline with future holdouts.",
      "Accept only a physical prediction output with model/run metadata and completeness flags.",
      "Join accepted predictions through the same recipe/UOM/stock/PO route; otherwise retain the deterministic fallback and label it.",
    ],
  },
} as const;
