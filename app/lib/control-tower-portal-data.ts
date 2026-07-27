export type PortalPageId = "p1" | "p2";
export type PortalRow = Record<string, unknown>;

export interface PortalPageDatasets {
  [dataset: string]: PortalRow[];
}

export interface PortalPageData {
  schema: "abnah-control-tower-portal-page/v1";
  page: PortalPageId;
  generatedAt: string;
  source: "zoho_analytics" | "synthetic_validation_truth";
  dataBoundary: string;
  datasets: PortalPageDatasets;
  datasetErrors?: Record<string, string>;
}

export interface PortalDemoData {
  schema: "abnah-control-tower-portal-data/v1";
  generatedAt: string;
  source: "synthetic_validation_truth";
  dataBoundary: string;
  defaultRange: {
    start: string;
    end: string;
  };
  outlets: PortalRow[];
  pages: Record<PortalPageId, PortalPageDatasets>;
}

export function rowText(row: PortalRow, key: string) {
  const value = row[key];
  return value === null || value === undefined ? "" : String(value);
}

export function rowNumber(row: PortalRow, key: string) {
  const value = row[key];
  if (typeof value === "number") return Number.isFinite(value) ? value : 0;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

export function rowBoolean(row: PortalRow, key: string) {
  const value = row[key];
  if (typeof value === "boolean") return value;
  if (typeof value === "number") return value !== 0;
  return ["1", "true", "yes"].includes(String(value).toLowerCase());
}

export function uniqueValues(rows: PortalRow[], key: string) {
  return Array.from(
    new Set(rows.map((row) => rowText(row, key)).filter(Boolean)),
  ).sort((left, right) => left.localeCompare(right));
}

export function inDateRange(
  value: string,
  start: string,
  end: string,
) {
  if (!value) return false;
  return value >= start && value <= end;
}

export function formatIndianCurrency(
  value: number,
  options: { compact?: boolean; decimals?: number } = {},
) {
  const { compact = true, decimals = 1 } = options;
  const absolute = Math.abs(value);
  const sign = value < 0 ? "-" : "";
  if (compact && absolute >= 10_000_000) {
    return `${sign}₹${(absolute / 10_000_000).toFixed(decimals)}Cr`;
  }
  if (compact && absolute >= 100_000) {
    return `${sign}₹${(absolute / 100_000).toFixed(decimals)}L`;
  }
  if (compact && absolute >= 1_000) {
    return `${sign}₹${(absolute / 1_000).toFixed(decimals)}K`;
  }
  return `${sign}₹${new Intl.NumberFormat("en-IN", {
    maximumFractionDigits: options.decimals ?? 0,
  }).format(absolute)}`;
}

export function formatNumber(value: number, decimals = 0) {
  return new Intl.NumberFormat("en-IN", {
    maximumFractionDigits: decimals,
    minimumFractionDigits: decimals,
  }).format(value);
}

export function formatPercent(value: number, decimals = 1) {
  return `${formatNumber(value, decimals)}%`;
}

export function formatDate(value: string) {
  if (!value) return "Not available";
  const date = new Date(`${value}T00:00:00`);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(date);
}

export function severityRank(value: string) {
  return { PURPLE: 4, RED: 3, AMBER: 2, GREEN: 1 }[value] ?? 0;
}

export function clampPresentedQuantity(value: number) {
  return Math.max(0, value);
}
