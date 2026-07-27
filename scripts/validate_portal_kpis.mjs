import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const source = JSON.parse(
  readFileSync(
    new URL("../public/data/control-tower-portal-demo.json", import.meta.url),
    "utf8",
  ),
);

const start = "2026-03-01";
const end = "2026-03-31";
const p1 = source.pages.p1;
const p2 = source.pages.p2;

function text(row, key) {
  const value = row[key];
  return value === null || value === undefined ? "" : String(value);
}

function number(row, key) {
  const value = Number(row[key]);
  return Number.isFinite(value) ? value : 0;
}

function bool(row, key) {
  const value = row[key];
  return (
    value === true ||
    value === 1 ||
    String(value).toLowerCase() === "true" ||
    String(value) === "1"
  );
}

function inRange(value) {
  return value >= start && value <= end;
}

function matches(row, filters) {
  return (
    (!filters.outlet || text(row, "outlet_code") === filters.outlet) &&
    (!filters.category ||
      !text(row, "category_name") ||
      text(row, "category_name") === filters.category) &&
    (!filters.vendor || text(row, "vendor_name") === filters.vendor)
  );
}

function latest(rows, key) {
  return rows
    .map((row) => text(row, key))
    .filter(inRange)
    .sort()
    .at(-1) ?? "";
}

function p1Metrics(filters = {}) {
  const inventoryDate = latest(p1.inventoryRisk, "snapshot_date");
  const expiryDate = latest(p1.expiryRisk, "as_of_date");
  const inventory = p1.inventoryRisk.filter(
    (row) =>
      text(row, "snapshot_date") === inventoryDate &&
      matches(row, filters),
  );
  const stockout = inventory.filter(
    (row) => text(row, "risk_severity") !== "GREEN",
  );
  const riskKeys = new Set(
    inventory.map(
      (row) => `${text(row, "outlet_code")}|${text(row, "item_code")}`,
    ),
  );
  const menu = p1.menuImpact.filter(
    (row) =>
      text(row, "snapshot_date") === inventoryDate &&
      matches(row, filters) &&
      riskKeys.has(
        `${text(row, "outlet_code")}|${text(row, "ingredient_code")}`,
      ),
  );
  const expiry = p1.expiryRisk.filter(
    (row) =>
      text(row, "as_of_date") === expiryDate &&
      matches(row, filters),
  );
  return {
    outlets: new Set(
      [...stockout, ...expiry].map((row) => text(row, "outlet_code")),
    ).size,
    menuItems: new Set(
      menu.map((row) => text(row, "menu_item_code")),
    ).size,
    stockoutValue: menu.reduce(
      (total, row) =>
        total + number(row, "allocated_forecast_net_sales_at_risk"),
      0,
    ),
    expiryValue: expiry.reduce(
      (total, row) => total + number(row, "expiry_risk_value"),
      0,
    ),
    actions: new Set(
      stockout.map((row) => text(row, "action_id")).filter(Boolean),
    ).size,
    stockoutRows: stockout.length,
    menuRows: menu.length,
    expiryRows: expiry.length,
  };
}

function poDate(row) {
  return (
    text(row, "po_date") ||
    text(row, "as_of_date") ||
    text(row, "source_period_end")
  );
}

function grossOrderValue(row) {
  return number(row, "gross_order_value") || number(row, "total_item_cost");
}

function p2Metrics(filters = {}) {
  const purchaseOrders = p2.purchaseOrders.filter(
    (row) => inRange(poDate(row)) && matches(row, filters),
  );
  const scoreRows = p2.poReceiptLines.filter(
    (row) => inRange(poDate(row)) && matches(row, filters),
  );
  const receipts = p2.purchaseReceipts.filter(
    (row) => inRange(text(row, "receipt_date")) && matches(row, filters),
  );
  const movement = p2.priceMovement.filter(
    (row) =>
      inRange(text(row, "price_as_of_date")) &&
      matches(row, filters),
  );
  const eligible = scoreRows.reduce(
    (total, row) => total + number(row, "eligible_closed_line_flag"),
    0,
  );
  const successful = scoreRows.reduce(
    (total, row) => total + number(row, "otif_success_flag"),
    0,
  );
  return {
    purchase: purchaseOrders.reduce(
      (total, row) => total + grossOrderValue(row),
      0,
    ),
    openPo: purchaseOrders.reduce(
      (total, row) => total + number(row, "open_po_value"),
      0,
    ),
    delayed: purchaseOrders.reduce(
      (total, row) =>
        total +
        (bool(row, "delayed_po_flag") ? number(row, "open_po_value") : 0),
      0,
    ),
    otif: eligible ? (successful / eligible) * 100 : null,
    priceWatch: new Set(
      movement.map((row) => text(row, "item_code")).filter(Boolean),
    ).size,
    poRows: purchaseOrders.length,
    scoreRows: scoreRows.length,
    receiptRows: receipts.length,
    movementRows: movement.length,
  };
}

