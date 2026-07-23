export type PresentationStoryKind = "kpi" | "chart" | "table";

export interface PresentationPage {
  id: string;
  number: number;
  name: string;
  purpose: string;
}

export interface PresentationSourceReport {
  name: string;
  reportId: string;
  role: string;
  fields: string[];
  evidence: "captured_posist_report" | "synthetic_model_input";
}

export interface PresentationSourceProfile {
  grain: string;
  reports: PresentationSourceReport[];
  inherits?: string[];
  route: string[];
  lookups: string[];
  joinLogic: string;
  guardrails: string[];
}

export interface PresentationZohoConfig {
  shelves: string[];
  fixedFilters: string[];
  userFilters: string[];
  sort: string;
  tooltips: string[];
  formatting: string[];
}

export interface PresentationStory {
  id: string;
  pageId: string;
  name: string;
  kind: PresentationStoryKind;
  visual: string;
  sourceTable: string;
  question: string;
  finalFields: string[];
  formula: string;
  aggregation: string;
  zoho: PresentationZohoConfig;
  caveats: string[];
  talkTrack: string;
}

export interface ControlTowerPresentation {
  contractVersion: string;
  status: string;
  title: string;
  sourcePolicy: string;
  syncPolicy: string;
  pages: PresentationPage[];
  sourceProfiles: Record<string, PresentationSourceProfile>;
  stories: PresentationStory[];
  counts: {
    pages: number;
    stories: number;
    kpis: number;
    charts: number;
    tables: number;
    queryTables: number;
  };
}

export interface ModelLayerDefinition {
  id: "raw" | "standardized" | "dimension" | "fact" | "summary";
  order: number;
  label: string;
  shortLabel: string;
  purpose: string;
  example: string;
}

export interface ModelTableDefinition {
  buildOrder: number;
  layer: "standardized" | "dimension" | "fact" | "summary";
  physicalName: string;
  logicalName: string;
  dependencyLevel: number;
  purpose: string;
  sources: string[];
  dependencies: string[];
  rawInputs: string[];
  sql: string;
}

export interface ControlTowerModel {
  contractVersion: string;
  title: string;
  sourcePolicy: string;
  layers: ModelLayerDefinition[];
  tables: ModelTableDefinition[];
}
