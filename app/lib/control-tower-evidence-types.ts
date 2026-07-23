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
  semanticFindingCount: number;
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
  auditStatus:
    | "populated"
    | "header_only"
    | "not_in_local_export_set"
    | "historical_schema_with_documented_quality_gate";
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
  semanticReview: {
    classification:
      | "formula_definition_gate"
      | "reconciliation_exception"
      | "coverage_blocker"
      | "cost_coverage_gap"
      | "operational_exception"
      | "deduplication_risk"
      | "review_required";
    confidence: "high" | "medium" | "low";
    assessment: string;
    businessQuestion: string;
  };
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

export interface EvidenceReportContextColumn {
  field: string;
  label: string;
  sensitive: boolean;
}

export interface EvidenceReportContextRow {
  sourceRowNumber: number;
  state: "issue" | "context";
  values: EvidenceRowValue[];
}

export interface EvidenceReportContext {
  mode: "hosted_structure_local_values";
  statement: string;
  columns: EvidenceReportContextColumn[];
  exports: Array<{
    label: string;
    rowCount: number;
    headerRowNumber: number;
    issueObservationCount: number;
    issueDensity: number[];
  }>;
  contextWindows: Array<{
    id: string;
    findingId: string;
    exportLabel: string;
    focusSourceRowNumber: number;
    rows: EvidenceReportContextRow[];
  }>;
  localViewerUrl: string;
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
  codexReview: {
    status:
      | "coverage_blocked"
      | "coverage_review"
      | "definition_review"
      | "business_review"
      | "no_encoded_exception";
    headline: string;
    assessment: string;
    confirmedStructuralErrorCount: number;
    classificationCounts: Record<string, number | undefined>;
    nextDecision: string;
  };
  keyFieldCoverage: EvidenceFieldCoverage[];
  findings: EvidenceFinding[];
  evidenceRows: EvidenceRow[];
  reportContext: EvidenceReportContext;
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
  zohoReadiness: {
    demoBuild: "ready";
    productionModelBuild: "ready_with_gates";
    productionPublication: "blocked_pending_signoff";
    requiredLandingTableCount: number;
    queryTableCount: number;
    dashboardTabCount: number;
    migrationRule: string;
    nextSequence: string[];
  };
  summary: EvidenceSummary;
  sourceRegister: EvidenceSource[];
  reportEvidence: EvidenceReport[];
}
