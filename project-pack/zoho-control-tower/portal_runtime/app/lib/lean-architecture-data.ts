export type JourneyStageId =
  | "inputs"
  | "controls"
  | "model"
  | "calculations"
  | "forecasting"
  | "outputs"
  | "filters";

export interface QueryTableJourney {
  order: number;
  name: string;
  sqlFile: string;
  level: 1 | 2 | 3;
  dependencies: string[];
  grain: string;
  dateField: string;
  purpose: string;
  derived: string[];
  feeds: string[];
}

export const journeyStages: Array<{
  id: JourneyStageId;
  number: string;
  label: string;
  summary: string;
  count: string;
}> = [
  { id: "inputs", number: "01", label: "Source inputs", summary: "POSIST-shaped operational, reference and provisional evidence", count: "26 tables" },
  { id: "controls", number: "02", label: "Governed controls", summary: "Editable rules, date spine, units and snapshot readiness", count: "5 controls" },
  { id: "model", number: "03", label: "Lean model", summary: "Three dependency levels, built in a fixed order", count: "10 queries" },
  { id: "calculations", number: "04", label: "Calculations", summary: "Row-level SQL logic plus filter-safe aggregate measures", count: "14 metrics" },
  { id: "forecasting", number: "05", label: "Forecasting", summary: "Transparent action forecast and Zoho-native comparisons", count: "3 products" },
  { id: "outputs", number: "06", label: "Decision outputs", summary: "A concise KPI and report layer across three dashboard tabs", count: "27 objects" },
  { id: "filters", number: "07", label: "Filter contract", summary: "Exact field mappings keep flow and state questions separate", count: "10 controls" },
];

export const sourceGroups = [
  {
    id: "operational",
    label: "Operational inputs",
    summary: "Physical sales, stock, procurement, receipt, return, movement and period evidence.",
    items: [
      "RAW_Bill_Item_Detail",
      "RAW_Bulk_Return",
      "RAW_Closing_Stock",
      "RAW_Enterprise_Consumption_Detail",
      "RAW_Enterprise_Entry",
      "RAW_Enterprise_Opening",
      "RAW_Enterprise_Physical",
      "RAW_Enterprise_Purchase_Order",
      "RAW_Enterprise_Stock_Return",
      "RAW_Enterprise_Transfer_From",
      "RAW_Enterprise_Transfer_To",
      "RAW_Enterprise_Variance_Master",
      "RAW_Enterprise_Variance_Normal",
      "RAW_Enterprise_Wastage_Normal",
      "RAW_Gross_Net_Margin",
      "RAW_Purchase_Detail",
      "RAW_Recipe_Consumption",
      "RAW_Stock_In_Stock_Out",
    ],
  },
  {
    id: "reference",
    label: "Reference masters",
    summary: "Current recipe and vendor identity used to translate business events.",
    items: ["REF_Item_Recipe", "REF_Vendor"],
  },
  {
    id: "provisional",
    label: "Provisional demonstration",
    summary: "A separately labelled expiry input used only until the POSIST expiry export is enabled.",
    items: ["SYN_Provisional_Expiry_Report"],
  },
] as const;

export const controlTables = [
  {
    name: "CTL_Rule_Parameters",
    role: "Business rules",
    changes: "Forecast windows, safety factor, expiry and PO timing thresholds, value basis and engineering tolerances.",
    effect: "Query Tables select the active effective-dated row; changing an approved value changes the next model refresh without rewriting report formulas.",
    examples: ["forecast_history_weeks = 4", "forecast_horizon_days = 7", "forecast_fallback_days = 14", "inventory_safety_factor = 1.15"],
  },
  {
    name: "CTL_Calendar",
    role: "Date spine",
    changes: "Operational dates, weekdays, week starts, month ends and forecast-extension dates.",
    effect: "Generates every as-of and target date needed for daily state, same-weekday history and future horizons.",
    examples: ["calendar_date", "day_name", "is_month_end", "is_forecast_extension"],
  },
  {
    name: "CTL_UOM_Conversions",
    role: "Comparable quantity",
    changes: "Approved kg, litre and piece identities plus mathematical gram/millilitre conversions.",
    effect: "Recipe, stock, PO and consumption quantities meet only after an approved source-to-canonical conversion.",
    examples: ["g -> kg × 0.001", "ml -> litre × 0.001", "piece -> pcs"],
  },
  {
    name: "CTL_Expiry_Assumptions",
    role: "Provisional shelf life",
    changes: "Category-level shelf-life days for the clearly disclosed expiry demonstration.",
    effect: "Supports demo expiry bands only; it never converts provisional expiry into observed POSIST truth.",
    examples: ["Dairy = 7 days", "Produce = 5 days", "Packaging = 365 days"],
  },
  {
    name: "CTL_Snapshot_Status",
    role: "Publication readiness",
    changes: "Daily source-completeness flags and the latest complete snapshot selector.",
    effect: "Prevents an incomplete daily load from being presented as the current operational state.",
    examples: ["core_complete_flag", "latest_valid_flag", "inventory_snapshot_date", "load_id"],
  },
] as const;

