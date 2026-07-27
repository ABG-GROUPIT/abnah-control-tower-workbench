import {
  AlertTriangle,
  CalendarDays,
  CheckCircle2,
  ChefHat,
  CircleDollarSign,
  ClipboardCheck,
  RotateCcw,
  Search,
  Store,
} from "lucide-react";
import { useMemo, useState } from "react";
import {
  clampPresentedQuantity,
  formatDate,
  formatIndianCurrency,
  formatNumber,
  inDateRange,
  rowNumber,
  rowText,
  severityRank,
  uniqueValues,
  type PortalPageDatasets,
  type PortalRow,
} from "../../lib/control-tower-portal-data";
import type { ZohoPortalUrlMaps } from "../../lib/zoho-portal-types";
import {
  combineZohoCriteria,
  withZohoCriteria,
  zohoDateRange,
  zohoEquals,
} from "../../lib/zoho-view-criteria";
import {
  EmptyState,
  EvidenceDrawer,
  ExecutiveBrief,
  HybridVisualPanel,
  MetricCard,
  PortalPanel,
  SeverityBadge,
  SourceBadge,
  TableShell,
  type EvidenceContext,
} from "./PortalPrimitives";

interface RiskFilters {
  start: string;
  end: string;
  region: string;
  outlet: string;
  risk: string;
  category: string;
  owner: string;
}

const EMPTY_ROWS: PortalRow[] = [];

const filterDefaults = {
  region: "ALL",
  outlet: "ALL",
  risk: "ALL",
  category: "ALL",
  owner: "ALL",
};

function initialFilters(range: { start: string; end: string }): RiskFilters {
  return { ...filterDefaults, ...range };
}

function latestDate(rows: PortalRow[], field: string, end: string) {
  return rows
    .map((row) => rowText(row, field))
    .filter((value) => value && value <= end)
    .sort()
    .at(-1) ?? "";
}

function matchesSharedFilters(row: PortalRow, filters: RiskFilters) {
  const region =
    rowText(row, "region") || (rowText(row, "outlet_code") ? "North" : "");
  const owner =
    rowText(row, "action_owner") ||
    (rowText(row, "po_number") ? "Procurement" : "");
  const outletMatch =
    filters.outlet === "ALL" || rowText(row, "outlet_code") === filters.outlet;
  const regionMatch =
    filters.region === "ALL" || region === filters.region;
  const categoryMatch =
    filters.category === "ALL" ||
    rowText(row, "category_name") === filters.category;
  const ownerMatch =
    filters.owner === "ALL" || !owner || owner === filters.owner;
  return outletMatch && regionMatch && categoryMatch && ownerMatch;
}

function shortenedOutlet(value: string) {
  return value.replace(/^ABNAH Cafe\s*/i, "");
}

function quantity(value: number, uom: string, decimals = 1) {
  return `${formatNumber(value, decimals)} ${uom || ""}`.trim();
}

function actionSeverityRank(value: string) {
  return (
    {
      RED: 4,
      PURPLE: 3,
      AMBER: 2,
      GREEN: 1,
    }[value.toUpperCase()] ?? 0
  );
}

export function RiskMapValidationFallback({
  inventory,
  expiry,
}: {
  inventory: PortalRow[];
  expiry: PortalRow[];
}) {
  const pins = useMemo(() => {
    const grouped = new Map<
      string,
      {
        code: string;
        name: string;
        latitude: number;
        longitude: number;
        severity: string;
        value: number;
        risks: number;
      }
    >();
    [...inventory, ...expiry].forEach((row) => {
      const code = rowText(row, "outlet_code");
      if (!code) return;
      const current = grouped.get(code) ?? {
        code,
        name: rowText(row, "outlet_name"),
        latitude: rowNumber(row, "latitude"),
        longitude: rowNumber(row, "longitude"),
        severity: "GREEN",
        value: 0,
        risks: 0,
      };
      const severity = rowText(row, "risk_severity");
      if (severityRank(severity) > severityRank(current.severity)) {
        current.severity = severity;
      }
      current.value +=
        rowNumber(row, "shortage_cost_value") +
        rowNumber(row, "expiry_risk_value");
      current.risks += 1;
      grouped.set(code, current);
    });
    return Array.from(grouped.values());
  }, [expiry, inventory]);

  const positions: Record<string, [number, number]> = {
    OUT001: [295, 102],
    OUT002: [222, 218],
    OUT003: [385, 258],
  };

  return (
    <div className="ct-risk-map">
      <svg
        role="img"
        aria-label="Delhi NCR outlet risk map"
        viewBox="0 0 620 340"
      >
        <path
          className="ct-map-boundary"
          d="M119 44 L247 21 L351 48 L480 35 L551 102 L527 189 L564 266 L476 315 L352 299 L242 326 L139 283 L72 190 Z"
        />
        <path className="ct-map-road" d="M89 191 C206 176 304 155 538 124" />
        <path className="ct-map-road" d="M251 25 C277 111 303 194 342 311" />
        <path className="ct-map-road is-secondary" d="M130 273 C272 235 385 204 520 207" />
        <path className="ct-map-road is-secondary" d="M155 73 C250 123 362 190 476 306" />
        <text x="34" y="28" className="ct-map-label">DELHI NCR</text>
        <text x="36" y="314" className="ct-map-caption">Outlet coordinates · selected snapshot</text>
        {pins.map((pin) => {
          const [x, y] = positions[pin.code] ?? [310, 170];
          return (
            <g key={pin.code} className={`ct-map-pin severity-${pin.severity.toLowerCase()}`}>
              <circle className="ct-map-pulse" cx={x} cy={y} r="17" />
              <circle className="ct-map-dot" cx={x} cy={y} r="8" />
              <rect x={x + 12} y={y - 20} width="154" height="42" rx="4" />
              <text x={x + 22} y={y - 4}>{shortenedOutlet(pin.name)}</text>
              <text className="ct-map-value" x={x + 22} y={y + 12}>
                {pin.risks} risks · {formatIndianCurrency(pin.value)}
              </text>
            </g>
          );
        })}
      </svg>
      <div className="ct-map-legend" aria-label="Risk severity legend">
        <SeverityBadge value="PURPLE" label="Now" />
        <SeverityBadge value="RED" label="High" />
        <SeverityBadge value="AMBER" label="Watch" />
        <SeverityBadge value="GREEN" label="Healthy" />
      </div>
    </div>
  );
}

