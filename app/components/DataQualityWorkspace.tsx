"use client";

import {
  AlertTriangle,
  CheckCircle2,
  FileJson2,
  LockKeyhole,
  Search,
  ShieldCheck,
  Upload,
  X,
} from "lucide-react";
import { useMemo, useRef, useState } from "react";
import type { ControlTowerEvidence } from "../lib/control-tower-evidence-types";
import type {
  LocalIssueSeverity,
  LocalReviewIssue,
  LocalReviewPacket,
} from "../lib/local-evidence-types";
import { ControlTowerEvidenceView } from "./ControlTowerEvidence";

interface DataQualityWorkspaceProps {
  evidence: ControlTowerEvidence;
  onOpenReport: (reportId: string) => void;
}

const severityRank: Record<LocalIssueSeverity, number> = {
  info: 0,
  minor: 1,
  major: 2,
  critical: 3,
};
const numberFormat = new Intl.NumberFormat("en-IN");
const label = (value: string) => value.replaceAll("_", " ");

function highestSeverity(issues: LocalReviewIssue[]): LocalIssueSeverity {
  return issues.reduce<LocalIssueSeverity>(
    (current, issue) =>
      severityRank[issue.severity] > severityRank[current]
        ? issue.severity
        : current,
    "info",
  );
}

function validatePacket(value: unknown): LocalReviewPacket {
  if (!value || typeof value !== "object") throw new Error("The selected file is not a JSON packet.");
  const candidate = value as Partial<LocalReviewPacket>;
  if (!candidate.packet_version || !Array.isArray(candidate.reports)) {
    throw new Error("This is not an ABNAH local review packet.");
  }
  return candidate as LocalReviewPacket;
}

function QualityPill({ value }: { value: string }) {
  const tone =
    value === "critical" || value === "failed" || value === "confirmed_issue"
      ? "red"
      : value === "major" || value === "definition_gate" || value === "operational_exception"
        ? "amber"
        : value === "minor" || value === "needs_business_definition"
          ? "blue"
          : "green";
  return <span className={`ct-pill tone-${tone}`}>{label(value)}</span>;
}

