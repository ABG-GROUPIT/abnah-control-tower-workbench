import {
  BadgeIndianRupee,
  CalendarDays,
  ClockAlert,
  Gauge,
  RotateCcw,
  Search,
  ShoppingCart,
  Tags,
} from "lucide-react";
import { useMemo, useState } from "react";
import {
  formatDate,
  formatIndianCurrency,
  formatNumber,
  formatPercent,
  inDateRange,
  rowBoolean,
  rowNumber,
  rowText,
  uniqueValues,
  type PortalPageDatasets,
  type PortalRow,
} from "../../lib/control-tower-portal-data";
import {
  EmptyState,
  MetricCard,
  PortalPanel,
  SeverityBadge,
  TableShell,
} from "./PortalPrimitives";

interface ProcurementFilters {
  start: string;
  end: string;
  region: string;
  outlet: string;
  category: string;
  vendor: string;
  poStatus: string;
  rawMaterial: string;
}

const EMPTY_ROWS: PortalRow[] = [];

const filterDefaults = {
  region: "ALL",
  outlet: "ALL",
  category: "ALL",
  vendor: "ALL",
  poStatus: "ALL",
  rawMaterial: "",
};

function initialFilters(
  range: { start: string; end: string },
): ProcurementFilters {
  return { ...filterDefaults, ...range };
}

function poScopeDate(row: PortalRow) {
  return (
    rowText(row, "po_date") ||
    rowText(row, "as_of_date") ||
    rowText(row, "source_period_end")
  );
}

function matchesFilters(row: PortalRow, filters: ProcurementFilters) {
  const region = rowText(row, "region") || "North";
  const category = rowText(row, "category_name");
  const status = rowText(row, "po_status");
  const material = `${rowText(row, "item_code")} ${rowText(row, "item_name")}`
    .toLowerCase();
  return (
    (filters.region === "ALL" || region === filters.region) &&
    (filters.outlet === "ALL" ||
      rowText(row, "outlet_code") === filters.outlet) &&
    (filters.category === "ALL" ||
      !category ||
      category === filters.category) &&
    (filters.vendor === "ALL" ||
      rowText(row, "vendor_name") === filters.vendor) &&
    (filters.poStatus === "ALL" ||
      !status ||
      status === filters.poStatus) &&
    (!filters.rawMaterial ||
      material.includes(filters.rawMaterial.trim().toLowerCase()))
  );
}

function grossOrderValue(row: PortalRow) {
  return (
    rowNumber(row, "gross_order_value") || rowNumber(row, "total_item_cost")
  );
}

function remainingQuantity(row: PortalRow) {
  return (
    rowNumber(row, "remaining_qty") ||
    rowNumber(row, "remaining_balance_qty")
  );
}

function rowUnit(row: PortalRow) {
  return rowText(row, "canonical_uom") || rowText(row, "unit");
}

function weightedOtif(rows: PortalRow[]) {
  const eligible = rows.reduce(
    (total, row) => total + rowNumber(row, "eligible_closed_line_flag"),
    0,
  );
  const successful = rows.reduce(
    (total, row) => total + rowNumber(row, "otif_success_flag"),
    0,
  );
  return eligible ? (successful / eligible) * 100 : null;
}

