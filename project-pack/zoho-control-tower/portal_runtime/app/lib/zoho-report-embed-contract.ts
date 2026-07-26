import type {
  ZohoPortalFilterBinding,
  ZohoPortalMetric,
  ZohoPortalPanel,
} from "./zoho-portal-types";

type PortalView = ZohoPortalMetric | ZohoPortalPanel;

const periodExclusions = new Set([
  "CT_P2_Ingredient_Price_Trend",
  "CT_P3_Sales_Trend",
  "CT_P4_SCM_Monthly_Trend",
  "CT_P4_Consumption_Variance_Trend",
  "CT_P4_Data_Quality_Detail",
]);

const ingredientSources = new Set([
  "05_std_ct_inventory_snapshot.sql",
  "19_fact_ct_theoretical_consumption.sql",
  "20_fact_ct_actual_consumption.sql",
  "21_fact_ct_consumption_variance.sql",
  "22_fact_ct_purchase_order.sql",
  "23_fact_ct_purchase_receipt.sql",
  "24_fact_ct_po_receipt_line.sql",
  "27_fact_ct_inventory_risk.sql",
  "28_fact_ct_menu_impact.sql",
  "31_sum_ct_price_movement.sql",
  "36_fact_ct_risky_po.sql",
  "38_fact_ct_expiry_risk.sql",
]);

const menuSources = new Set([
  "18_fact_ct_sales.sql",
  "25_fact_ct_menu_profitability.sql",
  "32_sum_ct_menu_profitability.sql",
]);

const vendorSources = new Set([
  "22_fact_ct_purchase_order.sql",
  "23_fact_ct_purchase_receipt.sql",
  "24_fact_ct_po_receipt_line.sql",
  "29_sum_ct_procurement_funnel.sql",
  "30_sum_ct_vendor_scorecard.sql",
  "31_sum_ct_price_movement.sql",
  "36_fact_ct_risky_po.sql",
  "38_fact_ct_expiry_risk.sql",
]);

const quantityConsumptionSources = new Set([
  "19_fact_ct_theoretical_consumption.sql",
  "20_fact_ct_actual_consumption.sql",
  "21_fact_ct_consumption_variance.sql",
]);

function binding(
  filterId: string,
  criteriaTable: string,
  criteriaColumn: string,
  operator: "equals" | "contains" = "equals",
): ZohoPortalFilterBinding {
  return { filterId, criteriaTable, criteriaColumn, operator };
}

export function getReportFilterBindings(
  pageId: string,
  view: PortalView,
): ZohoPortalFilterBinding[] {
  const source = view.sourceQuery;
  const viewName = view.zohoViewName;
  const isQuality = source === "34_fact_ct_data_quality_exception.sql";
  const bindings: ZohoPortalFilterBinding[] = [];

  if (!periodExclusions.has(viewName) && !isQuality) {
    bindings.push(binding("period", source, "source_period_code"));
  }
  if (!isQuality) {
    bindings.push(binding("outlet", source, "outlet_code"));
    bindings.push(binding("region", "37_dim_ct_outlet_enriched.sql", "region"));
  }

  if (pageId === "p1") {
    if (ingredientSources.has(source)) {
      bindings.push(
        binding(
          "category",
          "14_dim_ct_item.sql",
          "category_name",
          "contains",
        ),
      );
    }
    if (source === "27_fact_ct_inventory_risk.sql") {
      bindings.push(binding("owner", source, "action_owner"));
    }
  }

  if (pageId === "p2") {
    if (ingredientSources.has(source)) {
      bindings.push(
        binding(
          "category",
          "14_dim_ct_item.sql",
          "category_name",
          "contains",
        ),
      );
      bindings.push(binding("rawMaterial", source, "item_code", "contains"));
    }
    if (vendorSources.has(source)) {
      bindings.push(binding("vendor", source, "vendor_name", "contains"));
    }
    if (
      source === "22_fact_ct_purchase_order.sql" ||
      source === "24_fact_ct_po_receipt_line.sql"
    ) {
      bindings.push(binding("poStatus", source, "po_status"));
    }
  }

  if (pageId === "p3") {
    if (menuSources.has(source)) {
      bindings.push(
        binding(
          "superCategory",
          "15_dim_ct_menu_item.sql",
          "super_category_name",
          "contains",
        ),
      );
      bindings.push(
        binding(
          "category",
          "15_dim_ct_menu_item.sql",
          "category_name",
          "contains",
        ),
      );
      bindings.push(binding("menuItem", source, "menu_item_code", "contains"));
    }
    if (ingredientSources.has(source)) {
      bindings.push(binding("rawMaterial", source, "item_code", "contains"));
    }
    if (quantityConsumptionSources.has(source)) {
      bindings.push(binding("uom", source, "canonical_uom"));
    }
  }

  if (pageId === "p4") {
    if (ingredientSources.has(source)) {
      bindings.push(
        binding(
          "category",
          "14_dim_ct_item.sql",
          "category_name",
          "contains",
        ),
      );
    }
    if (isQuality) {
      bindings.push(binding("exceptionType", source, "exception_type"));
    }
  }

  return bindings;
}

export function isViewVisibleForFilters(
  pageId: string,
  view: PortalView,
  values: Record<string, string>,
) {
  if (pageId !== "p1") return true;
  const risk = values.risk;
  if (!risk || risk === "ALL") return true;
  const isExpiry = view.sourceQuery === "38_fact_ct_expiry_risk.sql";
  return risk === "EXPIRY" ? isExpiry : !isExpiry;
}
