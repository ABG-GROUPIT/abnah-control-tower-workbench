"use client";

import { Braces, Search } from "lucide-react";
import { useMemo, useState } from "react";
import type { ReportWorkspaceDocument } from "../lib/workspace-types";

interface ApiRegistryProps {
  reports: ReportWorkspaceDocument[];
  onOpenReport: (reportId: string) => void;
}

export function ApiRegistry({ reports, onOpenReport }: ApiRegistryProps) {
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState("all");
  const records = useMemo(
    () =>
      reports
        .flatMap((report) => report.apiTests.map((test) => ({ report, test })))
        .filter(({ report, test }) => {
          const haystack = `${report.name} ${test.endpointName} ${test.path} ${test.status}`.toLowerCase();
          return haystack.includes(query.trim().toLowerCase()) && (status === "all" || test.status === status);
        })
        .sort((a, b) => a.report.name.localeCompare(b.report.name) || a.test.endpointName.localeCompare(b.test.endpointName)),
    [query, reports, status],
  );
  const tested = records.filter(({ test }) => !["not_tested", "planned"].includes(test.status)).length;

  return (
    <section className="registry-surface">
      <header className="surface-header">
        <div>
          <span className="section-kicker">Connection evidence</span>
          <h1>API validation register</h1>
          <p>{records.length} report-endpoint records / {tested} tested</p>
        </div>
      </header>
      <div className="registry-toolbar">
        <label className="search-control">
          <Search aria-hidden="true" size={16} />
          <input type="search" value={query} placeholder="Report or endpoint" onChange={(event) => setQuery(event.target.value)} />
        </label>
        <select aria-label="API test status" value={status} onChange={(event) => setStatus(event.target.value)}>
          <option value="all">All test states</option>
          <option value="not_tested">Not tested</option>
          <option value="planned">Planned</option>
          <option value="passed">Passed</option>
          <option value="partial">Partial</option>
          <option value="failed">Failed</option>
          <option value="blocked">Blocked</option>
        </select>
      </div>
      {records.length ? (
        <div className="registry-table-wrap">
          <table className="registry-table">
            <thead><tr><th>Report</th><th>Endpoint</th><th>Method</th><th>Path</th><th>Test</th><th>Status</th><th>Result / error</th></tr></thead>
            <tbody>
              {records.map(({ report, test }) => (
                <tr key={`${report.id}:${test.id}`}>
                  <td><button type="button" className="text-button" onClick={() => onOpenReport(report.id)}>{report.name}</button></td>
                  <td>{test.endpointName}</td><td><code>{test.method}</code></td><td><code>{test.path || "Not recorded"}</code></td>
                  <td>{test.testType}</td><td><span className={`status-label status-${test.status}`}>{test.status.replaceAll("_", " ")}</span></td>
                  <td>{test.errorType || test.result || "No result recorded"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="empty-state"><Braces aria-hidden="true" size={23} /><strong>No API records in this scope</strong></div>
      )}
    </section>
  );
}
