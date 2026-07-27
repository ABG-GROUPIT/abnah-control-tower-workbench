import {
  ArrowUpRight,
  ChartNoAxesCombined,
  ChevronRight,
  Database,
  ExternalLink,
  Layers3,
  X,
} from "lucide-react";
import { useEffect, useState, type ReactNode } from "react";
import type { LucideIcon } from "lucide-react";
import {
  getPortalSessionToken,
  getZohoViewUrl,
} from "../../lib/supabase-portal-client";

export interface EvidenceColumn {
  key: string;
  label: string;
  render?: (record: Record<string, unknown>) => ReactNode;
}

export interface EvidenceContext {
  title: string;
  subtitle: string;
  reason: string;
  sourceQuery: string;
  sourceView: string;
  sourceUrl?: string;
  sourceCriteria?: string;
  records: Array<Record<string, unknown>>;
  columns: EvidenceColumn[];
}

export function MetricCard({
  title,
  value,
  detail,
  icon: Icon,
  tone = "default",
  onInspect,
}: {
  title: string;
  value: string;
  detail: string;
  icon: LucideIcon;
  tone?: "default" | "danger" | "warning" | "success";
  onInspect?: () => void;
}) {
  const content = (
    <>
      <header>
        <span>{title}</span>
        <span className="ct-metric-icon">
          <Icon aria-hidden="true" size={16} />
        </span>
      </header>
      <strong>{value}</strong>
      <footer>
        <p>{detail}</p>
        {onInspect ? <ChevronRight aria-hidden="true" size={14} /> : null}
      </footer>
    </>
  );

  return onInspect ? (
    <button
      type="button"
      className={`ct-metric-card tone-${tone} is-interactive`}
      onClick={onInspect}
      title={`Inspect ${title}`}
    >
      {content}
    </button>
  ) : (
    <article className={`ct-metric-card tone-${tone}`}>{content}</article>
  );
}

export function ExecutiveBrief({
  label,
  title,
  detail,
  tone = "neutral",
  action,
}: {
  label: string;
  title: string;
  detail: string;
  tone?: "neutral" | "danger" | "warning";
  action?: ReactNode;
}) {
  return (
    <section className={`ct-executive-brief tone-${tone}`}>
      <span>{label}</span>
      <div>
        <strong>{title}</strong>
        <p>{detail}</p>
      </div>
      {action ? <aside>{action}</aside> : null}
    </section>
  );
}

export function PortalPanel({
  title,
  subtitle,
  badge,
  children,
  className = "",
  action,
}: {
  title: string;
  subtitle: string;
  badge?: string;
  children: ReactNode;
  className?: string;
  action?: ReactNode;
}) {
  return (
    <section className={`ct-data-panel ${className}`.trim()}>
      <header>
        <div>
          <h2>{title}</h2>
          <p>{subtitle}</p>
        </div>
        <div className="ct-panel-actions">
          {badge ? <span>{badge}</span> : null}
          {action}
        </div>
      </header>
      <div className="ct-panel-body">{children}</div>
    </section>
  );
}

export function HybridVisualPanel({
  title,
  subtitle,
  badge,
  viewName,
  embedUrl,
  sourceUrl,
  children,
  onInspect,
  className = "",
}: {
  title: string;
  subtitle: string;
  badge?: string;
  viewName: string;
  embedUrl?: string;
  sourceUrl?: string;
  children: ReactNode;
  onInspect?: () => void;
  className?: string;
}) {
  const connected = Boolean(embedUrl);
  return (
    <section className={`ct-data-panel ct-hybrid-panel ${className}`.trim()}>
      <header>
        <div>
          <span className="ct-panel-kicker">
            <ChartNoAxesCombined aria-hidden="true" size={12} />
            {connected ? "Zoho native visual" : "Validation fallback"}
          </span>
          <h2>{title}</h2>
          <p>{subtitle}</p>
        </div>
        <div className="ct-panel-actions">
          {badge ? <span>{badge}</span> : null}
          {onInspect ? (
            <button type="button" onClick={onInspect} title="Inspect underlying data">
              <Layers3 aria-hidden="true" size={14} />
            </button>
          ) : null}
          {sourceUrl ? (
            <a
              href={sourceUrl}
              target="_blank"
              rel="noreferrer"
              title={`Open ${viewName} in Zoho`}
            >
              <ExternalLink aria-hidden="true" size={14} />
            </a>
          ) : null}
        </div>
      </header>
      {connected ? (
        <div className="ct-zoho-frame">
          <iframe
            title={viewName}
            src={embedUrl}
            loading="lazy"
            allow="fullscreen"
            referrerPolicy="strict-origin-when-cross-origin"
          />
        </div>
      ) : (
        <div className="ct-hybrid-fallback">
          {children}
          <div className="ct-visual-source-note">
            <Database aria-hidden="true" size={13} />
            <span>{viewName}</span>
            <small>Connect the secured Zoho view to replace this fallback.</small>
          </div>
        </div>
      )}
    </section>
  );
}

export function SeverityBadge({
  value,
  label,
}: {
  value: string;
  label?: string;
}) {
  const tone = value.toLowerCase();
  return (
    <span className={`ct-severity severity-${tone}`}>
      {label ?? value}
    </span>
  );
}