function vendorScore(rows: PortalRow[]) {
  const grouped = new Map<
    string,
    {
      vendor: string;
      purchase: number;
      open: number;
      ordered: number;
      received: number;
      eligible: number;
      success: number;
      delays: number;
      leadTotal: number;
      leadCount: number;
    }
  >();
  rows.forEach((row) => {
    const vendor = rowText(row, "vendor_name") || "Unassigned vendor";
    const current = grouped.get(vendor) ?? {
      vendor,
      purchase: 0,
      open: 0,
      ordered: 0,
      received: 0,
      eligible: 0,
      success: 0,
      delays: 0,
      leadTotal: 0,
      leadCount: 0,
    };
    current.purchase += grossOrderValue(row);
    current.open += rowNumber(row, "open_po_value");
    current.ordered += rowNumber(row, "ordered_qty");
    current.received += rowNumber(row, "received_qty");
    current.eligible += rowNumber(row, "eligible_closed_line_flag");
    current.success += rowNumber(row, "otif_success_flag");
    current.delays += rowNumber(row, "delayed_po_flag");
    const lead = row["lead_time_deviation_days"];
    if (lead !== null && lead !== undefined && lead !== "") {
      current.leadTotal += rowNumber(row, "lead_time_deviation_days");
      current.leadCount += 1;
    }
    grouped.set(vendor, current);
  });
  return Array.from(grouped.values())
    .map((row) => {
      const otif = row.eligible ? (row.success / row.eligible) * 100 : null;
      const fill = row.ordered ? (row.received / row.ordered) * 100 : 0;
      const rag =
        row.open >= 50_000 || (otif !== null && otif < 45)
          ? "RED"
          : row.open > 0 || (otif !== null && otif < 70)
            ? "AMBER"
            : "GREEN";
      return {
        ...row,
        otif,
        fill,
        averageLead: row.leadCount ? row.leadTotal / row.leadCount : 0,
        rag,
      };
    })
    .sort(
      (left, right) =>
        right.open - left.open ||
        (left.otif ?? Number.POSITIVE_INFINITY) -
          (right.otif ?? Number.POSITIVE_INFINITY),
    );
}

function priceTrend(
  rows: PortalRow[],
  itemCode: string,
  canonicalUom: string,
) {
  const grouped = new Map<
    string,
    { label: string; value: number; qty: number; date: string }
  >();
  rows
    .filter(
      (row) =>
        rowText(row, "item_code") === itemCode &&
        (!canonicalUom || rowUnit(row) === canonicalUom),
    )
    .forEach((row) => {
      const receiptDate = rowText(row, "receipt_date");
      const period =
        /^\d{4}-\d{2}/.test(receiptDate)
          ? receiptDate.slice(0, 7)
          : rowText(row, "source_period_code");
      const current = grouped.get(period) ?? {
        label: period,
        value: 0,
        qty: 0,
        date: receiptDate,
      };
      current.value += rowNumber(row, "receipt_subtotal");
      current.qty += rowNumber(row, "received_qty");
      if (receiptDate > current.date) {
        current.date = receiptDate;
      }
      grouped.set(period, current);
    });
  return Array.from(grouped.values())
    .map((row) => ({
      ...row,
      unitPrice: row.qty ? row.value / row.qty : 0,
    }))
    .sort((left, right) => left.date.localeCompare(right.date));
}

function PriceLineChart({
  points,
}: {
  points: ReturnType<typeof priceTrend>;
}) {
  if (!points.length) {
    return <EmptyState>No comparable receipt prices match this scope.</EmptyState>;
  }
  const values = points.map((point) => point.unitPrice);
  const minimum = Math.min(...values);
  const maximum = Math.max(...values);
  const spread = maximum - minimum || 1;
  const coordinates = points.map((point, index) => {
    const x = points.length === 1 ? 320 : 55 + (index * 530) / (points.length - 1);
    const y = 235 - ((point.unitPrice - minimum) / spread) * 155;
    return { ...point, x, y };
  });
  return (
    <div className="ct-price-chart">
      <svg viewBox="0 0 640 285" role="img" aria-label="Weighted receipt unit price trend">
        {[80, 130, 180, 230].map((y) => (
          <line key={y} x1="45" x2="600" y1={y} y2={y} className="ct-chart-grid" />
        ))}
        <polyline
          points={coordinates.map((point) => `${point.x},${point.y}`).join(" ")}
          className="ct-price-line"
        />
        {coordinates.map((point) => (
          <g key={`${point.label}-${point.x}`}>
            <circle cx={point.x} cy={point.y} r="6" className="ct-price-point" />
            <text x={point.x} y={point.y - 14} textAnchor="middle">
              {formatIndianCurrency(point.unitPrice, { compact: false, decimals: 1 })}
            </text>
            <text x={point.x} y="263" textAnchor="middle" className="ct-chart-axis">
              {formatDate(point.date).replace(/\s\d{4}$/, "")}
            </text>
          </g>
        ))}
      </svg>
    </div>
  );
}