export const queryTables: QueryTableJourney[] = [
  {
    order: 1,
    name: "QT_01A_Menu_Forecast",
    sqlFile: "01a_menu_forecast.sql",
    level: 1,
    dependencies: ["RAW_Bill_Item_Detail", "CTL_Calendar", "CTL_Rule_Parameters"],
    grain: "as_of_date × outlet × forecast_date × menu item",
    dateField: "as_of_date",
    purpose: "Aggregate daily menu sales early and produce an explainable forward menu-quantity forecast.",
    derived: ["forecast_menu_qty_daily", "forecast_net_sales_daily", "forecast_method_code", "same_weekday_observation_count"],
    feeds: ["QT_01_Demand_Requirement", "QT_02A_Risk_Base_Evidence", "QT_02_Numerical_Risk_Center"],
  },
  {
    order: 2,
    name: "QT_03_Consumption_Variance",
    sqlFile: "03_consumption_variance_month1_corrected.sql",
    level: 1,
    dependencies: ["RAW_Enterprise_Consumption_Detail", "RAW_Enterprise_Variance_Normal", "RAW_Bill_Item_Detail", "REF_Item_Recipe", "CTL_UOM_Conversions", "CTL_Rule_Parameters"],
    grain: "period end × outlet × store × ingredient",
    dateField: "reporting_period_end",
    purpose: "Reconcile the observed stock bridge with recipe-derived theoretical ingredient consumption.",
    derived: ["actual_consumption_qty", "theoretical_consumption_qty", "consumption_variance_qty", "consumption_leakage_value"],
    feeds: ["Consumption leakage KPI", "Ingredient leakage Top 10", "DQ checks"],
  },
  {
    order: 3,
    name: "QT_04_Menu_Profitability",
    sqlFile: "04_menu_profitability.sql",
    level: 1,
    dependencies: ["RAW_Gross_Net_Margin", "REF_Item_Recipe", "RAW_Enterprise_Variance_Normal", "CTL_UOM_Conversions", "CTL_Rule_Parameters"],
    grain: "sales date × outlet × menu item",
    dateField: "sales_date",
    purpose: "Combine recognized sales with recipe and ingredient cost evidence for theoretical menu economics.",
    derived: ["theoretical_cogs", "menu_gross_margin", "source_net_margin_value", "cost_evaluation_status_code"],
    feeds: ["Executive margin KPIs", "Category economics", "Menu rankings", "Native forecasts"],
  },
  {
    order: 4,
    name: "QT_05A_Receipt_Return_As_Of",
    sqlFile: "05a_receipt_return_as_of.sql",
    level: 1,
    dependencies: ["RAW_Enterprise_Entry", "RAW_Enterprise_Stock_Return", "REF_Vendor", "CTL_Calendar", "CTL_UOM_Conversions", "CTL_Rule_Parameters"],
    grain: "record type × as-of date × source row",
    dateField: "as_of_date",
    purpose: "Materialize receipt cohorts and the returns observed through each exact as-of date.",
    derived: ["eligible_received_qty_canonical", "observed_return_qty_canonical", "observed_vendor_return_rate", "return_link_status"],
    feeds: ["QT_05_Procurement_Control"],
  },
  {
    order: 5,
    name: "QT_06A_Return_DQ",
    sqlFile: "06a_return_dq.sql",
    level: 1,
    dependencies: ["RAW_Enterprise_Stock_Return", "RAW_Bulk_Return", "RAW_Enterprise_Entry", "CTL_Rule_Parameters"],
    grain: "one exception occurrence",
    dateField: "exception_date",
    purpose: "Detect return linkage, quantity, amount and cross-report reconciliation exceptions once.",
    derived: ["exception_id", "rule_code", "gap_value", "evaluation_status"],
    feeds: ["QT_06_Data_Quality_Exceptions"],
  },
  {
    order: 6,
    name: "QT_01_Demand_Requirement",
    sqlFile: "01_demand_requirement.sql",
    level: 2,
    dependencies: ["QT_01A_Menu_Forecast", "REF_Item_Recipe", "CTL_UOM_Conversions"],
    grain: "as-of date × outlet × target date × menu item × ingredient",
    dateField: "as_of_date",
    purpose: "Expand forecast menu units through recipes and approved UOM conversions into ingredient demand.",
    derived: ["recipe_qty_canonical_per_menu_unit", "forecast_ingredient_qty_daily", "uom_mapping_status"],
    feeds: ["QT_02A_Risk_Base_Evidence", "Demand drill-through"],
  },
  {
    order: 7,
    name: "QT_05_Procurement_Control",
    sqlFile: "05_procurement_control.sql",
    level: 2,
    dependencies: ["QT_05A_Receipt_Return_As_Of", "RAW_Enterprise_Purchase_Order", "RAW_Enterprise_Entry", "RAW_Enterprise_Stock_Return", "REF_Vendor", "CTL_Calendar", "CTL_UOM_Conversions", "CTL_Rule_Parameters", "CTL_Snapshot_Status"],
    grain: "record type × as-of date × source row",
    dateField: "as_of_date",
    purpose: "Unify PO lifecycle, receipt, return, timing severity and snapshot evidence without mixing line quantities.",
    derived: ["remaining_qty_canonical", "open_po_liability_pre_tax", "overdue_days", "risk_color"],
    feeds: ["Open PO KPIs", "Vendor exposure", "Liability flow", "Delivery breach action"],
  },
  {
    order: 8,
    name: "QT_02A_Risk_Base_Evidence",
    sqlFile: "02a_risk_base_evidence.sql",
    level: 2,
    dependencies: ["QT_01A_Menu_Forecast", "RAW_Closing_Stock", "RAW_Enterprise_Purchase_Order", "SYN_Provisional_Expiry_Report", "REF_Item_Recipe", "CTL_Calendar", "CTL_UOM_Conversions", "CTL_Rule_Parameters"],
    grain: "as-of date × evaluation",
    dateField: "as_of_date",
    purpose: "Place inventory, provisional expiry, menu impact and open-PO timing on one numerical evidence contract.",
    derived: ["next_day_required_qty", "forecast_required_qty", "shortage_qty", "monetary_exposure", "risk_priority_rank"],
    feeds: ["QT_02_Numerical_Risk_Center"],
  },
  {
    order: 9,
    name: "QT_06_Data_Quality_Exceptions",
    sqlFile: "06_data_quality_exceptions.sql",
    level: 2,
    dependencies: ["QT_01A_Menu_Forecast", "QT_06A_Return_DQ", "RAW_Closing_Stock", "RAW_Enterprise_Entry", "RAW_Enterprise_Purchase_Order", "RAW_Gross_Net_Margin", "REF_Item_Recipe", "REF_Vendor", "SYN_Provisional_Expiry_Report", "CTL_UOM_Conversions", "CTL_Rule_Parameters"],
    grain: "one governed exception occurrence",
    dateField: "exception_date",
    purpose: "Publish dated operational exceptions and explicitly undated static-reference exceptions in one register.",
    derived: ["exception_id", "date_provenance", "eligible_denominator", "exception_flag"],
    feeds: ["DQ KPIs", "DQ exception register"],
  },
  {
    order: 10,
    name: "QT_02_Numerical_Risk_Center",
    sqlFile: "02_numerical_risk_center.sql",
    level: 3,
    dependencies: ["QT_02A_Risk_Base_Evidence", "QT_01A_Menu_Forecast", "REF_Item_Recipe", "CTL_UOM_Conversions", "CTL_Snapshot_Status"],
    grain: "as-of date × evaluation",
    dateField: "as_of_date",
    purpose: "Publish the final daily action evidence with Purple-first numeric ordering and snapshot completeness.",
    derived: ["subject_id", "base_shortage_qty", "overall_priority_rank", "snapshot_selector"],
    feeds: ["Executive risk KPIs", "Expiry action", "Inventory shortage action", "Risk load"],
  },
];

