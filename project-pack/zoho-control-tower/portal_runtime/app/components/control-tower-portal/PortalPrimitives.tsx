import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";

export function MetricCard({
  title,
  value,
  detail,
  icon: Icon,
  tone = "default",
}: {
  title: string;
  value: string;
  detail: string;
  icon: LucideIcon;
  tone?: "default" | "danger" | "warning" | "success";
}) {
  return (
    <article className={`ct-metric-card tone-${tone}`}>
      <header>
        <span>{title}</span>
        <Icon aria-hidden="true" size={16} />
      </header>
      <strong>{value}</strong>
      <p>{detail}</p>
    </article>
  );
}

export function PortalPanel({
  title,
  subtitle,
  badge,
  children,
  className = "",
}: {
  title: string;
  subtitle: string;
  badge?: string;
  children: ReactNode;
  className?: string;
}) {
  return (
    <section className={`ct-data-panel ${className}`.trim()}>
      <header>
        <div>
          <h2>{title}</h2>
          <p>{subtitle}</p>
        </div>
        {badge ? <span>{badge}</span> : null}
      </header>
      <div className="ct-panel-body">{children}</div>
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