function OutletRiskOverview({
  inventory,
  expiry,
}: {
  inventory: PortalRow[];
  expiry: PortalRow[];
}) {
  const outlets = useMemo(() => {
    const grouped = new Map<
      string,
      {
        code: string;
        name: string;
        severity: string;
        value: number;
        risks: number;
      }
    >();
    [...inventory, ...expiry].forEach((row) => {
      const code = rowText(row, "outlet_code");
      if (!code) return;
      const current = grouped.get(code) ?? {
        code,
        name: rowText(row, "outlet_name"),
        severity: "GREEN",
        value: 0,
        risks: 0,
      };
      const severity = rowText(row, "risk_severity");
      if (
        actionSeverityRank(severity) >
        actionSeverityRank(current.severity)
      ) {
        current.severity = severity;
      }
      current.value +=
        rowNumber(row, "shortage_cost_value") +
        rowNumber(row, "expiry_risk_value");
      current.risks += 1;
      grouped.set(code, current);
    });
    return Array.from(grouped.values()).sort(
      (left, right) =>
        actionSeverityRank(right.severity) -
          actionSeverityRank(left.severity) ||
        right.value - left.value,
    );
  }, [expiry, inventory]);

  return (
    <div className="ct-outlet-risk-list">
      {outlets.map((outlet, index) => (
        <div key={outlet.code}>
          <span>{String(index + 1).padStart(2, "0")}</span>
          <div>
            <strong>{shortenedOutlet(outlet.name)}</strong>
            <small>
              {outlet.risks} risk records / {formatIndianCurrency(outlet.value)}
            </small>
          </div>
          <SeverityBadge
            value={outlet.severity}
            label={outlet.severity === "RED" ? "Action now" : outlet.severity}
          />
        </div>
      ))}
    </div>
  );
}

