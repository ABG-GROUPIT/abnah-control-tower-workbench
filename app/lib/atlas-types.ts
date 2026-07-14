export type AtlasNodeType =
  | "page"
  | "section"
  | "report"
  | "field"
  | "api"
  | "model"
  | "domain"
  | "validation";

export type AtlasViewMode = "discovery" | "data" | "api" | "mapping";

export type MappingStatus = "candidate" | "selected" | "rejected" | "deferred";
export type ValidationStatus = "planned" | "passed" | "partial" | "failed" | "blocked";

export interface AtlasNode {
  id: string;
  type: AtlasNodeType;
  label: string;
  status: string;
  priority: "P0" | "P1" | "P2";
  domain: string;
  description: string;
  is_core?: boolean;
  page?: string;
  section?: string;
  layer?: string;
  method?: string;
  path?: string;
  evidence_count?: number;
  occurrence_count?: number;
  field_count?: number;
  schema_ready?: boolean;
  validation_status?: string;
  subject_id?: string;
  test_type?: string;
}

export interface AtlasEdge {
  id: string;
  source: string;
  target: string;
  type: string;
  label: string;
  status: string;
  confidence: number;
  rationale: string;
}

export interface AtlasReport {
  id: string;
  name: string;
  page: string;
  section: string;
  report_folder: string;
  domain: string;
  priority: "P0" | "P1" | "P2";
  is_core: boolean;
  status: string;
  capture_method: string;
  next_action: string;
  field_ids: string[];
  evidence_count: number;
  questions: Array<Record<string, string>>;
  api_links: string[];
  model_links: string[];
}

export interface AtlasField {
  id: string;
  name: string;
  label: string;
  occurrence_count: number;
  report_ids: string[];
  semantic_roles: string[];
  data_type_guesses: string[];
  status: string;
}

export interface AtlasApiEndpoint {
  id: string;
  packet_id: string;
  folder: string;
  endpoint_name: string;
  method: string;
  path: string;
  auth_or_key_params: string;
  abnah_priority: "P0" | "P1" | "P2";
  primary_dashboard_fit: string;
  usefulness: string;
  notes: string;
  status: string;
  validation_status: string;
  validation_test_ids: string[];
  report_links: string[];
  model_links: string[];
}

export interface AtlasModel {
  id: string;
  name: string;
  label: string;
  layer: string;
  domain: string;
  status: string;
  source_path: string;
  description: string;
}

export interface AtlasMappingOption {
  id: string;
  mapping_id: string;
  source_id: string;
  target_id: string;
  relationship_type: string;
  status: MappingStatus;
  confidence: number;
  rationale: string;
  decision_reason: string;
  evidence_ref: string;
  owner: string;
  updated_at: string;
}

export interface AtlasValidationTest {
  id: string;
  test_id: string;
  subject_id: string;
  test_type: string;
  status: ValidationStatus;
  result: string;
  evidence_ref: string;
  tested_at: string;
  owner: string;
  notes: string;
}

export interface AtlasData {
  schema_version: string;
  generated_at: string;
  title: string;
  summary: {
    reports: number;
    reports_with_fields: number;
    unique_fields: number;
    field_occurrences: number;
    evidence_items: number;
    api_endpoints: number;
    model_objects: number;
    mapping_options: number;
    selected_mappings: number;
    validation_tests: number;
    passed_validation_tests: number;
    candidate_relationships: number;
    unresolved_questions: number;
    node_types: Record<string, number>;
    edge_types: Record<string, number>;
  };
  quality: {
    status: string;
    errors: string[];
    warnings: string[];
    coverage: {
      reports_total: number;
      reports_with_fields: number;
      reports_with_fields_pct: number;
      reports_with_api_candidates_or_verified: number;
      verified_report_api_links: number;
      verified_report_model_links: number;
      tested_api_endpoints: number;
      selected_mappings: number;
      validation_tests: number;
      passed_validation_tests: number;
    };
  };
  facets: {
    pages: string[];
    domains: Array<{ id: string; label: string }>;
    priorities: string[];
    node_types: string[];
    mapping_statuses: MappingStatus[];
    validation_statuses: ValidationStatus[];
  };
  nodes: AtlasNode[];
  edges: AtlasEdge[];
  reports: AtlasReport[];
  fields: AtlasField[];
  api_endpoints: AtlasApiEndpoint[];
  models: AtlasModel[];
  mapping_options: AtlasMappingOption[];
  validation_tests: AtlasValidationTest[];
  unresolved_questions: Array<Record<string, string>>;
}

export interface GraphSlice {
  nodes: AtlasNode[];
  edges: AtlasEdge[];
}
