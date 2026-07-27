import type { ZohoEnvironment } from "./zoho.ts";

export type PortalDataPage = "p1" | "p2";

interface SessionWorkspace {
  workspace_id: string;
  organization_id: string;
}

interface ExportSpec {
  dataset: string;
  viewName: string;
  dateField: string;
}

export type ZohoViewUrlMode = "embed" | "source";

export interface ZohoResolvedViewUrl {
  viewName: string;
  viewId: string;
  viewType: string;
  mode: ZohoViewUrlMode;
  url: string;
}

interface CachedPageData {
  expiresAt: number;
  value: {
    datasets: Record<string, Record<string, unknown>[]>;
    datasetErrors: Record<string, string>;
  };
}

interface ZohoViewMetadata {
  id: string;
  type: string;
}

const pageCacheTtlMs = 2 * 60 * 1000;
const pageCache = new Map<string, CachedPageData>();
const pageRequests = new Map<
  string,
  Promise<CachedPageData["value"]>
>();
let exportQueue: Promise<void> = Promise.resolve();

const pageExports: Record<PortalDataPage, ExportSpec[]> = {
  p1: [
    {
      dataset: "inventoryRisk",
      viewName: "27_fact_ct_inventory_risk.sql",
      dateField: "snapshot_date",
    },
    {
      dataset: "menuImpact",
      viewName: "28_fact_ct_menu_impact.sql",
      dateField: "snapshot_date",
    },
    {
      dataset: "expiryRisk",
      viewName: "38_fact_ct_expiry_risk.sql",
      dateField: "as_of_date",
    },
    {
      dataset: "riskyPo",
      viewName: "36_fact_ct_risky_po.sql",
      dateField: "as_of_date",
    },
  ],
  p2: [
    {
      dataset: "purchaseOrders",
      viewName: "22_fact_ct_purchase_order.sql",
      dateField: "po_date",
    },
    {
      dataset: "poReceiptLines",
      viewName: "24_fact_ct_po_receipt_line.sql",
      dateField: "po_date",
    },
    {
      dataset: "purchaseReceipts",
      viewName: "23_fact_ct_purchase_receipt.sql",
      dateField: "receipt_date",
    },
    {
      dataset: "priceMovement",
      viewName: "31_sum_ct_price_movement.sql",
      dateField: "price_as_of_date",
    },
  ],
};

function apiHeaders(accessToken: string, organizationId: string) {
  return {
    Authorization: `Zoho-oauthtoken ${accessToken}`,
    "ZANALYTICS-ORGID": organizationId,
  };
}

async function jsonResponse(response: Response, fallback: string) {
  const payload = (await response.json().catch(() => null)) as
    | Record<string, unknown>
    | null;
  if (!response.ok || !payload) {
    throw new Error(fallback);
  }
  if (payload.status === "failure") {
    const data =
      payload.data && typeof payload.data === "object"
        ? (payload.data as Record<string, unknown>)
        : {};
    throw new Error(String(data.errorMessage || fallback));
  }
  return payload;
}

function objectAt(value: unknown, key: string) {
  return value && typeof value === "object" && !Array.isArray(value)
    ? (value as Record<string, unknown>)[key]
    : undefined;
}

function stringAt(value: unknown, key: string) {
  const candidate = objectAt(value, key);
  return typeof candidate === "string" || typeof candidate === "number"
    ? String(candidate)
    : "";
}

function findObjectRows(value: unknown): Record<string, unknown>[] {
  if (Array.isArray(value)) {
    if (
      value.every(
        (row) => row && typeof row === "object" && !Array.isArray(row),
      )
    ) {
      return value as Record<string, unknown>[];
    }
    for (const child of value) {
      const rows = findObjectRows(child);
      if (rows.length) return rows;
    }
    return [];
  }
  if (!value || typeof value !== "object") return [];
  for (const child of Object.values(value)) {
    const rows = findObjectRows(child);
    if (rows.length) return rows;
  }
  return [];
}

function normalizeZohoDate(value: unknown) {
  if (typeof value !== "string") return value;
  const clean = value.trim();
  const iso = clean.match(/^(\d{4}-\d{2}-\d{2})(?:[T\s].*)?$/);
  if (iso) return iso[1];
  const zoho = clean.match(
    /^(\d{1,2})\s+([A-Za-z]{3}),\s*(\d{4})(?:\s+.*)?$/,
  );
  if (!zoho) return value;
  const months: Record<string, string> = {
    Jan: "01",
    Feb: "02",
    Mar: "03",
    Apr: "04",
    May: "05",
    Jun: "06",
    Jul: "07",
    Aug: "08",
    Sep: "09",
    Oct: "10",
    Nov: "11",
    Dec: "12",
  };
  const month =
    months[zoho[2][0].toUpperCase() + zoho[2].slice(1).toLowerCase()];
  return month
    ? `${zoho[3]}-${month}-${zoho[1].padStart(2, "0")}`
    : value;
}

