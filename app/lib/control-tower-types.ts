export type ControlTowerStatus = "requirements_received_pending_source_validation";
export type KpiApprovalStatus = "draft" | "approved" | "retired";
export type CapturePriority = "P0" | "P1" | "P2";

export interface ControlTowerRule {
  label: string;
  meaning: string;
  condition: string;
}

export interface ControlTowerVisualModule {
  order: number;
  name: string;
  question: string;
  logic: string;
}

export interface ControlTowerPage {
  id: string;
  number: number;
  name: string;
  purpose: string;
  audiences: string[];
  decisionFlow: string[];
  kpiIds: string[];
  visualModules: ControlTowerVisualModule[];
  rules: ControlTowerRule[];
}

export interface ControlTowerKpi {
  id: string;
  pageId: string;
  name: string;
  businessDefinition: string;
  formula: string;
  grain: string;
  owner: string;
  approvalStatus: KpiApprovalStatus;
  validationStatus: string;
  caveats: string[];
}

export interface CaptureReportCandidate {
  reportId: string;
  name: string;
  role: "primary_candidate" | "comparison_candidate" | "reconciliation_candidate" | "validation_candidate";
  reason: string;
}

export interface CaptureGroup {
  id: string;
  priority: CapturePriority;
  purpose: string;
  reports: CaptureReportCandidate[];
  decisionGate: string;
}

export interface ApiAssessmentItem {
  endpointId: string;
  name: string;
  fit: string;
  status: "candidate" | "passed" | "partial" | "failed" | "blocked";
  coverage: string[];
  gaps: string[];
}

export interface ControlTowerRequirements {
  contractVersion: string;
  status: ControlTowerStatus;
  sourcePolicy: string;
  terminology: {
    preferredTerm: string;
    replacedTerm: string;
    rule: string;
  };
  discoveryProgress: {
    reportedCheckpoint: string;
    reportId: string;
    status: string;
    note: string;
  };
  pages: ControlTowerPage[];
  kpis: ControlTowerKpi[];
  capturePlan: {
    principles: string[];
    groups: CaptureGroup[];
    deferredAreas: string[];
  };
  apiAssessment: {
    status: string;
    strategy: string;
    endpoints: ApiAssessmentItem[];
    knownCoverageGaps: string[];
  };
  modelRevision: {
    decision: string;
    rationale: string;
    retain: string[];
    revise: string[];
    add: string[];
    defer: string[];
  };
  deliveryPlan: {
    pocIngestion: string;
    productionIngestion: string;
    analytics: string;
    presentation: string;
    validationSequence: string[];
  };
}
