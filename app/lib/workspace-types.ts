export type WorkflowStatus = "draft" | "in_review" | "published";
export type SchemaStatus = "captured" | "partial" | "pending" | "unavailable";
export type VerificationStatus = "needs_review" | "reviewed" | "uat_verified";
export type LayoutKind =
  | "flat"
  | "grouped_columns"
  | "grouped_rows"
  | "mixed"
  | "freeform";

export type SchemaCellKind = "group" | "field" | "label" | "context" | "blank";

export interface SchemaCell {
  id: string;
  row: number;
  column: number;
  rowSpan: number;
  columnSpan: number;
  text: string;
  kind: SchemaCellKind;
  fieldId?: string;
}

export interface SchemaTable {
  id: string;
  name: string;
  rows: number;
  columns: number;
  columnWidths: number[];
  cells: SchemaCell[];
}

export interface WorkspaceField {
  id: string;
  key: string;
  label: string;
  semanticRole: string;
  dataType: string;
  status: "captured" | "candidate" | "needs_review";
  notes: string;
}

export type ApiTestStatus =
  | "not_tested"
  | "planned"
  | "passed"
  | "partial"
  | "failed"
  | "blocked";

export interface WorkspaceApiTest {
  id: string;
  endpointId: string;
  endpointName: string;
  method: string;
  path: string;
  testType: string;
  status: ApiTestStatus;
  result: string;
  errorType: string;
  notes: string;
  testedAt: string;
}

export interface WorkspaceNote {
  id: string;
  category: "engineering" | "source" | "decision" | "issue";
  body: string;
  author: string;
  createdAt: string;
}

export interface ReportWorkspaceDocument {
  id: string;
  name: string;
  page: string;
  section: string;
  domain: string;
  priority: "P0" | "P1" | "P2";
  schemaStatus: SchemaStatus;
  verificationStatus: VerificationStatus;
  layoutKind: LayoutKind;
  captureMethod: string;
  sourcePolicy: string;
  workflowStatus: WorkflowStatus;
  version: number;
  isArchived: boolean;
  isCustom: boolean;
  fields: WorkspaceField[];
  tables: SchemaTable[];
  apiTests: WorkspaceApiTest[];
  notes: WorkspaceNote[];
  updatedAt: string;
  updatedBy: string;
}

export interface WorkspaceSeed {
  contractVersion: string;
  generatedAt: string;
  sourcePolicy: string;
  reports: ReportWorkspaceDocument[];
}

export interface WorkspaceDocumentIndexEntry {
  reportId: string;
  name: string;
  page: string;
  section: string;
  domain: string;
  workflowStatus: WorkflowStatus;
  version: number;
  isArchived: boolean;
  updatedAt: string;
  updatedBy: string;
}

export interface WorkspaceRevision {
  id: string;
  reportId: string;
  version: number;
  workflowStatus: WorkflowStatus;
  action: string;
  actor: string;
  createdAt: string;
}
