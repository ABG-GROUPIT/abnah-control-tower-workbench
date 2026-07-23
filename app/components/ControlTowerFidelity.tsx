"use client";

import {
  CheckCircle2,
  ChevronRight,
  CircleOff,
  Database,
  FileWarning,
  Layers3,
  Search,
  ShieldCheck,
  TableProperties,
} from "lucide-react";
import { useMemo, useState } from "react";
import type {
  ControlTowerFidelity,
  FidelityFieldRef,
  FidelityReport,
} from "../lib/control-tower-fidelity-types";

interface ControlTowerFidelityProps {
  fidelity: ControlTowerFidelity;
}

type FidelityFilter = "all" | "active" | "gated" | "audit";

const numberFormat = new Intl.NumberFormat("en-IN");

const humanize = (value: string) => value.replaceAll("_", " ");

function reportTone(report: FidelityReport) {
  if (report.downstreamStatus === "active_projected_fields") return "blue";
  if (report.downstreamStatus === "gated_source_unavailable") return "rose";
  return "neutral";
}

function reportStatus(report: FidelityReport) {
  if (report.downstreamStatus === "active_projected_fields") return "Active model";
  if (report.downstreamStatus === "gated_source_unavailable") return "Gated";
  return "Audit only";
}

function FieldTokens({
  fields,
  emptyLabel,
}: {
  fields: FidelityFieldRef[];
  emptyLabel: string;
}) {
  if (!fields.length) return <p className="ct-fidelity-empty">{emptyLabel}</p>;
  return (
    <div className="ct-fidelity-fields">
      {fields.map((field) => (
        <span key={field.field} title={field.field}>
          <strong>{field.label}</strong>
          <code>{field.field}</code>
        </span>
      ))}
    </div>
  );
}