function assertClose(actual, expected, label, tolerance = 0.011) {
  assert.ok(
    Math.abs(actual - expected) <= tolerance,
    `${label}: expected ${expected}, received ${actual}`,
  );
}

const p1Cases = [
  {
    label: "P1 all outlets",
    filters: {},
    expected: {
      outlets: 3,
      menuItems: 110,
      stockoutValue: 411695.5,
      expiryValue: 271399.12,
      actions: 6,
      stockoutRows: 6,
      menuRows: 302,
      expiryRows: 68,
    },
  },
  {
    label: "P1 OUT001",
    filters: { outlet: "OUT001" },
    expected: {
      outlets: 1,
      menuItems: 109,
      stockoutValue: 155161,
      expiryValue: 103856.36,
      actions: 2,
    },
  },
  {
    label: "P1 OUT002",
    filters: { outlet: "OUT002" },
    expected: {
      outlets: 1,
      menuItems: 62,
      stockoutValue: 102670.47,
      expiryValue: 91224.21,
      actions: 2,
    },
  },
  {
    label: "P1 OUT003",
    filters: { outlet: "OUT003" },
    expected: {
      outlets: 1,
      menuItems: 75,
      stockoutValue: 153864.03,
      expiryValue: 76318.55,
      actions: 2,
    },
  },
  {
    label: "P1 Dairy",
    filters: { category: "Dairy" },
    expected: {
      outlets: 3,
      menuItems: 62,
      stockoutValue: 122946.3,
      expiryValue: 85934.71,
      actions: 2,
    },
  },
  {
    label: "P1 Bakery",
    filters: { category: "Bakery" },
    expected: {
      outlets: 3,
      menuItems: 0,
      stockoutValue: 0,
      expiryValue: 42003.08,
      actions: 0,
    },
  },
];

for (const testCase of p1Cases) {
  const actual = p1Metrics(testCase.filters);
  for (const [key, expected] of Object.entries(testCase.expected)) {
    assertClose(actual[key], expected, `${testCase.label} ${key}`);
  }
}

const p2Cases = [
  {
    label: "P2 all outlets",
    filters: {},
    expected: {
      purchase: 1565981.32,
      openPo: 177145.39,
      delayed: 156529.83,
      otif: 53.7,
      priceWatch: 42,
      poRows: 215,
      scoreRows: 215,
      receiptRows: 220,
      movementRows: 103,
    },
  },
  {
    label: "P2 OUT001",
    filters: { outlet: "OUT001" },
    expected: {
      purchase: 562587.3,
      openPo: 62631.64,
      delayed: 53739.41,
      otif: 61.67,
      priceWatch: 34,
    },
  },
  {
    label: "P2 OUT002",
    filters: { outlet: "OUT002" },
    expected: {
      purchase: 505212.2,
      openPo: 50677.13,
      delayed: 43694.22,
      otif: 51.92,
      priceWatch: 33,
    },
  },
  {
    label: "P2 OUT003",
    filters: { outlet: "OUT003" },
    expected: {
      purchase: 498181.82,
      openPo: 63836.62,
      delayed: 59096.2,
      otif: 46,
      priceWatch: 36,
    },
  },
  {
    label: "P2 Dairy",
    filters: { category: "Dairy" },
    expected: {
      purchase: 416754.79,
      openPo: 41523.15,
      delayed: 34691.54,
      otif: 36.67,
      priceWatch: 5,
    },
  },
  {
    label: "P2 BeanCraft",
    filters: { vendor: "BeanCraft Roasters Delhi" },
    expected: {
      purchase: 54269.9,
      openPo: 1464.83,
      delayed: 1464.83,
      otif: 66.67,
      priceWatch: 1,
    },
  },
];

for (const testCase of p2Cases) {
  const actual = p2Metrics(testCase.filters);
  for (const [key, expected] of Object.entries(testCase.expected)) {
    assertClose(actual[key], expected, `${testCase.label} ${key}`, 0.011);
  }
}

console.log(
  `Portal KPI validation passed: ${p1Cases.length + p2Cases.length} filter scenarios.`,
);
