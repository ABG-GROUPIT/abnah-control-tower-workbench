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
import {
  EmptyState,
  MetricCard,
  PortalPanel,
  SeverityBadge,
  SourceBadge,
  TableShell,
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

function RiskMap({
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

export function RiskActionPage({
  datasets,
  sourceLabel,
  range,
  onRangeChange,
}: {
  datasets: PortalPageDatasets;
  sourceLabel: string;
  range: { start: string; end: string };
  onRangeChange: (range: { start: string; end: string }) => void;
}) {
  const inventory = datasets.inventoryRisk ?? EMPTY_ROWS;
  const menu = datasets.menuImpact ?? EMPTY_ROWS;
  const expiry = datasets.expiryRisk ?? EMPTY_ROWS;
  const riskyPo = datasets.riskyPo ?? EMPTY_ROWS;
  const [draft, setDraft] = useState<RiskFilters>(() => initialFilters(range));
  const [filters, setFilters] = useState<RiskFilters>(() => initialFilters(range));

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
            severityRank(rowText(right, "risk_severity")) -
              severityRank(rowText(left, "risk_severity")) ||
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
            severityRank(rowText(right, "risk_severity")) -
              severityRank(rowText(left, "risk_severity")) ||
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
            severityRank(rowText(right, "risk_severity")) -
              severityRank(rowText(left, "risk_severity")) ||
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

      <section className="ct-metric-grid" aria-label="Risk action metrics">
        <MetricCard
          title="Restaurants at risk"
          value={formatNumber(riskOutlets.size)}
          detail={`${scopedStockout.length} stock risks · ${scopedExpiry.length} expiry lines`}
          icon={Store}
        />
        <MetricCard
          title="Menu items impacted"
          value={formatNumber(menuItems.size)}
          detail="Distinct forecast menu items"
          icon={ChefHat}
          tone="warning"
        />
        <MetricCard
          title="Stockout risk"
          value={formatIndianCurrency(stockoutValue)}
          detail="Allocated seven-day forecast sales"
          icon={CircleDollarSign}
          tone="danger"
        />
        <MetricCard
          title="Expiry risk"
          value={formatIndianCurrency(expiryValue)}
          detail="Estimated batch-linked exposure"
          icon={AlertTriangle}
          tone="warning"
        />
        <MetricCard
          title="Open actions"
          value={formatNumber(actionCount)}
          detail="Rule-derived actions in scope"
          icon={ClipboardCheck}
          tone="success"
        />
      </section>

      <div className="ct-primary-grid">
        <PortalPanel
          title="Outlet risk map"
          subtitle="Severity, exposure and affected ingredients"
          badge={`${riskOutlets.size} outlets`}
        >
          <RiskMap inventory={scopedStockout} expiry={scopedExpiry} />
        </PortalPanel>
        <PortalPanel
          title="Priority action queue"
          subtitle="Evidence-backed decision rules, not POSist instructions"
          badge={`${actionRows.length} records`}
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
                  <div key={rowText(row, "action_id") || `${rowText(row, "po_number")}-${index}`}>
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
                  </div>
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
                    <tr key={rowText(row, "action_id")}>
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
                  <tr key={`${rowText(row, "outlet_code")}-${rowText(row, "ingredient_code")}-${rowText(row, "menu_item_code")}-${index}`}>
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
                    <tr key={rowText(row, "batch_allocation_id") || index}>
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
                    <tr key={`${rowText(row, "po_number")}-${rowText(row, "item_code")}-${index}`}>
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
    </div>
  );
}