export function RiskActionPage({
  datasets,
  sourceLabel,
  range,
  onRangeChange,
  visualUrls,
}: {
  datasets: PortalPageDatasets;
  sourceLabel: string;
  range: { start: string; end: string };
  onRangeChange: (range: { start: string; end: string }) => void;
  visualUrls: ZohoPortalUrlMaps;
}) {
  const inventory = datasets.inventoryRisk ?? EMPTY_ROWS;
  const menu = datasets.menuImpact ?? EMPTY_ROWS;
  const expiry = datasets.expiryRisk ?? EMPTY_ROWS;
  const riskyPo = datasets.riskyPo ?? EMPTY_ROWS;
  const [draft, setDraft] = useState<RiskFilters>(() => initialFilters(range));
  const [filters, setFilters] = useState<RiskFilters>(() => initialFilters(range));
  const [evidence, setEvidence] = useState<EvidenceContext | null>(null);

  const riskDate = latestDate(inventory, "snapshot_date", filters.end);
  const expiryDate = latestDate(expiry, "as_of_date", filters.end);
  const poDate = latestDate(
    riskyPo,
    riskyPo.some((row) => rowText(row, "as_of_date"))
      ? "as_of_date"
      : "source_period_end",
    filters.end,
  );

  const snapshotInventory = useMemo(
    () =>
      inventory.filter(
        (row) =>
          rowText(row, "snapshot_date") === riskDate &&
          inDateRange(riskDate, filters.start, filters.end) &&
          matchesSharedFilters(row, filters),
      ),
    [filters, inventory, riskDate],
  );
  const stockoutRows = useMemo(
    () =>
      snapshotInventory
        .filter((row) => rowText(row, "risk_severity") !== "GREEN")
        .sort(
          (left, right) =>
            actionSeverityRank(rowText(right, "risk_severity")) -
              actionSeverityRank(rowText(left, "risk_severity")) ||
            rowNumber(right, "shortage_cost_value") -
              rowNumber(left, "shortage_cost_value"),
        ),
    [snapshotInventory],
  );
  const inventoryRiskKeys = useMemo(
    () =>
      new Set(
        snapshotInventory.map(
          (row) =>
            `${rowText(row, "outlet_code")}|${rowText(row, "item_code")}`,
        ),
      ),
    [snapshotInventory],
  );
  const menuRows = useMemo(
    () =>
      menu
        .filter(
          (row) =>
            rowText(row, "snapshot_date") === riskDate &&
            matchesSharedFilters(row, filters) &&
            inventoryRiskKeys.has(
              `${rowText(row, "outlet_code")}|${rowText(row, "ingredient_code")}`,
            ),
        )
        .sort(
          (left, right) =>
            rowNumber(right, "allocated_forecast_net_sales_at_risk") -
            rowNumber(left, "allocated_forecast_net_sales_at_risk"),
        ),
    [filters, inventoryRiskKeys, menu, riskDate],
  );
  const expiryRows = useMemo(
    () =>
      expiry
        .filter(
          (row) =>
            rowText(row, "as_of_date") === expiryDate &&
            inDateRange(expiryDate, filters.start, filters.end) &&
            matchesSharedFilters(row, filters),
        )
        .sort(
          (left, right) =>
            actionSeverityRank(rowText(right, "risk_severity")) -
              actionSeverityRank(rowText(left, "risk_severity")) ||
            rowNumber(right, "expiry_risk_value") -
              rowNumber(left, "expiry_risk_value"),
        ),
    [expiry, expiryDate, filters],
  );
  const poRows = useMemo(
    () =>
      riskyPo
        .filter((row) => {
          const rowDate =
            rowText(row, "as_of_date") || rowText(row, "source_period_end");
          return (
            rowDate === poDate &&
            inDateRange(rowDate, filters.start, filters.end) &&
            matchesSharedFilters(row, filters)
          );
        })
        .sort(
          (left, right) =>
            actionSeverityRank(rowText(right, "risk_severity")) -
              actionSeverityRank(rowText(left, "risk_severity")) ||
            rowNumber(right, "open_po_value") -
              rowNumber(left, "open_po_value"),
        ),
    [filters, poDate, riskyPo],
  );

  const showStockout = ["ALL", "STOCKOUT"].includes(filters.risk);
  const showExpiry = ["ALL", "EXPIRY"].includes(filters.risk);
  const showVendor = ["ALL", "VENDOR"].includes(filters.risk);
  const scopedStockout = showStockout ? stockoutRows : [];
  const scopedMenu = showStockout ? menuRows : [];
  const scopedExpiry = showExpiry ? expiryRows : [];
  const scopedPo = showVendor ? poRows : [];
  const riskOutlets = new Set(
    [
      ...scopedStockout.map((row) => rowText(row, "outlet_code")),
      ...scopedExpiry.map((row) => rowText(row, "outlet_code")),
      ...scopedPo.map((row) => rowText(row, "outlet_code")),
    ].filter(Boolean),
  );
  const menuItems = new Set(
    scopedMenu.map((row) => rowText(row, "menu_item_code")).filter(Boolean),
  );
  const stockoutValue = scopedMenu.reduce(
    (total, row) =>
      total + rowNumber(row, "allocated_forecast_net_sales_at_risk"),
    0,
  );
  const expiryValue = scopedExpiry.reduce(
    (total, row) => total + rowNumber(row, "expiry_risk_value"),
    0,
  );
  const actionRows =
    filters.risk === "EXPIRY"
      ? scopedExpiry
      : filters.risk === "VENDOR"
        ? scopedPo
        : scopedStockout;
  const actionCount = new Set(
    actionRows
      .map((row) => rowText(row, "action_id") || rowText(row, "po_number"))
      .filter(Boolean),
  ).size;

  const categories = uniqueValues(
    [...inventory, ...expiry, ...riskyPo],
    "category_name",
  );
  const outlets = Array.from(
    new Map(
      inventory.map((row) => [
        rowText(row, "outlet_code"),
        rowText(row, "outlet_name"),
      ]),
    ),
  ).filter(([code]) => code);
  const regions = uniqueValues([...inventory, ...expiry], "region");
  if (!regions.length && inventory.some((row) => rowText(row, "outlet_code"))) {
    regions.push("North");
  }

  const redActionRows = actionRows.filter(
    (row) => rowText(row, "risk_severity") === "RED",
  );
  const redExposure = redActionRows.reduce(
    (total, row) =>
      total +
      rowNumber(row, "shortage_cost_value") +
      rowNumber(row, "expiry_risk_value") +
      rowNumber(row, "open_po_value"),
    0,
  );
  const mapCriteria = combineZohoCriteria(
    zohoDateRange("snapshot_date", filters.start, filters.end),
    filters.outlet === "ALL"
      ? ""
      : zohoEquals("outlet_code", filters.outlet),
    filters.category === "ALL"
      ? ""
      : zohoEquals("category_name", filters.category),
    filters.owner === "ALL"
      ? ""
      : zohoEquals("action_owner", filters.owner),
    filters.risk === "STOCKOUT"
      ? zohoEquals("risk_type", "STOCKOUT")
      : "",
  );
  const menuCriteria = combineZohoCriteria(
    zohoDateRange("snapshot_date", filters.start, filters.end),
    filters.outlet === "ALL"
      ? ""
      : zohoEquals("outlet_code", filters.outlet),
    filters.category === "ALL"
      ? ""
      : zohoEquals("category_name", filters.category),
  );
  const expiryCriteria = combineZohoCriteria(
    zohoDateRange("as_of_date", filters.start, filters.end),
    filters.outlet === "ALL"
      ? ""
      : zohoEquals("outlet_code", filters.outlet),
    filters.category === "ALL"
      ? ""
      : zohoEquals("category_name", filters.category),
  );
  const riskyPoCriteria = combineZohoCriteria(
    zohoDateRange("as_of_date", filters.start, filters.end),
    filters.outlet === "ALL"
      ? ""
      : zohoEquals("outlet_code", filters.outlet),
    filters.category === "ALL"
      ? ""
      : zohoEquals("category_name", filters.category),
  );
  const nativeMapEligible = ["ALL", "STOCKOUT"].includes(filters.risk);
  const reportVisualUrl = (reportId: string, criteria = "") => {
    const reportUrl = visualUrls.reports[reportId] || "";
    return reportUrl ? withZohoCriteria(reportUrl, criteria) : "";
  };
  const visualUrl = (reportId: string, criteria = "") =>
    reportVisualUrl(reportId, criteria) || visualUrls.dashboards.p1 || "";
  const openEvidence = (
    context: Omit<EvidenceContext, "sourceUrl"> & {
      reportId: string;
      criteria?: string;
    },
  ) => {
    const { reportId, criteria = "", ...details } = context;
    setEvidence({
      ...details,
      sourceUrl: visualUrl(reportId, criteria),
    });
  };
  const riskColumns: EvidenceContext["columns"] = [
    { key: "risk_severity", label: "Risk" },
    { key: "item_name", label: "Raw material" },
    { key: "outlet_name", label: "Outlet" },
    {
      key: "forecast_required_qty",
      label: "Forecast requirement",
      render: (record) =>
        quantity(
          Number(record.forecast_required_qty ?? 0),
          String(record.canonical_uom ?? ""),
          1,
        ),
    },
    {
      key: "current_stock_qty",
      label: "Current stock",
      render: (record) =>
        quantity(
          clampPresentedQuantity(Number(record.current_stock_qty ?? 0)),
          String(record.canonical_uom ?? ""),
          1,
        ),
    },
    {
      key: "valid_open_po_qty",
      label: "Open PO",
      render: (record) =>
        quantity(
          Number(record.valid_open_po_qty ?? 0),
          String(record.canonical_uom ?? ""),
          1,
        ),
    },
    {
      key: "shortage_cost_value",
      label: "Exposure",
      render: (record) =>
        formatIndianCurrency(Number(record.shortage_cost_value ?? 0)),
    },
    { key: "recommended_action", label: "Model action" },
  ];
  const outletRiskColumns: EvidenceContext["columns"] = [
    {
      key: "risk_type",
      label: "Risk type",
      render: (record) =>
        String(
          record.risk_type ||
            (record.expiry_risk_value
              ? "EXPIRY"
              : record.po_number
                ? "VENDOR / PO"
                : "STOCKOUT"),
        ),
    },
    { key: "risk_severity", label: "Risk" },
    { key: "item_name", label: "Raw material" },
    { key: "outlet_name", label: "Outlet" },
    {
      key: "exposure",
      label: "Exposure",
      render: (record) =>
        formatIndianCurrency(
          Number(record.shortage_cost_value ?? 0) +
            Number(record.expiry_risk_value ?? 0) +
            Number(record.open_po_value ?? 0),
        ),
    },
    {
      key: "evidence_date",
      label: "Evidence date",
      render: (record) =>
        formatDate(
          String(
            record.snapshot_date ??
              record.as_of_date ??
              record.source_period_end ??
              "",
          ),
        ),
    },
    { key: "recommended_action", label: "Model action" },
  ];
  const menuColumns: EvidenceContext["columns"] = [
    { key: "menu_item_name", label: "Menu item" },
    { key: "ingredient_name", label: "Blocking material" },
    { key: "outlet_name", label: "Outlet" },
    { key: "forecast_menu_qty", label: "Forecast quantity" },
    {
      key: "allocated_forecast_net_sales_at_risk",
      label: "Sales exposure",
      render: (record) =>
        formatIndianCurrency(
          Number(record.allocated_forecast_net_sales_at_risk ?? 0),
        ),
    },
  ];
  const expiryColumns: EvidenceContext["columns"] = [
    { key: "risk_severity", label: "Risk" },
    { key: "item_name", label: "Raw material" },
    { key: "outlet_name", label: "Outlet" },
    { key: "estimated_expiry_date", label: "Estimated expiry" },
    { key: "days_to_expiry", label: "Days" },
    {
      key: "expiry_qty_at_risk",
      label: "Quantity at risk",
      render: (record) =>
        quantity(
          Number(record.expiry_qty_at_risk ?? 0),
          String(record.canonical_uom ?? ""),
          1,
        ),
    },
    {
      key: "expiry_risk_value",
      label: "Exposure",
      render: (record) =>
        formatIndianCurrency(Number(record.expiry_risk_value ?? 0)),
    },
    { key: "receipt_source_status", label: "Lineage" },
  ];
  const poColumns: EvidenceContext["columns"] = [
    { key: "po_number", label: "PO" },
    { key: "vendor_name", label: "Vendor" },
    { key: "item_name", label: "Raw material" },
    { key: "outlet_name", label: "Outlet" },
    { key: "expected_delivery_date", label: "Expected" },
    {
      key: "open_po_value",
      label: "Open exposure",
      render: (record) =>
        formatIndianCurrency(Number(record.open_po_value ?? 0)),
    },
  ];

  const reset = () => {
    const next = initialFilters(range);
    setDraft(next);
    setFilters(next);
  };
  const apply = () => {
    setFilters(draft);
    if (draft.start !== range.start || draft.end !== range.end) {
      onRangeChange({ start: draft.start, end: draft.end });
    }
  };

  return (
    <div className="ct-page ct-page-risk">
      <section className="ct-filter-bar" aria-label="Risk action filters">
        <label>
          <span>From</span>
          <input
            type="date"
            value={draft.start}
            onChange={(event) =>
              setDraft((current) => ({ ...current, start: event.target.value }))
            }
          />
        </label>
        <label>
          <span>To</span>
          <input
            type="date"
            value={draft.end}
            onChange={(event) =>
              setDraft((current) => ({ ...current, end: event.target.value }))
            }
          />
        </label>
        <label>
          <span>Region</span>
          <select
            value={draft.region}
            onChange={(event) =>
              setDraft((current) => ({ ...current, region: event.target.value }))
            }
          >
            <option value="ALL">All regions</option>
            {regions.map((region) => <option key={region}>{region}</option>)}
          </select>
        </label>
        <label>
          <span>Outlet</span>
          <select
            value={draft.outlet}
            onChange={(event) =>
              setDraft((current) => ({ ...current, outlet: event.target.value }))
            }
          >
            <option value="ALL">All outlets</option>
            {outlets.map(([code, name]) => (
              <option key={code} value={code}>{shortenedOutlet(name)}</option>
            ))}
          </select>
        </label>
        <label>
          <span>Risk</span>
          <select
            value={draft.risk}
            onChange={(event) =>
              setDraft((current) => ({ ...current, risk: event.target.value }))
            }
          >
            <option value="ALL">All risks</option>
            <option value="STOCKOUT">Stockout</option>
            <option value="EXPIRY">Expiry</option>
            <option value="VENDOR">Vendor / PO</option>
          </select>
        </label>
        <label>
          <span>Category</span>
          <select
            value={draft.category}
            onChange={(event) =>
              setDraft((current) => ({ ...current, category: event.target.value }))
            }
          >
            <option value="ALL">All categories</option>
            {categories.map((category) => <option key={category}>{category}</option>)}
          </select>
        </label>
        <label>
          <span>Owner</span>
          <select
            value={draft.owner}
            onChange={(event) =>
              setDraft((current) => ({ ...current, owner: event.target.value }))
            }
          >
            <option value="ALL">All owners</option>
            <option value="Procurement">Procurement</option>
            <option value="Operations">Operations</option>
            <option value="Supply Chain">Supply Chain</option>
          </select>
        </label>
        <div className="ct-filter-actions">
          <button type="button" className="is-primary" onClick={apply}>
            <Search aria-hidden="true" size={15} />
            Apply
          </button>
          <button type="button" onClick={reset} title="Reset filters">
            <RotateCcw aria-hidden="true" size={15} />
            Reset
          </button>
        </div>
      </section>

      <div className="ct-scope-line">
        <CalendarDays aria-hidden="true" size={15} />
        <span>
          Snapshot as of <strong>{formatDate(riskDate || expiryDate)}</strong>
        </span>
        <span>{sourceLabel}</span>
      </div>

      <ExecutiveBrief
        label="ACTION NOW"
        title={`${redActionRows.length} red-priority records require review`}
        detail={`${formatIndianCurrency(redExposure)} is exposed in the selected scope. Red records are placed first; open any KPI or row to inspect its contributing evidence.`}
        tone={redActionRows.length ? "danger" : "neutral"}
        action={
          redActionRows.length ? (
            <button
              type="button"
              onClick={() =>
                openEvidence({
                  reportId:
                    filters.risk === "EXPIRY"
                      ? "p1-expiry-detail"
                      : filters.risk === "VENDOR"
                        ? "p1-po-mitigation"
                        : "p1-action-queue",
                  criteria:
                    filters.risk === "EXPIRY"
                      ? expiryCriteria
                      : filters.risk === "VENDOR"
                        ? riskyPoCriteria
                        : mapCriteria,
                  title: "Red-priority action evidence",
                  subtitle: "Records currently prioritized for operational review",
                  reason:
                    "These rows carry RED severity in the selected risk scope and are ranked ahead of depleted and watch records.",
                  sourceQuery:
                    filters.risk === "EXPIRY"
                      ? "38_fact_ct_expiry_risk.sql"
                      : filters.risk === "VENDOR"
                        ? "36_fact_ct_risky_po.sql"
                        : "27_fact_ct_inventory_risk.sql",
                  sourceView:
                    filters.risk === "EXPIRY"
                      ? "CT_P1_Expiry_Risk_Detail_Demo"
                      : filters.risk === "VENDOR"
                        ? "CT_P1_Vendor_PO_Risk"
                        : "CT_P1_Action_Center",
                  records: redActionRows,
                  columns: riskColumns,
                })
              }
            >
              Inspect red queue
            </button>
          ) : null
        }
      />

      <section className="ct-metric-grid" aria-label="Risk action metrics">
        <MetricCard
          title="Restaurants at risk"
          value={formatNumber(riskOutlets.size)}
          detail={`${scopedStockout.length} stock risks · ${scopedExpiry.length} expiry lines`}
          icon={Store}
          onInspect={() =>
            openEvidence({
              reportId: "p1-risk-map",
              criteria: mapCriteria,
              title: "Restaurants at risk",
              subtitle: "Outlet records contributing to the selected scope",
              reason:
                "An outlet is counted when at least one non-green stockout, expiry or risky-PO row remains after the active filters.",
              sourceQuery: "27_fact_ct_inventory_risk.sql",
              sourceView: "CT_P1_Outlet_Risk_Map",
              records: [...scopedStockout, ...scopedExpiry, ...scopedPo],
              columns: outletRiskColumns,
            })
          }
        />
        <MetricCard
          title="Menu items impacted"
          value={formatNumber(menuItems.size)}
          detail="Distinct forecast menu items"
          icon={ChefHat}
          tone="warning"
          onInspect={() =>
            openEvidence({
              reportId: "p1-menu-detail",
              criteria: menuCriteria,
              title: "Menu items impacted",
              subtitle: "Menu demand paths blocked by shortage-risk materials",
              reason:
                "Distinct menu items are counted from recipe-linked forecast rows whose ingredient is present in the selected inventory-risk snapshot.",
              sourceQuery: "28_fact_ct_menu_impact.sql",
              sourceView: "CT_P1_Menu_Impact_Detail",
              records: scopedMenu,
              columns: menuColumns,
            })
          }
        />
        <MetricCard
          title="Stockout risk"
          value={formatIndianCurrency(stockoutValue)}
          detail="Allocated seven-day forecast sales"
          icon={CircleDollarSign}
          tone="danger"
          onInspect={() =>
            openEvidence({
              reportId: "p1-menu-detail",
              criteria: menuCriteria,
              title: "Stockout sales exposure",
              subtitle: "Menu forecast value allocated to shortage-risk ingredients",
              reason:
                "The KPI sums allocated forecast net sales at risk from recipe-linked menu rows. Allocation prevents the same menu sale from being counted once per blocking ingredient.",
              sourceQuery: "28_fact_ct_menu_impact.sql",
              sourceView: "CT_P1_Menu_Impact_Detail",
              records: scopedMenu,
              columns: menuColumns,
            })
          }
        />
        <MetricCard
          title="Expiry risk"
          value={formatIndianCurrency(expiryValue)}
          detail="Estimated batch-linked exposure"
          icon={AlertTriangle}
          tone="warning"
          onInspect={() =>
            openEvidence({
              reportId: "p1-expiry-detail",
              criteria: expiryCriteria,
              title: "Expiry risk exposure",
              subtitle: "Synthetic batch estimates and their receipt lineage",
              reason:
                "Expiry exposure is an explicit estimate because the production expiry report is not enabled. Receipt-linked rows retain PO and vendor evidence; opening-stock rows are labelled as estimates.",
              sourceQuery: "38_fact_ct_expiry_risk.sql",
              sourceView: "CT_P1_Expiry_Risk_Detail_Demo",
              records: scopedExpiry,
              columns: expiryColumns,
            })
          }
        />
        <MetricCard
          title="Open actions"
          value={formatNumber(actionCount)}
          detail="Rule-derived actions in scope"
          icon={ClipboardCheck}
          tone="success"
          onInspect={() =>
            openEvidence({
              reportId:
                filters.risk === "EXPIRY"
                  ? "p1-expiry-detail"
                  : filters.risk === "VENDOR"
                    ? "p1-po-mitigation"
                    : "p1-action-queue",
              criteria:
                filters.risk === "EXPIRY"
                  ? expiryCriteria
                  : filters.risk === "VENDOR"
                    ? riskyPoCriteria
                    : mapCriteria,
              title: "Open control-tower actions",
              subtitle: "Current rule-derived action records",
              reason:
                "Each distinct action or purchase order in the selected scope contributes once. The recommendation is a documented control-tower rule, while the supporting quantities and values come from the governed source views.",
              sourceQuery:
                filters.risk === "EXPIRY"
                  ? "38_fact_ct_expiry_risk.sql"
                  : filters.risk === "VENDOR"
                    ? "36_fact_ct_risky_po.sql"
                    : "27_fact_ct_inventory_risk.sql",
              sourceView:
                filters.risk === "EXPIRY"
                  ? "CT_P1_Expiry_Risk_Detail_Demo"
                  : filters.risk === "VENDOR"
                    ? "CT_P1_Vendor_PO_Risk"
                    : "CT_P1_Action_Center",
              records: actionRows,
              columns:
                filters.risk === "EXPIRY"
                  ? expiryColumns
                  : filters.risk === "VENDOR"
                    ? poColumns
                    : riskColumns,
            })
          }
        />
      </section>

      <div className="ct-primary-grid">
        <PortalPanel
          title="Priority action queue"
          subtitle="Red actions first, followed by depleted and watch records"
          badge={`${actionRows.length} records`}
          className="ct-priority-panel"
        >
          <div className="ct-action-queue">
            {actionRows.length ? (
              actionRows.slice(0, 10).map((row, index) => {
                const isPo = Boolean(rowText(row, "po_number"));
                const value =
                  rowNumber(row, "shortage_cost_value") ||
                  rowNumber(row, "expiry_risk_value") ||
                  rowNumber(row, "open_po_value");
                const severity = rowText(row, "risk_severity") || "RED";
                return (
                  <button
                    type="button"
                    key={rowText(row, "action_id") || `${rowText(row, "po_number")}-${index}`}
                    onClick={() =>
                      openEvidence({
                        reportId:
                          filters.risk === "EXPIRY"
                            ? "p1-expiry-detail"
                            : isPo
                              ? "p1-po-mitigation"
                              : "p1-action-queue",
                        criteria:
                          filters.risk === "EXPIRY"
                            ? expiryCriteria
                            : isPo
                              ? riskyPoCriteria
                              : mapCriteria,
                        title:
                          rowText(row, "recommended_action") ||
                          (isPo ? "Expedite open purchase order" : "Review risk"),
                        subtitle: `${rowText(row, "item_name")} / ${shortenedOutlet(rowText(row, "outlet_name"))}`,
                        reason:
                          "This record is positioned by severity and financial exposure. Open the governed Zoho view to inspect the complete filtered dataset.",
                        sourceQuery: isPo
                          ? "36_fact_ct_risky_po.sql"
                          : filters.risk === "EXPIRY"
                            ? "38_fact_ct_expiry_risk.sql"
                            : "27_fact_ct_inventory_risk.sql",
                        sourceView:
                          filters.risk === "EXPIRY"
                            ? "CT_P1_Expiry_Risk_Detail_Demo"
                            : isPo
                              ? "CT_P1_Vendor_PO_Risk"
                              : "CT_P1_Action_Center",
                        records: [row],
                        columns: isPo
                          ? poColumns
                          : filters.risk === "EXPIRY"
                            ? expiryColumns
                            : riskColumns,
                      })
                    }
                  >
                    <SeverityBadge
                      value={severity}
                      label={severity === "PURPLE" ? "NOW" : severity}
                    />
                    <span>
                      <strong>
                        {rowText(row, "recommended_action") ||
                          (isPo ? "Expedite open purchase order" : "Review risk")}
                      </strong>
                      <small>
                        {rowText(row, "item_name")} ·{" "}
                        {shortenedOutlet(rowText(row, "outlet_name"))} ·{" "}
                        {rowText(row, "action_owner") || "Procurement"} ·{" "}
                        {rowText(row, "due_band") || "Due today"}
                      </small>
                    </span>
                    <b>{formatIndianCurrency(value)}</b>
                  </button>
                );
              })
            ) : (
              <EmptyState>No actions match the selected scope.</EmptyState>
            )}
          </div>
          <div className="ct-decision-note">
            <CheckCircle2 aria-hidden="true" size={15} />
            <span>
              Action wording is generated by documented control-tower rules.
              POSist supplies the stock, demand and PO evidence.
            </span>
          </div>
        </PortalPanel>

        <HybridVisualPanel
          title="Outlet risk map"
          subtitle="Zoho geospatial view for location, severity and exposure"
          badge={`${riskOutlets.size} outlets`}
          viewName="CT_P1_Outlet_Risk_Map"
          embedUrl={
            nativeMapEligible
              ? reportVisualUrl("p1-risk-map", mapCriteria) || undefined
              : undefined
          }
          sourceUrl={visualUrl("p1-risk-map", mapCriteria) || undefined}
          onInspect={() =>
            openEvidence({
              reportId: "p1-risk-map",
              criteria: mapCriteria,
              title: "Outlet risk map evidence",
              subtitle: "All outlet-level risk records in the selected snapshot",
              reason:
                "The map locates outlets using the governed Zoho view. This evidence table shows the records contributing to its severity and exposure encoding.",
              sourceQuery: "27_fact_ct_inventory_risk.sql",
              sourceView: "CT_P1_Outlet_Risk_Map",
              records: [...scopedStockout, ...scopedExpiry, ...scopedPo],
              columns: outletRiskColumns,
            })
          }
        >
          <OutletRiskOverview
            inventory={scopedStockout}
            expiry={scopedExpiry}
          />
        </HybridVisualPanel>
      </div>

      <div className="ct-detail-grid">
        <PortalPanel
          title="Stockout risk"
          subtitle="Requirement, stock, inbound and days cover"
          badge={`${scopedStockout.length} lines`}
        >
          <TableShell label="Stockout risk detail">
            <table>
              <thead>
                <tr>
                  <th>Raw material</th>
                  <th>Outlet</th>
                  <th>Forecast req.</th>
                  <th>Current stock</th>
                  <th>Open PO</th>
                  <th>Days cover</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {scopedStockout.map((row) => {
                  const rawStock = rowNumber(row, "current_stock_qty");
                  return (
                    <tr
                      key={rowText(row, "action_id")}
                      className="is-drillable"
                      tabIndex={0}
                      onClick={() =>
                        openEvidence({
                          reportId: "p1-stockout-detail",
                          criteria: combineZohoCriteria(
                            mapCriteria,
                            zohoEquals("item_code", rowText(row, "item_code")),
                            zohoEquals(
                              "outlet_code",
                              rowText(row, "outlet_code"),
                            ),
                          ),
                          title: rowText(row, "item_name"),
                          subtitle: `Stockout evidence / ${shortenedOutlet(rowText(row, "outlet_name"))}`,
                          reason:
                            "This row combines the latest stock snapshot, forecast requirement, valid inbound quantity and rule-derived action for one outlet and material.",
                          sourceQuery: "27_fact_ct_inventory_risk.sql",
                          sourceView: "CT_P1_Stockout_Risk_Detail",
                          records: [row],
                          columns: riskColumns,
                        })
                      }
                      onKeyDown={(event) => {
                        if (event.key === "Enter" || event.key === " ") {
                          event.preventDefault();
                          event.currentTarget.click();
                        }
                      }}
                    >
                      <td>
                        <strong>{rowText(row, "item_name")}</strong>
                        <small>{rowText(row, "category_name")}</small>
                      </td>
                      <td>{shortenedOutlet(rowText(row, "outlet_name"))}</td>
                      <td>{quantity(rowNumber(row, "forecast_required_qty"), rowText(row, "canonical_uom"), 1)}</td>
                      <td title={rawStock < 0 ? `Raw source value: ${rawStock}` : undefined}>
                        {quantity(clampPresentedQuantity(rawStock), rowText(row, "canonical_uom"), 1)}
                        {rawStock < 0 ? <small className="ct-inline-warning">Raw negative</small> : null}
                      </td>
                      <td>
                        {rowNumber(row, "valid_open_po_qty") > 0
                          ? quantity(rowNumber(row, "valid_open_po_qty"), rowText(row, "canonical_uom"), 1)
                          : "No open PO"}
                      </td>
                      <td>{formatNumber(clampPresentedQuantity(rowNumber(row, "days_cover")), 1)}</td>
                      <td>
                        <SeverityBadge value={rowText(row, "risk_severity")} />
                        <small>{rowText(row, "recommended_action")}</small>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </TableShell>
        </PortalPanel>

        <PortalPanel
          title="Menu impact"
          subtitle="Forecast sales exposure allocated once across blockers"
          badge={`${menuItems.size} items`}
        >
          <TableShell label="Menu impact detail">
            <table>
              <thead>
                <tr>
                  <th>Menu item</th>
                  <th>Blocker raw material</th>
                  <th>Outlet</th>
                  <th>Forecast qty</th>
                  <th>Impact</th>
                </tr>
              </thead>
              <tbody>
                {scopedMenu.slice(0, 14).map((row, index) => (
                  <tr
                    key={`${rowText(row, "outlet_code")}-${rowText(row, "ingredient_code")}-${rowText(row, "menu_item_code")}-${index}`}
                    className="is-drillable"
                    tabIndex={0}
                    onClick={() =>
                      openEvidence({
                        reportId: "p1-menu-detail",
                        criteria: combineZohoCriteria(
                          menuCriteria,
                          zohoEquals(
                            "ingredient_code",
                            rowText(row, "ingredient_code"),
                          ),
                          zohoEquals(
                            "menu_item_code",
                            rowText(row, "menu_item_code"),
                          ),
                        ),
                        title: rowText(row, "menu_item_name"),
                        subtitle: `Blocked by ${rowText(row, "ingredient_name")}`,
                        reason:
                          "This menu item is connected through the recipe model to a shortage-risk ingredient. The displayed impact is its allocated share of forecast net sales at risk.",
                        sourceQuery: "28_fact_ct_menu_impact.sql",
                        sourceView: "CT_P1_Menu_Impact_Detail",
                        records: [row],
                        columns: menuColumns,
                      })
                    }
                    onKeyDown={(event) => {
                      if (event.key === "Enter" || event.key === " ") {
                        event.preventDefault();
                        event.currentTarget.click();
                      }
                    }}
                  >
                    <td><strong>{rowText(row, "menu_item_name")}</strong></td>
                    <td>
                      {rowText(row, "ingredient_name")}
                      <small>{rowText(row, "category_name")}</small>
                    </td>
                    <td>{shortenedOutlet(rowText(row, "outlet_name"))}</td>
                    <td>{formatNumber(rowNumber(row, "forecast_menu_qty"), 1)}</td>
                    <td><strong>{formatIndianCurrency(rowNumber(row, "allocated_forecast_net_sales_at_risk"))}</strong></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </TableShell>
        </PortalPanel>

        <PortalPanel
          title="Expiry risk"
          subtitle="Near-expiry estimate with explicit receipt lineage"
          badge={`${scopedExpiry.length} batches`}
        >
          <TableShell label="Expiry risk detail">
            <table>
              <thead>
                <tr>
                  <th>Raw material</th>
                  <th>Outlet</th>
                  <th>Qty at risk</th>
                  <th>Expiry</th>
                  <th>PO / vendor evidence</th>
                  <th>Risk value</th>
                </tr>
              </thead>
              <tbody>
                {scopedExpiry.slice(0, 14).map((row, index) => {
                  const receiptLinked =
                    rowText(row, "receipt_source_status") ===
                    "synthetic_internal_receipt_lineage";
                  return (
                    <tr
                      key={rowText(row, "batch_allocation_id") || index}
                      className="is-drillable"
                      tabIndex={0}
                      onClick={() =>
                        openEvidence({
                          reportId: "p1-expiry-detail",
                          criteria: combineZohoCriteria(
                            expiryCriteria,
                            zohoEquals("item_code", rowText(row, "item_code")),
                            zohoEquals(
                              "outlet_code",
                              rowText(row, "outlet_code"),
                            ),
                          ),
                          title: rowText(row, "item_name"),
                          subtitle: `Expiry estimate / ${shortenedOutlet(rowText(row, "outlet_name"))}`,
                          reason:
                            receiptLinked
                              ? "This estimate is tied to internal receipt lineage, retaining the contributing PO and vendor."
                              : "This is an opening-stock estimate with no receipt-linked PO or vendor and is labelled accordingly.",
                          sourceQuery: "38_fact_ct_expiry_risk.sql",
                          sourceView: "CT_P1_Expiry_Risk_Detail_Demo",
                          records: [row],
                          columns: expiryColumns,
                        })
                      }
                      onKeyDown={(event) => {
                        if (event.key === "Enter" || event.key === " ") {
                          event.preventDefault();
                          event.currentTarget.click();
                        }
                      }}
                    >
                      <td>
                        <strong>{rowText(row, "item_name")}</strong>
                        <small>{rowText(row, "category_name")}</small>
                      </td>
                      <td>{shortenedOutlet(rowText(row, "outlet_name"))}</td>
                      <td>{quantity(rowNumber(row, "expiry_qty_at_risk"), rowText(row, "canonical_uom"), 1)}</td>
                      <td>
                        {formatDate(rowText(row, "estimated_expiry_date"))}
                        <small>{formatNumber(rowNumber(row, "days_to_expiry"))} days</small>
                      </td>
                      <td>
                        {receiptLinked ? (
                          <>
                            <strong>{rowText(row, "po_number")}</strong>
                            <small>{rowText(row, "vendor_name")}</small>
                            <SourceBadge />
                          </>
                        ) : (
                          <>
                            <strong>Opening-stock estimate</strong>
                            <small>No receipt-linked PO or vendor</small>
                            <SourceBadge estimated />
                          </>
                        )}
                      </td>
                      <td>
                        <strong>{formatIndianCurrency(rowNumber(row, "expiry_risk_value"))}</strong>
                        <SeverityBadge value={rowText(row, "risk_severity")} />
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </TableShell>
        </PortalPanel>

        <PortalPanel
          title="Vendor / PO mitigation"
          subtitle="Open PO lines that intersect the selected inventory risks"
          badge={`${scopedPo.length} lines`}
        >
          {scopedPo.length ? (
            <TableShell label="Vendor and PO mitigation detail">
              <table>
                <thead>
                  <tr>
                    <th>Risk</th>
                    <th>PO / vendor</th>
                    <th>Raw material</th>
                    <th>Outlet</th>
                    <th>Expected</th>
                    <th>Pending value</th>
                  </tr>
                </thead>
                <tbody>
                  {scopedPo.map((row, index) => (
                    <tr
                      key={`${rowText(row, "po_number")}-${rowText(row, "item_code")}-${index}`}
                      className="is-drillable"
                      tabIndex={0}
                      onClick={() =>
                        openEvidence({
                          reportId: "p1-po-mitigation",
                          criteria: combineZohoCriteria(
                            riskyPoCriteria,
                            zohoEquals("po_number", rowText(row, "po_number")),
                            zohoEquals("item_code", rowText(row, "item_code")),
                          ),
                          title: rowText(row, "po_number"),
                          subtitle: `${rowText(row, "vendor_name")} / ${rowText(row, "item_name")}`,
                          reason:
                            "This open purchase-order line intersects the selected inventory-risk snapshot and can mitigate or delay the recommended action.",
                          sourceQuery: "36_fact_ct_risky_po.sql",
                          sourceView: "CT_P1_Vendor_PO_Risk",
                          records: [row],
                          columns: poColumns,
                        })
                      }
                      onKeyDown={(event) => {
                        if (event.key === "Enter" || event.key === " ") {
                          event.preventDefault();
                          event.currentTarget.click();
                        }
                      }}
                    >
                      <td><SeverityBadge value={rowText(row, "risk_severity")} /></td>
                      <td>
                        <strong>{rowText(row, "po_number")}</strong>
                        <small>{rowText(row, "vendor_name")}</small>
                      </td>
                      <td>{rowText(row, "item_name")}</td>
                      <td>{shortenedOutlet(rowText(row, "outlet_name"))}</td>
                      <td>{formatDate(rowText(row, "expected_delivery_date"))}</td>
                      <td>{formatIndianCurrency(rowNumber(row, "open_po_value"))}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </TableShell>
          ) : (
            <EmptyState>
              No open PO line intersects the selected risk snapshot. This is
              the expected month_03 all-outlet result.
            </EmptyState>
          )}
        </PortalPanel>
      </div>
      <EvidenceDrawer
        context={evidence}
        onClose={() => setEvidence(null)}
      />
    </div>
  );
}
