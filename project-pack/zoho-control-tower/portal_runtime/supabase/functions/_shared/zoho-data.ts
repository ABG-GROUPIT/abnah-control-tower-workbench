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

async function accessibleQueryTables(
  environment: ZohoEnvironment,
  session: SessionWorkspace,
  accessToken: string,
) {
  const url = new URL(
    `${environment.analyticsApiBaseUrl}/restapi/v2/workspaces/${session.workspace_id}/views`,
  );
  url.searchParams.set(
    "CONFIG",
    JSON.stringify({
      viewTypes: [6],
      noOfResult: 200,
      startIndex: 1,
      sortedColumn: 0,
      sortedOrder: 0,
    }),
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
      return name && id ? [[name, id] as const] : [];
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
  return findObjectRows(payload);
}

async function exportDataset(
  environment: ZohoEnvironment,
  session: SessionWorkspace,
  accessToken: string,
  queryTables: Map<string, string>,
  spec: ExportSpec,
  start: string,
  end: string,
) {
  const viewId = queryTables.get(spec.viewName);
  if (!viewId) {
    throw new Error(
      `${spec.viewName} is not available to the signed-in Zoho account.`,
    );
  }
  const jobId = await startExport(
    environment,
    session,
    accessToken,
    viewId,
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
}

export async function fetchControlTowerPageData(
  environment: ZohoEnvironment,
  session: SessionWorkspace,
  accessToken: string,
  page: PortalDataPage,
  start: string,
  end: string,
) {
  const queryTables = await accessibleQueryTables(
    environment,
    session,
    accessToken,
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
