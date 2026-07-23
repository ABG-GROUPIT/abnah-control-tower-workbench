export interface EvidenceSummary {
  selectedSourceCount: number;
  primarySourceCount: number;
  auxiliarySourceCount: number;
  controlSourceCount: number;
  auditedReportCount: number;
  auditedFileCount: number;
  auditedRowCount: number;
  schemaContractMatches: number;
  schemaVisualMatches: number;
  headerOnlyReportCount: number;
  deterministicIssueRowCount: number;
}

export interface EvidenceSource {
  id: string;
  sourceName: string;
  sourceTable: string;
  modelRole: string;
  roleGroup: "primary" | "auxiliary" | "control";
  pages: string[];
  requiredFields: string[];
  productionDecision: string;
  fallbackOrReconciliation: string;
  auditReportId: string;
  workbenchReportId: string;
  auditStatus: "populated" | "header_only" | "not_in_local_export_set";
  rowCount: number;
}

export interface EvidenceFinding {
  id: string;
  category: string;
  severity: string;
  title: string;
  affectedRowCount: number;
  fields: string[];
  observation: string;
  productionTreatment: string;
}

export interface EvidenceRowValue {
  field: string;
  label: string;
  value: string;
}

export interface EvidenceRow {
  id: string;
  findingId: string;
  exportLabel: string;
  sourceRowNumber: number;
  values: EvidenceRowValue[];
  expected: string;
  observed: string;
  privacy: string;
}

export interface EvidenceFieldCoverage {
  field: string;
  label: string;
  declaredType: string;
  totalCount: number;
  nonNullCount: number;
  nullCount: number;
  zeroCount: number;
  negativeCount: number;
  parseErrorCount: number;
  coverageStatus: "complete" | "partial" | "weak" | "missing";
  coveragePercent: number;
}

export interface EvidenceReport {
  reportId: string;
  displayName: string;
  selection: {
    status: "selected" | "evaluated_not_selected";
    modelRole: string;
    roleGroup: "primary" | "auxiliary" | "control" | "evaluated";
    pages: string[];
    sourceTable: string;
    reason: string;
  };
  filesAudited: number;
  rowsAudited: number;
  emptyFileCount: number;
  duplicateRowCount: number;
  periods: string[];
  schema: {
    contractMatch: "exact" | "difference_detected";
    contractVariantCount: number;
    status: "exact";
    workbenchReportId: string;
    matchedVariantId: string;
    matchedVariantName: string;
    columnCount: number;
    statement: string;
  };
  readiness:
    | "blocked_header_only"
    | "review_required"
    | "schema_ready_value_checks_passed";
  decision: string;
  keyFieldCoverage: EvidenceFieldCoverage[];
  findings: EvidenceFinding[];
  evidenceRows: EvidenceRow[];
}

export interface ControlTowerEvidence {
  contractVersion: string;
  status: string;
  asOfDate: string;
  sourcePolicy: string;
  privacy: {
    rawFilesRemainLocal: boolean;
    fullRowsIncluded: boolean;
    sensitiveValuesIncluded: boolean;
    issueExcerptPolicy: string;
  };
  decision: {
    headline: string;
    reason: string;
    productionRule: string;
  };
  summary: EvidenceSummary;
  sourceRegister: EvidenceSource[];
  reportEvidence: EvidenceReport[];
}
