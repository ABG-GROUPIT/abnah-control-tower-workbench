export type ZohoPortalCapability =
  | "native"
  | "native_better"
  | "custom_required";

export type ZohoPortalPreview =
  | "map"
  | "queue"
  | "table"
  | "funnel"
  | "scorecard"
  | "line"
  | "movement"
  | "waterfall"
  | "butterfly"
  | "bcg"
  | "heatmap"
  | "combo"
  | "quality";

export interface ZohoPortalFilterOption {
  label: string;
  value: string;
}

export interface ZohoPortalFilter {
  id: string;
  label: string;
  kind: "date" | "select" | "search";
  defaultValue: string;
  options?: ZohoPortalFilterOption[];
  placeholder?: string;
}

export interface ZohoPortalMetric {
  id: string;
  title: string;
  expectedValue: string;
  detail: string;
  zohoViewName: string;
  sourceQuery: string;
  sourceField: string;
  aggregation: string;
  capability: ZohoPortalCapability;
}

export interface ZohoPortalPanel {
  id: string;
  title: string;
  subtitle: string;
  zohoViewName: string;
  sourceQuery: string;
  sourceFields: string[];
  capability: ZohoPortalCapability;
  preview: ZohoPortalPreview;
  span: "half" | "full";
  embedUrl: string;
}

export interface ZohoPortalPage {
  id: string;
  label: string;
  title: string;
  subtitle: string;
  dashboardViewName: string;
  dashboardEmbedUrl: string;
  filterStrategy: "zoho_dashboard_user_filters";
  criteriaTable: string;
  criteriaColumns: Record<string, string>;
  filters: ZohoPortalFilter[];
  metrics: ZohoPortalMetric[];
  panels: ZohoPortalPanel[];
}

export interface ZohoPortalConfig {
  version: string;
  portalName: string;
  baselineLabel: string;
  defaultRange: {
    start: string;
    end: string;
  };
  auth: {
    mode: "zoho_secured_login";
    loginUrl: string;
    allowedEmail: string;
    shellProtection: "public_shell_zoho_protected_views";
  };
  pages: ZohoPortalPage[];
}

export type ZohoPortalUrlOverrides = Record<string, string>;
export type ZohoPortalDashboardUrlOverrides = Record<string, string>;

export interface ZohoPortalHandoffReport {
  viewName: string;
  securedViewUrl: string;
}

export interface ZohoPortalHandoffPage {
  dashboardViewName: string;
  securedDashboardFallbackUrl: string;
  reports: Record<string, ZohoPortalHandoffReport>;
}

export interface ZohoPortalHandoff {
  schema: "abnah-zoho-view-handoff/v4";
  generatedAt?: string;
  authMode: "zoho_secured_login";
  integrationMode: "individual_report_views_with_dashboard_fallbacks";
  note?: string;
  pages: Record<string, ZohoPortalHandoffPage>;
}

export interface ZohoPortalUrlMaps {
  reports: ZohoPortalUrlOverrides;
  dashboards: ZohoPortalDashboardUrlOverrides;
}

export interface ZohoPortalConfigEnvelope {
  handoff: ZohoPortalHandoff;
  version: number;
  updatedAt: string | null;
  updatedBy: string | null;
}

export interface ZohoPortalAuthSession {
  authenticated: boolean;
  configured: boolean;
  canConfigure: boolean;
  expiresAt?: number;
  missingEnvironment?: string[];
  user?: {
    displayName: string;
    email: string;
  };
  workspace?: {
    id: string;
    name: string;
    organizationId: string;
  };
}

export interface ZohoPortalFilterBinding {
  filterId: string;
  criteriaTable: string;
  criteriaColumn: string;
  operator: "equals" | "contains";
}
