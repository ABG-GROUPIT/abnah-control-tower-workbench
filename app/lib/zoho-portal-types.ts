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
  kind: "select" | "search";
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
  filterStrategy: "report_views";
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
  auth: {
    mode: "zoho_secured_login";
    loginUrl: string;
    allowedEmail: string;
    shellProtection: "public_shell_zoho_protected_views";
  };
  pages: ZohoPortalPage[];
}

export type ZohoPortalUrlOverrides = Record<string, string>;

export interface ZohoPortalHandoffView {
  pageId: string;
  slotKind: "kpi" | "report";
  zohoViewName: string;
  securedEmbedUrl: string;
}

export interface ZohoPortalHandoff {
  schema: "abnah-zoho-report-embed-handoff/v2";
  generatedAt?: string;
  authMode: "zoho_secured_login";
  integrationMode: "individual_report_views";
  note?: string;
  views: Record<string, ZohoPortalHandoffView>;
}

export interface ZohoPortalFilterBinding {
  filterId: string;
  criteriaTable: string;
  criteriaColumn: string;
  operator: "equals" | "contains";
}
