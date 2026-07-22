export type ArchitectureLayerId =
  | "source"
  | "raw"
  | "standardized"
  | "dimension"
  | "fact"
  | "summary"
  | "kpi"
  | "experience";

export type ArchitectureNodeStatus =
  | "selected_for_validation"
  | "conditional"
  | "required_gap"
  | "planned"
  | "definition_ready"
  | "control_only";

export interface ArchitectureLayer {
  id: ArchitectureLayerId;
  label: string;
  shortLabel: string;
  order: number;
  description: string;
}

export interface ArchitectureGroup {
  id: string;
  label: string;
  description: string;
}

export interface ArchitectureNode {
  id: string;
  layerId: Exclude<ArchitectureLayerId, "kpi" | "experience">;
  groupId: string;
  kind: "report" | "master" | "table";
  label: string;
  description: string;
  status: ArchitectureNodeStatus;
  role: string;
  pages: string[];
  dataPoints: string[];
  inputs: string[];
  logic: string;
  alternatives: string[];
  reportId?: string;
  catalogState?: "catalogued" | "external_reference";
}

export interface ArchitectureKpiRoute {
  summaryNodeId: string;
  kpiIds: string[];
}

export interface ArchitectureDecision {
  id: string;
  title: string;
  decision: string;
  rationale: string;
  status: "adopted" | "conditional" | "pending_validation";
}

export interface ControlTowerArchitecture {
  contractVersion: string;
  status: "planned_architecture_under_feasibility_validation";
  title: string;
  sourcePolicy: string;
  currentPhase: {
    label: string;
    state: "in_progress";
    description: string;
    nextGate: string;
  };
  layers: ArchitectureLayer[];
  groups: ArchitectureGroup[];
  sourceNodes: ArchitectureNode[];
  modelNodes: ArchitectureNode[];
  kpiRoutes: ArchitectureKpiRoute[];
  decisions: ArchitectureDecision[];
}
