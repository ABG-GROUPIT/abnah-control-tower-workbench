export type FidelityFieldState =
  | "all_blank"
  | "all_zero"
  | "no_rows"
  | "partially_blank"
  | "mixed_zero_nonzero"
  | "populated";

export interface FidelityFieldRef {
  field: string;
  label: string;
}

export interface FidelityIgnoredField extends FidelityFieldRef {
  declaredType: string;
  observedState: FidelityFieldState;
  syntheticState: FidelityFieldState;
  decision:
    | "ignored_until_source_populates"
    | "source_unavailable_header_only";
  reason: string;
}

export interface FidelityReport {
  reportId: string;
  reportStem: string;
  displayName: string;
  grain: string;
  schemaStatus: "exact_validated_contract";
  headerMatch: boolean;
  columnCount: number;
  actualFilesAudited: number;
  actualRowsAudited: number;
  syntheticFilesGenerated: number;
  syntheticRowsGenerated: number;
  rowPatternStatus: "modelled_at_captured_grain" | "mirrored_header_only";
  downstreamStatus:
    | "active_projected_fields"
    | "gated_source_unavailable"
    | "audit_or_reconciliation_only";
  activeFields: FidelityFieldRef[];
  gatedFields: FidelityFieldRef[];
  contextOnlyFields: FidelityFieldRef[];
  ignoredFields: FidelityIgnoredField[];
  fidelityNote: string;
}

export interface ControlTowerFidelity {
  contractVersion: string;
  asOfDate: string;
  status: "verified";
  headline: string;
  scopeStatement: string;
  handlingPolicy: string[];
  layers: Array<{
    id: string;
    label: string;
    status: "exact_contract" | "intentional_translation" | "projected_fields_only";
    description: string;
  }>;
  summary: {
    validatedReportContracts: number;
    exactHeaderReports: number;
    populatedReportContracts: number;
    headerOnlyReportContracts: number;
    confirmedAllBlankFields: number;
    confirmedAllZeroFields: number;
    ignoredNoSignalFields: number;
    activeReportContracts: number;
    gatedReportContracts: number;
    schemaCaptureOnlyReports: number;
    auxiliaryModelTables: number;
  };
  schemaCaptureOnlyReports: Array<{
    name: string;
    status: string;
    handling: string;
  }>;
  auxiliaryTables: string[];
  reports: FidelityReport[];
}