function normalizeExportRows(rows: Record<string, unknown>[]) {
  return rows.map((row) =>
    Object.fromEntries(
      Object.entries(row).map(([key, value]) => [
        key,
        /(date|_at|period_start|period_end)$/i.test(key)
          ? normalizeZohoDate(value)
          : value,
      ]),
    )
  );
}

function serializedExport<T>(operation: () => Promise<T>) {
  const current = exportQueue.then(operation, operation);
  exportQueue = current.then(
    () => undefined,
    () => undefined,
  );
  return current;
}

async function accessibleViews(
  environment: ZohoEnvironment,
  session: SessionWorkspace,
  accessToken: string,
  queryTablesOnly = false,
) {
  const url = new URL(
    `${environment.analyticsApiBaseUrl}/restapi/v2/workspaces/${session.workspace_id}/views`,
  );
  const config: Record<string, unknown> = {
    noOfResult: 200,
    startIndex: 1,
    sortedColumn: 0,
    sortedOrder: 0,
  };
  if (queryTablesOnly) config.viewTypes = [6];
  url.searchParams.set(
    "CONFIG",
    JSON.stringify(config),
  );
  const response = await fetch(url, {
    headers: apiHeaders(accessToken, session.organization_id),
  });
  const payload = await jsonResponse(
    response,
    "Zoho query-table metadata could not be loaded.",
  );
  const views = findObjectRows(objectAt(payload, "data"));
  return new Map(
    views.flatMap((view) => {
      const name = stringAt(view, "viewName");
      const id = stringAt(view, "viewId");
      const type =
        stringAt(view, "viewType") ||
        stringAt(view, "viewTypeName") ||
        "View";
      return name && id
        ? [[name, { id, type } satisfies ZohoViewMetadata] as const]
        : [];
    }),
  );
}

function dateCriteria(dateField: string, start: string, end: string) {
  return `("${dateField}" BETWEEN '${start}' AND '${end}')`;
}

async function startExport(
  environment: ZohoEnvironment,
  session: SessionWorkspace,
  accessToken: string,
  viewId: string,
  spec: ExportSpec,
  start: string,
  end: string,
) {
  const url = new URL(
    `${environment.analyticsApiBaseUrl}/restapi/v2/bulk/workspaces/${session.workspace_id}/views/${viewId}/data`,
  );
  url.searchParams.set(
    "CONFIG",
    JSON.stringify({
      responseFormat: "json",
      keyValueFormat: true,
      showHiddenCols: true,
      criteria: dateCriteria(spec.dateField, start, end),
    }),
  );
  const response = await fetch(url, {
    headers: apiHeaders(accessToken, session.organization_id),
  });
  const payload = await jsonResponse(
    response,
    `${spec.viewName} export could not be started.`,
  );
  const jobId = stringAt(objectAt(payload, "data"), "jobId");
  if (!jobId) throw new Error(`${spec.viewName} did not return an export job.`);
  return jobId;
}

async function waitForExport(
  environment: ZohoEnvironment,
  session: SessionWorkspace,
  accessToken: string,
  jobId: string,
  viewName: string,
) {
  const statusUrl =
    `${environment.analyticsApiBaseUrl}/restapi/v2/bulk/workspaces/` +
    `${session.workspace_id}/exportjobs/${jobId}`;
  for (let attempt = 0; attempt < 32; attempt += 1) {
    const response = await fetch(statusUrl, {
      headers: apiHeaders(accessToken, session.organization_id),
    });
    const payload = await jsonResponse(
      response,
      `${viewName} export status could not be checked.`,
    );
    const data = objectAt(payload, "data");
    const status = stringAt(data, "jobStatus").toUpperCase();
    if (status.includes("COMPLETED")) {
      return stringAt(data, "downloadUrl");
    }
    if (status.includes("FAILED")) {
      throw new Error(`${viewName} export failed in Zoho Analytics.`);
    }
    await new Promise((resolve) =>
      setTimeout(resolve, Math.min(1_500, 250 + attempt * 75))
    );
  }
  throw new Error(`${viewName} export did not finish in time.`);
}

async function downloadExport(
  environment: ZohoEnvironment,
  session: SessionWorkspace,
  accessToken: string,
  jobId: string,
  downloadUrl: string,
  viewName: string,
) {
  const url =
    downloadUrl ||
    `${environment.analyticsApiBaseUrl}/restapi/v2/bulk/workspaces/` +
      `${session.workspace_id}/exportjobs/${jobId}/data`;
  const response = await fetch(url, {
    headers: apiHeaders(accessToken, session.organization_id),
  });
  const payload = (await response.json().catch(() => null)) as unknown;
  if (!response.ok || payload === null) {
    throw new Error(`${viewName} export could not be downloaded.`);
  }
  return normalizeExportRows(findObjectRows(payload));
}