export const calculationFamilies = [
  {
    id: "forecast",
    label: "Demand and recipe",
    base: "QT_01A → QT_01",
    formula: "forecast menu units × recipe quantity × approved UOM multiplier",
    result: "Daily ingredient requirement by outlet, menu item and target date.",
  },
  {
    id: "risk",
    label: "Inventory action",
    base: "QT_02A → QT_02",
    formula: "max(0, requirement − current stock − qualifying PO supply)",
    result: "Tomorrow and seven-day shortage, valued using closing-stock average unit cost.",
  },
  {
    id: "margin",
    label: "Menu economics",
    base: "QT_04",
    formula: "theoretical gross margin = net sales − recipe-derived theoretical COGS",
    result: "Filter-safe additive margin values and ratio-of-sums percentages.",
  },
  {
    id: "procurement",
    label: "Procurement state",
    base: "QT_05A → QT_05",
    formula: "open liability = remaining canonical quantity × normalized pre-tax unit price",
    result: "Pending and overdue exposure at exact PO-line and as-of-date grain.",
  },
  {
    id: "consumption",
    label: "Consumption variance",
    base: "QT_03",
    formula: "actual stock-bridge consumption − recipe-derived theoretical consumption",
    result: "Quantity variance and positive leakage value without treating negative variance as savings.",
  },
] as const;

