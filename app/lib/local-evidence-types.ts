export type LocalIssueSeverity = "critical" | "major" | "minor" | "info";

export interface LocalReviewIssue {
  id: string;
  finding_id: string;
  report_id: string;
  export_label: string;
  row_number: number;
  severity: LocalIssueSeverity;
  issue_class: string;
  state: "confirmed_issue" | "operational_exception" | "needs_business_definition";
  confidence: "high" | "medium" | "low";
  title: string;
  message: string;
  fields: string[];
  expected: string;
  observed: string;
  impact_abs: string;
  impact_pct: string;
  production_treatment: string;
}

export interface LocalReviewPacket {
  packet_version: string;
  privacy: string;
  as_of_date: string;
  reports: Array<{
    report_id: string;
    display_name: string;
    findings: Array<Record<string, unknown>>;
    controls: Array<Record<string, unknown>>;
    exports: Array<{
      id: string;
      label: string;
      columns: string[];
      column_types: Record<string, string>;
      rows: Array<{
        source_row_number: number;
        values: Record<string, string>;
        issues: LocalReviewIssue[];
      }>;
    }>;
  }>;
}