async function exportDataset(
  environment: ZohoEnvironment,
  session: SessionWorkspace,
  accessToken: string,
  queryTables: Map<string, ZohoViewMetadata>,
  spec: ExportSpec,
  start: string,
  end: string,
) {
  const view = queryTables.get(spec.viewName);
  if (!view) {
    throw new Error(
      `${spec.viewName} is not available to the signed-in Zoho account.`,
    );
  }
  return serializedExport(async () => {
    const jobId = await startExport(
      environment,
      session,
      accessToken,
      view.id,
      spec,
      start,
      end,
    );
    const downloadUrl = await waitForExport(
      environment,
      session,
      accessToken,
      jobId,
      spec.viewName,
    );
    return downloadExport(
      environment,
      session,
      accessToken,
      jobId,
      downloadUrl,
      spec.viewName,
    );
  });
}

async function loadControlTowerPageData(
  environment: ZohoEnvironment,
  session: SessionWorkspace,
  accessToken: string,
  page: PortalDataPage,
  start: string,
  end: string,
) {
  const queryTables = await accessibleViews(
    environment,
    session,
    accessToken,
    true,
  );

  const datasets: Record<string, Record<string, unknown>[]> = {};
  const datasetErrors: Record<string, string> = {};
  for (const spec of pageExports[page]) {
    try {
      datasets[spec.dataset] = await exportDataset(
        environment,
        session,
        accessToken,
        queryTables,
        spec,
        start,
        end,
      );
    } catch (error) {
      datasets[spec.dataset] = [];
      datasetErrors[spec.dataset] =
        error instanceof Error
          ? error.message
          : `${spec.viewName} could not be exported.`;
    }
  }

  return { datasets, datasetErrors };
}

export async function fetchControlTowerPageData(
  environment: ZohoEnvironment,
  session: SessionWorkspace,
  accessToken: string,
  page: PortalDataPage,
  start: string,
  end: string,
) {
  const cacheKey = [
    session.organization_id,
    session.workspace_id,
    page,
    start,
    end,
  ].join(":");
  const cached = pageCache.get(cacheKey);
  if (cached && cached.expiresAt > Date.now()) return cached.value;

  const activeRequest = pageRequests.get(cacheKey);
  if (activeRequest) return activeRequest;

  const request = loadControlTowerPageData(
    environment,
    session,
    accessToken,
    page,
    start,
    end,
  ).then((value) => {
    pageCache.set(cacheKey, {
      expiresAt: Date.now() + pageCacheTtlMs,
      value,
    });
    return value;
  }).finally(() => {
    pageRequests.delete(cacheKey);
  });
  pageRequests.set(cacheKey, request);
  return request;
}

export async function fetchZohoViewUrl(
  environment: ZohoEnvironment,
  session: SessionWorkspace,
  accessToken: string,
  viewName: string,
  criteria: string,
  mode: ZohoViewUrlMode,
): Promise<ZohoResolvedViewUrl> {
  const views = await accessibleViews(
    environment,
    session,
    accessToken,
  );
  const view = views.get(viewName);
  if (!view) {
    throw new Error(
      `${viewName} is not available to the signed-in Zoho account.`,
    );
  }

  if (mode === "source") {
    const analyticsUiBaseUrl = environment.analyticsApiBaseUrl.replace(
      "://analyticsapi.",
      "://analytics.",
    );
    return {
      viewName,
      viewId: view.id,
      viewType: view.type,
      mode,
      url:
        `${analyticsUiBaseUrl}/workspace/${session.workspace_id}/edit/` +
        `${view.id}`,
    };
  }

  const suffix = mode === "embed" ? "/publish/embed" : "/publish";
  const url = new URL(
    `${environment.analyticsApiBaseUrl}/restapi/v2/workspaces/${session.workspace_id}/views/${view.id}${suffix}`,
  );
  const config: Record<string, unknown> = {
    includeTitle: false,
    includeDesc: false,
    includeToolBar: false,
    includeSearchBox: false,
  };
  if (criteria) config.criteria = criteria;
  config.validityPeriod = 900;
  config.permissions = {
    export: false,
    vud: true,
    drillDown: true,
    insight: false,
  };
  url.searchParams.set("CONFIG", JSON.stringify(config));

  const response = await fetch(url, {
    headers: apiHeaders(accessToken, session.organization_id),
  });
  const payload = await jsonResponse(
    response,
    `${viewName} could not produce a secured embed URL.`,
  );
  const data = objectAt(payload, "data");
  const resolved =
    stringAt(data, "embedUrl") ||
    stringAt(data, "viewUrl") ||
    stringAt(data, "embedURL");
  if (!resolved) {
    throw new Error(`${viewName} did not return a usable Zoho URL.`);
  }

  return {
    viewName,
    viewId: view.id,
    viewType: view.type,
    mode,
    url: resolved,
  };
}
