"use client";

import {
  AlertTriangle,
  BrainCircuit,
  CheckCircle2,
  ChevronRight,
  ExternalLink,
  FileWarning,
  Laptop,
  Rows3,
  Search,
  ShieldCheck,
  TableProperties,
} from "lucide-react";
import { useMemo, useState } from "react";
import type {
  ControlTowerEvidence,
  EvidenceFinding,
  EvidenceReport,
  EvidenceSource,
} from "../lib/control-tower-evidence-types";

interface ControlTowerEvidenceProps {
  evidence: ControlTowerEvidence;
  onOpenReport: (reportId: string) => void;
}

type SourceFilter = "all" | "primary" | "auxiliary" | "control";
type ReportFilter = "selected" | "evaluated" | "all";

const numberFormat = new Intl.NumberFormat("en-IN");
const label = (value: string) => value.replaceAll("_", " ");

function toneForStatus(value: string) {
  if (["exact", "complete", "populated", "schema_ready_value_checks_passed", "no_encoded_exception", "derived_reference", "derived_dimension"].includes(value)) return "green";
  if (["partial", "review_required", "review", "warning", "coverage_review", "definition_review", "business_review", "formula_definition_gate", "reconciliation_exception", "cost_coverage_gap", "operational_exception", "deduplication_risk", "derived_reference_optional_master", "primary_quality_gated", "historical_schema_with_documented_quality_gate"].includes(value)) return "amber";
  if (["weak", "missing", "header_only", "blocked_header_only", "blocker", "coverage_blocked", "coverage_blocker", "gated_unavailable", "unavailable_header_only", "blocked_feature"].includes(value)) return "red";
  return "neutral";
}

function EvidencePill({ value }: { value: string }) {
  return <span className={`ct-pill tone-${toneForStatus(value)}`}>{label(value)}</span>;
}

