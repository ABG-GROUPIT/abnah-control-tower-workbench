import type {
  ZohoPortalConfig,
  ZohoPortalHandoff,
  ZohoPortalHandoffReport,
  ZohoPortalUrlMaps,
} from "./zoho-portal-types";

export const zohoPortalHandoffSchema = "abnah-zoho-view-handoff/v4" as const;

export function isSecuredZohoUrl(value: string) {
  if (!value) return true;
  try {
    const url = new URL(value);
    const host = url.hostname.toLowerCase();
    const approvedHost =
      /^analytics\.zoho\.(com|in|eu|jp|ca|sa)$/.test(host) ||
      host === "analytics.zoho.com.au";
    return url.protocol === "https:" && approvedHost;
  } catch {
    return false;
  }
}

function cleanUrl(value: unknown, label: string) {
  if (typeof value !== "string") return "";
  const url = value.trim();
  if (url && !isSecuredZohoUrl(url)) {
    throw new Error(`${label}: enter an HTTPS Zoho Analytics URL.`);
  }
  return url;
}

function reportUrl(report: unknown) {
  if (!report || typeof report !== "object" || Array.isArray(report)) return "";
  const candidate = report as Record<string, unknown>;
  return candidate.securedViewUrl ?? candidate.securedEmbedUrl ?? "";
}

function reportViewName(report: unknown) {
  if (!report || typeof report !== "object" || Array.isArray(report)) return "";
  const candidate = report as Record<string, unknown>;
  const value = candidate.viewName ?? candidate.zohoViewName;
  return typeof value === "string" ? value : "";
}

export function buildZohoPortalHandoff(
  portal: ZohoPortalConfig,
  maps: ZohoPortalUrlMaps,
): ZohoPortalHandoff {
  return {
    schema: zohoPortalHandoffSchema,
    generatedAt: new Date().toISOString(),
    authMode: "zoho_secured_login",
    integrationMode: "individual_report_views_with_dashboard_fallbacks",
    note:
      "Backward-compatible QA artifact only. Production uses authenticated Query Table API exports and does not require these URLs. Do not add passwords, OAuth secrets, tokens, or operational rows.",
    pages: Object.fromEntries(
      portal.pages.map((page) => [
        page.id,
        {
          dashboardViewName: page.dashboardViewName,
          securedDashboardFallbackUrl:
            maps.dashboards[page.id]?.trim() ?? "",
          reports: Object.fromEntries(
            page.panels.map((panel) => [
              panel.id,
              {
                viewName: panel.zohoViewName,
                securedViewUrl: maps.reports[panel.id]?.trim() ?? "",
              } satisfies ZohoPortalHandoffReport,
            ]),
          ),
        },
      ]),
    ),
  };
}

export function normalizeZohoPortalHandoff(
  value: unknown,
  portal: ZohoPortalConfig,
): ZohoPortalHandoff {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new Error("The selected file is not a Zoho portal handoff.");
  }
  const candidate = value as Record<string, unknown>;
  if (
    candidate.schema !== zohoPortalHandoffSchema ||
    candidate.authMode !== "zoho_secured_login" ||
    candidate.integrationMode !==
      "individual_report_views_with_dashboard_fallbacks" ||
    !candidate.pages ||
    typeof candidate.pages !== "object" ||
    Array.isArray(candidate.pages)
  ) {
    throw new Error(
      "Use an ABNAH secured individual-view handoff v4 JSON file.",
    );
  }

  const inputPages = candidate.pages as Record<string, unknown>;
  const maps: ZohoPortalUrlMaps = { reports: {}, dashboards: {} };

  for (const page of portal.pages) {
    const inputPage =
      inputPages[page.id] &&
      typeof inputPages[page.id] === "object" &&
      !Array.isArray(inputPages[page.id])
        ? (inputPages[page.id] as Record<string, unknown>)
        : {};
    maps.dashboards[page.id] = cleanUrl(
      inputPage.securedDashboardFallbackUrl ??
        inputPage.securedDashboardEmbedUrl,
      page.dashboardViewName,
    );

    const inputReports =
      inputPage.reports &&
      typeof inputPage.reports === "object" &&
      !Array.isArray(inputPage.reports)
        ? (inputPage.reports as Record<string, unknown>)
        : {};
    const reportEntries = Object.entries(inputReports);
    for (const panel of page.panels) {
      const direct = inputReports[panel.id];
      const matching = reportEntries.find(
        ([, report]) => reportViewName(report) === panel.zohoViewName,
      )?.[1];
      maps.reports[panel.id] = cleanUrl(
        reportUrl(direct ?? matching),
        panel.zohoViewName,
      );
    }
  }

  return buildZohoPortalHandoff(portal, maps);
}

export function handoffToUrlMaps(
  handoff: ZohoPortalHandoff,
  portal: ZohoPortalConfig,
): ZohoPortalUrlMaps {
  const normalized = normalizeZohoPortalHandoff(handoff, portal);
  const maps: ZohoPortalUrlMaps = { reports: {}, dashboards: {} };
  for (const page of portal.pages) {
    const pageHandoff = normalized.pages[page.id];
    maps.dashboards[page.id] =
      pageHandoff?.securedDashboardFallbackUrl ?? "";
    for (const panel of page.panels) {
      maps.reports[panel.id] =
        pageHandoff?.reports[panel.id]?.securedViewUrl ?? "";
    }
  }
  return maps;
}
