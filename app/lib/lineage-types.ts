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
  name: string;
  businessDefinition: string;
  owner: string;
  approvalStatus: "draft" | "approved" | "retired";
  grain: string;
  formula: string;
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
  status: "awaiting_kpi_approval" | "active";
  sourcePolicy: string;
  kpis: KpiDefinition[];
  nodes: LineageNode[];
  edges: LineageEdge[];
  publications: LineagePublication[];
}