function movementChange(row: PortalRow) {
  return (
    rowNumber(row, "price_change_amount") ||
    rowNumber(row, "unit_price_change")
  );
}

function movementChangePercent(row: PortalRow) {
  return (
    rowNumber(row, "price_change_percent") ||
    rowNumber(row, "unit_price_change_percent")
  );
}

function movementAbsolutePercent(row: PortalRow) {
  return (
    rowNumber(row, "absolute_price_change_percent") ||
    rowNumber(row, "absolute_unit_price_change_percent")
  );
}

export function ProcurementPage({
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
  const purchaseOrders = datasets.purchaseOrders ?? EMPTY_ROWS;
  const receiptLines = datasets.poReceiptLines ?? EMPTY_ROWS;
  const receipts = datasets.purchaseReceipts ?? EMPTY_ROWS;
  const movement = datasets.priceMovement ?? EMPTY_ROWS;
  const [draft, setDraft] =
    useState<ProcurementFilters>(() => initialFilters(range));
  const [filters, setFilters] =
    useState<ProcurementFilters>(() => initialFilters(range));

  const poRows = useMemo(
    () =>
      purchaseOrders.filter(
        (row) =>
          inDateRange(poScopeDate(row), filters.start, filters.end) &&
          matchesFilters(row, filters),
      ),
    [filters, purchaseOrders],
  );
  const scoreRows = useMemo(
    () =>
      receiptLines.filter(
        (row) =>
          inDateRange(poScopeDate(row), filters.start, filters.end) &&
          matchesFilters(row, filters),
      ),
    [filters, receiptLines],
  );
  const receiptRows = useMemo(
    () =>
      receipts.filter(
        (row) =>
          inDateRange(rowText(row, "receipt_date"), filters.start, filters.end) &&
          matchesFilters(row, filters),
      ),
    [filters, receipts],
  );
  const movementRows = useMemo(
    () =>
      movement
        .filter(
          (row) =>
            inDateRange(
              rowText(row, "price_as_of_date"),
              filters.start,
              filters.end,
            ) && matchesFilters(row, filters),
        )
        .sort(
          (left, right) =>
            movementAbsolutePercent(right) - movementAbsolutePercent(left),
        ),
    [filters, movement],
  );

  const monthlyPurchase = poRows.reduce(
    (total, row) => total + grossOrderValue(row),
    0,
  );
  const processed = poRows.reduce(
    (total, row) => total + rowNumber(row, "processed_po_value"),
    0,
  );
  const openExposure = poRows.reduce(
    (total, row) => total + rowNumber(row, "open_po_value"),
    0,
  );
  const delayedExposure = poRows.reduce(
    (total, row) =>
      total +
      (rowBoolean(row, "delayed_po_flag")
        ? rowNumber(row, "open_po_value")
        : 0),
    0,
  );
  const otif = weightedOtif(scoreRows);
  const priceWatch = new Set(
    movementRows.map((row) => rowText(row, "item_code")).filter(Boolean),
  ).size;
  const comparableMovementRows = movementRows.filter(
    (row) =>
      row.previous_unit_price !== null &&
      row.previous_unit_price !== undefined &&
      row.previous_unit_price !== "",
  );
  const comparablePriceWatch = new Set(
    comparableMovementRows
      .map((row) => rowText(row, "item_code"))
      .filter(Boolean),
  ).size;
  const noBaselinePriceWatch = Math.max(0, priceWatch - comparablePriceWatch);
  const vendorRows = vendorScore(scoreRows);
  const pendingRows = poRows
    .filter((row) => rowBoolean(row, "is_open_po"))
    .sort(
      (left, right) =>
        rowNumber(right, "open_po_value") - rowNumber(left, "open_po_value"),
    );
  const breachRows = pendingRows.filter((row) =>
    rowBoolean(row, "delayed_po_flag"),
  );

  const materialSpend = new Map<string, number>();
  receiptRows.forEach((row) => {
    const code = rowText(row, "item_code");
    materialSpend.set(
      code,
      (materialSpend.get(code) ?? 0) + rowNumber(row, "receipt_subtotal"),
    );
  });
  const materialOptions = Array.from(
    new Map(
      receiptRows.map((row) => [
        rowText(row, "item_code"),
        rowText(row, "item_name"),
      ]),
    ),
  ).filter(([code]) => code);
  const defaultMaterial =
    Array.from(materialSpend.entries()).sort((left, right) => right[1] - left[1])[0]?.[0] ??
    materialOptions[0]?.[0] ??
    "";
  const [trendItem, setTrendItem] = useState("");
  const selectedTrendItem =
    trendItem && materialOptions.some(([code]) => code === trendItem)
      ? trendItem
      : defaultMaterial;
  const trendUomOptions = uniqueValues(
    receiptRows.filter(
      (row) => rowText(row, "item_code") === selectedTrendItem,
    ),
    "canonical_uom",
  );
  const [trendUom, setTrendUom] = useState("");
  const selectedTrendUom =
    trendUom && trendUomOptions.includes(trendUom)
      ? trendUom
      : trendUomOptions[0] ?? "";
  const trendPoints = priceTrend(
    receiptRows,
    selectedTrendItem,
    selectedTrendUom,
  );

  const categories = uniqueValues(purchaseOrders, "category_name");
  const vendors = uniqueValues(purchaseOrders, "vendor_name");
  const statuses = uniqueValues(purchaseOrders, "po_status");
  const outlets = Array.from(
    new Map(
      purchaseOrders.map((row) => [
        rowText(row, "outlet_code"),
        rowText(row, "outlet_name") || rowText(row, "outlet_code"),
      ]),
    ),
  ).filter(([code]) => code);
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
    <div className="ct-page ct-page-procurement">
      <section className="ct-filter-bar" aria-label="Procurement filters">
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
            <option value="North">North</option>
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
              <option value={code} key={code}>{name}</option>
            ))}
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
          <span>Vendor</span>
          <select
            value={draft.vendor}
            onChange={(event) =>
              setDraft((current) => ({ ...current, vendor: event.target.value }))
            }
          >
            <option value="ALL">All vendors</option>
            {vendors.map((vendor) => <option key={vendor}>{vendor}</option>)}
          </select>
        </label>
        <label>
          <span>PO status</span>
          <select
            value={draft.poStatus}
            onChange={(event) =>
              setDraft((current) => ({ ...current, poStatus: event.target.value }))
            }
          >
            <option value="ALL">All PO statuses</option>
            {statuses.map((status) => <option key={status}>{status}</option>)}
          </select>
        </label>
        <label className="ct-filter-search">
          <span>Raw material</span>
          <input
            type="search"
            placeholder="Search item"
            value={draft.rawMaterial}
            onChange={(event) =>
              setDraft((current) => ({
                ...current,
                rawMaterial: event.target.value,
              }))
            }
          />
        </label>
        <div className="ct-filter-actions">
          <button type="button" className="is-primary" onClick={apply}>
            <Search aria-hidden="true" size={15} />
            Apply
          </button>
          <button type="button" onClick={reset}>
            <RotateCcw aria-hidden="true" size={15} />
            Reset
          </button>
        </div>
      </section>

      <div className="ct-scope-line">
        <CalendarDays aria-hidden="true" size={15} />
        <span>
          Activity from <strong>{formatDate(filters.start)}</strong> to{" "}
          <strong>{formatDate(filters.end)}</strong>
        </span>
        <span>{sourceLabel}</span>
      </div>

      <section className="ct-metric-grid" aria-label="Procurement metrics">
        <MetricCard
          title="Monthly purchase"
          value={formatIndianCurrency(monthlyPurchase)}
          detail="Ordered gross value"
          icon={ShoppingCart}
        />
        <MetricCard
          title="Open PO exposure"
          value={formatIndianCurrency(openExposure)}
          detail={`${new Set(pendingRows.map((row) => rowText(row, "po_number"))).size} open purchase orders`}
          icon={BadgeIndianRupee}
          tone="warning"
        />
        <MetricCard
          title="Delayed PO value"
          value={formatIndianCurrency(delayedExposure)}
          detail={`${breachRows.length} delayed lines`}
          icon={ClockAlert}
          tone="danger"
        />
        <MetricCard
          title="Vendor OTIF"
          value={otif === null ? "Not available" : formatPercent(otif)}
          detail={
            otif === null
              ? "No eligible closed lines in scope"
              : "Weighted eligible-line rate"
          }
          icon={Gauge}
          tone={otif === null ? undefined : otif < 60 ? "danger" : "success"}
        />
        <MetricCard
          title="Price watch"
          value={formatNumber(priceWatch)}
          detail={`${comparablePriceWatch} comparable · ${noBaselinePriceWatch} no baseline`}
          icon={Tags}
        />
      </section>

      <div className="ct-primary-grid">
        <PortalPanel
          title="Procurement funnel"
          subtitle="Ordered, processed, pending and delayed value"
          badge="selected scope"
        >
          <div className="ct-procurement-funnel">
            {[
              ["Ordered", monthlyPurchase, "ordered"],
              ["Processed", processed, "processed"],
              ["Pending", openExposure, "pending"],
              ["Delayed", delayedExposure, "delayed"],
            ].map(([label, value, tone]) => {
              const numericValue = Number(value);
              const width = monthlyPurchase
                ? Math.max(4, (numericValue / monthlyPurchase) * 100)
                : 0;
              return (
                <div key={String(label)}>
                  <span>
                    <strong>{formatIndianCurrency(numericValue)}</strong>
                    <small>{label}</small>
                  </span>
                  <i>
                    <b className={`tone-${tone}`} style={{ width: `${width}%` }} />
                  </i>
                </div>
              );
            })}
          </div>
        </PortalPanel>

        <PortalPanel
          title="Vendor risk scorecard"
          subtitle="Purchase, exposure, OTIF and fulfillment"
          badge={`${vendorRows.length} vendors`}
        >
          <TableShell label="Vendor risk scorecard">
            <table>
              <thead>
                <tr>
                  <th>RAG</th>
                  <th>Vendor</th>
                  <th>Purchase</th>
                  <th>Open PO</th>
                  <th>OTIF</th>
                  <th>Fill rate</th>
                  <th>Delayed</th>
                </tr>
              </thead>
              <tbody>
                {vendorRows.map((row) => (
                  <tr key={row.vendor}>
                    <td><SeverityBadge value={row.rag} /></td>
                    <td><strong>{row.vendor}</strong></td>
                    <td>{formatIndianCurrency(row.purchase)}</td>
                    <td>{formatIndianCurrency(row.open)}</td>
                    <td>{row.otif === null ? "Not available" : formatPercent(row.otif)}</td>
                    <td>{formatPercent(row.fill)}</td>
                    <td>{formatNumber(row.delays)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </TableShell>
        </PortalPanel>
      </div>

      <div className="ct-detail-grid">
        <PortalPanel
          title="Raw material price trend"
          subtitle="Weighted accepted receipt price"
          badge={`${trendPoints.length} periods`}
        >
          <div className="ct-chart-control">
            <label>
              <span>Raw material</span>
              <select
                value={selectedTrendItem}
                onChange={(event) => {
                  setTrendItem(event.target.value);
                  setTrendUom("");
                }}
              >
                {materialOptions.map(([code, name]) => (
                  <option value={code} key={code}>{name}</option>
                ))}
              </select>
            </label>
            <label>
              <span>UOM</span>
              <select
                value={selectedTrendUom}
                onChange={(event) => setTrendUom(event.target.value)}
              >
                {trendUomOptions.map((uom) => (
                  <option value={uom} key={uom}>{uom}</option>
                ))}
              </select>
            </label>
          </div>
          <PriceLineChart points={trendPoints} />
        </PortalPanel>

        <PortalPanel
          title="Top price movement"
          subtitle="Prior-period comparisons; new price records remain in Price watch"
          badge={`${comparableMovementRows.length} comparable records`}
        >
          <TableShell label="Top raw material price movement">
            <table>
              <thead>
                <tr>
                  <th>Raw material</th>
                  <th>Vendor</th>
                  <th>UOM</th>
                  <th>Previous</th>
                  <th>Current</th>
                  <th>Change</th>
                  <th>Change %</th>
                  <th>Value impact</th>
                </tr>
              </thead>
              <tbody>
                {comparableMovementRows.slice(0, 12).map((row, index) => {
                  const change = movementChange(row);
                  return (
                    <tr key={`${rowText(row, "outlet_code")}-${rowText(row, "vendor_name")}-${rowText(row, "item_code")}-${index}`}>
                      <td><strong>{rowText(row, "item_name")}</strong></td>
                      <td>{rowText(row, "vendor_name")}</td>
                      <td>{rowUnit(row)}</td>
                      <td>{formatIndianCurrency(rowNumber(row, "previous_unit_price"), { compact: false, decimals: 1 })}</td>
                      <td>{formatIndianCurrency(rowNumber(row, "current_unit_price"), { compact: false, decimals: 1 })}</td>
                      <td className={change >= 0 ? "ct-positive" : "ct-negative"}>
                        {change >= 0 ? "+" : ""}
                        {formatIndianCurrency(change, { compact: false, decimals: 1 })}
                      </td>
                      <td className={change >= 0 ? "ct-positive" : "ct-negative"}>
                        {formatPercent(movementChangePercent(row))}
                      </td>
                      <td>{formatIndianCurrency(rowNumber(row, "price_change_value_impact"))}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </TableShell>
        </PortalPanel>

        <PortalPanel
          title="Pending by vendor"
          subtitle="Open liability by supplier and raw material"
          badge={`${pendingRows.length} lines`}
        >
          <TableShell label="Pending purchase orders by vendor">
            <table>
              <thead>
                <tr>
                  <th>Vendor</th>
                  <th>Raw material</th>
                  <th>Category</th>
                  <th>Pending qty</th>
                  <th>Value</th>
                  <th>Expected</th>
                </tr>
              </thead>
              <tbody>
                {pendingRows.slice(0, 14).map((row, index) => (
                  <tr key={`${rowText(row, "po_number")}-${rowText(row, "item_code")}-${index}`}>
                    <td><strong>{rowText(row, "vendor_name")}</strong></td>
                    <td>{rowText(row, "item_name")}</td>
                    <td>{rowText(row, "category_name")}</td>
                    <td>{formatNumber(remainingQuantity(row), 1)} {rowUnit(row)}</td>
                    <td>{formatIndianCurrency(rowNumber(row, "open_po_value"))}</td>
                    <td>{formatDate(rowText(row, "expected_delivery_date"))}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </TableShell>
        </PortalPanel>

        <PortalPanel
          title="Expected delivery breach"
          subtitle="Delayed open lines requiring escalation"
          badge={`${breachRows.length} lines`}
        >
          {breachRows.length ? (
            <TableShell label="Expected delivery breaches">
              <table>
                <thead>
                  <tr>
                    <th>PO</th>
                    <th>Vendor</th>
                    <th>Raw material</th>
                    <th>Pending qty</th>
                    <th>Expected</th>
                    <th>Exposure</th>
                  </tr>
                </thead>
                <tbody>
                  {breachRows.slice(0, 14).map((row, index) => (
                    <tr key={`${rowText(row, "po_number")}-${rowText(row, "item_code")}-${index}`}>
                      <td><strong>{rowText(row, "po_number")}</strong></td>
                      <td>{rowText(row, "vendor_name")}</td>
                      <td>{rowText(row, "item_name")}</td>
                      <td>{formatNumber(remainingQuantity(row), 1)} {rowUnit(row)}</td>
                      <td>{formatDate(rowText(row, "expected_delivery_date"))}</td>
                      <td>{formatIndianCurrency(rowNumber(row, "open_po_value"))}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </TableShell>
          ) : (
            <EmptyState>No expected-delivery breach matches this scope.</EmptyState>
          )}
        </PortalPanel>
      </div>
    </div>
  );
}