export const activeAggregateMetrics = [
  ["AF_Flow_Purchase_Value", "RAW_Purchase_Detail", "SUM(Purchase Amount)", "Received value"],
  ["AF_Flow_Weighted_Purchase_Unit_Price", "RAW_Purchase_Detail", "SUM(Purchase Amount) / SUM(Purchase Quantity)", "Comparable unit price"],
  ["AF_Flow_Net_Sales", "RAW_Gross_Net_Margin", "SUM(Net Sale Value)", "Recognized net sales"],
  ["AF_Flow_Quantity_Sold", "RAW_Gross_Net_Margin", "SUM(Item Qty)", "Sold menu quantity"],
  ["AF_Period_Actual_Consumption_Qty", "QT_03_Consumption_Variance", "SUM(actual_consumption_qty)", "Observed bridge consumption"],
  ["AF_Period_Theoretical_Consumption_Qty", "QT_03_Consumption_Variance", "SUM(theoretical_consumption_qty)", "Recipe-derived consumption"],
  ["AF_Period_Consumption_Variance_Qty", "QT_03_Consumption_Variance", "SUM(consumption_variance_qty)", "Actual minus theoretical"],
  ["AF_Period_Positive_Leakage_Value", "QT_03_Consumption_Variance", "SUM(consumption_leakage_value)", "Positive valued variance"],
  ["AF_Period_Consumption_Variance_Pct", "QT_03_Consumption_Variance", "SUM(variance) / SUM(theoretical)", "Ratio of sums"],
  ["AF_Flow_Theoretical_COGS", "QT_04_Menu_Profitability", "SUM(theoretical_cogs)", "Recipe cost of sold items"],
  ["AF_Flow_Theoretical_Gross_Margin", "QT_04_Menu_Profitability", "SUM(menu_gross_margin)", "Sales minus theoretical COGS"],
  ["AF_Flow_Theoretical_Gross_Margin_Pct", "QT_04_Menu_Profitability", "SUM(menu_gross_margin) / SUM(net_sales_value)", "Ratio of sums; never sum row percentages"],
  ["AF_DQ_Exception_Count", "QT_06_Data_Quality_Exceptions", "DISTINCTCOUNT(exception_id)", "Evaluated exceptions"],
  ["AF_DQ_Affected_Subject_Count", "QT_06_Data_Quality_Exceptions", "DISTINCTCOUNT(source table + row key)", "Affected source records"],
] as const;