function ControlLedger({ evidence }: { evidence: ControlTowerEvidence }) {
  const [status, setStatus] = useState<"all" | "passed" | "failed" | "definition_gate">("all");
  const controls = evidence.businessReview.controls.filter(
    (control) => status === "all" || control.status === status,
  );
  return (
    <section className="dq-control-ledger">
      <header>
        <span>
          <ShieldCheck aria-hidden="true" size={16} />
          <strong>Cross-report control ledger</strong>
        </span>
        <div className="ct-segmented" role="group" aria-label="Control status">
          {(["all", "passed", "definition_gate", "failed"] as const).map((item) => (
            <button
              key={item}
              type="button"
              className={status === item ? "is-active" : ""}
              onClick={() => setStatus(item)}
            >
              {label(item)}
            </button>
          ))}
        </div>
      </header>
      <div className="ct-table-wrap">
        <table className="ct-table dq-control-table">
          <thead>
            <tr><th>Status</th><th>Control</th><th>Observed result</th><th>Fields</th></tr>
          </thead>
          <tbody>
            {controls.map((control) => (
              <tr key={control.id}>
                <td><QualityPill value={control.status} /></td>
                <td><strong>{control.title}</strong><code>{control.reports.join(" / ")}</code></td>
                <td>{control.observation}</td>
                <td><code>{control.fields.join(" / ") || "report contract"}</code></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function PriorityFindingRegister({ evidence }: { evidence: ControlTowerEvidence }) {
  const [severity, setSeverity] = useState<"all" | LocalIssueSeverity>("all");
  const findings = evidence.reportEvidence
    .flatMap((report) =>
      report.findings.map((finding) => ({
        ...finding,
        reportName: report.displayName,
      })),
    )
    .filter((finding) => severity === "all" || finding.severity === severity)
    .sort(
      (left, right) =>
        (severityRank[right.severity as LocalIssueSeverity] ?? -1) -
          (severityRank[left.severity as LocalIssueSeverity] ?? -1) ||
        right.affectedRowCount - left.affectedRowCount,
    );
  return (
    <section className="dq-finding-register">
      <header>
        <span>
          <AlertTriangle aria-hidden="true" size={16} />
          <strong>Priority finding register</strong>
        </span>
        <div className="ct-segmented" role="group" aria-label="Finding severity">
          {(["all", "critical", "major", "minor"] as const).map((item) => (
            <button
              key={item}
              type="button"
              className={severity === item ? "is-active" : ""}
              onClick={() => setSeverity(item)}
            >
              {label(item)}
            </button>
          ))}
        </div>
      </header>
      <div className="ct-table-wrap">
        <table className="ct-table dq-finding-table">
          <thead>
            <tr><th>Impact</th><th>Report and finding</th><th>Evidence</th><th>Production treatment</th></tr>
          </thead>
          <tbody>
            {findings.map((finding) => (
              <tr key={finding.id}>
                <td>
                  <QualityPill value={finding.severity} />
                  <QualityPill value={finding.state} />
                  <small>{numberFormat.format(finding.affectedRowCount)} affected rows</small>
                </td>
                <td><strong>{finding.title}</strong><small>{finding.reportName}</small><code>{finding.fields.join(" / ") || finding.issueClass}</code></td>
                <td>{finding.observation}<small><b>Decision:</b> {finding.semanticReview.businessQuestion}</small></td>
                <td>{finding.productionTreatment}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function PacketBrowser({
  packet,
  onClear,
}: {
  packet: LocalReviewPacket;
  onClear: () => void;
}) {
  const [reportId, setReportId] = useState(packet.reports[0]?.report_id ?? "");
  const report = packet.reports.find((item) => item.report_id === reportId) ?? packet.reports[0];
  const [exportId, setExportId] = useState(report?.exports[0]?.id ?? "");
  const selectedExport =
    report?.exports.find((item) => item.id === exportId) ?? report?.exports[0];
  const [severity, setSeverity] = useState<"all" | LocalIssueSeverity>("all");
  const [issuesOnly, setIssuesOnly] = useState(false);
  const [query, setQuery] = useState("");
  const [page, setPage] = useState(1);
  const [selectedIssueRow, setSelectedIssueRow] = useState<number | null>(null);

  const rows = useMemo(() => {
    const needle = query.trim().toLowerCase();
    return (selectedExport?.rows ?? []).filter((row) => {
      const visibleIssues =
        severity === "all"
          ? row.issues
          : row.issues.filter((issue) => issue.severity === severity);
      if (issuesOnly && !visibleIssues.length) return false;
      return !needle || Object.values(row.values).some((value) => value.toLowerCase().includes(needle));
    });
  }, [issuesOnly, query, selectedExport?.rows, severity]);
  const pageSize = 100;
  const pageCount = Math.max(1, Math.ceil(rows.length / pageSize));
  const currentPage = Math.min(page, pageCount);
  const visibleRows = rows.slice((currentPage - 1) * pageSize, currentPage * pageSize);
  const issueRow = selectedExport?.rows.find(
    (row) => row.source_row_number === selectedIssueRow,
  );
  const packetCounts = useMemo(() => {
    const issues = packet.reports.flatMap((item) =>
      item.exports.flatMap((exportItem) => exportItem.rows.flatMap((row) => row.issues)),
    );
    return {
      rows: packet.reports.reduce(
        (total, item) =>
          total + item.exports.reduce((sum, exportItem) => sum + exportItem.rows.length, 0),
        0,
      ),
      issues,
      counts: issues.reduce<Record<string, number>>((counts, issue) => {
        counts[issue.severity] = (counts[issue.severity] ?? 0) + 1;
        return counts;
      }, {}),
    };
  }, [packet.reports]);

  if (!report || !selectedExport) return null;

  return (
    <section className="dq-packet-browser">
      <header className="dq-packet-header">
        <div>
          <span className="section-kicker">Private evidence loaded in this browser tab</span>
          <h2>Row-level report reviewer</h2>
          <p>{packet.privacy}</p>
        </div>
        <button type="button" className="dq-clear-packet" onClick={onClear}>
          <X aria-hidden="true" size={14} /> Close packet
        </button>
      </header>
      <div className="dq-packet-summary">
        <span><b>{packet.reports.length}</b><small>reports</small></span>
        <span><b>{numberFormat.format(packetCounts.rows)}</b><small>rows</small></span>
        <span className="tone-critical"><b>{numberFormat.format(packetCounts.counts.critical ?? 0)}</b><small>critical observations</small></span>
        <span className="tone-major"><b>{numberFormat.format(packetCounts.counts.major ?? 0)}</b><small>major observations</small></span>
        <span className="tone-minor"><b>{numberFormat.format(packetCounts.counts.minor ?? 0)}</b><small>minor observations</small></span>
      </div>
      <div className="dq-browser-layout">
        <aside className="dq-report-index">
          {packet.reports.map((item) => {
            const issueCount = item.exports.reduce(
              (total, exportItem) =>
                total + exportItem.rows.reduce((sum, row) => sum + row.issues.length, 0),
              0,
            );
            return (
              <button
                key={item.report_id}
                type="button"
                className={item.report_id === report.report_id ? "is-active" : ""}
                onClick={() => {
                  setReportId(item.report_id);
                  setExportId(item.exports[0]?.id ?? "");
                  setPage(1);
                  setSelectedIssueRow(null);
                }}
              >
                <strong>{item.display_name}</strong>
                <small>{numberFormat.format(issueCount)} row observations</small>
              </button>
            );
          })}
        </aside>
        <div className="dq-report-detail">
          <div className="dq-report-heading">
            <div><span className="section-kicker">Local report</span><h2>{report.display_name}</h2></div>
            <QualityPill value={highestSeverity(
              report.exports.flatMap((item) => item.rows.flatMap((row) => row.issues)),
            )} />
          </div>
          <div className="dq-toolbar">
            <select value={selectedExport.id} onChange={(event) => { setExportId(event.target.value); setPage(1); }}>
              {report.exports.map((item) => (
                <option key={item.id} value={item.id}>{item.label} ({numberFormat.format(item.rows.length)} rows)</option>
              ))}
            </select>
            <label className="dq-search">
              <Search aria-hidden="true" size={14} />
              <input value={query} onChange={(event) => { setQuery(event.target.value); setPage(1); }} placeholder="Search this export" />
            </label>
            <select value={severity} onChange={(event) => { setSeverity(event.target.value as "all" | LocalIssueSeverity); setPage(1); }}>
              <option value="all">All severities</option>
              <option value="critical">Critical</option>
              <option value="major">Major</option>
              <option value="minor">Minor</option>
              <option value="info">Info</option>
            </select>
            <label className="dq-check"><input type="checkbox" checked={issuesOnly} onChange={(event) => { setIssuesOnly(event.target.checked); setPage(1); }} /> Flagged only</label>
          </div>
          {issueRow?.issues.length ? (
            <div className="dq-issue-panel">
              {issueRow.issues.map((issue) => (
                <div key={issue.id} className={`severity-${issue.severity}`}>
                  <QualityPill value={issue.severity} />
                  <span>
                    <strong>{issue.title}</strong>
                    <small>{label(issue.issue_class)} / {label(issue.state)} / {issue.confidence} confidence</small>
                    <p>{issue.message}</p>
                    <code>Expected: {issue.expected || "approved definition"} | Observed: {issue.observed || "review"}</code>
                    <em>{issue.production_treatment}</em>
                  </span>
                </div>
              ))}
            </div>
          ) : null}
          <div className="ct-table-wrap dq-local-table-wrap">
            <table className="ct-table dq-local-table">
              <thead>
                <tr>
                  <th className="dq-row-number">Source row</th>
                  {selectedExport.columns.map((column) => <th key={column}>{column}</th>)}
                </tr>
              </thead>
              <tbody>
                {visibleRows.map((row) => {
                  const filteredIssues =
                    severity === "all"
                      ? row.issues
                      : row.issues.filter((issue) => issue.severity === severity);
                  const rowSeverity = highestSeverity(filteredIssues);
                  const fieldSeverity = new Map<string, LocalIssueSeverity>();
                  filteredIssues.forEach((issue) => issue.fields.forEach((field) => {
                    const current = fieldSeverity.get(field) ?? "info";
                    if (severityRank[issue.severity] >= severityRank[current]) fieldSeverity.set(field, issue.severity);
                  }));
                  return (
                    <tr
                      key={row.source_row_number}
                      className={filteredIssues.length ? `is-issue severity-${rowSeverity}` : ""}
                      onClick={() => setSelectedIssueRow(row.source_row_number)}
                    >
                      <th className="dq-row-number">{row.source_row_number}</th>
                      {selectedExport.columns.map((column) => {
                        const value = row.values[column] ?? "";
                        const cellSeverity = fieldSeverity.get(column);
                        return (
                          <td key={column} className={cellSeverity ? `is-issue-cell severity-${cellSeverity}` : value === "" ? "is-blank" : ""}>
                            <code>{value === "" ? "blank" : value}</code>
                          </td>
                        );
                      })}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <footer className="dq-pagination">
            <span>{numberFormat.format(rows.length)} matching rows / page {currentPage} of {pageCount}</span>
            <div>
              <button type="button" disabled={currentPage === 1} onClick={() => setPage(1)}>|&lt;</button>
              <button type="button" disabled={currentPage === 1} onClick={() => setPage((value) => Math.max(1, value - 1))}>&lt;</button>
              <button type="button" disabled={currentPage === pageCount} onClick={() => setPage((value) => Math.min(pageCount, value + 1))}>&gt;</button>
              <button type="button" disabled={currentPage === pageCount} onClick={() => setPage(pageCount)}>&gt;|</button>
            </div>
          </footer>
        </div>
      </div>
    </section>
  );
}

export function DataQualityWorkspace({
  evidence,
  onOpenReport,
}: DataQualityWorkspaceProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [packet, setPacket] = useState<LocalReviewPacket | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const loadPacket = async (file: File) => {
    setLoading(true);
    setError("");
    try {
      const parsed = JSON.parse(await file.text()) as unknown;
      setPacket(validatePacket(parsed));
    } catch (caught) {
      setPacket(null);
      setError(caught instanceof Error ? caught.message : "The packet could not be opened.");
    } finally {
      setLoading(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  };

  return (
    <div className="dq-workspace">
      <section className="dq-intake">
        <div className="dq-intake-heading">
          <LockKeyhole aria-hidden="true" size={22} />
          <div>
            <span className="section-kicker">Data quality and local evidence</span>
            <h1>Actual-data review, classification, and publication gates</h1>
            <p>Hosted evidence remains aggregate and redacted. A selected local packet is processed only inside this browser tab.</p>
          </div>
          <input
            ref={inputRef}
            type="file"
            accept=".json,application/json"
            hidden
            onChange={(event) => {
              const file = event.target.files?.[0];
              if (file) void loadPacket(file);
            }}
          />
          <button type="button" onClick={() => inputRef.current?.click()} disabled={loading}>
            <Upload aria-hidden="true" size={15} />
            {loading ? "Opening packet" : packet ? "Replace local packet" : "Open local packet"}
          </button>
        </div>
        <div className="dq-hosted-summary">
          <span className="tone-critical"><b>{evidence.summary.criticalFindingCount}</b><small>critical finding types</small></span>
          <span className="tone-major"><b>{evidence.summary.majorFindingCount}</b><small>major finding types</small></span>
          <span className="tone-minor"><b>{evidence.summary.minorFindingCount}</b><small>minor finding types</small></span>
          <span className="tone-passed"><b>{evidence.summary.passedControlCount}</b><small>passed controls</small></span>
          <span className={evidence.summary.failedControlCount ? "tone-critical" : "tone-passed"}><b>{evidence.summary.failedControlCount}</b><small>failed controls</small></span>
        </div>
        {error ? <p className="dq-error"><AlertTriangle aria-hidden="true" size={14} /> {error}</p> : null}
        {!packet ? (
          <div className="dq-local-state">
            <FileJson2 aria-hidden="true" size={18} />
            <span><strong>Hosted review active</strong><small>Row values are not loaded. Aggregate findings and report schemas remain available below.</small></span>
            <CheckCircle2 aria-hidden="true" size={17} />
          </div>
        ) : null}
      </section>
      {packet ? (
        <PacketBrowser
          key={`${packet.packet_version}:${packet.as_of_date}:${packet.reports.length}`}
          packet={packet}
          onClear={() => setPacket(null)}
        />
      ) : null}
      <PriorityFindingRegister evidence={evidence} />
      <ControlLedger evidence={evidence} />
      <ControlTowerEvidenceView evidence={evidence} onOpenReport={onOpenReport} />
    </div>
  );
}