function SourceRegister({
  sources,
  onOpenReport,
}: {
  sources: EvidenceSource[];
  onOpenReport: (reportId: string) => void;
}) {
  const [filter, setFilter] = useState<SourceFilter>("all");
  const [query, setQuery] = useState("");
  const visible = useMemo(() => {
    const needle = query.trim().toLowerCase();
    return sources.filter((source) => {
      if (filter !== "all" && source.roleGroup !== filter) return false;
      return !needle || `${source.sourceName} ${source.sourceTable} ${source.modelRole}`.toLowerCase().includes(needle);
    });
  }, [filter, query, sources]);

  return (
    <section className="ct-section ct-source-register">
      <div className="ct-section-heading">
        <div>
          <TableProperties aria-hidden="true" size={16} />
          <span>
            <strong>Governed source register</strong>
            <small>Active reports, derived references, model outputs, reconciliation controls, and gated sources</small>
          </span>
        </div>
        <span className="ct-register-count">{visible.length} / {sources.length}</span>
      </div>
      <div className="ct-evidence-toolbar">
        <div className="ct-segmented" role="group" aria-label="Filter selected sources">
          {(["all", "primary", "auxiliary", "control"] as SourceFilter[]).map((item) => (
            <button key={item} type="button" className={filter === item ? "is-active" : ""} onClick={() => setFilter(item)}>
              {item === "all" ? "All sources" : label(item)}
            </button>
          ))}
        </div>
        <label className="ct-evidence-search">
          <Search aria-hidden="true" size={14} />
          <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Find a source" />
        </label>
      </div>
      <div className="ct-table-wrap">
        <table className="ct-table ct-evidence-source-table">
          <thead>
            <tr>
              <th>Source and role</th>
              <th>Control Tower pages</th>
              <th>Required data points</th>
              <th>Local audit</th>
              <th>Production decision</th>
              <th aria-label="Open schema" />
            </tr>
          </thead>
          <tbody>
            {visible.map((source) => (
              <tr key={source.id}>
                <td>
                  <strong>{source.sourceName}</strong>
                  <code>{source.sourceTable}</code>
                  <EvidencePill value={source.modelRole} />
                </td>
                <td><span className="ct-page-tags">{source.pages.map((page) => <b key={page}>{page}</b>)}</span></td>
                <td><span className="ct-field-list">{source.requiredFields.join(" / ")}</span></td>
                <td>
                  <EvidencePill value={source.auditStatus} />
                  <small>
                    {source.auditReportId
                      ? `${numberFormat.format(source.rowCount)} rows reviewed`
                      : source.auditStatus === "historical_schema_with_documented_quality_gate"
                        ? "Historical schema retained; local structural repair required"
                      : source.modelRole.startsWith("derived_")
                        ? "Derived from reviewed operational reports"
                        : ["gated_unavailable", "unavailable_header_only", "blocked_feature"].includes(source.modelRole)
                          ? "Excluded from the active landing model"
                          : "Approved model output"}
                  </small>
                </td>
                <td>
                  {source.productionDecision}
                  <small><b>Fallback:</b> {source.fallbackOrReconciliation}</small>
                </td>
                <td>
                  {source.workbenchReportId ? (
                    <button
                      type="button"
                      className="icon-button"
                      title={`Open ${source.sourceName} schema`}
                      onClick={() => onOpenReport(source.workbenchReportId)}
                    >
                      <ExternalLink aria-hidden="true" size={14} />
                    </button>
                  ) : null}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function FindingTable({ findings }: { findings: EvidenceFinding[] }) {
  if (!findings.length) {
    return (
      <div className="ct-evidence-clear">
        <CheckCircle2 aria-hidden="true" size={17} />
        <span><strong>No encoded value exception was detected</strong><small>This does not replace business sign-off or production-period reconciliation.</small></span>
      </div>
    );
  }
  return (
    <div className="ct-table-wrap">
      <table className="ct-table ct-finding-table">
        <thead><tr><th>State</th><th>Evidence observation</th><th>Codex semantic review</th><th>Production treatment</th></tr></thead>
        <tbody>
          {findings.map((finding) => (
            <tr key={finding.id}>
              <td>
                <EvidencePill value={finding.semanticReview.classification} />
                <small>{finding.semanticReview.confidence} confidence</small>
              </td>
              <td>
                <strong>{finding.title}</strong>
                <code>{finding.fields.join(" / ") || label(finding.category)}</code>
                <small>{finding.observation} / {finding.affectedRowCount ? `${numberFormat.format(finding.affectedRowCount)} affected observations` : "period-level finding"}</small>
              </td>
              <td>
                {finding.semanticReview.assessment}
                <small><b>Definition question:</b> {finding.semanticReview.businessQuestion}</small>
              </td>
              <td>{finding.productionTreatment}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ReportContext({
  report,
  findingById,
}: {
  report: EvidenceReport;
  findingById: Record<string, EvidenceFinding>;
}) {
  const [exportIndex, setExportIndex] = useState(0);
  const selectedExport = report.reportContext.exports[exportIndex] ?? report.reportContext.exports[0];
  const availableWindows = report.reportContext.contextWindows.filter(
    (window) => window.exportLabel === selectedExport?.label,
  );
  const [windowId, setWindowId] = useState("");
  const selectedWindow = availableWindows.find((window) => window.id === windowId) ?? availableWindows[0];
  const maxDensity = Math.max(1, ...(selectedExport?.issueDensity ?? []));

  return (
    <section className="ct-audit-subsection ct-report-context">
      <header>
        <span><Rows3 aria-hidden="true" size={15} /><strong>Reviewed report context</strong></span>
        <a href={report.reportContext.localViewerUrl} target="_blank" rel="noreferrer">
          <Laptop aria-hidden="true" size={14} /> Open full local report
        </a>
      </header>
      <div className="ct-report-context-intro">
        <p>{report.reportContext.statement}</p>
        <span><ShieldCheck aria-hidden="true" size={14} /> Operational values never leave the approved PC.</span>
      </div>

      <div className="ct-report-export-tabs" role="tablist" aria-label="Captured exports">
        {report.reportContext.exports.map((item, index) => (
          <button
            key={`${item.label}:${index}`}
            type="button"
            className={index === exportIndex ? "is-active" : ""}
            onClick={() => {
              setExportIndex(index);
              setWindowId("");
            }}
          >
            <span>{item.label}</span>
            <small>{numberFormat.format(item.rowCount)} rows / {numberFormat.format(item.issueObservationCount)} observations</small>
          </button>
        ))}
      </div>

      {selectedExport ? (
        <div className="ct-report-map">
          <div>
            <strong>Complete export row map</strong>
            <small>Every block represents an equal portion of the report; darker blocks contain more bounded row observations.</small>
          </div>
          <div className="ct-density-track" aria-label={`Review observation density across ${selectedExport.rowCount} rows`}>
            {selectedExport.issueDensity.map((count, index) => (
              <i
                key={`${selectedExport.label}:bucket:${index}`}
                className={count ? "has-issue" : ""}
                style={{ opacity: count ? 0.28 + (count / maxDensity) * 0.72 : 1 }}
                title={count ? `${count} review observations in this report segment` : "No row-level observation in this report segment"}
              />
            ))}
          </div>
          <div className="ct-report-map-scale"><span>first row</span><b>{numberFormat.format(selectedExport.rowCount)} data rows</b><span>last row</span></div>
        </div>
      ) : null}

      {availableWindows.length ? (
        <div className="ct-context-window-picker">
          <span>Highlighted context</span>
          <select value={selectedWindow?.id ?? ""} onChange={(event) => setWindowId(event.target.value)}>
            {availableWindows.map((window) => (
              <option key={window.id} value={window.id}>
                Row {window.focusSourceRowNumber}: {findingById[window.findingId]?.title ?? "Observed exception"}
              </option>
            ))}
          </select>
        </div>
      ) : null}

      <div className="ct-table-wrap ct-full-report-wrap">
        <table className="ct-table ct-full-report-table">
          <thead>
            <tr>
              <th className="ct-row-number-cell">Source row</th>
              {report.reportContext.columns.map((column) => (
                <th key={column.field}>
                  <span>{column.label}</span>
                  <code>{column.field}</code>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {(selectedWindow?.rows ?? [{ sourceRowNumber: 0, state: "context" as const, values: [] }]).map((row) => {
              const values = Object.fromEntries(row.values.map((value) => [value.field, value.value]));
              return (
                <tr key={`${selectedWindow?.id ?? "empty"}:${row.sourceRowNumber}`} className={row.state === "issue" ? "is-issue-row" : ""}>
                  <th className="ct-row-number-cell">{row.sourceRowNumber || "local"}</th>
                  {report.reportContext.columns.map((column) => {
                    const hasValue = Object.hasOwn(values, column.field);
                    return (
                      <td key={column.field} className={hasValue ? "is-issue-cell" : ""}>
                        {hasValue ? <code>{values[column.field] || "blank"}</code> : <span>{column.sensitive ? "protected" : "local"}</span>}
                      </td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      {selectedWindow ? (
        <p className="ct-context-caption">
          <b>Highlighted source row {selectedWindow.focusSourceRowNumber}.</b> Surrounding rows and all other report values are intentionally resolved by the localhost reviewer, where every row and flagged cell can be inspected.
        </p>
      ) : (
        <p className="ct-context-caption">No row-level excerpt is needed for this export. Its complete schema and row coverage are shown; full values remain local.</p>
      )}
    </section>
  );
}

function ReportEvidenceDetail({
  report,
  onOpenReport,
}: {
  report: EvidenceReport;
  onOpenReport: (reportId: string) => void;
}) {
  const findingById = useMemo(
    () => Object.fromEntries(report.findings.map((finding) => [finding.id, finding])),
    [report.findings],
  );
  return (
    <div className="ct-audit-detail">
      <header className="ct-audit-heading">
        <div>
          <span className="section-kicker">{report.selection.status === "selected" ? "Selected source" : "Evaluated alternative"}</span>
          <h2>{report.displayName}</h2>
          <p>{report.decision}</p>
        </div>
        <div className="ct-audit-heading-actions">
          <EvidencePill value={report.readiness} />
          <button type="button" className="icon-button" title="Open captured schema" onClick={() => onOpenReport(report.schema.workbenchReportId)}>
            <ExternalLink aria-hidden="true" size={14} />
          </button>
        </div>
      </header>

      <div className="ct-audit-metrics">
        <span><b>{report.filesAudited}</b><small>exports</small></span>
        <span><b>{numberFormat.format(report.rowsAudited)}</b><small>rows</small></span>
        <span><b>{report.schema.columnCount}</b><small>columns</small></span>
        <span><b>{report.emptyFileCount}</b><small>empty exports</small></span>
        <span><b>{numberFormat.format(report.duplicateRowCount)}</b><small>duplicate rows</small></span>
      </div>

      <div className="ct-schema-proof">
        <CheckCircle2 aria-hidden="true" size={18} />
        <span>
          <strong>Schema contract and Workbench visual both match</strong>
          <small>{report.schema.statement} Variant: {report.schema.matchedVariantName || report.schema.matchedVariantId}.</small>
        </span>
        <EvidencePill value={report.schema.status} />
      </div>

      <div className={`ct-codex-review tone-${toneForStatus(report.codexReview.status)}`}>
        <BrainCircuit aria-hidden="true" size={18} />
        <span>
          <strong>{report.codexReview.headline}</strong>
          <small>{report.codexReview.assessment} {report.codexReview.nextDecision}</small>
        </span>
        <b>{report.codexReview.confirmedStructuralErrorCount} confirmed structural errors</b>
      </div>

      <section className="ct-audit-subsection">
        <header>
          <span><AlertTriangle aria-hidden="true" size={15} /><strong>Review ledger</strong></span>
          <small>{report.periods.join(" / ")}</small>
        </header>
        <FindingTable findings={report.findings} />
      </section>

      <ReportContext report={report} findingById={findingById} />

      {report.evidenceRows.length ? (
        <section className="ct-audit-subsection">
          <header>
            <span><FileWarning aria-hidden="true" size={15} /><strong>Local evidence excerpt</strong></span>
            <small>Focused non-sensitive values retained for review</small>
          </header>
          <div className="ct-evidence-rows">
            {report.evidenceRows.map((row, index) => {
              const finding = findingById[row.findingId];
              return (
                <details key={row.id} open={index === 0}>
                  <summary>
                    <span><b>{row.exportLabel}</b> / source row {row.sourceRowNumber}</span>
                    <strong>{finding?.title ?? "Observed exception"}</strong>
                    <ChevronRight aria-hidden="true" size={15} />
                  </summary>
                  <div className="ct-evidence-row-body">
                    <div className="ct-table-wrap">
                      <table className="ct-table ct-row-value-table">
                        <thead><tr>{row.values.map((value) => <th key={value.field}>{value.label}</th>)}</tr></thead>
                        <tbody><tr>{row.values.map((value) => <td key={value.field}><code>{value.value || "blank"}</code></td>)}</tr></tbody>
                      </table>
                    </div>
                    <dl>
                      <div><dt>Expected</dt><dd>{row.expected}</dd></div>
                      <div><dt>Observed</dt><dd>{row.observed}</dd></div>
                    </dl>
                  </div>
                </details>
              );
            })}
          </div>
        </section>
      ) : null}

      {report.keyFieldCoverage.length ? (
        <section className="ct-audit-subsection">
          <header>
            <span><TableProperties aria-hidden="true" size={15} /><strong>Key-field coverage</strong></span>
            <small>Coverage is separate from schema presence</small>
          </header>
          <div className="ct-table-wrap">
            <table className="ct-table ct-coverage-table">
              <thead><tr><th>Field</th><th>Non-null</th><th>Zero</th><th>Negative</th><th>Coverage</th></tr></thead>
              <tbody>
                {report.keyFieldCoverage.map((field) => (
                  <tr key={field.field}>
                    <td><strong>{field.label}</strong><code>{field.field}</code></td>
                    <td>{numberFormat.format(field.nonNullCount)} / {numberFormat.format(field.totalCount)}</td>
                    <td>{numberFormat.format(field.zeroCount)}</td>
                    <td>{numberFormat.format(field.negativeCount)}</td>
                    <td><EvidencePill value={field.coverageStatus} /><small>{field.coveragePercent}% populated</small></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      ) : null}
    </div>
  );
}

function AuditExplorer({
  reports,
  onOpenReport,
}: {
  reports: EvidenceReport[];
  onOpenReport: (reportId: string) => void;
}) {
  const preferredId = reports.find((report) => report.reportId === "p4.enterprise_purchase_order.item")?.reportId ?? reports[0]?.reportId ?? "";
  const [selectedId, setSelectedId] = useState(preferredId);
  const [filter, setFilter] = useState<ReportFilter>("selected");
  const visible = reports.filter((report) => {
    if (filter === "all") return true;
    return filter === "selected"
      ? report.selection.status === "selected"
      : report.selection.status === "evaluated_not_selected";
  });
  const selected = reports.find((report) => report.reportId === selectedId) ?? visible[0] ?? reports[0];

  return (
    <section className="ct-section ct-audit-explorer">
      <div className="ct-section-heading">
        <div>
          <ShieldCheck aria-hidden="true" size={16} />
          <span><strong>Local data audit explorer</strong><small>Schema proof, aggregate risks, bounded row evidence, and publication treatment</small></span>
        </div>
        <div className="ct-segmented" role="group" aria-label="Filter audited reports">
          {(["selected", "evaluated", "all"] as ReportFilter[]).map((item) => (
            <button key={item} type="button" className={filter === item ? "is-active" : ""} onClick={() => setFilter(item)}>
              {item}
            </button>
          ))}
        </div>
      </div>
      <div className="ct-audit-browser">
        <aside className="ct-audit-index" aria-label="Audited reports">
          {visible.map((report) => (
            <button
              key={report.reportId}
              type="button"
              className={selected?.reportId === report.reportId ? "is-active" : ""}
              onClick={() => setSelectedId(report.reportId)}
            >
              <span className={`ct-audit-dot tone-${toneForStatus(report.readiness)}`} />
              <span><strong>{report.displayName}</strong><small>{numberFormat.format(report.rowsAudited)} rows / {report.findings.length} finding types</small></span>
            </button>
          ))}
        </aside>
        {selected ? <ReportEvidenceDetail report={selected} onOpenReport={onOpenReport} /> : null}
      </div>
    </section>
  );
}

export function ControlTowerEvidenceView({ evidence, onOpenReport }: ControlTowerEvidenceProps) {
  const summaryItems = [
    [evidence.summary.selectedSourceCount, "active sources"],
    [evidence.summary.auditedReportCount, "audited reports"],
    [evidence.summary.auditedFileCount, "local exports"],
    [evidence.summary.auditedRowCount, "rows reviewed"],
    [evidence.summary.deterministicIssueRowCount, "rule exceptions"],
    [evidence.summary.semanticFindingCount, "semantic findings"],
    [evidence.summary.headerOnlyReportCount, "header-only reports"],
  ] as const;

  return (
    <div className="ct-evidence-view">
      <section className="ct-evidence-decision">
        <AlertTriangle aria-hidden="true" size={20} />
        <div>
          <span className="section-kicker">Actual-data readiness decision</span>
          <h2>{evidence.decision.headline}</h2>
          <p>{evidence.decision.reason}</p>
          <small>{evidence.decision.productionRule}</small>
        </div>
        <EvidencePill value="review_required" />
      </section>

      <div className="ct-evidence-summary">
        {summaryItems.map(([value, itemLabel]) => (
          <span key={itemLabel}><b>{numberFormat.format(value)}</b><small>{itemLabel}</small></span>
        ))}
      </div>

      <div className="ct-privacy-band">
        <ShieldCheck aria-hidden="true" size={15} />
        <span><strong>Private evidence boundary</strong> {evidence.sourcePolicy}</span>
      </div>

      <section className="ct-zoho-readiness">
        <header>
          <div>
            <span className="section-kicker">Zoho execution decision</span>
            <h2>Start the demonstrator now; keep production publication gated.</h2>
            <p>{evidence.zohoReadiness.migrationRule}</p>
          </div>
          <div className="ct-zoho-state-grid">
            <span><EvidencePill value={evidence.zohoReadiness.demoBuild} /><small>Synthetic demonstrator</small></span>
            <span><EvidencePill value="review_required" /><small>Production-shaped model</small></span>
            <span><EvidencePill value="blocker" /><small>Actual KPI publication</small></span>
          </div>
        </header>
        <div className="ct-zoho-build-counts">
          <span><b>{evidence.zohoReadiness.requiredLandingTableCount}</b><small>landing tables</small></span>
          <span><b>{evidence.zohoReadiness.queryTableCount}</b><small>Query Tables</small></span>
          <span><b>{evidence.zohoReadiness.dashboardTabCount}</b><small>dashboard tabs</small></span>
        </div>
        <ol>
          {evidence.zohoReadiness.nextSequence.map((step, index) => (
            <li key={step}><b>{index + 1}</b><span>{step}</span></li>
          ))}
        </ol>
      </section>

      <SourceRegister sources={evidence.sourceRegister} onOpenReport={onOpenReport} />
      <AuditExplorer reports={evidence.reportEvidence} onOpenReport={onOpenReport} />
    </div>
  );
}