export const forecastProducts = [
  {
    id: "deterministic",
    label: "Operational demand baseline",
    state: "Live · reusable rows",
    question: "What menu and ingredient demand is expected tomorrow and through the governed seven-day horizon?",
    method: "Use the average of the same weekday in the prior four weeks when at least two observations exist; otherwise use the observed-day average from the trailing 14 days.",
    route: "RAW_Bill_Item_Detail → QT_01A → QT_01 → QT_02A → QT_02",
    boundary: "This transparent forecast drives the current expiry-pressure and inventory-shortage action tables.",
  },
  {
    id: "native",
    label: "Zoho-native forecast",
    state: "Live · report layer",
    question: "What do the next seven daily periods look like for sales, theoretical margin value and total expected menu units?",
    method: "Zoho Forecast on the full daily sales_date series: FC04 net sales, FC05 theoretical gross margin value and FC06 sold menu quantity.",
    route: "QT_04 actual daily series → Zoho native Forecast → seven displayed future periods",
    boundary: "Native future points are transient report output. They cannot be joined back into Query Tables or multiplied through recipes.",
  },
  {
    id: "automl",
    label: "Materialized AutoML path",
    state: "Designed · acceptance required",
    question: "How can weather-aware menu demand replace the baseline without breaking stock, recipe, PO and audit logic?",
    method: "Chronological regression using menu history, calendar, leakage-safe lags, outlet and weather known at each forecast cutoff.",
    route: "Training/scoring features → Zoho AutoML → physical prediction table → QT_01-compatible view",
    boundary: "Only an accepted physical prediction table can feed a parallel ML action report; missing model/weather inputs fall back to the deterministic baseline and remain labelled.",
  },
] as const;

export const allDashboardFilters = [
  "Reporting Period",
  "Snapshot As Of",
  "Outlet",
  "Menu Item",
  "Menu Category",
  "Raw Material",
  "Material Category",
  "Canonical UOM",
  "Risk Domain",
  "Vendor",
] as const;

type DashboardFilterName = (typeof allDashboardFilters)[number];

export interface DashboardObject {
  name: string;
  kind: "KPI" | "Chart" | "Pivot" | "Action table" | "Flow";
  base: string;
  question: string;
  measure: string;
  fixed: string[];
  mappings: Partial<Record<DashboardFilterName, string>>;
  note?: string;
}

const salesMappings = {
  "Reporting Period": "RAW_Gross_Net_Margin.Date",
  Outlet: "RAW_Gross_Net_Margin.Store Name",
  "Menu Item": "RAW_Gross_Net_Margin.SKU / Item Name",
  "Menu Category": "RAW_Gross_Net_Margin.Category",
} satisfies DashboardObject["mappings"];

const marginMappings = {
  "Reporting Period": "QT_04_Menu_Profitability.sales_date",
  Outlet: "QT_04_Menu_Profitability.outlet_name",
  "Menu Item": "QT_04_Menu_Profitability.menu_item_name",
  "Menu Category": "QT_04_Menu_Profitability.category_name",
} satisfies DashboardObject["mappings"];

const riskMappings = {
  "Snapshot As Of": "QT_02_Numerical_Risk_Center.as_of_date",
  Outlet: "QT_02_Numerical_Risk_Center.outlet_name",
  "Raw Material": "QT_02_Numerical_Risk_Center.item_name",
  "Material Category": "QT_02_Numerical_Risk_Center.category_name",
  "Canonical UOM": "QT_02_Numerical_Risk_Center.canonical_uom",
} satisfies DashboardObject["mappings"];

const riskDomainMappings = {
  ...riskMappings,
  "Risk Domain": "QT_02_Numerical_Risk_Center.subject_type",
} satisfies DashboardObject["mappings"];

const procurementMappings = {
  "Snapshot As Of": "QT_05_Procurement_Control.as_of_date",
  Outlet: "QT_05_Procurement_Control.outlet_name",
  "Raw Material": "QT_05_Procurement_Control.item_name",
  "Material Category": "QT_05_Procurement_Control.category_name",
  "Canonical UOM": "QT_05_Procurement_Control.canonical_uom",
  Vendor: "QT_05_Procurement_Control.vendor_name",
} satisfies DashboardObject["mappings"];

const orderedMappings = {
  "Reporting Period": "RAW_Enterprise_Purchase_Order.PO Date",
  Outlet: "RAW_Enterprise_Purchase_Order.Deployment",
  "Raw Material": "RAW_Enterprise_Purchase_Order.Item Name",
  "Material Category": "RAW_Enterprise_Purchase_Order.Category Name",
  Vendor: "RAW_Enterprise_Purchase_Order.Vendor Name",
} satisfies DashboardObject["mappings"];