export function EmptyState({ children }: { children: ReactNode }) {
  return <div className="ct-empty-state">{children}</div>;
}

export function TableShell({
  children,
  label,
}: {
  children: ReactNode;
  label: string;
}) {
  return (
    <div className="ct-table-shell" role="region" aria-label={label} tabIndex={0}>
      {children}
    </div>
  );
}

export function SourceBadge({
  estimated = false,
}: {
  estimated?: boolean;
}) {
  return (
    <span className={`ct-source-badge${estimated ? " is-estimated" : ""}`}>
      {estimated ? "Estimated evidence" : "Source-linked"}
    </span>
  );
}

function displayValue(value: unknown) {
  if (value === null || value === undefined || value === "") return "Not available";
  if (typeof value === "boolean") return value ? "Yes" : "No";
  return String(value);
}

export function EvidenceDrawer({
  context,
  onClose,
}: {
  context: EvidenceContext | null;
  onClose: () => void;
}) {
  const contextKey = context
    ? [
        context.sourceView,
        context.sourceQuery,
        context.sourceCriteria ?? "",
      ].join("|")
    : "";
  const [resolution, setResolution] = useState({
    key: "",
    reportUrl: "",
    queryUrl: "",
    message: "",
  });

  useEffect(() => {
    if (!context) return;
    const handleKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    globalThis.addEventListener("keydown", handleKey);
    return () => globalThis.removeEventListener("keydown", handleKey);
  }, [context, onClose]);

  useEffect(() => {
    let active = true;
    if (!context || !getPortalSessionToken()) {
      return () => {
        active = false;
      };
    }

    const criteria = context.sourceCriteria ?? "";
    void Promise.allSettled([
      getZohoViewUrl(context.sourceView, criteria, "source"),
      getZohoViewUrl(context.sourceQuery, criteria, "source"),
    ]).then((results) => {
      if (!active) return;
      const [report, query] = results;
      const message =
        report.status === "rejected" &&
        query.status === "rejected"
          ? report.reason instanceof Error
            ? report.reason.message
            : "The exact Zoho sources could not be resolved."
          : "";
      setResolution({
        key: contextKey,
        reportUrl:
          report.status === "fulfilled" ? report.value.url : "",
        queryUrl:
          query.status === "fulfilled" ? query.value.url : "",
        message,
      });
    });

    return () => {
      active = false;
    };
  }, [context, contextKey]);

  if (!context) return null;
  const currentResolution =
    resolution.key === contextKey
      ? resolution
      : { reportUrl: "", queryUrl: "", message: "" };
  const resolvedReportUrl = currentResolution.reportUrl;
  const resolvedQueryUrl = currentResolution.queryUrl;
  const resolutionMessage = currentResolution.message;
  const governedReportUrl = resolvedReportUrl || context.sourceUrl || "";
  return (
    <div
      className="ct-evidence-backdrop"
      role="presentation"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) onClose();
      }}
    >
      <aside
        className="ct-evidence-drawer"
        role="dialog"
        aria-modal="true"
        aria-label={`${context.title} underlying evidence`}
      >
        <header>
          <div>
            <span>
              <Layers3 aria-hidden="true" size={13} />
              UNDERLYING EVIDENCE
            </span>
            <h2>{context.title}</h2>
            <p>{context.subtitle}</p>
          </div>
          <button type="button" onClick={onClose} title="Close drilldown">
            <X aria-hidden="true" size={18} />
          </button>
        </header>

        <section className="ct-evidence-reason">
          <strong>Why this is shown</strong>
          <p>{context.reason}</p>
        </section>

        <section className="ct-evidence-lineage">
          <div>
            <span>Query Table</span>
            <strong>{context.sourceQuery}</strong>
          </div>
          <div>
            <span>Zoho view</span>
            <strong>{context.sourceView}</strong>
          </div>
          <div>
            <span>Rows in scope</span>
            <strong>{context.records.length}</strong>
          </div>
        </section>

        <div className="ct-evidence-toolbar">
          <span>Selected scope records</span>
          <div>
            {governedReportUrl ? (
              <a href={governedReportUrl} target="_blank" rel="noreferrer">
                Open Zoho report
                <ArrowUpRight aria-hidden="true" size={14} />
              </a>
            ) : null}
            {resolvedQueryUrl ? (
              <a href={resolvedQueryUrl} target="_blank" rel="noreferrer">
                Open Query Table
                <ArrowUpRight aria-hidden="true" size={14} />
              </a>
            ) : null}
            {!governedReportUrl && !resolvedQueryUrl ? (
              <span className="is-pending">
                {resolutionMessage || "Resolving exact Zoho sources"}
              </span>
            ) : null}
          </div>
        </div>

        <div className="ct-evidence-table" role="region" tabIndex={0}>
          <table>
            <thead>
              <tr>
                {context.columns.map((column) => (
                  <th key={column.key}>{column.label}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {context.records.slice(0, 100).map((record, index) => (
                <tr key={index}>
                  {context.columns.map((column) => (
                    <td key={column.key}>
                      {column.render
                        ? column.render(record)
                        : displayValue(record[column.key])}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </aside>
    </div>
  );
}
