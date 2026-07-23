export type LineageNodeKind =
  | "source_report"
  | "raw"
  | "std"
  | "dimension"
  | "fact"
  | "summary"
  | "kpi"
  | "chart";

export interface KpiDefinition {
  id: string;
  pageId: string;
  name: string;
  businessDefinition: string;
  owner: string;
  approvalStatus: "draft" | "approved" | "retired" | "blocked" | "provisional" | "partial";
  validationStatus: string;
  grain: string;
  formula: string;
  caveats: string[];
}

export interface LineageNode {
  id: string;
  kpiId: string;
  kind: LineageNodeKind;
  refId: string;
  label: string;
  layerOrder: number;
  notes: string;
}

export interface LineageEdge {
  id: string;
  kpiId: string;
  sourceNodeId: string;
  targetNodeId: string;
  transformation: string;
  joinKeys: string[];
  decisionStatus: "candidate" | "selected" | "rejected" | "deferred";
  rationale: string;
}

export interface LineagePublication {
  id: string;
  kpiId: string;
  version: number;
  publishedAt: string;
  publishedBy: string;
}

export interface KpiLineageContract {
  contractVersion: string;
  status: "awaiting_kpi_approval" | "requirements_received" | "active";
  sourcePolicy: string;
  kpiDefinitionSource?: string;
  kpis: KpiDefinition[];
  nodes: LineageNode[];
  edges: LineageEdge[];
  publications: LineagePublication[];
}