const receivedMappings = {
  "Reporting Period": "RAW_Purchase_Detail.Date",
  Outlet: "RAW_Purchase_Detail.Deployment",
  "Raw Material": "RAW_Purchase_Detail.Item Name",
  "Material Category": "RAW_Purchase_Detail.Category Name",
  Vendor: "RAW_Purchase_Detail.Vendor Name",
} satisfies DashboardObject["mappings"];

const consumptionMappings = {
  "Reporting Period": "QT_03_Consumption_Variance.reporting_period_end",
  Outlet: "QT_03_Consumption_Variance.outlet_name",
  "Raw Material": "QT_03_Consumption_Variance.ingredient_name",
  "Material Category": "QT_03_Consumption_Variance.category_name",
  "Canonical UOM": "QT_03_Consumption_Variance.canonical_uom",
} satisfies DashboardObject["mappings"];

const priceMappings = {
  "Reporting Period": "QT_07_Price_Movement.current_date",
  Outlet: "QT_07_Price_Movement.outlet_name",
  "Raw Material": "QT_07_Price_Movement.item_name",
  "Material Category": "QT_07_Price_Movement.category_name",
  Vendor: "QT_07_Price_Movement.vendor_name",
} satisfies DashboardObject["mappings"];

export const dashboardTabs: Array<{
  id: string;
  label: string;
  purpose: string;
  visibleFilters: DashboardFilterName[];
  objects: DashboardObject[];
}> = [
  {
    id: "executive",
    label: "01 Executive Control",
    purpose: "A first-screen answer to sales, margin, current inventory risk, open liability and today's two action queues.",
    visibleFilters: ["Reporting Period", "Snapshot As Of", "Outlet", "Menu Item", "Menu Category", "Raw Material", "Material Category", "Canonical UOM", "Risk Domain"],
    objects: [
      { name: "Net Sales", kind: "KPI", base: "RAW_Gross_Net_Margin", question: "How much recognized net sales flowed in the selected period?", measure: "SUM(Net Sale Value)", fixed: [], mappings: salesMappings },
      { name: "Theoretical Gross Margin", kind: "KPI", base: "QT_04_Menu_Profitability", question: "How much theoretical recipe margin was generated?", measure: "SUM(menu_gross_margin)", fixed: ["cost_evaluation_status_code = COMPLETE_RECIPE_COST"], mappings: marginMappings },
      { name: "Theoretical Gross Margin %", kind: "KPI", base: "QT_04_Menu_Profitability", question: "What share of eligible net sales remains after theoretical recipe cost?", measure: "SUM(menu_gross_margin) / SUM(net_sales_value)", fixed: ["cost_evaluation_status_code = COMPLETE_RECIPE_COST"], mappings: marginMappings, note: "Ratio of sums; never sum or average the row percentage." },
      { name: "Open PO Liability", kind: "KPI", base: "QT_05_Procurement_Control", question: "What pre-tax PO value remains open at the selected snapshot?", measure: "SUM(open_po_liability_pre_tax)", fixed: ["record_type = PO_AS_OF", "remaining_qty_canonical > 0"], mappings: procurementMappings },
      { name: "Outlets With Inventory Risk", kind: "KPI", base: "QT_02_Numerical_Risk_Center", question: "How many outlets have an active inventory risk?", measure: "DISTINCTCOUNT(outlet_name)", fixed: ["subject_type = INVENTORY", "risk_color excludes Green and Grey"], mappings: riskMappings },
      { name: "Critical Inventory Risk Subjects", kind: "KPI", base: "QT_02_Numerical_Risk_Center", question: "How many distinct inventory evaluations are currently critical?", measure: "DISTINCTCOUNT(evaluation_id)", fixed: ["subject_type = INVENTORY", "risk_color = Red"], mappings: riskMappings },
      { name: "Red Numerical Breaches", kind: "KPI", base: "QT_02_Numerical_Risk_Center", question: "How many red numerical evaluations require attention?", measure: "DISTINCTCOUNT(evaluation_id)", fixed: ["risk_color = Red"], mappings: riskDomainMappings },
      { name: "Shortage by Canonical UOM", kind: "KPI", base: "QT_02_Numerical_Risk_Center", question: "How much projected shortage exists in each compatible unit?", measure: "SUM(base_shortage_qty), grouped by canonical_uom", fixed: ["subject_type = INVENTORY", "risk_color = Red", "grand total off"], mappings: riskMappings, note: "kg, litre and pcs are never added into one total." },
      { name: "RPT_V2_E06_Daily_Net_Sales_By_Outlet", kind: "Chart", base: "RAW_Gross_Net_Margin", question: "How did recognized sales move each day by outlet?", measure: "Date × AF_Flow_Net_Sales; color Store Name", fixed: [], mappings: salesMappings },
      { name: "RPT_V2_E08_Active_Risk_Load_By_Outlet", kind: "Chart", base: "QT_02_Numerical_Risk_Center", question: "Which outlets carry the most active risk, split by domain?", measure: "DISTINCTCOUNT(subject_id) by outlet and subject_type", fixed: ["risk_color excludes Green and Grey"], mappings: riskDomainMappings },
      { name: "RPT_V2_R08A_Provisional_Synthetic_Expiry_Top10_By_Exposure", kind: "Action table", base: "QT_02_Numerical_Risk_Center", question: "Which provisional expiry batches have the highest exposure, and how does usable stock compare with tomorrow/seven-day demand?", measure: "Batch quantities, signed expiry days, exposure and deterministic requirements", fixed: ["subject_type = EXPIRY", "data_status = PROVISIONAL_SYNTHETIC", "Top 10 by exposure"], mappings: { "Snapshot As Of": riskMappings["Snapshot As Of"], Outlet: riskMappings.Outlet, "Raw Material": riskMappings["Raw Material"], "Material Category": riskMappings["Material Category"] }, note: "Always disclose that expiry is provisional synthetic demonstration evidence." },
      { name: "RPT_V2_R08B_7_Day_Inventory_Shortage_Action_Table", kind: "Action table", base: "QT_02_Numerical_Risk_Center", question: "Which ingredients are short tomorrow or over seven days after stock and eligible PO supply?", measure: "MAX stock, demand, eligible PO, shortage and exposure by item/UOM", fixed: ["subject_type = INVENTORY", "positive shortage", "Top 10 by exposure"], mappings: riskMappings },
    ],
  },
  {
    id: "procurement",
    label: "02 Procurement Vendor Consumption",
    purpose: "Separate ordered, received, pending and delayed value while preserving PO-line and ingredient evidence.",
    visibleFilters: ["Reporting Period", "Snapshot As Of", "Outlet", "Raw Material", "Material Category", "Canonical UOM", "Vendor"],
    objects: [
      { name: "Ordered Value", kind: "KPI", base: "RAW_Enterprise_Purchase_Order", question: "What value was ordered during the period?", measure: "SUM(Subtotal)", fixed: [], mappings: orderedMappings },
      { name: "Received Value", kind: "KPI", base: "RAW_Purchase_Detail", question: "What purchase value was physically received during the period?", measure: "AF_Flow_Purchase_Value", fixed: [], mappings: receivedMappings },
      { name: "Pending Open PO Liability", kind: "KPI", base: "QT_05_Procurement_Control", question: "What open PO value remains at the snapshot?", measure: "SUM(open_po_liability_pre_tax)", fixed: ["record_type = PO_AS_OF", "remaining_qty_canonical > 0"], mappings: procurementMappings },
      { name: "Delayed Open PO Liability", kind: "KPI", base: "QT_05_Procurement_Control", question: "How much open liability is already overdue?", measure: "SUM(open_po_liability_pre_tax)", fixed: ["record_type = PO_AS_OF", "remaining_qty_canonical > 0", "expected_delivery_date is not null", "overdue_days > 0"], mappings: procurementMappings },
      { name: "Closing Inventory Value", kind: "KPI", base: "QT_02_Numerical_Risk_Center", question: "What is the valued closing inventory at the snapshot?", measure: "SUM(current_stock_value)", fixed: ["subject_type = INVENTORY"], mappings: riskMappings },
      { name: "Positive Consumption Leakage", kind: "KPI", base: "QT_03_Consumption_Variance", question: "What is the value of eligible positive actual-over-theoretical consumption?", measure: "AF_Period_Positive_Leakage_Value", fixed: ["approved UOM", "evaluated theoretical consumption", "positive non-null leakage"], mappings: consumptionMappings },
      { name: "RPT_V2_P05_Vendor_Exposure", kind: "Chart", base: "QT_05_Procurement_Control", question: "Which vendors carry the largest open-PO exposure by timing severity?", measure: "SUM(open_po_liability_pre_tax) by vendor and risk_color", fixed: ["record_type = PO_AS_OF", "remaining_qty_canonical > 0", "Top 8 vendors"], mappings: procurementMappings },
      { name: "Open_Liability_Flow", kind: "Flow", base: "QT_05_Procurement_Control", question: "How does open liability flow from vendor to category to outlet?", measure: "vendor_name → category_name → outlet_name; weight liability", fixed: ["record_type = PO_AS_OF", "remaining_qty_canonical > 0", "path dimensions non-null"], mappings: procurementMappings },
      { name: "RPT_V2_P07A_Top_Unit_Price_Movement_Action_Table", kind: "Action table", base: "QT_07_Price_Movement · optional report extension", question: "Which comparable receipt-unit prices changed most?", measure: "Previous/current source-unit price and change % by unique receipt event", fixed: ["Top 10 by absolute unit-price change"], mappings: priceMappings, note: "QT_07 is an optional event-level extension and is not one of the ten core Query Tables." },
      { name: "RPT_V2_S08_Ingredient_Leakage_Top10", kind: "Chart", base: "QT_03_Consumption_Variance", question: "Which ingredients have the largest positive valued consumption variance?", measure: "SUM(consumption_leakage_value) by ingredient", fixed: ["approved UOM", "evaluated theoretical consumption", "positive leakage", "Top 10"], mappings: consumptionMappings },
      { name: "RPT_V2_P08_Delivery_Breach_Action_Top10", kind: "Action table", base: "QT_05_Procurement_Control", question: "Which overdue PO lines have the highest liability?", measure: "MAX overdue days and liability by vendor, PO, outlet and item", fixed: ["record_type = PO_AS_OF", "positive overdue days", "Top 10 by liability"], mappings: procurementMappings },
    ],
  },
  {
    id: "sales",
    label: "03 Sales & Menu Economics",
    purpose: "Explain category and item sales, theoretical recipe economics, source margin concentration and recipe relationships.",
    visibleFilters: ["Reporting Period", "Outlet", "Menu Item", "Menu Category", "Raw Material"],
    objects: [
      { name: "RPT_V2_S06_Category_Economics", kind: "Chart", base: "QT_04_Menu_Profitability", question: "How does eligible category net sales split into theoretical COGS and margin?", measure: "SUM(theoretical_cogs) + SUM(menu_gross_margin) by category", fixed: ["cost_evaluation_status_code = COMPLETE_RECIPE_COST", "Top 10 by net sales"], mappings: marginMappings },
      { name: "RPT_V2_S07B_Top_12_Menu_Items_By_Net_Sales", kind: "Chart", base: "QT_04_Menu_Profitability", question: "Which eligible menu items generated the most net sales?", measure: "SUM(net_sales_value) by menu item; sold qty and margin % in tooltip", fixed: ["cost_evaluation_status_code = COMPLETE_RECIPE_COST", "Top 12 by net sales"], mappings: marginMappings },
      { name: "RPT_V2_S10A_Source_Net_Margin_Heatmap", kind: "Chart", base: "QT_04_Menu_Profitability", question: "Where is source-reported net margin concentrated across outlet and category?", measure: "SUM(source_net_margin_value) by outlet × category", fixed: [], mappings: marginMappings, note: "Source-reported margin evidence; do not call it theoretical recipe margin or accounting profit." },
      { name: "RPT_V2_S09_Menu_Item_Raw_Material_Map", kind: "Pivot", base: "REF_Item_Recipe", question: "Which current recipe ingredients and quantities belong to a selected menu item?", measure: "Rows Item Name, Ingredient Name, Recipe Unit; SUM(Qty); totals off", fixed: ["No Top-N"], mappings: { "Menu Item": "REF_Item_Recipe.Item Name", "Raw Material": "REF_Item_Recipe.Ingredient Name" }, note: "Current recipe master only; no historical recipe version is available." },
    ],
  },
];

export function unmappedFilters(object: DashboardObject) {
  return allDashboardFilters.filter((filter) => !object.mappings[filter]);
}
