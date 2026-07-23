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
  | "control_only"
  | "source_supported_derived"
  | "unavailable_header_only"
  | "unavailable_not_enabled"
  | "planned_derived"
  | "planned_partial"
  | "blocked_source_unavailable";

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
  kind: "report" | "master" | "table" | "derived_reference";
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
  catalogState?:
    | "catalogued"
    | "external_reference"
    | "not_a_report"
    | "catalogued_unavailable"
    | "catalogued_not_enabled";
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