function ReportDetail({ report }: { report: FidelityReport }) {
  const isHistorical = report.evidenceScope === "historical_abnah_export";
  const blankCount = report.ignoredFields.filter(
    (field) => field.observedState === "all_blank",
  ).length;
  const zeroCount = report.ignoredFields.filter(
    (field) => field.observedState === "all_zero",
  ).length;

  return (
    <article className="ct-fidelity-detail">
      <header className="ct-fidelity-report-heading">
        <div>
          <span className="section-kicker">
            {isHistorical ? "Historical ABNAH contract" : "Validated POSIST contract"} / {report.reportStem}
          </span>
          <h2>{report.displayName}</h2>
          <p>{report.grain}</p>
        </div>
        <span className={`ct-pill tone-${reportTone(report)}`}>{reportStatus(report)}</span>
      </header>

      <div className="ct-fidelity-contract-strip">
        <span>
          <CheckCircle2 aria-hidden="true" size={15} />
          <b>Exact header</b>
          <small>{report.columnCount} columns, spelling and order verified</small>
        </span>
        <span>
          <TableProperties aria-hidden="true" size={15} />
          <b>
            {isHistorical
              ? "Historical quality gate"
              : report.rowPatternStatus === "mirrored_header_only"
                ? "Header-only mirror"
                : "Captured grain"}
          </b>
          <small>
            {isHistorical
              ? "Phone and address spillover must be repaired locally"
              : report.rowPatternStatus === "mirrored_header_only"
              ? "No synthetic business rows fabricated"
              : "Synthetic frequencies and values remain modelled"}
          </small>
        </span>
        <span>
          <Database aria-hidden="true" size={15} />
          <b>
            {isHistorical ? "Historical" : numberFormat.format(report.actualRowsAudited ?? 0)}
            {" / "}
            {numberFormat.format(report.syntheticRowsGenerated)}
          </b>
          <small>
            {isHistorical
              ? "Current UAT rows not retained / generated synthetic rows"
              : "Audited POSIST rows / generated synthetic rows"}
          </small>
        </span>
        <span>
          <CircleOff aria-hidden="true" size={15} />
          <b>{report.ignoredFields.length}</b>
          <small>
            {isHistorical
              ? "Structural repair gate documented"
              : `${blankCount} blank, ${zeroCount} zero-only, ${report.rowPatternStatus === "mirrored_header_only" ? "source gated" : "excluded downstream"}`}
          </small>
        </span>
      </div>

      <section className="ct-fidelity-field-section">
        <header>
          <div>
            <strong>KPI-projected fields</strong>
            <small>Only these populated fields enter the active standardized and analytical path.</small>
          </div>
          <span>{report.activeFields.length}</span>
        </header>
        <FieldTokens
          fields={report.activeFields}
          emptyLabel="This report is retained for audit, reconciliation, or future coverage; it is not projected into the active model."
        />
      </section>

      {report.gatedFields.length ? (
        <section className="ct-fidelity-field-section is-gated">
          <header>
            <div>
              <strong>Fields waiting behind a source gate</strong>
              <small>Do not expose these as zero-valued KPIs. A populated export must be audited first.</small>
            </div>
            <span>{report.gatedFields.length}</span>
          </header>
          <FieldTokens fields={report.gatedFields} emptyLabel="" />
        </section>
      ) : null}

      <section className="ct-fidelity-field-section">
        <header>
          <div>
            <strong>Confirmed no-signal fields</strong>
            <small>Preserved in RAW_CT shape; deliberately omitted from active Query Tables and dashboards.</small>
          </div>
          <span>{report.ignoredFields.length}</span>
        </header>
        {report.ignoredFields.length ? (
          <div className="ct-table-wrap">
            <table className="ct-table ct-fidelity-ignore-table">
              <thead>
                <tr>
                  <th>POSIST column</th>
                  <th>Canonical field</th>
                  <th>Observed</th>
                  <th>Synthetic</th>
                  <th>Current decision</th>
                </tr>
              </thead>
              <tbody>
                {report.ignoredFields.map((field) => (
                  <tr key={field.field}>
                    <td><strong>{field.label}</strong><small>{field.declaredType}</small></td>
                    <td><code>{field.field}</code></td>
                    <td><span className={`ct-signal-state state-${field.observedState}`}>{humanize(field.observedState)}</span></td>
                    <td><span className={`ct-signal-state state-${field.syntheticState}`}>{humanize(field.syntheticState)}</span></td>
                    <td>{field.decision === "source_unavailable_header_only" ? "Gate source" : "Ignore until populated"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="ct-fidelity-clear">
            <CheckCircle2 aria-hidden="true" size={17} />
            <span><strong>No fully blank or zero-only fields detected</strong><small>All captured fields retain at least some audited source signal.</small></span>
          </div>
        )}
      </section>

      <details className="ct-fidelity-context">
        <summary>
          <span><strong>Context-only source fields</strong><small>Available for drill or reconciliation, but not required by current KPIs</small></span>
          <b>{report.contextOnlyFields.length}</b>
        </summary>
        <FieldTokens fields={report.contextOnlyFields} emptyLabel="No additional context-only fields." />
      </details>

      <p className="ct-fidelity-note">{report.fidelityNote}</p>
    </article>
  );
}

export function ControlTowerFidelityView({
  fidelity,
}: ControlTowerFidelityProps) {
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<FidelityFilter>("all");
  const [selectedId, setSelectedId] = useState(
    fidelity.reports.find(
      (report) => report.downstreamStatus === "active_projected_fields",
    )?.reportId ?? fidelity.reports[0]?.reportId ?? "",
  );

  const visibleReports = useMemo(() => {
    const needle = query.trim().toLowerCase();
    return fidelity.reports.filter((report) => {
      const statusMatch =
        filter === "all"
        || (filter === "active" && report.downstreamStatus === "active_projected_fields")
        || (filter === "gated" && report.downstreamStatus === "gated_source_unavailable")
        || (filter === "audit" && report.downstreamStatus === "audit_or_reconciliation_only");
      if (!statusMatch) return false;
      if (!needle) return true;
      return [
        report.displayName,
        report.reportStem,
        report.grain,
        ...report.activeFields.flatMap((field) => [field.label, field.field]),
        ...report.ignoredFields.flatMap((field) => [field.label, field.field]),
      ].some((value) => value.toLowerCase().includes(needle));
    });
  }, [fidelity.reports, filter, query]);

  const selected =
    visibleReports.find((report) => report.reportId === selectedId)
    ?? visibleReports[0]
    ?? fidelity.reports[0];

  const filters: Array<{ id: FidelityFilter; label: string; count: number }> = [
    { id: "all", label: "All reports", count: fidelity.reports.length },
    {
      id: "active",
      label: "Active",
      count: fidelity.summary.activeReportContracts,
    },
    {
      id: "gated",
      label: "Gated",
      count: fidelity.summary.gatedReportContracts,
    },
    {
      id: "audit",
      label: "Audit only",
      count: fidelity.reports.filter(
        (report) => report.downstreamStatus === "audit_or_reconciliation_only",
      ).length,
    },
  ];

  return (
    <div className="ct-fidelity-view">
      <header className="ct-fidelity-decision">
        <ShieldCheck aria-hidden="true" size={24} />
        <div>
          <span className="section-kicker">Synthetic-to-POSIST fidelity register</span>
          <h2>{fidelity.headline}</h2>
          <p>{fidelity.scopeStatement}</p>
        </div>
        <span className="ct-pill tone-green">Verified {fidelity.asOfDate}</span>
      </header>

      <div className="ct-fidelity-summary" aria-label="Fidelity summary">
        <span><b>{fidelity.summary.exactHeaderReports}/{fidelity.summary.validatedReportContracts}</b><small>Exact headers</small></span>
        <span><b>{fidelity.summary.populatedReportContracts}</b><small>Populated contracts</small></span>
        <span><b>{fidelity.summary.headerOnlyReportContracts}</b><small>Header-only gates</small></span>
        <span><b>{fidelity.summary.confirmedAllBlankFields}</b><small>All-blank fields</small></span>
        <span><b>{fidelity.summary.confirmedAllZeroFields}</b><small>Zero-only fields</small></span>
        <span><b>{fidelity.summary.ignoredNoSignalFields}</b><small>Excluded downstream</small></span>
      </div>

      <section className="ct-fidelity-layers" aria-label="Data layer fidelity boundary">
        <header><Layers3 aria-hidden="true" size={16} /><span><strong>What “same as POSIST” means by layer</strong><small>Exact source contract, intentional landing translation, then usable-field projection</small></span></header>
        <ol>
          {fidelity.layers.map((layer, index) => (
            <li key={layer.id}>
              <span>{index + 1}</span>
              <div><strong>{layer.label}</strong><small>{layer.description}</small></div>
              <b>{humanize(layer.status)}</b>
              {index < fidelity.layers.length - 1 ? <ChevronRight aria-hidden="true" size={16} /> : null}
            </li>
          ))}
        </ol>
      </section>

      <section className="ct-fidelity-policy">
        <header><FileWarning aria-hidden="true" size={16} /><strong>Current modeling rules</strong></header>
        <ul>
          {fidelity.handlingPolicy.map((rule) => <li key={rule}>{rule}</li>)}
        </ul>
      </section>

      <div className="ct-fidelity-toolbar">
        <label className="ct-fidelity-search">
          <Search aria-hidden="true" size={15} />
          <input
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search report or field"
            aria-label="Search fidelity register"
          />
        </label>
        <div className="ct-fidelity-filters" role="group" aria-label="Fidelity report status">
          {filters.map((item) => (
            <button
              key={item.id}
              type="button"
              className={filter === item.id ? "is-active" : ""}
              aria-pressed={filter === item.id}
              onClick={() => setFilter(item.id)}
            >
              {item.label}<b>{item.count}</b>
            </button>
          ))}
        </div>
      </div>

      <div className="ct-fidelity-browser">
        <aside className="ct-fidelity-index" aria-label="Validated report contracts">
          <header><strong>Report contracts</strong><small>{visibleReports.length} visible</small></header>
          {visibleReports.map((report) => (
            <button
              key={report.reportId}
              type="button"
              className={selected?.reportId === report.reportId ? "is-active" : ""}
              onClick={() => setSelectedId(report.reportId)}
            >
              <span><b>{report.displayName}</b><small>{report.columnCount} columns / {report.ignoredFields.length} excluded</small></span>
              <i className={`tone-${reportTone(report)}`}>{reportStatus(report)}</i>
            </button>
          ))}
          {!visibleReports.length ? (
            <div className="ct-fidelity-no-results">No report or field matches this filter.</div>
          ) : null}
        </aside>
        {selected ? <ReportDetail report={selected} /> : null}
      </div>

      <section className="ct-fidelity-boundaries">
        <div>
          <strong>Schema-capture only</strong>
          <small>Captured visually, but not claimed as validated UAT CSV contracts.</small>
          {fidelity.schemaCaptureOnlyReports.map((report) => (
            <span key={report.name}><b>{report.name}</b>{report.handling}</span>
          ))}
        </div>
        <div>
          <strong>Explicit synthetic model inputs</strong>
          <small>These support the demonstrator and are never presented as POSIST reports.</small>
          <div className="ct-fidelity-aux">
            {fidelity.auxiliaryTables.map((table) => <code key={table}>{table}</code>)}
          </div>
        </div>
      </section>
    </div>
  );
}
